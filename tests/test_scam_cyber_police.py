"""โดนหลอกในทุกภาษาต้องได้ทางแจ้งตำรวจไซเบอร์ (1441 · thaipoliceonline.go.th) และเบอร์ของประเทศตัวเอง
เดิมภาษาจีนไม่มีเบอร์เลย เวียดนาม เกาหลี ญี่ปุ่น สเปน ไม่มีช่องทางแจ้งเรื่องโดนหลอก"""
import re

import pytest

from core.kernel_voice import compose

CASES = {
    "มีคนโทรมาอ้างเป็นตำรวจให้โอนเงิน": ["1441"],
    "I got scammed online and sent money": ["1441", "thaipoliceonline"],
    "Tôi bị lừa đảo chuyển tiền": ["1441", "113"],
    "toi bi lua mat tien": ["1441", "113"],
    "我被网上诈骗了": ["1441", "96110"],
    "사기당했어요 돈을 보냈어요": ["1441", "1332"],
    "詐欺にあってお金を送ってしまった": ["1441", "188"],
    "Me estafaron por internet": ["1441", "thaipoliceonline"],
}


@pytest.mark.parametrize("text", CASES)
def test_scam_reply_has_cyber_police_and_home_number(text):
    out = compose(text, footer=False)
    for need in CASES[text]:
        assert re.search(rf"(?<!\d){re.escape(need)}(?!\d)", out), (text, need)
    assert out.count("1441") <= 2


@pytest.mark.parametrize("text", ["什么是诈骗", "lừa đảo là gì", "how are you today", "ทำงานเหนื่อยจัง"])
def test_not_a_scam_gets_no_scam_line(text):
    assert "thaipoliceonline" not in compose(text, footer=False)
