from __future__ import annotations

import re


# ──────────────────────────────────────────────────────────────
# FIX: คำภาษาอังกฤษ (a-z0-9) จะ match แบบ word-boundary
# กันปัญหา "render" ไป match ใน "king-diadem.onrender.com"
# (เดิม `"render" in t` → True เสมอเมื่อมี URL .onrender.com)
#
# คำไทยใช้ substring match แบบเดิม เพราะภาษาไทยไม่มี word boundary
# มาตรฐานแบบ regex (\b ใช้กับ a-zA-Z0-9 เท่านั้น)
# ──────────────────────────────────────────────────────────────
_RE_CACHE: dict[str, re.Pattern] = {}


def _matches(text: str, keyword: str) -> bool:
    if re.fullmatch(r"[a-z0-9\- ]+", keyword):
        pattern = _RE_CACHE.get(keyword)
        if pattern is None:
            pattern = re.compile(rf"\b{re.escape(keyword)}\b")
            _RE_CACHE[keyword] = pattern
        return pattern.search(text) is not None

    return keyword in text


def evaluate_risk(text: str) -> dict:
    t = (text or "").casefold()

    score = 0

    if any(_matches(t, k) for k in (
        "error", "พัง", "ล่ม", "traceback", "exception",
        "module not found", "500", "502", "503",
    )):
        score += 2

    if any(_matches(t, k) for k in (
        "deploy", "render", "github pages", "cors",
        "uvicorn", "fastapi", "start command",
    )):
        score += 1

    if any(_matches(t, k) for k in (
        "อดข้าว", "ไม่มีเงิน", "เงินหมด", "ตาย",
        "kill myself", "suicide", "ทำร้ายตัวเอง",
    )):
        score += 3

    if any(_matches(t, k) for k in (
        "now", "ด่วน", "เดี๋ยวนี้", "ทันที", "immediately", "urgent",
    )):
        score += 1

    if score >= 4:
        level = "high"
    elif score >= 2:
        level = "medium"
    else:
        level = "low"

    return {
        "score": score,
        "level": level,
        "pause": level == "high",
    }
