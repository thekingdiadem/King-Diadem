"""สร้างไอคอนแอปทุกขนาด + favicon + logo.png จากโลโก้เวกเตอร์ static/logo.svg (ดาวในวงแหวน — คมทุกขนาด)
และภาพแชร์ลิงก์ static/og.jpg จากภาพแบนเนอร์ (ถ้าให้มา)

ใช้:  python scripts/build_icons.py [ภาพแบนเนอร์สำหรับ og.jpg]
ต้องมี Pillow + Playwright/Chromium (เรนเดอร์ SVG ให้ตรงกับที่เบราว์เซอร์เห็น) · ระบุตัว Chromium ได้ด้วย CHROMIUM=/path
ทุกไฟล์ที่สร้างเล็กกว่า 1MB (GitHub ไม่รับภาพเกิน 1MB ผ่านหน้าเว็บ)
"""
import asyncio
import io
import os
import sys

from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC = os.path.join(ROOT, "static")
SVG = os.path.join(STATIC, "logo.svg")
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


async def _render(sizes):
    """เรนเดอร์ logo.svg แบบโปร่งใสตามขนาด → {px: Image}"""
    from playwright.async_api import async_playwright
    svg = open(SVG, encoding="utf-8").read().replace("<svg ", '<svg width="100%" height="100%" ', 1)
    out = {}
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=os.environ.get("CHROMIUM") or None)
        for px in sorted(set(sizes)):
            pg = await b.new_page(viewport={"width": px, "height": px})
            await pg.set_content(f"<html><body style='margin:0;background:transparent'><div style='width:{px}px;height:{px}px'>{svg}</div></body></html>")
            out[px] = Image.open(io.BytesIO(await pg.screenshot(omit_background=True))).convert("RGBA")
            await pg.close()
        await b.close()
    return out


def build():
    inner = {out: int(n * scale) for out, (n, scale) in SIZES.items()}
    art = asyncio.run(_render(list(inner.values()) + [256]))
    for out, (n, _) in SIZES.items():
        im = space(n)
        l = art[inner[out]]
        im.alpha_composite(l, ((n - l.width) // 2, (n - l.height) // 2))
        im.convert("RGB").save(os.path.join(STATIC, out), optimize=True)
    art[256].save(os.path.join(STATIC, "logo.png"), optimize=True)


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
    for f in list(SIZES) + ["logo.png", "og.jpg", "logo.svg"]:
        path = os.path.join(STATIC, f)
        print(f, "" if f.endswith(".svg") else Image.open(path).size, os.path.getsize(path) // 1024, "KB")
