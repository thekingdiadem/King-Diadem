"""คำขอที่ผู้ใช้ส่งเข้ามา: ขนาด body, ความยาวประวัติแชต, ตัวเลขที่ไม่จำกัด, security headers, เอกสาร API

พบจากการตรวจความปลอดภัย — เซิร์ฟเวอร์มี worker เดียว: JSON ก้อนเดียว ~20MB ทำหน่วยความจำพุ่ง ~700MB จนล่มทั้งระบบ
"""
import json

import pytest


def test_oversized_json_is_rejected_before_parsing(client):
    big = '{"route":"x","a":[' + ",".join(["{}"] * 200000) + "]}"   # ~600KB
    r = client.post("/api/galaxy/signal", content=big, headers={"content-type": "application/json"})
    assert r.status_code == 413


def test_oversized_chunked_body_is_cut_off(client):
    """ไม่มี Content-Length (ส่งเป็น chunk) ก็ต้องนับไบต์จริงแล้วตัด"""
    def gen():
        yield b'{"route":"x","a":['
        for _ in range(100):
            yield b"{}," * 2000
        yield b"{}]}"
    r = client.post("/api/galaxy/signal", content=gen(), headers={"content-type": "application/json"})
    assert r.status_code == 413


def test_normal_requests_still_work(client):
    assert client.post("/api/galaxy/signal", json={"route": "risk"}).status_code == 200
    assert client.post("/run", json={"input": "สวัสดีค่ะ"}).status_code == 200


def test_image_route_allows_up_to_its_own_cap(app_module):
    assert app_module._body_limit("/analyze-image") == 11 * 1024 * 1024
    assert app_module._body_limit("/run") == 256 * 1024


def test_history_is_trimmed_before_reaching_the_llm(app_module):
    """เดิมประวัติแชตจาก client ไม่ถูกตัด — ข้อความ "hi" พ่วงประวัติหลาย MB ไปเผาโควตา Gemini ได้"""
    hist = [{"role": "user", "content": "ก" * 30000}] * 3 + [{"role": "hacker", "content": "x"}] + ["junk"] * 20
    out = app_module._clean_history(hist)
    assert len(out) <= 8
    assert all(len(t["content"]) <= 2000 for t in out)
    assert {t["role"] for t in out} <= {"user", "assistant"}
    assert app_module._clean_history("not a list") == []


def test_llm_contents_cap_each_turn():
    import core.llm_gemini as L
    if L.types is None:
        pytest.skip("google-genai not installed")
    contents = L._build_contents([{"role": "user", "content": "ข" * 9000}], "hi")
    assert len(contents[0].parts[0].text) == 2000


def test_infinite_numbers_do_not_break_a_report(client):
    """เดิม risk_score / governance เป็น 1e309 แล้วรายงานนั้นเปิดไม่ได้ถาวร (500)"""
    raw = '{"input":"x","result":{"route":"risk","risk_score":1e309,"governance":{"w":1e309,"l":[1e309]},"ai_response":"ok"}}'
    r = client.post("/api/report/create", content=raw, headers={"content-type": "application/json"})
    assert r.status_code == 200
    rid = r.json()["report_id"]
    g = client.get(f"/api/report/{rid}")
    assert g.status_code == 200
    assert g.json()["risk_score"] == 0 and g.json()["governance"] == {"w": None, "l": [None]}


def test_security_headers_and_noindex_reports(client):
    h = client.get("/").headers
    assert h["x-content-type-options"] == "nosniff"
    assert h["x-frame-options"] == "DENY"
    assert h["referrer-policy"] == "strict-origin-when-cross-origin"
    r = client.get("/report/abc123")
    assert r.headers.get("x-robots-tag") == "noindex, nofollow"
    assert '<meta name="robots" content="noindex, nofollow">' in r.text


@pytest.mark.parametrize("path", ["/docs", "/redoc", "/openapi.json"])
def test_api_docs_are_not_public(client, path):
    assert client.get(path).status_code == 404
