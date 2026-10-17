"""โลโก้มงกุฎเวกเตอร์ + ภาพแชร์ลิงก์ — ทุกหน้าต้องใช้ไอคอนเดียวกัน และหน้าหลักมีภาพตอนแชร์ในไลน์/เฟซ"""
import glob
import re

from PIL import Image


def test_logo_is_vector_and_icons_are_built_from_it():
    svg = open("static/logo.svg", encoding="utf-8").read()
    assert svg.startswith("<svg") and 'viewBox="0 0 512 512"' in svg and "<image" not in svg   # เวกเตอร์ล้วน ไม่ฝังภาพ
    for f, size in (("static/icons/icon-512.png", 512), ("static/icons/icon-192.png", 192), ("static/logo.png", 256)):
        assert Image.open(f).size == (size, size)


def test_every_page_uses_the_crown_icon():
    for f in glob.glob("static/*.html"):
        s = open(f, encoding="utf-8").read()
        assert '<link rel="icon" href="/static/logo.svg"' in s, f


def test_share_image_is_full_size_and_on_main_pages():
    assert Image.open("static/og.jpg").size == (1200, 630)
    for f in ("static/index.html", "static/king_diadem_universe.html", "static/ask.html"):
        s = open(f, encoding="utf-8").read()
        assert re.search(r'og:image" content="https://[^"]+/static/og\.jpg"', s), f
        assert 'twitter:card" content="summary_large_image"' in s
