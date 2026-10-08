"""GeminiLLM._call กับคำตอบที่ถูกตัดกลางทาง (ภาพจากเว็บจริง: "…การที่เรื่องนี้ยังวนอยู่ในใจของคุณและ")"""
import itertools
from types import SimpleNamespace

import pytest

import core.llm_gemini as L
from tests.conftest import REAL_CALL

pytestmark = pytest.mark.skipif(L.types is None, reason="ไม่มี google-genai")
_n = itertools.count()

FULL = "ฉันรับฟังอยู่นะคะ ตอนนี้คุณอยู่ในที่ปลอดภัยไหมคะ ถ้ายังไม่ปลอดภัย ไปอยู่ใกล้คนอื่นไว้ก่อนนะคะ\n\n— LYLA ◈"
CUT = "ฉันรับฟังนะคะว่าคุณพ่อตีหัวคุณ 🤍\n\nไม่ว่าจะด้วยเหตุผลอะไร การที่เรื่องนี้ยังวนอยู่ในใจของคุณและ"


class FakeModels:
    def __init__(self, replies):
        self.replies, self.configs, self.models = list(replies), [], []

    def generate_content(self, model, contents, config):
        self.models.append(model)
        self.configs.append(config)
        r = self.replies.pop(0)
        if isinstance(r, Exception):
            raise r
        text, finish = r
        return SimpleNamespace(text=text, candidates=[SimpleNamespace(finish_reason=finish)])


def make(replies, model="gemini-2.0-flash-lite", chain=("gemini-2.0-flash-lite", "gemini-2.5-flash")):
    llm = L.GeminiLLM.__new__(L.GeminiLLM)
    llm.model, llm._keys, llm.MODEL_FALLBACK_CHAIN = model, ["k"], list(chain)
    llm.client = SimpleNamespace(models=FakeModels(replies))
    llm._rotate_key = lambda: None
    return llm


def call(llm):
    L._tls.fallback = False
    text = f"พ่อตีหัว {next(_n)}"                        # ไม่ให้ cache ของเทสต์ก่อนหน้าตอบแทน
    contents = [L.types.Content(role="user", parts=[L.types.Part.from_text(text=text)])]
    return REAL_CALL(llm, "LYLA", contents)


def test_safety_cut_tries_next_model():
    llm = make([(CUT, "FinishReason.SAFETY"), (FULL, "FinishReason.STOP")])
    assert call(llm) == FULL and llm.client.models.models == ["gemini-2.0-flash-lite", "gemini-2.5-flash"]


def test_safety_filter_only_blocks_high_harm():
    llm = make([(FULL, "FinishReason.STOP")])
    call(llm)
    ss = llm.client.models.configs[0].safety_settings
    assert ss and all(x.threshold == L.types.HarmBlockThreshold.BLOCK_ONLY_HIGH for x in ss)


def test_max_tokens_gets_one_bigger_retry():
    llm = make([(CUT, "FinishReason.MAX_TOKENS"), (FULL, "FinishReason.STOP")], chain=("gemini-2.0-flash-lite",))
    assert call(llm) == FULL
    a, b = llm.client.models.configs
    assert b.max_output_tokens == 2 * a.max_output_tokens


def test_never_returns_a_half_sentence():
    llm = make([(CUT, "FinishReason.SAFETY"), (CUT, "FinishReason.SAFETY")])
    out = call(llm)
    assert not out.endswith("และ")
    assert L._tls.fallback is True                     # ส่วนที่เหลือสั้นเกิน → ให้คำตอบจากสมการแทน


def test_long_partial_is_trimmed_to_last_sentence():
    long_cut = ("ขอบคุณที่เล่าให้ฟังนะคะ " * 6) + "\n\nสิ่งที่อยากชวนคิดต่อคือการที่"
    llm = make([(long_cut, "FinishReason.SAFETY"), (long_cut, "FinishReason.OTHER")])
    out = call(llm)
    assert out.endswith("นะคะ") and L._tls.fallback is False


def test_thinking_models_get_a_thinking_limit():
    llm = make([(FULL, "FinishReason.STOP")], model="gemini-3-flash", chain=())
    call(llm)
    tc = llm.client.models.configs[0].thinking_config
    assert tc.thinking_level == L.types.ThinkingLevel.LOW


def test_model_that_rejects_thinking_config_is_retried_plain():
    llm = make([ValueError("400 thinking_level is not supported"), (FULL, "FinishReason.STOP")],
               model="gemini-flash-latest", chain=())
    assert call(llm) == FULL and llm.client.models.configs[1].thinking_config is None


def test_outage_trips_breaker_so_next_users_dont_wait(monkeypatch):
    """Gemini ล่มแบบ 503 (ไม่ใช่โควตา) — เดิมทุกข้อความรอได้ถึง 45 วินาที เพราะไม่เคยพักวงจร"""
    monkeypatch.setattr(L.time, "sleep", lambda s: None)
    monkeypatch.setattr(L, "_ai_down_until", 0.0)
    L._fail_times.clear()
    boom = [RuntimeError("503 Service Unavailable")] * 8
    for _ in range(2):
        llm = make(list(boom), chain=("gemini-2.0-flash-lite",))
        call(llm)
        assert L._tls.fallback
    assert L.ai_disabled()                                  # ล้มทั้งชุด 2 ครั้ง → พักสั้นๆ
    llm = make([(FULL, "FinishReason.STOP")])
    call(llm)
    assert llm.client.models.models == []                  # คนถัดไปไม่ต้องรอ Gemini เลย
    monkeypatch.setattr(L, "_ai_down_until", 0.0)


def test_single_failure_does_not_trip_breaker(monkeypatch):
    monkeypatch.setattr(L.time, "sleep", lambda s: None)
    monkeypatch.setattr(L, "_ai_down_until", 0.0)
    L._fail_times.clear()
    call(make([RuntimeError("503")] * 4, chain=("gemini-2.0-flash-lite",)))
    assert not L.ai_disabled()
    L._fail_times.clear()
