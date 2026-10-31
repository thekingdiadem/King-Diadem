"""ฐานข้อมูลบนคลาวด์ (Turso) — Render แพ็กเกจฟรีไม่มีดิสก์ถาวร ไฟล์ SQLite หายทุก deploy/ทุกครั้งที่เซิร์ฟเวอร์หลับ

รอบแรกใช้ไลบรารี libsql (Rust/C) → บนเว็บจริงเซิร์ฟเวอร์ตาย segfault (exit 139) เป็นพักๆ
ตอนนี้ต่อด้วย Python ล้วนผ่าน HTTPS (DATABASE/turso.py · โปรโตคอล Hrana v2) — ทำโปรเซสตายแบบนั้นไม่ได้
เทสต์คุยกับเซิร์ฟเวอร์ Turso จำลอง (tests/_fake_hrana.py) และ CI รันเทสต์ทั้งชุดซ้ำผ่านตัวนี้ (KD_DB_DRIVER=hrana-fake)"""
import pathlib
import sqlite3

import httpx
import pytest

from DATABASE import turso


@pytest.fixture
def cloud(tmp_path, monkeypatch):
    from DATABASE import db
    from tests import _fake_hrana
    old = turso._client
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "cloud.db"))
    _fake_hrana.install()
    yield lambda: turso.Connection("libsql://king-diadem-x.turso.io", "tok")
    turso.set_client(old)


def test_rows_read_like_sqlite(cloud):
    c = cloud()
    c.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, n REAL, b BLOB)")
    cur = c.execute("INSERT INTO users (email, n, b) VALUES (?, ?, ?)", ("row@test.co", 1.5, b"\x00\x01"))
    assert cur.rowcount == 1 and cur.lastrowid == 1
    r = c.execute("SELECT email, id, n, b FROM users WHERE email = ?", ("row@test.co",)).fetchone()
    assert r["email"] == "row@test.co" and r[0] == "row@test.co" and r["EMAIL"] == "row@test.co"
    assert r["n"] == 1.5 and r["b"] == b"\x00\x01" and r["id"] == 1
    assert dict(r) == {"email": "row@test.co", "id": 1, "n": 1.5, "b": b"\x00\x01"}
    assert [x["email"] for x in c.execute("SELECT email FROM users")] == ["row@test.co"]
    assert c.execute("SELECT email FROM users WHERE id = 99").fetchone() is None


def test_unique_violation_is_a_sqlite_integrity_error(cloud):
    c = cloud()
    c.execute("CREATE TABLE t (k TEXT PRIMARY KEY)")
    c.execute("INSERT INTO t VALUES ('a')")
    with pytest.raises(sqlite3.IntegrityError):
        c.execute("INSERT INTO t VALUES ('a')")


def test_transactions_hold_until_commit_and_roll_back(cloud):
    a, b = cloud(), cloud()
    a.execute("CREATE TABLE m (v INTEGER)")
    a.execute("BEGIN IMMEDIATE")
    a.execute("INSERT INTO m VALUES (1)")
    assert b.execute("SELECT COUNT(*) AS n FROM m").fetchone()["n"] == 0      # ยังไม่ commit คนอื่นไม่เห็น
    a.commit()
    assert b.execute("SELECT COUNT(*) AS n FROM m").fetchone()["n"] == 1
    a.execute("BEGIN IMMEDIATE")
    a.execute("INSERT INTO m VALUES (2)")
    a.close()                                                                  # ปิดกลางทาง = ยกเลิก
    assert b.execute("SELECT COUNT(*) AS n FROM m").fetchone()["n"] == 1


def test_setting_pragmas_are_skipped_but_reading_ones_work(cloud):
    c = cloud()
    with pytest.raises(sqlite3.DatabaseError):                 # init_db / get_conn เดิมจับ DatabaseError อยู่แล้ว
        c.execute("PRAGMA journal_mode = WAL")
    c.execute("CREATE TABLE p (x)")
    assert [r[1] for r in c.execute("PRAGMA table_info(p)")] == ["x"]


def test_network_trouble_is_an_error_not_a_crash(monkeypatch):
    def boom(req):
        raise httpx.ConnectError("down")
    old = turso._client
    turso.set_client(httpx.Client(transport=httpx.MockTransport(boom)))
    try:
        with pytest.raises(sqlite3.OperationalError):
            turso.Connection("libsql://x.turso.io", "t").execute("SELECT 1")
    finally:
        turso.set_client(old)


def test_url_and_auth_are_sent_right(monkeypatch):
    seen = {}

    def grab(req):
        seen["url"], seen["auth"] = str(req.url), req.headers.get("authorization")
        return httpx.Response(200, json={"baton": None, "results": [
            {"type": "ok", "response": {"type": "execute", "result": {"cols": [], "rows": [], "affected_row_count": 0}}},
            {"type": "ok", "response": {"type": "close"}}]})
    old = turso._client
    turso.set_client(httpx.Client(transport=httpx.MockTransport(grab)))
    try:
        turso.Connection("libsql://king-diadem-x.aws-us-west-2.turso.io", "secret").execute("SELECT 1")
    finally:
        turso.set_client(old)
    assert seen == {"url": "https://king-diadem-x.aws-us-west-2.turso.io/v2/pipeline", "auth": "Bearer secret"}


def test_no_native_database_library_left():
    """libsql ทำให้เซิร์ฟเวอร์ segfault — ห้ามกลับมาใช้ตัวที่มีโค้ด native อีก"""
    root = pathlib.Path(__file__).resolve().parent.parent
    assert "libsql" not in (root / "requirements.txt").read_text(encoding="utf-8")
    assert "import libsql" not in (root / "DATABASE" / "db.py").read_text(encoding="utf-8")


def test_health_says_where_the_data_lives(client):
    assert client.get("/health").json()["db_cloud"] is False
