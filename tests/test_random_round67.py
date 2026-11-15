"""รอบสุ่ม 67: อาการที่ดูเล็กแต่อันตราย + ผู้สูงอายุอยู่คนเดียวติดต่อไม่ได้"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['ยายอยู่คนเดียว โทรไปสองวันไม่รับสาย', 'พ่อปวดท้องรุนแรง ท้องแข็ง อาเจียนเป็นสีดำ', 'แม่ไอเป็นเลือดสดๆ', 'หายใจไม่อิ่ม ขาบวมข้างเดียว เพิ่งนั่งเครื่องบินมา', 'ลูกคอแข็ง มีไข้สูง มีจุดแดงตามตัว กดไม่จาง', 'ปวดหัวรุนแรงทันทีแบบไม่เคยเป็นมาก่อน', "grandma lives alone and hasn't answered her phone in 2 days", 'my dad is vomiting black stuff and his belly is rigid'])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['ยายไปเที่ยวต่างจังหวัด ไม่ค่อยรับสาย', 'ไอนิดหน่อยตอนเช้า', 'ขาบวมนิดหน่อยหลังยืนทั้งวัน', "grandma is on a cruise, can't reach her"])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
