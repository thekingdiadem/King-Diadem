# ENGINE/brain.py
"""
KING DIADEM — Brain v2.0
Route-aware orchestration layer
ต่อ intent → risk → intervention → build_reply ครบ loop
"""

from __future__ import annotations
from typing import Optional

from .dicision import build_reply   # ไฟล์จริงสะกดว่า dicision.py (ไม่มี decision.py)
from .intent   import detect_intent
from .memory   import append_turn, get_state, snapshot
from .risk     import evaluate_risk

# ── Optional integrations — safe import ──────────────────────────
try:
    from ENGINE.intervention_engine import intervene as _intervene
    _INTERVENTION_LOADED = True
except ImportError:
    _INTERVENTION_LOADED = False

try:
    from ENGINE.survival_advisor import advise as _advise
    _SURVIVAL_LOADED = True
except ImportError:
    _SURVIVAL_LOADED = False


# ── Route keywords — Thai + English ──────────────────────────────
_SURVIVAL_KW = (
    "หิว", "เงิน", "รถเสีย", "หลงทาง", "อันตราย", "ช่วย",
    "ฉุกเฉิน", "พัง", "หมด", "ไม่มี", "กลัว", "เจ็บ",
    "urgent", "help", "emergency", "broke", "lost", "danger",
)
_BUSINESS_KW = (
    "ธุรกิจ", "ลงทุน", "กำไร", "ขาดทุน", "ต้นทุน", "ราคา",
    "ตลาด", "ขาย", "ลูกค้า", "รายได้", "งบ",
    "business", "invest", "profit", "revenue", "market",
)
_LIFE_KW = (
    "ความสัมพันธ์", "ครอบครัว", "เพื่อน", "ความรัก", "ชีวิต",
    "ทิศทาง", "เป้าหมาย", "อนาคต",
    "relationship", "family", "life", "goal", "direction",
)
_WORLD_KW = (
    "การเมือง", "เศรษฐกิจ", "โลก", "ข่าว", "สงคราม", "ภัยพิบัติ",
    "politics", "economy", "world", "news", "war", "disaster",
)

def _detect_route(text: str) -> str:
    t = text.lower()
    if any(k in t for k in _SURVIVAL_KW):
        return "survival"
    if any(k in t for k in _BUSINESS_KW):
        return "business"
    if any(k in t for k in _LIFE_KW):
        return "life"
    if any(k in t for k in _WORLD_KW):
        return "world"
    return "general"


# ── Main think() ──────────────────────────────────────────────────
def think(
    message:    str,
    mode:       str = "chat",
    session_id: str = "default",
    seed:       str = "",
    context:    Optional[dict] = None,   # optional: {money, food, energy, ...}
) -> dict:

    session_id = (session_id or "default").strip() or "default"
    mode       = (mode       or "chat").strip()    or "chat"
    seed       = (seed       or "").strip()

    state      = get_state(session_id)
    state.mode = mode
    if seed:
        state.seed = seed

    msg = (message or "").strip()

    # ── Empty input ───────────────────────────────────────────────
    if not msg:
        return {
            "reply":      "พิมพ์ข้อความมาได้เลย",
            "actions":    ["ใส่ข้อความ", "กดส่ง", "หรือกด + เพื่อเปิด context"],
            "context":    snapshot(session_id),
            "intent":     "empty",
            "route":      "general",
            "risk":       {"score": 0, "level": "low", "pause": False},
            "mode":       mode,
            "seed":       state.seed,
            "session_id": session_id,
            "history":    snapshot(session_id),
        }

    append_turn(session_id, "user", msg)

    # ── Core analysis ─────────────────────────────────────────────
    intent = detect_intent(msg)
    risk   = evaluate_risk(msg)
    route  = _detect_route(msg)

    # ── Intervention check (survival route หรือ risk สูง) ─────────
    intervention_report = None
    if _INTERVENTION_LOADED and (route == "survival" or risk.get("score", 0) >= 60):
        risk_level = risk.get("level", "moderate")
        intervention_report = _intervene(risk_level, context or {})

    # ── Survival advisor (survival route) ─────────────────────────
    survival_report = None
    if _SURVIVAL_LOADED and route == "survival" and context:
        survival_report = _advise(context)

    # ── Build reply ───────────────────────────────────────────────
    reply_pack = build_reply(
        message  = msg,
        intent   = intent,
        risk     = risk,
        history  = snapshot(session_id),
        seed     = state.seed,
        mode     = mode,
    )

    append_turn(session_id, "assistant", reply_pack["reply"])

    result = {
        "reply":      reply_pack["reply"],
        "actions":    reply_pack["actions"],
        "context":    reply_pack["context"],
        "intent":     intent,
        "route":      route,
        "risk":       reply_pack["risk"],
        "mode":       reply_pack["mode"],
        "seed":       state.seed,
        "session_id": session_id,
        "history":    snapshot(session_id),
    }

    # เพิ่ม optional reports ถ้ามี
    if intervention_report:
        result["intervention"] = intervention_report
    if survival_report:
        result["survival"]     = survival_report

    return result
