"""รอบสุ่ม 138: อาการแพ้รุนแรงที่เล่าอาการก่อน แล้วค่อยบอกว่ากินอะไร"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ["ตาบวมปิด ปากบวม หลังกินกุ้ง", "ปากบวม หายใจลำบาก ตั้งแต่กินถั่ว", "throat swelling after eating shrimp"])
def test_reverse_order_allergy_is_emergency(q):
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", ["ตาบวมเพราะร้องไห้ทั้งคืน", "ปากบวมนิดหน่อยหลังทำฟัน"])
def test_everyday_swelling_stays_calm(q):
    assert assess(q)["risk_shown"] < 80
