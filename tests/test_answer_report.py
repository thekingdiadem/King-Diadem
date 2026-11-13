"""ปุ่มธงใต้คำตอบ → /api/report-answer (core/answer_reports.py)
ร้านแอปกำหนดให้แอปที่ใช้ AI สร้างเนื้อหามีทางให้ผู้ใช้รายงานคำตอบที่ไม่เหมาะสมได้ในแอป — เดิมมีแค่ปุ่มช่วยได้/ยังไม่ช่วย ซึ่งไม่ส่งข้อความ"""
import pytest
from fastapi.testclient import TestClient

import app as kd
from core import answer_reports
from tests._front import front_page


@pytest.fixture()
def client():
    kd._rate_bucket.clear()
    return TestClient(kd.app)


def test_report_is_stored_with_the_answer(client):
    r = client.post("/api/report-answer", json={"reason": "harmful", "answer": "คำตอบที่มีปัญหา", "note": "อ่านแล้วไม่สบายใจ", "route": "risk", "risk": 80})
    assert r.status_code == 200 and r.json()["ok"]
    row = answer_reports.recent(1)[0]
    assert row["reason"] == "harmful" and row["answer"] == "คำตอบที่มีปัญหา" and row["note"] == "อ่านแล้วไม่สบายใจ"
    assert row["route"] == "risk" and row["risk"] == 80


def test_report_keeps_nothing_about_the_person(client):
    client.post("/api/report-answer", json={"reason": "wrong", "answer": "ก", "question": "ความลับของฉัน", "email": "a@b.c"})
    row = answer_reports.recent(1)[0]
    assert set(row) == {"id", "ts", "reason", "route", "risk", "note", "answer"}
    assert "ความลับ" not in str(row) and "a@b.c" not in str(row)


@pytest.mark.parametrize("payload", [{}, {"reason": "spam", "answer": "x"}, {"reason": "wrong"}, {"reason": "wrong", "answer": "   "},
                                     {"reason": ["wrong"], "answer": "x"}, {"reason": "wrong", "answer": {"a": 1}}])
def test_bad_report_rejected(client, payload):
    assert client.post("/api/report-answer", json=payload).status_code == 400


def test_long_and_odd_input_is_trimmed():
    assert answer_reports.record("other", "ก" * 9000, "ข" * 900, "<script>", "nan")["ok"]
    row = answer_reports.recent(1)[0]
    assert len(row["answer"]) == answer_reports.MAX_ANSWER and len(row["note"]) == answer_reports.MAX_NOTE
    assert row["route"] == "general" and row["risk"] == 0


def test_only_the_owner_can_read_reports(client):
    assert client.get("/api/admin/reports").status_code == 404


def test_page_has_report_button_and_says_what_is_sent():
    page = front_page()
    assert 'id="dlg-rp"' in page and "data-rp=\"1\"" in page and "kdIcon('flag')" in page
    assert "ไม่ส่งข้อความที่คุณพิมพ์ถาม" in page                       # ผู้ใช้เห็นก่อนกดส่งว่าอะไรถูกส่งไป
    body = page[page.index("function sendReport()"):][:900]
    assert "fetch('/api/report-answer'" in body and "answer: String(m.t || '')" in body
    assert "$('#rp-send').addEventListener('click', sendReport)" in page   # CSP: ไม่ใช้ onclick
    # ปุ่มธงต้องยังกดได้หลังโหวต (แถวปุ่มถูกวาดใหม่) — ฟังที่กล่องข้อความ
    assert "e.target.closest('.fb button')" in page
