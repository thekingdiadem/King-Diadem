"""รายงานแชร์ได้: สร้างเมื่อผู้ใช้กดแชร์เท่านั้น · หมดอายุ · เจ้าของลบได้

เดิมทุกครั้งที่ถาม /run สร้างลิงก์ /report/<id> ที่ใครมีลิงก์ก็อ่านได้ ไม่มีวันหมดอายุ และลบไม่ได้
คนที่เล่าเรื่องส่วนตัว (หนี้ ความสัมพันธ์ อยากทำร้ายตัวเอง) จึงมีข้อความค้างอยู่ในลิงก์สาธารณะโดยไม่รู้ตัว
"""
import sqlite3

from fastapi.testclient import TestClient
from tests._front import front_page  # noqa: E402


def _count(app_module):
    import report_engine
    report_engine.init_report_table()
    conn = report_engine.get_conn()
    try:
        return conn.execute("SELECT COUNT(*) FROM decision_reports").fetchone()[0]
    finally:
        conn.close()


def test_run_does_not_create_a_public_report(client, app_module):
    before = _count(app_module)
    d = client.post("/run", json={"input": "เป็นหนี้สองแสน ไม่รู้จะทำยังไงดี"}).json()
    assert "report_id" not in d and "share_url" not in d
    assert d.get("share_token")
    assert _count(app_module) == before


def test_share_creates_report_once_from_the_real_answer(client, app_module):
    d = client.post("/run", json={"input": "ควรลาออกไหม"}).json()
    r1 = client.post("/api/report/share", json={"token": d["share_token"]})
    assert r1.status_code == 200
    rid = r1.json()["report_id"]
    rep = client.get(f"/api/report/{rid}").json()
    assert rep["input_text"] == "ควรลาออกไหม" and rep["ai_response"] == d["ai_response"]
    assert rep["user_submitted"] is False
    assert client.post("/api/report/share", json={"token": d["share_token"]}).json()["report_id"] == rid   # กดซ้ำได้ลิงก์เดิม


def test_unknown_or_expired_token_is_refused(client, app_module, monkeypatch):
    assert client.post("/api/report/share", json={"token": "nope"}).status_code == 410
    d = client.post("/run", json={"input": "ทดสอบหมดเวลา"}).json()
    app_module._share_cache[d["share_token"]]["t"] -= app_module._SHARE_TTL + 1
    assert client.post("/api/report/share", json={"token": d["share_token"]}).status_code == 410


def test_another_account_cannot_share_my_answer(user, app_module):
    d = user.post("/run", json={"input": "เรื่องส่วนตัวของฉัน"}).json()
    other = TestClient(app_module.app, base_url="https://testserver", headers={"cf-connecting-ip": "10.251.0.9"})
    other.post("/register", json={"email": "other-share@test.co", "password": "secret12"})
    assert other.post("/api/report/share", json={"token": d["share_token"]}).status_code == 403


def test_owner_can_delete_and_others_cannot(user, app_module):
    d = user.post("/run", json={"input": "ลบได้ไหม"}).json()
    rid = user.post("/api/report/share", json={"token": d["share_token"]}).json()["report_id"]
    anon = TestClient(app_module.app, base_url="https://testserver", headers={"cf-connecting-ip": "10.251.0.10"})
    assert anon.delete(f"/api/report/{rid}").status_code == 401
    assert user.delete(f"/api/report/{rid}").status_code == 200
    assert user.get(f"/api/report/{rid}").status_code == 404


def test_reports_expire(client, app_module):
    import report_engine
    d = client.post("/run", json={"input": "รายงานหมดอายุ"}).json()
    rid = client.post("/api/report/share", json={"token": d["share_token"]}).json()["report_id"]
    conn = report_engine.get_conn()
    try:
        exp = conn.execute("SELECT julianday(expires_at) - julianday(created_at) FROM decision_reports WHERE id=?", (rid,)).fetchone()[0]
        assert round(exp) == report_engine.REPORT_TTL_DAYS
        conn.execute("UPDATE decision_reports SET expires_at = datetime('now', '-1 minute') WHERE id=?", (rid,))
        conn.commit()
    finally:
        conn.close()
    assert client.get(f"/api/report/{rid}").status_code == 404


def test_old_reports_without_expiry_get_one(tmp_path, monkeypatch):
    """รายงานเก่าที่สร้างอัตโนมัติ (ไม่มีวันหมดอายุ) ได้อายุนับจากวันสร้าง · ที่เก่าเกินถูกลบตอนเริ่มระบบ"""
    import report_engine
    db = tmp_path / "old.db"
    monkeypatch.setattr(report_engine, "get_conn", lambda: _conn(db))
    monkeypatch.setattr(report_engine, "_TABLE_READY", False)
    c = _conn(db)
    c.executescript("""CREATE TABLE decision_reports (id TEXT PRIMARY KEY, user_email TEXT, input_text TEXT, route TEXT,
        persona TEXT, ai_response TEXT, governance TEXT, risk_score REAL, consensus TEXT, fate_audit TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP, expires_at DATETIME);
        INSERT INTO decision_reports (id, created_at) VALUES ('old', datetime('now', '-400 days')), ('new', datetime('now', '-1 day'));""")
    c.commit(); c.close()
    report_engine.init_report_table()
    c = _conn(db)
    ids = [r[0] for r in c.execute("SELECT id FROM decision_reports WHERE expires_at IS NOT NULL")]
    c.close()
    assert ids == ["new"]


def _conn(path):
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    return c


def test_chat_ui_has_share_button_not_auto_link():
    from pathlib import Path
    html = front_page()
    assert "share: d.share_token || ''" in html and 'data-act="share"' in html
    assert "fetch('/api/report/share'" in html
