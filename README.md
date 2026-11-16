# T0CH1NA Figura AutoCloud — รุ่นทดลอง

ม็อดเสริมฝั่งผู้เล่นสำหรับ Figura **0.1.6** บน Fabric / Minecraft Forge / NeoForge
รองรับ Minecraft **1.20.1 และ 1.21.1**

## สิ่งที่ทำ

- ติดตั้งคู่กับ Figura แล้วตั้งคลาวด์ให้อัตโนมัติ ไม่ต้องวาง IP เอง
- อ่านที่อยู่ล่าสุดจาก cloud.json บน GitHub ฟรี แล้วตรวจ /health ก่อนเลือกใช้
- เมื่อคลาวด์ส่วนตัวปิด: ตรวจไม่ผ่านสองรอบจะสลับไปคลาวด์ทางการของ Figura
- เมื่อคลาวด์กลับมา/ลิงก์เปลี่ยน: ตามที่อยู่ใหม่แล้วสลับกลับโดยไม่ต้องออกเซิร์ฟเวอร์
- โฮสต์ประกาศที่อยู่ผ่าน publisher ที่อ่านลิงก์ปัจจุบันจาก cloudflared
- backend รุ่นนี้ปฏิเสธคำขอ Figura ที่ไม่มีส่วนหัวของ AutoCloud
- ไม่มี GitHub token หรือรหัส Minecraft ฝังอยู่ใน JAR ที่แจกผู้เล่น

ตรวจประมาณทุก 15 วินาที การสลับไม่ใช่ทันที; เครือข่าย, GitHub raw cache และ timeout
อาจทำให้การตรวจพบลิงก์ใหม่ช้าขึ้นได้ เมื่ออ่าน GitHub ไม่ได้แต่คลาวด์เดิมยังตอบอยู่
จะใช้คลาวด์เดิมต่อ แทนการสลับออกทันที

## ดาวน์โหลดสำหรับผู้เล่น

เลือก **เพียง 1 ไฟล์** ให้ตรงกับ instance ใน Prism ของคุณ:

| Minecraft | Loader | JAR |
|---|---|---|
| 1.20.1 | fabric | t0ch1na-autocloud-1.0.0-beta.2-1.20.1-fabric.jar |
| 1.20.1 | forge | t0ch1na-autocloud-1.0.0-beta.2-1.20.1-forge.jar |
| 1.20.1 | neoforge | t0ch1na-autocloud-1.0.0-beta.2-1.20.1-neoforge.jar |
| 1.21.1 | fabric | t0ch1na-autocloud-1.0.0-beta.2-1.21.1-fabric.jar |
| 1.21.1 | forge | t0ch1na-autocloud-1.0.0-beta.2-1.21.1-forge.jar |
| 1.21.1 | neoforge | t0ch1na-autocloud-1.0.0-beta.2-1.21.1-neoforge.jar |

ปิดเกม → Prism: คลิกขวา instance → Edit → Mods → Add File → เลือก JAR
ต้องมี Figura 0.1.6 ของ loader/เวอร์ชันเดียวกันอยู่ด้วย ไม่มี Figura อยู่ใน JAR นี้
ฝั่ง Minecraft server ไม่ต้องลง addon นี้

**NeoForge 1.21.1:** ใช้ Figura 0.1.6 รุ่น NeoForge + AutoCloud neoforge-1.21.1

**NeoForge 1.20.1 (legacy ทดลอง):** ใช้ loader NeoForge สาย 47.x + Figura 0.1.6 รุ่น Forge
+ AutoCloud neoforge-1.20.1 รุ่นนี้ compile กับ NeoForge language-java 47.2.2
และตรวจ metadata ของ NeoForge 1.20.1-47.1.106 แล้ว ซึ่งยังใช้ mod ID forge และ namespace net.minecraftforge
Figura ไม่ได้เผยแพร่ JAR ที่ติดป้าย NeoForge 1.20.1 โดยตรง จึงยังต้องทดสอบความเข้ากันได้ในเกม
ไฟล์ NeoForge 1.21.1 ใช้แทนตัว 1.20.1 ไม่ได้
1.20.1 ใช้ Java 17 ขึ้นไป, 1.21.1 ใช้ Java 21
ม็อดนี้ควบคุม Figura Cloud IP ขณะเปิดเกม การแก้ช่องนั้นด้วยมือจะถูกระบบเลือกให้อีกครั้ง
ถ้าต้องการหยุดระบบอัตโนมัติ ให้ปิดเกมแล้วเอา AutoCloud ออกจาก Mods

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

