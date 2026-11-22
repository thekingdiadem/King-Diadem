"""
core/admin_access.py — สิทธิ์ผู้ดูแล · บันทึกว่าใครทำอะไร · สถานะความปลอดภัยของบัญชีผู้ดูแล

ที่มา: เจ้าของโปรเจกต์ใส่ ADMIN_EMAILS 5 อีเมล (ของตัวเอง 4 + ของแม่ 1) เพื่อกันมือถือหาย
ทุกอีเมลในนั้นเห็นทุกอย่าง (รายได้ · รายงาน · ประโยคที่ผู้ใช้แนบมา) จึงต้องมี
  1. สิทธิ์ "ติดป้ายอย่างเดียว" (LABELER_EMAILS) — คนช่วยติดป้ายไม่ต้องเห็นรายได้หรือรายงานอื่น
  2. บันทึกการกระทำของผู้ดูแลในฐานข้อมูล (Turso ไม่หายตอน deploy) — ถ้าบัญชีหลุดย้อนดูได้ว่าใครทำอะไรเมื่อไร
  3. สถานะ 2FA ของทุกอีเมลผู้ดูแล — มือถือหายแล้วคนเก็บได้เข้าหน้าผู้ดูแลได้ทันที ถ้าไม่เปิด 2FA

ไม่เก็บ: ประโยคของผู้ใช้ในบันทึก (เก็บแค่เลขรายการและป้าย) · รหัสผ่าน · IP
"""
from __future__ import annotations

import os
import re
import threading
import time

ROLES = ("admin", "labeler")
ACTIONS = ("label", "export", "view_reports", "view_security")
KEEP_DAYS = 365
_CTRL = re.compile(r"[\x00-\x1f\x7f]")
_lock = threading.Lock()


def _emails(var: str) -> set[str]:
    return {e.strip().lower() for e in os.getenv(var, "").split(",") if e.strip()}


def role(email, admin_emails: set[str] | None = None, labeler_emails: set[str] | None = None) -> str | None:
    """admin > labeler > None · ผู้ดูแลทำทุกอย่างที่คนติดป้ายทำได้"""
    if not email:
        return None
    e = str(email).strip().lower()
    admins = _emails("ADMIN_EMAILS") if admin_emails is None else admin_emails
    labelers = _emails("LABELER_EMAILS") if labeler_emails is None else labeler_emails
    if e in admins:
        return "admin"
    if e in labelers:
        return "labeler"
    return None


def can_label(email, admin_emails=None, labeler_emails=None) -> bool:
    return role(email, admin_emails, labeler_emails) in ("admin", "labeler")


def mask(email: str) -> str:
    """แสดงอีเมลบนหน้าจอแบบไม่เต็ม (กันคนแอบมองจอ) — boss@gmail.com → bo•••@gmail.com"""
    e = str(email or "")
    name, at, dom = e.partition("@")
    if not at:
        return "•••"
    return (name[:2] + "•••" if len(name) > 2 else name[:1] + "•••") + "@" + dom


# ── บันทึกการกระทำ ────────────────────────────────────────────────────────────

def _conn():
    from DATABASE.db import get_conn
    return get_conn()


def _ensure(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS admin_actions (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            ts     REAL NOT NULL,
            who    TEXT NOT NULL,
            role   TEXT NOT NULL,
            action TEXT NOT NULL,
            detail TEXT NOT NULL DEFAULT ''
        )
    """)
    conn.commit()


def record(who, who_role, action, detail="") -> bool:
    """บันทึกหนึ่งการกระทำ · พลาดแล้วงานหลักต้องไม่ล้ม (คืน False แทน)"""
    if action not in ACTIONS or who_role not in ROLES or not who:
        return False
    detail = _CTRL.sub(" ", str(detail or ""))[:200]
    try:
        with _lock:
            conn = _conn()
            try:
                _ensure(conn)
                conn.execute("INSERT INTO admin_actions (ts, who, role, action, detail) VALUES (?,?,?,?,?)",
                             (time.time(), str(who).lower(), who_role, action, detail))
                conn.commit()
            finally:
                conn.close()
        return True
    except Exception as e:
        print(f"⚠ admin_actions: {type(e).__name__}")
        return False


def recent(limit: int = 50) -> list:
    limit = max(1, min(int(limit or 50), 500))
    conn = _conn()
    try:
        _ensure(conn)
        rows = conn.execute("SELECT ts, who, role, action, detail FROM admin_actions ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    finally:
        conn.close()
    return [{"ts": r[0], "who": mask(r[1]), "role": r[2], "action": r[3], "detail": r[4]} for r in rows]


def prune(now: float | None = None) -> int:
    """ลบบันทึกเกิน 1 ปี (housekeeping)"""
    cut = (now or time.time()) - KEEP_DAYS * 86400
    with _lock:
        conn = _conn()
        try:
            _ensure(conn)
            n = conn.execute("DELETE FROM admin_actions WHERE ts < ?", (cut,)).rowcount
            conn.commit()
        finally:
            conn.close()
    return n


# ── สถานะความปลอดภัย ──────────────────────────────────────────────────────────

def security_status(twofa_on, user_exists, admin_emails=None, labeler_emails=None) -> dict:
    """ทุกอีเมลที่มีสิทธิ์: สมัครแล้วหรือยัง · เปิด 2FA หรือยัง · คำแนะนำที่ต้องทำ
    twofa_on / user_exists = ฟังก์ชันจากระบบหลัก (ส่งเข้ามา จะได้ทดสอบได้)
    user_exists ที่ส่งมาควรนับเฉพาะบัญชีที่พิสูจน์อีเมลแล้ว (เคยเข้าด้วย Google) — สิทธิ์ผู้ดูแลต้องใช้แบบนั้น"""
    admins = sorted(_emails("ADMIN_EMAILS") if admin_emails is None else admin_emails)
    labelers = sorted((_emails("LABELER_EMAILS") if labeler_emails is None else labeler_emails) - set(admins))
    people = []
    for r, group in (("admin", admins), ("labeler", labelers)):
        for e in group:
            try:
                exists = bool(user_exists(e))
            except Exception:
                exists = False
            try:
                tfa = bool(twofa_on(e)) if exists else False
            except Exception:
                tfa = False
            if not exists:
                todo = "ยังใช้สิทธิ์ไม่ได้ — ต้องเข้าสู่ระบบด้วย Google ด้วยอีเมลนี้ 1 ครั้ง (พิสูจน์ว่าเป็นเจ้าของอีเมลจริง)"
            elif not tfa:
                todo = "ยังไม่เปิดการยืนยันสองขั้น (2FA) — ถ้ามือถือหาย คนเก็บได้เข้าหน้าผู้ดูแลได้ทันที"
            else:
                todo = ""
            people.append({"email": mask(e), "role": r, "verified": exists, "twofa": tfa, "todo": todo})
    weak = [p for p in people if p["todo"]]
    return {"people": people, "ok": not weak and bool(admins), "weak": len(weak),
            "admins": len(admins), "labelers": len(labelers)}
