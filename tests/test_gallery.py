"""แกลเลอรีจักรวาล (index.html ที่ root) — ทุกไฟล์ที่แกลเลอรีโหลดต้องมีอยู่จริง

แกลเลอรีกางงานภาพใน static/ ที่แอปไม่ได้โหลดแล้ว ถ้าวันหนึ่งย้ายหรือลบไฟล์ไป แกลเลอรีจะว่างเปล่าแบบเงียบๆ
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()


def test_every_showcased_file_exists():
    files = set(re.findall(r"'(static/[\w./-]+\.(?:js|html))'", HTML))
    assert len(files) >= 10
    missing = [f for f in files if not os.path.exists(os.path.join(ROOT, f))]
    assert not missing


def test_links_point_at_real_pages():
    nav = re.search(r'<nav class="links".*?</nav>', HTML, re.S).group(0)
    hrefs = re.findall(r'href="((?!https?:|#)[^"]+)"', nav)
    assert hrefs
    for href in hrefs:
        assert os.path.exists(os.path.join(ROOT, href)), href


def test_gallery_is_mobile_ready():
    assert 'name="viewport"' in HTML and "IntersectionObserver" in HTML
