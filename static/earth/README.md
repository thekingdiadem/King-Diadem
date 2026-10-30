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

| `admin1.json` | 3,539 เมือง | เมืองศูนย์กลางจังหวัด/รัฐ (GeoNames PPLA) — 76 จังหวัดของไทยมีชื่อไทยในช่องที่ 4 |
| `cities_t2–t5.json` | ~46,000 เมือง | เมืองอื่นตามประชากร 200k+ · 50k+ · 15k+ · 5k+ เรียงใหญ่ไปเล็ก |

ชื่อเมืองสร้างด้วย `scripts/build_earth_cities.py` จาก `all-the-cities@3.1.0` (MIT · ข้อมูล GeoNames CC BY 4.0)
ป้ายวาดตามลำดับ เมืองหลวง → ศูนย์กลางจังหวัด → เมืองใหญ่ไปเล็ก ชนกันแล้วป้ายที่สำคัญน้อยกว่าหลีกทาง

ภาพ 4K โหลดหลังภาพ 2K ขึ้นแล้ว และเฉพาะเครื่องที่รองรับภาพกว้าง 4096 พิกเซล (ไม่โหลดในโหมดประหยัดเน็ต)
ชื่อเมืองหลวงจะแสดงเฉพาะตอนซูมเข้าใกล้ — มุมมองปกติไม่มีอะไรทับภาพโลก

## ท้องฟ้าจริงหน้าแรก (`sky_taurus.json`)

- ดาว 5,804 ดวงรอบดาวลูกไก่ (ห่างไม่เกิน 55° · สว่างกว่าโชติมาตร 7.5) — ตำแหน่ง J2000 · โชติมาตร · สี B−V
- ข้อมูลจากแคตตาล็อก Hipparcos (ESA) ผ่านแพ็กเกจ [d3-celestial](https://github.com/ofrohn/d3-celestial) 0.7.35
  — BSD-3-Clause · Copyright (c) 2015, Olaf Frohn
- สร้างใหม่ได้ด้วย `scripts/build_sky_stars.py`
