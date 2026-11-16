"""รอบสุ่ม 128: ไฟช็อตแล้วใจเต้นผิดปกติ (หัวใจเต้นผิดจังหวะเกิดตามมาได้หลายชั่วโมง)"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "got shocked by an outlet yesterday and now my heart is racing", "ไฟฟ้าช็อตเมื่อวาน ตอนนี้ใจสั่น",
    "โดนไฟดูดตอนซ่อมปลั๊ก แล้วเจ็บหน้าอก",
])
def test_shock_then_heart_symptoms_is_emergency(q):
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", ["i was shocked by the plot twist, my heart is racing lol", "โดนไฟช็อตนิดเดียวตอนเสียบปลั๊ก ไม่เป็นไร"])
def test_surprise_and_static_stay_below_emergency(q):
    assert assess(q)["risk_shown"] < 80
