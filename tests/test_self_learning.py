"""วงจรเรียนรู้ภาพรวม (ENGINE/self_learning) ต้องได้ข้อมูลจริง

เดิม: ไม่มีโค้ดไหนเรียก record_decision → ไฟล์ประวัติว่างตลอด แต่ DecisionEngine อ่านไฟล์นั้นทุกคำถาม
แล้วโยนผลทิ้ง (ไม่มีใครใช้ _learning_patterns) · และเก็บในไฟล์ JSON ที่หายทุก deploy บน Render ฟรี
ตอนนี้: /run บันทึกตัวเลข + เส้นทางลงฐานข้อมูลหลัก · เจ้าของเห็นภาพรวมในการ์ดตัวเลขธุรกิจ
"""
import uuid

import pytest

from ENGINE import self_learning as SL


@pytest.fixture
def fresh():
    c = SL._conn()
    c.execute("DELETE FROM learning_samples")
    c.commit()
    c.close()


def test_record_and_analyze(fresh):
    assert SL.analyze_patterns()["status"] == "insufficient_data"
    for r in (10, 20, 90, 30):
        assert SL.record_decision({"route": "general", "risk_score": r})
    a = SL.analyze_patterns()
    assert a["status"] == "active" and a["records"] == 4
    assert a["high_risk_ratio"] == 0.25 and a["avg_waterline"] is None


def test_backend_defaults_are_not_averaged_as_real_state(fresh):
    pat = {"waterline": 55, "entropy": 40, "resource": 50}
    for _ in range(3):
        SL.record_decision({"route": "general", "risk_score": 0, "pattern": pat}, has_state=False)
    SL.record_decision({"route": "risk", "risk_score": 40, "pattern": {"waterline": 20, "entropy": 80}}, has_state=True)
    a = SL.analyze_patterns()
    assert a["with_state"] == 1 and a["avg_waterline"] == 20


def test_only_numbers_and_route_are_stored(fresh):
    c = SL._conn()
    cols = [r[1] for r in c.execute("PRAGMA table_info(learning_samples)")]
    c.close()
    assert cols == ["id", "ts", "route", "risk_level", "risk", "waterline", "entropy", "resource"]


def test_run_feeds_the_loop(client, app_module, monkeypatch, fresh):
    monkeypatch.setenv("KD_AI", "off")
    monkeypatch.setattr(SL, "record_async", lambda r, s=False: SL.record_decision(r, s))
    before = len(SL.load_history())
    d = client.post("/run", json={"input": "ตำรวจโทรมาบอกให้โอนเงินไปบัญชีปลอดภัย"}).json()
    h = SL.load_history()
    assert len(h) == before + 1 and h[-1]["risk"] == float(d["risk_score"]) > 0


def test_owner_card_gets_the_overview(client, app_module, monkeypatch, fresh):
    email = f"owner-{uuid.uuid4().hex[:8]}@test.co"
    monkeypatch.setattr(app_module, "_ADMIN_EMAILS", {email})
    client.post("/register", json={"email": email, "password": "secret12"})
    for r in (10, 20, 30):
        SL.record_decision({"route": "general", "risk_score": r})
    L = client.get("/api/admin/metrics?days=1").json()["learning"]
    assert L["status"] == "active" and L["records"] == 3


def test_decision_engine_no_longer_reads_it_for_nothing():
    import pathlib
    src = (pathlib.Path(__file__).resolve().parent.parent / "ENGINE" / "decision_engine.py").read_text(encoding="utf-8")
    assert "analyze_patterns()" not in src
