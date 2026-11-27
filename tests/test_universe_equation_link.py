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


def test_equations_page_explains_choice_floor_honestly():
    """หัวข้อ 3 ต้องบอกตรงๆ ว่าโค้ดตอนนี้บังคับ Choice ไม่ต่ำกว่า 1 — ถ้าโค้ดเปลี่ยน ข้อความต้องเปลี่ยนตาม"""
    html = (ROOT / "static/equations.html").read_text(encoding="utf-8")
    assert 'id="collapse"' in html and "Choice(t+1) = 0" in html
    src = (ROOT / "ENGINE/risk_engine.py").read_text(encoding="utf-8")
    if "max(1, int((100 - risk_score) / 20))" in src:
        assert "max(1, ⌊(100 − Risk) / 20⌋)" in html
    assert ("choice_measured" in src) == ("choice_measured" in html)
