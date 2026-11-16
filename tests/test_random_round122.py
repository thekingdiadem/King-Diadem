"""รอบสุ่ม 122: น้ำตาลในเลือดสูงมาก (400 ขึ้นไป)"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "แม่ไม่ยอมกินยาเบาหวาน น้ำตาล 500", "น้ำตาลในเลือด 500", "น้ำตาลสูง 450 กระหายน้ำมาก", "blood sugar is 550",
])
def test_very_high_sugar_is_urgent(q):
    assert assess(q)["risk_shown"] >= 75


@pytest.mark.parametrize("q", ["น้ำตาลขึ้น 130 หลังกินข้าว", "ขนมนี้น้ำตาล 500 กรัม", "this cake has 450 calories of sugar"])
def test_normal_numbers_stay_calm(q):
    assert assess(q)["risk_shown"] < 60