## ขนาด การย้ายคลาวด์ และข้อจำกัด

- คลาวด์ส่วนตัวยังคง **1 avatar ต่อบัญชี สูงสุด 10 MiB**
- เมื่อสลับไปคลาวด์ทางการ ต้องใช้ขีดจำกัดของคลาวด์ทางการตามปกติ
  ม็อดนี้ไม่ได้เพิ่มเพดานของบริการทางการ
- อวาตาร์ที่เก็บในคลาวด์ส่วนตัวไม่ถูกย้าย/อัปโหลดไปคลาวด์ทางการอัตโนมัติ
  ดังนั้นเมื่อคลาวด์ส่วนตัวปิด ผู้ชมอาจเห็น avatar เดิมบนคลาวด์ทางการหรือไม่มี avatar
- การสลับเก็บ local preview ที่เลือกไว้ และล้าง cache ของผู้เล่นคนอื่นเพื่ออ่านจากคลาวด์ใหม่
- ต้องมี Minecraft Java session ที่ Mojang ยืนยันได้
- Figura Server Backend (FSB) ของ Minecraft server อาจเลือกเส้นทางเหนือ cloud
  ในกรณีนั้นให้ปิดการใช้ FSB สำหรับเซิร์ฟเวอร์นั้นใน Figura หากต้องการใช้ cloud นี้
- การตรวจ addon ใช้ HTTP/WebSocket header เพื่อปฏิเสธ Figura ปกติที่ไม่ได้ลง addon
  **ไม่ใช่การยืนยันไฟล์ม็อดที่ป้องกันไคลเอนต์ดัดแปลงปลอม header ได้**
- คลาวด์นี้จำกัดว่าต้องมี addon แต่หากจะจำกัดเฉพาะสมาชิกเซิร์ฟเวอร์ ให้ตั้ง ALLOWED_UUIDS เพิ่ม
- GitHub directory เริ่มจากสถานะ offline จนกว่าเจ้าของเครื่องตั้ง publisher สำเร็จ
- รุ่นนี้เป็น **beta**: build/ทดสอบ protocol และ state machine แล้ว
  ยังไม่ได้เปิด Minecraft จริงครบทั้ง 6 ชุด และยังไม่ได้ทดสอบด้วยบัญชี Minecraft จริง

## Build / ตรวจสอบ

ติดตั้ง Java 21 และ Python 3 แล้วรัน `python build.py`
ตัว build ดาวน์โหลด Eclipse ECJ, Mixin และ loader API เพื่อ compile Java 17 bytecode (NeoForge 1.21.1 เป็น Java 21 bytecode)
ไม่มีการแจก library เหล่านั้นหรือ Minecraft รวมใน addon JAR

```sh
python build.py
java -jar deps/ecj.jar -17 -proc:none -cp build/1.20.1-fabric:deps/gson.jar -d build/tests tests/PolicyTest.java
java -cp build/tests:build/1.20.1-fabric:deps/gson.jar PolicyTest
python -m pip install -r host/requirements.txt
python -m unittest discover -s tests -v
```

บน Windows เปลี่ยนตัวคั่น classpath จาก `:` เป็น `;`
`tests/verify_figura_contract.py` ตรวจชื่อ/descriptor จริงใน Figura 5 JAR (legacy 1.20.1 ใช้ Figura Forge ร่วมกัน)
โดยคาดว่าไฟล์อยู่ที่ `../figura-cloud/clients/`
Mixin ใช้ remap=false และแตะเฉพาะคลาส Figura ที่ชื่อเหมือนกันทั้ง loader/game versions
ไม่มีการอ้างชื่อคลาส Minecraft ที่ต้อง remap
