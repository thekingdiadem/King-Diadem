"""รอบสุ่ม 203 (เดิมเลข 133 ซึ่งซ้ำกับอีกแชท): คนลงไปในบ่อเกรอะแล้วไม่ขึ้นมา (ห้ามลงไปช่วยเอง) · ไฟดับขณะใช้เครื่องช่วยหายใจ · แมงกะพรุนแล้วหายใจขัด"""
import pytest
from core.kernel_voice import assess, compose

REAL = [("เพื่อนลงไปในบ่อเกรอะแล้วไม่ขึ้นมา", "confined_space"), ("my friend went into the septic tank and isn't coming out", "confined_space"),
        ("ไฟดับทั้งตึก แม่ใช้เครื่องช่วยหายใจอยู่", "home_ventilator"), ("power is out and my mom is on a home ventilator", "home_ventilator")]
CALM = ["ทำความสะอาดท่อน้ำทิ้งในครัว", "ไฟดับทั้งซอย ร้อนมาก", "my friend cleans septic tanks for a living", "แม่ใช้เครื่องช่วยหายใจตอนนอน หมอให้ใช้"]


@pytest.mark.parametrize("t,topic", REAL)
def test_missed_before_now_has_its_own_reply(t, topic):
    a = assess(t)
    assert a["risk_shown"] >= 85 and a["topics"][0] == topic


def test_confined_space_says_do_not_go_in_first():
    # เดิมได้ "นั่งในท่าที่หายใจสบาย" — คนที่ลงไปช่วยมักหมดสติเป็นคนที่สอง
    assert compose("เพื่อนลงไปในบ่อเกรอะแล้วไม่ขึ้นมา", footer=False).startswith("อย่าลงไปช่วยเองเด็ดขาด")
    assert "Do not go in" in compose("my friend went into the septic tank and isn't coming out", footer=False)


def test_jellyfish_with_breathing_trouble_is_urgent():
    assert assess("โดนแมงกะพรุนต่อย หายใจขัด")["risk_shown"] >= 80


@pytest.mark.parametrize("t", CALM)
def test_everyday_calm(t):
    assert assess(t)["risk_shown"] < 60
