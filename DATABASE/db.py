# DATABASE/db.py — KING DIADEM v2.2
# v2.2 — เพิ่ม chat_memory table สำหรับ cross-session RAG memory

import sqlite3, os, json, hashlib, hmac, re, secrets

DB_PATH = os.getenv("DB_PATH", "data/king_diadem.db")

def get_conn():
    d = os.path.dirname(DB_PATH)
    if d:
        os.makedirs(d, exist_ok=True)
    # timeout + busy_timeout: เดิมใช้ค่าเริ่มต้น — worker หลาย thread เขียนพร้อมกันได้ "database is locked"
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 15000")
    return conn

def init_db():
    conn = get_conn()
    try:
        conn.execute("PRAGMA journal_mode = WAL")   # อ่านพร้อมเขียนได้ ไม่ล็อกทั้งไฟล์
    except sqlite3.DatabaseError:
        pass
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
        CREATE INDEX IF NOT EXISTS idx_chat_memory_key
            ON chat_memory(user_email, memory_key);
        CREATE INDEX IF NOT EXISTS idx_decision_log_user
            ON decision_log(user_email, created_at DESC);
        CREATE TABLE IF NOT EXISTS waterline_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            waterline REAL NOT NULL,
            state TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_waterline_user
            ON waterline_log(user_email, id DESC);
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
        CREATE INDEX IF NOT EXISTS idx_credit_ledger_ref
            ON credit_ledger(reason, ref);
        CREATE TABLE IF NOT EXISTS pending_charges (
            id TEXT PRIMARY KEY,
            mode TEXT NOT NULL,
            identity TEXT,
            day TEXT,
            email TEXT,
            what TEXT,
            created_at REAL NOT NULL
        );
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

def stripe_event_done(event_id: str) -> bool:
    """event นี้ประมวลผลสำเร็จแล้วหรือยัง (บันทึกหลังทำเสร็จเท่านั้น)"""
    if not event_id:
        return False
    conn = get_conn()
    try:
        return conn.execute("SELECT 1 FROM stripe_events WHERE event_id = ?", (event_id,)).fetchone() is not None
    finally:
        conn.close()

def mark_stripe_event(event_id: str, event_type: str = ""):
    """บันทึกว่าประมวลผลเสร็จแล้ว — เรียกหลังการให้เครดิต/premium สำเร็จ
    (เดิม claim ก่อนประมวลผล: server ดับกลางทาง → Stripe ส่งซ้ำก็ถูกมองว่าซ้ำ เงินจ่ายแล้วแต่ไม่ได้เครดิต)"""
    if not event_id:
        return
    conn = get_conn()
    try:
        conn.execute("INSERT OR IGNORE INTO stripe_events (event_id, event_type) VALUES (?, ?)",
                     (event_id, event_type))
        conn.commit()
    finally:
        conn.close()

def add_credits_once(user_email: str, amount: int, reason: str, ref: str) -> bool:
    """ให้เครดิตครั้งเดียวต่อ (reason, ref) — ยอดและ ledger อยู่ใน transaction เดียว
    ref = id ของ Stripe checkout session: event ซ้ำ/ประมวลผลซ้ำหลังล่ม ไม่เติมซ้ำ"""
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        return False
    if not user_email or amount <= 0 or not ref:
        return False
    ensure_user(user_email)
    conn = get_conn()
    try:
        conn.execute("BEGIN IMMEDIATE")          # ล็อกการเขียน: สอง delivery พร้อมกันจะเรียงคิว
        if conn.execute("SELECT 1 FROM credit_ledger WHERE reason = ? AND ref = ?",
                        (reason, ref)).fetchone():
            conn.rollback()
            return False
        conn.execute(
            """INSERT INTO credits (user_email, amount) VALUES (?, ?)
               ON CONFLICT(user_email) DO UPDATE SET
                 amount = amount + excluded.amount,
                 updated_at = CURRENT_TIMESTAMP""",
            (user_email, amount))
        conn.execute("INSERT INTO credit_ledger (user_email, delta, reason, ref) VALUES (?, ?, ?, ?)",
                     (user_email, amount, reason, ref))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
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

def premium_subscription(user_email: str):
    """subscription id ที่ผูกกับ premium ของบัญชีนี้ล่าสุด"""
    conn = get_conn()
    try:
        row = conn.execute("SELECT stripe_subscription FROM premium WHERE user_email = ?", (user_email,)).fetchone()
        return row["stripe_subscription"] if row else None
    finally:
        conn.close()

