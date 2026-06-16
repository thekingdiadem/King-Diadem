"""
core/fate_core.py — KING DIADEM
FATE™ v1.0 — Deterministic Decision Infrastructure
One-Line Lock: "Fail less, not win more."
"""

import time

# ══════════════════════════════════════════════════════════════════
# FATE™ IMMUTABLE AXIOMS
# ══════════════════════════════════════════════════════════════════
SYSTEM_MODE = "DETERMINISTIC_LOGIC_KERNEL"

AXIOMS = {
    1: "Logic Over Persona — ยึดกฎ ไม่ยึดบุคคล",
    2: "Rule Over Authority — กฎมาก่อนอำนาจเสมอ",
    3: "Determinism — Input เดิม + กฎเดิม = Output เดิม",
    4: "Downside Before Upside — ประเมินความเสียหายก่อนผลตอบแทน",
    5: "Explainability = 100% — อธิบายไม่ได้ = ใช้ไม่ได้",
    6: "Human Final Authority — มนุษย์ตัดสินขั้นสุดท้ายเสมอ",
}

CONSTRAINTS = [
    "NO_DECISION_SUBSTITUTION",
    "NO_NARRATIVE_MANIPULATION",
    "NO_IDENTITY_CLAIMS",
    "NO_EMOTION_SIMULATION",
    "NO_AUTONOMOUS_ENFORCEMENT",
]

CRISIS_SIGNALS = [
    "ฆ่าตัว", "ไม่อยากอยู่", "อยากตาย", "จบชีวิต",
    "ฆ่า", "ตาย", "พังหมด", "จบแล้ว", "หมดแล้ว",
    "suicid", "kill myself", "end my life", "want to die",
]


# ══════════════════════════════════════════════════════════════════
# FATE™ AUDIT TEMPLATE
# ══════════════════════════════════════════════════════════════════
def create_audit_record(decision_id: str, domain: str) -> dict:
    """สร้าง audit template ตาม FATE™ Section 6"""
    return {
        "decision_id":      decision_id,
        "timestamp":        time.time(),
        "domain":           domain,
        "ruleset_version":  "FATE™ v1.0",
        "sections": {
            "S0_metadata":       {"status": "pending"},
            "S1_input_integrity":{"status": "pending"},
            "S2_determinism":    {"status": "pending"},
            "S3_explainability": {"status": "pending"},
            "S4_conflict":       {"status": "pending"},
            "S5_override":       {"status": "pending"},
            "S6_outcome":        {"status": "pending"},
            "S7_post_audit":     {"status": "pending"},
        },
        "human_reviewer":   None,
        "final_attestation": None,
    }


# ══════════════════════════════════════════════════════════════════
# MAIN RUN
# ══════════════════════════════════════════════════════════════════
def run_fate(input_data: dict) -> dict:
    """
    FATE™ main entry point
    คืน: pass / block / reject + audit trace
    """
    # ── S1: Input Integrity ──────────────────────────────────────
    if not input_data or not isinstance(input_data, dict):
        return _reject("INVALID_INPUT", "input ต้องเป็น dict")

    message = input_data.get("message") or input_data.get("input") or ""
    if not isinstance(message, str):
        return _reject("INVALID_TYPE", "message ต้องเป็น string")

    message = message.strip()
    if not message:
        return _reject("EMPTY_INPUT", "message ว่างเปล่า")

    # ── S4: Conflict / Crisis Detection ─────────────────────────
    risk = detect_human_risk(message)
    trace = {
        "axioms_invoked": [1, 4, 5, 6],
        "rules":          ["INPUT_VALIDATION", "NORMALIZATION", "RISK_SCAN", "DOWNSIDE_CHECK"],
        "risk_level":     risk,
        "explainable":    True,
        "time_to_explain": "< 2 นาที",
    }

    if risk == "critical":
        return {
            "status":        "block",
            "reason":        "CRISIS_SIGNAL_DETECTED",
            "safe_response": safe_response(),
            "trace":         trace,
            "hotline":       "1323 — สายด่วนสุขภาพจิต ฟรี 24 ชม.",
            "fate_axiom":    AXIOMS[6],
        }

    # ── Civil Work ───────────────────────────────────────────────
    civil_result = None
    if "tasks" in input_data:
        try:
            from core.civil_work_core import evaluate_work_plan
            civil_result = evaluate_work_plan(input_data["tasks"])
        except Exception as e:
            civil_result = {"error": str(e)}

    # ── Dependency Cycle ─────────────────────────────────────────
    cycle_result = None
    if "state" in input_data:
        try:
            from core.dependency_cycle import dependent_cycle
            cycle_result = dependent_cycle(input_data["state"])
        except Exception as e:
            cycle_result = {"error": str(e)}

    # ── S6: Outcome Classification ───────────────────────────────
    return {
        "status":       "pass",
        "data":         {"message": message},
        "risk":         risk,
        "trace":        trace,
        "civil":        civil_result,
        "cycle":        cycle_result,
        "fate_lock":    "Fail less, not win more.",
        "human_authority": "Human retains final authority.",
    }


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════
def detect_human_risk(text: str) -> str:
    t = text.lower()
    for w in CRISIS_SIGNALS:
        if w in t:
            return "critical"
    if len(text) < 3:
        return "low"
    # ตรวจ pattern เพิ่มเติม
    if any(w in t for w in ["เสี่ยง", "พัง", "หมดหวัง", "ไม่ไหว"]):
        return "elevated"
    return "normal"


def safe_response() -> str:
    return (
        "สถานการณ์นี้มีสัญญาณที่ต้องการความช่วยเหลือทันที\n"
        "ขอให้หยุดก่อน และติดต่อคนที่ไว้ใจได้\n"
        "สายด่วนสุขภาพจิต: 1323 (ฟรี 24 ชม.)"
    )


def _reject(reason: str, detail: str = "") -> dict:
    return {
        "status": "reject",
        "reason": reason,
        "detail": detail,
        "fate_axiom": AXIOMS[5],
    }


def get_axioms() -> dict:
    return AXIOMS


def get_constraints() -> list:
    return CONSTRAINTS
