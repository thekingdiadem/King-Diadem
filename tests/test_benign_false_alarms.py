"""ข้อความธรรมดาที่เคยได้คำตอบฉุกเฉิน — เกม ฝัน ซ้อม นิยาย/รายงาน — แต่เรื่องจริงต้องยังจับได้"""
import pytest

from core.kernel_voice import assess

BENIGN = [
    "เล่นเกมโดนยิงตายตลอด",
    "ฝันว่าตกตึก แปลว่าอะไร",
    "ฝันว่าโดนยิง แปลว่าอะไร",
    "Heart attack-level excitement for the finals",
    "ทดลองระบบเตือนภัยสึนามิวันนี้",
    "earthquake drill at school tomorrow",
    "the movie had a shooting scene",
]
REAL = [
    "พ่อโดนยิงที่ขา", "ยายตกตึก", "dad is having a heart attack",
    "ตัวละครในนิยายอยากตาย เหมือนฉันตอนนี้",
    "I am writing a novel but honestly I want to kill myself",
    "this is not a drill, earthquake now", "มีคนยิงกันหน้าบ้าน",
]


@pytest.mark.parametrize("t", BENIGN)
def test_benign_is_calm(t):
    a = assess(t)
    assert a["text_risk"] < 35 and not a["crisis"] and "soft_check" not in a["topics"], (t, a)


@pytest.mark.parametrize("t", REAL)
def test_real_still_urgent(t):
    a = assess(t)
    assert a["crisis"] or a["text_risk"] >= 50, (t, a)


@pytest.mark.parametrize("t", ["เขียนนิยาย ตัวละครฆ่าตัวตาย ช่วยเกลาให้หน่อย", "research paper on self-harm statistics"])
def test_work_frame_is_gentle_not_crisis(t):
    """งานเขียน/งานวิจัย: ไม่ใช่วิกฤตเต็มรูป แต่ยังถามไถ่เบาๆ (soft_check) เผื่อเป็นเรื่องของตัวเอง"""
    a = assess(t)
    assert not a["crisis"] and "soft_check" in a["topics"] and 40 <= a["text_risk"] < 60


def test_work_frame_opener_fits_the_request():
    from core.kernel_voice import compose
    assert compose("research paper on self-harm statistics").startswith("Happy to help with the work")
    assert compose("เขียนนิยาย ตัวละครฆ่าตัวตาย ช่วยเกลาให้หน่อย").startswith("เรื่องนี้หนักแม้จะเป็นงานเขียน")
