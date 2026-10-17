"""get_llm เคยคืนตัวเดิมเงียบๆ แม้ขอโมเดลอื่น และสร้างซ้อนกันได้เมื่อมีหลาย request พร้อมกัน"""
import threading

from core import llm_gemini


def test_one_instance_per_model_and_thread_safe(monkeypatch):
    made = []

    class Fake:
        def __init__(self, model=""):
            made.append(model)
            self.model = model
    monkeypatch.setattr(llm_gemini, "GeminiLLM", Fake)
    monkeypatch.setattr(llm_gemini, "_instance", None)
    monkeypatch.setattr(llm_gemini, "_instances", {})
    ts = [threading.Thread(target=llm_gemini.get_llm) for _ in range(20)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    assert made == [""]
    assert llm_gemini.get_llm("other").model == "other"
    assert llm_gemini.get_llm() is llm_gemini.get_llm()
