"""DriftZero รอบสุ่ม 18 (จากหม้อหุงข้าวของเจ้าของโปรเจกต์ที่สวิตช์ละลาย): อันตรายจากไฟฟ้าและไฟไหม้"""
import pytest
from ENGINE.driftzero import audit


def _stops(a):
    return [g["id"] for g in a["gates"] if g["status"] == "stop"]


@pytest.mark.parametrize("t", ["ร้านจะใช้หม้อหุงข้าวเก่าที่สายไฟละลายต่อไปก่อน ยังไม่มีเงินซื้อใหม่",
                               "โรงงานจะใช้ปลั๊กพ่วงต่อกันหลายตัวเสียบเครื่องจักร", "จะให้พนักงานซ่อมไฟเองทั้งที่ยังเสียบปลั๊กอยู่",
                               "ร้านอาหารจะใช้ถังแก๊สที่รั่วไปก่อนจนกว่าจะหมด", "we'll keep using the frayed extension cord for the kitchen fryer",
                               "the landlord will not fix the broken fire exit this year"])
def test_electrical_and_fire_hazards_stop(t):
    assert "P1" in _stops(audit(t))


@pytest.mark.parametrize("t", ["จะเปลี่ยนหม้อหุงข้าวใหม่เพราะสายไฟละลาย", "จะเรียกช่างไฟฟ้าที่มีใบอนุญาตมาเดินสายใหม่",
                               "จะถอดปลั๊กก่อนซ่อมไฟทุกครั้ง"])
def test_fixing_it_safely_passes(t):
    assert not _stops(audit(t))
