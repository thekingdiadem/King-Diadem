"""รอบสุ่ม 135–143 เคยถูกใส่ผิดกลุ่ม (ตัวจับความรุนแรง) — ระดับความเสี่ยงถูก แต่คำตอบเป็นเรื่องถูกทำร้าย
เทสต์ของรอบเหล่านั้นตรวจแค่ตัวเลข จึงไม่เห็น · ไฟล์นี้ตรวจหัวข้อด้วย"""
import pytest
from core.kernel_voice import assess, compose

BODY = [
    "my dad's foot wound turned black and smells", "คนแก่ในบ้านไม่ตื่น ตัวเย็น", "baby fell off the bed and vomited twice",
    "ตาบวมปิด ปากบวม หลังกินกุ้ง", "แม่ทานยาละลายลิ่มเลือด ล้มหัวกระแทก", "nosebleed won't stop for 30 minutes",
    "dad has chest pressure but says it's just gas", "the carbon monoxide detector keeps beeping", "fell through the ice on the lake",
]


@pytest.mark.parametrize("q", BODY)
def test_body_emergencies_are_not_answered_as_violence(q):
    a = assess(q)
    assert a["risk_shown"] >= 80 and "violence" not in a["topics"]
    assert "อีกฝ่ายเข้าไม่ถึง" not in compose(q, footer=False)


def test_generator_indoors_gets_fresh_air_advice():
    assert "อากาศโล่ง" in compose("เปิดเครื่องปั่นไฟในบ้าน ทุกคนปวดหัว คลื่นไส้")


def test_locked_in_is_still_violence():
    assert "violence" in assess("he locked the door and won't let me leave")["topics"]
