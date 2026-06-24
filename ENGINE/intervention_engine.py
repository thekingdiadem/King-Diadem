# ENGINE/intervention_engine.py
"""
KING DIADEM — Intervention Engine
FATE™ Axiom 4: Downside before Upside
TITAN CORE: Choice(t) ≥ 1 → collapse = False

ไม่ return string — return action plan จริง พร้อม priority และ reason
"""

from __future__ import annotations
from typing import Optional


# ── Risk level normalizer ─────────────────────────────────────────
RISK_LEVELS = ("low", "moderate", "unstable", "critical", "collapse")

def _normalize_risk(risk_state: str) -> str:
    r = (risk_state or "").lower().strip()
    if r in RISK_LEVELS:
        return r
    # fuzzy map
    if any(k in r for k in ("crit", "danger", "วิกฤต", "อันตราย")):
        return "critical"
    if any(k in r for k in ("unstab", "ไม่มั่นคง", "เสี่ยง")):
        return "unstable"
    if any(k in r for k in ("collaps", "พัง", "หมด")):
        return "collapse"
    if any(k in r for k in ("mod", "warn", "เฝ้าระวัง")):
        return "moderate"
    return "low"


# ── Intervention catalog — deterministic per level ────────────────
_INTERVENTIONS = {

    "collapse": {
        "priority":   "IMMEDIATE",
        "actions": [
            {
                "step":   1,
                "action": "HALT — หยุดการตัดสินใจใหม่ทั้งหมดชั่วคราว",
                "reason": "Choice(t) ≥ 1 ต้องรักษาให้ได้ก่อน ก่อนจะ optimize อะไร",
            },
            {
                "step":   2,
                "action": "ระบุทรัพยากรที่เหลืออยู่จริง (เงิน, อาหาร, พลังงาน, คน)",
                "reason": "ไม่สามารถวางแผนได้ถ้าไม่รู้ baseline",
            },
            {
                "step":   3,
                "action": "หา 1 ทางเลือกที่ยังเปิดอยู่ — ไม่ต้องดีที่สุด แค่ยังเปิดอยู่",
                "reason": "restore choice ก่อน — นั่นคือ intervention เดียวที่สำคัญตอนนี้",
            },
        ],
        "stop_the_line": True,
        "axiom":        "Choice(t) ≥ 1 → collapse = False",
        "waterline":    "BREACHED",
    },

    "critical": {
        "priority":   "HIGH",
        "actions": [
            {
                "step":   1,
                "action": "ประเมิน immediate physical safety ก่อน (ที่, อาหาร, น้ำ, ความปลอดภัย)",
                "reason": "Axiom 4 — Downside before Upside: ปิดความเสี่ยงชีวิตก่อนทุกอย่าง",
            },
            {
                "step":   2,
                "action": "ย้ายออกจากจุดเสี่ยงถ้า physical threat ยังอยู่",
                "reason": "relocation เป็นตัวเลือก ไม่ใช่คำสั่ง — ขึ้นกับ context จริง",
            },
            {
                "step":   3,
                "action": "ติดต่อคนที่ไว้ใจได้ 1 คน — ไม่ต้องอธิบายครบ แค่ให้รู้ว่าอยู่ที่ไหน",
                "reason": "entropy สูง — ไม่ควรแก้คนเดียว",
            },
            {
                "step":   4,
                "action": "ระงับ non-urgent commitment ทั้งหมดไว้ก่อน",
                "reason": "resource ที่มีอยู่ต้องใช้กับ survival ก่อน",
            },
        ],
        "stop_the_line": True,
        "axiom":        "Fail less. Harm less. Restore more.",
        "waterline":    "CRITICAL",
    },

    "unstable": {
        "priority":   "MEDIUM",
        "actions": [
            {
                "step":   1,
                "action": "Stabilize ทรัพยากรหลัก (เงิน / อาหาร / ที่พัก) ให้อยู่เกิน 72 ชั่วโมง",
                "reason": "Axiom E3: Stabilize before Optimize — ห้าม optimize ก่อนมีฐาน",
            },
            {
                "step":   2,
                "action": "ระบุสิ่งที่กำลังไหลออก (drain) มากที่สุดและหยุดก่อน",
                "reason": "ปิด leak ก่อนเติม — ไม่งั้นเติมเท่าไรก็ไม่พอ",
            },
            {
                "step":   3,
                "action": "อย่าเพิ่ม commitment ใหม่จนกว่า stability จะ > 72h",
                "reason": "DriftZero: ห้ามขยายระบบขณะที่ waterline ยังไม่นิ่ง",
            },
        ],
        "stop_the_line": False,
        "axiom":        "Stabilize before Optimize",
        "waterline":    "WARNING",
    },

    "moderate": {
        "priority":   "LOW",
        "actions": [
            {
                "step":   1,
                "action": "Monitor daily — ตรวจสอบ waterline ทุกวัน",
                "reason": "moderate ไม่ได้แปลว่าปลอดภัย แปลว่ายังมีเวลา",
            },
            {
                "step":   2,
                "action": "ระบุ 1 จุดที่เสี่ยงมากที่สุดและวาง contingency ไว้",
                "reason": "DriftZero: prevent drift ก่อนมันถึง unstable",
            },
        ],
        "stop_the_line": False,
        "axiom":        "0.1% drift prevention",
        "waterline":    "WATCH",
    },

    "low": {
        "priority":   "NONE",
        "actions": [
            {
                "step":   1,
                "action": "Maintain current strategy — ระบบอยู่ใน safe zone",
                "reason": "ไม่มีสัญญาณที่ต้องแทรกแซง",
            },
        ],
        "stop_the_line": False,
        "axiom":        "Choice(t) ≥ 1 → collapse = False",
        "waterline":    "NOMINAL",
    },
}


