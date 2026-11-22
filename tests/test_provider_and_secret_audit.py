"""ต่อ AI เฉพาะปลายทางทางการ + บันทึกหลักฐานทุกครั้งที่ซ่อนข้อมูลลับ (ข่าว พ.ย. 2569 · HD Moore/Dragos:
ตัวกลาง AI เก็บ/รั่ว prompt · กุญแจปลอมถูกใช้ภายในไม่กี่ชั่วโมง)"""
import json
import uuid

import pytest

from core import llm_gemini, secret_audit
from core.llm_provider_policy import check_url


@pytest.mark.parametrize("url,ok", [
    ("https://api.openai.com/v1", True), ("https://api.deepseek.com", True),
    ("https://dashscope-intl.aliyuncs.com/compatible-mode/v1", True), ("http://localhost:11434/v1", True),
    ("http://10.0.0.5:8000/v1", True),
    ("https://openrouter.ai/api/v1", False), ("https://evil-proxy.example.com/v1", False),
    ("http://api.openai.com/v1", False), ("", False), ("ftp://api.openai.com", False),
])
def test_only_official_or_self_hosted_endpoints(url, ok, monkeypatch):
    monkeypatch.delenv("KD_ALLOW_UNVERIFIED_LLM", raising=False)
    assert check_url(url)["ok"] is ok


def test_owner_can_opt_in_but_it_is_marked_unverified(monkeypatch):
    monkeypatch.setenv("KD_ALLOW_UNVERIFIED_LLM", "1")
    r = check_url("https://openrouter.ai/api/v1")
    assert r["ok"] and r["verified"] is False and "ตัวกลาง" in r["reason"]


def test_router_provider_is_refused_and_falls_back(monkeypatch):
    from core.llm_openai_compat import OpenAICompatLLM
    monkeypatch.delenv("KD_ALLOW_UNVERIFIED_LLM", raising=False)
    monkeypatch.setenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
    monkeypatch.setenv("LLM_API_KEY", "x")
    monkeypatch.setenv("LLM_MODEL", "m")
    monkeypatch.delenv("KD_AI", raising=False)
    with pytest.raises(ValueError, match="ไม่ผ่านนโยบาย"):
        OpenAICompatLLM()
    # get_llm สลับไป Gemini ทางการ (หรือยกต่อถ้าไม่มี key Gemini → ระบบตอบจากสมการ)
    monkeypatch.setenv("LLM_PROVIDER", "openai_compat")
    made = []
    monkeypatch.setattr(llm_gemini, "GeminiLLM", type("G", (), {"__init__": lambda self, model="": made.append(1)}))
    monkeypatch.setattr(llm_gemini, "_instances", {})
    monkeypatch.setattr(llm_gemini, "_instance", None)
    llm_gemini.get_llm("fallback-test-model")
    assert made == [1]


def test_gemini_endpoint_is_pinned_to_google():
    src = open("core/llm_gemini.py", encoding="utf-8").read()
    assert "http_options=types.HttpOptions(base_url=GEMINI_OFFICIAL)" in src


def test_every_path_to_the_ai_is_scrubbed_including_generate():
    """generate() (สภา 6 เสียง · DecisionEngine) สร้างข้อความเอง — เดิมไม่ผ่านตัวซ่อน"""
    m = llm_gemini._msg("user", "บัญชี 1234567890123 OTP: 556677 me@x.co")
    text = m.parts[0].text
    for secret in ("1234567890123", "556677", "me@x.co"):
        assert secret not in text


def test_audit_records_kinds_and_counts_never_the_values():
    secret_audit.flush()
    before = secret_audit.report(1)["messages_with_secrets"]
    tag = uuid.uuid4().hex[:6]
    llm_gemini._msg("user", f"โอนเข้า 123-4-56789-0 กับ 9876543210987 ส่ง OTP: 4821{tag[:2]} ไป boss{tag}@gmail.com")
    secret_audit.flush()
    rep = secret_audit.report(1)
    assert rep["messages_with_secrets"] == before + 1
    assert rep["masked"]["long_number"] >= 2 and rep["masked"]["password"] >= 1 and rep["masked"]["email"] >= 1
    assert rep["chain"]["ok"]
    blob = json.dumps(rep, ensure_ascii=False) + secret_audit.export_csv(1)
    for secret in ("56789", "9876543210987", f"boss{tag}"):
        assert secret not in blob


def test_tampering_breaks_the_chain():
    llm_gemini._msg("user", "เลข 5555666677778888")
    secret_audit.flush()
    from DATABASE.db import get_conn
    conn = get_conn()
    try:
        rid = conn.execute("SELECT id FROM secret_audit ORDER BY id DESC LIMIT 1").fetchone()[0]
        conn.execute("UPDATE secret_audit SET kinds = ? WHERE id = ?", ('{"email": 0}', rid))
        conn.commit()
        v = secret_audit.verify()
        assert v["ok"] is False and v["broken_at"] == rid
        conn.execute("DELETE FROM secret_audit WHERE id >= ?", (rid,))      # คืนสภาพให้เทสต์อื่น
        conn.commit()
    finally:
        conn.close()


def test_admin_report_endpoints(client, app_module, monkeypatch):
    from tests.conftest import verify_email
    email = f"owner-{uuid.uuid4().hex[:8]}@test.co"
    monkeypatch.setattr(app_module, "_ADMIN_EMAILS", {email})
    assert client.get("/api/admin/secret-audit").status_code == 404
    verify_email(email)
    client.post("/register", json={"email": email, "password": "secret12"})
    j = client.get("/api/admin/secret-audit?days=7").json()
    assert j["provider"]["verified"] is True and "never_stored" in j
    csv = client.get("/api/admin/secret-audit.csv")
    assert csv.status_code == 200 and csv.text.startswith("﻿id,time_utc,provider")
