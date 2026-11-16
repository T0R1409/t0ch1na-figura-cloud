"""Local-only tunnel dashboard; no Docker socket or credentials required."""
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import build_opener, ProxyHandler

opener = build_opener(ProxyHandler({}))


def tunnel_status():
    try:
        with opener.open('http://tunnel:20241/quicktunnel', timeout=2) as r:
            hostname = json.load(r).get('hostname', '').removeprefix('https://').rstrip('/')
        if not re.fullmatch(r'[a-z0-9-]+\.trycloudflare\.com', hostname):
            raise ValueError('Tunnel hostname is not ready')
        try:
            with opener.open('http://tunnel:20241/ready', timeout=2) as r:
                ready = r.status == 200
        except Exception:
            ready = False
        return {'hostname': hostname, 'ready': ready}
    except Exception:
        return {'hostname': '', 'ready': False}


HTML = '''<!doctype html>
<html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Figura Cloud</title>
<style>
body{background:#101821;color:#edf4fb;font:18px system-ui,sans-serif;max-width:760px;margin:60px auto;padding:24px}
section{background:#1b2939;padding:28px;border-radius:18px;border:1px solid #38516b}
h1{margin-top:0}input{box-sizing:border-box;width:100%;padding:16px;font:16px monospace;border-radius:9px;border:1px solid #61768c;background:#101821;color:white}
button,a{display:inline-block;margin:18px 10px 0 0;padding:12px 18px;border:0;border-radius:9px;background:#68dbc0;color:#102923;font:inherit;text-decoration:none;cursor:pointer}
button:disabled{opacity:.4;cursor:wait}p{line-height:1.7}.hint{color:#b7c8d8;font-size:16px}#message{min-height:28px}
</style>
<section><h1>Figura Cloud</h1><p id="status" role="status">กำลังตรวจสอบคลาวด์…</p>
<label for="hostname">คัดลอกชื่อนี้ไปใส่ช่อง Figura Cloud IP</label>
<p><input id="hostname" readonly placeholder="กำลังรอลิงก์…" onclick="this.select()"></p>
<button id="copy" disabled>คัดลอกชื่อคลาวด์</button>
<a id="health" target="_blank" rel="noopener" hidden>ตรวจสอบคลาวด์</a>
<p id="message" role="status"></p>
<p class="hint">อัปเดตลิงก์อัตโนมัติทุก 3 วินาที<br>เปิด Docker ค้างไว้ระหว่างใช้งาน<br>หากชื่อเปลี่ยน ให้คุณกับเพื่อนเปลี่ยน Figura Cloud IP ตามด้วย</p></section>
<script>
const input=document.getElementById('hostname'), copy=document.getElementById('copy');
const health=document.getElementById('health'), statusText=document.getElementById('status');
async function refresh(){
 try{
  const r=await fetch('/api/status',{cache:'no-store'});if(!r.ok)throw Error();const d=await r.json();
  input.value=d.hostname||'';copy.disabled=!d.hostname;
  health.hidden=!d.hostname;if(d.hostname)health.href='https://'+d.hostname+'/health';
  statusText.textContent=d.ready?'คลาวด์เชื่อมต่อแล้ว ✓':(d.hostname?'มีลิงก์แล้ว กำลังเชื่อมต่อ…':'กำลังรอคลาวด์ กรุณาเปิด backend และ tunnel ใน Docker');
 }catch(e){input.value='';copy.disabled=true;health.hidden=true;statusText.textContent='ติดต่อหน้าดูลิงก์ไม่ได้ กรุณาตรวจว่า Docker ยังเปิดอยู่';}
 setTimeout(refresh,3000);
}
copy.onclick=async()=>{
 try{await navigator.clipboard.writeText(input.value);document.getElementById('message').textContent='คัดลอกแล้ว นำไปวางใน Figura Cloud IP ได้เลย';}
 catch(e){input.select();document.getElementById('message').textContent='กด Ctrl + C เพื่อคัดลอกชื่อที่เลือกไว้';}
};refresh();
</script></html>'''


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/status':
            body = json.dumps(tunnel_status()).encode()
            content_type = 'application/json; charset=utf-8'
        elif self.path == '/':
            body = HTML.encode('utf-8')
            content_type = 'text/html; charset=utf-8'
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', 8787), Handler).serve_forever()
