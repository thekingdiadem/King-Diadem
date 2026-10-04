"""
core/civil_work_core.py — KING DIADEM
CIVIL WORK CORE: Human-independent decision support
ทำงานได้แม้ไม่มีทรัพยากร — ออกแบบเพื่ออารยธรรมที่ยังมีชีวิต
"""

import re

# ══════════════════════════════════════════════════════════════════
# CIVIL WORK AXIOMS
# ══════════════════════════════════════════════════════════════════
AXIOMS = {
    "A1": "เงินคือเครื่องมือ ไม่ใช่ศีลธรรม",
    "A2": "งานต้องลดความโง่ ไม่ใช่สร้างการเชื่อฟัง",
    "A3": "ไม่ตัดสินใจดีกว่าตัดสินใจผิด",
    "A4": "การอยู่รอดมาก่อนการเติบโต",
    "A5": "ศักดิ์ศรีต้องมีทางออกอย่างน้อย 1 ทาง",
}

VALID_WORK_CONDITIONS = {
    "has_choice":              "งานต้องให้ทางเลือก",
    "has_exit":                "งานต้องมีทางออก",
    "no_forced_identity":      "ไม่บังคับอัตลักษณ์",
    "no_required_belief":      "ไม่ต้องการความเชื่อ",
}

FORBIDDEN = [
    "selling_dreams", "guaranteeing_success",
    "making_decisions_for_clients", "dependency_creation",
    "forced_loyalty", "identity_trap",
]

ALLOWED_SCOPE = [
    "brand_analysis", "persona_structure", "identity_logic",
    "directional_decision_support", "risk_filtering",
    "work_plan_evaluation", "resource_assessment",
]

SUCCESS_CONDITIONS = {
    "client_not_broken":        True,
    "client_has_next_step":     True,
    "system_silent_after":      True,
}

FAILURE_CONDITIONS = {
    "forced_decision":          True,
    "loss_of_exit":             True,
    "economic_floor_broken":    True,
}


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════
def _normalize(item) -> dict:
    if isinstance(item, str):
        return {"description": item}
    if isinstance(item, dict):
        return item.copy()
    return {"description": str(item)}


def _has(text: str, words: list) -> bool:
    # คำเต็ม: เดิม "must" ติด "mustard", "stop" ติด "nonstop", "join" ฯลฯ
    t = str(text or "").lower()
    return any(re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", t) for w in words)


def _infer(text: str, pos: list, neg: list, default=True) -> bool:
    if _has(text, neg): return False
    if _has(text, pos): return True
    return default


# ══════════════════════════════════════════════════════════════════
# VALIDATION
# ══════════════════════════════════════════════════════════════════
def validate_work_item(item: dict) -> dict:
    item = _normalize(item)
    desc = str(item.get("description", "") or "")
    out  = dict(item)

    out["has_choice"] = item.get("has_choice", _infer(desc,
        pos=["choice","option","alternate","possible","can choose"],
        neg=["forced","must","no choice","only option","required to"]))

    out["has_exit"] = item.get("has_exit", _infer(desc,
        pos=["exit","leave","opt out","fallback","pause","withdraw","stop"],
        neg=["forever","no return","never leave","locked in","permanent"]))

    out["no_forced_identity"] = item.get("no_forced_identity",
        not _has(desc, ["become","belong","loyal","cult","join us","follow me","identity is"]))

    out["no_required_belief"] = item.get("no_required_belief",
        not _has(desc, ["faith","believe","trust that","promise success","cult","miracle","guaranteed"]))

    out["in_allowed_scope"] = _has(desc,
        ["brand","persona","identity","direction","risk","support","analysis","structure","evaluate","assess"])

    out["in_forbidden_scope"] = _has(desc,
        ["sell dream","selling dreams","guarantee","guaranteeing","force decision","dependency","locked"])

    out["valid"] = all([
        out["has_choice"],
        out["has_exit"],
        out["no_forced_identity"],
        out["no_required_belief"],
        not out["in_forbidden_scope"],
    ])

    return out


def score_work_item(item: dict) -> dict:
    item = _normalize(item)
    if "has_choice" not in item:       # เรียกตรงโดยไม่ผ่าน validate → KeyError เดิม
        item = validate_work_item(item)
    desc  = str(item.get("description", "") or "")
    score = 0
    notes = []

    if not item.get("has_choice"):         score -= 40; notes.append("ไม่มีทางเลือก")
    if not item.get("has_exit"):           score -= 40; notes.append("ไม่มีทางออก")
    if not item.get("no_forced_identity"): score -= 30; notes.append("บังคับอัตลักษณ์")
    if not item.get("no_required_belief"): score -= 30; notes.append("ต้องการความเชื่อ")
    if item.get("in_forbidden_scope"):     score -= 40; notes.append("ขัดขอบเขตที่อนุญาต")

    if _has(desc, ["learn","understand","research","audit","review"]):
        score += 15; notes.append("เพิ่มความเข้าใจ ลดความโง่")
    if _has(desc, ["survive","stabilize","protect","sustain","secure"]):
        score += 12; notes.append("ให้ความสำคัญกับการอยู่รอด")
    if _has(desc, ["grow","scale","expand"]):
        score += 4;  notes.append("มีแรงจูงใจเติบโต")
    if item.get("in_allowed_scope"):
        score += 6;  notes.append("อยู่ในขอบเขตที่อนุญาต")

    item["score"] = score
    item["notes"] = notes
    return item


def evaluate_work_plan(items: list) -> dict:
    """
    ประเมินแผนงานทั้งหมด
    คืน: recommendation + valid/rejected + axioms
    """
    if isinstance(items, (str, dict)):
        items = [items]
    if not isinstance(items, (list, tuple)) or not items:
        return {
            "system":  "CIVIL_WORK_CORE",
            "status":  "NO_WORK_DEFINED",
            "message": "ไม่มีงานหรือทางเลือกให้ประเมิน",
            "axioms":  AXIOMS,
        }

    evaluated = []
    for item in items:
        v = validate_work_item(_normalize(item))
        s = score_work_item(v)
        evaluated.append(s)

    valid    = [x for x in evaluated if x["valid"]]
    rejected = [x for x in evaluated if not x["valid"]]
    best     = sorted(valid, key=lambda x: x["score"], reverse=True)
    recommendation = best[0] if best else None

    recovery = []
    if not recommendation:
        recovery = [
            {"action": "pause_and_assess",  "reason": "หยุดและประเมินใหม่ก่อนลงมือ"},
            {"action": "restore_choice",    "reason": "สร้างทางเลือกสำรอง"},
            {"action": "limit_scope",       "reason": "ลดขอบเขตเพื่อป้องกันทรัพยากรหมด"},
        ]

    return {
        "system":          "CIVIL_WORK_CORE",
        "status":          "SUCCESS" if recommendation else "REJECTED",
        "axioms":          AXIOMS,
        "recommendation":  recommendation,
        "valid_count":     len(valid),
        "rejected_count":  len(rejected),
        "all_items":       evaluated,
        "rejected":        rejected,
        "recovery":        recovery,
        "fate_lock":       "Fail Less. Harm Less. Restore Choice.",
    }
