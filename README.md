# T-Zero Auto Figura IP

ม็อดเสริมฝั่งผู้เล่นสำหรับ Figura บน Fabric / Forge / NeoForge / Quilt
ดูเวอร์ชันเกมและรุ่น Figura ที่ต้องใช้ใน [หน้าดาวน์โหลด](DOWNLOADS.md)

## พฤติกรรม — ตรวจสูงสุด 15 วินาทีก่อนเลือกคลาวด์ครั้งแรก

- ตอน Figura โหลด config เริ่มอ่าน GitHub และตรวจ /health ใน worker แยก
- ระหว่างรอตัดสินใจ ยังไม่เริ่มการยืนยันตัวตนคลาวด์ของ Figura เกมและ UI ไม่ถูกบล็อก
- พบคลาวด์ส่วนตัวพร้อมในกรอบเวลา: เลือก IP ส่วนตัวแล้วเริ่มเชื่อมต่อทันที
- GitHub ประกาศ offline ที่ยังไม่หมดอายุและไม่มี private endpoint ที่ยังตอบได้: ใช้คลาวด์ทางการ
- อ่าน/ตรวจไม่สำเร็จภายใน 15 วินาที: ใช้คลาวด์ทางการชั่วคราว แล้วตรวจต่อเบื้องหลัง
- พบคลาวด์ส่วนตัวภายหลัง: สลับไป IP ล่าสุดอัตโนมัติ แม้เพื่อนไม่เคยตั้ง IP มาก่อน
- ขณะใช้งานส่วนตัวอยู่ จะทนตรวจพลาดอย่างน้อย 3 รอบและ 60 วินาที ก่อนกลับทางการ
- แยกสถานะอ่าน GitHub ไม่ได้ออกจากสถานะที่โฮสต์ประกาศปิด พร้อม toast และข้อความใน log

15 วินาทีเป็นกรอบตัดสินใจเริ่มต้น ไม่ใช่การรับรองว่าล็อกอิน Mojang หรือโหลด avatar จะเสร็จใน 15 วินาที
หากตัวเกมยังโหลดก่อนมี client tick แรก การนำผลมาตั้งค่า/เริ่มเชื่อมต่อจะเกิดเมื่อ client tick ทำงาน
กรณีแก้ IP ระหว่างรอ จะเริ่มช่วงตรวจใหม่และทิ้งผลตรวจเก่า

อ่าน raw.githubusercontent.com เป็นหลัก และมี GitHub Contents API แบบไม่ใช้ token สำรอง
จำกัด API สำรองหนึ่งครั้งต่อห้านาทีเพื่อไม่ใช้ quota หมด และจำ hostname ที่อ่านได้ไว้ตรวจซ้ำ
กรณี raw ถูกบล็อกและลิงก์เปลี่ยน การพบลิงก์ใหม่ผ่าน API สำรองอาจช้าหลายนาที
อ่านอายุประกาศเทียบ HTTP Date ของ GitHub เมื่อมี เพื่อลดปัญหานาฬิกาคอมคลาดเคลื่อน
ไม่ได้ข้ามการตรวจสอบ HTTPS certificate

## ดาวน์โหลดสำหรับผู้เล่น — beta 7 ทุกเวอร์ชันที่ตรวจพบ

เปิด **[หน้าดาวน์โหลดแยกตามเวอร์ชัน Minecraft](DOWNLOADS.md)**
มี 40 ไฟล์ใน 15 เวอร์ชันเกม ตั้งแต่ 1.16.5 ถึง 1.21.4
ครอบคลุม Fabric, Forge, NeoForge และ Quilt ตามไฟล์ Figura ที่เผยแพร่จริง
อ่านข้อจำกัดของ Modrinth tags, Figura รุ่นที่ต้องใช้ และสถานะรุ่นทดลองในหน้านั้น

ปิดเกม → เอา AutoCloud/T-Zero รุ่นเก่าออก (เก็บ Figura ไว้) → Prism: Edit → Mods → Add File
เลือกไฟล์เพียงหนึ่งไฟล์ให้ตรง Minecraft และ loader

## อัปเกรดเครื่องโฮสต์ Windows 11 — ทำครั้งเดียว

เครื่องโฮสต์ของ T0CH1NA ต้องมี Docker Desktop และชุดเดิมที่
`%USERPROFILE%\FiguraCloud\compose.try.yaml` อยู่แล้ว
การอัปเกรดสำรอง server.py เดิมและคง named volume อวาตาร์เดิมไว้
หากเคยปรับข้อความบริการด้วยตนเอง ให้สำรองไว้ก่อน; รุ่นนี้ใส่ข้อความ T0CH1NA ไว้แล้ว

1. ดาวน์โหลด `t0ch1na-autocloud-host-1.0.0-beta.1.zip` จาก Releases แล้วแตก ZIP
2. สร้าง GitHub **fine-grained personal access token** ที่
   https://github.com/settings/personal-access-tokens/new
3. Resource owner: **T0R1409**; Repository access: **Only select repositories**
   เลือก **t0ch1na-figura-cloud** เท่านั้น
4. Repository permissions: **Contents: Read and write**
   กำหนดวันหมดอายุตามต้องการ จดไว้ว่าต้องเปลี่ยน token เมื่อหมดอายุ
