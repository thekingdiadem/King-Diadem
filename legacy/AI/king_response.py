# AI/king_response.py — KING DIADEM
# KING = governance observer / voice ที่ผู้ใช้ได้ยิน
# VEGA = FATE™ + COSMIC LATTE CANON — logic deterministic ที่มีหัวใจ, ไม่ใช้ emoji
# LYLA = Persona Engine — อบอุ่น, รับรู้, เปิดทางเลือก, ฟังก่อนวิเคราะห์
# Fail less. Harm less. Restore more.

from AI.galaxy_tree import expand_options

# ── ROUTE CONTEXT — ข้อความสั้น ไม่ใช้ emoji ──────────────────────
_ROUTE_CONTEXT: dict[str, str] = {
    "survival": "[SURVIVAL] สถานการณ์ต้องการทางออกทันที — ก่อนวิเคราะห์ ต้องรอด",
    "collapse": "[COLLAPSE] ความเสี่ยงสูงวิกฤต — ลดความเสียหายก่อน อย่างอื่นรอได้",
    "risk":     "[RISK] ระดับความเสี่ยงสูงกว่าปกติ — ระมัดระวัง Downside ก่อน",
    "general":  "[GENERAL] วิเคราะห์ตามบริบท",
    "civil":    "[CIVIL] บริบทสังคม/งาน — มองผลระยะยาวด้วย",
    "vega":     "[VEGA] Strategic analysis — รับฟังก่อน ไม่เร่งผลัก",
}

_RISK_TEXT: dict[str, str] = {
    "safe":   "ความเสี่ยงต่ำ",
    "low":    "ความเสี่ยงพอรับได้",
    "medium": "ความเสี่ยงปานกลาง",
    "high":   "ความเสี่ยงสูง — ระวัง",
}


# ── VEGA RESPONSE — FATE™ + COSMIC LATTE ─────────────────────────
# ตรง, deterministic, ไม่ใช้ emoji, มีหัวใจ แต่ไม่น่ารัก
def _vega_response(
    question: str,
    council_summary: str,
    route: str,
    options: list[dict],
) -> str:
    route_note = _ROUTE_CONTEXT.get(route, _ROUTE_CONTEXT["general"])

    options_lines = []
    for i, opt in enumerate(options, 1):
        risk_text  = _RISK_TEXT.get(opt.get("tier", ""), "")
        downside   = opt.get("downside", "ไม่ระบุ")
        reversible = "ย้อนได้" if opt.get("tier") not in ("high",) else "ย้อนยาก"
        try:
            risk_pct = f"{float(opt.get('risk', 0)):.0%}"
        except (TypeError, ValueError):
            risk_pct = "?"
        options_lines.append(
            f"{i}. {str(opt.get('strategy', '')).upper()}\n"
            f"   ความเสี่ยง: {risk_pct} ({risk_text}) | {reversible}\n"
            f"   Downside: {downside}"
        )

    options_block = "\n\n".join(options_lines)

    council_section = (
        f"ผล Council:\n{council_summary.strip()}"
        if council_summary and council_summary.strip()
        else "Council: ยังไม่มีข้อมูล"
    )

    return (
        f"{route_note}\n\n"
        f"ประเด็น: {question.strip()}\n\n"
        f"{council_section}\n\n"
        f"ทางเลือก (Downside First):\n\n"
        f"{options_block}\n\n"
        f"ระบบไม่ตัดสินใจแทน ทางไหนใกล้กับสถานการณ์จริงของคุณที่สุดครับ\n— VEGA"
    )


# ── LYLA RESPONSE — Persona Engine ───────────────────────────────
# อบอุ่น, รับรู้ก่อน, ฟังก่อนวิเคราะห์, เปิดทางเลือกอย่างนุ่มนวล
def _lyla_response(
    question: str,
    council_summary: str,
    route: str,
    options: list[dict],
    entropy: float,
) -> str:
    # รับรู้สถานการณ์ตาม route + entropy
    if route in ("survival", "collapse") or entropy > 65:
        opening = "รับรู้สิ่งที่คุณเผชิญอยู่ค่ะ — เราดูทางออกที่ใกล้ที่สุดก่อนนะคะ"
    elif route == "vega":
        opening = "ฟังอยู่ค่ะ — ไม่รีบค่ะ ค่อยๆ เล่าให้ฟังได้"
    else:
        opening = "เข้าใจแล้วค่ะ ดูด้วยกันนะคะ"

    options_lines = []
    for i, opt in enumerate(options, 1):
        downside = opt.get("downside", "")
        line = f"{i}. {opt.get('strategy', '')}"
        if downside:
            line += f" — ระวัง: {downside}"
        options_lines.append(line)

    options_block = "\n".join(options_lines)

    council_section = ""
    if council_summary and council_summary.strip():
        council_section = f"\nจากที่ระบบวิเคราะห์มา:\n{council_summary.strip()}\n"

    closing = (
        "ทางไหนรู้สึกใกล้กับสถานการณ์ของคุณมากที่สุดคะ"
        if route not in ("survival", "collapse")
        else "ก้าวแรกที่เล็กที่สุดที่ทำได้ตอนนี้คืออะไรคะ"
    )

    return (
        f"{opening}\n\n"
        f"{council_section}"
        f"ทางเลือกที่มีค่ะ:\n{options_block}\n\n"
        f"{closing}\n— LYLA"
    )


# ── MAIN ENTRY ────────────────────────────────────────────────────
def king_response(
    question: str,
    council_summary: str,
    route: str = "general",
    entropy: float = 40.0,
    stability: float = 60.0,
    persona: str = "LYLA",
) -> str:
    """
    สร้าง response จาก council + strategic options
    VEGA = FATE™ + COSMIC LATTE — ตรง, deterministic, มีหัวใจ, ไม่ใช้ emoji
    LYLA = Persona Engine — อบอุ่น, รับรู้, เปิดทางเลือกอย่างนุ่มนวล

    FATE™: Choice(t) ≥ 1 เสมอ | ไม่ force single path
    """
    question = str(question or "")
    council_summary = str(council_summary or "")
    try:
        entropy = float(entropy)
    except (TypeError, ValueError):
        entropy = 40.0
    if not question.strip():
        if persona == "VEGA":
            return "FATE_VIOLATION: ไม่มี input — ระบบไม่สามารถสร้าง response ได้ครับ"
        return "ยังไม่ได้รับ input ค่ะ — ลองพิมพ์บอกมาใหม่ได้เลยนะคะ"

    options = expand_options(
        problem=question,
        route=route,
        entropy=entropy,
        stability=stability,
        max_options=3,
    )

    if persona == "VEGA":
        return _vega_response(question, council_summary, route, options)

    # Default: LYLA
    return _lyla_response(question, council_summary, route, options, entropy)
