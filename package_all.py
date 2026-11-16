"""Package one clearly labelled ZIP per Minecraft version; preserve original logo."""
from pathlib import Path
import json,zipfile,hashlib,collections
ROOT=Path(__file__).resolve().parent
rows=json.loads((ROOT/'build/all-build-manifest.json').read_text())
out=ROOT/'downloads/all-versions';out.mkdir(parents=True,exist_ok=True)
versions=collections.defaultdict(list)
for row in rows:versions[row['minecraft']].append(row)
labels={'fabric':'Fabric','forge':'Forge','neoforge':'NeoForge','quilt':'Quilt'}
all_hashes=[]
for game,items in versions.items():
    bundle=out/f'T-Zero-Minecraft-{game}-beta7.zip'
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for row in items:
            loader=labels[row['loader']];source=ROOT/'dist/all-versions'/row['addon_filename']
            name=f'Minecraft {game}/{loader}/{game}-{loader}-T-Zero.jar'
            z.write(source,name)
            note=f'''T-Zero Auto Figura IP — Minecraft {game} / {loader}\r
\r
จัดทำโดย\r
\r
⋆. 𐙚˚࿔ T-Zero 𝜗𝜚˚⋆\r
\r
ใช้กับ Figura {row['figura']}\r
Java ที่เกมต้องใช้: {row['java']} ขึ้นไป\r
ลิงก์ Figura ที่ตรวจคู่กัน:\r
{row['figura_url']}\r
\r
ปิดเกม เอา AutoCloud/T-Zero ตัวเก่าออก (เก็บ Figura ไว้)\r
แล้วใส่ไฟล์ .jar เพียงไฟล์เดียวผ่าน Prism > Edit > Mods > Add File\r
'''
            if row['loader']=='quilt':note+='ไฟล์ Quilt นี้ใช้กับ Figura 0.1.2 รุ่น Quilt ที่มีชื่อคลาสแบบ fabric.org เท่านั้น\r\nถ้าใช้ Figura รุ่น Fabric 0.1.6 บน Quilt ให้ใช้ไฟล์ addon ในโฟลเดอร์ Fabric แทน\r\n'
            if row.get('experimental'):note+='NeoForge 1.20.1 เป็น legacy ทดลอง ใช้ Figura รุ่น Forge\r\n'
            z.writestr(f'Minecraft {game}/{loader}/อ่านก่อนติดตั้ง.txt',b'\xef\xbb\xbf'+note.encode())
            all_hashes.append((row['addon_filename'],row['addon_sha256']))
        text=f'''ชุดสำหรับ Minecraft {game} เท่านั้น\r
\r
เลือกโฟลเดอร์ตัวโหลดที่ตรงกับชุดเกมของคุณ แล้วใส่ .jar เพียงไฟล์เดียว\r
อ่านไฟล์ อ่านก่อนติดตั้ง.txt ในโฟลเดอร์นั้น เพื่อเลือก Figura และ Java ให้ตรงรุ่น\r
ทั้งคุณกับเพื่อนต้องลง Figura และ T-Zero Auto Figura IP\r
ระบบตรวจลิงก์และคลาวด์ตอนเริ่มเกมสูงสุด 15 วินาที แล้วใช้คลาวด์ส่วนตัวหรือทางการชั่วคราว\r
ยังเป็นรุ่น beta ตรวจ API/metadata และทดสอบตัวควบคุมแล้ว แต่ยังไม่ได้เปิดเกมจริงครบทุกชุด\r
'''
        z.writestr('เริ่มอ่านตรงนี้.txt',b'\xef\xbb\xbf'+text.encode())
        z.write(ROOT/'host/update-credit.ps1','อัปเดตข้อความคลาวด์/update-credit.ps1')
    with zipfile.ZipFile(bundle) as z:
        assert z.testzip() is None
        for row in items:
            n=f'Minecraft {game}/{labels[row["loader"]]}/{game}-{labels[row["loader"]]}-T-Zero.jar'
            assert hashlib.sha256(z.read(n)).hexdigest()==row['addon_sha256']
    assert bundle.stat().st_size < 100*1024*1024
    print('Packaged',game,len(items),'loaders',bundle.stat().st_size,'bytes')
    all_hashes.append((bundle.name,hashlib.sha256(bundle.read_bytes()).hexdigest()))
