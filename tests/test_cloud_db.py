"""ฐานข้อมูลบนคลาวด์ (Turso) — Render แพ็กเกจฟรีไม่มีดิสก์ถาวร ไฟล์ SQLite หายทุก deploy/ทุกครั้งที่เซิร์ฟเวอร์หลับ
(บัญชี เครดิตที่จ่ายเงินซื้อ 2FA หายหมด) · ตั้ง TURSO_URL + TURSO_TOKEN แล้วข้อมูลไปอยู่ที่ Turso

เทสต์ใช้ไดรเวอร์ libsql ตัวเดียวกับบนเว็บจริงกับไฟล์ในเครื่อง (ต่อ Turso จริงในเทสต์ไม่ได้)
และ CI รันเทสต์ทั้งชุดซ้ำผ่าน libsql อีกรอบ (KD_DB_DRIVER=libsql)"""
import sqlite3

import pytest

from DATABASE import db


@pytest.fixture
def lib(tmp_path, monkeypatch):
    pytest.importorskip("libsql")
    monkeypatch.setenv("KD_DB_DRIVER", "libsql")
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "cloud.db"))
    db.init_db()
    return db


def test_rows_read_like_sqlite(lib):
    lib.ensure_user("row@test.co")
    c = lib.get_conn()
    r = c.execute("SELECT email, id FROM users WHERE email = ?", ("row@test.co",)).fetchone()
    assert r["email"] == "row@test.co" and r[0] == "row@test.co" and r["EMAIL"] == "row@test.co"
    assert dict(r) == {"email": "row@test.co", "id": r["id"]} and r.keys() == ["email", "id"]
    assert [x["email"] for x in c.execute("SELECT email FROM users")] == ["row@test.co"]
    c.close()


def test_money_and_security_paths_work_on_libsql(lib):
    lib.ensure_user("pay@test.co")
    start = lib.get_credits("pay@test.co")
    lib.add_credits_once("pay@test.co", 50, "topup", "cs_1")
    lib.add_credits_once("pay@test.co", 50, "topup", "cs_1")               # Stripe ส่ง webhook ซ้ำ
    assert lib.get_credits("pay@test.co") == start + 50                     # เติมครั้งเดียว
    assert lib.spend_credit("pay@test.co", 1, "run")
    assert lib.metric_once("2026-11-01", "visitor", "k1") is True
    assert lib.metric_once("2026-11-01", "visitor", "k1") is False


def test_unique_violation_is_a_sqlite_integrity_error(lib):
    c = lib.get_conn()
    c.execute("INSERT INTO users (email) VALUES (?)", ("dup@test.co",))
    c.commit()
    with pytest.raises(sqlite3.IntegrityError):
        c.execute("INSERT INTO users (email) VALUES (?)", ("dup@test.co",))
    c.close()


def test_cloud_mode_skips_pragmas_the_server_does_not_support(monkeypatch):
    class Raw:
        def execute(self, sql, params=()):
            raise AssertionError("PRAGMA ไม่ควรถูกส่งไปเซิร์ฟเวอร์")
    monkeypatch.setattr(db, "TURSO_URL", "libsql://example.turso.io")
    with pytest.raises(sqlite3.DatabaseError):                 # โค้ดเดิม (init_db, get_conn) จับ DatabaseError อยู่แล้ว
        db._Conn(Raw()).execute("PRAGMA journal_mode = WAL")


def test_local_file_stays_the_default():
    assert not db.TURSO_URL or db.using_cloud()
    if not db.TURSO_URL:
        import os
        if os.getenv("KD_DB_DRIVER") != "libsql":
            assert isinstance(db.get_conn(), sqlite3.Connection)


def test_health_says_where_the_data_lives(client):
    assert client.get("/health").json()["db_cloud"] is False
