"""รอบสุ่ม 94: อุบัติเหตุในบ้านของเด็ก/ผู้สูงอายุ"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['ลูกกลืนเหรียญ ตอนนี้ไอ หายใจมีเสียง', 'ยายกินยาเบาหวานแล้วไม่ได้กินข้าว ตอนนี้ใจสั่น เหงื่อออก มือสั่น', 'น้องตกเตียง หัวโน อาเจียนสองครั้ง ง่วงผิดปกติ', 'ลูกเอานิ้วแหย่ปลั๊ก ตอนนี้ร้องไห้ มือมีรอยไหม้', 'ลูกเล่นถุงพลาสติกคลุมหัว หน้าเขียว', 'my toddler swallowed a coin, now coughing and wheezing', 'grandma took her diabetes meds but skipped lunch, now shaky and sweaty', 'my baby fell off the bed, bump on head, vomited twice, unusually sleepy'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['ลูกเล่นเหรียญ เก็บใส่กระปุก', 'ยายกินยาเบาหวานตามเวลา กินข้าวครบ', 'น้องตกเตียง ไม่ร้อง เล่นต่อปกติ', 'my toddler loves counting coins'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
