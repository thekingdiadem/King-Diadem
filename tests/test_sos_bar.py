"""แถบโทรฉุกเฉิน: มีเบอร์จริง กดได้ด้วยลิงก์ tel: และโผล่ทุกครั้งที่แสดงการ์ดฉุกเฉิน · /safe สอนตั้ง SOS ของมือถือ"""
from pathlib import Path

from tests._front import front_page

ROOT = Path(__file__).resolve().parent.parent


def test_sos_bar_has_real_numbers_and_location():
    page = front_page()
    i = page.index('id="sos-bar"'); bar = page[i:page.index('</div>', i)]
    assert 'href="tel:191"' in bar and 'href="tel:1669"' in bar and 'href="/safe"' in bar


def test_crisis_card_opens_sos_bar():
    js = (ROOT / "static/app.js").read_text(encoding="utf-8")
    body = js[js.index("function crisisCard(){"):js.index("}", js.index("function crisisCard(){"))]
    assert "showSos()" in body


def test_safe_page_teaches_phone_sos():
    html = (ROOT / "static/safe.html").read_text(encoding="utf-8")
    assert 'id="sos"' in html and "5 ครั้ง" in html


def test_sos_bar_does_not_cover_chat_box_and_close_is_tappable():
    """บนจอเล็ก (iPhone SE) แถบเคยบังช่องพิมพ์ · ปุ่มปิดเคยเล็ก 30px ต่ำกว่าขนาดกดได้ 44px"""
    import re
    from tests._front import front_page
    page = front_page()
    assert re.search(r"function showSos\(\)\{.*setProperty\('--sos-h', b\.offsetHeight", page)
    assert "height:calc(100dvh - var(--sos-h,0px))" in page and "removeProperty('--sos-h')" in page
    assert re.search(r"#sos-bar \.sos-x\{[^}]*width:44px;height:44px", page)


def test_sos_close_listens_on_document():
    """app.js อยู่ก่อน #sos-bar ใน index.html — getElementById('sos-x') ตอนโหลดได้ null ปุ่มปิดเลยไม่เคยทำงาน"""
    from tests._front import front_page
    page = front_page()
    assert "document.getElementById('sos-x')" not in page and "closest('#sos-x')" in page
