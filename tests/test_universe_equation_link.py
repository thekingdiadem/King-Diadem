"""สมการ Choice(t) ≥ 1 ในหน้าจักรวาลต้องกดแล้วไปหน้า /equations ตรงหัวข้อนั้น"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_hero_equation_links_to_equations_page():
    html = (ROOT / "static/king_diadem_universe.html").read_text(encoding="utf-8")
    m = re.search(r'<a class="hero-rule" href="([^"]+)"[^>]*>(.*?)</a>', html, re.S)
    assert m, "สมการหลักในหน้าจักรวาลยังไม่เป็นลิงก์"
    assert m.group(1) == "/equations#choice"
    assert "Choice(t) ≥ 1" in m.group(2)


def test_equations_page_has_anchor_targets():
    html = (ROOT / "static/equations.html").read_text(encoding="utf-8")
    assert 'id="choice"' in html and 'id="risk"' in html
