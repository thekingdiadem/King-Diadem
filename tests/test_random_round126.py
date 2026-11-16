"""รอบสุ่ม 126: ติดอยู่ในห้องเย็น/ตู้แช่/ตู้คอนเทนเนอร์"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "ถูกล็อกอยู่ในห้องเย็นที่ทำงาน", "ติดอยู่ในตู้แช่ ประตูเปิดไม่ได้", "i'm locked in the walk-in freezer at work",
])
def test_trapped_in_cold_room_is_emergency(q):
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", ["ตู้เย็นเสีย ต้องเรียกช่าง", "เก็บของในห้องเย็นทั้งวัน หนาวมาก", "the freezer door is stuck, ice cream melting"])
def test_appliance_talk_stays_calm(q):
    assert assess(q)["risk_shown"] < 60
