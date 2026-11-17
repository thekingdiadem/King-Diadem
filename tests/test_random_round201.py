"""รอบสุ่ม 201 (เดิมเลข 131 ซึ่งซ้ำกับอีกแชท): หัวติดลูกกรง · เดินเซ+พูดสับสน (สโตรก) · ติดลิฟต์หายใจไม่ออก · น้ำร้อนลวกจนพอง (อังกฤษ)"""
import pytest
from core.kernel_voice import assess, compose

REAL = ["หลานเอาหัวติดลูกกรงระเบียง ดึงไม่ออก", "ยายเดินเซ พูดจาสับสน ตั้งแต่เช้า", "ติดอยู่ในลิฟต์ หายใจไม่ค่อยออก",
        "grandma is confused and slurring since this morning", "boiling water spilled on my baby's arm, big blisters"]
CALM = ["หลานเอาหัวลอดลูกกรงเล่น ดึงออกได้แล้ว", "เมาเดินเซ พูดจาสับสน ฮ่าๆ", "grandma is confused by the new TV remote",
        "แม่ลืมกินยาความดันเมื่อวาน", "ลิฟต์คอนโดปิดซ่อมวันนี้"]


@pytest.mark.parametrize("t", REAL)
def test_missed_before_now_caught(t):
    # ทุกข้อเคยได้ 0 หรือ 50
    assert assess(t)["risk_shown"] >= 75


@pytest.mark.parametrize("t", CALM)
def test_everyday_calm(t):
    assert assess(t)["risk_shown"] < 60


def test_breathing_trouble_in_a_lift_is_not_answered_with_the_lift_is_safe():
    assert "1669" in compose("ติดอยู่ในลิฟต์ หายใจไม่ค่อยออก", footer=False)
    assert "ลิฟต์ไม่ตก" in compose("ติดลิฟต์อยู่ ทำยังไงดี", footer=False)
