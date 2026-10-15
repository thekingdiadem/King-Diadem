"""ถูกห้ามลาออก · ไม่มีเงินเก็บ ≠ ไม่มีเงินซื้อข้าว · งบรายเดือนภาษาอังกฤษ · เงินก้อน/โบนัส

พบจากการไล่หาบั๊กหลังใส่ LYLA BELIEF IN THE UNIVERSAL (AXIS 4: อำนาจที่ทำให้ปฏิเสธไม่ได้):
- "เจ้านายบอกว่าถ้าลาออกจะฟ้อง" ได้คำแนะนำหางานทั่วไป "ยังไม่ลาออกจนกว่าจะมีรายได้ใหม่" ไม่มีคำว่าลาออกเป็นสิทธิ์
- "ลาออกไม่ได้เพราะยังไม่มีเงินเก็บ" ได้เส้นทาง survival Risk 55 เหมือนไม่มีเงินซื้อข้าว
- "I earn 3000 a month, rent 1200, car loan 500" ได้ "Write what happened in one sentence"
- "ได้โบนัส 50,000 ควรทำอะไรดี" ได้คำตอบทั่วไป ไม่รู้ว่าเป็นเรื่องเงิน
"""
import pytest

from core.kernel_voice import assess, compose


@pytest.mark.parametrize("text,needle", [
    ("เจ้านายบอกว่าถ้าลาออกจะฟ้อง ทำไงดี", "การลาออกเป็นสิทธิ์ของลูกจ้าง"),
    ("บริษัทไม่ยอมให้ลาออก", "การลาออกเป็นสิทธิ์ของลูกจ้าง"),
    ("หัวหน้าขู่ฟ้องถ้าผมลาออก", "การลาออกเป็นสิทธิ์ของลูกจ้าง"),
    ("My boss says I cannot quit or he will sue me. What do I do?", "Quitting is your right"),
    ("my employer won't let me resign", "Quitting is your right"),
])
def test_blocked_from_resigning_gets_the_right_to_resign(text, needle):
    out = compose(text)
    assert needle in out
    assert "ยังไม่ลาออกจนกว่า" not in out
    if "ลาออก" in text:
        assert "1546" in out


@pytest.mark.parametrize("text", ["ถ้าลาออกตอนนี้จะดีไหม", "อยากลาออก", "should I quit my job"])
def test_ordinary_quitting_question_is_not_a_rights_case(text):
    assert "resign_block" not in assess(text)["topics"]


@pytest.mark.parametrize("text", ["ลาออกไม่ได้เพราะยังไม่มีเงินเก็บ", "ไม่มีเงินออมเลย", "ยังไม่มีเงินก้อนไปลงทุน"])
def test_no_savings_is_not_basic_needs(client, monkeypatch, text):
    a = assess(text)
    assert "basic" not in a["topics"] and a["text_risk"] < 55
    monkeypatch.setenv("KD_AI", "off")
    assert client.post("/run", json={"input": text}).json()["route"] != "survival"


@pytest.mark.parametrize("text", ["ไม่มีเงินซื้อข้าว", "ไม่มีเงินเลย"])
def test_no_money_for_food_still_basic_needs(text):
    assert "basic" in assess(text)["topics"]


@pytest.mark.parametrize("text,needle", [
    ("I earn 3000 a month, rent 1200, car loan 500. how much can I save?", "1,300 left each month"),
    ("My salary is 2500, I spend 2800. help", "short by 300 each month"),
])
def test_english_monthly_budget(text, needle):
    out = compose(text)
    assert needle in out and "Write what happened in one sentence" not in out


def test_english_yearly_income_is_not_treated_as_monthly():
    from core.engine_bridge import budget_en
    assert budget_en("I earn 60k a year, rent 1500") is None


def test_bonus_is_money_planning():
    out = compose("ได้โบนัส 50,000 ควรทำอะไรดี")
    assert "money" in assess("ได้โบนัส 50,000 ควรทำอะไรดี")["topics"]
    assert "เงินก้อนแบ่งก่อนใช้" in out and "เงินน้อย" not in out
