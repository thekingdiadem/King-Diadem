"""โลโก้มงกุฎเวกเตอร์ + ภาพแชร์ลิงก์ — ทุกหน้าต้องใช้ไอคอนเดียวกัน และหน้าหลักมีภาพตอนแชร์ในไลน์/เฟซ"""
import glob
import re

from PIL import Image


def test_icons_are_built_from_the_master_logo():
    """โลโก้ใหม่ (ดาวในวงแหวน) เป็นภาพ — ต้นฉบับ static/brand/logo-master.png สร้างทุกขนาดด้วย scripts/build_icons.py
    ทุกไฟล์ < 1MB (GitHub ไม่รับภาพเกิน 1MB) · ไอคอนแอปทึบ (iOS ทำขอบโปร่งเป็นสีดำ)"""
    import os
    m = Image.open("static/brand/logo-master.png")
    assert m.mode == "RGBA" and max(m.size) == 1024
    # ดาวกลางโลโก้ต้องทึบ — ไฟล์ที่ลบพื้นขาวทิ้งเคยลบดาวสีขาวไปด้วยจนเป็นรู
    w, h = m.size
    assert m.getpixel((w // 2, int(h * .30)))[3] == 255     # จุดนี้ในไฟล์ที่ลบพื้นขาวเคยโปร่ง 100%
    for f, size in (("static/icons/icon-512.png", 512), ("static/icons/icon-192.png", 192),
                    ("static/icons/maskable-512.png", 512), ("static/icons/apple-touch-icon.png", 180),
                    ("static/icons/favicon-48.png", 48), ("static/logo.png", 256)):
        im = Image.open(f)
        assert im.size == (size, size), f
        assert os.path.getsize(f) < 1_000_000, f
        if "icons/" in f:
            assert im.mode == "RGB", f
    assert os.path.getsize("static/brand/logo-master.png") < 1_000_000


def test_every_page_uses_the_same_icon():
    for f in glob.glob("static/*.html"):
        s = open(f, encoding="utf-8").read()
        assert '<link rel="icon" href="/static/icons/favicon-48.png" sizes="48x48" type="image/png">' in s, f
        assert 'href="/static/logo.svg"' not in s, f


def test_share_image_is_full_size_and_on_main_pages():
    assert Image.open("static/og.jpg").size == (1200, 630)
    for f in ("static/index.html", "static/king_diadem_universe.html", "static/ask.html"):
        s = open(f, encoding="utf-8").read()
        assert re.search(r'og:image" content="https://[^"]+/static/og\.jpg"', s), f
        assert 'twitter:card" content="summary_large_image"' in s


def test_inputs_have_accessible_names():
    """โปรแกรมอ่านหน้าจอเคยได้แค่ placeholder ซึ่งหายไปทันทีที่เริ่มพิมพ์"""
    uni = open("static/king_diadem_universe.html", encoding="utf-8").read()
    assert re.search(r'id="intent-text"[^>]*aria-label=|aria-label=[^>]*id="intent-text"', uni)
    ask = open("static/ask.html", encoding="utf-8").read()
    assert 'aria-label="ตัวเลือก A"' in ask and 'aria-label="ตัวเลือก B"' in ask
    assert "esc(p.text)" in uni and "esc(p.letter)" in uni
