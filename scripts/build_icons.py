"""สร้างไอคอนแอปทุกขนาดจาก static/logo.svg (มงกุฎเวกเตอร์ — คมทุกขนาด) และภาพแชร์ลิงก์ static/og.jpg

ใช้:  python scripts/build_icons.py [ภาพปกต้นฉบับสำหรับ og.jpg]
ต้องมี Playwright + Chromium (เรนเดอร์ SVG ให้ตรงกับที่เบราว์เซอร์เห็น)
"""
import asyncio
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC = os.path.join(ROOT, "static")
SIZES = {"icons/icon-192.png": (192, 1.0), "icons/icon-512.png": (512, 1.0),
         "icons/apple-touch-icon.png": (180, 1.0), "logo.png": (256, 1.0),
         "icons/maskable-512.png": (512, 0.8)}     # maskable: ย่อมงกุฎให้อยู่ในวง 80% ที่ระบบไม่ตัด


async def render():
    from playwright.async_api import async_playwright
    svg = open(os.path.join(STATIC, "logo.svg"), encoding="utf-8").read()
    async with async_playwright() as p:
        exe = os.environ.get("CHROMIUM") or None
        b = await p.chromium.launch(executable_path=exe)
        for out, (px, scale) in SIZES.items():
            pg = await b.new_page(viewport={"width": px, "height": px}, device_scale_factor=1)
            inner = int(px * scale)
            pad = (px - inner) // 2
            # maskable ต้องเต็มกรอบ — พื้นสีเดียวกับมุมของโลโก้ แล้ววางโลโก้ไว้กลาง
            await pg.set_content(f"<html><body style='margin:0;background:{'#04050d' if scale < 1 else 'transparent'}'>"
                                 f"<div style='padding:{pad}px'><div style='width:{inner}px;height:{inner}px'>{svg}</div></div>"
                                 "</body></html>")
            await pg.screenshot(path=os.path.join(STATIC, out), omit_background=scale >= 1,
                                clip={"x": 0, "y": 0, "width": px, "height": px})
            await pg.close()
        await b.close()


def og(src):
    """ภาพแชร์ลิงก์ 1200×630 — ครอปจากภาพปกที่ความละเอียดเต็ม (ไม่ขยายเกินต้นฉบับมาก)"""
    im = Image.open(src).convert("RGB")
    w, h = im.size
    ch = round(w * 630 / 1200)
    top = max(0, min(h - ch, round(h * 0.105)))   # ไม่ให้ศีรษะคนในภาพโผล่ที่ขอบล่าง
    im.crop((0, top, w, top + ch)).resize((1200, 630), Image.LANCZOS) \
        .save(os.path.join(STATIC, "og.jpg"), quality=90, optimize=True, progressive=True)


if __name__ == "__main__":
    asyncio.run(render())
    if len(sys.argv) > 1:
        og(sys.argv[1])
    # iOS ไม่รองรับไอคอนโปร่งใส (ขอบกลายเป็นสีดำ) — apple-touch-icon ต้องเป็นภาพทึบ
    ap = os.path.join(STATIC, "icons/apple-touch-icon.png")
    im = Image.open(ap).convert("RGBA")
    bg = Image.new("RGBA", im.size, (4, 5, 13, 255))
    Image.alpha_composite(bg, im).convert("RGB").save(ap, optimize=True)
    for f in list(SIZES) + ["og.jpg"]:
        path = os.path.join(STATIC, f)
        if os.path.exists(path):
            print(f, Image.open(path).size, os.path.getsize(path) // 1024, "KB")
