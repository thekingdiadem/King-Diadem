"""เบอร์ในคำตอบต้องแตะโทรได้ — เดิมแตะได้แค่เบอร์ไทยกับ 911/988/112/999 (110 จีน · 119 ญี่ปุ่น · 109 เกาหลี ฯลฯ แตะไม่ได้)"""
import re
import sys

import pytest
from tests._front import front_page  # noqa: E402

sys.path.insert(0, ".")
from scripts.build_translation_review import numbers, table  # noqa: E402

HTML = front_page()
HOT = re.compile(re.search(r"var HOTLINES = /(.*)/g;", HTML).group(1).replace("\\/", "/"))


def _linked(s):
    return [m.group(2) for m in HOT.finditer(s)]


@pytest.mark.parametrize("s,n", [("拨打 110 报警", "110"), ("119に電話", "119"), ("상담전화 109", "109"),
                                 ("appelez le 3114", "3114"), ("โทร 1669 ตอนนี้", "1669"), ("call 1155", "1155")])
def test_hotlines_become_links(s, n):
    assert n in _linked(s)


@pytest.mark.parametrize("s", ["ราคา 110 บาท", "กดหน้าอก 100–120 ครั้ง", "ปี 2019", "เบอร์ 08-1101-2345", "เงินเดือน 1300 บาท"])
def test_money_years_and_rates_are_not_links(s):
    assert _linked(s) == []


def test_every_short_number_in_the_54_language_replies_is_tappable():
    """ทุกเบอร์ 3–4 หลักในคำตอบทุกภาษา ต้องอยู่ในรายการแตะโทร (ยกเว้นอัตรากดหน้าอก 100–120 ครั้งต่อนาที
    และ #8008 ของญี่ปุ่นที่ต้องกด # นำหน้าและโทรได้เฉพาะในญี่ปุ่น)"""
    missing = set()
    for topics in table().values():
        for msg in topics.values():
            for n in numbers(msg):
                n = n.replace(" ", "").replace("-", "")
                if n.isascii() and n.isdigit() and 3 <= len(n) <= 4 and n not in ("100", "120", "0800", "8008"):
                    if not _linked(f"โทร {n} ตอนนี้"):
                        missing.add(n)
    assert not missing, sorted(missing)


def test_report_page_uses_the_same_hotline_list():
    rep = open("static/report.html", encoding="utf-8").read()
    assert re.search(r"var HOTLINES = /(.*)/g;", rep).group(1) == re.search(r"var HOTLINES = /(.*)/g;", HTML).group(1)
    assert "telify(esc(d.ai_response" in rep


def test_offline_page_numbers_are_tappable():
    """หน้าออฟไลน์: ไม่มีเน็ตก็ยังโทรได้ — เดิมเบอร์เป็นตัวหนังสือธรรมดา"""
    off = open("static/offline.html", encoding="utf-8").read()
    for n in ("1669", "191", "1323", "1155"):
        assert f'href="tel:{n}"' in off
