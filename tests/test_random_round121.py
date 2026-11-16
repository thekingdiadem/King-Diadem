"""รอบสุ่ม 121: ผู้สูงอายุไม่กินไม่ดื่มหลายวัน = ขาดน้ำรุนแรง"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "ยายไม่กินข้าวไม่กินน้ำมาสองวัน", "grandma hasn't eaten or drunk anything in two days", "ลูกไม่กินนมไม่ดื่มน้ำมา 2 วัน",
])
def test_no_food_no_water_for_days_is_urgent(q):
    assert assess(q)["risk_shown"] >= 75


@pytest.mark.parametrize("q", ["ยายไม่กินข้าวเพราะไม่อร่อย", "แม่ไม่กินข้าวเย็นเพราะลดน้ำหนัก"])
def test_picky_eating_stays_calm(q):
    assert assess(q)["risk_shown"] < 60
