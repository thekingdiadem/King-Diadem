"""เครดิตต้อนรับต้องลงสมุดบัญชี (credit_ledger) — สมุดนี้คือหลักฐานทางบัญชีที่เก็บไว้แม้ลบบัญชี
เดิม ensure_user ให้ 10 เครดิตโดยไม่จด → ยอดรวมในสมุดน้อยกว่ายอดจริง 10 ทุกบัญชี
และหน้า wallet ที่เตรียมป้าย "เครดิตเริ่มต้น" (grant) ไว้ ขึ้นว่า "ยังไม่มีรายการ" ทั้งที่มีเครดิตอยู่"""
import concurrent.futures as cf
import uuid

from DATABASE import db


def _ledger_sum(email):
    conn = db.get_conn()
    try:
        return int(conn.execute("SELECT COALESCE(SUM(delta), 0) FROM credit_ledger WHERE user_email = ?", (email,)).fetchone()[0])
    finally:
        conn.close()


def _grants(email):
    return [h for h in db.credit_history(email, 50) if h.get("reason") == "grant"]


def test_new_account_welcome_credit_is_in_the_ledger():
    em = f"w{uuid.uuid4().hex[:10]}@test.co"
    db.ensure_user(em)
    assert db.get_credits(em) == 10
    assert [g["delta"] for g in _grants(em)] == [10]
    assert _ledger_sum(em) == db.get_credits(em)


def test_ensure_user_again_does_not_grant_twice():
    em = f"w{uuid.uuid4().hex[:10]}@test.co"
    for _ in range(3):
        db.ensure_user(em)
    assert db.get_credits(em) == 10 and len(_grants(em)) == 1


def test_ledger_matches_balance_after_spending_and_topup():
    em = f"w{uuid.uuid4().hex[:10]}@test.co"
    db.ensure_user(em)
    assert db.spend_credit(em, 3, "run")
    db.add_credits(em, 7, "topup", "cs_test")
    assert db.get_credits(em) == 14 == _ledger_sum(em)


def test_concurrent_ensure_user_grants_once():
    em = f"w{uuid.uuid4().hex[:10]}@test.co"
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        list(ex.map(lambda _: db.ensure_user(em), range(12)))
    assert db.get_credits(em) == 10 and len(_grants(em)) == 1 and _ledger_sum(em) == 10


def test_wallet_page_shows_the_welcome_credit(user):
    hist = user.post("/wallet/balance").json()["history"]
    assert [h["reason"] for h in hist] == ["grant"] and hist[0]["delta"] == 10
