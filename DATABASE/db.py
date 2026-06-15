# DATABASE/db.py — KING DIADEM v2.1
# v2.1 — แก้ log_decision() signature ให้ตรงกับที่ app.py เรียก
#         (app.py เรียกด้วย kwargs: user_id, input, output, route, persona)
#         เดิม (v2.0) ใช้ user_email/input_text/response → TypeError ทุกครั้ง
#         (ถูก except: pass กลืนไว้ใน app.py เลย log ไม่เคยทำงาน)
# credits table ใช้ upsert ไม่ใช่ insert ซ้ำ

import sqlite3, os

DB_PATH = os.getenv("DB_PATH", "data/king_diadem.db")

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS credits (
            user_email TEXT PRIMARY KEY,
            amount INTEGER DEFAULT 0,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS decision_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            input TEXT,
            route TEXT,
            persona TEXT,
            response TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            amount_usd REAL,
            stripe_session_id TEXT,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS user_chat_state (
            user_email TEXT PRIMARY KEY,
            payload TEXT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
    print("✅ DB initialized")

def ensure_user(email: str):
    if not email or email in ("anonymous", "guest"):
        return
    conn = get_conn()
    try:
        conn.execute("INSERT OR IGNORE INTO users (email) VALUES (?)", (email,))
        conn.execute(
            "INSERT OR IGNORE INTO credits (user_email, amount) VALUES (?, 10)",
            (email,)
        )
        conn.commit()
    finally:
        conn.close()

def get_credits(user_email: str) -> int:
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT amount FROM credits WHERE user_email=?", (user_email,)
        ).fetchone()
        return int(row["amount"]) if row else 0
    finally:
        conn.close()

def add_credits(user_email: str, amount: int):
    ensure_user(user_email)
    conn = get_conn()
    try:
        conn.execute(
            """INSERT INTO credits (user_email, amount) VALUES (?, ?)
               ON CONFLICT(user_email) DO UPDATE SET
                 amount = amount + excluded.amount,
                 updated_at = CURRENT_TIMESTAMP""",
            (user_email, amount)
        )
        conn.commit()
    finally:
        conn.close()

def deduct_credits(user_email: str, amount: int) -> bool:
    """หักเครดิต — คืน False ถ้าไม่พอ"""
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT amount FROM credits WHERE user_email=?", (user_email,)
        ).fetchone()
        current = int(row["amount"]) if row else 0
        if current < amount:
            return False
        conn.execute(
            """UPDATE credits SET amount = amount - ?, updated_at = CURRENT_TIMESTAMP
               WHERE user_email = ?""",
            (amount, user_email)
        )
        conn.commit()
        return True
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════
# v2.1 FIX — log_decision()
# app.py เรียกด้วย: log_decision(user_id=email, input=user_input,
#                                  output=..., route=..., persona=...)
# รับทั้ง kwargs ใหม่ (user_id/input/output/persona) และชื่อเดิม
# (user_email/input_text/response) เพื่อ backward-compat
# ══════════════════════════════════════════════════════════════
def log_decision(
    user_id=None, input=None, output=None, route=None, persona=None,
    user_email=None, input_text=None, response=None,
):
    final_email = user_id or user_email or "anonymous"
    final_input = input if input is not None else (input_text or "")
    final_resp  = output if output is not None else (response or "")

    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO decision_log (user_email,input,route,persona,response) "
            "VALUES (?,?,?,?,?)",
            (
                final_email,
                str(final_input)[:2000],
                route,
                persona,
                str(final_resp)[:4000],
            )
        )
        conn.commit()
    finally:
        conn.close()


def save_chat_state(user_email: str, payload_json: str):
    conn = get_conn()
    try:
        conn.execute(
            """INSERT INTO user_chat_state (user_email, payload, updated_at)
               VALUES (?,?,CURRENT_TIMESTAMP)
               ON CONFLICT(user_email) DO UPDATE SET
                 payload=excluded.payload, updated_at=CURRENT_TIMESTAMP""",
            (user_email, payload_json),
        )
        conn.commit()
    finally:
        conn.close()

def load_chat_state(user_email: str):
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT payload FROM user_chat_state WHERE user_email=?",
            (user_email,),
        ).fetchone()
        return row["payload"] if row else None
    finally:
        conn.close()

def record_payment(user_email: str, amount_usd: float, session_id: str):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO payments (user_email,amount_usd,stripe_session_id,status) VALUES (?,?,?,'completed')",
            (user_email, amount_usd, session_id)
        )
        conn.commit()
    finally:
        conn.close()

def get_decision_history(user_email: str, limit: int = 20) -> list:
    conn = get_conn()
    try:
        rows = conn.execute(
            """SELECT input, route, response, created_at
               FROM decision_log WHERE user_email=?
               ORDER BY created_at DESC LIMIT ?""",
            (user_email, limit)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
