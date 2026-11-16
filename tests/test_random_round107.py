"""รอบสุ่ม 107: จำนวนเม็ดยาที่สะกดเป็นคำ ต้องได้เท่ากับตัวเลข"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "กินยาพาราไปยี่สิบเม็ด", "กินยานอนหลับไปสิบห้าเม็ด",
    "took twenty paracetamol", "swallowed thirty pills", "took twenty-five sleeping pills",
    "swallowed 30 pills",
])
def test_spelled_out_overdose_is_urgent(q):
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", [
    "took two paracetamol for headache", "กินยาพาราสองเม็ด", "twenty people came to the party", "ห้าโมงเย็นกินยา",
])
def test_normal_doses_stay_calm(q):
    assert assess(q)["risk_shown"] < 60
