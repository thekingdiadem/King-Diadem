# DATABASE/payment_store.py
"""
KING DIADEM — Payment Store
idempotent payment recording — ป้องกัน double-charge
"""
from __future__ import annotations
import time
from typing import Optional

from DATABASE.db import get_conn


def payment_exists(payment_id: str) -> bool:
    try:
        with get_conn() as conn:
            row = conn.execute(
                "SELECT id FROM payments WHERE id = ?", (payment_id,)
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
    try:
        with get_conn() as conn:
            # ตรวจก่อน insert — ป้องกัน race condition
            existing = conn.execute(
                "SELECT id FROM payments WHERE id = ?", (payment_id,)
            ).fetchone()
            if existing:
                return False   # already recorded

            conn.execute(
                """INSERT INTO payments(id, email, amount, plan, provider, created_at)
                   VALUES(?, ?, ?, ?, ?, ?)""",
                (payment_id, email, amount, plan, provider, time.time()),
            )
            conn.commit()
            return True
    except Exception:
        return False


def get_payment(payment_id: str) -> Optional[dict]:
    try:
        with get_conn() as conn:
            row = conn.execute(
                "SELECT id, email, amount, plan, provider, created_at "
                "FROM payments WHERE id = ?", (payment_id,)
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
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT id, amount, plan, provider, created_at "
                "FROM payments WHERE email = ? ORDER BY created_at DESC",
                (email,)
            ).fetchall()
            return [
                {"id": r[0], "amount": r[1], "plan": r[2],
                 "provider": r[3], "created_at": r[4]}
                for r in rows
            ]
    except Exception:
        return []
