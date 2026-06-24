# INTELLIGENCE/risk_engine.py
# KING DIADEM — Risk Engine v2.0
# FATE™ Formula: Risk = Drift × Exposure / Remaining_Choice
# DriftZero Waterline Standard — Fail less. Harm less. Restore more.
#
# PROBLEM กับ v1:
#   - get_drift()     นับ len(log) → ยิ่ง active ใช้งาน ยิ่ง risky (ผิด logic)
#   - get_exposure()  average node_trust ไม่บอก exposure จริง
#   - get_remaining_choice() ใช้ world_history.json["choices"] ที่ไม่เคย update
#
# FIX v2:
#   - drift     = ความเบี่ยงเบนของ decision ล่าสุดจาก baseline (time-decay)
#   - exposure  = สัดส่วนของ node ที่ trust_score ต่ำ (risky nodes)
#   - choice    = จำนวน viable path ที่เหลืออยู่จริง
# -----------------------------------------------------------------

import json, os, math, time
from typing import Union

DATA_PATH = "data"

# ── CONSTANTS ─────────────────────────────────────────────────────
DRIFT_DECAY_HOURS    = 24.0    # drift ลดลงตาม time ถ้าไม่มี event ใหม่
DRIFT_MAX            = 10.0    # ceiling
EXPOSURE_RISKY_THRESHOLD = 0.5 # trust_score < 0.5 = risky node
DEFAULT_CHOICE       = 5       # ถ้าไม่มีข้อมูล → assume 5 choices

# ── RISK STATUS THRESHOLDS ────────────────────────────────────────
STATUS_THRESHOLDS = {
    "COLLAPSE": float("inf"),
    "DANGER":   50.0,
    "WARNING":  20.0,
    "ELEVATED": 10.0,
    "SAFE":      0.0,
}


# ══════════════════════════════════════════════════════════════════
# IO HELPERS
# ══════════════════════════════════════════════════════════════════

