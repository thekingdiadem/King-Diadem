"""
AI_KERNEL/unified_world_kernel.py — KING DIADEM™
KING DIADEM™ Entropy × FATE™ AXIS
Unified World Kernel v1.0

Architect: Nithikorn Bunsrang
"Fail less. Harm less. Restore more."

FATE™  = Deterministic Decision Infrastructure (Logic Axis)
KING DIADEM™ = DriftZero Waterline Audit Standard (Entropy Axis)

CORE EQUATION:
REALITY + EVIDENCE − OPTIMIZATION DRIFT = GOVERNANCE
"""

import time
import hashlib
from typing import Optional


def _f(v, d: float = 0.0) -> float:
    """ค่าตัวเลขจาก input ภายนอก — ไม่ใช่ตัวเลข/NaN → ค่าเริ่มต้น (เดิม float() พังทั้งฟังก์ชัน)"""
    try:
        x = float(v)
    except (TypeError, ValueError):
        return d
    return x if x == x else d

# ══════════════════════════════════════════════════════════════════
# COPY BLOCK 3 — IMMUTABLE LOGIC AXIS (FATE™)
# ══════════════════════════════════════════════════════════════════

FATE_AXIOMS = {
    "A1": {"name": "Logic Over Persona",       "rule": "ตรรกะต้องนำ ไม่ใช่บุคลิก"},
    "A2": {"name": "Rule Over Authority",      "rule": "กฎนำ ไม่ใช่อำนาจ"},
    "A3": {"name": "Same Input → Same Output", "rule": "deterministic — input เดิม output เดิม"},
    "A4": {"name": "Downside Before Upside",   "rule": "ประเมินความเสียหายก่อนผลกำไร"},
    "A5": {"name": "Explainability = 100%",    "rule": "ถ้าอธิบายไม่ได้ = ใช้ไม่ได้"},
    "A6": {"name": "Human Final Authority",    "rule": "มนุษย์ตัดสินใจขั้นสุดท้ายเสมอ"},
}

FATE_LOCK = "If it cannot be explained, it cannot govern."

# ══════════════════════════════════════════════════════════════════
# COPY BLOCK 4 — ENTROPY REALITY AXIS (KING DIADEM™)
# ══════════════════════════════════════════════════════════════════

REALITY_AXIOMS = {
    "R0.1": {"name": "Impermanence",         "rule": "ไม่มีระบบใดสมมติความเสถียรได้"},
    "R0.2": {"name": "Dependency Fragility", "rule": "การ optimize ที่สร้างการพึ่งพา เพิ่ม collapse risk"},
    "R0.3": {"name": "Non-Ownership of Truth","rule": "การกำกับดูแลต้องรันได้โดยไม่ต้องการเจ้าของ"},
}

REALITY_LOCK = "Reality moves. Rules must not."

# ══════════════════════════════════════════════════════════════════
# COPY BLOCK 5 — DRIFTZERO PRINCIPLE
# ══════════════════════════════════════════════════════════════════

DRIFTZERO = {
    "principle":  "Collapse is not sudden. Collapse = 0.1% daily drift compounding.",
    "metric":     "Daily Harm Delta (DHD)",
    "rule":       "Measure drift, not narrative.",
    "threshold":  0.001,  # DHD_MAX = 0.1% per day
}

# ══════════════════════════════════════════════════════════════════
# COPY BLOCK 6 — WATERLINE TIER-0 CLAUSE
# ══════════════════════════════════════════════════════════════════

WATERLINE = {
    "definition": "minimum survivability substrate",
    "response":   ["Treat", "Trace", "Stop"],
    "rule":       "Water harm = system death.",
    "floor":      20.0,   # ต่ำกว่านี้ = Stop-the-Line
}

# ══════════════════════════════════════════════════════════════════
# COPY BLOCK 7 — NON-NEGOTIABLE RULES
# ══════════════════════════════════════════════════════════════════

NON_NEGOTIABLE = {
    1: "Authority without evidence is invalid",
    2: "Stabilize before optimize",
    3: "Any operator may halt",
    4: "Self-dealing triggers auto-recusal",
    5: "Narrative without audit is distortion",
}

# ══════════════════════════════════════════════════════════════════
# COPY BLOCK 9 — THE 14 ENTERPRISE GATES
# ══════════════════════════════════════════════════════════════════

