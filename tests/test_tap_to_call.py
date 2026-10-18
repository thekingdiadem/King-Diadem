"""เบอร์ในคำตอบต้องแตะโทรได้ — เดิมแตะได้แค่เบอร์ไทยกับ 911/988/112/999 (110 จีน · 119 ญี่ปุ่น · 109 เกาหลี ฯลฯ แตะไม่ได้)"""
import re
import sys

import pytest

sys.path.insert(0, ".")
from scripts.build_translation_review import numbers, table  # noqa: E402

HTML = open("static/index.html", encoding="utf-8").read()
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
