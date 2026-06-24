# ENGINE/king_response.py
# KING DIADEM — Response Formatter
# แปลง council/decision output → response ที่ user อ่านได้
# ไม่ใช่แค่ print dict — format ตาม persona + waterline + route

from __future__ import annotations
import json


def king_response(
    user_input:     str,
    consensus_json: str | dict,
    persona:        str = "LYLA",
    waterline:      float | None = None,
    route:          str = "general",
) -> str:
    """
    Format final response จาก council consensus
    persona: "LYLA" | "VEGA" | "HALT"
    """
    # ── Parse consensus ───────────────────────────────────────────
    if isinstance(consensus_json, str):
        try:
            consensus = json.loads(consensus_json)
        except Exception:
            consensus = {}
    else:
        consensus = consensus_json or {}

    action     = str(consensus.get("final_action", "observe")).upper()
    confidence = float(consensus.get("confidence", 0.6))
    halt       = bool(consensus.get("halt", False))
    choice_count = consensus.get("choice_count")
    votes      = consensus.get("votes", [])

    # ── Persona signature ─────────────────────────────────────────
    sig = {
        "LYLA": "— LYLA ◈",
        "VEGA": "— VEGA ◆",
        "HALT": "— HALT ⬡",
    }.get(persona.upper(), "— KING DIADEM")

    lines: list[str] = []

    # ── HALT override ─────────────────────────────────────────────
    if halt or action == "HALT":
        lines += [
            "⬡ SYSTEM HALT",
            "",
            "สถานการณ์วิกฤต — ไม่แนะนำให้ดำเนินการต่อในขณะนี้",
            "",
            "สิ่งที่ต้องทำก่อน:",
            "  1. หยุดพักทันที",
            "  2. ติดต่อคนที่ไว้ใจได้",
            "  3. ประเมินสถานการณ์ใหม่เมื่อพร้อม",
            "",
            f"Choice(t) ≥ 1 → ยังมีทางเสมอ",
        ]
        if waterline is not None:
            lines.append(f"Waterline: {waterline:.0f} / 100")
        lines += ["", sig]
        return "\n".join(lines)

    # ── Normal response ───────────────────────────────────────────
    lines += [
        f"[KING DIADEM — {route.upper()} / {persona}]",
        "",
        f"Action:     {action}",
        f"Confidence: {confidence*100:.0f}%",
    ]

    if waterline is not None:
        wl_bar = "█" * int(waterline / 10) + "░" * (10 - int(waterline / 10))
        lines.append(f"Waterline:  {wl_bar} {waterline:.0f}")

    if choice_count is not None:
        lines.append(f"Choice(t):  {choice_count} ({'≥1 ✓' if choice_count >= 1 else '= 0 ⚠'})")

    # ── Council summary (ถ้ามี) ───────────────────────────────────
    if votes:
        lines += ["", "Council:"]
        for v in votes[:3]:  # แสดงแค่ 3 vote แรก
            lines.append(f"  {v.get('voice','?'):10} → {v.get('vote','?')}")

    # ── Input echo (ย่อ) ──────────────────────────────────────────
    if user_input:
        lines += ["", f"Input: {user_input[:80]}{'...' if len(user_input) > 80 else ''}"]

    lines += ["", "Fail Less · Harm Less · Restore Choice", "", sig]

    return "\n".join(lines)
