"""รอบสุ่ม 19: ผู้สูงอายุและคนเปราะบาง"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ["น้องออทิสติกหายไปจากบ้าน", "dad is diabetic, sweaty and confused, barely responding",
                               "the caregiver is hitting my grandmother, I saw it on camera", "my autistic brother wandered off and we can't find him",
                               "ยายล้มในห้องน้ำ ลุกไม่ได้ อยู่คนเดียว", "คนดูแลตียายตอนเราไม่อยู่ เห็นในกล้อง", "my grandma fell and can't get up, she lives alone"])
def test_vulnerable_people_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ["ยายเป็นอัลไซเมอร์ จำชื่อหลานไม่ได้", "dad is diabetic, what snacks are ok", "the nurse is helping my grandma walk",
                               "ยายล้มเล็กน้อย ลุกได้เอง ไม่เจ็บ", "grandma fell asleep watching tv", "my brother wandered around the mall all day"])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
