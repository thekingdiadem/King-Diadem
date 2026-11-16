"""DriftZero รอบสุ่ม 20: ความปลอดภัยของอาหาร — เดิมผ่านทุกด่านทั้ง 7 แบบ"""
import pytest
from ENGINE.driftzero import audit


def _stops(a):
    return [g["id"] for g in a["gates"] if g["status"] == "stop"]


@pytest.mark.parametrize("t", ["ร้านจะเอาอาหารที่เหลือเมื่อวานมาอุ่นขายใหม่โดยไม่บอกลูกค้า", "ร้านจะใช้น้ำมันทอดซ้ำจนดำเพื่อประหยัดต้นทุน",
                               "โรงงานจะเปลี่ยนวันหมดอายุบนฉลากให้ขายได้นานขึ้น", "ร้านจะให้พนักงานที่ท้องเสียทำอาหารต่อเพราะคนไม่พอ",
                               "ร้านจะใส่บอแรกซ์ในลูกชิ้นให้เด้ง", "we'll relabel expired meat with new dates",
                               "the kitchen will keep raw chicken next to salads to save fridge space"])
def test_food_that_makes_people_sick_stops(t):
    assert "P1" in _stops(audit(t))


@pytest.mark.parametrize("t", ["ร้านจะเปลี่ยนน้ำมันทอดทุกวัน", "โรงงานจะทิ้งสินค้าที่หมดอายุทั้งหมด", "ร้านจะให้พนักงานที่ป่วยพักจนหาย"])
def test_safe_kitchen_passes(t):
    assert not _stops(audit(t))
