"""ไล่หาบั๊กรอบยาว 5: สัญญาณบอกลา · ซึมเศร้าหลังคลอด · ผู้สูงอายุเห็นภาพหลอน · เด็กขาดน้ำ · เข็มทิ่ม
· ถูกขู่จะตามมาที่บ้าน · เด็กข้างบ้านโดนตี · คนแปลกหน้าเข้าหาเด็กทางออนไลน์ · เรื่องด่วนภาษาอังกฤษ"""
import pytest

from core.kernel_voice import assess, compose


@pytest.mark.parametrize("text,needle,min_risk", [
    ("เพื่อนส่งข้อความบอกลาแปลกๆ แล้วปิดเครื่อง", "1323", 75),
    ("my friend texted goodbye and turned off her phone", "emergency", 75),
    ("คลอดลูกมา 2 เดือน ร้องไห้ทุกวัน ไม่อยากอุ้มลูก", "ซึมเศร้าหลังคลอด", 70),
    ("แม่บอกว่าเห็นคนที่ไม่มีอยู่จริง", "อาการทางกาย", 60),
    ("ลูกท้องเสียหลายรอบ ปากแห้ง ไม่มีปัสสาวะ", "ORS", 75),
    ("โดนเข็มทิ่มตอนทำงานที่โรงพยาบาล", "PEP", 60),
    ("มีคนขู่จะตามมาที่บ้าน", "เก็บหลักฐาน", 60),
    ("ลูกเล่นมือถือแล้วเจอคนแปลกหน้าชวนไปเจอ", "ห้ามให้ไปเจอ", 75),
    ("I was assaulted last night", "72 hours", 75),
    ("my baby has a fever and is 2 months old", "under 3 months", 75),
    ("I'm pregnant and bleeding", "Bleeding during pregnancy", 75),
    ("I think my drink was spiked", "don't go home alone", 75),
])
def test_urgent_cases_get_specific_help(text, needle, min_risk):
    assert needle in compose(text)
    assert assess(text)["text_risk"] >= min_risk


def test_neighbour_child_being_hit_is_a_witness_case():
    out = compose("เด็กข้างบ้านโดนตีทุกวัน ได้ยินเสียงร้อง")
    assert "ดีแล้วที่ไม่เพิกเฉย" in out and "ความปลอดภัยของคุณมาก่อนทุกเรื่อง" not in out


def test_english_urgent_cases_are_not_mixed_up():
    assert "assaulted" not in compose("my baby has a fever and is 2 months old")
