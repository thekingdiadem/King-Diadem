"""
core/choice_dynamics.py
KING DIADEM™ — Choice Dynamics (Choice Collapse Model เป็นโค้ด)

  Drift(t)     = Σ DHD                                         (≥ 0)
  Choice(t+Δ)  = Choice(t) − Drift(t) − Entropy(t) + Intervention(t)
  Intervention(t) > Drift(t)  →  Choice(t) ไม่ลดลง (stabilizing)
  Choice(t+Δ) ≤ 1  →  EARLY_WARNING  ·  Choice(t+Δ) = 0  →  SYSTEM_PAUSE

State space (domain ของตัวแปรระบบ):
  Choice(t) ∈ ℕ
  Cycle(t), Seal(t), Motion(t), Decision(t), Silence(t), SYSTEM_PAUSE(t) ∈ {0, 1}
  Authority(t), Force(t) ∈ ℝ≥0
  Existence(t) ∈ [0, 9]

เอกสาร: MODELS/choice-collapse-model.md · MODELS/drift-governance-model.md
Deterministic | No random | ค่าที่อ่านไม่ได้ → เลือกทางที่ปลอดภัยไว้ก่อน
"""

import math

CHOICE_EARLY_WARNING = 1     # ตรงกับ AI/freedom_signal.py — Choice ≤ 1 → เตือนทันที

BINARY_VARS = ("Cycle", "Seal", "Motion", "Decision", "Silence", "SYSTEM_PAUSE")
NONNEG_VARS = ("Authority", "Force")
EXISTENCE_RANGE = (0.0, 9.0)


def _num(v, d: float) -> float:
    if isinstance(v, bool):
        return float(v)
    try:
        x = float(v)
    except (TypeError, ValueError):
        return d
    return x if math.isfinite(x) else d


# ═══════════════════════════════════════════════════════════════
# Drift(t) = Σ DHD
# ═══════════════════════════════════════════════════════════════

def accumulate_drift(dhd_series) -> float:
    """
    รวม Daily Harm Delta เป็น Drift สะสม
    DHD ติดลบ/อ่านไม่ได้ไม่ช่วยลด drift — การฟื้นตัวนับผ่าน Intervention(t) เท่านั้น
    """
    if not isinstance(dhd_series, (list, tuple)):
        return 0.0
    return round(sum(max(0.0, _num(d, 0.0)) for d in dhd_series), 6)


# ═══════════════════════════════════════════════════════════════
# Choice(t+Δ) = Choice(t) − Drift(t) − Entropy(t) + Intervention(t)
# ═══════════════════════════════════════════════════════════════

def choice_next(choice, drift, entropy, intervention) -> dict:
    """
    คำนวณทางเลือกในก้าวถัดไป
    Choice ∈ ℕ — ทางเลือกที่ถูกกัดกร่อนไปบางส่วนไม่นับว่ายังใช้ได้ (ปัดลง)
    """
    c = max(0.0, _num(choice, 0.0))           # อ่านไม่ได้ → ถือว่าไม่มีทางเลือก
    d = max(0.0, _num(drift, 0.0))
    e = max(0.0, _num(entropy, 0.0))
    i = max(0.0, _num(intervention, 0.0))

    raw = c - d - e + i
    nxt = max(0, math.floor(raw + 1e-9))       # กัน 2.9999999 จากทศนิยมลอยตัว

    if nxt <= 0:
        status, action = "COLLAPSE", "SYSTEM_PAUSE — Choice = 0 → คืนทางเลือก ≥ 1 แล้วถอยออก"
    elif nxt <= CHOICE_EARLY_WARNING:
        status, action = "EARLY_WARNING", "เหลือทางเลือกสุดท้าย — ต้องลด drift หรือเพิ่ม intervention ตอนนี้"
    else:
        status, action = "STABLE", "SILENCE"

    return {
        "choice": int(math.floor(c)),
        "choice_next": nxt,
        "choice_next_raw": round(raw, 6),
        "drift": d,
        "entropy": e,
        "intervention": i,
        "stabilizing": i > d,
        "status": status,
        "early_warning": nxt <= CHOICE_EARLY_WARNING,
        "system_pause": nxt == 0,
        "action": action,
        "equation": "Choice(t+Δ) = Choice(t) − Drift(t) − Entropy(t) + Intervention(t)",
    }


def steps_to_collapse(choice, drift, entropy, intervention):
    """
    Time_to_Failure — จำนวนก้าวจนทางเลือกเหลือ 0 ถ้าทุกอย่างคงที่
    None = ไม่พัง (intervention ชดเชย drift + entropy ได้)
    """
    c = max(0.0, _num(choice, 0.0))
    loss = max(0.0, _num(drift, 0.0)) + max(0.0, _num(entropy, 0.0)) - max(0.0, _num(intervention, 0.0))
    if c < 1:
        return 0
    if loss <= 0:
        return None
    # หา k ที่เล็กสุดซึ่ง c − k·loss < 1
    return int(math.floor((c - 1) / loss + 1e-9)) + 1


# ═══════════════════════════════════════════════════════════════
# STATE SPACE — domain ของตัวแปรระบบ
# ═══════════════════════════════════════════════════════════════

def validate_state(state: dict) -> dict:
    """
    ตรวจว่าตัวแปรแต่ละตัวอยู่ใน domain ของมัน ไม่แปลงค่าให้เอง
    ตัวที่ไม่ได้ส่งมาไม่ถูกตรวจ · ตัวที่ส่งมาผิด domain → valid = False
    """
    if not isinstance(state, dict):
        return {"valid": False, "violations": ["STATE_NOT_DICT"], "invariant_violations": []}

    v = []

    def _real(x):
        return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)

    if "Choice" in state:
        c = state["Choice"]
        if not (isinstance(c, int) and not isinstance(c, bool) and c >= 0):
            v.append(f"Choice ∉ ℕ: {c!r}")

    for k in BINARY_VARS:
        if k in state and (isinstance(state[k], bool) or state[k] not in (0, 1)):
            v.append(f"{k} ∉ {{0,1}}: {state[k]!r}")

    for k in NONNEG_VARS:
        if k in state and not (_real(state[k]) and state[k] >= 0):
            v.append(f"{k} ∉ ℝ≥0: {state[k]!r}")

    if "Existence" in state:
        x = state["Existence"]
        lo, hi = EXISTENCE_RANGE
        if not (_real(x) and lo <= x <= hi):
            v.append(f"Existence ∉ [0,9]: {x!r}")

    return {"valid": not v, "violations": v, "invariant_violations": check_invariants(state) if not v else []}


def check_invariants(state: dict) -> list:
    """
    กฎที่มีอยู่แล้วในระบบ (ใช้เฉพาะตัวแปรที่ส่งมา):
      |Choice| ≥ 1 ⇒ Cycle = 0          — WHITEPAPER (COSMIC LATTE)
      Choice = 0  ⇒ SYSTEM_PAUSE = 1    — emptiness_guard: system_pause_trigger
    Silence ไม่ผูกกับ Choice อย่างเดียว — Governance_CORE ให้เงียบเมื่อปัจจัยพื้นฐานครบด้วย
    """
    out = []
    c = state.get("Choice")
    if not isinstance(c, int) or isinstance(c, bool):
        return out
    if c >= 1 and state.get("Cycle") == 1:
        out.append("|Choice| ≥ 1 ⇒ Cycle = 0")
    if c == 0 and state.get("SYSTEM_PAUSE") == 0:
        out.append("Choice = 0 ⇒ SYSTEM_PAUSE = 1")
    return out
