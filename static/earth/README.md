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
