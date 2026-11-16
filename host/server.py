"""Private Figura backend v2. Minecraft sessions are verified by Mojang."""
import asyncio
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import sqlite3
import time
import uuid
from collections import defaultdict, deque

from aiohttp import ClientSession, ClientTimeout, WSMsgType, web

HTTP = web.AppKey('http', ClientSession)


def create_app(data_dir=None, max_size=None, verifier=None):
    limit = int(max_size or os.getenv('MAX_AVATAR_BYTES', '10485760'))
    if not 102400 < limit <= 67108864:
        raise ValueError('MAX_AVATAR_BYTES must be >102400 and <=67108864')
    folder = Path(data_dir or os.getenv('DATA_DIR', '/data'))
    folder.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(folder / 'figura.sqlite3')
    db.executescript('''
      PRAGMA journal_mode=WAL;
      CREATE TABLE IF NOT EXISTS avatars(owner TEXT,id TEXT,data BLOB,hash TEXT,PRIMARY KEY(owner,id));
      CREATE TABLE IF NOT EXISTS equipped(user TEXT PRIMARY KEY,owner TEXT,id TEXT);
      CREATE TABLE IF NOT EXISTS tokens(hash TEXT PRIMARY KEY,user TEXT,expires REAL);
    ''')
    @web.middleware
    async def addon_required(req, handler):
        if (req.path.startswith('/api') or req.path == '/ws') and os.getenv('REQUIRE_ADDON', '1') != '0':
            if req.headers.get('X-T0CH1NA-Addon') != '1':
                raise web.HTTPForbidden(text='Install T-Zero Auto Figura IP before using this cloud')
        return await handler(req)

    app = web.Application(client_max_size=limit + 1, middlewares=[addon_required])
    pending, sockets, attempts = {}, {}, defaultdict(deque)
    allowed = {str(uuid.UUID(v.strip())) for v in os.getenv('ALLOWED_UUIDS', '').split(',') if v.strip()}

    def throttle(key, count, seconds):
        now = time.monotonic()
        queue = attempts[key]
        while queue and queue[0] <= now - seconds:
            queue.popleft()
        if len(queue) >= count:
            raise web.HTTPTooManyRequests()
        queue.append(now)
        if len(attempts) > 4096:
            for old in list(attempts):
                if not attempts[old] or attempts[old][-1] < now - 3600:
                    del attempts[old]

    def token_user(token):
        if not token or len(token) > 256:
            raise web.HTTPUnauthorized()
        hashed = hashlib.sha256(token.encode()).hexdigest()
        row = db.execute('SELECT user,expires FROM tokens WHERE hash=?', (hashed,)).fetchone()
        if not row or row[1] < time.time() or (allowed and row[0] not in allowed):
            raise web.HTTPUnauthorized()
        return row[0]

    def user(req):
        return token_user(req.headers.get('token'))

    def avatar_id(value):
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', value):
            raise web.HTTPBadRequest(text='Invalid avatar id')
        return value

    async def broadcast(owner, packet, sync=False):
        for socket, state in list(sockets.items()):
            if state['expires'] <= time.time():
                sockets.pop(socket, None)
                await socket.close(code=4000)
                continue
            if owner in state['subscriptions'] or (sync and state['user'] == owner):
                try:
                    await asyncio.wait_for(socket.send_bytes(packet), 5)
                except (ConnectionError, TimeoutError, RuntimeError):
                    sockets.pop(socket, None)

    async def event(owner):
        await broadcast(owner, b'\x02' + uuid.UUID(owner).bytes)

    async def health(req):
        return web.json_response({'status': 'ok', 'maxAvatarSize': limit, 'cloudId': 't0ch1na', 'requiresAddon': os.getenv('REQUIRE_ADDON', '1') != '0'})

    async def auth_id(req):
        # Only trust the socket address; no client-controlled forwarding headers.
        throttle(('auth', req.remote), 30, 60)
        name = req.query.get('username', '')
        if not re.fullmatch(r'[A-Za-z0-9_]{1,16}', name):
            raise web.HTTPBadRequest()
        now = time.time()
        for key in list(pending):
            if pending[key][1] < now:
                del pending[key]
        if len(pending) >= 2048:
            raise web.HTTPServiceUnavailable()
        challenge = secrets.token_hex(20)
        pending[challenge] = (name, now + 120)
        return web.Response(text=challenge)

    async def verify(req):
        throttle(('verify', req.remote), 30, 60)
        entry = pending.pop(req.query.get('id', ''), None)
        if not entry or entry[1] < time.time():
            raise web.HTTPUnauthorized()
        name, _ = entry
        try:
            if verifier:
                profile = await verifier(name, req.query['id'])
            else:
                async with app[HTTP].get(
                    'https://sessionserver.mojang.com/session/minecraft/hasJoined',
                    params={'username': name, 'serverId': req.query['id']},
                    allow_redirects=False,
                ) as response:
                    profile = await response.json() if response.status == 200 else None
            if not profile or profile.get('name', '').lower() != name.lower():
                raise web.HTTPUnauthorized()
            owner = str(uuid.UUID(profile['id']))
        except (ValueError, KeyError):
            raise web.HTTPUnauthorized()
        except (TimeoutError, OSError):
            raise web.HTTPServiceUnavailable(text='Mojang verification unavailable')
        if allowed and owner not in allowed:
            raise web.HTTPForbidden(text='Account is not on the allowlist')
        token = secrets.token_urlsafe(48)
        with db:
            db.execute('DELETE FROM tokens WHERE expires < ?', (time.time(),))
            db.execute('INSERT INTO tokens VALUES(?,?,?)',
                       (hashlib.sha256(token.encode()).hexdigest(), owner, time.time() + 86400))
        return web.Response(text=token)

    async def root(req):
        user(req)
        return web.Response(text='Figura private cloud')

    async def limits(req):
        user(req)
        return web.json_response({'rate': {'upload': 60, 'download': 600, 'pingRate': 32, 'pingSize': 1024},
                                  'limits': {'maxAvatarSize': limit, 'maxAvatars': 1}})

    async def version(req):
        user(req)
        return web.json_response({'release': '0.1.6', 'prerelease': '0.1.6'})

    async def motd(req):
        user(req)
        return web.json_response({"text": "จัดทำโดย\n\n⋆. 𐙚˚࿔ T-Zero 𝜗𝜚˚⋆"})

    async def profile(req):
        user(req)
        try:
            owner = str(uuid.UUID(req.match_info['owner']))
        except ValueError:
            raise web.HTTPBadRequest()
        row = db.execute('SELECT a.owner,a.id,a.hash FROM equipped e JOIN avatars a '
                         'ON a.owner=e.owner AND a.id=e.id WHERE e.user=?', (owner,)).fetchone()
        equipped = [dict(zip(('owner', 'id', 'hash'), row))] if row else []
        return web.json_response({'equipped': equipped, 'equippedBadges': {'pride': [], 'special': []}})

    async def upload(req):
        owner, aid = user(req), avatar_id(req.match_info['aid'])
        throttle(('upload', owner), 60, 60)
        data = await req.read()
        if not data:
            raise web.HTTPBadRequest(text='Empty avatar')
        if len(data) > limit:
            raise web.HTTPRequestEntityTooLarge(max_size=limit, actual_size=len(data))
        row = db.execute('SELECT id FROM avatars WHERE owner=?', (owner,)).fetchone()
        if row and row[0] != aid:
            raise web.HTTPInsufficientStorage(text='One avatar per account')
        with db:
            db.execute('INSERT OR REPLACE INTO avatars VALUES(?,?,?,?)',
                       (owner, aid, data, hashlib.sha256(data).hexdigest()))
        await event(owner)
        return web.Response(text='OK')

    async def download(req):
        owner = user(req)
        throttle(('download', owner), 600, 60)
        try:
            target = str(uuid.UUID(req.match_info['owner']))
        except ValueError:
            raise web.HTTPBadRequest()
        row = db.execute('SELECT data FROM avatars WHERE owner=? AND id=?',
                         (target, avatar_id(req.match_info['aid']))).fetchone()
        if not row:
            raise web.HTTPNotFound()
        return web.Response(body=row[0], content_type='application/octet-stream')

    async def equip(req):
        owner = user(req)
        throttle(('equip', owner), 60, 60)
        try:
            entries = await req.json()
            if not isinstance(entries, list) or len(entries) > 1:
                raise ValueError()
            if entries:
                target = entries[0]
                if str(uuid.UUID(target['owner'])) != owner:
                    raise web.HTTPForbidden()
                aid = avatar_id(target['id'])
                if not db.execute('SELECT 1 FROM avatars WHERE owner=? AND id=?', (owner, aid)).fetchone():
                    raise web.HTTPNotFound()
                with db:
                    db.execute('INSERT OR REPLACE INTO equipped VALUES(?,?,?)', (owner, owner, aid))
            else:
                with db:
                    db.execute('DELETE FROM equipped WHERE user=?', (owner,))
        except (ValueError, KeyError, TypeError):
            raise web.HTTPBadRequest()
        await event(owner)
        return web.Response(text='OK')

    async def delete(req):
        owner, aid = user(req), avatar_id(req.match_info['aid'])
        with db:
            db.execute('DELETE FROM equipped WHERE owner=? AND id=?', (owner, aid))
            cursor = db.execute('DELETE FROM avatars WHERE owner=? AND id=?', (owner, aid))
        if not cursor.rowcount:
            raise web.HTTPNotFound()
        await event(owner)
        return web.Response(text='OK')

    async def badge(req):
        user(req)
        return web.Response(text='OK')

    async def websocket(req):
        ws = web.WebSocketResponse(heartbeat=30, max_msg_size=2048, compress=False)
        await ws.prepare(req)
        state = None
        try:
            msg = await ws.receive(timeout=15)
            if msg.type != WSMsgType.BINARY or not msg.data or msg.data[0] != 0:
                raise web.HTTPUnauthorized()
            ws_token = msg.data[1:].decode('utf-8')
            owner = token_user(ws_token)
            if sum(s['user'] == owner for s in sockets.values()) >= 3:
                await ws.close(code=4002)
                return ws
            expiry = db.execute('SELECT expires FROM tokens WHERE hash=?',
                                (hashlib.sha256(ws_token.encode()).hexdigest(),)).fetchone()[0]
            state = {'user': owner, 'subscriptions': set(), 'expires': expiry}
            sockets[ws] = state
            await ws.send_bytes(b'\x00')
            async for msg in ws:
                if time.time() > state['expires']:
                    await ws.close(code=4000)
                    break
                if msg.type != WSMsgType.BINARY or not msg.data:
                    continue
                token_user(ws_token)
                data, kind = msg.data, msg.data[0]
                throttle(('ws', owner), 256, 1)
                if kind in (2, 3) and len(data) == 17:
                    target = str(uuid.UUID(bytes=data[1:]))
                    if kind == 2 and len(state['subscriptions']) < 512:
                        state['subscriptions'].add(target)
                    elif kind == 3:
                        state['subscriptions'].discard(target)
                elif kind == 1 and 6 <= len(data) <= 1030:
                    throttle(('ping', owner), 32, 1)
                    await broadcast(owner, b'\x01' + uuid.UUID(owner).bytes + data[1:], bool(data[5]))
        except (web.HTTPException, UnicodeDecodeError, TimeoutError, ValueError):
            await ws.close(code=3000)
        finally:
            sockets.pop(ws, None)
        return ws

    async def startup(app):
        app[HTTP] = ClientSession(timeout=ClientTimeout(total=15))

    async def shutdown(app):
        for ws in list(sockets):
            await ws.close(code=1001)

    async def cleanup(app):
        await app[HTTP].close()
        db.close()

    app.on_startup.append(startup)
    app.on_shutdown.append(shutdown)
    app.on_cleanup.append(cleanup)
    app.add_routes([
        web.get('/health', health), web.get('/ws', websocket),
        web.get('/api/auth/id', auth_id), web.get('/api/auth/verify', verify),
        web.get('/api//auth/id', auth_id), web.get('/api//auth/verify', verify),
        web.get('/api', root), web.get('/api/', root),
        web.get('/api/limits', limits), web.get('/api/version', version),
        web.get('/api/motd', motd), web.post('/api/equip', equip),
        web.post('/api/temp_badges', badge),
        web.get('/api/{owner}/{aid}', download), web.get('/api/{owner}', profile),
        web.put('/api/{aid}', upload), web.delete('/api/{aid}', delete),
    ])
    return app


if __name__ == '__main__':
    web.run_app(create_app(), host='0.0.0.0', port=8080, access_log=None)
