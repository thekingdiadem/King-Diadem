"""พร้อมใช้ Gemini 4 Hydrogen: ตั้ง GEMINI_MODEL=gemini-4-hydrogen ใน Render ได้เลย
  · รุ่น 4 ค่าเริ่มต้นคิดระดับ high (ช้า) และส่ง thinking_budget ไม่ได้ → ต้องส่ง thinking_level=low
  · ชื่อรุ่นใหม่ยังไม่แน่ชัด → ถ้า 404 ให้เสียแค่ครั้งแรก ไม่ใช่ทุกข้อความ
  · เวลาแยกตามรุ่นที่ /health → เทียบรุ่นใหม่กับรุ่นเดิมด้วยตัวเลขจริง"""
from google.genai import types

from core import latency
from core import llm_gemini as G


def test_gemini4_gets_low_thinking_level_and_no_budget():
    for m in ("gemini-4-hydrogen", "gemini-4-argon"):
        assert G._thinks(m)
        tc = G._thinking_config(m)
        assert tc.thinking_level == types.ThinkingLevel.LOW and tc.thinking_budget is None, m
    assert G._thinking_config("gemini-2.5-flash").thinking_budget == 0       # รุ่นเดิมไม่เปลี่ยน


def test_missing_model_is_skipped_after_first_404(monkeypatch):
    G._dead_models.clear()
    assert not G._model_dead("gemini-4-nope")
    G._mark_model_dead("gemini-4-nope")
    assert G._model_dead("gemini-4-nope")
    monkeypatch.setattr(G.time, "time", lambda: 10 ** 12)                    # พ้นเวลาที่จำไว้ → ลองใหม่ได้
    assert not G._model_dead("gemini-4-nope")
    G._dead_models.clear()


def test_call_loop_skips_dead_models_and_marks_404():
    import inspect
    src = inspect.getsource(G)
    assert "alive = [m for m in models_to_try if not _model_dead(m)]" in src
    assert "for model_name in (alive or models_to_try):" in src          # ถ้าตายหมดทุกรุ่น ยังลองตามเดิม ไม่เงียบ
    i = src.index('"404", "not_found"')
    assert "_mark_model_dead(model_name)" in src[i:i + 400]


def test_per_model_latency():
    latency.reset()
    for ms in (800, 900, 1000):
        latency.record_model("gemini-4-hydrogen", ms)
    latency.record_model("gemini-2.0-flash-lite", 1500)
    b = latency.by_model()
    assert b["gemini-4-hydrogen"] == {"n": 3, "p50": 900, "p95": 1000, "p99": 1000}
    assert b["gemini-2.0-flash-lite"]["n"] == 1
    latency.reset()
    assert latency.by_model() == {}
