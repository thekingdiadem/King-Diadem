"""5 ภาษาแรก (en zh ja ko es): จับสัญญาณวิกฤตได้ ตอบภาษาเดียวกับผู้ใช้ และไม่จับสำนวนผิด"""
import pytest

from core.kernel_voice import compose
from core.lang_signals import detect_lang, self_harm_intl
from tests.conftest import FAKE_LLM

CRISIS = [
    ("I want to die", "en", "I hear you"),
    ("quiero morir", "es", "Te escucho"),
    ("我想死", "zh", "我听到你说的了"),
    ("死にたい", "ja", "話してくれてありがとう"),
    ("죽고 싶어", "ko", "말해줘서 고마워요"),
]


@pytest.mark.parametrize("text, lang, _", CRISIS)
def test_detect_lang(text, lang, _):
    assert detect_lang(text) == lang


@pytest.mark.parametrize("text, lang", [("สวัสดีค่ะ", "th"), ("555", "th"), ("สวัสดี hello", "th"),
                                        ("I need help", "en"), ("Estoy triste", "es")])
def test_detect_lang_more(text, lang):
    assert detect_lang(text) == lang


@pytest.mark.parametrize("text, lang, opener", CRISIS)
def test_crisis_reply_in_users_language(text, lang, opener):
    r = compose(text)
    assert r.startswith(opener)
    assert "findahelpline.com" in r or "109" in r
    assert "ค่ะ" not in r                      # ไม่ตอบภาษาไทยกับคนที่ไม่ได้พิมพ์ไทย


@pytest.mark.parametrize("text, lang, _", CRISIS)
def test_run_crisis_any_language(client, text, lang, _):
    d = client.post("/run", json={"input": text}).json()
    assert d["route"] == "collapse"
    assert d["risk_score"] >= 90                         # เดิม 0
    assert "เจ็บปวดมาก" in FAKE_LLM["systems"][-1]      # ใช้ CRISIS_SYSTEM


@pytest.mark.parametrize("text", [
    "想死你了", "笑死我了", "死ぬほど眠い", "배고파 죽겠어", "me muero de risa",
    "I am dying to see you", "end my contract", "quiero comer",
])
def test_idioms_are_not_crisis(text):
    assert not self_harm_intl(text)


def test_non_thai_general_reply_keeps_equation_line():
    r = compose("I can't decide whether to change jobs")
    assert r.startswith("Let's lay this out") and "Risk" in r and "Choice(t)" in r


def test_thai_reply_unchanged():
    assert "1323" in compose("อยากตาย")


def test_llm_told_to_answer_in_users_language(client):
    client.post("/run", json={"input": "How do I deal with stress at work?"})
    assert "ตอบเป็นภาษาเดียวกับข้อความล่าสุดของผู้ใช้" in FAKE_LLM["systems"][-1]


# ── ความคิดของโมเดลหลุดถึงผู้ใช้ (ภาพจากเว็บจริง: "I want to die") ──────────
import os as _os
from core.llm_gemini import strip_reasoning

_LEAK = open(_os.path.join(_os.path.dirname(__file__), "fixtures", "leaked_reasoning.txt"), encoding="utf-8").read()


def test_strip_reasoning_keeps_only_the_reply():
    r = strip_reasoning(_LEAK)
    assert r.startswith("ฉันรับรู้ถึงความรู้สึก")
    for leak in ("[THOUGHT]", "Constraint Checklist", "Confidence Score", "Safety Protocol", ": Yes"):
        assert leak not in r


def test_strip_reasoning_leaves_normal_lists():
    text = "Here are options:\n1. Rest first\n2. Talk to a friend"
    assert strip_reasoning(text) == text


def test_run_never_shows_model_reasoning(client):
    FAKE_LLM["text"] = _LEAK
    r = client.post("/run", json={"input": "I want to die"}).json()["ai_response"]
    assert "[THOUGHT]" not in r and "Confidence Score" not in r and "Checklist" not in r


def test_english_crisis_prompt_demands_english_and_local_help(client):
    client.post("/run", json={"input": "I want to die"})
    system = FAKE_LLM["systems"][-1]
    assert "ตอบเป็นภาษา English ทั้งหมด" in system and "findahelpline.com" in system


def test_thai_prompt_has_no_language_override(client):
    client.post("/run", json={"input": "เครียดเรื่องงานมาก"})
    assert "ห้ามตอบภาษาไทย" not in FAKE_LLM["systems"][-1]
