import asyncio
import gzip
import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import uuid

from aiohttp.test_utils import TestClient, TestServer
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'host'))
from server import create_app

ALICE = str(uuid.UUID('12345678-1234-4234-8234-123456789abc'))
BOB = str(uuid.UUID('22345678-1234-4234-8234-123456789abc'))
LIMIT = 256 * 1024


class BackendTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.verified = []
        async def verifier(name, challenge):
            self.verified.append((name, challenge))
            if name == 'Denied':
                return None
            return {'name': name, 'id': (ALICE if name == 'Alice' else BOB).replace('-', '')}
        self.verifier = verifier
        self.client = TestClient(TestServer(create_app(self.tmp.name, LIMIT, verifier)), headers={'X-T0CH1NA-Addon':'1'})
        await self.client.start_server()

    async def asyncTearDown(self):
        await self.client.close()
        self.tmp.cleanup()

    async def login(self, name='Alice'):
        # Actual Figura AuthHandler contains two slashes after /api.
        r = await self.client.get('/api//auth/id', params={'username': name})
        self.assertEqual(r.status, 200)
        challenge = await r.text()
        r = await self.client.get('/api//auth/verify', params={'id': challenge})
        self.assertEqual(r.status, 200)
        self.assertEqual(self.verified[-1], (name, challenge))
        return {'token': await r.text()}

    async def test_roundtrip_large_avatar_and_persistence(self):
        headers = await self.login()
        # Valid compressed NBT root with a large byte-array field.
        import os
        raw = os.urandom(160 * 1024)
        data = gzip.compress(b'\x0a\x00\x00\x07\x00\x04test' + struct.pack('>i', len(raw)) + raw + b'\x00')
        self.assertGreater(len(data), 102400)
        r = await self.client.put('/api/avatar', data=data, headers=headers)
        self.assertEqual(r.status, 200)
        r = await self.client.post('/api/equip', json=[{'owner': ALICE, 'id': 'avatar'}], headers=headers)
        self.assertEqual(r.status, 200)
        r = await self.client.get('/api/' + ALICE, headers=headers)
        equipped = (await r.json())['equipped']
        self.assertEqual(equipped[0]['hash'], hashlib.sha256(data).hexdigest())
        r = await self.client.get(f'/api/{ALICE}/avatar', headers=headers)
        self.assertEqual(await r.read(), data)
        await self.client.close()
        self.client = TestClient(TestServer(create_app(self.tmp.name, LIMIT, self.verifier)), headers={'X-T0CH1NA-Addon':'1'})
        await self.client.start_server()
        r = await self.client.get(f'/api/{ALICE}/avatar', headers=headers)
        self.assertEqual(await r.read(), data)
        r = await self.client.get('/api/' + ALICE, headers=headers)
        self.assertEqual((await r.json())['equipped'], equipped)

    async def test_limits_and_boundary(self):
        h = await self.login()
        r = await self.client.get('/api/limits', headers=h)
        self.assertEqual((await r.json())['limits']['maxAvatarSize'], LIMIT)
        r = await self.client.put('/api/avatar', data=b'x' * LIMIT, headers=h)
        self.assertEqual(r.status, 200)
        r = await self.client.put('/api/avatar', data=b'x' * (LIMIT + 1), headers=h)
        self.assertEqual(r.status, 413)
        r = await self.client.put('/api/second', data=b'abc', headers=h)
        self.assertEqual(r.status, 507)

    async def test_auth_and_ownership(self):
        r = await self.client.put('/api/avatar', data=b'abc')
        self.assertEqual(r.status, 401)
        a, b = await self.login(), await self.login('Bob')
        self.assertEqual((await self.client.put('/api/avatar', data=b'abc', headers=a)).status, 200)
        r = await self.client.post('/api/equip', json=[{'owner': ALICE, 'id': 'avatar'}], headers=b)
        self.assertEqual(r.status, 403)
        r = await self.client.delete('/api/avatar', headers=b)
        self.assertEqual(r.status, 404)
        r = await self.client.get(f'/api/{ALICE}/avatar', headers=a)
        self.assertEqual(await r.read(), b'abc')
        r = await self.client.get('/api/auth/id?username=Denied')
        challenge = await r.text()
        r = await self.client.get('/api/auth/verify', params={'id': challenge})
        self.assertEqual(r.status, 401)
        r = await self.client.get('/api/auth/verify', params={'id': challenge})
        self.assertEqual(r.status, 401)

    async def test_websocket_event_and_ping(self):
        a, b = await self.login(), await self.login('Bob')
        ws_a = await self.client.ws_connect('/ws')
        ws_b = await self.client.ws_connect('/ws')
        for ws, h in [(ws_a, a), (ws_b, b)]:
            await ws.send_bytes(b'\x00' + h['token'].encode())
            self.assertEqual(await ws.receive_bytes(timeout=2), b'\x00')
        await ws_b.send_bytes(b'\x02' + uuid.UUID(ALICE).bytes)
        # A request on ws_b acts as a fence so its subscription is processed.
        await ws_b.ping(b'fence')
        await asyncio.sleep(0.02)
        await self.client.put('/api/avatar', data=b'abc', headers=a)
        self.assertEqual(await ws_b.receive_bytes(timeout=2), b'\x02' + uuid.UUID(ALICE).bytes)
        ping = b'\x01' + struct.pack('>i', 12345) + b'\x00payload'
        await ws_a.send_bytes(ping)
        self.assertEqual(await ws_b.receive_bytes(timeout=2), b'\x01' + uuid.UUID(ALICE).bytes + ping[1:])
        await ws_b.send_bytes(b'\x03' + uuid.UUID(ALICE).bytes)
        await ws_a.close()
        await ws_b.close()

    async def test_allowlist(self):
        import os
        from unittest.mock import patch
        await self.client.close()
        with patch.dict(os.environ, {'ALLOWED_UUIDS': ALICE}):
            self.client = TestClient(TestServer(create_app(self.tmp.name, LIMIT, self.verifier)), headers={'X-T0CH1NA-Addon':'1'})
        await self.client.start_server()
        await self.login()
        r = await self.client.get('/api/auth/id?username=Bob')
        challenge = await r.text()
        r = await self.client.get('/api/auth/verify', params={'id': challenge})
        self.assertEqual(r.status, 403)

    async def test_addon_gate(self):
        r = await self.client.get('/health', headers={'X-T0CH1NA-Addon':'wrong'})
        self.assertEqual(r.status, 200)
        self.assertEqual((await r.json())['cloudId'], 't0ch1na')
        r = await self.client.get('/api/auth/id?username=Alice', headers={'X-T0CH1NA-Addon':'wrong'})
        self.assertEqual(r.status, 403)
        r = await self.client.get('/ws', headers={'X-T0CH1NA-Addon':'wrong'})
        self.assertEqual(r.status, 403)

    async def test_delete_and_unequip(self):
        h = await self.login()
        await self.client.put('/api/avatar', data=b'abc', headers=h)
        await self.client.post('/api/equip', json=[{'owner': ALICE, 'id': 'avatar'}], headers=h)
        self.assertEqual((await self.client.delete('/api/avatar', headers=h)).status, 200)
        r = await self.client.get('/api/' + ALICE, headers=h)
        self.assertEqual((await r.json())['equipped'], [])
        self.assertEqual((await self.client.get(f'/api/{ALICE}/avatar', headers=h)).status, 404)


if __name__ == '__main__':
    unittest.main()
