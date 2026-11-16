"""สร้างภาพไฟเมืองจาก NASA Black Marble 2016 (VIIRS Day/Night Band) — 2K · 4K · 8K

ต้นฉบับ (สาธารณสมบัติ, NASA Earth Observatory · ภาพ 144898):
  https://assets.science.nasa.gov/content/dam/science/esd/eo/images/imagerecords/144000/144898/BlackMarble_2016_3km.jpg
  13500×6750 พิกเซล ≈ 3 กม./พิกเซล — เห็นเส้นถนนที่เชื่อมเมืองเป็นใยแสง (ภาพเดิมของ three-globe เป็นข้อมูลปี 2012 ที่ละเอียดน้อยกว่า)

ภาพต้นฉบับมีพื้นแผ่นดิน/น้ำแข็งสีน้ำเงินอมม่วงอยู่ใต้แสงไฟ — แยกเฉพาะแสงไฟด้วย (R − 0.65·B) / 0.5
  · พื้นหลังสีน้ำเงิน R น้อยกว่า 0.65·B เสมอ → 0
  · ไฟเหลือง/ขาว R สูง → สว่าง · หาร 0.5 (ไม่ใช่ 0.35) เพื่อให้ใจกลางเมืองยังไล่ระดับความสว่างได้ ไม่ขาวจ้าเท่ากันหมด

ใช้:  python scripts/build_earth_lights_2016.py <ไฟล์ BlackMarble_2016_3km.jpg>
"""
import os
import sys

from PIL import Image

Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "static", "earth")
SIZES = {"lights.jpg": 2048, "lights_4k.jpg": 4096, "lights_8k.jpg": 8192}


def extract(src):
    r, _g, b = Image.open(src).convert("RGB").split()
    lut_b = [int(v * 0.65) for v in range(256)]
    from PIL import ImageChops
    return ImageChops.subtract(r, b.point(lut_b), scale=0.5)


def main(src):
    lit = extract(src)
    for name, w in SIZES.items():
        lit.resize((w, w // 2), Image.LANCZOS).save(os.path.join(OUT, name), quality=88, optimize=True, progressive=True)
        print(name, os.path.getsize(os.path.join(OUT, name)) // 1024, "KB")


if __name__ == "__main__":
    main(sys.argv[1])