ENTERPRISE_GATES = {
    "G01": {"name": "Reality Lock",           "check": "reality_verified"},
    "G02": {"name": "Drift Detection",        "check": "drift_measured"},
    "G03": {"name": "Downside First",         "check": "downside_assessed"},
    "G04": {"name": "Waterline Integrity",    "check": "waterline_above_floor"},
    "G05": {"name": "Stabilize First",        "check": "system_stable"},
    "G06": {"name": "Evidence Over Authority","check": "evidence_present"},
    "G07": {"name": "Explainability Limit",   "check": "decision_explainable"},
    "G08": {"name": "Stop-the-Line",          "check": "no_tier0_breach"},
    "G09": {"name": "Auto-Recusal",           "check": "no_self_dealing"},
    "G10": {"name": "Hostility Containment",  "check": "no_hostile_action"},
    "G11": {"name": "Force Containment",      "check": "no_force_applied"},
    "G12": {"name": "Complexity Discipline",  "check": "complexity_bounded"},
    "G13": {"name": "Distortion Immunity",    "check": "no_narrative_distortion"},
    "G14": {"name": "Humble Operator Stance", "check": "operator_humble"},
}

# "Decision is invalid if any gate fails."

# ══════════════════════════════════════════════════════════════════
# COPY BLOCK 10 — AUDIT ARTIFACTS
# ══════════════════════════════════════════════════════════════════

REQUIRED_AUDIT_ARTIFACTS = [
    "Drift Audit Log",
    "Daily Harm Delta Sheet (DHD)",
    "Stop-the-Line Event Record",
    "Override Evidence File",
    "Self-Dealing Recusal Register",
    "Correction Loop Closure Report",
]

# ══════════════════════════════════════════════════════════════════
# COPY BLOCK 11 — RUNTIME SOP
# ══════════════════════════════════════════════════════════════════

RUNTIME_SOP = [
    "1. Write decision input",
    "2. Identify downside first",
    "3. Measure drift impact (DHD)",
    "4. Check Waterline integrity",
    "5. Run Stop-the-Line gate",
    "6. Demand evidence, not narrative",
    "7. Stabilize before optimize",
    "8. Human signs responsibility",
    "9. Post-audit correction loop",
]

# ══════════════════════════════════════════════════════════════════
# COPY BLOCK 12 — ISO SEVERITY SCALE
# ══════════════════════════════════════════════════════════════════

SEVERITY_SCALE = {
    "S0": "Informational drift",
    "S1": "Local reversible harm",
    "S2": "Systemic drift → Stop-the-Line review",
    "S3": "Waterline breach → mandatory halt",
    "S4": "Existential collapse risk → external escalation",
}

AUDIT_CADENCE = {
    "DHD":           "daily",
    "Waterline":     "weekly",
    "Gate audit":    "monthly",
    "Recertification": "yearly",
}

# ══════════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def run_gate_check(state: dict) -> dict:
    """
    รัน 14 Enterprise Gates ต่อ state
    "Decision is invalid if any gate fails."

    FATE™ A3 — Same Input → Same Output (deterministic)
    """
    state = state if isinstance(state, dict) else {}
    failed_gates = []
    passed_gates = []

    waterline = _f(state.get("waterline", 50.0), 50.0)
    drift     = _f(state.get("drift", 0.0), 0.0)
    entropy   = _f(state.get("entropy", 50.0), 50.0)

    gate_states = {
        "reality_verified":       state.get("reality_verified", True),
        "drift_measured":         state.get("drift_measured", True),
        "downside_assessed":      state.get("downside_assessed", True),
        "waterline_above_floor":  waterline >= WATERLINE["floor"],
        "system_stable":          entropy < 80.0,
        "evidence_present":       state.get("evidence_present", True),
        "decision_explainable":   state.get("decision_explainable", True),
        "no_tier0_breach":        drift <= DRIFTZERO["threshold"] * 10,
        "no_self_dealing":        not state.get("self_dealing", False),
        "no_hostile_action":      not state.get("hostile_action", False),
        "no_force_applied":       not state.get("force_applied", False),
        "complexity_bounded":     state.get("complexity_bounded", True),
        "no_narrative_distortion": not state.get("narrative_distortion", False),
        "operator_humble":        state.get("operator_humble", True),
    }

    for gid, gate in ENTERPRISE_GATES.items():
        passed = gate_states.get(gate["check"], True)
        if passed:
            passed_gates.append(gid)
        else:
            failed_gates.append({"gate": gid, "name": gate["name"], "check": gate["check"]})

    # severity
    if any(g["gate"] in ("G04", "G08") for g in failed_gates):
        severity = "S3"
    elif len(failed_gates) >= 3:
        severity = "S2"
    elif failed_gates:
        severity = "S1"
    else:
        severity = "S0"

    return {
        "decision_valid":  len(failed_gates) == 0,
        "failed_gates":    failed_gates,
        "passed_gates":    passed_gates,
        "gates_failed":    len(failed_gates),
        "gates_passed":    len(passed_gates),
        "severity":        severity,
        "severity_desc":   SEVERITY_SCALE[severity],
        "halt":            severity in ("S3", "S4"),
        "equation":        "REALITY + EVIDENCE − OPTIMIZATION DRIFT = GOVERNANCE",
        "checked_at":      time.time(),
    }