def customer_for_email(user_email: str):
    """Stripe customer ของบัญชีนี้ (ใช้เปิดหน้าจัดการสมาชิก)"""
    conn = get_conn()
    try:
        row = conn.execute("SELECT stripe_customer FROM premium WHERE user_email = ?", (user_email,)).fetchone()
        return row["stripe_customer"] if row else None
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
    """บันทึกหรืออัปเดต memory ด้วย key

    เดิม INSERT ... ON CONFLICT DO NOTHING แต่ตารางไม่มี unique key → แทรกแถวใหม่ทุกครั้ง
    ("last_route" +1 แถวต่อทุกข้อความ) ตารางโตไม่หยุด และ memory ที่ส่งเข้า prompt ซ้ำกัน
    ตอนนี้: UPDATE ก่อน ถ้าไม่มีแถวค่อย INSERT
    """
    conn = get_conn()
    try:
        cur = conn.execute("""
            UPDATE chat_memory
            SET content=?, route=?, importance=?, updated_at=CURRENT_TIMESTAMP
            WHERE user_email=? AND memory_key=?
        """, (content, route, importance, user_email, memory_key))
        if cur.rowcount == 0:
            conn.execute("""
                INSERT INTO chat_memory (user_email, memory_key, content, route, importance, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (user_email, memory_key, content, route, importance))
        conn.commit()
    finally:
        conn.close()

def get_relevant_memory(user_email: str, limit: int = 5) -> list:
    """ดึง memory ที่สำคัญที่สุด เรียงตาม importance + recency (1 แถวต่อ key — แถวซ้ำเก่ายังอยู่ในตาราง)"""
    conn = get_conn()
    try:
        rows = conn.execute("""
            SELECT memory_key, content, route, importance, updated_at
            FROM chat_memory
            WHERE id IN (SELECT MAX(id) FROM chat_memory WHERE user_email=? GROUP BY memory_key)
            ORDER BY importance DESC, updated_at DESC
            LIMIT ?
        """, (user_email, int(limit))).fetchall()
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

# ── ความจำข้ามแชท: ผู้ใช้ควบคุมเองได้ (ดู · ปิด · ล้าง) ──────────────────────────
# แถวเหล่านี้เป็นค่าตั้ง/ข้อมูลภายใน ไม่ใช่ "สิ่งที่รู้เกี่ยวกับผู้ใช้" — ไม่ส่งเข้า prompt และไม่แสดง
_MEM_INTERNAL = ("engine_last_turns", "last_route", "memory_reset", "memory_off")


def _mem_value(user_email: str, key: str):
    conn = get_conn()
    try:
        row = conn.execute("SELECT content FROM chat_memory WHERE user_email=? AND memory_key=? "
                           "ORDER BY id DESC LIMIT 1", (user_email, key)).fetchone()
        return row["content"] if row else None
    finally:
        conn.close()


def memory_enabled(user_email: str) -> bool:
    if not user_email or user_email in ("anonymous", "guest"):
        return False
    return _mem_value(user_email, "memory_off") != "1"


def set_memory_enabled(user_email: str, on: bool) -> None:
    save_memory(user_email, "memory_off", "0" if on else "1", "general", importance=0)


def list_memory(user_email: str) -> list:
    """สิ่งที่ LYLA จำไว้ (สำหรับให้ผู้ใช้ดูเอง)"""
    if not user_email or user_email in ("anonymous", "guest"):
        return []
    return [m for m in get_relevant_memory(user_email, limit=50) if m["memory_key"] not in _MEM_INTERNAL]


def clear_memory(user_email: str) -> int:
    """ลบความจำทั้งหมดของผู้ใช้ และไม่ดึงบทสนทนาก่อนหน้านี้มาใช้อีก (คงค่าเปิด/ปิดไว้)"""
    if not user_email or user_email in ("anonymous", "guest"):
        return 0
    conn = get_conn()
    try:
        cur = conn.execute("DELETE FROM chat_memory WHERE user_email=? AND memory_key != 'memory_off'", (user_email,))
        conn.execute("DELETE FROM waterline_log WHERE user_email=?", (user_email,))
        conn.commit()
        n = cur.rowcount
    finally:
        conn.close()
    from datetime import datetime, timezone
    save_memory(user_email, "memory_reset", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                "general", importance=0)
    return n


# ── waterline รายคน: ติดตามว่าช่วงนี้ผู้ใช้มั่นคงขึ้นหรือหนักลง ──────────────────────
# เก็บเฉพาะตอนผู้ใช้เล่าสถานะเอง (ไม่เก็บค่าตั้งต้น) · ผูกกับสวิตช์ความจำ · ล้างพร้อมความจำ
_WATERLINE_KEEP = 60


def record_waterline(user_email: str, waterline, state: str = "") -> bool:
    if not memory_enabled(user_email):
        return False
    try:
        wl = max(0.0, min(100.0, float(waterline)))
    except (TypeError, ValueError):
        return False
    conn = get_conn()
    try:
        conn.execute("INSERT INTO waterline_log (user_email, waterline, state) VALUES (?,?,?)",
                     (user_email, wl, str(state or "")[:40]))
        conn.execute("""DELETE FROM waterline_log WHERE user_email=? AND id NOT IN
                        (SELECT id FROM waterline_log WHERE user_email=? ORDER BY id DESC LIMIT ?)""",
                     (user_email, user_email, _WATERLINE_KEEP))
        conn.commit()
    finally:
        conn.close()
    return True


def waterline_history(user_email: str, limit: int = 20) -> dict:
    """ค่าล่าสุดก่อน · trend เทียบค่าเฉลี่ย 3 ครั้งล่าสุดกับ 3 ครั้งก่อนหน้า"""
    if not memory_enabled(user_email):
        return {"points": [], "latest": None, "trend": "unknown"}
    conn = get_conn()
    try:
        rows = conn.execute("SELECT waterline, state, created_at FROM waterline_log "
                            "WHERE user_email=? ORDER BY id DESC LIMIT ?",
                            (user_email, max(1, min(int(limit), _WATERLINE_KEEP)))).fetchall()
    finally:
        conn.close()
    points = [{"waterline": r["waterline"], "state": r["state"], "at": str(r["created_at"])} for r in rows]
    trend = "unknown"
    if len(points) >= 2:
        k = min(3, len(points) // 2)
        recent = sum(p["waterline"] for p in points[:k]) / k
        before = sum(p["waterline"] for p in points[k:2 * k]) / k
        trend = "rising" if recent - before >= 5 else "falling" if before - recent >= 5 else "steady"
    return {"points": points, "latest": points[0]["waterline"] if points else None, "trend": trend}


def build_memory_context(user_email: str) -> str:
    """
    สร้าง memory context string ให้ inject เข้า prompt
    ถ้าไม่มี memory คืน empty string (ไม่บวม token)
    """
    if not memory_enabled(user_email):
        return ""

    memories = [m for m in get_relevant_memory(user_email, limit=10)
                if m["memory_key"] not in _MEM_INTERNAL][:5]
    reset_at = _mem_value(user_email, "memory_reset") or ""
    recent = [r for r in get_recent_decisions(user_email, limit=2)
              if not reset_at or str(r.get("created_at") or "") > reset_at]

    if not memories and not recent:
        return ""

    parts = []
    if memories:
        mem_lines = "\n".join(
            f"- [{m['memory_key']}] {m['content']}"
            for m in memories
        )
        parts.append("[MEMORY — สิ่งที่รู้เกี่ยวกับผู้ใช้จากแชทก่อนๆ: ใช้เพื่อเข้าใจต่อเนื่องอย่างอ่อนโยน "
                     "พูดถึงเฉพาะเมื่อเกี่ยวกับเรื่องตอนนี้ ห้ามยกป้ายนี้มาพูด]\n" + mem_lines)

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
    if not memory_enabled(user_email):
        return

    text = str(user_input or "").lower()
    # เรื่องเปราะบาง (ทำร้ายตัวเอง/ถูกทำร้าย/วิกฤต) ไม่เก็บข้อความ — เก็บแค่ว่าเคยผ่านช่วงหนัก เพื่อถามไถ่อย่างอ่อนโยน
    topics, sensitive = [], False
    try:
        from core.kernel_voice import assess
        a = assess(str(user_input or "")[:2000])
        topics = [t for t in a.get("topics", []) if t not in ("positive", "decision")][:3]
        sensitive = bool(a.get("crisis") or a.get("relationship") or
                         set(topics) & {"warning", "overdose", "violence", "pregnancy", "addiction", "someone",
                                        "sexual_abuse", "sextortion", "stop_meds", "panic", "drunk_drive",
                                        "eating", "psychosis", "diagnosis", "legal"})
    except Exception:
        pass
    if sensitive:
        from datetime import date
        save_memory(user_email, "sensitive_checkin",
                    f"เคยเล่าเรื่องที่หนักมาก (เมื่อ {date.today().isoformat()}) — ถามไถ่อย่างอ่อนโยนว่าตอนนี้เป็นอย่างไร "
                    "ไม่ต้องลงรายละเอียดเรื่องเดิม", route, importance=5)
        save_memory(user_email, "last_route", route, route, importance=1)
        return
    if topics:
        th = {"debt": "หนี้", "money": "เงิน", "job": "งาน", "business": "ธุรกิจ", "relationship": "ความรัก",
              "family": "ครอบครัว", "study": "การเรียน", "lonely": "ความเหงา", "stress": "ความเครียด",
              "health": "สุขภาพ", "basic": "ปัจจัยพื้นฐาน", "grief": "การสูญเสีย", "bullying": "การถูกแกล้ง",
              "scam": "มิจฉาชีพ", "help": "ขอความช่วยเหลือ", "health_emergency": "เจ็บป่วยฉุกเฉิน",
              "first_aid": "ปฐมพยาบาล", "missing": "ตามหาคนหาย", "labor": "สิทธิแรงงาน", "housing": "ที่อยู่/ค่าเช่า",
              "caregiver": "การดูแลคนในบ้าน", "health_rights": "สิทธิรักษา"}
        save_memory(user_email, "recent_topics", "เคยคุยเรื่อง: " + " · ".join(th.get(t, t) for t in topics),
                    route, importance=2)

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
    # คำอังกฤษเป็นคำเต็ม ("plan" ไม่ติด "planet"/"explanation")
    if any(k in text for k in ["อยากทำ", "เป้าหมาย", "ตั้งใจ"]) or \
            re.search(r"(?<![a-z])(plan|project)(?![a-z])", text):
        save_memory(user_email, f"goal_{route}",
                    user_input[:200], route, importance=imp + 1)

    # บันทึกสถานการณ์ที่ยาก (เงิน/งาน) — เรื่องเปราะบางกว่านี้ไม่ถึงตรงนี้ (กรองไว้ด้านบน)
    if any(k in text for k in ["วิกฤต", "เงินหมด", "ตกงาน", "พังหมด", "เป็นหนี้", "หนี้สิน"]):
        save_memory(user_email, "crisis_context",
                    user_input[:160], route, importance=4)

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
    # จำนวนต้องเป็นจำนวนเต็มบวก — เดิมรับค่าลบ/ทศนิยม (credits เก็บค่าดิบ แต่ ledger ปัด int → ไม่ตรงกัน)
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        return
    if not user_email or amount <= 0:
        return
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
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        return False
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
    """ชื่อเดิม — เดิม SELECT แล้ว UPDATE (หักซ้ำ/ติดลบได้เมื่อพร้อมกัน) และไม่ลง ledger"""
    return spend_credit(user_email, amount, reason="deduct")

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
            (user_email, max(1, min(int(limit), 200)))
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()



# ── การหักที่ยังไม่ปิด (ใบเสร็จค้าง) ─────────────────────────────────────
# เดิม "ตั๋ว" ของการหักโควตา/เครดิตอยู่ในหน่วยความจำของ request เท่านั้น ถ้า worker ถูกฆ่ากลางทาง
# (gunicorn --timeout, deploy, เครื่องดับ) ผู้ใช้ถูกหักแต่ไม่ได้คำตอบและไม่ได้คืน
# ตอนนี้จดลงฐานข้อมูลก่อน แล้วลบเมื่อได้คำตอบ/คืนแล้ว — แถวที่ค้างนานคือ request ที่ตายไปแล้ว
def open_charge(ticket: dict) -> str:
    import time as _t, uuid as _u
    cid = _u.uuid4().hex
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO pending_charges (id, mode, identity, day, email, what, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (cid, ticket.get("mode"), ticket.get("identity"), ticket.get("day"),
             ticket.get("email"), ticket.get("what"), _t.time()))
        conn.commit()
    finally:
        conn.close()
    return cid


def close_charge(cid: str) -> bool:
    """ปิดใบเสร็จ — True ถ้ายังค้างอยู่ (ยังไม่ถูกเก็บคืนโดย reclaim_stale_charges)"""
    if not cid:
        return False
    conn = get_conn()
    try:
        cur = conn.execute("DELETE FROM pending_charges WHERE id = ?", (cid,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def reclaim_stale_charges(older_than_s: float = 300) -> list:
    """เอาใบเสร็จที่ค้างนานกว่า older_than_s ออก แล้วคืนให้ผู้เรียกไปคืนโควตา/เครดิต
    (request ที่ยังทำงานอยู่จบภายใน gunicorn --timeout 120 เสมอ)"""
    import time as _t
    conn = get_conn()
    try:
        conn.execute("BEGIN IMMEDIATE")
        rows = [dict(r) for r in conn.execute(
            "SELECT * FROM pending_charges WHERE created_at < ?", (_t.time() - older_than_s,))]
        if rows:
            conn.executemany("DELETE FROM pending_charges WHERE id = ?", [(r["id"],) for r in rows])
        conn.commit()
        return rows
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
