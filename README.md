# T0CH1NA Figura AutoCloud — รุ่นทดลอง

ม็อดเสริมฝั่งผู้เล่นสำหรับ Figura **0.1.6** บน Fabric / Minecraft Forge / NeoForge
รองรับ Minecraft **1.20.1 และ 1.21.1**

## พฤติกรรม beta 5 — ตรวจสูงสุด 15 วินาทีก่อนเลือกคลาวด์ครั้งแรก

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

## ดาวน์โหลดสำหรับผู้เล่น

เลือก **เพียง 1 ไฟล์** ให้ตรงกับ instance ใน Prism ของคุณ:

| Minecraft | Loader | JAR |
|---|---|---|
| 1.20.1 | fabric | t0ch1na-autocloud-1.0.0-beta.5-1.20.1-fabric.jar |
| 1.20.1 | forge | t0ch1na-autocloud-1.0.0-beta.5-1.20.1-forge.jar |
| 1.20.1 | neoforge | t0ch1na-autocloud-1.0.0-beta.5-1.20.1-neoforge.jar |
| 1.21.1 | fabric | t0ch1na-autocloud-1.0.0-beta.5-1.21.1-fabric.jar |
| 1.21.1 | forge | t0ch1na-autocloud-1.0.0-beta.5-1.21.1-forge.jar |
| 1.21.1 | neoforge | t0ch1na-autocloud-1.0.0-beta.5-1.21.1-neoforge.jar |

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
