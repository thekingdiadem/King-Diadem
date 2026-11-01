"""สร้างไอคอนแอปทุกขนาด + favicon + logo.png จากโลโก้ต้นฉบับ static/brand/logo-master.png
และภาพแชร์ลิงก์ static/og.jpg จากภาพแบนเนอร์ (ถ้าให้มา)

ใช้:  python scripts/build_icons.py [ภาพแบนเนอร์สำหรับ og.jpg]

โลโก้ปัจจุบัน (ดาวในวงแหวน ฟ้า–ส้ม) เป็นภาพ ไม่ใช่เวกเตอร์ — ต้นฉบับเก็บไว้ 1024px โปร่งใส
ส่วนสีขาว (ดาว ลูกศร) ทึบแล้ว: ไฟล์ PNG ที่ลบพื้นขาวทิ้งมักลบสีขาวในโลโก้ไปด้วยจนเป็นรู
ทุกไฟล์ที่สร้างเล็กกว่า 1MB (GitHub ไม่รับภาพเกิน 1MB ผ่านหน้าเว็บ)
ต้องมีแค่ Pillow
"""
import os
import sys

from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC = os.path.join(ROOT, "static")
MASTER = os.path.join(STATIC, "brand", "logo-master.png")
BG_IN, BG_OUT = (20, 26, 64), (4, 5, 13)      # พื้นอวกาศ: กลางน้ำเงินลึก → ขอบดำเดียวกับธีมเว็บ
# (ขนาด, สัดส่วนโลโก้ต่อกรอบ) · maskable: Android ตัดเป็นวงกลม/สี่เหลี่ยมมน ต้องอยู่ในวง 80% กลาง
SIZES = {"icons/icon-512.png": (512, .92), "icons/icon-192.png": (192, .92),
         "icons/maskable-512.png": (512, .72), "icons/apple-touch-icon.png": (180, .86),
         "icons/favicon-48.png": (48, .96)}


def space(n):
    """พื้นไล่สีแบบวงกลม (ทึบ — iOS ไม่รองรับไอคอนโปร่งใส ขอบจะกลายเป็นสีดำ)"""
    g = Image.radial_gradient("L").resize((n, n), Image.BICUBIC)        # 0 กลาง → 255 ขอบ
    g = g.point(lambda v: min(255, int(v * 1.25)))
    return Image.composite(Image.new("RGB", (n, n), BG_OUT), Image.new("RGB", (n, n), BG_IN), g).convert("RGBA")


def fitted(logo, n, scale):
    w = int(n * scale)
    h = int(w * logo.height / logo.width)
    small = logo.resize((w, h), Image.LANCZOS)
    # ดาวคม: unsharp ตามขนาด แล้วคืน alpha เดิม (ไม่ให้ขอบโปร่งเป็นเส้นแข็ง)
    sharp = small.convert("RGB").filter(ImageFilter.UnsharpMask(radius=max(.6, n / 512), percent=70, threshold=2)).convert("RGBA")
    sharp.putalpha(small.getchannel("A"))
    return sharp


def build():
    logo = Image.open(MASTER).convert("RGBA")
    for out, (n, scale) in SIZES.items():
        im = space(n)
        l = fitted(logo, n, scale)
        im.alpha_composite(l, ((n - l.width) // 2, (n - l.height) // 2))
        im.convert("RGB").save(os.path.join(STATIC, out), optimize=True)
    l = fitted(logo, 256, 1.0)
    l.thumbnail((256, 256), Image.LANCZOS)
    c = Image.new("RGBA", (256, 256))
    c.alpha_composite(l, ((256 - l.width) // 2, (256 - l.height) // 2))
    c.save(os.path.join(STATIC, "logo.png"), optimize=True)


def og(src):
    """ภาพแชร์ลิงก์ 1200×630 — ครอปจากแบนเนอร์ให้ทั้งโลโก้และชื่อ KING DIADEM อยู่ในกรอบ"""
    im = Image.open(src).convert("RGB")
    w, h = im.size
    ch = round(w * 630 / 1200)
    top = max(0, min(h - ch, round(h * 0.105)))
    im.crop((0, top, w, top + ch)).resize((1200, 630), Image.LANCZOS) \
        .filter(ImageFilter.UnsharpMask(radius=.8, percent=50, threshold=2)) \
        .save(os.path.join(STATIC, "og.jpg"), quality=86, optimize=True, progressive=True)


if __name__ == "__main__":
    build()
    if len(sys.argv) > 1:
        og(sys.argv[1])
    for f in list(SIZES) + ["logo.png", "og.jpg", "brand/logo-master.png"]:
        path = os.path.join(STATIC, f)
        print(f, Image.open(path).size, os.path.getsize(path) // 1024, "KB")