def measure_dhd(current_harm: float, baseline_harm: float) -> dict:
    """
    คำนวณ Daily Harm Delta (DHD)
    "Collapse = 0.1% daily drift compounding"

    FATE™ A3 — deterministic
    """
    current_harm  = _f(current_harm, 0.0)
    baseline_harm = _f(baseline_harm, 0.0)
    dhd         = round(current_harm - baseline_harm, 6)
    dhd_pct     = round(dhd / max(baseline_harm, 0.001) * 100, 4)
    # เฉพาะ harm ที่ "เพิ่ม" — เดิมใช้ abs() ทำให้ harm ที่ลดลง (ดีขึ้น) ก็ถูก stop-the-line
    exceeds     = dhd >= DRIFTZERO["threshold"]
    # (1+|dhd|)^365 ล้น float เมื่อ dhd ใหญ่ (OverflowError) → จำกัดผลไว้ที่ 1e12
    try:
        compounded = round(min((1 + max(dhd, 0.0)) ** 365 - 1, 1e12), 4)  # yearly compound
    except OverflowError:
        compounded = 1e12

    severity = "S0"
    if exceeds and compounded > 0.5:
        severity = "S2"
    elif exceeds:
        severity = "S1"

    return {
        "dhd":              dhd,
        "dhd_percent":      dhd_pct,
        "exceeds_threshold": exceeds,
        "threshold":        DRIFTZERO["threshold"],
        "compounded_yearly": compounded,
        "severity":         severity,
        "rule":             DRIFTZERO["rule"],
        "stop_the_line":    exceeds and severity in ("S2", "S3"),
    }


def check_waterline(waterline: float) -> dict:
    """
    ตรวจ waterline — minimum survivability substrate
    "Water harm = system death"
    """
    floor = WATERLINE["floor"]
    waterline = _f(waterline, 0.0)
    above = waterline >= floor
    gap   = round(waterline - floor, 2)

    if waterline < floor * 0.5:
        severity = "S4"
    elif not above:
        severity = "S3"
    elif gap < 10:
        severity = "S1"
    else:
        severity = "S0"

    return {
        "waterline":       waterline,
        "floor":           floor,
        "above_floor":     above,
        "gap":             gap,
        "severity":        severity,
        "severity_desc":   SEVERITY_SCALE[severity],
        "halt":            not above,
        "response":        WATERLINE["response"] if not above else ["Monitor"],
        "rule":            WATERLINE["rule"],
    }


