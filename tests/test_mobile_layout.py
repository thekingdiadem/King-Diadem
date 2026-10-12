"""ของที่คนเปิดบนมือถือเห็นจริง (พบจากการไล่เปิดทุกหน้าที่จอกว้าง 360px)

- หน้า /architecture: คำอธิบายไฟล์ที่ยาวติดกันไม่มีช่องว่าง (เช่น RESET/NO_FOOD/NO_SHELTER, ก→ข→ค)
  เคยดันรายการให้กว้าง ~430px บนจอ 360px แล้ว body ซ่อนส่วนเกิน — ท้ายประโยคจึงหายไปเฉยๆ
- ลิงก์กลับหน้าหลัก/คู่มือในหน้า ask, guide, letter เคยสูงแค่ 13–19px กดด้วยนิ้วยาก
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _page(name):
    return (ROOT / "static" / name).read_text(encoding="utf-8")


def _rule(html, selector):
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", html)
    assert m, selector
    return m.group(1)


def test_architecture_file_notes_wrap_instead_of_overflowing():
    html = _page("architecture.html")
    span = _rule(html, ".flist span")
    assert "overflow-wrap: anywhere" in span and "min-width: 0" in span
    # คอลัมน์คำอธิบายต้องหดได้ต่ำกว่าความยาวคำ (1fr เฉยๆ = minmax(auto,1fr) จะไม่ยอมหด)
    cols = re.findall(r"\.flist li \{[^}]*grid-template-columns:([^;]+);", html)
    assert len(cols) == 2
    for c in cols:
        assert c.strip().endswith("minmax(0, 1fr)"), c


def test_small_nav_links_have_finger_sized_tap_area():
    ask = _page("ask.html")
    assert "min-height:32px" in _rule(ask, ".back")
    assert re.search(r"padding:9px 8px", _rule(ask, ".nav-row a"))
    assert "min-height: 32px" in _rule(_page("guide.html"), ".back-link")
    assert "padding: 9px 10px" in _rule(_page("letter.html"), ".back")
