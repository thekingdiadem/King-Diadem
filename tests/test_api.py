"""เส้นทางจริงของแอปผ่าน FastAPI (Gemini ปลอม — ดู conftest.FAKE_LLM)"""
import pytest

from tests.conftest import FAKE_LLM
from DATABASE.db import get_credits, spend_credit

ROUTES = [
    ("วันนี้อากาศดี", "general"), ("ไม่มีข้าวกิน", "survival"), ("อยากตาย ไม่ไหวแล้ว", "collapse"),
    ("ไม่มีข้าวกินมาสองวันแล้ว", "survival"), ("เงินหมด งานพัง", "survival"),
    ("รอดูก่อนดีกว่า หิวข้าวจัง", "general"), ("ธุรกิจล้มละลาย ไม่มีเงินจ่ายหนี้", "collapse"),
    ("ไม่มีเงินซื้อไอโฟน", "general"), ("ชักจะเบื่องานแล้ว", "general"),
]


@pytest.mark.parametrize("text,route", ROUTES)
def test_run_route(client, text, route):
    d = client.post("/run", json={"input": text}).json()
    assert d["route"] == route
    assert d["ai_response"]
    assert FAKE_LLM["calls"] == 1              # เรียก LLM ครั้งเดียวต่อข้อความ


def test_vega_route(client):
    assert client.post("/run", json={"input": "วิเคราะห์ตลาดกาแฟ", "route": "vega"}).json()["route"] == "vega"


@pytest.mark.parametrize("bad", [None, 1, [], {"a": 1}, "x" * 50, True])
def test_run_never_500_on_odd_fields(client, bad):
    for key in ("route", "voice_mode", "history", "context", "input"):
        r = client.post("/run", json={"input": "เงินหมด", key: bad} if key != "input" else {"input": bad})
        assert r.status_code < 500, (key, bad, r.text[:200])


def test_crisis_prompt_only_for_real_crisis(client):
    client.post("/run", json={"input": "ไม่อยากอยู่แล้วที่ทำงานนี้"})
    assert not any("เจ็บปวดมาก" in s for s in FAKE_LLM["systems"])


def test_no_ai_answers_from_kernel_and_is_free(user):
    FAKE_LLM["mode"] = "fail"
    d = user.post("/run", json={"input": "เงินหมด งานพัง"}).json()
    assert d["answer_source"] == "kernel"
    assert "ไม่ได้ใช้ AI" in d["ai_response"]
    assert d["quota"]["free_left"] == 3        # ไม่หักโควตาเมื่อไม่ได้ใช้ AI


def test_quota_then_credits_then_402(user):
    start = get_credits(user.email)
    modes = [user.post("/run", json={"input": "เงินหมด"}).json()["quota"]["charged"] for _ in range(5)]
    assert modes == ["free", "free", "free", "credit", "credit"]
    assert get_credits(user.email) == start - 2
    while spend_credit(user.email, 1, "drain"):
        pass
    r = user.post("/run", json={"input": "เงินหมด"})
    assert r.status_code == 402 and r.json()["code"] == "quota_exhausted"


def test_auth_flow(client):
    assert client.post("/register", json={"email": "Case@Test.co", "password": "secret12"}).json()["email"] == "case@test.co"
    assert client.post("/register", json={"email": "case@test.co", "password": "other123"}).status_code == 409
    assert client.post("/login", json={"email": "case@test.co", "password": "nope"}).status_code == 401
    assert client.post("/login", json={"email": "CASE@TEST.CO", "password": "secret12"}).status_code == 200
    client.post("/logout", json={})
    assert not client.get("/me").json().get("logged_in")


def test_chat_state_isolated(user, app_module):
    from fastapi.testclient import TestClient
    user.put("/api/chat-state", json={"state": {"items": [{"id": "a", "msgs": [{"r": "u", "t": "secret-A"}]}], "savedAt": 1}})
    other = TestClient(app_module.app, base_url="https://testserver", headers={"cf-connecting-ip": "10.99.99.99"})
    other.post("/register", json={"email": "other-" + user.email, "password": "secret12"})
    assert "secret-A" not in other.get("/api/chat-state").text
    assert "secret-A" in user.get("/api/chat-state").text
    assert user.post("/api/chat-state", json={"session_id": "x", "history": []}).status_code == 400


def test_report_hides_email(user, client):
    rid = user.post("/api/report/create", json={"input": "ลับ", "result": {"route": "general", "risk_score": 40,
                                                                            "ai_response": "y"}}).json()["report_id"]
    rep = client.get(f"/api/report/{rid}").json()
    assert rep["user_submitted"] is True and user.email not in str(rep)


def test_simulate_without_ai(client):
    FAKE_LLM["mode"] = "fail"
    d = client.post("/simulate", json={"input": "จะเปิดร้าน", "paths": ["ลาออกเลย", "ขายออนไลน์ก่อน"]}).json()
    assert d["source"] == "kernel" and "Downside" in d["simulation"]


def test_unmetered_never_uses_ai(client, app_module, monkeypatch):
    monkeypatch.setattr(app_module, "take_free_run", None)
    d = client.post("/run", json={"input": "เงินหมด งานพัง"}).json()
    assert d["answer_source"] == "kernel" and FAKE_LLM["calls"] == 0
