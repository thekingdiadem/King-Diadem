# DATABASE/db.py — KING DIADEM v2.2
# v2.2 — เพิ่ม chat_memory table สำหรับ cross-session RAG memory

import sqlite3, os, json, hashlib, hmac, secrets

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
        CREATE TABLE IF NOT EXISTS chat_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            memory_key TEXT NOT NULL,
            content TEXT NOT NULL,
            route TEXT,
            importance INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_chat_memory_user
            ON chat_memory(user_email, importance DESC, updated_at DESC);
        CREATE TABLE IF NOT EXISTS credit_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            delta INTEGER NOT NULL,
            reason TEXT,
            ref TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_credit_ledger_user
            ON credit_ledger(user_email, id DESC);
        CREATE TABLE IF NOT EXISTS usage_daily (
            identity TEXT NOT NULL,
            day TEXT NOT NULL,
            n INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (identity, day)
        );
        CREATE TABLE IF NOT EXISTS stripe_events (
            event_id TEXT PRIMARY KEY,
            event_type TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS premium (
            user_email TEXT PRIMARY KEY,
            premium_until REAL NOT NULL DEFAULT 0,
            stripe_customer TEXT,
            stripe_subscription TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS user_passwords (
            user_email TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
    print("✅ DB initialized")

# ── PASSWORD (email login) ─────────────────────────────────────
# PBKDF2-HMAC-SHA256 จาก standard library — ไม่ต้องเพิ่ม dependency
_PBKDF2_ROUNDS = 200_000

def _hash_password(password: str, salt: str = None) -> str:
    salt = salt or secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _PBKDF2_ROUNDS)
    return f"pbkdf2_sha256${_PBKDF2_ROUNDS}${salt}${dk.hex()}"

def has_password(user_email: str) -> bool:
    conn = get_conn()
    try:
        row = conn.execute("SELECT 1 FROM user_passwords WHERE user_email = ?", (user_email,)).fetchone()
        return row is not None
    finally:
        conn.close()

def set_password(user_email: str, password: str) -> bool:
    """ตั้งรหัสผ่านครั้งแรกเท่านั้น — คืน False ถ้าอีเมลนี้มีรหัสผ่านอยู่แล้ว"""
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT OR IGNORE INTO user_passwords (user_email, password_hash) VALUES (?, ?)",
            (user_email, _hash_password(password)),
        )
        conn.commit()
        return cur.rowcount == 1
    finally:
        conn.close()

def verify_password(user_email: str, password: str) -> bool:
    conn = get_conn()
    try:
        row = conn.execute("SELECT password_hash FROM user_passwords WHERE user_email = ?", (user_email,)).fetchone()
    finally:
        conn.close()
    if not row:
        # เทียบกับ hash หลอกเพื่อให้เวลาตอบเท่ากัน ไม่บอกว่าอีเมลมีอยู่หรือไม่
        _hash_password(password or "x")
        return False
    try:
        _, rounds, salt, want = row["password_hash"].split("$")
        got = hashlib.pbkdf2_hmac("sha256", (password or "").encode(), salt.encode(), int(rounds)).hex()
        return hmac.compare_digest(got, want)
    except Exception:
        return False

def user_exists(user_email: str) -> bool:
    conn = get_conn()
    try:
        return conn.execute("SELECT 1 FROM users WHERE email = ?", (user_email,)).fetchone() is not None
    finally:
        conn.close()

# ── STRIPE: idempotency + premium ──────────────────────────────
def claim_stripe_event(event_id: str, event_type: str = "") -> bool:
    """บันทึก event id — คืน False ถ้าเคยประมวลผลแล้ว (Stripe ส่งซ้ำได้)"""
    if not event_id:
        return True
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT OR IGNORE INTO stripe_events (event_id, event_type) VALUES (?, ?)",
            (event_id, event_type),
        )
        conn.commit()
        return cur.rowcount == 1
    finally:
        conn.close()

def release_stripe_event(event_id: str):
    """ยกเลิกการ claim เมื่อประมวลผลล้มเหลว เพื่อให้ Stripe retry ได้"""
    conn = get_conn()
    try:
        conn.execute("DELETE FROM stripe_events WHERE event_id = ?", (event_id,))
        conn.commit()
    finally:
        conn.close()

