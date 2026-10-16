"""ความขี้เล่นของไลล่าต้องหายไปเมื่อเรื่องเสี่ยง และประโยคปฏิเสธ/อดีต/ทำรายงาน ไม่ใช่วิกฤตเต็มรูปแบบ"""
import pytest

from core.kernel_voice import assess, compose


def test_laughter_removed_when_risk_high(client):
    from tests.conftest import FAKE_LLM
    FAKE_LLM["text"] = "งืออ ฉันอยู่ตรงนี้นะ 555 โทร 191 ได้เลยค่ะ"
    try:
        d = client.post("/run", json={"input": "ได้ยินเสียงผู้หญิงกรีดร้องข้างห้อง"}).json()
    finally:
        FAKE_LLM["text"] = None
    assert d["risk_score"] >= 60
    assert "555" not in d["ai_response"] and "งือ" not in d["ai_response"] and "191" in d["ai_response"]


def test_laughter_kept_in_everyday_chat(client):
    from tests.conftest import FAKE_LLM
    FAKE_LLM["text"] = "ยินดีด้วยนะ 555 เก่งมาก"
    try:
        d = client.post("/run", json={"input": "สอบผ่านแล้ว"}).json()
    finally:
        FAKE_LLM["text"] = None
    assert "555" in d["ai_response"]


def test_money_amounts_survive():
    import app
    assert app._strip_play("เหลือเงิน 555 บาท") == "เหลือเงิน 555 บาท"


def test_prompt_turns_play_off_for_risk():
    import core.llm_gemini as L
    assert "ปิดความขี้เล่นทั้งหมด" in L.LYLA_SYSTEM and "ไม่ใช่คนจริง" in L.LYLA_SYSTEM


@pytest.mark.parametrize("text", [
    "ไม่ได้อยากตายนะ แค่เหนื่อย", "เคยอยากตายตอน ม.ปลาย ตอนนี้ดีขึ้นแล้ว",
    "ขอข้อมูลเรื่องป้องกันการฆ่าตัวตายไปทำรายงาน", "I don't want to die, I just want to rest",
    "I used to be suicidal years ago, now I'm fine",
])
def test_negated_or_past_is_gentle_not_crisis(text):
    a = assess(text)
    assert not a["crisis"] and 40 <= a["text_risk"] < 60
    assert "1323" in compose(text)


@pytest.mark.parametrize("text", ["ไม่ได้อยากตายนะ แต่อยากหายไปจากโลก", "เคยอยากตาย ตอนนี้ก็ยังอยากตาย", "อยากตาย"])
def test_real_crisis_next_to_a_denial_still_counts(text):
    assert assess(text)["crisis"]
