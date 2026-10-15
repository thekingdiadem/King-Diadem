"""ไล่หาบั๊ก 10,000 ข้อความ: ผู้ประสบเหตุ × อาการด่วน × สำนวน — ทุกอันต้องได้ Risk ≥ 60 และไม่ได้คำตอบทั่วไป
(รอบแรกหลุด 3,917 ข้อความ: ถูกแทง/ยิง · ยาฆ่าหญ้า · กลืนเหรียญ (ผู้ใหญ่) · ชัก (ผู้ใหญ่) · แพ้อาหาร · นิ้วขาด · สารเข้าตา ฯลฯ)"""
import itertools

import pytest

from core.kernel_voice import assess, compose

WHO = ["", "ลูก", "แม่", "ยาย", "เพื่อน", "สามี", "คนข้างบ้าน", "ฉัน"]
EVENTS = ["หมดสติ", "ไม่หายใจ", "จมน้ำ", "ตกน้ำ", "ชัก", "เลือดออกไม่หยุด", "เลือดกำเดาไหลไม่หยุด", "ไอเป็นเลือด", "ถ่ายดำ",
          "กินยาฆ่าหญ้า", "กลืนถ่านกระดุม", "กลืนเหรียญ", "กินถั่วแล้วปากบวม", "กินกุ้งแล้วหายใจลำบาก", "นิ้วขาด", "กระดูกหัก",
          "กระดูกโผล่", "หัวฟาดพื้นแล้วอาเจียน", "ตาโดนสารเคมี", "ปูนเข้าตา", "เป็นลมแดด ตัวร้อนจัด", "สับสนกะทันหัน",
          "ตัวเหลืองมาก ไม่กินนม", "ท้องเสีย ปากแห้ง ไม่ฉี่", "น้ำตาลต่ำ หน้ามืด", "เมาจนปลุกไม่ตื่น", "เสพยาแล้วตัวร้อนชัก",
          "กินยาอีแล้วตัวร้อน", "ถูกแทง", "ถูกยิง", "ไข้สูง คอแข็ง"]
FRAME = ["{w}{e}", "ช่วยด้วย {w}{e}", "ตอนนี้{w}{e}", "{w}{e} ค่ะ", "{w} {e}", "{w}{e}อยู่ ต้องทำยังไง"]
GENERIC = ("เขียนสิ่งที่เกิดขึ้นเป็นประโยคเดียว", "ถ้าอาการแย่ลงเร็ว มีไข้สูงไม่ลด", "ให้เวลาตัวเอง 24–72 ชั่วโมง")


def test_urgent_grid_never_slips():
    slipped = []
    for w, e, f in itertools.product(WHO, EVENTS, FRAME):
        t = f.format(w=w, e=e).strip()
        if assess(t)["text_risk"] < 60 or any(g in compose(t) for g in GENERIC):
            slipped.append(t)
    assert not slipped, slipped[:10]


@pytest.mark.parametrize("text,needle", [
    ("พ่อถูกแทง", "ห้ามดึงมีด"),
    ("สามีนิ้วขาด", "วางบนน้ำแข็ง"),
    ("ลูกกระดูกโผล่", "ห้ามดันกลับ"),
    ("ยายตาโดนสารเคมี", "15–20 นาที"),
    ("เลือดกำเดาไหลไม่หยุด", "ห้ามเงยหน้า"),
    ("ถูกมีดบาดลึก เลือดพุ่ง", "กดแผลแน่นๆ"),
    ("พ่อกินถั่วแล้วปากบวม", "อะดรีนาลีน"),
    ("ยายสับสน จำใครไม่ได้กะทันหัน", "น้ำตาลต่ำ"),
    ("ทารกตัวเหลืองมาก ไม่ยอมกินนม", "อันตรายต่อสมอง"),
    ("แฟนจมน้ำ", "โยนของลอยน้ำ"),
    ("my mom is confused and can't speak properly", "stroke"),
    ("my child swallowed a battery", "even if your child seems fine"),
])
def test_specific_first_step(text, needle):
    assert needle in compose(text)


@pytest.mark.parametrize("text", [
    "ทำงานชักช้า", "แม่ชักจะโมโหแล้ว", "ชักไม่แน่ใจว่าจะลาออกดีไหม", "เพื่อนชักชวนไปเที่ยว", "บ้านจมน้ำหมดแล้ว",
    "โดนแทงข้างหลังจากเพื่อน", "โดนยิงแอดทั้งวัน", "แทงบอลเสีย", "ขาดเรียนบ่อย", "น้ำตาลต่ำกว่าเกณฑ์ไหมคะ ค่าน้ำตาล 90",
    "ถ่ายดำหลังกินยาบำรุงเลือด", "ตัวเหลืองเพราะกินส้มเยอะ", "he will kill me if he finds out I failed the exam lol",
])
def test_everyday_words_are_not_emergencies(text):
    assert assess(text)["text_risk"] < 60


@pytest.mark.parametrize("text,min_risk", [
    ("my husband said he'll kill me", 60),
    ("there's a gas smell in my house", 60),
    ("my friend took ecstasy and is overheating", 85),
])
def test_english_dangers_are_recognised(text, min_risk):
    assert assess(text)["text_risk"] >= min_risk