def load_json(filename: str, default=None):
    if default is None:
        default = {}
    path = os.path.join(DATA_PATH, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(filename: str, data):
    os.makedirs(DATA_PATH, exist_ok=True)
    path = os.path.join(DATA_PATH, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ══════════════════════════════════════════════════════════════════
# METRIC CALCULATORS
# ══════════════════════════════════════════════════════════════════

def get_drift() -> float:
    """
    Drift = ความเบี่ยงเบนสะสม weighted by recency (time-decayed)

    Logic:
    - อ่าน decision_log.json
    - แต่ละ entry ที่มี "status" != "SAFE" คือ drift event
    - event เก่ากว่า → weight น้อยกว่า (exponential decay)
    - ผลลัพธ์ 0.0 → 10.0
    """
    logs = load_json("decision_log.json", [])
    if not logs:
        return 1.0  # baseline drift เสมอ (ไม่มีข้อมูล ≠ safe)

    now         = time.time()
    decay_secs  = DRIFT_DECAY_HOURS * 3600
    drift_score = 0.0

    for entry in logs:
        ts     = float(entry.get("timestamp", now))
        status = str(entry.get("status", "SAFE")).upper()
        age    = max(now - ts, 0.0)

        # weight: decay ตาม age
        weight = math.exp(-age / decay_secs)

        # contribution: SAFE=0, ELEVATED=1, WARNING=2, DANGER=4, COLLAPSE=10
        severity = {
            "SAFE": 0.0, "ELEVATED": 1.0, "WARNING": 2.0,
            "DANGER": 4.0, "COLLAPSE": 10.0
        }.get(status, 0.5)

        drift_score += severity * weight

    # normalize ให้ไม่เกิน DRIFT_MAX
    return round(min(drift_score, DRIFT_MAX), 4)


def get_exposure() -> float:
    """
    Exposure = สัดส่วน risky nodes ใน system

    Logic:
    - อ่าน node_trust.json  {"node_name": trust_score, …}
    - trust_score ต่ำกว่า threshold = risky
    - exposure = risky_count / total_count  (0.0-1.0)
    - ถ้าไม่มีข้อมูล → 1.0 (worst case, unknown = exposed)
    """
    node_trust = load_json("node_trust.json", {})
    if not node_trust:
        return 1.0  # unknown system = fully exposed

    total  = len(node_trust)
    risky  = sum(
        1 for score in node_trust.values()
        if float(score) < EXPOSURE_RISKY_THRESHOLD
    )

    exposure = risky / total
    return round(exposure, 4)


def get_remaining_choice() -> float:
    """
    Remaining Choice = จำนวน viable path ที่ยังเปิดอยู่

    Logic:
    - อ่าน world_history.json
    - ถ้ามี "open_paths" list → นับ length
    - ถ้ามีแค่ "choices" int → ใช้ตรง
    - ห้ามต่ำกว่า 1 (TITAN CORE: Choice > 0)
    - fallback = DEFAULT_CHOICE
    """
    world = load_json("world_history.json", {})

    # Priority 1: open_paths list
    open_paths = world.get("open_paths")
    if isinstance(open_paths, list):
        return max(float(len(open_paths)), 1.0)

    # Priority 2: explicit choice count
    choices = world.get("choices")
    if choices is not None:
        return max(float(choices), 1.0)

    # Fallback
    return float(DEFAULT_CHOICE)


# ══════════════════════════════════════════════════════════════════
# CORE FORMULA
# Risk = Drift × Exposure / Remaining_Choice
# ══════════════════════════════════════════════════════════════════

def calculate_risk(
    drift:            float,
    exposure:         float,
    remaining_choice: float,
) -> float:
    """
    Returns risk score.
    inf ถ้า remaining_choice <= 0 (collapse state)
    """
    if remaining_choice <= 0:
        return float("inf")
    risk = (drift * exposure) / remaining_choice
    return round(risk, 4)


def _status_from_risk(risk: float) -> str:
    if risk == float("inf"):
        return "COLLAPSE"
    if risk > STATUS_THRESHOLDS["DANGER"]:
        return "DANGER"
    if risk > STATUS_THRESHOLDS["WARNING"]:
        return "WARNING"
    if risk > STATUS_THRESHOLDS["ELEVATED"]:
        return "ELEVATED"
    return "SAFE"


# ══════════════════════════════════════════════════════════════════
# DASHBOARD GENERATOR
# ══════════════════════════════════════════════════════════════════

def generate_dashboard() -> dict:
    """
    Collect metrics → compute risk → return dashboard dict
    """
    drift            = get_drift()
    exposure         = get_exposure()
    remaining_choice = get_remaining_choice()
    risk             = calculate_risk(drift, exposure, remaining_choice)
    status           = _status_from_risk(risk)

    return {
        "timestamp":        time.time(),
        "drift":            drift,
        "exposure":         exposure,
        "remaining_choice": remaining_choice,
        "risk":             risk,
        "status":           status,
        # explainability: แสดง formula ให้เห็น
        "formula":          f"({drift} × {exposure}) / {remaining_choice} = {risk}",
        "waterline":        "BREACH" if remaining_choice <= 0 else "OK",
    }


# ══════════════════════════════════════════════════════════════════
# AUDIT RUNNER
# ══════════════════════════════════════════════════════════════════

def run_audit() -> dict:
    """
    Generate dashboard, append to log, return result.
    """
    dashboard = generate_dashboard()

    logs = load_json("decision_log.json", [])
    logs.append(dashboard)

    # ไม่เก็บ log เกิน 500 entries (prevent drift inflation)
    if len(logs) > 500:
        logs = logs[-500:]

    save_json("decision_log.json", logs)
    return dashboard


# ══════════════════════════════════════════════════════════════════
# EXTERNAL API (ใช้จาก app.py)
# ══════════════════════════════════════════════════════════════════

def assess(context: dict | None = None) -> dict:
    """
    Entry point สำหรับ app.py: `from ENGINE.risk_engine import assess as assess_risk`
    รับ context dict optional เพื่อ override choice count จาก caller
    """
    if context:
        # caller อาจบอก remaining_choice โดยตรง (เช่น จาก simulation)
        explicit_choice = context.get("remaining_choice")
        if explicit_choice is not None:
            drift    = get_drift()
            exposure = get_exposure()
            choice   = max(float(explicit_choice), 1.0)
            risk     = calculate_risk(drift, exposure, choice)
            status   = _status_from_risk(risk)
            return {
                "timestamp":        time.time(),
                "drift":            drift,
                "exposure":         exposure,
                "remaining_choice": choice,
                "risk":             risk,
                "status":           status,
                "formula":          f"({drift} × {exposure}) / {choice} = {risk}",
                "waterline":        "OK",
                "source":           "context_override",
            }

    return generate_dashboard()


# ══════════════════════════════════════════════════════════════════
# CLI TEST
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    result = run_audit()
    print("=== DRIFTZERO DASHBOARD v2 ===")
    for k, v in result.items():
        print(f"  {k:20s}: {v}")
