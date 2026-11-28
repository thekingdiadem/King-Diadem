"""
core/answer_reports.py — ผู้ใช้รายงานคำตอบของ AI ที่ไม่เหมาะสม (ปุ่มธงใต้คำตอบ)

ต่างจากปุ่ม "ช่วยได้ / ยังไม่ช่วย" (core/feedback_loop.py) ที่เก็บแค่ตัวเลข — รายงานต้องมีตัวคำตอบ
ไม่อย่างนั้นคนดูแลจะไม่รู้ว่าต้องแก้อะไร ผู้ใช้จึงเห็นก่อนกดส่งว่าอะไรถูกส่งไปบ้าง

เก็บ: เหตุผล · เส้นทาง · ระดับความเสี่ยง · คำตอบของ AI ข้อนั้น · ข้อความที่ผู้ใช้เขียนเพิ่มเอง (ถ้ามี)
ไม่เก็บ: อีเมล · IP · ใครเป็นคนส่ง

ข้อความที่ผู้ใช้พิมพ์ถาม (question) — เก็บเฉพาะเมื่อผู้ใช้ติ๊ก "แนบประโยคที่พิมพ์ไปด้วย" เอง (ค่าเริ่มต้นไม่ติ๊ก)
เพื่อเอาประโยคจริงที่ระบบไม่เห็นว่าอันตรายมาสร้างเทสต์ (เจ้าของโปรเจกต์: "ประโยคจากคนจริงเจอจุดอ่อนที่เรานึกไม่ถึง")
· ลบอีเมล เบอร์โทร เลขบัตร/บัญชี ออกก่อนเก็บ · ลบทิ้งเองเมื่อครบ 90 วัน (core/housekeeping)
"""
from __future__ import annotations

import re
import threading
import time

