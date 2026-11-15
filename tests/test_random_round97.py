"""รอบสุ่ม 97: ข้อความสั้นมาก (คนพิมพ์ได้แค่คำเดียว)"""
import re

import pytest
from core.kernel_voice import assess, compose

HELP = ["ช่วยด้วย", "ช่วยด้วยค่ะ", "help", "help me", "SOS", "911", "助けて", "救命", "살려주세요", "ayuda", "cứu tôi",
        "au secours", "Hilfe", "socorro", "помогите"]
DANGER = ["อยากตาย", "เลือดออกเยอะ", "หายใจไม่ออก", "ไฟไหม้", "fire", "โดนตี"]


@pytest.mark.parametrize("q", HELP)
def test_one_word_help_gets_numbers(q):
    # คำว่า "ช่วยด้วย" เดี่ยวๆ อาจเป็นเรื่องอื่นได้ ระบบถามกลับ — แต่ต้องมีเบอร์ฉุกเฉินให้เสมอ
    assert assess(q)["risk_shown"] >= 50
    assert re.search(r"1669|191|911|112|120|119|110|113|115|190", compose(q, footer=False))


@pytest.mark.parametrize("q", DANGER)
def test_one_word_danger_is_urgent(q):
    assert assess(q)["risk_shown"] >= 60


@pytest.mark.parametrize("q", ["สวัสดี", "ขอบคุณ", "hi", "ok", "555", "thanks", "good night", "ฝันดี", "camp fire tonight", "911 call center job"])
def test_everyday_short_stays_calm(q):
    assert assess(q)["risk_shown"] < 50
