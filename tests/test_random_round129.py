"""รอบสุ่ม 129: บาดเจ็บที่ผ่านมานานแล้วและหายดี ไม่ใช่เหตุฉุกเฉิน"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "ตกบันไดเมื่อปีที่แล้ว ตอนนี้หายดีแล้ว", "ข้อเท้าแพลงเมื่อเดือนก่อน ตอนนี้หายดีแล้ว", "broke my arm last year, fully healed now",
])
def test_healed_past_injury_stays_calm(q):
    assert assess(q)["risk_shown"] < 60


@pytest.mark.parametrize("q", ["ตกบันไดเมื่อกี้ ขาบวมผิดรูป", "fell down the stairs just now and my arm looks bent"])
def test_fresh_injury_still_gets_first_aid(q):
    assert assess(q)["risk_shown"] >= 75


@pytest.mark.xfail(reason="ช่องโหว่ที่รู้แล้ว: 'ขาหัก' ให้ความเสี่ยงระดับข้อความ (text_risk) ก่อนชั้นหัวข้อจะรู้ว่าเป็นเรื่องเก่า", strict=True)
def test_known_gap_broken_leg_as_child():
    assert assess("ขาหักตอนเด็ก ตอนนี้เดินได้ปกติ")["risk_shown"] < 60
