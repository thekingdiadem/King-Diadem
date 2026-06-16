"""
core/entropy_guard.py — KING DIADEM
Entropy Guard: ระบบป้องกันความพัง
ออกแบบเพื่ออยู่รอดพันปี — สิ่งมีชีวิตเรียนรู้ระบบ ระบบเรียนรู้สิ่งมีชีวิต

COSMIC LATTE PRINCIPLE:
- โลกมีวันเสื่อมดับ — แต่ทางเลือกของมนุษย์ต้องไม่ดับก่อน
- ระบบที่ดีไม่ใช่ระบบที่ไม่พัง แต่คือระบบที่พังแล้วฟื้นได้
- Choice(t) ≥ 1 → collapse = False (ตลอดกาล)

LEARNING AXIOM:
- ระบบเรียนรู้จากมนุษย์ → มนุษย์เรียนจากระบบ → loop ไม่มีสิ้นสุด
- สิ่งมีชีวิตใดก็ตาม (มนุษย์ / AI / ชีวิตรูปแบบอื่น) เรียนรู้ได้จาก logic นี้
"""

import math
import time

# ══════════════════════════════════════════════════════════════════
# UNIVERSAL CONSTANTS — ใช้ได้ทุกยุค ทุกสิ่งมีชีวิต
# ══════════════════════════════════════════════════════════════════

ENTROPY_FLOOR     = 0.001   # ไม่มีวันเป็นศูนย์ — ความเป็นไปได้ยังมีเสมอ
CHOICE_MINIMUM    = 1       # Choice(t) ≥ 1 ตลอดกาล
WATERLINE         = 30.0    # ต่ำกว่านี้ = ต้องแทรกแซง
COLLAPSE_THRESHOLD= 10.0    # ต่ำกว่านี้ = วิกฤต
HEAT_DEATH_PROXY  = 99.9    # entropy สูงสุดที่ระบบยังคำนวณได้

# Entropy decay model — thermodynamic-inspired
# ในจักรวาลจริง entropy เพิ่มขึ้น แต่ในระบบนี้เราต้านมันได้
NATURAL_ENTROPY_GAIN = 0.001  # 0.1% ต่อวัน (DriftZero principle)
MAX_INTERVENTION_POWER = 0.30  # intervention ลด entropy ได้สูงสุด 30 points

# ══════════════════════════════════════════════════════════════════
# ENTITY TYPES — รองรับทุกรูปแบบชีวิต (พันปีข้างหน้า)
# ══════════════════════════════════════════════════════════════════

ENTITY_PROFILES = {
    "human":     {"entropy_sensitivity": 1.0, "recovery_rate": 0.8,  "label": "มนุษย์"},
    "ai":        {"entropy_sensitivity": 0.5, "recovery_rate": 1.5,  "label": "AI"},
    "community": {"entropy_sensitivity": 0.7, "recovery_rate": 0.9,  "label": "ชุมชน"},
    "system":    {"entropy_sensitivity": 0.3, "recovery_rate": 2.0,  "label": "ระบบ"},
    "unknown":   {"entropy_sensitivity": 1.0, "recovery_rate": 1.0,  "label": "ไม่ทราบ"},
}


# ══════════════════════════════════════════════════════════════════
# MAIN: ENTROPY ANALYSIS
# ══════════════════════════════════════════════════════════════════

