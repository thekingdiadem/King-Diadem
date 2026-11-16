"""รอบสุ่ม 114: ล้มแล้วสับสนหรือซึม ต้องเป็นเหตุฉุกเฉิน ไม่ใช่แค่ปฐมพยาบาล"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "แม่ล้มในห้องน้ำ ลุกไม่ขึ้น พูดไม่รู้เรื่อง", "ยายล้มหัวฟาดพื้น พูดไม่รู้เรื่อง",
    "แม่ล้มแล้วซึม เรียกไม่ค่อยตอบ", "พ่อล้มเมื่อเช้า ตอนนี้อาเจียน", "ลูกหกล้มหัวฟาดพื้น แล้วซึม",
])
def test_fall_with_confusion_is_emergency(q):
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", [
    "แม่ล้มในห้องน้ำ ไม่เป็นไร ลุกเองได้", "บริษัทล้มละลาย เครียดจนซึมไปหลายวัน", "หกล้มเข่าถลอก", "ล้มเหลวในการสอบ ซึมเลย",
])
def test_everyday_falls_stay_calm(q):
    assert assess(q)["risk_shown"] < 80