# ── Main entry point ──────────────────────────────────────────────
def intervene(
    risk_state: str,
    context: Optional[dict] = None,
) -> dict:
    """
    Args:
        risk_state: "low" | "moderate" | "unstable" | "critical" | "collapse"
        context:    optional dict with keys: money, food, energy, location, people

    Returns:
        {
            "risk_level":     str,
            "priority":       str,
            "stop_the_line":  bool,
            "waterline":      str,
            "axiom":          str,
            "actions":        list[dict],
            "context_notes":  list[str],   # เพิ่มตาม context ที่ส่งมา
        }
    """
    level  = _normalize_risk(risk_state)
    plan   = _INTERVENTIONS[level].copy()
    ctx    = context or {}

    # ── Context-aware notes ───────────────────────────────────────
    notes = []

    money  = ctx.get("money",  None)
    food   = ctx.get("food",   None)
    energy = ctx.get("energy", None)
    people = ctx.get("people", None)

    if money is not None and money < 100:
        notes.append(f"⚠ เงินเหลือ {money} บาท — ต่ำกว่า 72h threshold ควร prioritize ทันที")

    if food is not None and food < 2:
        notes.append(f"⚠ อาหารเหลือ {food} มื้อ — ต้องแก้ภายใน 24 ชั่วโมง")

    if energy is not None and energy < 30:
        notes.append(f"⚠ energy {energy}% — ห้ามตัดสินใจใหญ่จนกว่าจะพักพอ")

    if people is not None and people == 0:
        notes.append("⚠ ไม่มีคนช่วย — entropy สูงขึ้น ควรหาคนรับรู้สถานการณ์ด้วย 1 คน")

    return {
        "risk_level":    level,
        "priority":      plan["priority"],
        "stop_the_line": plan["stop_the_line"],
        "waterline":     plan["waterline"],
        "axiom":         plan["axiom"],
        "actions":       plan["actions"],
        "context_notes": notes,
    }


# ── Backward-compat shim (ถ้า code เก่าเรียก intervention()) ──────
def intervention(risk_state: str) -> str:
    result = intervene(risk_state)
    # return action step 1 เป็น string เหมือนเดิม
    return result["actions"][0]["action"]
