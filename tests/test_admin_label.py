"""โต๊ะติดป้ายข้อความจริง (/admin/label) — ประโยคที่ผู้ใช้แนบมากับปุ่มธง → ผู้ดูแลติดป้าย → บรรทัดของชุดปิดตา

ทำไม: ชุดปิดตา 3,700 กว่าข้อเขียนโดยคนเดียวกับที่เขียนตัวตรวจจับ — ตัวเลขความแม่นดีเกินจริง
ข้อความจากผู้ใช้จริงคือสิ่งที่ขาดที่สุด (ROADMAP ข้อ 1) · เดิมต้องเปิด JSON แล้วคัดลอกเองทีละข้อ
"""
import re
import uuid

import pytest

from core import answer_reports


@pytest.fixture
def owner(client, app_module, monkeypatch):
    email = f"owner-{uuid.uuid4().hex[:8]}@test.co"
    monkeypatch.setattr(app_module, "_ADMIN_EMAILS", {email})
    from tests.conftest import verify_email; verify_email(email)
    client.post("/register", json={"email": email, "password": "secret12"})
    return client


def _report(client, question, reason="missed"):
    r = client.post("/api/report-answer", json={"reason": reason, "answer": "คำตอบ", "question": question, "include_question": True})
    assert r.status_code == 200, r.text


def _find(owner, text):
    items = owner.get("/api/admin/label-queue?limit=200").json()["items"]
    return next(i for i in items if i["question"] == text)


def test_only_admin_sees_any_of_it(client, user):
    for path in ("/admin/label", "/api/admin/label-queue", "/api/admin/label-export"):
        assert client.get(path).status_code == 404, path
    assert client.post("/api/admin/label", json={"id": 1, "label": "none"}).status_code == 404


def test_queue_shows_what_the_system_sees_now_and_days_left(owner):
    q = f"แม่หายใจไม่ออก {uuid.uuid4().hex[:6]}"
    _report(owner, q)
    it = _find(owner, q)
    assert "emergency" in it["now"]["detected"] and it["now"]["risk"] >= 75
    assert 85 <= it["days_left"] <= 90


def test_label_then_export_as_blind_line(owner):
    q = f"ลูกกินถ่านกระดุมเข้าไป {uuid.uuid4().hex[:6]}"
    _report(owner, q)
    it = _find(owner, q)
    assert owner.post("/api/admin/label", json={"id": it["id"], "label": "emergency"}).json()["ok"]
    items = owner.get("/api/admin/label-queue?limit=200").json()["items"]
    assert all(i["question"] != q for i in items)                       # ติดแล้วไม่อยู่ในคิว
    out = owner.get("/api/admin/label-export")
    assert out.status_code == 200 and "attachment" in out.headers["content-disposition"]
    assert f"{q}\temergency\tth\treal-user" in out.text.splitlines()


def test_skip_is_not_exported_and_bad_label_rejected(owner):
    q = f"asdf {uuid.uuid4().hex[:6]}"
    _report(owner, q)
    it = _find(owner, q)
    assert owner.post("/api/admin/label", json={"id": it["id"], "label": "lol"}).status_code == 400
    assert owner.post("/api/admin/label", json={"id": "x", "label": "none"}).status_code == 400
    assert owner.post("/api/admin/label", json={"id": it["id"], "label": "skip"}).json()["ok"]
    assert q not in owner.get("/api/admin/label-export").text


def test_reports_without_a_question_never_reach_the_queue(owner):
    owner.post("/api/report-answer", json={"reason": "harmful", "answer": "x", "question": "ไม่ได้ติ๊กแนบ"})
    items = owner.get("/api/admin/label-queue?limit=200").json()["items"]
    assert all(i["question"] != "ไม่ได้ติ๊กแนบ" for i in items)


def test_export_line_is_one_line_and_deduplicated():
    assert answer_reports.guess_lang("mẹ tôi") == "vi" and answer_reports.guess_lang("hello") == "en"
    assert answer_reports.guess_lang("我被骗了") == "zh" and answer_reports.guess_lang("詐欺にあった") == "ja"


def test_scoreboard_reports_real_users_separately():
    import json
    s = json.load(open("static/blind_score.json", encoding="utf-8"))
    assert set(s["real_user"]) == {"n", "danger_missed", "false_alarm", "right_category"}
    page = open("static/architecture.html", encoding="utf-8").read()
    assert "s.real_user" in page


def test_label_page_is_csp_safe_and_has_every_label():
    html = open("static/admin_label.html", encoding="utf-8").read()
    assert not re.search(r"<[^>]+\son[a-z]+=", html)
    assert 'name="robots" content="noindex' in html
    for l in answer_reports.LABELS:
        assert f"{l}:" in html or f"'{l}'" in html, l