5. เปิด PowerShell ในโฟลเดอร์ host ที่แตกแล้ว รัน:

```powershell
powershell -ExecutionPolicy Bypass -File .\upgrade-host.ps1
```

6. วาง token ในช่องลับที่สคริปต์ถาม ไม่ต้องส่ง token ในแชต
7. รอ Docker ทำงานและ publisher ประกาศ cloud.json แล้วแจก JAR ให้เพื่อน

ไฟล์ token อยู่ที่ `%USERPROFILE%\FiguraCloud\.github-publisher.token`
จำกัดสิทธิ์ไฟล์ไว้กับผู้ใช้ปัจจุบัน ใช้เฉพาะ publisher ผ่าน Docker secret
**ห้ามแจกไฟล์ token หรืออัปโหลดโฟลเดอร์โฮสต์ทั้งโฟลเดอร์ขึ้น GitHub**
หากต้องเปลี่ยน token ให้รัน setup-token.ps1 แล้ว recreate publisher:

```powershell
Set-Location "$env:USERPROFILE\FiguraCloud"
powershell -ExecutionPolicy Bypass -File .\setup-token.ps1
docker compose -f compose.try.yaml -f compose.autocloud.yaml up -d --force-recreate publisher
```

publisher ใช้ GitHub Contents API อัปเดตเมื่อ URL/สถานะเปลี่ยน และทุกประมาณ 10 นาที
เพื่อให้ประกาศมีอายุ 20 นาที ไม่ส่ง avatar หรือข้อมูลบัญชี Minecraft ไป GitHub
ไม่ต้องเปิด GitHub ค้างไว้ GitHub/Cloudflare ต้องพร้อมใช้งานและ token ต้องยังมีสิทธิ์

## เปิด–ปิดหลังอัปเกรด

เปิด Docker Desktop แล้วใช้ `Start-AutoCloud.bat` ในโฟลเดอร์ FiguraCloud
ปิดด้วย `Stop-AutoCloud.bat` หรือปุ่มหยุดทั้งกลุ่มใน Docker Desktop
หลังเปิดใหม่ม็อดผู้เล่นจะตาม URL ให้อัตโนมัติ ไม่ต้องคัดลอกชื่อใหม่
หน้า http://localhost:8787 ยังใช้ตรวจดูชื่อคลาวด์ได้
อย่าใช้ Start-Trial.bat เดิมหลังอัปเกรด เพราะจะไม่เริ่ม publisher ในการสร้างชุดใหม่

## ขนาดและข้อจำกัด

- คลาวด์ส่วนตัวเก็บได้บัญชีละ 1 avatar สูงสุด 10 MiB
- คลาวด์ทางการมีเพดานตามบริการทางการ ม็อดไม่ได้เพิ่มเพดานที่นั่น
- ไม่ย้ายหรืออัปโหลด avatar ของคลาวด์ส่วนตัวไปคลาวด์ทางการอัตโนมัติ
- ต้องมี Minecraft Java session ที่ Mojang ยืนยันได้
- Figura Server Backend (FSB) อาจมีลำดับเหนือ cloud; รุ่นนี้ยังไม่ได้เปลี่ยน FSB
- การตรวจ addon ใช้ header ไม่ใช่ระบบป้องกันไคลเอนต์ดัดแปลงปลอม header
- ถ้าจะจำกัดเฉพาะสมาชิก ให้กำหนด ALLOWED_UUIDS ฝั่งโฮสต์เพิ่ม
- beta 5 ผ่าน build, policy/transport/controller regressions และ API contract checks
  แต่ยังไม่ได้เปิด Minecraft จริงครบ 6 แบบหรือทดสอบจากเครื่องเพื่อนจริง
- ไม่ต้องอัปเกรดชุดโฮสต์หรือตั้ง GitHub token ใหม่เพื่อใช้ beta 5

## Build / ตรวจสอบ

ใช้ Python 3.11+ และ Java 21 เพื่อ build (ตัว build ดาวน์โหลด ECJ และ loader annotation API)

```sh
python build.py
python package_all.py
```

`support-matrix.json` ล็อกรายการ Figura และ SHA-512 ของไฟล์ SDK ที่ตรวจแล้ว
ถ้าต้องการอัปเดตรายการจาก Modrinth/GitHub ให้รัน `python prepare_support_matrix.py`
ตัวเตรียม matrix จะตรวจ method/field descriptors กับ binary จริง และหยุดเมื่อ API ไม่ตรง
ไม่ได้แจก Figura หรือ library ตัวอื่นรวมกับ addon

`generate_legacy_sources.py` แปลง controller ร่วมเป็น Java 8 สำหรับ 1.16.5
โดยใช้ HttpURLConnection สำหรับ discovery และ Apache HTTP สำหรับ header ของ Figura
ตัว Quilt 0.1.2 ใช้ namespace `fabric.org.figuramc.figura` และ WebsocketThingy constructor hook
ตัว Forge ใช้ Mod annotation รูปแบบเดียวกันที่คงเดิมระหว่างสาย 36–54; ไม่มีการอ้างชื่อคลาส Minecraft โดยตรง

รุ่นนี้ยังเป็น beta ดูผลทดสอบและขอบเขตใน VALIDATION.md
