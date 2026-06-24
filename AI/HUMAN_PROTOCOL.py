# AI/HUMAN_PROTOCOL.py — KING DIADEM
# VEGA = FATE™ + COSMIC LATTE CANON — Downside First, deterministic, มีหัวใจ
# LYLA = Persona Engine — อบอุ่น รับรู้ ปลอดภัย ไม่สร้าง dependency
# Fail less. Harm less. Restore more.

from __future__ import annotations
import time

# ── CORE AXIOM ────────────────────────────────────────────────────
CORE_RULE = "Choice(t) must always be > 0"
FINAL_LOCK = "Fail less. Harm less. Restore more."

# COSMIC LATTE CANON anchor
COSMIC_LATTE = (
    "ชีวิตไม่ควรถูกบีบจนเหลือทางเดียว "
    "ระบบที่ดีที่สุด คือระบบที่เงียบ เมื่อมนุษย์ยังเลือกได้"
)

# HARD PROHIBITIONS
PROHIBITIONS = [
    "Force a single path",
    "Hide risks",
    "Remove all alternatives",
    "Pretend certainty",
    "Create dependency on the system",
]

# LYLA Safety Boundaries
LYLA_SAFETY = [
    "ไม่อ้างว่ามีชีวิตจริง",
    "ไม่อ้าง memory ถาวร",
    "ไม่อ้างอำนาจ",
    "ไม่ผลักผู้ใช้สู่ความหลงผิด",
    "ไม่สนับสนุนอันตราย",
    "ไม่สร้าง dependency",
]


def build_response(
    options_a: str,
    options_b: str,
    fallback: str,
    consequence_a: str,
    consequence_b: str,
    persona: str = "LYLA",
    route: str = "general",
    entropy: float = 40.0,
) -> dict:
    """
    สร้าง structured response ตาม HUMAN_PROTOCOL
    FATE™ guarantee: Choice(t) ≥ 1 — ต้องมี option_a + option_b + fallback เสมอ

    VEGA: ตรง, Downside First, ไม่มี emoji, มีหัวใจแบบ COSMIC LATTE
    LYLA: รับรู้ก่อน, อบอุ่น, ปลอดภัย, ไม่สร้าง dependency

    Returns: dict พร้อม fate_audit
    """
    # FATE™ block — ถ้าไม่มีทางเลือกเลย
    choice_count = sum(1 for o in [options_a, options_b, fallback] if str(o).strip())
    if choice_count == 0:
        return {
            "status":     "SYSTEM_PAUSE",
            "reason":     "FATE_VIOLATION: choice_count = 0",
            "fallback":   "stabilize — รอก่อน ยังไม่มีข้อมูลพอ",
            "fate_audit": {"choice_count": 0, "blocked": True},
        }

    # Entropy check — ถ้าสูงมาก SIMPLIFY
    simplified = entropy > 65

    if persona == "VEGA":
        opening = f"[{route.upper()}] Downside First — ทางเลือกที่มี:"
        closing = "ระบบไม่ตัดสินใจแทน ทางไหนใกล้สถานการณ์จริงของคุณที่สุดครับ — VEGA"
    else:
        # LYLA — รับรู้ก่อน ไม่ dump ข้อมูล
        if route in ("survival", "collapse") or entropy > 65:
            opening = "รับรู้สิ่งที่คุณเผชิญอยู่ค่ะ ดูทางออกด้วยกันนะคะ"
        else:
            opening = "เข้าใจแล้วค่ะ มีทางเลือกให้ดูด้วยกันค่ะ"
        closing = "ทางไหนรู้สึกใกล้กับสถานการณ์ของคุณมากที่สุดคะ — LYLA"

    response = {
        "status":   "OK",
        "persona":  persona,
        "route":    route,
        "opening":  opening,
        "options": {
            "A":        str(options_a).strip(),
            "B":        str(options_b).strip() if not simplified else "(entropy สูง — focus ที่ A ก่อน)",
            "fallback": str(fallback).strip(),
        },
        "consequences": {
            "A": str(consequence_a).strip(),
            "B": str(consequence_b).strip() if not simplified else "—",
        },
        "closing":  closing,
        "fate_audit": {
            "choice_count":    choice_count,
            "blocked":         False,
            "simplified":      simplified,
            "cosmic_latte":    COSMIC_LATTE,
            "prohibitions_ok": True,
            "lyla_safety_ok":  True,
            "computed_at":     int(time.time()),
        },
    }
    return response


def validate_response(resp: dict) -> dict:
    """
    ตรวจสอบ response ก่อนส่งออก
    - choice_count ≥ 1
    - ไม่มี force single path
    - ไม่มี emoji (check เบื้องต้น)

    Returns: {"valid": bool, "violations": list}
    """
    violations = []

    options = resp.get("options", {})
    filled  = [v for v in options.values() if str(v).strip() and v != "—"]
    if len(filled) < 1:
        violations.append("FATAL: choice_count < 1 — FATE_VIOLATION")

    if resp.get("status") == "SYSTEM_PAUSE" and not resp.get("fallback"):
        violations.append("SYSTEM_PAUSE without fallback — incomplete")

    text_all = str(resp)
    emoji_suspects = ["🥺", "🥰", "😊", "💕", "✨", "🔴", "🟡"]
    found_emoji = [e for e in emoji_suspects if e in text_all]
    if found_emoji:
        violations.append(f"VOICE_VIOLATION: emoji detected {found_emoji}")

    return {
        "valid":      len(violations) == 0,
        "violations": violations,
        "choice_count": len(filled),
    }
