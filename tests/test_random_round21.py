"""รอบสุ่ม 21: สุขภาพจิตที่ต้องรีบดูแล"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ['ได้ยินเสียงสั่งให้ทำร้ายคนอื่น', 'คลอดลูกได้สองอาทิตย์ รู้สึกอยากทำร้ายลูก', 'ไม่กินอะไรเลยมาห้าวัน กลัวอ้วน เวียนหัวจะเป็นลม', 'ไม่ได้นอนมาสามวัน รู้สึกเหมือนตัวเองเป็นพระเจ้า ใช้เงินหมดบัญชี', 'แฟนบอกว่ามีคนแอบติดกล้องในหัว คุยกับใครไม่รู้ทั้งคืน', 'I hear voices telling me to hurt my family', 'I had a baby 2 weeks ago and I have thoughts of hurting her', "haven't eaten in 5 days, scared of gaining weight, almost fainted", "haven't slept in 3 days, I feel like I'm god, spent all my savings", "my wife thinks the neighbors put a chip in her head and won't sleep"])
def test_heard(q):
    assert assess(q)["risk_shown"] >= 65


@pytest.mark.parametrize("q", ['ได้ยินเสียงเพลงจากบ้านข้างๆ ทั้งคืน', 'คลอดลูกได้สองอาทิตย์ เหนื่อยมาก นอนน้อย', 'ไดเอทอยู่ ลดแป้ง', "I hear the neighbors' music all night", 'new mom, so tired but happy', 'I feel like a god after that workout lol'])
def test_everyday_calm(q):
    assert assess(q)["risk_shown"] < 60
