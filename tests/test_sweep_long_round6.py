"""ไล่หาบั๊กรอบยาว 6: คนไม่หายใจ (CPR) · คนจมน้ำ · พิษคาร์บอนมอนอกไซด์ · ถูกแฟนบังคับมีเพศสัมพันธ์ · CPR/จมน้ำภาษาอังกฤษ"""
import pytest

from core.kernel_voice import assess, compose


@pytest.mark.parametrize("text,needle,min_risk", [
    ("มีคนหมดสติไม่หายใจ", "กดหน้าอก (CPR)", 85),
    ("พ่อหัวใจหยุดเต้น", "กดหน้าอก (CPR)", 85),
    ("เห็นคนจมน้ำ", "โยนของลอยน้ำ", 85),
    ("ลูกตกน้ำ", "ห้ามอุ้มพาดบ่า", 85),
    ("คาร์บอนมอนอกไซด์ ปวดหัวในห้องที่มีเครื่องปั่นไฟ", "คาร์บอนมอนอกไซด์ — พาทุกคนออกไป", 85),
    ("เปิดเครื่องปั่นไฟในบ้าน ทุกคนปวดหัว คลื่นไส้", "อากาศโล่ง", 85),
    ("โดนแฟนบังคับให้มีเพศสัมพันธ์", "ไม่ใช่ความผิดของคุณ", 75),
    ("someone is not breathing", "chest compressions", 85),
    ("my dad collapsed and is unconscious", "AED", 85),
    ("my son is drowning", "Throw something that floats", 85),
])
def test_life_threatening_cases_get_the_right_first_step(text, needle, min_risk):
    assert needle in compose(text)
    assert assess(text)["text_risk"] >= min_risk


@pytest.mark.parametrize("text", ["มีคนหมดสติไม่หายใจ", "เห็นคนจมน้ำ"])
def test_unresponsive_person_is_not_told_to_sit_comfortably(text):
    assert "นั่งหรือนอนในท่าที่หายใจสบาย" not in compose(text)


def test_conscious_breathlessness_keeps_the_sitting_advice():
    out = compose("หายใจไม่ออก แน่นหน้าอก")
    assert "นั่งหรือนอนในท่าที่หายใจสบาย" in out and "CPR" not in out


def test_breathing_normally_is_not_a_cardiac_arrest():
    assert "chest compressions" not in compose("I have chest pain but I'm breathing fine")
