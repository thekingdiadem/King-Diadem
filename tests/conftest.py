"""
ตั้งค่าก่อน import แอป: ฐานข้อมูล/ไฟล์ข้อมูลอยู่ในโฟลเดอร์ชั่วคราว, Gemini เป็นตัวปลอม (ไม่ใช้เน็ต ไม่เสียเงิน)

FAKE_LLM ปรับพฤติกรรมของ Gemini ปลอมได้ในแต่ละเทสต์:
    mode = "ok"    → ตอบข้อความสั้นๆ
    mode = "fail"  → ทำเหมือนโควตาหมด (ระบบต้องตอบจากสมการแทน)
    calls / systems → นับจำนวนครั้งที่เรียก และ system prompt ที่ใช้
    text = "..."    → ให้ Gemini ปลอมตอบข้อความนี้ (เช่น ทดสอบ canon gate)
"""
import os
import sys
import tempfile
import uuid

_TMP = tempfile.mkdtemp(prefix="kd-tests-")
os.environ.update({
    "SECRET_KEY": "test-secret",
    "DB_PATH": os.path.join(_TMP, "kd.db"),
    "KD_DATA_DIR": _TMP,
    "GEMINI_API_KEY": "fake",
    "FREE_DAILY_RUNS": "3",
    "TRUST_CF_HEADER": "1",          # แยกผู้ใช้ไม่ล็อกอินด้วย cf-connecting-ip ในเทสต์
    "STRIPE_WEBHOOK_SECRET": "whsec_test",
    "STRIPE_PRICE_ID": "price_basic",
    "STRIPE_PREMIUM_PRICE_ID": "price_prem",
})
os.environ.pop("KD_AI", None)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402
import core.llm_gemini as L  # noqa: E402

FAKE_LLM = {"mode": "ok", "calls": 0, "systems": [], "text": None}


def _fake_call(self, system, contents, temperature=0.72, max_tokens=1024):
    if L.ai_disabled() or FAKE_LLM["mode"] == "fail":
        L._tls.fallback = True
        return self._fallback_response(system, "")
    FAKE_LLM["calls"] += 1
    FAKE_LLM["systems"].append(system)
    return FAKE_LLM["text"] or "เข้าใจค่ะ มี 2 ทาง 1) พักก่อน 2) เขียนสิ่งที่กังวล\n— LYLA ◈"


L.GeminiLLM._call = _fake_call
L.GeminiLLM._init_client = lambda self: None

import app as _app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_fake_llm():
    FAKE_LLM.update(mode="ok", calls=0, systems=[], text=None)
    yield


@pytest.fixture
def app_module():
    return _app


@pytest.fixture
def client():
    """ผู้ใช้ใหม่ทุกเทสต์ (IP ไม่ซ้ำ) — โควตา/rate limit/สถานะอารมณ์ไม่ปนกัน"""
    ip = "10.%d.%d.%d" % tuple(uuid.uuid4().bytes[:3])
    return TestClient(_app.app, base_url="https://testserver", headers={"cf-connecting-ip": ip})


@pytest.fixture
def user(client):
    """ผู้ใช้ที่ล็อกอินแล้ว (อีเมลไม่ซ้ำ)"""
    email = f"u{uuid.uuid4().hex[:10]}@test.co"
    r = client.post("/register", json={"email": email, "password": "secret12"})
    assert r.status_code == 200
    client.email = email
    return client
