"""คำตอบที่ตรงใจ: ตอบให้ถูกคน และตอบตรงความรู้สึกที่เขาพูดออกมา

1) "ถ้าไม่มีหนู พ่อแม่คงสบายขึ้น" คือความเชื่อว่าตัวเองเป็นภาระ — คำตอบต้องพูดถึงความรู้สึกนั้นตรงๆ
   ไม่ใช่แค่คำถามคัดกรองทั่วไป และยังต้องมีสายด่วน 1323
2) เล่าสัญญาณเตือนของ "คนอื่น" — เคยได้คำตอบที่ถามผู้ใช้ว่า "คุณคิดทำร้ายตัวเองไหม" ซึ่งถามผิดคน
"""
import pytest
from core.kernel_voice import assess, compose


@pytest.mark.parametrize("q", ["ถ้าไม่มีหนู พ่อแม่คงสบายขึ้น", "ถ้าขาดผมไป ครอบครัวคงมีความสุขกว่า"])
def test_burden_belief_gets_a_reply_about_that_feeling(q):
    r = assess(q)
    assert r["topics"][0] == "burden" and r["risk_shown"] >= 80
    reply = compose(q)
    assert "ภาระ" in reply and "1323" in reply


def test_burden_reply_in_english():
    from core.kernel_voice import EN_TOPIC
    open_line, paths, ask = EN_TOPIC["burden"]
    assert "burden" in " ".join(paths) and "988" in " ".join(paths)


@pytest.mark.parametrize("q", [
    "my brother gave away his dog and his guitar this week",
    "พี่ชายบอกว่าถ้าไม่มีเขาที่บ้านคงสบายขึ้น แล้วก็เงียบไปเลย",
    "น้องชายยกแมวที่รักที่สุดให้คนอื่น แล้วแจกของหมดเลย",
    "my husband stopped eating and keeps saying everyone would be better without him",
])
def test_warning_signs_about_someone_else_are_answered_for_the_helper(q):
    r = assess(q)
    assert r["topics"][0] == "someone" and r["risk_shown"] >= 80
    reply = compose(q).lower()
    assert "คุณคิดทำร้ายตัวเอง" not in reply and "are you having thoughts of hurting yourself" not in reply
