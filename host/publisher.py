"""Publish only a public hostname. GitHub credentials stay in a Docker secret."""
import base64
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import re
import time
from urllib.error import HTTPError
from urllib.request import Request, build_opener, HTTPRedirectHandler

REPO = os.getenv('GITHUB_REPOSITORY', 'T0R1409/t0ch1na-figura-cloud')
if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', REPO):
    raise ValueError('Invalid repository')
API = 'https://api.github.com/repos/' + REPO + '/contents/cloud.json'
HOST = re.compile(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.trycloudflare\.com')
TOKEN_FILE = Path(os.getenv('GITHUB_TOKEN_FILE', '/run/secrets/github_token'))


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


OPENER = build_opener(NoRedirect())


def fetch(url):
    with OPENER.open(url, timeout=10) as r:
        return json.load(r)


def candidate():
    try:
        data = fetch('http://tunnel:20241/quicktunnel')
        host = data.get('hostname', '').removeprefix('https://').rstrip('/')
        if not HOST.fullmatch(host):
            return None
        health = fetch('http://backend:8080/health')
        if health.get('cloudId') != 't0ch1na' or not health.get('requiresAddon'):
            return None
        with OPENER.open('http://tunnel:20241/ready', timeout=5) as r:
            if r.status != 200:
                return None
        return host
    except Exception:
        return None


def publish(host, now):
    token = TOKEN_FILE.read_text(encoding='utf-8-sig').strip()
    if not token:
        raise ValueError('Missing publisher token')
    headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
               'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'T0CH1NA-Cloud-Publisher/1'}
    sha = None
    try:
        with OPENER.open(Request(API, headers=headers), timeout=15) as r:
            current = json.load(r)
            sha = current['sha']
    except HTTPError as e:
        if e.code != 404:
            raise
    document = {'schema': 1, 'cloudId': 't0ch1na', 'online': bool(host), 'hostname': host or '',
                'updatedAt': now.isoformat().replace('+00:00', 'Z'),
                'expiresAt': (now + timedelta(minutes=20)).isoformat().replace('+00:00', 'Z')}
    content = (json.dumps(document, indent=2) + '\n').encode()
    body = {'message': 'Update Figura cloud availability',
            'content': base64.b64encode(content).decode(), 'branch': 'main'}
    if sha:
        body['sha'] = sha
    headers['Content-Type'] = 'application/json'
    with OPENER.open(Request(API, data=json.dumps(body).encode(), headers=headers, method='PUT'), timeout=15) as r:
        if r.status not in (200, 201):
            raise RuntimeError('GitHub write failed')


def main():
    last_host = object()
    next_refresh = 0
    while True:
        host = candidate()
        now = datetime.now(timezone.utc)
        if host != last_host or time.monotonic() >= next_refresh:
            try:
                publish(host, now)
                last_host = host
                next_refresh = time.monotonic() + 600
                print('Directory updated: ' + (host or 'offline'), flush=True)
            except HTTPError as e:
                # Never log request headers, tokens, or response bodies.
                print('GitHub update failed: HTTP ' + str(e.code) + '. Check repository Contents permission.', flush=True)
            except Exception as e:
                print('Directory update failed: ' + type(e).__name__ + '. Check publisher token setup.', flush=True)
        time.sleep(15)


if __name__ == '__main__':
    main()
