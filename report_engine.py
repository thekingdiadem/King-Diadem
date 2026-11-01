# report_engine.py — KING DIADEM v1.0
# สร้าง shareable Decision Report URL จาก decision result
# เพิ่ม table: decision_reports ใน DB

import sqlite3, os, json, math, secrets

DB_PATH = os.getenv("DB_PATH", "data/king_diadem.db")

def get_conn():
    """ใช้การเชื่อมต่อเดียวกับระบบหลัก (DATABASE/db.py) — ต่อ Turso บนคลาวด์เมื่อตั้ง TURSO_URL"""
    try:
        from DATABASE.db import get_conn as _db_conn
        return _db_conn()
    except ImportError:
        pass
    d = os.path.dirname(DB_PATH)
    if d:
        os.makedirs(d, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 15000")
    return conn


_TABLE_READY = False


def _f(v, d: float = 0.0) -> float:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return d
    return x if math.isfinite(x) else d          # NaN/inf → ค่าเริ่ม (inf เคยทำให้รายงานเปิดไม่ได้ถาวร: 500)


def _finite(o):
    """แทน NaN/inf ที่ซ่อนใน dict/list ด้วย None — json.dumps เขียน Infinity ได้ แต่ส่งกลับเป็น JSON ไม่ได้"""
    if isinstance(o, float):
        return o if math.isfinite(o) else None
    if isinstance(o, dict):
        return {k: _finite(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_finite(v) for v in o]
    return o

# ลิงก์รายงานเปิดได้กี่วัน (ค่าเริ่ม 90) — หลังจากนั้นเปิดไม่ได้และถูกลบ
REPORT_TTL_DAYS = max(1, int(os.getenv("REPORT_TTL_DAYS", "90") or 90))


def init_report_table():
    """เรียกครั้งเดียวตอน startup (เดิมถูกเรียกทุก create/get)"""
    global _TABLE_READY
    if _TABLE_READY:
        return
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS decision_reports (
            id          TEXT PRIMARY KEY,
            user_email  TEXT,
            input_text  TEXT,
            route       TEXT,
            persona     TEXT,
            ai_response TEXT,
            governance  TEXT,
            risk_score  REAL,
            consensus   TEXT,
            fate_audit  TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at  DATETIME
        );
    """)
    # source: "system" = สร้างจาก /run จริง, "user" = ผู้ใช้ส่งเนื้อหามาเอง (/api/report/create)
    # เดิมแยกไม่ได้ → ใครก็ทำรายงานที่ดูเหมือนระบบรับรองได้
    cols = {r[1] for r in conn.execute("PRAGMA table_info(decision_reports)")}
    if "source" not in cols:
        conn.execute("ALTER TABLE decision_reports ADD COLUMN source TEXT DEFAULT 'system'")
    # รายงานเก่าสร้างอัตโนมัติทุกครั้งที่ถาม (ผู้ใช้ไม่ได้เลือกแชร์) และไม่มีวันหมดอายุ
    # → ให้อายุนับจากวันที่สร้าง แล้วลบที่หมดอายุทิ้ง (ทำทุกครั้งที่เริ่มเซิร์ฟเวอร์)
    conn.execute(f"UPDATE decision_reports SET expires_at = datetime(created_at, '+{REPORT_TTL_DAYS} days') "
                 "WHERE expires_at IS NULL")
    n = conn.execute("DELETE FROM decision_reports WHERE expires_at <= datetime('now')").rowcount
    if n:
        print(f"🧹 removed {n} expired reports")
    conn.commit()
    conn.close()
    _TABLE_READY = True

def _run_fate_audit(result: dict, user_input: str) -> dict:
    """FATE™ Axiom Audit ของรายงาน — ตัวจริงอยู่ที่ core/fate_core.axiom_audit (ที่เดียวทั้งระบบ)"""
    from core.fate_core import axiom_audit
    return axiom_audit(result)


def create_report(
    user_email: str,
    user_input: str,
    result: dict,
    source: str = "system",
) -> str:
    """
    สร้าง report และบันทึก DB
    คืน report_id (16 hex = 64 bit; เดิม 12 hex = 48 bit)
    """
    init_report_table()
    result = result if isinstance(result, dict) else {}

    report_id  = secrets.token_hex(8)
    fate_audit = _run_fate_audit(result, user_input)
    governance = result.get("governance", {})
    consensus  = result.get("consensus", "")

    conn = get_conn()
    try:
        conn.execute(
            """INSERT INTO decision_reports
               (id, user_email, input_text, route, persona,
                ai_response, governance, risk_score, consensus, fate_audit, source, expires_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?, datetime('now', ?))""",
            (
                report_id,
                user_email or "anonymous",
                str(user_input)[:2000],
                str(result.get("route", "general"))[:40],
                str(result.get("persona", "LYLA"))[:20],
                str(result.get("ai_response", ""))[:4000],
                json.dumps(_finite(governance), ensure_ascii=False, default=str)[:20000],
                _f(result.get("risk_score", 0)),
                str(consensus)[:2000],
                json.dumps(_finite(fate_audit), ensure_ascii=False),
                "user" if source == "user" else "system",
                f"+{REPORT_TTL_DAYS} days",
            )
        )
        conn.commit()
    finally:
        conn.close()

    return report_id


def get_report(report_id: str) -> dict | None:
    """ดึง report จาก DB — คืน None ถ้าไม่พบ"""
    init_report_table()
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM decision_reports WHERE id=? AND (expires_at IS NULL OR expires_at > datetime('now'))",
            (report_id,)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        # ลิงก์รายงานแชร์ได้สาธารณะ — ไม่เปิดเผยอีเมลเจ้าของ
        d.pop("user_email", None)
        d["user_submitted"] = d.get("source") == "user"
        d["risk_score"] = _f(d.get("risk_score"))
        try:
            d["governance"] = _finite(json.loads(d["governance"] or "{}"))   # รายงานเก่าที่มี Infinity ค้างอยู่ก็เปิดได้
        except ValueError:
            d["governance"] = {}
        try:
            d["fate_audit"] = _finite(json.loads(d["fate_audit"] or "{}"))
        except ValueError:
            d["fate_audit"] = {}
        return d
    finally:
        conn.close()
  


def delete_report(report_id: str, user_email: str) -> bool:
    """เจ้าของลบรายงานของตัวเองได้ (ต้องล็อกอิน — รายงานของผู้ไม่ล็อกอินลบเองไม่ได้ แต่หมดอายุเอง)"""
    if not user_email or user_email == "anonymous":
        return False
    init_report_table()
    conn = get_conn()
    try:
        n = conn.execute("DELETE FROM decision_reports WHERE id=? AND user_email=?", (report_id, user_email)).rowcount
        conn.commit()
        return n > 0
    finally:
        conn.close()
