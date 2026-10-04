# GLOBAL_NODE/node_trust.py
# KING DIADEM™ — Node Trust Registry
# Article 2: Trust is earned, bounded, and auditable.
# Article 6: Persistence via SQLite — ไม่ใช้ flat JSON ที่ race condition ได้

import sqlite3
import threading
import time
import os
from contextlib import contextmanager
from typing import Optional

# ── Config ────────────────────────────────────────────────────────
DB_PATH          = os.environ.get("KD_DB_PATH") or os.environ.get("DB_PATH", "data/king_diadem.db")
TRUST_DEFAULT    = 0.5
TRUST_MAX        = 1.0
TRUST_MIN        = 0.0
TRUST_GAIN       = 0.05   # ต่อ valid interaction
TRUST_PENALTY    = 0.10   # ต่อ invalid interaction
TRUST_DECAY_RATE = 0.01   # decay ต่อวันที่ไม่มี interaction (ป้องกัน stale trust)

_lock = threading.Lock()


# ── DB init ───────────────────────────────────────────────────────
_table_ready = False


@contextmanager
def _get_conn():
    """เปิด-ปิด connection จริง (เดิม `with conn` แค่ commit ไม่ปิด → fd รั่ว)
    และสร้างตารางเองครั้งแรก — เดิมสร้างแค่ใน _self_test ทำให้ production อัปเดต trust ล้มเงียบทุกครั้ง"""
    global _table_ready
    d = os.path.dirname(DB_PATH)
    if d:
        os.makedirs(d, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=15)
    conn.row_factory = sqlite3.Row
    try:
        if not _table_ready:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS node_trust (
                    node_id     TEXT PRIMARY KEY,
                    score       REAL NOT NULL DEFAULT 0.5,
                    updated_at  REAL NOT NULL,
                    interactions INTEGER NOT NULL DEFAULT 0
                )
            """)
            conn.commit()
            _table_ready = True
        yield conn
    finally:
        conn.close()


def _ensure_table() -> None:
    """สร้าง table ถ้ายังไม่มี — เรียกครั้งเดียวตอน startup"""
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS node_trust (
                node_id     TEXT PRIMARY KEY,
                score       REAL NOT NULL DEFAULT 0.5,
                updated_at  REAL NOT NULL,
                interactions INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.commit()


# ── Core API ──────────────────────────────────────────────────────
def get_trust(node_id: str) -> float:
    """
    คืน trust score ของ node
    ถ้ายังไม่มีในระบบ → คืน TRUST_DEFAULT (0.5)

    Article 2 — trust ต้องอ่านได้ตลอดเวลา
    """
    try:
        with _lock, _get_conn() as conn:
            row = conn.execute(
                "SELECT score FROM node_trust WHERE node_id = ?", (node_id,)
            ).fetchone()
        return float(row["score"]) if row else TRUST_DEFAULT
    except Exception:
        return TRUST_DEFAULT


def update_trust(node_id: str, valid: bool = True) -> float:
    """
    อัปเดต trust score — atomic, thread-safe
    valid=True  → +TRUST_GAIN
    valid=False → -TRUST_PENALTY

    Article 2 — trust เปลี่ยนได้เฉพาะผ่าน function นี้
    คืน score ใหม่
    """
    with _lock:
        try:
            with _get_conn() as conn:
                row = conn.execute(
                    "SELECT score, interactions FROM node_trust WHERE node_id = ?",
                    (node_id,)
                ).fetchone()

                current_score = float(row["score"]) if row else TRUST_DEFAULT
                interactions  = int(row["interactions"]) + 1 if row else 1

                delta     = TRUST_GAIN if valid is True else -TRUST_PENALTY
                new_score = round(
                    max(TRUST_MIN, min(TRUST_MAX, current_score + delta)), 4
                )
                now = time.time()

                conn.execute("""
                    INSERT INTO node_trust (node_id, score, updated_at, interactions)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(node_id) DO UPDATE SET
                        score        = excluded.score,
                        updated_at   = excluded.updated_at,
                        interactions = excluded.interactions
                """, (node_id, new_score, now, interactions))
                conn.commit()
            return new_score
        except Exception:
            return TRUST_DEFAULT


def reset_trust(node_id: str) -> float:
    """reset trust กลับ default — ใช้ใน admin / test"""
    with _lock:
        try:
            with _get_conn() as conn:
                conn.execute("""
                    INSERT INTO node_trust (node_id, score, updated_at, interactions)
                    VALUES (?, ?, ?, 0)
                    ON CONFLICT(node_id) DO UPDATE SET
                        score      = ?,
                        updated_at = ?,
                        interactions = 0
                """, (node_id, TRUST_DEFAULT, time.time(), TRUST_DEFAULT, time.time()))
                conn.commit()
        except Exception:
            pass
    return TRUST_DEFAULT


def apply_decay(max_age_days: float = 7.0) -> int:
    """
    ลด trust ของ node ที่ไม่มี interaction เกิน max_age_days
    เรียกจาก APScheduler รายวัน — ไม่ใช่ per-request

    Article 2 — trust ที่หยุดนิ่งต้อง decay ไม่ใช่ freeze
    คืนจำนวน node ที่ถูก decay
    """
    cutoff = time.time() - (max_age_days * 86400)
    count  = 0
    with _lock:
        try:
            with _get_conn() as conn:
                rows = conn.execute(
                    "SELECT node_id, score FROM node_trust WHERE updated_at < ?",
                    (cutoff,)
                ).fetchall()
                for row in rows:
                    new_score = round(
                        max(TRUST_MIN, float(row["score"]) - TRUST_DECAY_RATE), 4
                    )
                    conn.execute(
                        "UPDATE node_trust SET score = ?, updated_at = ? WHERE node_id = ?",
                        (new_score, time.time(), row["node_id"])
                    )
                    count += 1
                conn.commit()
        except Exception:
            pass
    return count


def get_all_trust() -> dict:
    """dump trust ทั้งหมด — ใช้ใน /api/kernel_snapshot"""
    try:
        with _lock, _get_conn() as conn:
            rows = conn.execute(
                "SELECT node_id, score, interactions FROM node_trust"
            ).fetchall()
        return {row["node_id"]: {"score": row["score"], "interactions": row["interactions"]}
                for row in rows}
    except Exception:
        return {}


# ── Self-test ─────────────────────────────────────────────────────
def _self_test() -> dict:
    _ensure_table()
    test_id = "__test_node__"
    reset_trust(test_id)

    s0 = get_trust(test_id)
    assert s0 == TRUST_DEFAULT, f"expected {TRUST_DEFAULT} got {s0}"

    s1 = update_trust(test_id, valid=True)
    assert s1 == round(TRUST_DEFAULT + TRUST_GAIN, 4), f"gain failed: {s1}"

    s2 = update_trust(test_id, valid=False)
    assert s2 == round(s1 - TRUST_PENALTY, 4), f"penalty failed: {s2}"

    # clamp test
    for _ in range(30):
        update_trust(test_id, valid=True)
    assert get_trust(test_id) <= TRUST_MAX

    reset_trust(test_id)
    assert get_trust(test_id) == TRUST_DEFAULT

    return {"status": "OK", "module": "node_trust"}


if __name__ == "__main__":
    _ensure_table()
    print(_self_test())

