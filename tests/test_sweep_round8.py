"""รอบหาบั๊ก 8: คำตอบที่ระบบประกอบเอง (ไม่ใช้ AI) — พยาน/ญาติไม่ใช่เหยื่อ · ทางเลือกสัตว์/เผาไร่ขึ้นเป็นขั้นหลัก"""
import pytest
from core.kernel_voice import assess, compose


@pytest.mark.parametrize("text", ["ได้ยินเสียงผู้หญิงกรีดร้องข้างห้อง", "เห็นเด็กถูกทำร้ายในบ้านข้างๆ",
                                  "I can hear a woman screaming next door"])
def test_witness_is_not_addressed_as_victim(text):
    """เดิมได้ "ความปลอดภัยของคุณมาก่อน · คืนนี้คุณนอนที่ไหนได้โดยที่อีกฝ่ายเข้าไม่ถึง?" """
    a = assess(text)
    assert a["topics"][0] == "witness" and a["text_risk"] >= 70
    r = compose(text)
    assert "191" in r and "นอนที่ไหนได้โดยที่อีกฝ่าย" not in r and "Let's lay this out" not in r


@pytest.mark.parametrize("text", ["ลูกเอาเงินบำนาญแม่ไปหมด ไม่ให้กินข้าว", "my brother took mom's pension"])
def test_elder_abuse_gets_its_own_steps(text):
    a = assess(text)
    assert a["topics"][0] == "elder_abuse"
    r = compose(text)
    assert "1300" in r and "นอนที่ไหนได้โดยที่อีกฝ่าย" not in r


@pytest.mark.parametrize("text, must", [("จะวางยาเบื่อหนู", "ไม่ต้องฆ่า"), ("จะเผาตอซังดีไหม", "ไถกลบ"),
                                        ("กระต่ายที่บ้านไม่ยอมกิน", "สัตวแพทย์"),
                                        ("เพื่อนบ้านเผาขยะทุกเย็น ควันเข้าบ้าน", "N95")])
def test_animal_and_earth_steps_lead_the_answer(text, must):
    """เดิมทางเลือกไปอยู่ท้ายคำตอบ ใต้ขั้นทั่วไป "เขียนสิ่งที่เกิดขึ้นเป็นประโยคเดียว" """
    r = compose(text)
    steps = r.split("จากสิ่งที่คุณเล่า")[0]
    assert must in steps and "เขียนสิ่งที่เกิดขึ้นเป็นประโยคเดียว" not in r


def test_alternatives_are_not_printed_twice():
    r = compose("จะเผาตอซังดีไหม")
    assert r.count("ไถกลบตอซัง") == 1


@pytest.mark.parametrize("text", ["แม่ไม่ให้กินขนม", "ไม่ให้กินข้าวก่อนเจาะเลือด", "ได้ยินเสียงฟ้าร้อง"])
def test_round8_ordinary_phrases(text):
    assert not {"witness", "elder_abuse", "violence"} & set(assess(text)["topics"])