def set_premium_until(user_email: str, until_ts: float, customer: str = None, subscription: str = None):
    conn = get_conn()
    try:
        conn.execute("""
            INSERT INTO premium (user_email, premium_until, stripe_customer, stripe_subscription, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_email) DO UPDATE SET
                premium_until       = excluded.premium_until,
                stripe_customer     = COALESCE(excluded.stripe_customer, premium.stripe_customer),
                stripe_subscription = COALESCE(excluded.stripe_subscription, premium.stripe_subscription),
                updated_at          = CURRENT_TIMESTAMP
        """, (user_email, float(until_ts), customer, subscription))
        conn.commit()
    finally:
        conn.close()

def get_premium_until(user_email: str) -> float:
    conn = get_conn()
    try:
        row = conn.execute("SELECT premium_until FROM premium WHERE user_email = ?", (user_email,)).fetchone()
        return float(row["premium_until"]) if row else 0.0
    finally:
        conn.close()

def email_for_stripe_customer(customer: str):
    if not customer:
        return None
    conn = get_conn()
    try:
        row = conn.execute("SELECT user_email FROM premium WHERE stripe_customer = ?", (customer,)).fetchone()
        return row["user_email"] if row else None
    finally:
        conn.close()

# ── CHAT MEMORY API ────────────────────────────────────────────

def save_memory(user_email: str, memory_key: str, content: str,
                route: str = "general", importance: int = 1):
    """บันทึกหรืออัปเดต memory ด้วย key"""
    conn = get_conn()
    try:
        conn.execute("""
            INSERT INTO chat_memory (user_email, memory_key, content, route, importance, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT DO NOTHING
        """, (user_email, memory_key, content, route, importance))
        # ถ้า key ซ้ำ update แทน
        conn.execute("""
            UPDATE chat_memory
            SET content=?, route=?, importance=?, updated_at=CURRENT_TIMESTAMP
            WHERE user_email=? AND memory_key=?
        """, (content, route, importance, user_email, memory_key))
        conn.commit()
    finally:
        conn.close()

