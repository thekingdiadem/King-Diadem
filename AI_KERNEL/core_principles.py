"""
AI_KERNEL/core_principles.py — KING DIADEM™
Core Principles — Permanent Reference Layer

สร้างโดย: Nithikorn Bunsrang
ไฟล์นี้คือ source of truth ของ principles ทั้งหมด
import ได้จากทุก module ในระบบ

"ถ้าอธิบายไม่ได้ = ใช้ไม่ได้"
"""

import time

# ══════════════════════════════════════════════════════════════════
# CORE PRINCIPLES — พี่คิงเขียนเอง ห้ามแก้
# ══════════════════════════════════════════════════════════════════

CORE_PRINCIPLES = {
    "CP1": {
        "en":    "Drift — accumulated decay, small step at a time",
        "th":    "Drift — ความเสื่อมสะสมทีละน้อย",
        "apply": "ตรวจ drift ทุกวัน ไม่รอให้มันระเบิด — DHD ≤ 0.1%",
        "link":  ["DriftZero", "DHD", "R=(D×T)/C"],
    },
    "CP2": {
        "en":    "Growth must not destroy Sustainability",
        "th":    "Growth ต้องไม่ทำลาย Sustainability",
        "apply": "optimize ได้ แต่ห้าม optimize จนพัง survival floor",
        "link":  ["HUMAN_SUSTAINABILITY", "B-2", "waterline"],
    },
    "CP3": {
        "en":    "Structure serves life, not life serving the structure",
        "th":    "Structure serves life, not life serving the structure",
        "apply": "ถ้า structure ทำให้มนุษย์เจ็บ → structure นั้นผิด ต้องแก้ structure",
        "link":  ["SCL-A2", "GOV-P5", "north_principle"],
    },
    "CP4": {
        "en":    "Structure is for protection, not dominating",
        "th":    "Structure is for protection, not dominating. Good structure gives humans room to breathe — not zero choices.",
        "apply": "โครงสร้างที่ดีต้องมีพื้นที่ให้มนุษย์หายใจ ไม่ใช่ไม่มีทางเลือก",
        "link":  ["SCL-A2", "A2-axioms", "evaluate_structure"],
    },
    "CP5": {
        "en":    "Trust = Observation × Consistency over Time",
        "th":    "Trust = Observation × Consistency over Time",
        "apply": "อำนาจไม่เคย = ความเชื่อใจ ความเชื่อใจมาจากการสังเกตและความสม่ำเสมอ",
        "link":  ["node_trust", "SCL7-P3", "update_trust"],
    },
    "CP6": {
        "en":    "Downside before Upside",
        "th":    "Downside before Upside",
        "apply": "ประเมินความเสียหายก่อนผลกำไรเสมอ — FATE™ A4",
        "link":  ["FATE-A4", "decision_tree", "galaxy_expand"],
    },
    "CP7": {
        "en":    "Fail less · Harm less · Restore more",
        "th":    "Fail less · Harm less · Restore more",
        "apply": "ไม่ได้สร้างมาเพื่อชนะ แต่สร้างมาเพื่อลดความเสียหาย",
        "link":  ["DriftZero", "FATE", "unified_world_kernel"],
    },
}

# ══════════════════════════════════════════════════════════════════
# SEALS — ประโยคปิดที่ใช้ทุก module
# ══════════════════════════════════════════════════════════════════

SEALS = {
    "fate":        "Fail less, not win more.",
    "fate_th":     "ไม่ทำให้คุณชนะบ่อยขึ้น แต่มันทำให้คุณไม่พังซ้ำ อย่างอธิบายย้อนกลับได้",
    "driftzero":   "Fail less. Harm less. Restore more.",
    "titan":       "ทางเลือก>0:ไม่ต้องกระทำ / ทางเลือก=0:ต้องกระทำขั้นต่ำสุด",
    "unified":     "Protect the Choice. Respect the Void.",
    "equation":    "Reality + Evidence − Drift = Governance",
    "master_eq":   "R = (D × T) / C",
    "invariant":   "Choice(t) >= 1 → collapse = False",
    "scl7":        "Logic must never erase warmth.",
    "udok":        "หยุดที่เวทนา ก่อนมันสร้างตัณหา",
    "sati":        "สิ่งที่สำคัญกว่าสติ — ไม่มี",
    "survival":    "ดีพอให้รอด สำคัญกว่า ดีสุดจนพัง",
    "endurance":   "Stay simple long enough to outlive the impossible.",
    "audit":       "ถ้าอธิบายไม่ได้ = ใช้ไม่ได้ ถ้า override โดยไร้ร่องรอย = ผิดกฎ",
    "truth":       "Truth doesn't compete. It waits.",
    "trust":       "Trust = Observation × Consistency over Time",
    "structure":   "Structure serves life, not life serving the structure.",
    "freedom":     "ถ้าหากอิสรภาพที่แท้จริงคือวันที่เราไม่มีหนี้",
}

