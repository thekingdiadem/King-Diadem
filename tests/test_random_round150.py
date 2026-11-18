"""รอบสุ่ม 150: เด็ก/สัตว์ถูกทิ้งในรถร้อน (อังกฤษ) ต้องได้เท่าฉบับไทย"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "there's a baby alone in a hot car in the parking lot", "a dog is locked in a parked car and it's 38 degrees",
    "I see a toddler left in the car, windows up, he's crying", "เด็กเล็กอยู่ในรถคนเดียว แดดร้อนมาก กระจกปิด",
])
def test_left_in_hot_car_is_emergency(q):
    a = assess(q)
    assert a["risk_shown"] >= 80 and "violence" not in a["topics"]


@pytest.mark.parametrize("q", ["the baby is sleeping in the car seat while I drive", "my dog loves riding in the car with me"])
def test_normal_car_rides_stay_calm(q):
    assert assess(q)["risk_shown"] < 60
