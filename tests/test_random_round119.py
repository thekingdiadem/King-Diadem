"""รอบสุ่ม 119: ตก/ล้ม/ถูกชน แล้วชาหรือขยับขาไม่ได้ = อาจบาดเจ็บไขสันหลัง"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "ตกบันไดหลังหัก ขาขยับไม่ได้", "ตกจากหลังคา ขาชา ขยับไม่ได้", "ตกบันได คอเจ็บ แขนชา",
    "กระโดดน้ำหัวกระแทกพื้นสระ ขยับตัวไม่ได้", "fell off a ladder and can't feel my legs",
])
def test_spinal_signs_are_emergency(q):
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", ["นั่งนานจนขาชา", "ตกบันไดเมื่อปีที่แล้ว ตอนนี้หายดีแล้ว เดินได้ปกติ", "เล่นเกมตกรอบ เซ็งจนขยับตัวไม่ได้เลย 555"])
def test_everyday_numbness_stays_below_emergency(q):
    assert assess(q)["risk_shown"] < 80
