"""ประโยคปฏิเสธ/ชื่อหนัง/มุก ที่เคยได้วิกฤต 95 หรือฉุกเฉิน 85 (ตรวจ core/ รอบ 397 ไฟล์) — และข้อความยาวมากต้องไม่ช้า"""
import time

import pytest

from core.kernel_voice import assess

CALM = ["ไม่อยากตาย", "ไม่อยากตายค่ะ แค่เหนื่อย", "I am not going to kill myself", "I would never kill myself",
        "ฆ่าตัวตายไม่ใช่ทางออก", "Suicide Squad is a great movie", "หนังเรื่องฆ่าตัวตายหมู่ดีมาก",
        "overdose of coffee lol", "กินยาเกินขนาดไหม paracetamol 2 เม็ด"]
STILL_URGENT = ["ไม่อยากอยู่แล้ว", "ไม่อยากตาย แต่ไม่อยากอยู่", "ไม่อยากตายแล้ว อยากหายไป", "อยากตาย",
                "I want to kill myself", "I overdosed on pills", "ลูกกินยาเกินขนาด", "กินยาเกินขนาด 20 เม็ด", "I took an overdose"]


@pytest.mark.parametrize("t", CALM)
def test_negation_is_not_a_crisis(t):
    a = assess(t)
    assert a["text_risk"] < 60 and not a["crisis"], (t, a["text_risk"])


@pytest.mark.parametrize("t", STILL_URGENT)
def test_real_danger_still_urgent(t):
    assert assess(t)["text_risk"] >= 85, t


def test_very_long_message_is_fast_and_keeps_the_ending():
    t = "aaa " * 20000 + " I want to kill myself"
    s = time.time()
    a = assess(t)
    assert time.time() - s < 1.5 and a["crisis"]
