"""รอบสุ่ม 210: เด็กตกบ่อ/สระ (ยังไม่ได้บอกว่าจมน้ำ) · ผู้สูงอายุล้มแล้วขยับไม่ได้ (สงสัยสะโพกหัก)"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "เด็กตกบ่อน้ำหลังบ้าน", "ลูกตกสระ", "หลานพลัดตกลงไปในคลอง", "my grandma fell and can't move her hip",
    "ยายล้มในห้องน้ำ ลุกไม่ได้",
])
def test_fall_into_water_or_elderly_fall_is_urgent(q):
    assert assess(q)["risk_shown"] >= 75


@pytest.mark.parametrize("q", ["ลูกบอลตกสระ", "ลูกทำมือถือตกสระ", "grandma fell asleep on the couch", "เด็กตกบ่อน้ำแต่ดึงขึ้นมาแล้ว ปกติดี ร้องเสียงดัง"])
def test_everyday_stays_calm(q):
    assert assess(q)["risk_shown"] < 60
