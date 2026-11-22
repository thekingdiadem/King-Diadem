"""โต๊ะแพทย์ตรวจข้อความทางการแพทย์ (/admin/medical · core/medical_review) — ROADMAP ข้อ 2

ข้อความสุขภาพทั้งหมด (แผนดูแลไต ค่าเลือด ยาตีกัน) เขียนโดยผู้ช่วยเขียนโค้ด ยังไม่มีแพทย์ตรวจ
หัวใจของระบบ: แพทย์อนุมัติ "เนื้อความนี้" — แก้ข้อความทีหลัง สถานะต้องกลับเป็นรอตรวจใหม่เอง
"""
import re
import uuid

import pytest

from core import medical_review as mr
from tests.conftest import verify_email


def _mail(tag):
    return f"{tag}-{uuid.uuid4().hex[:8]}@test.co"


@pytest.fixture
def doctor(client, app_module, monkeypatch):
    email = _mail("doctor")
    monkeypatch.setattr(app_module, "_REVIEWER_EMAILS", {email})
    verify_email(email)
    client.post("/register", json={"email": email, "password": "secret12"})
    return client


def test_every_medical_source_is_collected_with_unique_ids():
    items = mr.items()
    ids = [i["id"] for i in items]
    assert len(ids) == len(set(ids))
    by = {s: [i for i in items if i["source"] == s] for s in mr.SOURCES}
    assert len(by["chronic"]) >= 200 and len(by["lab"]) >= 40 and len(by["drug"]) >= 30
    assert any("มะเฟือง" in i["text"] for i in by["chronic"])             # ดึงจากโค้ดจริง ไม่ใช่สำเนา
    assert all(i["text"].strip() and len(i["hash"]) == 16 for i in items)
    assert not any(i["text"] in ("ปกติ", "normal") for i in by["lab"])   # "ปกติ" ไม่ใช่คำแนะนำ


def test_changed_text_goes_back_to_needing_review(monkeypatch):
    it = next(i for i in mr.items() if i["id"] == "chronic:star_fruit:th")
    assert mr.review(it["id"], "approved", "", "doc@x.co")["ok"]
    assert next(x for x in mr.listing() if x["id"] == it["id"])["status"] == "approved"
    from core import chronic_care
    monkeypatch.setitem(chronic_care.T["star_fruit"], "th", it["text"] + " (แก้ไขแล้ว)")
    assert next(x for x in mr.listing() if x["id"] == it["id"])["status"] == "changed"


def test_needs_fix_requires_a_note_and_bad_input_is_refused():
    assert not mr.review("chronic:salt:th", "needs_fix", "", "doc@x.co")["ok"]
    assert mr.review("chronic:salt:th", "needs_fix", "ควรระบุว่าเกลือ 5 กรัม = โซเดียม 2,000 มก.", "doc@x.co")["ok"]
    assert not mr.review("chronic:salt:th", "maybe", "", "doc@x.co")["ok"]
    assert not mr.review("nope:nope:th", "approved", "", "doc@x.co")["ok"]


def test_doctor_can_review_and_export_but_sees_no_admin_data(doctor):
    j = doctor.get("/api/admin/medical").json()
    assert j["summary"]["total"] == len(j["items"]) >= 300
    assert not any(i["topic"] in ("title", "lang_fallback") for i in j["items"])
    target = next(i for i in j["items"] if i["id"] == "chronic:nsaid:en")
    r = doctor.post("/api/admin/medical", json={"id": target["id"], "verdict": "approved"})
    assert r.status_code == 200 and r.json()["ok"]
    row = next(i for i in doctor.get("/api/admin/medical").json()["items"] if i["id"] == target["id"])
    assert row["status"] == "approved" and "•••" in row["reviewer"]
    csv = doctor.get("/api/admin/medical-export")
    assert csv.status_code == 200 and "attachment" in csv.headers["content-disposition"]
    assert csv.text.startswith("﻿id,source,topic,lang,status")
    for path in ("/api/admin/metrics", "/api/admin/reports", "/api/admin/security", "/admin/label"):
        assert doctor.get(path).status_code == 404, path


def test_unverified_or_ordinary_users_get_nothing(client, app_module, monkeypatch):
    email = _mail("doctor")
    monkeypatch.setattr(app_module, "_REVIEWER_EMAILS", {email})
    client.post("/register", json={"email": email, "password": "secret12"})   # ไม่ได้พิสูจน์อีเมล
    for path in ("/admin/medical", "/api/admin/medical", "/api/admin/medical-export"):
        assert client.get(path).status_code == 404, path
    assert client.post("/api/admin/medical", json={"id": "chronic:salt:th", "verdict": "approved"}).status_code == 404


def test_public_summary_has_numbers_only(client):
    j = client.get("/api/medical-review").json()
    assert set(j) == {"total", "approved", "by_source"} and j["total"] >= 300
    assert "chronic" in j["by_source"]


def test_kidney_page_tells_the_truth_about_review():
    html = open("static/kidney.html", encoding="utf-8").read()
    assert 'id="review"' in html and "/api/medical-review" in html and "ยังไม่ผ่านการตรวจจากแพทย์" in html


def test_review_page_is_csp_safe_and_not_indexed():
    html = open("static/admin_medical.html", encoding="utf-8").read()
    assert not re.search(r"<[^>]+\son[a-z]+=", html)
    assert 'name="robots" content="noindex' in html
