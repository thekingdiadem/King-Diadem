# DATABASE/payment_store.py
"""
KING DIADEM — Payment Store
idempotent payment recording — ป้องกัน double-charge
"""
from __future__ import annotations
import time
from typing import Optional

from DATABASE.db import get_conn

# เดิม query คอลัมน์ id/email/amount/plan/provider บนตาราง payments ของ db.py ซึ่งไม่มีคอลัมน์เหล่านี้
# → ทุกคำสั่งล้ม: payment_exists คืน True เสมอ, record_payment คืน False เสมอ
# ใช้ตารางของตัวเองที่มี payment_id เป็น PRIMARY KEY (idempotent จริงด้วย INSERT OR IGNORE)
_TABLE = "payment_records"


def _ensure():
    with get_conn() as conn:
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {_TABLE} (
                id         TEXT PRIMARY KEY,
                email      TEXT,
                amount     REAL,
                plan       TEXT,
                provider   TEXT,
                created_at REAL
            )""")
        conn.commit()


def payment_exists(payment_id: str) -> bool:
    try:
        _ensure()
        with get_conn() as conn:
            row = conn.execute(
                f"SELECT id FROM {_TABLE} WHERE id = ?", (payment_id,)
            ).fetchone()
            return row is not None
    except Exception:
        # ถ้า DB ไม่พร้อม — conservative: assume exists เพื่อป้องกัน double-charge
        return True


def record_payment(
    payment_id: str,
    email:      str   = "",
    amount:     float = 0.0,
    plan:       str   = "",
    provider:   str   = "stripe",
) -> bool:
    """
    บันทึก payment — idempotent
    ถ้า payment_id ซ้ำ → return False ไม่ crash
    """
    if not payment_id:
        return False
    try:
        _ensure()
        with get_conn() as conn:
            # INSERT OR IGNORE บน PRIMARY KEY = atomic (เดิม SELECT แล้ว INSERT แยกกัน → race)
            cur = conn.execute(
                f"""INSERT OR IGNORE INTO {_TABLE}(id, email, amount, plan, provider, created_at)
                   VALUES(?, ?, ?, ?, ?, ?)""",
                (str(payment_id), email, amount, plan, provider, time.time()),
            )
            conn.commit()
            return cur.rowcount == 1
    except Exception:
        return False


def get_payment(payment_id: str) -> Optional[dict]:
    try:
        _ensure()
        with get_conn() as conn:
            row = conn.execute(
                f"SELECT id, email, amount, plan, provider, created_at "
                f"FROM {_TABLE} WHERE id = ?", (payment_id,)
            ).fetchone()
            if not row:
                return None
            return {
                "id":         row[0],
                "email":      row[1],
                "amount":     row[2],
                "plan":       row[3],
                "provider":   row[4],
                "created_at": row[5],
            }
    except Exception:
        return None


def get_payments_by_email(email: str) -> list:
    try:
        _ensure()
        with get_conn() as conn:
            rows = conn.execute(
                f"SELECT id, amount, plan, provider, created_at "
                f"FROM {_TABLE} WHERE email = ? ORDER BY created_at DESC",
                (email,)
            ).fetchall()
            return [
                {"id": r[0], "amount": r[1], "plan": r[2],
                 "provider": r[3], "created_at": r[4]}
                for r in rows
            ]
    except Exception:
        return []