def get_relevant_memory(user_email: str, limit: int = 5) -> list:
    """ดึง memory ที่สำคัญที่สุด เรียงตาม importance + recency"""
    conn = get_conn()
    try:
        rows = conn.execute("""
            SELECT memory_key, content, route, importance, updated_at
            FROM chat_memory
            WHERE user_email=?
            ORDER BY importance DESC, updated_at DESC
            LIMIT ?
        """, (user_email, limit)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def get_recent_decisions(user_email: str, limit: int = 3) -> list:
    """ดึง decision log ล่าสุด เพื่อ context continuity"""
    conn = get_conn()
    try:
        rows = conn.execute("""
            SELECT input, route, response, created_at
            FROM decision_log
            WHERE user_email=? AND user_email != 'anonymous'
            ORDER BY created_at DESC
            LIMIT ?
        """, (user_email, limit)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def build_memory_context(user_email: str) -> str:
    """
    สร้าง memory context string ให้ inject เข้า prompt
    ถ้าไม่มี memory คืน empty string (ไม่บวม token)
    """
    if not user_email or user_email in ("anonymous", "guest"):
        return ""

    memories = get_relevant_memory(user_email, limit=5)
    recent = get_recent_decisions(user_email, limit=2)

    if not memories and not recent:
        return ""

    parts = []
    if memories:
        mem_lines = "\n".join(
            f"- [{m['memory_key']}] {m['content']}"
            for m in memories
        )
        parts.append(f"[MEMORY — สิ่งที่รู้เกี่ยวกับผู้ใช้]\n{mem_lines}")

    if recent:
        rec_lines = "\n".join(
            f"- ({r['route']}) {r['input'][:80]}…"
            for r in recent
        )
        parts.append(f"[บทสนทนาล่าสุด]\n{rec_lines}")

    return "\n\n".join(parts)

def auto_extract_memory(user_email: str, user_input: str,
                        ai_response: str, route: str = "general"):
    """
    Auto-extract memory จาก conversation โดยอัตโนมัติ
    จับ pattern สำคัญแล้วบันทึก — ทำงานหลัง log_decision
    """
    if not user_email or user_email in ("anonymous", "guest"):
        return

    text = user_input.lower()

    # Route สำคัญ = importance สูง
    importance_map = {
        "survival": 5,
        "collapse": 5,
        "risk": 4,
        "vega": 3,
        "civil": 2,
        "general": 1,
    }
    imp = importance_map.get(route, 1)

    # บันทึกเป้าหมายหลัก
    if any(k in text for k in ["อยากทำ", "เป้าหมาย", "ตั้งใจ", "plan", "project"]):
        save_memory(user_email, f"goal_{route}",
                    user_input[:200], route, importance=imp + 1)

    # บันทึกสถานการณ์วิกฤต
    if any(k in text for k in ["วิกฤต", "เงินหมด", "ตกงาน", "พัง", "ไม่ไหว", "หนี้"]):
        save_memory(user_email, "crisis_context",
                    user_input[:200], route, importance=5)

    # บันทึก route ที่ใช้บ่อย
    save_memory(user_email, "last_route", route, route, importance=1)

# ══════════════════════════════════════════════════════════════
# ฟังก์ชันเดิมทั้งหมด (ไม่เปลี่ยน)
# ══════════════════════════════════════════════════════════════

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

def add_credits(user_email: str, amount: int, reason: str = "grant", ref: str = None):
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
        conn.execute(
            "INSERT INTO credit_ledger (user_email, delta, reason, ref) VALUES (?, ?, ?, ?)",
            (user_email, int(amount), reason, ref),
        )
        conn.commit()
    finally:
        conn.close()

def spend_credit(user_email: str, amount: int = 1, reason: str = "run", ref: str = None) -> bool:
    """หักเครดิตแบบ atomic — คืน False ถ้าเครดิตไม่พอ (ไม่มีทางติดลบ)"""
    if not user_email or amount <= 0:
        return False
    conn = get_conn()
    try:
        cur = conn.execute(
            """UPDATE credits SET amount = amount - ?, updated_at = CURRENT_TIMESTAMP
               WHERE user_email = ? AND amount >= ?""",
            (amount, user_email, amount),
        )
        if cur.rowcount != 1:
            conn.rollback()
            return False
        conn.execute(
            "INSERT INTO credit_ledger (user_email, delta, reason, ref) VALUES (?, ?, ?, ?)",
            (user_email, -int(amount), reason, ref),
        )
        conn.commit()
        return True
    finally:
        conn.close()

def credit_history(user_email: str, limit: int = 20) -> list:
    conn = get_conn()
    try:
        rows = conn.execute(
            """SELECT delta, reason, ref, created_at FROM credit_ledger
               WHERE user_email = ? ORDER BY id DESC LIMIT ?""",
            (user_email, int(limit)),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

# ── โควตาฟรีรายวัน (นับฝั่ง server — ล้าง localStorage ก็ไม่ได้เพิ่ม) ──
def take_free_run(identity: str, day: str, limit: int) -> bool:
    if not identity or limit <= 0:
        return False
    conn = get_conn()
    try:
        conn.execute("INSERT OR IGNORE INTO usage_daily (identity, day, n) VALUES (?, ?, 0)", (identity, day))
        cur = conn.execute(
            "UPDATE usage_daily SET n = n + 1 WHERE identity = ? AND day = ? AND n < ?",
            (identity, day, int(limit)),
        )
        conn.commit()
        return cur.rowcount == 1
    finally:
        conn.close()

def give_back_free_run(identity: str, day: str):
    conn = get_conn()
    try:
        conn.execute("UPDATE usage_daily SET n = n - 1 WHERE identity = ? AND day = ? AND n > 0", (identity, day))
        conn.commit()
    finally:
        conn.close()

def free_runs_used(identity: str, day: str) -> int:
    conn = get_conn()
    try:
        row = conn.execute("SELECT n FROM usage_daily WHERE identity = ? AND day = ?", (identity, day)).fetchone()
        return int(row["n"]) if row else 0
    finally:
        conn.close()

def deduct_credits(user_email: str, amount: int) -> bool:
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
            (final_email, str(final_input)[:2000], route, persona, str(final_resp)[:4000])
        )
        conn.commit()
    finally:
        conn.close()

    # Auto-extract memory หลัง log
    auto_extract_memory(final_email, str(final_input), str(final_resp), route or "general")

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