# ══════════════════════════════════════════════════════════════════
# LOOKUP FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def get_principle(key: str) -> dict:
    """คืน principle ตาม key เช่น 'CP1', 'CP5'"""
    return CORE_PRINCIPLES.get(key, {})


def get_seal(key: str) -> str:
    """คืน seal phrase เช่น 'fate', 'udok', 'sati'"""
    return SEALS.get(key, "")


def get_all_principles() -> dict:
    return {**CORE_PRINCIPLES}


def get_all_seals() -> dict:
    return {**SEALS}


def principles_snapshot() -> dict:
    """dump สำหรับ /api/kernel_snapshot + belief_audit"""
    return {
        "principles":  CORE_PRINCIPLES,
        "seals":       SEALS,
        "count":       len(CORE_PRINCIPLES),
        "architect":   "Nithikorn Bunsrang",
        "system":      "KING DIADEM™",
        "generated_at": time.time(),
    }


def check_principle_alignment(action: dict) -> dict:
    """
    ตรวจว่า action สอดคล้องกับ core principles ไหม
    ใช้ใน belief_core enforce layer
    """
    violations = []

    # CP1 — drift unchecked
    if action.get("drift_unchecked"):
        violations.append({"cp": "CP1", "reason": "Drift ไม่ถูกตรวจ — เสื่อมสะสมโดยไม่รู้"})

    # CP2 — growth destroys sustainability
    if action.get("growth_destroys_sustainability"):
        violations.append({"cp": "CP2", "reason": "Growth ทำลาย Sustainability"})

    # CP3 — structure over life
    if action.get("structure_over_life"):
        violations.append({"cp": "CP3", "reason": "Structure ถูกวางไว้เหนือชีวิต"})

    # CP4 — structure dominates
    if action.get("structure_dominates") or action.get("choices_available", 1) == 0:
        violations.append({"cp": "CP4", "reason": "Structure ครอบงำ ไม่มีพื้นที่หายใจ"})

    # CP5 — trust without observation
    if action.get("trust_without_evidence"):
        violations.append({"cp": "CP5", "reason": "Trust โดยไม่มี Observation × Consistency"})

    # CP6 — upside before downside
    if action.get("upside_before_downside"):
        violations.append({"cp": "CP6", "reason": "ประเมินผลกำไรก่อนความเสียหาย"})

    # CP7 — optimizing to win not to fail less
    if action.get("optimizing_to_win"):
        violations.append({"cp": "CP7", "reason": "Optimizing to win — ไม่ใช่ Fail less"})

    return {
        "aligned":       len(violations) == 0,
        "violations":    violations,
        "violation_count": len(violations),
        "seal":          SEALS["driftzero"],
    }


# ══════════════════════════════════════════════════════════════════
# SELF-TEST
# ══════════════════════════════════════════════════════════════════

def _self_test() -> dict:
    # all 7 principles present
    for i in range(1, 8):
        assert f"CP{i}" in CORE_PRINCIPLES, f"CP{i} missing"

    # seals
    assert get_seal("fate")    == SEALS["fate"]
    assert get_seal("udok")    == SEALS["udok"]
    assert get_seal("sati")    == SEALS["sati"]
    assert get_seal("trust")   == SEALS["trust"]
    assert get_seal("structure") == SEALS["structure"]

    # get_principle
    cp1 = get_principle("CP1")
    assert "drift" in cp1["en"].lower()

    cp5 = get_principle("CP5")
    assert "Observation" in cp5["en"]

    # alignment check
    a1 = check_principle_alignment({})
    assert a1["aligned"] is True

    a2 = check_principle_alignment({"choices_available": 0, "upside_before_downside": True})
    assert a2["aligned"] is False
    assert len(a2["violations"]) >= 2

    # snapshot
    snap = principles_snapshot()
    assert snap["count"] == 7
    assert snap["architect"] == "Nithikorn Bunsrang"

    return {"status": "OK", "module": "core_principles"}


if __name__ == "__main__":
    import json
    print(json.dumps(principles_snapshot(), indent=2, ensure_ascii=False, default=str))
    print(_self_test())
