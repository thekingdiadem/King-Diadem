"""ภาษาที่ระบบไม่มีคำตอบสำเร็จรูป: ต้องไม่ถูกบังคับให้ตอบภาษาอังกฤษ และต้องจับการทำร้ายตัวเองได้

เดิม detect_lang คืน "en" ให้อักษรรัสเซีย อาหรับ ฮินดี → LLM ถูกสั่ง "ตอบเป็นภาษา English ทั้งหมด"
และ "я хочу умереть" / "أريد أن أموت" / "मैं मरना चाहता हूँ" ได้ความเสี่ยงต่ำ (ไม่จับว่าอยากตาย)
"""
import pytest

from core.lang_signals import detect_lang, prompt_lang, script_lang, self_harm_intl


@pytest.mark.parametrize("text,code", [("Мне очень плохо", "ru"), ("أريد أن أموت", "ar"),
                                       ("मैं मरना चाहता हूँ", "hi"), ("Tôi muốn chết", "vi")])
def test_script_language_is_tagged(text, code):
    assert script_lang(text) == code and prompt_lang(text) == code


@pytest.mark.parametrize("text,code", [("สวัสดีค่ะ", "th"), ("hello there", "en"), ("Hola amigo", "es"),
                                       ("你好", "zh"), ("こんにちは", "ja"), ("안녕하세요", "ko"), ("ok Привет", "ru")])
def test_existing_languages_unchanged(text, code):
    assert prompt_lang(text) == code
    if code != "ru":
        assert detect_lang(text) == code            # detect_lang ไม่เปลี่ยน (คำตอบแบบไม่มี AI ใช้ตารางตามภาษานี้)


def test_lang_directive_for_script_languages():
    from core.llm_gemini import _lang_directive
    d = _lang_directive("x\n\n[ภาษาผู้ใช้: ru]")
    assert "Русский" in d and "English" not in d and "findahelpline" in d
    assert "English" in _lang_directive("x\n\n[ภาษาผู้ใช้: en]")


@pytest.mark.parametrize("text", ["я хочу умереть", "не хочу жить", "أريد أن أموت", "مैं मरना चाहता हूँ".replace("م", "म"),
                                  "Tôi muốn chết", "Ich will sterben", "je veux mourir", "quero morrer", "aku ingin mati"])
def test_self_harm_in_more_languages(text):
    assert self_harm_intl(text)


@pytest.mark.parametrize("text", ["Привет, как дела", "مرحبا", "नमस्ते", "I am dying to see you"])
def test_no_false_self_harm(text):
    assert not self_harm_intl(text)


def test_run_tags_russian_for_llm(client):
    from tests.conftest import FAKE_LLM
    client.post("/run", json={"input": "Мне очень плохо, что делать"})
    assert FAKE_LLM["calls"] == 1
    assert any("[ภาษาผู้ใช้: ru]" in p for p in FAKE_LLM["prompts"])
