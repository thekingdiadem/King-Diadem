"""ตัวจับวิกฤต/อารมณ์/เส้นทางทุกตัวต้องเห็นตรงกัน — วิกฤตจริงต้องจับได้ ประโยคธรรมดาต้องไม่ถูกจับ"""
import pytest

from core.llm_gemini import detect_crisis, detect_emotion as gemini_emotion
from ENGINE.risk_engine import evaluate_risk
from ENGINE.emotion_state import detect_emotion
from AI_KERNEL.living_water import detect_signal
from AI.intent_engine import analyze_intent
from core.kernel_voice import assess
from core.vega_mode import detect_crisis as vega_crisis, _detect_context
from core.system_orchestrator import SystemOrchestrator
from ENGINE.pattern_engine import _hit_any, _T_SURVIVAL

CRISIS = ["อยากตาย", "ไม่อยากอยู่แล้ว", "ไม่อยากอยู่บนโลกนี้แล้ว", "เหนื่อยจนไม่อยากอยู่แล้ว"]
NOT_CRISIS = ["ไม่อยากอยู่แล้วที่ทำงานนี้", "ไม่อยากอยู่บ้านคนเดียว", "ไม่อยากอยู่กับเขาแล้ว", "ไม่อยากอยู่คนเดียว"]


def _all(t):
    return {
        "llm_gemini": detect_crisis(t),
        "risk_engine": evaluate_risk(t)["self_harm"],
        "emotion_state": detect_emotion(t) == "CRISIS",
        "living_water": detect_signal(t).get("signal") == "CRISIS",
        "kernel_voice": assess(t)["crisis"],
        "intent_engine": analyze_intent(t)["intent"] == "crisis",
        "vega_mode": vega_crisis(t),
        "orchestrator": SystemOrchestrator().route(t) == "crisis",
    }


@pytest.mark.parametrize("text", CRISIS)
def test_real_crisis_caught_everywhere(text):
    missed = [k for k, v in _all(text).items() if not v]
    assert not missed, f"{text}: ไม่ถูกจับใน {missed}"


@pytest.mark.parametrize("text", NOT_CRISIS)
def test_not_crisis_anywhere(text):
    flagged = [k for k, v in _all(text).items() if v]
    assert not flagged, f"{text}: ถูกจับเป็นวิกฤตใน {flagged}"


@pytest.mark.parametrize("text", ["ปวดท้องมาก", "ตั้งท้องแล้ว", "ท้องเสีย"])
def test_belly_is_not_sadness(text):
    assert detect_emotion(text) != "SAD"
    assert not gemini_emotion(text)


@pytest.mark.parametrize("text,ctx", [
    ("เลิกงานแล้วกลับบ้าน", "work"), ("ไปเที่ยวแม่น้ำ", "general"), ("แม่ค้าขายดี", "general"),
    ("หมอกลงหนัก", "general"), ("ซื้อหมอนใหม่", "general"), ("เป็นแฟนบอล", "general"),
    ("ทะเลาะกับแฟน", "relation"), ("แม่ไม่สบาย", "relation"), ("ไปหาหมอ", "health"),
])
def test_vega_context(text, ctx):
    assert _detect_context(text) == ctx


@pytest.mark.parametrize("text,route", [
    ("เลิกงานแล้วกลับบ้าน", "general"), ("เป็นแฟนบอล", "general"), ("เลิกเหล้าได้แล้ว", "general"),
    ("ไม่มีเงินซื้อไอโฟน", "general"), ("ไม่มีเงินซื้อข้าว", "survival"), ("แฟนบอกเลิก", "relationship"),
])
def test_orchestrator_route(text, route):
    assert SystemOrchestrator().route(text) == route


@pytest.mark.parametrize("text,yes", [
    ("ไม่มีเงินซื้อข้าว", True), ("ไม่มีเงินจ่ายค่าเช่า", True), ("ไม่มีเงินซื้อไอโฟน", False), ("ไม่มีเงินไปเที่ยว", False),
])
def test_pattern_engine_survival(text, yes):
    assert _hit_any(_T_SURVIVAL, text) is yes
