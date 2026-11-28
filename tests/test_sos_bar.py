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
