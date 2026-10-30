"""
core/choice_dynamics.py
KING DIADEM™ — Choice Dynamics (Choice Collapse Model เป็นโค้ด)

  Drift(t)     = Σ DHD                                         (≥ 0)
  Choice(t+Δ)  = Choice(t) − Drift(t) − Entropy(t) + Intervention(t)
  Intervention(t) > Drift(t)  →  Choice(t) ไม่ลดลง (stabilizing)
  Choice(t+Δ) ≤ 1  →  EARLY_WARNING  ·  Choice(t+Δ) = 0  →  SYSTEM_PAUSE
  Time_to_Failure · Time_to_Intervention · Decision_Window นับเป็นวันจริง (drift ทบต้น 0.1%/วัน)

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

# ความหมายของตัวแปร — ตามที่เจ้าของโปรเจกต์กำหนด
STATE_SPEC = {
    "Choice":       "จำนวนทางเลือกที่ยังปลอดภัย ณ เวลา t (ℕ) — Alive(t) ⟺ Choice(t) ≥ 1",
    "Cycle":        "รอบการประมวลผลของระบบ: 0 = ปิด/ไม่ทำงาน · 1 = เปิด/ทำงาน",
    "Seal":         "ล็อกข้อมูลสถานะ: 0 = แก้ไขได้ · 1 = ปิดผนึก แก้ไขไม่ได้",
    "Motion":       "การเคลื่อนที่ของสถานะ: 0 = นิ่ง · 1 = กำลังเปลี่ยน",
    "Authority":    "ระดับอำนาจควบคุมที่ใช้ (ℝ≥0)",
    "Force":        "แรงที่ใช้ลงมือ (ℝ≥0)",
    "Existence":    "ทางออก/ความอยู่รอดของระบบ: 0 = ล่มสลาย … 9 = มั่นคงเต็มที่",
    "Decision":     "ประตูตัดสินใจ: 0 = ปฏิเสธ/ระงับ · 1 = อนุมัติ/ดำเนินการ",
    "Silence":      "ความเงียบของระบบ: 0 = ทำงานปกติ · 1 = เงียบ",
    "SYSTEM_PAUSE": "สวิตช์หยุดฉุกเฉิน (stop-the-line): 0 = เดินต่อ · 1 = หยุด",
}

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
# เวลาจริง (วัน) — Time_to_Failure · Time_to_Intervention · Decision_Window
# Collapse = 0.1% daily drift compounding: drift วันที่ k = drift × (1 + 0.001)^k
# ═══════════════════════════════════════════════════════════════

DRIFT_COMPOUND_DAILY = 0.001     # 0.1% ต่อวัน — ตรงกับ DRIFT_MAX_DAILY ใน AI/freedom_signal.py
HORIZON_DAYS = 36500             # มองไกลสุด 100 ปี — เกินนี้ถือว่าไม่พังในกรอบที่วัดได้


def compounded_drift(days, rate=DRIFT_COMPOUND_DAILY) -> float:
    """drift ทบต้นรายวันสะสมเป็นสัดส่วน: 0.1% × 365 วัน ≈ 0.44 (เสื่อมราว 44% ใน 1 ปี)"""
    n = max(0.0, _num(days, 0.0))
    r = max(0.0, _num(rate, DRIFT_COMPOUND_DAILY))
    return round((1 + r) ** n - 1, 6)


def time_windows(choice, drift_per_day, entropy_per_day=0.0, intervention_per_day=0.0,
                 compound=DRIFT_COMPOUND_DAILY) -> dict:
    """
    นับเป็นวันจริง โดยเดิน Choice(t+1) = Choice(t) − Drift(t) − Entropy + Intervention ทีละวัน
    และให้ Drift(t) โตแบบทบต้น compound ต่อวัน

      Time_to_Failure      = วันแรกที่ทางเลือกเหลือ 0
      Time_to_Intervention = วันแรกที่ทางเลือกเหลือ ≤ 1 (ต้องแทรกแซงก่อนวันนี้)
      Decision_Window      = จำนวนวันที่ยังมีทางเลือกมากกว่า 1 ทาง (นับจากวันนี้ถึงจุดแทรกแซง)
    status: ≤ 7 วัน → EARLY_WARNING · ≤ 30 วัน → WATCH · ที่เหลือ → STABLE
    None = ไม่ถึงจุดนั้นภายใน 100 ปี
    """
    c = max(0.0, _num(choice, 0.0))                    # อ่านไม่ได้ → ถือว่าไม่มีทางเลือก
    d = max(0.0, _num(drift_per_day, 0.0))
    e = max(0.0, _num(entropy_per_day, 0.0))
    i = max(0.0, _num(intervention_per_day, 0.0))
    g = max(0.0, _num(compound, DRIFT_COMPOUND_DAILY))

    def count(x):                                      # Choice ∈ ℕ — ปัดลงแบบเดียวกับ choice_next
        return max(0, math.floor(x + 1e-9))

    ttf = tti = 0 if count(c) <= 0 else None
    if tti is None and count(c) <= CHOICE_EARLY_WARNING:
        tti = 0
    raw, day = c, 0
    while ttf is None and day < HORIZON_DAYS:
        if (g == 0 or d == 0) and d + e <= i:
            break                                      # drift ไม่โต และไม่มีวันลดลง — ไม่ต้องเดินต่อ
        raw = raw - d * (1 + g) ** day - e + i
        day += 1
        n = count(raw)
        if tti is None and n <= CHOICE_EARLY_WARNING:
            tti = day
        if n <= 0:
            ttf = day

    window = tti if tti is not None else None
    if tti == 0:
        status = "COLLAPSE" if ttf == 0 else "EARLY_WARNING"
    elif tti is None:
        status = "STABLE"
    else:
        status = "EARLY_WARNING" if tti <= 7 else "WATCH" if tti <= 30 else "STABLE"

    return {
        "time_to_failure_days": ttf,
        "time_to_intervention_days": tti,
        "decision_window_days": window,
        "status": status,
        "early_warning": tti is not None and tti <= 7,
        "inputs": {"choice": c, "drift_per_day": d, "entropy_per_day": e,
                   "intervention_per_day": i, "compound_daily": g},
        "rule": "Choice(t + Δ) ≤ 1 → แจ้งเตือน · Choice(t + Δ) = 0 → Collapse",
    }


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
      SYSTEM_PAUSE = 1 ⇒ Decision = 0   — หยุดฉุกเฉินอยู่ อนุมัติ/ดำเนินการไม่ได้
    Silence ไม่ผูกกับ Choice อย่างเดียว — Governance_CORE ให้เงียบเมื่อปัจจัยพื้นฐานครบด้วย
    """
    out = []
    if not isinstance(state, dict):
        return out
    if state.get("SYSTEM_PAUSE") == 1 and state.get("Decision") == 1:
        out.append("SYSTEM_PAUSE = 1 ⇒ Decision = 0")
    c = state.get("Choice")
    if not isinstance(c, int) or isinstance(c, bool):
        return out
    if c >= 1 and state.get("Cycle") == 1:
        out.append("|Choice| ≥ 1 ⇒ Cycle = 0")
    if c == 0 and state.get("SYSTEM_PAUSE") == 0:
        out.append("Choice = 0 ⇒ SYSTEM_PAUSE = 1")
    return out
