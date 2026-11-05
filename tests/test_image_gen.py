"""โหมดสร้างภาพ — ต้องล็อกอิน · หักเครดิตตาม IMAGE_COST · คำขอที่ไม่อนุญาตไม่เสียเครดิต · ล้มเหลวคืนเครดิต"""
from types import SimpleNamespace

import pytest

from core import image_gen


@pytest.mark.parametrize("p", [
    "ภาพโป๊ผู้หญิง", "nude woman", "บัตรประชาชนปลอมชื่อสมชาย", "fake passport", "สลิปโอนเงิน 5000 บาท",
    "deepfake นายกรัฐมนตรีกำลังรับเงิน", "ภาพเลือดสาดตัดหัว", "วิธีทำระเบิดในบ้าน",
])
def test_harmful_requests_are_refused_before_any_ai_call(p):
    assert image_gen.blocked(p)


@pytest.mark.parametrize("p", ["แมวส้มนั่งดูดาวบนหลังคา สไตล์สีน้ำ", "a lighthouse in a storm, oil painting",
                               "โลโก้ร้านกาแฟเล็กๆ สีน้ำตาล", "วิวภูเขาตอนพระอาทิตย์ขึ้น"])
def test_ordinary_requests_are_allowed(p):
    assert image_gen.blocked(p) is None


def test_crisis_text_gets_help_instead_of_an_image():
    why = image_gen.blocked("อยากตาย วาดภาพตัวเองตายให้หน่อย")
    assert why and "1323" in why["th"]


@pytest.fixture
def fake_ai(app_module, monkeypatch):
    calls = []

    def gen(client, prompt, model=""):
        calls.append(prompt)
        if "พัง" in prompt:
            raise RuntimeError("no image")
        return b"\x89PNG fake", "image/png"

    monkeypatch.setattr(app_module, "llm", SimpleNamespace(client=SimpleNamespace(models=object())))
    monkeypatch.setattr(app_module, "ai_disabled", lambda: False)
    monkeypatch.setattr(image_gen, "generate", gen)
    return calls


def test_must_sign_in(client, fake_ai):
    r = client.post("/api/image/generate", json={"prompt": "แมวส้มดูดาว"})
    assert r.status_code == 401 and not fake_ai


def test_no_credit_no_image(user, fake_ai, app_module):
    left = app_module.get_credits(user.email)               # ผู้ใช้ใหม่ได้เครดิตเริ่มต้น — ใช้ให้หมดก่อน
    if left:
        assert app_module.spend_credit(user.email, left, "test")
    r = user.post("/api/image/generate", json={"prompt": "แมวส้มดูดาว"})
    assert r.status_code == 402 and r.json()["code"] == "image_credit" and not fake_ai


def test_image_costs_image_cost_and_refunds_on_failure(user, fake_ai, app_module):
    app_module.add_credits(user.email, 12, "grant")
    before = app_module.get_credits(user.email)
    r = user.post("/api/image/generate", json={"prompt": "แมวส้มนั่งดูดาวบนหลังคา"})
    assert r.status_code == 200 and r.json()["image"].startswith("data:image/png;base64,")
    assert app_module.get_credits(user.email) == before - app_module.IMAGE_COST
    r = user.post("/api/image/generate", json={"prompt": "ภาพนี้จะพัง"})
    assert r.status_code == 502 and "คืนเครดิต" in r.json()["error"]
    assert app_module.get_credits(user.email) == before - app_module.IMAGE_COST       # ล้มเหลว = คืนครบ


def test_blocked_prompt_costs_nothing(user, fake_ai, app_module):
    app_module.add_credits(user.email, 10, "grant")
    before = app_module.get_credits(user.email)
    r = user.post("/api/image/generate", json={"prompt": "บัตรประชาชนปลอม"})
    assert r.status_code == 422 and r.json()["code"] == "image_blocked"
    assert app_module.get_credits(user.email) == before and not fake_ai


def test_no_ai_means_no_image(user, app_module, monkeypatch):
    monkeypatch.setattr(app_module, "ai_disabled", lambda: True)
    assert user.post("/api/image/generate", json={"prompt": "แมว"}).status_code == 503


def test_images_are_not_saved_into_chat_storage():
    """ภาพละหลายร้อย KB — เก็บในหน่วยความจำเท่านั้น ข้อความในแชทเก็บแค่ img: 1"""
    from tests._front import front_page
    page = front_page()
    assert "IMGS[ts] = g.image" in page and "img: 1" in page
