"""ผู้ให้บริการ AI รายที่ 2 — เปลี่ยนเจ้าได้ด้วย env, governance ชุดเดิม, ล่มแล้วยังตอบได้"""
import io
import json
import urllib.error
import uuid

import pytest

from core import llm_gemini as L
from core.llm_openai_compat import OpenAICompatLLM


@pytest.fixture
def compat_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai_compat")
    monkeypatch.setenv("LLM_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("LLM_API_KEY", "k1")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("LLM_CALL_BUDGET_S", "5")
    monkeypatch.setattr(L, "_instance", None)
    monkeypatch.setattr(L, "_instances", {})
    monkeypatch.setattr(L, "_ai_down_until", 0.0)
    L.reset_fallback_flag()


def _reply(text, finish="stop"):
    return {"choices": [{"message": {"role": "assistant", "content": text}, "finish_reason": finish}]}


def test_default_provider_is_gemini(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    assert L._provider_class() is L.GeminiLLM


def test_env_switches_provider(compat_env):
    llm = L.get_llm()
    assert isinstance(llm, OpenAICompatLLM)
    assert llm.model == "test-model"


def test_unknown_provider_does_not_guess(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mystery")
    with pytest.raises(ValueError):
        L._provider_class()


def test_missing_config_refuses(monkeypatch, compat_env):
    monkeypatch.delenv("LLM_API_KEY")
    with pytest.raises(ValueError):
        OpenAICompatLLM()


def test_same_governance_reaches_second_provider(compat_env, monkeypatch):
    """system prompt ของ governance ต้องไปถึงผู้ให้บริการรายที่ 2 ครบเหมือน Gemini"""
    sent = {}

    def fake_post(self, payload, timeout):
        sent.update(payload)
        return _reply("ลองพักสักครู่ แล้วค่อยเลือกทางที่เสียน้อยที่สุดค่ะ")

    monkeypatch.setattr(OpenAICompatLLM, "_post", fake_post)
    llm = L.get_llm()
    out = llm.generate(f"ทดสอบ {uuid.uuid4()}", system_prompt="SYSTEM-RULE-X")
    assert "ลองพัก" in out
    assert sent["model"] == "test-model"
    assert sent["messages"][0]["role"] == "system"
    assert "SYSTEM-RULE-X" in sent["messages"][0]["content"]
    assert sent["messages"][-1]["role"] == "user"
    assert not L.used_fallback()


def test_history_roles_mapped(compat_env):
    contents = L._build_contents(
        [{"role": "user", "content": "สวัสดี"}, {"role": "assistant", "content": "สวัสดีค่ะ"}], "ต่อเลย")
    msgs = OpenAICompatLLM._to_messages("S", contents)
    assert [m["role"] for m in msgs] == ["system", "user", "assistant", "user"]


def test_outage_falls_back_to_kernel_answer(compat_env, monkeypatch):
    """ผู้ให้บริการล่ม → ไม่ throw, ได้คำตอบสำรอง และติดธง fallback ให้ app ใช้คำตอบจากสมการ"""
    def boom(self, payload, timeout):
        raise urllib.error.HTTPError("u", 503, "down", {}, io.BytesIO(b""))

    monkeypatch.setattr(OpenAICompatLLM, "_post", boom)
    out = L.get_llm().generate(f"ล่ม {uuid.uuid4()}")
    assert isinstance(out, str) and out
    assert L.used_fallback()


def test_works_without_google_genai(compat_env, monkeypatch):
    """ไม่มีไลบรารี Gemini ก็ยังสร้างข้อความและใช้ผู้ให้บริการรายอื่นได้"""
    monkeypatch.setattr(L, "types", None)
    c = L._build_contents([], "ไม่มี genai")
    assert c[-1].role == "user" and c[-1].parts[0].text == "ไม่มี genai"
    monkeypatch.setattr(OpenAICompatLLM, "_post", lambda self, p, timeout: _reply("ได้ค่ะ"))
    assert L.get_llm().generate(f"x {uuid.uuid4()}") == "ได้ค่ะ"
