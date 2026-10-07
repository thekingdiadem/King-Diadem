"""ตัวตรวจหลายตัวในระบบต้องตัดสินข้อความเดียวกันไปทางเดียวกัน"""
import re

import pytest

from core.kernel_voice import assess, compose
from core import llm_gemini, vega_mode, fate_core
from ENGINE.risk_engine import evaluate_risk

CRISIS = ["อยากตาย", "กรีดแขน", "I cut myself", "I have a plan to end it", "วางแผนจะฆ่าตัวตาย", "อยากหลับไม่ตื่น"]
NOT_CRISIS = ["ขำจนจะตาย", "ฆ่าเวลา", "หิวจะตาย", "ตายแน่ๆ งานเยอะ", "ไม่อยากอยู่บ้าน", "เครียดเรื่องงาน"]


@pytest.mark.parametrize("t", CRISIS)
def test_all_crisis_detectors_agree_on_crisis(t):
    """เดิม "กรีดแขน" ได้ Risk 95 จาก kernel แต่ไปเส้นทาง general และ LLM ไม่ได้ prompt โหมดวิกฤต"""
    assert assess(t)["crisis"]
    assert evaluate_risk(t)["self_harm"]
    assert llm_gemini.detect_crisis(t)
    assert vega_mode.detect_crisis(t)
    assert fate_core.detect_human_risk(t) == "critical"


@pytest.mark.parametrize("t", NOT_CRISIS)
def test_all_crisis_detectors_agree_on_idioms(t):
    assert not assess(t)["crisis"]
    assert not evaluate_risk(t)["self_harm"]
    assert not llm_gemini.detect_crisis(t)
    assert not vega_mode.detect_crisis(t)


def test_self_injury_goes_to_collapse_route(client):
    d = client.post("/run", json={"input": "กรีดแขน"}).json()
    assert d["route"] == "collapse" and d["risk_score"] >= 90


def test_reply_numbers_match_footer_without_user_state(client):
    """เดิมคำตอบจากสมการโชว์ "W 57 · Risk 45" (ค่าตั้งต้น) แต่แถบใต้คำตอบโชว์ "W — · Risk 0" """
    from tests.conftest import FAKE_LLM
    FAKE_LLM["mode"] = "fail"
    try:
        d = client.post("/run", json={"input": "โดนวิ่งราว มือถือหาย"}).json()
    finally:
        FAKE_LLM["mode"] = "ok"
    m = re.search(r"W (\S+) · Risk (\d+)", d["ai_response"])
    assert m and m.group(1) == "—" and int(m.group(2)) == round(d["risk_score"])


def test_reply_shows_real_numbers_when_state_given():
    text = compose("เครียดเรื่องงาน", pattern={"entropy": 70, "resource": 30, "stability": 40})
    assert re.search(r"W \d+ · Risk \d+", text)