(ROOT/'downloads/SHA256SUMS-beta.7.txt').write_text(''.join(f'{digest}  {name}\n' for name,digest in all_hashes))
(ROOT/'downloads/BUILD-MANIFEST-beta.7.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n')
base='https://github.com/T0R1409/t0ch1na-figura-cloud/raw/refs/tags/v1.0.0-beta.7/downloads/all-versions/'
text='''# ดาวน์โหลด T-Zero Auto Figura IP

จัดทำโดย

⋆. 𐙚˚࿔ T-Zero 𝜗𝜚˚⋆

**เลือกเวอร์ชัน Minecraft ที่เล่น แล้วกดดาวน์โหลด ZIP แถวเดียวเท่านั้น**
แตก ZIP แล้วเลือกโฟลเดอร์ Fabric / Forge / NeoForge / Quilt ให้ตรงกับ Prism instance
ใส่ addon เพียงหนึ่งไฟล์ และอ่าน Figura รุ่นที่ต้องใช้ในไฟล์ อ่านก่อนติดตั้ง.txt

| Minecraft | มีตัวโหลด | ดาวน์โหลด |
|---|---|---|
'''
for game in sorted(versions,key=lambda s:tuple(map(int,s.split('.'))),reverse=True):
    loaders=', '.join(labels[r['loader']]+(' (ทดลอง)' if r.get('experimental') else '') for r in versions[game])
    text+=f'| **{game}** | {loaders} | [ดาวน์โหลด {game}]({base}T-Zero-Minecraft-{game}-beta7.zip) |\n'
text+='''
## ก่อนติดตั้ง

- ปิดเกม และเอา AutoCloud/T-Zero รุ่นเดิมออกก่อน (เก็บ Figura ไว้)
- เลือกเพียงไฟล์เดียวต่อ instance อย่าใส่ทุก loader รวมกัน
- ส่วนใหญ่ใช้ Figura 0.1.6; Quilt รุ่นเก่าใช้ Figura 0.1.2 และบางชุดใช้ 0.1.5 ตามไฟล์คำแนะนำ
- Quilt: ถ้าคุณใช้ Figura รุ่น Fabric 0.1.6 บน Quilt ให้เลือก addon ในโฟลเดอร์ Fabric
- 1.16.5 มีตัว Java 8 โดยเฉพาะ ไม่ต้องนำ JAR ของ 1.20/1.21 ไปใส่
- ไม่ต้องเปลี่ยนโฮสต์ Docker หรือ GitHub token เพื่อใช้รุ่นนี้

## ขอบเขต

ชุดนี้สร้าง 40 ไฟล์สำหรับ Minecraft 15 เวอร์ชันที่พบจากไฟล์เผยแพร่ของ Figura บน Modrinth และ GitHub
ตรวจชื่อคลาส/เมธอด, metadata, Java bytecode, โลโก้และเครดิตแล้ว
ตัว Java 8 ผ่านการทดสอบตัวควบคุม, transport และ header บน Java 8 จริง
Quilt ผ่านตัวควบคุมกับ namespace เฉพาะ แต่ **ยังไม่ทดสอบเปิด Minecraft จริงครบ 40 ชุด**
จึงยังเป็นรุ่น beta; NeoForge 1.20.1 เป็น legacy ทดลอง

บาง Modrinth tag ไม่ตรงกับข้อกำหนดในไฟล์ Figura:
- Forge/NeoForge 1.21: ไฟล์ที่ติดป้ายไว้จริง ๆ กำหนด Minecraft 1.21.1 ขึ้นไป จึงไม่มีไฟล์ addon คู่ใช้งานในชุดนี้
- NeoForge 1.21.2: ไฟล์ Figura ที่ติดป้ายกำหนด Minecraft 1.21.3 ขึ้นไป จึงไม่มีคู่ใช้งานในชุดนี้
- Forge 1.21.2: เลือก Figura 0.1.5 ที่เผยแพร่กับเวอร์ชันนี้แทน 0.1.6 ที่กำหนด 1.21.3 ขึ้นไป

ที่มา: [Figura บน Modrinth](https://modrinth.com/mod/figura/versions) · [Figura GitHub releases](https://github.com/FiguraMC/Figura/releases)
'''
(ROOT/'DOWNLOADS.md').write_text(text)
