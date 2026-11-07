"""/health ต้องบอกได้ว่า AI ใช้ได้จริงไหม และถ้าไม่ได้ เพราะอะไร

พี่บอกว่า "ระบบพี่ยังไม่มี AI" — เดิม /health บอกแค่ llm_loaded: true ทั้งที่ AI อาจถูกพักเพราะโควตาหมด
key ผิด หรือ Gemini ล่มติดกัน จึงไม่มีทางรู้จากภายนอกว่าทำไมคำตอบขึ้น "ตอบจากสมการ — ไม่ได้ใช้ AI"
"""
import json

import core.llm_gemini as L


def test_health_reports_ai_block_without_secrets(client, monkeypatch):
    monkeypatch.setattr(L, "_ai_down_until", 0.0)
    monkeypatch.delenv("KD_AI", raising=False)
    monkeypatch.delenv("LLM_DAILY_CAP", raising=False)
    h = client.get("/health").json()
    ai = h["ai"]
    assert set(ai) >= {"available", "reason"}
    assert "AIza" not in json.dumps(h) and "key" not in json.dumps(ai).lower().replace("api_keys", "")


def test_pause_reason_is_reported(monkeypatch):
    monkeypatch.setattr(L, "_ai_down_until", 0.0)
    monkeypatch.delenv("KD_AI", raising=False)
    L._mark_ai_down(120, "quota")
    st = L.ai_status()
    assert st["available"] is False and st["reason"] == "quota" and 100 < st["paused_for_s"] <= 120


def test_forced_off_and_daily_cap_are_explained(monkeypatch):
    monkeypatch.setattr(L, "_ai_down_until", 0.0)
    monkeypatch.setenv("KD_AI", "off")
    assert L.ai_status()["reason"] == "forced_off"
    monkeypatch.delenv("KD_AI")
    monkeypatch.setenv("LLM_DAILY_CAP", "3")
    monkeypatch.setattr(L, "_billed", {"day": L._today_th(), "n": 3})
    st = L.ai_status()
    assert st["available"] is False and st["reason"] == "daily_cap" and st["billed_today"] == 3


def test_healthy_ai_has_no_reason(monkeypatch):
    monkeypatch.setattr(L, "_ai_down_until", 0.0)
    monkeypatch.delenv("KD_AI", raising=False)
    monkeypatch.delenv("LLM_DAILY_CAP", raising=False)
    st = L.ai_status()
    assert st["available"] is True and st["reason"] is None and st["max_billed_per_message"] == 2