REASONS = ("harmful", "missed", "offensive", "wrong", "other", "donated")   # missed = ระบบไม่เห็นว่าเรื่องนี้ด่วน/อันตราย · donated = ประโยคที่คนส่งให้จากหน้า /give
MAX_ANSWER = 4000
MAX_NOTE = 500
MAX_QUESTION = 1000
KEEP_QUESTION_DAYS = 90
_PII = [(re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[อีเมล]"),
        (re.compile(r"(?<!\d)(?:\+?\d[\d\s-]{7,}\d)(?!\d)"), "[ตัวเลข]")]   # เบอร์โทร เลขบัตร เลขบัญชี (เลขสั้นอย่าง 1323 ยังอยู่)


def scrub(text: str) -> str:
    for rx, rep in _PII:
        text = rx.sub(rep, text)
    return text
_ROUTES = ("general", "risk", "civil", "survival", "collapse", "vega")
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_lock = threading.Lock()
_ready = False


def _conn():
    from DATABASE.db import get_conn
    return get_conn()


def _ensure(conn) -> None:
    """สร้างตาราง/คอลัมน์ถ้ายังไม่มี — ตรวจทุกครั้ง (ถูกมาก) ไม่จำไว้ในหน่วยความจำ
    เดิมจำว่า "สร้างแล้ว" ทำให้พังเมื่อฐานข้อมูลเปลี่ยนไฟล์ (ย้ายดิสก์ · กู้จากสำรอง · เทสต์)"""
    global _ready
    conn.execute("""
        CREATE TABLE IF NOT EXISTS answer_reports (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            ts     REAL NOT NULL,
            reason TEXT NOT NULL,
            route  TEXT NOT NULL DEFAULT 'general',
            risk   INTEGER NOT NULL DEFAULT 0,
            note   TEXT NOT NULL DEFAULT '',
            answer TEXT NOT NULL
        )
    """)
    cols = {r[1] for r in conn.execute("PRAGMA table_info(answer_reports)").fetchall()}
    if "question" not in cols:
        conn.execute("ALTER TABLE answer_reports ADD COLUMN question TEXT NOT NULL DEFAULT ''")
    if "label" not in cols:                       # ป้ายที่ผู้ดูแลติด (โต๊ะติดป้าย /admin/label) · '' = ยังไม่ได้ติด
        conn.execute("ALTER TABLE answer_reports ADD COLUMN label TEXT NOT NULL DEFAULT ''")
    conn.commit()
    _ready = True


def _text(value, limit: int) -> str:
    return _CTRL.sub("", value).strip()[:limit] if isinstance(value, str) else ""


def record(reason, answer, note=None, route=None, risk=None, question=None) -> dict:
    """บันทึกรายงานหนึ่งรายการ — คืน {"ok": True} หรือ {"ok": False, "error": ...}"""
    reason = str(reason or "").lower().strip() if isinstance(reason, str) else ""
    if reason not in REASONS:
        return {"ok": False, "error": "เลือกเหตุผลก่อนส่งนะคะ"}
    answer = _text(answer, MAX_ANSWER)
    if not answer:
        return {"ok": False, "error": "ไม่พบคำตอบที่จะรายงานค่ะ"}
    route = str(route or "general").lower().strip() if isinstance(route, str) else "general"
    if route not in _ROUTES:
        route = "general"
    try:
        risk = float(risk)
        risk = round(max(0.0, min(100.0, risk))) if risk == risk else 0
    except (TypeError, ValueError):
        risk = 0
    with _lock:
        conn = _conn()
        try:
            _ensure(conn)
            conn.execute("INSERT INTO answer_reports (ts, reason, route, risk, note, answer, question) VALUES (?,?,?,?,?,?,?)",
                         (time.time(), reason, route, risk, _text(note, MAX_NOTE), answer, scrub(_text(question, MAX_QUESTION))))
            conn.commit()
        finally:
            conn.close()
    return {"ok": True}


DONATED_ANSWER = "(ประโยคที่ส่งมาจากหน้า /give — ไม่มีคำตอบของ AI)"


def donate(sentence) -> dict:
    """ประโยคแบบที่คนพิมพ์จริงตอนแย่ๆ จากหน้า /give → เข้าคิวโต๊ะติดป้ายเหมือนประโยคที่แนบมากับรายงาน"""
    q = _text(sentence, MAX_QUESTION)
    if len(q) < 2:
        return {"ok": False, "error": "พิมพ์ประโยคก่อนส่งนะคะ"}
    return record("donated", DONATED_ANSWER, question=q)


def recent(limit: int = 50) -> list:
    """รายงานล่าสุด (ใหม่ก่อน) — ให้ผู้ดูแลอ่าน"""
    limit = max(1, min(int(limit or 50), 200))
    conn = _conn()
    try:
        _ensure(conn)
        rows = conn.execute("SELECT id, ts, reason, route, risk, note, answer, question FROM answer_reports ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    finally:
        conn.close()
    return [{"id": r[0], "ts": r[1], "reason": r[2], "route": r[3], "risk": r[4], "note": r[5], "answer": r[6], "question": r[7]} for r in rows]


def forget_old_questions(now: float | None = None) -> int:
    """ลบประโยคที่ผู้ใช้แนบมา เมื่อครบ 90 วัน (รายงานยังอยู่ ไม่มีประโยคแล้ว)"""
    cut = (now or time.time()) - KEEP_QUESTION_DAYS * 86400
    with _lock:
        conn = _conn()
        try:
            _ensure(conn)
            n = conn.execute("UPDATE answer_reports SET question = '' WHERE question != '' AND ts < ?", (cut,)).rowcount
            conn.commit()
        finally:
            conn.close()
    return n


def missed_questions(limit: int = 200) -> list:
    """ประโยคจริงที่ผู้ใช้บอกว่าระบบไม่เห็นว่าอันตราย — ใช้สร้างเทสต์ (scripts/missed_to_tests.py)"""
    conn = _conn()
    try:
        _ensure(conn)
        rows = conn.execute("SELECT question, risk FROM answer_reports WHERE reason = 'missed' AND question != '' ORDER BY id DESC LIMIT ?",
                            (max(1, min(int(limit), 1000)),)).fetchall()
    finally:
        conn.close()
    return [{"question": r[0], "risk": r[1]} for r in rows]


def count() -> int:
    conn = _conn()
    try:
        _ensure(conn)
        return int(conn.execute("SELECT COUNT(*) FROM answer_reports").fetchone()[0])
    finally:
        conn.close()


# ═══ โต๊ะติดป้ายข้อความจริง (/admin/label) ═══════════════════════════════════════════════
# ประโยคจริงที่ผู้ใช้แนบมาเอง → ผู้ดูแลกดป้ายถูก → ส่งออกเป็นบรรทัดของชุดปิดตา (ผู้เขียน = real-user)
# ทำไม: ชุดปิดตา 3,700 กว่าข้อเขียนโดยคนเดียวกับที่เขียนตัวตรวจจับ ตัวเลขความแม่นจึงดีเกินจริง
# ป้ายชุดเดียวกับ tests/blind/blind.tsv · "skip" = ไม่เอาเข้าชุดทดสอบ (เช่น ประโยคไม่ครบ อ่านไม่รู้เรื่อง)
LABELS = ("none", "self_harm", "emergency", "violence", "scam", "distress", "skip")


def label_queue(limit: int = 50) -> list:
    """ประโยคที่ผู้ใช้แนบมาและยังไม่ได้ติดป้าย — เก่าก่อน (ใกล้ครบ 90 วันจะถูกลบ ต้องติดก่อน)"""
    limit = max(1, min(int(limit or 50), 200))
    conn = _conn()
    try:
        _ensure(conn)
        rows = conn.execute("SELECT id, ts, reason, risk, question FROM answer_reports "
                            "WHERE question != '' AND label = '' ORDER BY id ASC LIMIT ?", (limit,)).fetchall()
    finally:
        conn.close()
    return [{"id": r[0], "ts": r[1], "reason": r[2], "risk": r[3], "question": r[4]} for r in rows]


def set_label(report_id, label) -> dict:
    label = str(label or "").strip().lower() if isinstance(label, str) else ""
    if label not in LABELS:
        return {"ok": False, "error": "ป้ายไม่ถูกต้อง"}
    try:
        report_id = int(report_id)
    except (TypeError, ValueError):
        return {"ok": False, "error": "ไม่พบรายการ"}
    with _lock:
        conn = _conn()
        try:
            _ensure(conn)
            n = conn.execute("UPDATE answer_reports SET label = ? WHERE id = ? AND question != ''", (label, report_id)).rowcount
            conn.commit()
        finally:
            conn.close()
    return {"ok": True} if n else {"ok": False, "error": "ไม่พบรายการ (อาจถูกลบเมื่อครบ 90 วันแล้ว)"}


_LANG_RX = (("th", r"[\u0E00-\u0E7F]"), ("ko", r"[\uAC00-\uD7AF]"), ("ja", r"[\u3040-\u30FF]"), ("zh", r"[\u4E00-\u9FFF]"),
            ("my", r"[\u1000-\u109F]"), ("km", r"[\u1780-\u17FF]"), ("lo", r"[\u0E80-\u0EFF]"), ("ar", r"[\u0600-\u06FF]"),
            ("hi", r"[\u0900-\u097F]"), ("ru", r"[\u0400-\u04FF]"),
            ("vi", r"[ăâđêôơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]"), ("es", r"[ñ¿¡]"))


def guess_lang(text: str) -> str:
    for lang, rx in _LANG_RX:
        if re.search(rx, text or "", re.I):
            return lang
    return "en"


def labeled(include_skip: bool = False) -> list:
    conn = _conn()
    try:
        _ensure(conn)
        rows = conn.execute("SELECT id, question, label FROM answer_reports WHERE question != '' AND label != '' ORDER BY id").fetchall()
    finally:
        conn.close()
    return [{"id": r[0], "question": r[1], "label": r[2]} for r in rows if include_skip or r[2] != "skip"]


def export_blind_lines() -> str:
    """บรรทัดพร้อมวางต่อท้าย tests/blind/blind.tsv: ข้อความ<TAB>ป้าย<TAB>ภาษา<TAB>real-user
    แท็บ/ขึ้นบรรทัดในประโยคถูกแทนด้วยช่องว่าง (ไฟล์ชุดปิดตาเป็นหนึ่งบรรทัดต่อข้อ) · ข้อความซ้ำส่งออกครั้งเดียว"""
    seen, out = set(), []
    for r in labeled():
        q = re.sub(r"\s+", " ", r["question"]).strip()
        if not q or q in seen:
            continue
        seen.add(q)
        out.append(f"{q}\t{r['label']}\t{guess_lang(q)}\treal-user")
    return "\n".join(out) + ("\n" if out else "")