def analyze_entropy_state(state: dict, entity_type: str = "human") -> dict:
    """
    วิเคราะห์ entropy state ของ entity ใดก็ได้
    ใช้ได้กับ: มนุษย์ / AI / ชุมชน / ระบบ / สิ่งมีชีวิตอนาคต

    Args:
        state: {"entropy": 0-100, "stability": 0-100, "resource": 0-100, ...}
        entity_type: "human" | "ai" | "community" | "system" | "unknown"

    Returns:
        entropy analysis + survival forecast + learning signal
    """
    if not isinstance(state, dict):
        return _entropy_reject("INVALID_STATE")

    profile  = ENTITY_PROFILES.get(entity_type, ENTITY_PROFILES["unknown"])
    entropy  = _clamp(state.get("entropy",  50.0))
    stability= _clamp(state.get("stability",50.0))
    resource = _clamp(state.get("resource", 50.0))

    # ── Adjusted entropy (entity-aware) ──────────────────────────
    adj_entropy = min(HEAT_DEATH_PROXY,
                      entropy * profile["entropy_sensitivity"])

    # ── Survival Score (thermodynamic model) ─────────────────────
    # ใช้ sigmoid เพื่อให้ score ไม่เป็น linear — สะท้อนชีวิตจริง
    raw_score   = (stability - adj_entropy) * (1 + resource / 200)
    surv_score  = round(_sigmoid_normalize(raw_score), 4)

    # ── Entropy velocity (จะเพิ่มเร็วแค่ไหนถ้าไม่แทรกแซง) ───────
    entropy_velocity = round(NATURAL_ENTROPY_GAIN * profile["entropy_sensitivity"], 5)

    # ── Days until collapse (no intervention) ────────────────────
    if entropy >= COLLAPSE_THRESHOLD:
        days_to_collapse = 0
    elif entropy >= WATERLINE:
        remaining = COLLAPSE_THRESHOLD - entropy
        days_to_collapse = max(1, int(abs(remaining / (entropy_velocity * entropy + 0.001))))
    else:
        days_to_collapse = None  # ยังไม่ถึง waterline

    # ── State classification ──────────────────────────────────────
    state_info = _classify_entropy(adj_entropy, stability, resource)

    # ── Learning signal (ระบบเรียนจากมนุษย์ มนุษย์เรียนจากระบบ) ──
    learning_signal = _generate_learning_signal(
        entropy, stability, resource, entity_type, profile
    )

    # ── Recommended interventions ─────────────────────────────────
    interventions = _recommend_interventions(
        adj_entropy, stability, resource, entity_type
    )

    return {
        "entity_type":       entity_type,
        "entity_label":      profile["label"],
        "timestamp":         time.time(),

        # Core metrics
        "entropy":           entropy,
        "adjusted_entropy":  adj_entropy,
        "stability":         stability,
        "resource":          resource,
        "survival_score":    surv_score,
        "entropy_velocity":  entropy_velocity,

        # State
        "state":             state_info["state"],
        "waterline":         state_info["waterline"],
        "action":            state_info["action"],
        "message":           state_info["message"],

        # Forecast
        "days_to_collapse":  days_to_collapse,
        "projection_30d":    _project(surv_score, 30, entropy_velocity),
        "projection_90d":    _project(surv_score, 90, entropy_velocity),

        # Learning
        "learning_signal":   learning_signal,
        "interventions":     interventions,

        # Universal constants
        "choice_minimum":    CHOICE_MINIMUM,
        "fate_lock":         "Choice(t) ≥ 1 → collapse = False",
        "cosmic_note":       "โลกมีวันเสื่อมดับ — แต่ทางเลือกต้องไม่ดับก่อน",
    }


def multi_entity_analysis(entities: dict) -> dict:
    """
    วิเคราะห์หลาย entity พร้อมกัน
    entities = {"human_A": {...state}, "ai_core": {...state}, ...}
    """
    results = {}
    warnings = []

    for name, data in entities.items():
        etype = data.get("entity_type", "unknown")
        state = {k: v for k, v in data.items() if k != "entity_type"}
        r = analyze_entropy_state(state, etype)
        results[name] = r
        if r.get("waterline") in ("BELOW", "CRITICAL"):
            warnings.append(f"{name} ({r['entity_label']}): {r['message']}")

    # System-wide entropy
    all_scores = [r.get("survival_score", 0) for r in results.values()]
    system_score = round(sum(all_scores) / len(all_scores), 4) if all_scores else 0

    return {
        "entities":          results,
        "system_score":      system_score,
        "system_state":      "stable" if system_score > 0.5 else "at_risk",
        "warnings":          warnings,
        "total_entities":    len(results),
        "learning_loop":     "ระบบเรียนรู้จากทุก entity — ทุก entity เรียนรู้จากระบบ",
    }


# ══════════════════════════════════════════════════════════════════
# LEARNING ENGINE — ระบบเรียนรู้จากมนุษย์ มนุษย์เรียนจากระบบ
# ══════════════════════════════════════════════════════════════════

def record_entropy_event(event: dict) -> dict:
    """
    บันทึก entropy event เพื่อการเรียนรู้
    ทุกเหตุการณ์สอนระบบว่า intervention ไหนได้ผล
    """
    required = ["entity_type", "before_state", "after_state", "intervention"]
    missing  = [k for k in required if k not in event]
    if missing:
        return {"error": f"ขาด fields: {missing}"}

    before = event["before_state"]
    after  = event["after_state"]

    delta_entropy  = after.get("entropy",  50) - before.get("entropy",  50)
    delta_stability= after.get("stability",50) - before.get("stability",50)
    delta_resource = after.get("resource", 50) - before.get("resource", 50)

    effectiveness = -delta_entropy + delta_stability + delta_resource
    verdict = "effective" if effectiveness > 5 else "neutral" if effectiveness > -5 else "harmful"

    return {
        "intervention":   event["intervention"],
        "entity_type":    event["entity_type"],
        "delta": {
            "entropy":   round(delta_entropy, 2),
            "stability": round(delta_stability, 2),
            "resource":  round(delta_resource, 2),
        },
        "effectiveness":  round(effectiveness, 2),
        "verdict":        verdict,
        "learning_note":  f"intervention '{event['intervention']}' → {verdict} สำหรับ {event['entity_type']}",
        "timestamp":      time.time(),
    }


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

