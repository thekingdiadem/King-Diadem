"""รอบสุ่ม 123: ไฟกำลังลามเข้าบ้าน ต้องได้ระดับฉุกเฉิน ไม่ใช่เท่าข่าวควัน"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "ไฟไหม้ป่าใกล้บ้าน ลมพัดมาทางนี้", "ไฟป่าลามมาถึงหลังบ้านแล้ว", "wildfire is coming toward our house",
    "the fire is spreading to our street",
])
def test_fire_approaching_home_is_emergency(q):
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", ["ไฟไหม้ป่าที่เชียงใหม่ ควันเต็มเมือง", "ไฟป่าลามมาถึงบ้านในเกม", "ไฟไหม้ป่าในเกม"])
def test_news_and_games_stay_below_emergency(q):
    assert assess(q)["risk_shown"] < 80
