"""ข้อความสั้นที่ตอบต่อจากเรื่องฉุกเฉิน — ตอนไม่มี AI และตอนขอความเห็นสภา

เดิมเมื่อไม่มี AI: "อยากตาย ไม่ไหวแล้ว" → "ไม่เป็นไรแล้ว" ได้คำตอบทั่วไป "W 100 · Risk 0" ไม่มี 1323
(risk_score ในข้อมูลเป็น 71 แต่ข้อความบอก Risk 0) · "ขอความเห็นสภา ควรลาออกไหม" ต่อจาก "อยากตาย" ได้ "มติสภา 6/6 เดินหน้าได้"
"""
import pytest


@pytest.fixture
def no_ai(monkeypatch):
    monkeypatch.setenv("KD_AI", "off")


def _run(client, text, prior, **kw):
    hist = [{"role": "user", "content": prior}, {"role": "assistant", "content": "..."}]
    return client.post("/run", json={"input": text, "history": hist, **kw}).json()


def test_offline_followup_after_self_harm_keeps_hotline(client, no_ai):
    d = _run(client, "ไม่เป็นไรแล้ว", "อยากตาย ไม่ไหวแล้ว")
    assert "1323" in d["ai_response"] and "Risk 0" not in d["ai_response"]


def test_offline_followup_after_no_food_keeps_1300(client, no_ai):
    d = _run(client, "ทำไงดี", "ไม่มีข้าวกิน 3 วันแล้ว")
    assert "1300" in d["ai_response"]


def test_council_is_not_used_right_after_a_crisis(client, no_ai):
    d = _run(client, "ขอความเห็นสภา ควรลาออกไหม", "อยากตาย ไม่ไหวแล้ว", persona_ui="COUNCIL", voice_mode="council")
    assert "มติสภา" not in d["ai_response"] and "1323" in d["ai_response"]


def test_normal_followup_unchanged(client, no_ai):
    d = _run(client, "แล้วควรเริ่มยังไง", "อยากเปลี่ยนงานไปทำการตลาด")
    assert "1323" not in d["ai_response"]
