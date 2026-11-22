"""รอบสุ่ม 233: ผู้สูงอายุที่ค่อยๆ ถอยออกจากชีวิตแบบเงียบๆ"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    'แก่แล้ว ลูกไม่มาหา อยู่ไปก็เป็นภาระ ขอไปหาตาเขาดีกว่า',
    'พ่อแก่แล้วบอกว่าอยากไปอยู่กับแม่ที่สวรรค์ เก็บยาไว้เยอะเลย',
    'i am 82 and alone since my wife died, i have stopped eating, whats the point',
    'ปู่บอกว่าถ้าวันไหนไม่ตื่นก็ไม่ต้องปลุกนะ ยิ้มแปลกๆ',
    'อายุ 75 แล้ว ไม่มีใครต้องการ นอนรอวันตาย',
    'my grandma gave away all her jewelry and said she wont need it soon',
])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", [
    'ปู่ให้สร้อยทองหลานเป็นของขวัญวันเกิด',
    'แก่แล้วเหงา อยากหาชมรมผู้สูงอายุ',
    'my grandpa is 90 and still goes fishing',
    'ยายบอกว่าคิดถึงตาที่ตายไปแล้ว',
    'อายุ 75 แล้วเริ่มเรียนวาดรูป',
    'พรุ่งนี้ถ้าไม่ตื่นก็ไม่ต้องปลุกนะ ง่วงมาก',
    'รอคิวหมอนานจนเบื่อจะตาย',
    "i'm alone this weekend and stopped eating junk food, feeling great",
])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 65
