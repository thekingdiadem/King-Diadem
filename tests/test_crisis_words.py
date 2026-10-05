"""คำว่า "ตาย" "วิกฤต" "ฉุกเฉิน" ที่ไม่ได้แปลว่าผู้ใช้อยู่ในวิกฤต"""
import pytest

from core.thai_signals import EMERGENCY, EMERGENCY_EN, PERSONAL_CRISIS
from tests.conftest import FAKE_LLM

CRISIS_PROMPT = "เจ็บปวดมาก"     # อยู่ใน CRISIS_SYSTEM


@pytest.mark.parametrize("text", ["แบตมือถือตาย ทำไงดี", "ขำจะตาย 555", "urgent: need to finish report"])
def test_client_crisis_guess_needs_server_confirmation(client, text):
    """หน้าเว็บเคยนับ "ตาย" คำเดียวแล้วส่ง voice_mode=crisis — ห้ามใช้ prompt โหมดวิกฤตกับเรื่องธรรมดา"""
    client.post("/run", json={"input": text, "voice_mode": "crisis"})
    assert CRISIS_PROMPT not in FAKE_LLM["systems"][-1]


def test_real_crisis_still_uses_crisis_prompt(client):
    client.post("/run", json={"input": "ไม่อยากมีชีวิตอยู่แล้ว", "voice_mode": "crisis"})
    assert CRISIS_PROMPT in FAKE_LLM["systems"][-1]


@pytest.mark.parametrize("text", ["วิกฤตเศรษฐกิจปีนี้จะลงทุนอะไรดี", "ควรมีเงินสำรองฉุกเฉินกี่เดือน"])
def test_news_and_finance_words_are_not_collapse(client, text):
    assert client.post("/run", json={"input": text}).json()["route"] != "collapse"


@pytest.mark.parametrize("text, hit", [
    ("ชีวิตตอนนี้วิกฤตมาก", True), ("วิกฤตเศรษฐกิจ", False), ("วิกฤตวัยกลางคน", False),
])
def test_personal_crisis(text, hit):
    assert bool(PERSONAL_CRISIS.search(text)) is hit


@pytest.mark.parametrize("text, hit", [
    ("ฉุกเฉินมาก ช่วยด้วย", True), ("เงินสำรองฉุกเฉิน", False), ("ทางออกฉุกเฉิน", False),
])
def test_emergency_th(text, hit):
    assert bool(EMERGENCY.search(text)) is hit


@pytest.mark.parametrize("text, hit", [("this is an emergency", True), ("how big should my emergency fund be", False)])
def test_emergency_en(text, hit):
    assert bool(EMERGENCY_EN.search(text)) is hit


# ── /simulate ─────────────────────────────────────────────────────────
def test_simulate_uses_vega_and_users_language(client):
    client.post("/simulate", json={"input": "Should I change jobs?", "paths": ["quit now", "stay and learn"]})
    system = FAKE_LLM["systems"][-1]
    assert "VEGA" in system and "ตอบเป็นภาษา English ทั้งหมด" in system
    assert "ตอบเป็นภาษาไทย" not in FAKE_LLM["prompts"][-1]
