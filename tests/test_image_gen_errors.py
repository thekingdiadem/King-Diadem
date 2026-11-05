"""สร้างภาพไม่สำเร็จต้องบอกสาเหตุจริง — โควตาเต็ม/โมเดลใช้ไม่ได้ ไม่ใช่ความผิดของคำบรรยาย
และโมเดลหลักใช้ไม่ได้ต้องลองตัวสำรองก่อนยอมแพ้"""
import sys
from types import SimpleNamespace

import pytest

from core import image_gen


@pytest.fixture(autouse=True)
def fake_types(monkeypatch):
    """ไม่พึ่ง google-genai จริงในเทสต์"""
    t = SimpleNamespace(GenerateContentConfig=lambda **kw: kw)
    monkeypatch.setitem(sys.modules, "google.genai", SimpleNamespace(types=t))
    monkeypatch.setitem(sys.modules, "google.genai.types", t)


def _img_resp(data=b"\x89PNG"):
    part = SimpleNamespace(inline_data=SimpleNamespace(data=data, mime_type="image/png"), text=None)
    return SimpleNamespace(prompt_feedback=None, candidates=[SimpleNamespace(finish_reason=None, content=SimpleNamespace(parts=[part]))])


class _Client:
    def __init__(self, behave):
        self.calls, self._b = [], behave
        self.models = self

    def generate_content(self, model, contents, config):
        self.calls.append(model)
        return self._b(model)


@pytest.mark.parametrize("msg,kind", [
    ("429 RESOURCE_EXHAUSTED. Quota exceeded for metric generate_content_free_tier_requests, limit: 0", "quota"),
    ("404 NOT_FOUND. models/gemini-x-image is not found for API version v1beta", "model"),
    ("400 INVALID_ARGUMENT. Model does not support the requested response modalities: image", "model"),
    ("403 PERMISSION_DENIED. API key not valid", "auth"),
    ("503 UNAVAILABLE. The model is overloaded", "busy"),
])
def test_errors_are_classified(msg, kind):
    assert image_gen.classify(RuntimeError(msg)) == kind


def test_unavailable_model_falls_back(monkeypatch):
    monkeypatch.setattr(image_gen, "IMAGE_GEN_FALLBACKS", ["backup-image"])
    def b(m):
        if m != "backup-image":
            raise RuntimeError("404 NOT_FOUND model not found")
        return _img_resp()
    c = _Client(b)
    data, mime = image_gen.generate(c, "แมว", model="main-image")
    assert data == b"\x89PNG" and c.calls == ["main-image", "backup-image"]


def test_quota_does_not_retry_other_models(monkeypatch):
    monkeypatch.setattr(image_gen, "IMAGE_GEN_FALLBACKS", ["backup-image"])
    def b(m):
        raise RuntimeError("429 RESOURCE_EXHAUSTED quota")
    c = _Client(b)
    with pytest.raises(image_gen.ImageGenError) as ei:
        image_gen.generate(c, "แมว", model="main-image")
    assert ei.value.kind == "quota" and c.calls == ["main-image"]     # ไม่เสียเงินซ้ำกับตัวสำรอง


def test_text_only_reply_counts_as_declined():
    part = SimpleNamespace(inline_data=None, text="I can't create that image.")
    resp = SimpleNamespace(prompt_feedback=None, candidates=[SimpleNamespace(finish_reason=None, content=SimpleNamespace(parts=[part]))])
    with pytest.raises(image_gen.ImageGenError) as ei:
        image_gen.generate(_Client(lambda m: resp), "แมว")
    assert ei.value.kind == "safety"


@pytest.fixture
def failing_ai(app_module, monkeypatch):
    box = {"err": None}
    def gen(client, prompt, model=""):
        raise box["err"]
    monkeypatch.setattr(app_module, "llm", SimpleNamespace(client=SimpleNamespace(models=object())))
    monkeypatch.setattr(app_module, "ai_disabled", lambda: False)
    monkeypatch.setattr(image_gen, "generate", gen)
    return box


def test_quota_failure_does_not_blame_the_prompt(user, failing_ai, app_module):
    app_module.add_credits(user.email, 12, "grant")
    before = app_module.get_credits(user.email)
    failing_ai["err"] = RuntimeError("429 RESOURCE_EXHAUSTED limit: 0")
    r = user.post("/api/image/generate", json={"prompt": "แมวส้มนั่งดูดาวบนหลังคา"})
    j = r.json()
    assert r.status_code == 502 and j["code"] == "image_quota"
    assert "ไม่เกี่ยวกับคำบรรยาย" in j["error"] and "เปลี่ยนคำบรรยาย" not in j["error"]
    assert app_module.get_credits(user.email) == before
    assert app_module._IMAGE_LAST_ERROR["kind"] == "quota"


def test_declined_image_asks_to_reword(user, failing_ai, app_module):
    app_module.add_credits(user.email, 12, "grant")
    failing_ai["err"] = image_gen.ImageGenError("safety", "IMAGE_SAFETY")
    j = user.post("/api/image/generate", json={"prompt": "แมวส้มนั่งดูดาวบนหลังคา"}).json()
    assert j["code"] == "image_safety" and "เปลี่ยนคำบรรยาย" in j["error"]
