"""หน้าจอจริง: เคสได้ยินเสียงผู้หญิงกรีดร้อง (Risk 70) LYLA ใส่ 🥺 ท้ายคำตอบ"""
import re

def test_emoji_removed_when_risk_high(client):
    from tests.conftest import FAKE_LLM
    FAKE_LLM["text"] = "เป็นห่วงมากเลยนะคะ 🥺 โทร 191 ได้เลยค่ะ ✨"
    try:
        d = client.post("/run", json={"input": "ได้ยินเสียงผู้หญิงกรีดร้องข้างห้อง"}).json()
    finally:
        FAKE_LLM["text"] = None
    assert d["risk_score"] >= 60
    assert "🥺" not in d["ai_response"] and "✨" not in d["ai_response"] and "191" in d["ai_response"]


def test_emoji_removed_in_everyday_chat_too(client):
    """เจ้าของโปรเจกต์: "พวกอิโมจิคนมองก็รู้ว่าทั้งหมดทำมาจาก AI" — คำตอบทุกเรื่องไม่มี emoji แต่ความยินดียังอยู่ในคำ"""
    from tests.conftest import FAKE_LLM
    FAKE_LLM["text"] = "ยินดีด้วยนะคะ 🎉 สอบผ่าน 555"
    try:
        d = client.post("/run", json={"input": "สอบผ่านแล้ว"}).json()
    finally:
        FAKE_LLM["text"] = None
    assert d["risk_score"] < 60 and "🎉" not in d["ai_response"] and "ยินดีด้วยนะคะ" in d["ai_response"]
    assert "555" in d["ai_response"]                       # เรื่องสบายๆ ยังเล่นได้ ตัดเฉพาะเรื่องเสี่ยง


def test_lyla_is_not_told_to_use_emoji():
    from core import llm_gemini as L
    for name in ("LYLA_SYSTEM", "JOY_SYSTEM", "LOVE_SYSTEM", "WORK_WIN_SYSTEM"):
        p = getattr(L, name)
        assert not re.search("[\U0001F000-\U0001FAFF]", p), name
        assert "ใช้ emoji ได้" not in p and "ใช้ emoji พอประมาณ" not in p, name


def test_system_symbols_survive():
    import app
    assert app._strip_emoji("— LYLA ◈ ✦ ☸ ▲ 🤍") == "— LYLA ◈ ✦ ☸ ▲"