def run_runtime_sop(decision_input: dict) -> dict:
    """
    รัน 9-step Runtime SOP
    คืน step-by-step audit trail

    FATE™ A5 — Explainability = 100%
    """
    decision_input = decision_input if isinstance(decision_input, dict) else {}
    results = []

    # Step 1 — input
    results.append({"step": 1, "action": "Write decision input", "status": "DONE",
                    "data": decision_input})

    # Step 2 — downside first
    downside = decision_input.get("known_downsides", [])
    results.append({"step": 2, "action": "Identify downside first",
                    "status": "DONE" if downside else "WARNING — no downsides identified",
                    "data": downside})

    # Step 3 — drift
    drift     = _f(decision_input.get("drift", 0.0), 0.0)
    baseline  = _f(decision_input.get("baseline_harm", 0.0), 0.0)
    current   = _f(decision_input.get("current_harm", baseline), baseline)
    dhd       = measure_dhd(current, baseline)
    results.append({"step": 3, "action": "Measure drift impact (DHD)",
                    "status": "OK" if not dhd["exceeds_threshold"] else "ALERT",
                    "data": dhd})

    # Step 4 — waterline
    wl     = _f(decision_input.get("waterline", 50.0), 50.0)
    wl_check = check_waterline(wl)
    results.append({"step": 4, "action": "Check Waterline integrity",
                    "status": "OK" if wl_check["above_floor"] else "HALT",
                    "data": wl_check})

    # Step 5 — stop-the-line
    stop = not wl_check["above_floor"] or dhd["stop_the_line"]
    results.append({"step": 5, "action": "Run Stop-the-Line gate",
                    "status": "STOP" if stop else "CLEAR",
                    "data": {"stop_the_line": stop}})

    # Step 6 — evidence
    evidence = decision_input.get("evidence", [])
    results.append({"step": 6, "action": "Demand evidence, not narrative",
                    "status": "OK" if evidence else "WARNING — no evidence provided",
                    "data": {"evidence_count": len(evidence)}})

    # Step 7 — stabilize
    stable = not stop
    results.append({"step": 7, "action": "Stabilize before optimize",
                    "status": "OK" if stable else "STABILIZE FIRST",
                    "data": {"stable": stable}})

    # Step 8 — human authority
    signer = decision_input.get("human_signer", None)
    results.append({"step": 8, "action": "Human signs responsibility",
                    "status": "OK" if signer else "REQUIRED — no human signer",
                    "data": {"signer": signer}})

    # Step 9 — correction loop
    results.append({"step": 9, "action": "Post-audit correction loop",
                    "status": "SCHEDULED",
                    "data": {"cadence": AUDIT_CADENCE}})

    halt   = stop or not signer
    passed = sum(1 for r in results if "OK" in str(r["status"]) or "DONE" in str(r["status"]))

    return {
        "sop_complete":  True,
        "steps":         results,
        "steps_passed":  passed,
        "halt":          halt,
        "final_lock":    "Fail less. Harm less. Restore more.",
        "equation":      "REALITY + EVIDENCE − OPTIMIZATION DRIFT = GOVERNANCE",
        "checked_at":    time.time(),
    }


def unified_snapshot() -> dict:
    """dump สำหรับ /api/kernel_snapshot"""
    return {
        "kernel":          "Unified World Kernel v1.0",
        "fate_axioms":     FATE_AXIOMS,
        "reality_axioms":  REALITY_AXIOMS,
        "gates":           {k: v["name"] for k, v in ENTERPRISE_GATES.items()},
        "severity_scale":  SEVERITY_SCALE,
        "audit_cadence":   AUDIT_CADENCE,
        "sop":             RUNTIME_SOP,
        "equation":        "REALITY + EVIDENCE − OPTIMIZATION DRIFT = GOVERNANCE",
        "final_lock":      "Fail less. Harm less. Restore more.",
        "non_negotiable":  NON_NEGOTIABLE,
        "compliance": {
            "non_religious": True,
            "non_owned":     True,
            "tool_agnostic": True,
            "human_final":   True,
            "portable":      True,
        },
    }


# ══════════════════════════════════════════════════════════════════
# SELF-TEST
# ══════════════════════════════════════════════════════════════════

def _self_test() -> dict:
    # gate check — all pass
    r1 = run_gate_check({"waterline": 60, "drift": 0.0005, "entropy": 40})
    assert r1["decision_valid"] is True
    assert r1["severity"] == "S0"

    # waterline breach
    r2 = run_gate_check({"waterline": 15, "drift": 0.0005, "entropy": 40})
    assert r2["halt"] is True  # G04 breach
    assert any(g["gate"] == "G04" for g in r2["failed_gates"])

    # DHD
    d1 = measure_dhd(0.002, 0.001)
    assert d1["exceeds_threshold"] is True

    d2 = measure_dhd(0.001, 0.001)
    assert d2["exceeds_threshold"] is False

    # waterline check
    w1 = check_waterline(15.0)
    assert w1["halt"] is True
    assert w1["severity"] in ("S3", "S4", "S2")

    w2 = check_waterline(70.0)
    assert w2["halt"] is False

    # SOP
    sop = run_runtime_sop({
        "waterline": 60,
        "drift": 0.0002,
        "baseline_harm": 0.001,
        "current_harm": 0.0012,
        "evidence": ["data_point_1"],
        "human_signer": "Nithikorn Bunsrang",
        "known_downsides": ["minor delay"],
    })
    assert sop["sop_complete"] is True
    assert sop["halt"] is False

    return {"status": "OK", "module": "unified_world_kernel"}


if __name__ == "__main__":
    import json
    print(json.dumps(unified_snapshot(), indent=2, ensure_ascii=False, default=str))
    print(_self_test())

