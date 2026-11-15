"""ลอกท่อรอบดึก (core/housekeeping) — ล้างเฉพาะตะกอน ไม่แตะของสำคัญ และไม่ทำให้เซิร์ฟเวอร์ล้ม"""
from datetime import datetime, timedelta, timezone

import pytest

from core import housekeeping as hk

BKK = timezone(timedelta(hours=7))


@pytest.fixture(autouse=True)
def _fresh(monkeypatch, tmp_path):
    monkeypatch.setitem(hk._last, "ts", 0.0)
    import DATABASE.db as db
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "t.db"), raising=False)
    db.init_db() if hasattr(db, "init_db") else None
    yield


def test_only_runs_at_quiet_hours_once_a_day():
    night = datetime(2026, 11, 16, 3, 0, tzinfo=BKK)
    assert hk.due(night)                       # ยังไม่เคยทำ = ค้างนาน ทำได้เลย
    hk._last["ts"] = night.timestamp()
    assert not hk.due(night + timedelta(hours=10))           # วันเดียวกัน ไม่ทำซ้ำ
    assert not hk.due(datetime(2026, 11, 17, 0, 0, tzinfo=BKK))   # ครบ 21 ชม. แต่ยังไม่ถึงช่วงดึก รอก่อน
    assert hk.due(datetime(2026, 11, 17, 3, 0, tzinfo=BKK))       # ดึกคืนถัดไป ทำ
    assert hk.due(night + timedelta(hours=31))                    # ไม่ได้ทำเกิน 30 ชม. ทำได้ทุกเวลา


def test_clears_old_free_counters_but_keeps_today():
    from DATABASE.db import get_conn, take_free_run
    now = datetime(2026, 11, 16, 3, 0, tzinfo=BKK)
    take_free_run("ip:a", "2026-10-01", 3)
    take_free_run("ip:a", "2026-11-16", 3)
    out = hk.run(now, force=True)
    assert out["done"]["usage_daily"] == 1 and not out["skipped"]
    c = get_conn()
    days = [r[0] for r in c.execute("SELECT day FROM usage_daily")]
    c.close()
    assert days == ["2026-11-16"]


def test_a_broken_step_is_skipped_not_fatal(monkeypatch):
    def boom(now):
        raise RuntimeError("x")
    monkeypatch.setattr(hk, "STEPS", (("boom", boom),) + hk.STEPS[1:])
    out = hk.run(datetime(2026, 11, 16, 3, 0, tzinfo=BKK), force=True)
    assert out["skipped"] == ["boom: RuntimeError"] and "sqlite" in out["done"]


def test_never_touches_important_tables():
    src = open(hk.__file__, encoding="utf-8").read()
    for t in ("users", "credits", "payments", "credit_ledger", "decision_history", "chat_memory", "audit", "backups"):
        assert f"DELETE FROM {t}" not in src


def test_expired_reports_are_cleared_while_server_keeps_running():
    from DATABASE.db import get_conn
    c = get_conn()
    c.execute("CREATE TABLE IF NOT EXISTS decision_reports (id TEXT, user_email TEXT, expires_at TEXT)")
    c.execute("INSERT INTO decision_reports VALUES ('old','a','2020-01-01 00:00:00'), ('new','a','2999-01-01 00:00:00')")
    c.commit(); c.close()
    out = hk.run(datetime(2026, 11, 16, 3, 0, tzinfo=BKK), force=True)
    assert out["done"]["expired_reports"] == 1
    c = get_conn()
    assert [r[0] for r in c.execute("SELECT id FROM decision_reports")] == ["new"]
    c.close()
