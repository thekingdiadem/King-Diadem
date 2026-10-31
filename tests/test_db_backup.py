"""สำรองฐานข้อมูลอัตโนมัติ (DATABASE/backup.py)

บัญชี เครดิต ประวัติ และ 2FA อยู่ใน SQLite ไฟล์เดียว — ไฟล์เสียเมื่อไรต้องย้อนกลับได้
"""
import os
import sqlite3
from datetime import datetime, timezone

from DATABASE import backup as B


def _db(tmp_path):
    p = tmp_path / "kd.db"
    c = sqlite3.connect(p)
    c.execute("CREATE TABLE users (email TEXT, credits INTEGER)")
    c.execute("INSERT INTO users VALUES ('a@b.com', 42)")
    c.commit()
    c.close()
    return str(p)


def test_backup_is_a_complete_readable_copy(tmp_path):
    db = _db(tmp_path)
    out = B.backup_now(db)
    assert out and os.path.dirname(out) == str(tmp_path / "backups")
    c = sqlite3.connect(out)
    assert c.execute("SELECT credits FROM users WHERE email='a@b.com'").fetchone()[0] == 42
    assert c.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    c.close()
    assert not [n for n in os.listdir(tmp_path / "backups") if n.endswith(".tmp")]


def test_copy_is_consistent_while_someone_is_writing(tmp_path):
    """มีคนเขียนค้างอยู่ (transaction ยังไม่ commit) — สำเนาต้องเป็นสถานะที่ commit แล้วเท่านั้น"""
    db = _db(tmp_path)
    w = sqlite3.connect(db)
    w.execute("PRAGMA journal_mode=WAL")
    w.execute("BEGIN")
    w.execute("UPDATE users SET credits = 0")
    out = B.backup_now(db)
    w.rollback()
    w.close()
    assert sqlite3.connect(out).execute("SELECT credits FROM users").fetchone()[0] == 42


def test_once_a_day_not_every_restart(tmp_path):
    db = _db(tmp_path)
    t = 1_800_000_000
    assert B.backup_if_due(db, now=t)
    assert B.backup_if_due(db, now=t + 3600) is None              # รีสตาร์ทบ่อย ไม่สำรองซ้ำ
    assert B.backup_if_due(db, now=t + 21 * 3600)                 # ครบวันแล้วสำรองใหม่


def test_keeps_a_week_of_dailies_and_a_month_of_weeklies(tmp_path):
    db = _db(tmp_path)
    day = 86400
    t0 = 1_800_000_000
    for i in range(40):
        B.backup_now(db, now=t0 + i * day)
    kept = B.list_backups(db)
    stamps = [datetime.strptime(os.path.basename(f)[3:-3], "%Y%m%d-%H%M%S").replace(tzinfo=timezone.utc) for f in kept]
    assert len(kept) <= B.KEEP_RECENT + B.KEEP_WEEKLY
    assert (stamps[-1] - stamps[0]).days >= 21                     # ย้อนได้หลายสัปดาห์
    assert (stamps[-1] - stamps[-7]).days == 6                     # 7 วันล่าสุดครบทุกวัน


def test_no_database_yet_means_nothing_to_back_up(tmp_path):
    assert B.backup_now(str(tmp_path / "missing.db")) is None


def test_health_reports_backup_age(client):
    assert "db_backup_hours" in client.get("/health").json()
