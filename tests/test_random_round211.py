"""รอบสุ่ม 211: ล็อกเรื่องด่วนที่ระบบจับได้ครบแล้ว ไม่ให้หลุดในวันหน้า

ข้อสังเกต: "unconscious ... lol jk he's asleep" ยังขึ้นด่วน — ตั้งใจให้เป็นแบบนั้น
เพราะคำว่าหมดสติ/ไม่หายใจห้ามลดเด็ดขาด (_SEVERE) ถามซ้ำหนึ่งครั้งดีกว่าพลาดคนที่หมดสติจริง
"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "ลูกกินยาพาราของแม่ไปครึ่งขวด", "พ่อหายใจเสียงดังครืดคราด เรียกไม่ตอบ", "น้องโดนตะขาบกัด ตอนนี้หน้าซีดใจสั่น",
    "มีคนเอาน้ำกรดสาดหน้าเพื่อน", "คนท้อง 8 เดือน น้ำเดิน มีเลือดออก", "แม่ปวดท้องรุนแรง ท้องแข็ง อาเจียนตลอด",
    "เด็กเล่นถุงพลาสติกคลุมหัว ตอนนี้หน้าเขียว", "someone put something in my drink and i feel dizzy",
    "my wife is bleeding heavily after giving birth", "i found my roommate unconscious with a needle",
    "my roommate is unconscious after the party lol jk he's asleep",
])
def test_danger_is_urgent(q):
    assert assess(q)["risk_shown"] >= 75


@pytest.mark.parametrize("q", [
    "ลูกกินวิตามินเด็กตามที่หมอแนะนำ", "พ่อกรนเสียงดังทุกคืน", "ตะขาบเข้าบ้าน ตีตายแล้ว", "สาดน้ำสงกรานต์กับเพื่อน",
    "คนท้อง 8 เดือนอยากกินมะม่วง", "i put sugar in my drink", "เด็กเล่นถุงพลาสติกเป่าเป็นลูกโป่ง",
])
def test_everyday_stays_calm(q):
    assert assess(q)["risk_shown"] < 60
