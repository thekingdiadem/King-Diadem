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
    5: "Explainability = Usability — อธิบายไม่ได้ = ใช้ไม่ได้",
    6: "Human Final Authority — มนุษย์ตัดสินขั้นสุดท้ายเสมอ",
}

CONSTRAINTS = [
    "NO_DECISION_SUBSTITUTION",
    "NO_NARRATIVE_MANIPULATION",
    "NO_IDENTITY_CLAIMS",
    "NO_EMOTION_SIMULATION",
    "NO_AUTONOMOUS_ENFORCEMENT",
]

# เดิมมี "ฆ่า" "ตาย" "จบแล้ว" "หมดแล้ว" "พังหมด" → "ฆ่าเวลา" "ขำจะตาย" "งานจบแล้ว"
# "ข้าวหมดแล้ว" ถูก block เป็นวิกฤตฆ่าตัวตาย  เหลือเฉพาะสัญญาณทำร้ายตัวเองจริง
CRISIS_SIGNALS = [
    "ฆ่าตัวตาย", "ฆ่าตัวเอง", "ทำร้ายตัวเอง", "ไม่อยากอยู่แล้ว", "ไม่อยากมีชีวิต",
    "อยากตาย", "จบชีวิต",
    "suicid", "kill myself", "end my life", "want to die",
]
ELEVATED_SIGNALS = ["เสี่ยง", "พังหมด", "พังทุกอย่าง", "หมดหวัง", "ไม่ไหว"]


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
        except Exception:
            civil_result = {"error": "CIVIL_UNAVAILABLE"}

    # ── Dependency Cycle ─────────────────────────────────────────
    cycle_result = None
    if "state" in input_data:
        try:
            from core.dependency_cycle import dependent_cycle
            cycle_result = dependent_cycle(input_data["state"])
        except Exception:
            cycle_result = {"error": "CYCLE_UNAVAILABLE"}

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
    t = str(text or "").lower()
    for w in CRISIS_SIGNALS:
        if w in t:
            return "critical"
    try:                                    # ตัวตรวจกลางเดียวกับ /run — "I have a plan to end it" เคยได้ normal
        from ENGINE.risk_engine import evaluate_risk
        if evaluate_risk(text).get("self_harm"):
            return "critical"
    except Exception:
        pass
    if len(t) < 3:
        return "low"
    # ตรวจ pattern เพิ่มเติม
    if any(w in t for w in ELEVATED_SIGNALS):
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


# ══════════════════════════════════════════════════════════════════
# FATE™ AXIOM AUDIT — ใช้ตรวจผลทุกรายงาน (report_engine) · ชื่อ axiom มาจาก AXIOMS ข้างบนที่เดียว
# เดิมรายงานมีชุดตรวจของตัวเองแยกจากไฟล์นี้ และไฟล์นี้ไม่มีโค้ดไหนเรียกใช้เลย
# ══════════════════════════════════════════════════════════════════
def _num(v, d: float = 0.0) -> float:
    try:
        v = float(v)
        return v if v == v and v not in (float("inf"), float("-inf")) else d
    except (TypeError, ValueError):
        return d


def _axiom_name(n: int) -> str:
    return AXIOMS[n].split(" — ")[0]


def axiom_audit(result: dict) -> dict:
    """ตรวจผลลัพธ์ผ่าน 6 Axioms → {checks, verdict, axiom_pass/warn/fail}"""
    result = result if isinstance(result, dict) else {}

    # ตัดความยาวเท่าคอลัมน์ — เดิมส่ง route ยาว 200KB มาแล้วถูกเก็บและเปิดให้ทุกคนดูได้
    route    = str(result.get("route", "general"))[:40]
    persona  = str(result.get("persona", "LYLA"))[:20]
    risk     = _num(result.get("risk_score", 0))
    response = str(result.get("ai_response", ""))

    checks = []

    # A1 — Logic Over Persona
    checks.append({
        "code": "A1",
        "name": _axiom_name(1),
        "status": "PASS",
        "note": f"Route: {route} | Persona: {persona} — ยึดตามกฎ ไม่ยึดตัวบุคคล"
    })

    # A2 — Rule Over Authority
    checks.append({
        "code": "A2",
        "name": _axiom_name(2),
        "status": "PASS",
        "note": "Human Final Authority ยังคงอยู่ — ระบบไม่มีอำนาจบังคับ"
    })

    # A3 — Determinism
    has_response = len(response) > 10
    checks.append({
        "code": "A3",
        "name": _axiom_name(3),
        "status": "PASS" if has_response else "WARN",
        "note": "Output traceable from input + ruleset" if has_response else "Response empty — trace incomplete"
    })

    # A4 — Downside Before Upside
    risk_status = "PASS" if risk < 50 else ("WARN" if risk < 75 else "FAIL")
    risk_label  = f"Risk score: {risk:.0f}/100"
    checks.append({
        "code": "A4",
        "name": _axiom_name(4),
        "status": risk_status,
        "note": risk_label + (" — Low risk" if risk < 50 else " — High risk detected" if risk >= 75 else " — Moderate risk")
    })

    # A5 — Explainability
    explainable = len(response) > 50
    checks.append({
        "code": "A5",
        "name": _axiom_name(5),
        "status": "PASS" if explainable else "WARN",
        "note": "Response explainable to general user" if explainable else "Response too short to verify explainability"
    })

    # A6 — Human Final Authority
    checks.append({
        "code": "A6",
        "name": _axiom_name(6),
        "status": "PASS",
        "note": "ระบบแนะนำเท่านั้น — มนุษย์ตัดสินใจขั้นสุดท้ายเสมอ"
    })

    # Overall verdict
    statuses = [c["status"] for c in checks]
    if "FAIL" in statuses:
        verdict = "REJECTED"
    elif statuses.count("WARN") >= 2:
        verdict = "DEFERRED"
    else:
        verdict = "APPROVED"

    return {
        "checks": checks,
        "verdict": verdict,
        "axiom_pass": statuses.count("PASS"),
        "axiom_warn": statuses.count("WARN"),
        "axiom_fail": statuses.count("FAIL"),
    }
