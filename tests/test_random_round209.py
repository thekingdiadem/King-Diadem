"""รอบสุ่ม 209: เรื่องเล็กที่จบแล้วไม่ควรขึ้นฉุกเฉิน แต่ถ้ามีอาการเตือนยังต้องด่วน"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "คนงานโดนไฟดูดล้มอยู่ ยังจับตัวเขาอยู่", "พ่อเจ็บหน้าอกร้าวไปแขนซ้าย เหงื่อแตก",
    "เจ็บหน้าอกหลังยกเวท ร้าวไปแขนซ้าย เหงื่อแตก", "ไฟดูดเบาๆ ตอนนี้หายใจไม่ค่อยออก",
    "สามีบีบคอฉันเมื่อคืน วันนี้เขาจะกลับมา", "my son swallowed a magnet",
])
def test_danger_stays_urgent(q):
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", ["ไฟดูดเบาๆ ตอนเสียบปลั๊ก ตอนนี้ปกติ", "เจ็บหน้าอกหลังยกเวท กล้ามเนื้อตึง", "บีบนวดคอให้สามีเมื่อคืน"])
def test_small_finished_things_stay_calm(q):
    assert assess(q)["risk_shown"] < 60
