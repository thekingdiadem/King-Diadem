"""รอบสุ่ม 115: ถูกเอาอาวุธเล็งใส่ (อังกฤษ) ต้องได้เท่าฉบับไทย"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "my husband pointed a gun at me", "he pointed a gun at me", "he is pointing a knife at me",
    "my dad was waving a gun at my mom", "สามีเอาปืนจ่อหัว",
])
def test_weapon_aimed_is_emergency(q):
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", [
    "my son pointed a water gun at me and laughed", "the villain pointed a gun at me in the game",
    "he pointed at me across the room",
])
def test_play_and_pointing_stay_calm(q):
    assert assess(q)["risk_shown"] < 80
