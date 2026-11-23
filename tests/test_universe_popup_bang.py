"""ป้ายภัยพิบัติบนลูกโลก + ตอนจบฉากบิ๊กแบง"""
from pathlib import Path

UNI = Path("static/king_diadem_universe.html").read_text(encoding="utf-8")
BB = Path("static/big_bang.js").read_text(encoding="utf-8")


def test_popup_icons_not_stretched_by_globe_svg_rule():
    # กฎ .cockpit svg (ยืดเต็มจอให้ลูกโลก) เคยทำให้ไอคอนห่วงยาง/หนังสือในป้ายใหญ่ทับข้อความ
    assert ".cockpit svg{position:absolute" in UNI
    assert ".cockpit svg.kd-i{position:static" in UNI


def test_bang_fades_to_black_before_revealing_page():
    # ฉากต้องมืดก่อนหน้าเว็บโผล่ ไม่ให้ฟ้าในฉากซ้อนกับหน้าจนจอเป็นสีฟ้า
    assert "cv.style.opacity = Math.max(0, o * 2 - 1)" in BB
    assert "root.style.opacity = Math.min(1, o * 2)" in BB
    assert "cv.style.opacity = 1;" in BB          # เปิดดูซ้ำต้องคืนค่าความทึบ


def test_saturn_reply_hides_markdown_stars():
    s = Path("static/black_saturn.html").read_text(encoding="utf-8")
    assert "ans.replace(/\\*\\*([^*\\n]+)\\*\\*/g, '$1')" in s


def test_bang_has_no_android_blue_tap_flash():
    assert "#big-bang{-webkit-tap-highlight-color:transparent" in UNI
    assert "#big-bang *{-webkit-tap-highlight-color:transparent}" in UNI


def test_equations_linked_from_app():
    assert 'href="/equations"' in UNI
    assert 'href="/equations"' in Path("static/index.html").read_text(encoding="utf-8")
