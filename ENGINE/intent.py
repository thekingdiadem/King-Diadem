# ENGINE/intent.py
# KING DIADEM — Intent Detector
# ตรวจ intent จากภาษาไทย + อังกฤษ ครอบคลุม KING DIADEM use cases จริง

from __future__ import annotations


_PATTERNS: list[tuple[str, list[str]]] = [
    # ── Survival / crisis ──────────────────────────────────────────
    ("survival", [
        "หิว", "ไม่มีกิน", "ไม่มีเงิน", "ไม่มีที่อยู่", "ไม่มีที่พัก",
        "หมดแรง", "ล้มเลิก", "สิ้นหวัง", "หมดหวัง", "ไม่ไหวแล้ว",
        "รอดได้ไหม", "จะทำยังไง", "ทางออกไหน",
        "survive", "no food", "no money", "homeless", "crisis",
    ]),
    # ── Collapse / emotional overwhelm ────────────────────────────
    ("collapse", [
        "พัง", "ล้มเหลว", "พังหมดแล้ว", "ทุกอย่างพัง", "สิ้นสุด",
        "กลัว", "ตื่นตระหนก", "panic", "overwhelmed", "breakdown",
        "collapse", "ฉันไม่ได้เรื่อง", "ไม่มีทางออก",
    ]),
    # ── Business / financial ───────────────────────────────────────
    ("business", [
        "ธุรกิจ", "ขาดทุน", "กำไร", "ลงทุน", "ต้นทุน", "รายได้",
        "ลูกค้า", "ตลาด", "แข่งขัน", "scale", "pivot", "startup",
        "business", "revenue", "profit", "market", "investment",
    ]),
    # ── Risk / decision ────────────────────────────────────────────
    ("risk", [
        "เสี่ยง", "ควรทำไหม", "ตัดสินใจ", "เลือก", "ดีไหม",
        "โอกาส", "ผลกระทบ", "ความเสี่ยง",
        "risk", "decision", "should i", "worth it", "trade-off",
    ]),
    # ── Deploy / DevOps ────────────────────────────────────────────
    ("deploy", [
        "render", "deploy", "start command", "build command",
        "root directory", "web service", "gunicorn", "uvicorn",
        "dockerfile", "port", "env var", "environment variable",
    ]),
    # ── UI / frontend ─────────────────────────────────────────────
    ("ui", [
        "ui", "ux", "index.html", "button", "input", "chat",
        "หน้าเว็บ", "หน้าต่าง", "design", "css", "layout",
        "template", "frontend", "responsive", "mobile",
    ]),
    # ── Debug / error ─────────────────────────────────────────────
    ("debug", [
        "error", "traceback", "500", "404", "bug", "ไม่ทำงาน",
        "module not found", "import error", "cors", "fastapi",
        "flask", "exception", "crash", "ไม่ขึ้น", "ไม่ response",
    ]),
    # ── Auth ──────────────────────────────────────────────────────
    ("auth", [
        "login", "logout", "sign up", "register", "password",
        "oauth", "google login", "token", "session", "cookie",
        "เข้าสู่ระบบ", "สมัคร", "ยืนยันตัวตน",
    ]),
    # ── API / integration ─────────────────────────────────────────
    ("api", [
        "api", "endpoint", "fetch", "json", "request", "response",
        "http", "post", "get", "webhook", "integrate", "เชื่อมต่อ",
    ]),
    # ── Memory / history ──────────────────────────────────────────
    ("memory", [
        "จำ", "ลืม", "ประวัติ", "history", "session", "context",
        "remember", "recall", "cross-session",
    ]),
    # ── Help / general ─────────────────────────────────────────────
    ("help", [
        "help", "ช่วย", "ทำยังไง", "สอน", "อธิบาย", "บอก", "แนะนำ",
        "วิธี", "how to", "explain", "guide",
    ]),
]


def detect_intent(text: str) -> str:
    t = (text or "").casefold().strip()
    if not t:
        return "empty"

    # score แต่ละ intent
    scores: dict[str, int] = {}
    for intent, keywords in _PATTERNS:
        count = sum(1 for kw in keywords if kw.casefold() in t)
        if count:
            scores[intent] = count

    if not scores:
        return "general"

    # return intent ที่มี keyword match มากที่สุด
    return max(scores, key=lambda k: scores[k])


def detect_multi_intent(text: str, top_n: int = 3) -> list[str]:
    """Return top N intents — ใช้เมื่อ message มีหลาย context"""
    t = (text or "").casefold().strip()
    if not t:
        return ["empty"]

    scores: dict[str, int] = {}
    for intent, keywords in _PATTERNS:
        count = sum(1 for kw in keywords if kw.casefold() in t)
        if count:
            scores[intent] = count

    if not scores:
        return ["general"]

    ranked = sorted(scores, key=lambda k: scores[k], reverse=True)
    return ranked[:top_n]
