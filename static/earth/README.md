# ภาพโลกของหน้าแรก

โลกหน้าแรก (`static/index.html` → ฉากหน้าแรกใน `Cosmos`) วาดด้วย WebGL จากภาพสามภาพนี้

| ไฟล์ | ขนาด | ที่มา |
|---|---|---|
| `day.jpg` | 2048×1024 | NASA Blue Marble (พื้นผิวโลกตอนกลางวัน) |
| `lights.jpg` | 2048×1024 | NASA Earth at Night (Black Marble) — สกัดเฉพาะแสงเมือง เป็นภาพขาวดำ |
| `clouds.jpg` | 2048×1024 | ภาพเมฆทั้งโลก (ช่องความโปร่งใสของ `clouds.png`) |

ภาพต้นฉบับมาจากโฟลเดอร์ตัวอย่างของแพ็กเกจ npm `three-globe` (`example/img/earth-blue-marble.jpg`,
`example/img/earth-night.jpg`) และ `globe.gl` (`example/clouds/clouds.png`) ซึ่งเป็นสัญญาอนุญาต MIT
ภาพโลกของ NASA เป็นสาธารณสมบัติ (NASA imagery is not subject to copyright in the United States)
ขอบคุณ NASA Earth Observatory / NASA Visible Earth

ย่อขนาดและสกัดแสงเมืองด้วย Pillow: แสงเมือง = `min(R, G) − 0.25·B` (ตัดพื้นแผ่นดินสีน้ำเงินของภาพกลางคืนออก)

## ภาพ 4K และข้อมูลเพิ่ม (หน้า Universe)

| ไฟล์ | ขนาด | ที่มา |
|---|---|---|
| `lights_4k.jpg` · `day_4k.jpg` · `clouds_4k.jpg` | 4096×2048 | ภาพ NASA เดิมจาก `three-globe` (MIT) ความละเอียดเต็ม — สร้างด้วย `scripts/build_earth_textures.py` |
| `water.png` | 2048×1024 | แผนที่น้ำ (`three-globe` example/img/earth-water.png) — ใช้ทำประกายแสงจันทร์บนทะเล |
| `capitals.json` | 241 เมือง | เมืองหลวงทุกประเทศ/ดินแดน จาก GeoNames (CC BY 4.0) ผ่านแพ็กเกจ `all-the-cities` (MIT) — รหัส PPLC |

ภาพ 4K โหลดหลังภาพ 2K ขึ้นแล้ว และเฉพาะเครื่องที่รองรับภาพกว้าง 4096 พิกเซล (ไม่โหลดในโหมดประหยัดเน็ต)
ชื่อเมืองหลวงจะแสดงเฉพาะตอนซูมเข้าใกล้ — มุมมองปกติไม่มีอะไรทับภาพโลก
