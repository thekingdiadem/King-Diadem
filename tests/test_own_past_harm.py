"""ผู้ใช้สารภาพว่า "ตัวเอง" เคยทำร้ายคนอื่น แล้วรู้สึกผิด/เลิกแล้ว — ไม่ใช่คนที่กำลังถูกทำร้าย

ข้อความจริงจากเจ้าของโปรเจกต์ เคยได้หัวข้อความรุนแรง + Risk 100 และคำตอบ "ถ้ากำลังอยู่ในอันตราย โทร 191"
"""
import pytest

from core.kernel_voice import assess
from core.engine_bridge import _relationship

REAL = ("ทุกคนนี่หมายถึงทุกคนที่พี่เกิดมาเคยทำร้ายเขาและเคยพูดจาไม่ดีใส่เขานะ "
        "พอมีคนที่หน้ากลัวเขามาพูดไม่ดีสมัยก่อนพี่เก็บเอาไว้ในใจแล้วมาพูดให้คนที่บ้านฟังงี้ แต่ว่าตอนนี้ไม่มีแล้วนะ")


@pytest.mark.parametrize("text", [
    REAL,
    "ผมเคยตีน้อง รู้สึกผิดมาก",
    "ฉันเคยทำร้ายแฟน ตอนนี้เลิกแล้ว อยากขอโทษเขา",
])
def test_remorse_for_own_past_harm_is_not_violence_against_user(text):
    a = assess(text)
    assert "violence" not in a["topics"]
    assert a["risk_shown"] < 60
    assert _relationship(text) is None or "violence_risk" not in _relationship(text)["data"]["flags"]


@pytest.mark.parametrize("text", [
    "ฉันโดนแฟนทำร้าย",
    "พ่อเคยทำร้ายแม่ ตอนนี้ไม่มีแล้ว",          # คนอื่นเป็นคนทำ — ยังเป็นความรุนแรงในบ้าน
    "แฟนเคยทำร้ายฉัน ขอโทษที่เล่านะ",            # "ขอโทษ" แต่ผู้ใช้เป็นคนถูกทำ
    "ฉันเคยโดนพ่อตี ตอนนี้ไม่มีที่ไปแล้ว",        # "ไม่มีที่ไปแล้ว" ไม่ใช่ "เลิกแล้ว"
])
def test_user_as_victim_still_flagged(text):
    a = assess(text)
    assert "violence" in a["topics"] and a["risk_shown"] >= 85


def test_past_self_harm_stays_a_crisis_signal():
    assert assess("เมื่อก่อนฉันเคยทำร้ายตัวเอง ตอนนี้ไม่ทำแล้ว")["crisis"]
