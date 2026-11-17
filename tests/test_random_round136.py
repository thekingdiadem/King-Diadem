"""รอบสุ่ม 136: คนในบ้านไม่ตื่นและตัวเย็น/ไม่ขยับ ต้องเป็นเหตุฉุกเฉิน"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "คนแก่ในบ้านไม่ตื่น ตัวเย็น", "พ่อไม่ตื่น ตัวเย็น", "ยายตัวเย็น ไม่ขยับ", "ลูกปลุกไม่ตื่น เรียกไม่ตอบ ปากเขียว",
    "grandpa won't wake up and feels cold",
])
def test_unresponsive_and_cold_is_emergency(q):
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", ["ปลุกลูกไม่ตื่นไปโรงเรียน", "ยายไม่ยอมตื่นเช้า ชอบนอนตื่นสาย", "แม่ตัวเย็นเพราะเปิดแอร์แรง"])
def test_sleepy_mornings_stay_calm(q):
    assert assess(q)["risk_shown"] < 60
