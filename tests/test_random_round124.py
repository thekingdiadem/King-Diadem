"""รอบสุ่ม 124: หมากัดแผลลึก / หมาจรกัด (เสี่ยงพิษสุนัขบ้า)"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "ลูกโดนหมาข้างบ้านกัดแผลลึก", "โดนหมาจรกัดที่ขา", "my son got bitten by a stray dog, deep wound", "แมวจรกัดมือเป็นรู",
])
def test_serious_bite_is_emergency(q):
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", ["ลูกโดนหมาเลียหน้า", "หมากัดรองเท้าขาด", "ลูกแมวกัดเล่นเบาๆ"])
def test_play_stays_calm(q):
    assert assess(q)["risk_shown"] < 60
