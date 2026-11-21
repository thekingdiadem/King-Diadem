"""หน้าเว็บบนคอมเคยเฟรมตก: กระจกเบลอหลายชิ้นต้องเบลอใหม่ทุกเฟรมเพราะฉากข้างหลังขยับ"""
import re
from tests._front import front_page


def test_repeated_elements_have_no_backdrop_blur():
    css = open("static/app.css", encoding="utf-8").read()
    for sel in (r"\.sugg button\{", r"\.m\.a \.bubble,\.m\.e \.bubble\{max-width"):
        rule = re.search(sel + r"[^}]*\}", css).group(0)
        assert "backdrop-filter" not in rule, rule


def test_auto_lite_mode_exists_and_turns_off_blur():
    page = front_page()
    assert "function perfLite()" in page and "perfWatch(PERF.raw, PERF.gap)" in page
    assert "html.kd-lite *" in page and "backdrop-filter:none!important" in page
    # แท็บที่ถูกพักไว้ต้องไม่ถูกนับว่าเครื่องช้า
    assert "document.hidden) return;" in page
