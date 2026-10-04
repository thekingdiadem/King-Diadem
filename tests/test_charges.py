"""ใบเสร็จการหัก (pending_charges): request ตายกลางทาง → คืนให้ภายหลัง ไม่คืนซ้ำ · /register จำกัดการไล่เช็กอีเมล"""
import time
import uuid

from DATABASE import db


def _pending():
    conn = db.get_conn()
    try:
        return conn.execute("SELECT COUNT(*) FROM pending_charges").fetchone()[0]
    finally:
        conn.close()


def test_answered_run_closes_its_charge(client):
    before = _pending()
    client.post("/run", json={"input": "วันนี้ควรทำอะไรก่อนดี"})
    assert _pending() == before


def test_dead_request_is_refunded_once(app_module):
    ident, day = f"t-{uuid.uuid4().hex[:8]}", app_module._today()
    assert db.take_free_run(ident, day, 3)
    ticket = app_module._open({"mode": "free", "identity": ident, "day": day})
    assert ticket.get("id") and db.free_runs_used(ident, day) == 1

    # จำลอง worker ตายก่อนได้คำตอบ: ใบเสร็จค้างนานเกิน 5 นาที
    conn = db.get_conn()
    conn.execute("UPDATE pending_charges SET created_at = ? WHERE id = ?", (time.time() - 600, ticket["id"]))
    conn.commit()
    conn.close()
    app_module._reclaim_stale(force=True)
    assert db.free_runs_used(ident, day) == 0

    # request เดิม (ถ้ายังมีชีวิต) เรียก _refund อีก → ต้องไม่คืนซ้ำ
    assert db.take_free_run(ident, day, 3)
    app_module._refund(ticket)
    assert db.free_runs_used(ident, day) == 1


def test_settled_charge_is_not_reclaimed(app_module):
    ident, day = f"t-{uuid.uuid4().hex[:8]}", app_module._today()
    assert db.take_free_run(ident, day, 3)
    ticket = app_module._open({"mode": "free", "identity": ident, "day": day})
    app_module._settle(ticket)
    app_module._reclaim_stale(force=True)
    assert db.free_runs_used(ident, day) == 1


def test_register_probe_is_rate_limited(user, client):
    codes = [client.post("/register", json={"email": user.email, "password": "secret12"}).status_code
             for _ in range(9)]
    assert codes[:8] == [409] * 8 and codes[8] == 429
