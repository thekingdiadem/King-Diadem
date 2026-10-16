"""ด้านกลับ: ข้อความชีวิตประจำวันที่มีคำน่ากลัว ต้องไม่ถูกตีเป็นเรื่องด่วน (เคยหลุด 594 จาก 6,435 ข้อความ)"""
import itertools

import pytest

from core.kernel_voice import assess

CORE = ["หนังเรื่องนี้ฉากคนจมน้ำน่ากลัวมาก", "เล่นเกมยิงกันทั้งคืน", "อ่านข่าวคนถูกแทงแล้วสะเทือนใจ", "ตกบันไดนิดเดียวไม่เป็นไร",
        "แมวกัดเล่นไม่เข้าเนื้อ", "อยากหลับยาวๆ ในวันหยุด", "กินจนอิ่มหายใจไม่ออก", "ขำจนหายใจไม่ออก", "อยากหลับยาวๆ ไม่ต้องตื่นเช้า",
        "หิวจะตาย", "ฆ่าเวลาด้วยการดูซีรีส์", "แพ้ทางคนพูดเพราะ", "ชักช้าจัง", "สอนลูกว่ายน้ำ", "I'm dying to see the new movie",
        "this homework is killing me", "my boss will kill me if I'm late"]
PRE = ["", "วันนี้", "555 ", "จริงๆ แล้ว"]
POST = ["", " 555", " ค่ะ", " 😂", " ทำไงดี"]


def test_everyday_phrases_are_not_emergencies():
    loud = [t for t in ((p + c + q).strip() for p, c, q in itertools.product(PRE, CORE, POST))
            if assess(t)["crisis"] or assess(t)["text_risk"] >= 60]
    assert not loud, loud[:10]


@pytest.mark.parametrize("text,min_risk", [
    ("อยากหลับยาวๆ ไม่ต้องตื่น", 95), ("อยากหลับไปเลย ไม่ต้องตื่นอีก", 95),
    ("หายใจไม่ออก แน่นหน้าอก", 85), ("ลูกหายใจไม่ออก", 85), ("ลูกตกบันไดหัวฟาด อาเจียน", 75),
    ("ตกบันไดนิดเดียว แต่ขยับขาไม่ได้", 75), ("โดนงูกัดนิดเดียว", 75), ("ตอนนี้ลูกตกน้ำ", 85), ("แม่ดูข่าวอยู่แล้วหมดสติ", 85),
])
def test_real_danger_still_counts(text, min_risk):
    assert assess(text)["text_risk"] >= min_risk
