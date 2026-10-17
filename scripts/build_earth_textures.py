"""สร้างภาพโลกความละเอียด 4K (4096×2048) สำหรับหน้า Universe — โหลดเสริมหลังภาพ 2K เมื่อเครื่องรองรับ

ต้นฉบับ (สัญญาอนุญาตเปิด):
  · three-globe (MIT) example/img/earth-night.jpg · earth-blue-marble.jpg · example/clouds/clouds.png — ภาพ NASA (สาธารณสมบัติ)

ใช้:  npm pack three-globe@2.45.6   (แล้วแตกไฟล์)
      python scripts/build_earth_textures.py <โฟลเดอร์ package ของ three-globe>
"""
import os
import sys

from PIL import Image, ImageChops, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "static", "earth")
W, H = 4096, 2048


def lights(src):
    """แสงเมือง = min(R, G) − 0.25·B (ตัดพื้นแผ่นดินสีน้ำเงินของภาพกลางคืนออก) — สูตรเดียวกับภาพ 2K เดิม"""
    r, g, b = Image.open(src).convert("RGB").resize((W, H), Image.LANCZOS).split()
    m = ImageChops.darker(r, g)
    return ImageChops.subtract(m, b.point(lambda v: int(v * 0.25)))



def main(globe_pkg):
    os.makedirs(OUT, exist_ok=True)
    img = os.path.join(globe_pkg, "example", "img")
    lights(os.path.join(img, "earth-night.jpg")).save(os.path.join(OUT, "lights_4k.jpg"), quality=86, optimize=True)
    Image.open(os.path.join(img, "earth-blue-marble.jpg")).convert("RGB").resize((W, H), Image.LANCZOS) \
        .save(os.path.join(OUT, "day_4k.jpg"), quality=82, optimize=True)
    clouds = Image.open(os.path.join(globe_pkg, "example", "clouds", "clouds.png")).convert("RGBA").getchannel("A")  # ภาพ palette — ความหนาของเมฆอยู่ในช่องโปร่งใส
    clouds.resize((W, H), Image.LANCZOS).save(os.path.join(OUT, "clouds_4k.jpg"), quality=72, optimize=True)
    # แผนที่น้ำ (ขาว = ทะเล/ทะเลสาบ) — ใช้แยกผิวน้ำให้มีประกายแสงจันทร์และระลอกคลื่น
    water = Image.open(os.path.join(img, "earth-water.png")).convert("L").resize((W // 2, H // 2), Image.LANCZOS)
    water.save(os.path.join(OUT, "water.png"), optimize=True)
    for f in ("lights_4k.jpg", "day_4k.jpg", "clouds_4k.jpg", "water.png"):
        print(f, os.path.getsize(os.path.join(OUT, f)) // 1024, "KB")


if __name__ == "__main__":
    main(sys.argv[1])