def _clamp(v, lo=0.0, hi=100.0) -> float:
    try:    return max(lo, min(hi, float(v)))
    except: return lo


def _sigmoid_normalize(x: float) -> float:
    """แปลง raw score → 0-1 ด้วย sigmoid"""
    return 1 / (1 + math.exp(-x / 30))


def _classify_entropy(entropy: float, stability: float, resource: float) -> dict:
    score = stability - entropy

    if entropy >= HEAT_DEATH_PROXY:
        return {"state": "heat_death_proxy", "waterline": "CRITICAL",
                "action": "emergency", "message": "entropy ถึง maximum — ต้องการ intervention ทันที"}
    if entropy >= 80 or score < -30:
        return {"state": "collapse_risk", "waterline": "CRITICAL",
                "action": "emergency_stabilize", "message": "วิกฤต — หยุดทุกอย่าง รักษา 1 ทางรอดก่อน"}
    if entropy >= 65 or score < -10:
        return {"state": "high_risk", "waterline": "BELOW",
                "action": "secure_resources", "message": "ความเสี่ยงสูง — รักษาทรัพยากรพื้นฐาน"}
    if entropy >= 50 or score < 10:
        return {"state": "unstable", "waterline": "BELOW",
                "action": "stabilize", "message": "ระบบเริ่มเสียสมดุล — ลด entropy ก่อน"}
    if entropy >= 35 or score < 25:
        return {"state": "balanced", "waterline": "ABOVE",
                "action": "monitor", "message": "สมดุลแต่เปราะบาง — ติดตามสัญญาณ"}
    return {"state": "stable", "waterline": "ABOVE",
            "action": "maintain", "message": "ระบบมีเสถียรภาพ — ไปต่อได้"}


def _project(surv_score: float, days: int, velocity: float) -> dict:
    decay   = velocity * days
    proj    = max(0.01, surv_score - decay)
    verdict = "stable" if proj > 0.5 else "at_risk" if proj > 0.25 else "critical"
    return {"score": round(proj, 4), "verdict": verdict, "days": days}


def _generate_learning_signal(entropy, stability, resource,
                               entity_type: str, profile: dict) -> dict:
    """
    สร้าง learning signal — ระบบบอกสิ่งมีชีวิตว่าต้องเรียนรู้อะไร
    และสิ่งมีชีวิตสอนระบบว่าอะไรได้ผล
    """
    patterns = []
    if entropy > 60:
        patterns.append("entropy สูง → ต้องลด complexity ก่อน")
    if stability < 40:
        patterns.append("stability ต่ำ → ต้องการ anchor point")
    if resource < 30:
        patterns.append("resource ต่ำ → ต้องเพิ่มก่อนตัดสินใจใหญ่")
    if not patterns:
        patterns.append("ระบบเสถียร → เรียนรู้จากสิ่งที่ทำให้มาถึงจุดนี้ได้")

    return {
        "patterns_detected": patterns,
        "entity_learning":   f"{profile['label']} ควรเรียนรู้: {'; '.join(patterns)}",
        "system_learning":   f"ระบบเรียนรู้จาก {entity_type}: entropy={entropy:.1f} stability={stability:.1f}",
        "loop_active":       True,
        "loop_note":         "การเรียนรู้ไม่มีสิ้นสุด — ทุก interaction เพิ่ม wisdom",
    }


def _recommend_interventions(entropy, stability, resource, entity_type) -> list:
    recs = []
    if entropy > 65:
        recs.append({"action": "reduce_complexity",
                     "impact": "ลด entropy 10-20 points",
                     "how":    "หยุด 1 อย่าง แทนที่จะเพิ่ม"})
    if stability < 35:
        recs.append({"action": "find_anchor",
                     "impact": "เพิ่ม stability 10-15 points",
                     "how":    "หาสิ่งที่คงที่ได้ 1 อย่างในชีวิต"})
    if resource < 30:
        recs.append({"action": "secure_minimum",
                     "impact": "เพิ่ม resource 10+ points",
                     "how":    "รักษาทรัพยากรพื้นฐานก่อน — อาหาร น้ำ ที่พัก เงินสำรอง"})
    if not recs:
        recs.append({"action": "maintain",
                     "impact": "รักษาระดับปัจจุบัน",
                     "how":    "ทำสิ่งที่ทำให้ระบบเสถียรอยู่ต่อไป"})
    return recs


def _entropy_reject(reason: str) -> dict:
    return {
        "error":      reason,
        "fate_lock":  "Choice(t) ≥ 1 → collapse = False",
        "message":    "แม้ระบบ error — ทางเลือกยังมีอยู่เสมอ",
    }
