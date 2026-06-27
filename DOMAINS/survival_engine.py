# =============================================================================
# DOMAINS/survival_engine.py — KING DIADEM
# Survival Domain Engine v2.0
#
# สามชั้น:
#   1. Personal Survival     — energy/stress/food/shelter (ตัวเดิม)
#   2. Medical/Genomic       — symptom pattern → risk → decision support
#   3. Global Event          — pandemic/collapse/war/climate → minimum viable path
#
# หลักการ FATE™:
#   - ไม่มี random ทุกค่าคำนวณจาก input จริง
#   - ทุก output อธิบายย้อนกลับได้ ("ถ้าอธิบายไม่ได้ = ใช้ไม่ได้")
#   - Choice(t) ≥ 1 เสมอ — ถ้า 0 = SYSTEM_PAUSE
#   - ไม่วินิจฉัยแทนหมอ — เป็น decision support เท่านั้น
#
# Import ใน app.py:
#   from DOMAINS.survival_engine import (
#       analyze_survival,
#       analyze_medical_risk,
#       analyze_global_event,
#       full_survival_assessment,
#   )
# =============================================================================

import time
import math
from typing import Optional

try:
    from ENGINE.realhuman_survivorengine import (
        RealHumanSurvivorEngine,
        parse_state_from_context,
    )
    _engine = RealHumanSurvivorEngine()
    _REAL_ENGINE = True
except Exception:
    _engine = None
    _REAL_ENGINE = False


# =============================================================================
# LAYER 1 — PERSONAL SURVIVAL (ตัวเดิม + ปรับปรุง)
# =============================================================================

def analyze_survival(context: dict) -> dict:
    """
    ประเมิน survival state ของมนุษย์คนเดียว
    Input: energy, stress, sleep_hours, money, food_access, safe_place
    Output: waterline, entropy, recommended_path, can_decide
    """
    if _REAL_ENGINE and _engine:
        state  = parse_state_from_context(context)
        output = _engine.run(state)
        return {
            "domain":           "survival",
            "layer":            "personal",
            "timestamp":        time.time(),
            "status":           output.status,
            "priority":         output.priority,
            "waterline":        round(output.waterline, 1),
            "can_decide":       output.can_decide,
            "flags":            output.flags,
            "context_for_lyla": output.context_for_lyla,
            "recommended_path": _status_to_path(output.status),
            "choices_remaining": _count_choices(output),
            "input":            context,
        }

    # Fallback deterministic
    energy  = float(context.get("energy",        50))
    stress  = float(context.get("stress",         50))
    sleep   = float(context.get("sleep_hours",     6))
    money   = float(context.get("money",           0))
    food    = bool(context.get("food_access",   True))
    shelter = bool(context.get("safe_place",    True))
    social  = bool(context.get("social_support",True))

    entropy = (stress * 0.45) + ((100 - energy) * 0.28) + (max(0, 6 - sleep) * 3.2)
    if not food:    entropy += 28
    if not shelter: entropy += 38
    if money <= 0:  entropy += 12
    if not social:  entropy += 8
    entropy  = min(100.0, max(0.0, entropy))
    stability = max(0.0, 100.0 - entropy)
    score     = stability - (entropy * 0.28)

    path     = "stable_survival" if score > 55 else ("adapt" if score > 30 else "critical_risk")
    choices  = max(1, int((score / 100) * 6))   # 1–6 viable paths

    return {
        "domain":            "survival",
        "layer":             "personal",
        "timestamp":         time.time(),
        "entropy":           round(entropy, 1),
        "stability":         round(stability, 1),
        "survival_score":    round(score, 1),
        "waterline":         round(stability, 1),
        "recommended_path":  path,
        "can_decide":        entropy < 62,
        "choices_remaining": choices,
        "fate_axiom":        "Choice(t) >= 1" if choices >= 1 else "SYSTEM_PAUSE",
        "input":             context,
    }


# =============================================================================
# LAYER 2 — MEDICAL / GENOMIC DECISION SUPPORT
# ไม่วินิจฉัยแทนหมอ — ระบุความเสี่ยงและทางเลือกที่มีอยู่
# =============================================================================

# Risk weight table — based on established epidemiological patterns
# source logic: symptom clusters → system stress index
_SYMPTOM_WEIGHTS = {
    # Cardiovascular
    "chest_pain":          {"weight": 9.0, "system": "cardiovascular", "urgency": "immediate"},
    "shortness_of_breath": {"weight": 7.5, "system": "respiratory",    "urgency": "urgent"},
    "palpitations":        {"weight": 5.0, "system": "cardiovascular", "urgency": "soon"},
    "edema":               {"weight": 4.5, "system": "cardiovascular", "urgency": "soon"},

    # Neurological
    "sudden_headache":     {"weight": 8.0, "system": "neurological",   "urgency": "immediate"},
    "confusion":           {"weight": 7.0, "system": "neurological",   "urgency": "immediate"},
    "vision_change":       {"weight": 6.5, "system": "neurological",   "urgency": "urgent"},
    "weakness_one_side":   {"weight": 9.0, "system": "neurological",   "urgency": "immediate"},
    "seizure":             {"weight": 9.5, "system": "neurological",   "urgency": "immediate"},

    # Metabolic
    "extreme_thirst":      {"weight": 5.0, "system": "metabolic",      "urgency": "soon"},
    "frequent_urination":  {"weight": 4.0, "system": "metabolic",      "urgency": "monitor"},
    "unexplained_weight_loss": {"weight": 6.0, "system": "metabolic",  "urgency": "soon"},
    "fatigue_severe":      {"weight": 4.5, "system": "metabolic",      "urgency": "monitor"},

    # Infection/Immune
    "high_fever":          {"weight": 6.0, "system": "immune",         "urgency": "urgent"},
    "rash_spreading":      {"weight": 5.5, "system": "immune",         "urgency": "urgent"},
    "swollen_lymph_nodes": {"weight": 5.0, "system": "immune",         "urgency": "soon"},
    "persistent_cough":    {"weight": 4.5, "system": "respiratory",    "urgency": "monitor"},

    # Gastrointestinal
    "severe_abdominal_pain": {"weight": 7.5, "system": "gastrointestinal", "urgency": "urgent"},
    "blood_in_stool":      {"weight": 7.0, "system": "gastrointestinal", "urgency": "urgent"},
    "jaundice":            {"weight": 7.5, "system": "hepatic",        "urgency": "urgent"},

    # Mental health (also affects physical survival)
    "suicidal_ideation":   {"weight": 10.0,"system": "psychiatric",    "urgency": "immediate"},
    "severe_anxiety":      {"weight": 5.0, "system": "psychiatric",    "urgency": "soon"},
    "psychosis_signs":     {"weight": 8.0, "system": "psychiatric",    "urgency": "immediate"},
}

# Genomic risk modifiers — known pathogenic variant associations
# (simplified — for decision support only, not clinical diagnosis)
_GENOMIC_RISK_MODIFIERS = {
    "BRCA1_variant":      {"multiplier": 1.8, "systems": ["oncological"]},
    "BRCA2_variant":      {"multiplier": 1.6, "systems": ["oncological"]},
    "APOE4_variant":      {"multiplier": 1.5, "systems": ["neurological", "cardiovascular"]},
    "MTHFR_variant":      {"multiplier": 1.2, "systems": ["cardiovascular", "metabolic"]},
    "Factor_V_Leiden":    {"multiplier": 1.4, "systems": ["cardiovascular"]},
    "HbS_sickle_cell":    {"multiplier": 1.7, "systems": ["hematological"]},
    "CFTR_variant":       {"multiplier": 1.6, "systems": ["respiratory"]},
    "Lynch_syndrome":     {"multiplier": 1.9, "systems": ["oncological", "gastrointestinal"]},
}

# Comorbidity risk stacking
_COMORBIDITY_WEIGHTS = {
    "diabetes":           3.5,
    "hypertension":       3.0,
    "heart_disease":      5.0,
    "copd":               4.0,
    "kidney_disease":     4.5,
    "liver_disease":      4.5,
    "immunocompromised":  5.5,
    "obesity":            2.5,
    "cancer_history":     4.0,
    "autoimmune":         3.0,
}


def analyze_medical_risk(
    symptoms: list,
    age: int = 40,
    comorbidities: Optional[list] = None,
    genomic_variants: Optional[list] = None,
    vital_signs: Optional[dict] = None,
    duration_days: int = 1,
) -> dict:
    """
    Medical risk assessment — decision support เท่านั้น
    ไม่ใช่การวินิจฉัยทางการแพทย์

    Input:
        symptoms:         list of symptom keys (see _SYMPTOM_WEIGHTS)
        age:              อายุผู้ป่วย
        comorbidities:    โรคประจำตัว (list of keys from _COMORBIDITY_WEIGHTS)
        genomic_variants: known variants (list of keys from _GENOMIC_RISK_MODIFIERS)
        vital_signs:      {"bp_systolic":X, "bp_diastolic":X, "pulse":X,
                           "temp_c":X, "spo2":X, "rbs":X}
        duration_days:    อาการเป็นมากี่วันแล้ว

    Output:
        risk_score 0–100, urgency_level, affected_systems,
        recommended_action, choices, fate_note
    """
    comorbidities    = comorbidities    or []
    genomic_variants = genomic_variants or []
    vital_signs      = vital_signs      or {}
    symptoms         = [s.lower().replace(" ","_") for s in symptoms]

    # ── Symptom scoring ──────────────────────────────────────────
    symptom_score   = 0.0
    affected_systems = set()
    urgency_flags    = []

    for sym in symptoms:
        if sym in _SYMPTOM_WEIGHTS:
            w = _SYMPTOM_WEIGHTS[sym]
            symptom_score   += w["weight"]
            affected_systems.add(w["system"])
            if w["urgency"] in ("immediate", "urgent"):
                urgency_flags.append({"symptom": sym, "urgency": w["urgency"]})
        else:
            symptom_score += 2.0   # unknown symptom = baseline 2

    # ── Vital signs deviation ─────────────────────────────────────
    vital_penalty = 0.0
    vital_notes   = []

    bp_sys = vital_signs.get("bp_systolic", 120)
    bp_dia = vital_signs.get("bp_diastolic", 80)
    pulse  = vital_signs.get("pulse", 75)
    temp   = vital_signs.get("temp_c", 37.0)
    spo2   = vital_signs.get("spo2", 98)
    rbs    = vital_signs.get("rbs", 100)   # random blood sugar mg/dL

    if bp_sys > 180 or bp_sys < 80:
        vital_penalty += 8.0
        vital_notes.append(f"BP critical: {bp_sys}/{bp_dia}")
    elif bp_sys > 140:
        vital_penalty += 4.0
        vital_notes.append(f"BP elevated: {bp_sys}/{bp_dia}")

    if pulse > 130 or pulse < 40:
        vital_penalty += 7.0
        vital_notes.append(f"Pulse critical: {pulse}")
    elif pulse > 100 or pulse < 55:
        vital_penalty += 3.0

    if temp > 39.5:
        vital_penalty += 6.0
        vital_notes.append(f"High fever: {temp}°C")
    elif temp > 38.5:
        vital_penalty += 3.0

    if spo2 < 88:
        vital_penalty += 10.0
        vital_notes.append(f"SpO2 critical: {spo2}%")
    elif spo2 < 94:
        vital_penalty += 5.0
        vital_notes.append(f"SpO2 low: {spo2}%")

    if rbs > 400 or rbs < 50:
        vital_penalty += 7.0
        vital_notes.append(f"Blood sugar critical: {rbs}")
    elif rbs > 250 or rbs < 70:
        vital_penalty += 3.5

    # ── Comorbidity stack ─────────────────────────────────────────
    comorbidity_score = sum(
        _COMORBIDITY_WEIGHTS.get(c.lower().replace(" ","_"), 2.0)
        for c in comorbidities
    )

    # ── Age modifier ──────────────────────────────────────────────
    if age >= 80:   age_mod = 1.45
    elif age >= 65: age_mod = 1.28
    elif age >= 50: age_mod = 1.12
    elif age <= 5:  age_mod = 1.20
    else:           age_mod = 1.00

    # ── Duration modifier ─────────────────────────────────────────
    duration_mod = min(1.5, 1.0 + (duration_days - 1) * 0.05)

    # ── Base risk score ───────────────────────────────────────────
    base_score = (symptom_score + vital_penalty + comorbidity_score) * age_mod * duration_mod
    base_score = min(100.0, base_score)

    # ── Genomic modifier ─────────────────────────────────────────
    genomic_note = []
    genomic_mult = 1.0
    for variant in genomic_variants:
        v = variant.replace(" ", "_")
        if v in _GENOMIC_RISK_MODIFIERS:
            gdata = _GENOMIC_RISK_MODIFIERS[v]
            # apply only if affected system overlaps
            if any(s in affected_systems for s in gdata["systems"]) or not affected_systems:
                genomic_mult = max(genomic_mult, gdata["multiplier"])
                genomic_note.append(f"{v}: ×{gdata['multiplier']}")
                for sys in gdata["systems"]:
                    affected_systems.add(sys)

    final_score = min(100.0, base_score * genomic_mult)

    # ── Urgency determination ─────────────────────────────────────
    immediate_flags = [f for f in urgency_flags if f["urgency"] == "immediate"]
    if final_score >= 75 or immediate_flags or (spo2 < 90) or (bp_sys > 185):
        urgency = "IMMEDIATE"       # ER ทันที
    elif final_score >= 50 or vital_penalty >= 5:
        urgency = "URGENT"          # พบแพทย์วันนี้
    elif final_score >= 30:
        urgency = "SOON"            # พบแพทย์ใน 24-48h
    elif final_score >= 15:
        urgency = "MONITOR"         # ติดตามอาการ
    else:
        urgency = "ROUTINE"         # ตรวจสุขภาพตามปกติ

    # ── Recommended actions (choices) ────────────────────────────
    actions = _build_medical_actions(urgency, affected_systems, vital_notes, genomic_note)

    return {
        "domain":            "medical",
        "layer":             "medical_genomic",
        "timestamp":         time.time(),
        "risk_score":        round(final_score, 1),
        "urgency":           urgency,
        "affected_systems":  sorted(affected_systems),
        "symptom_count":     len(symptoms),
        "vital_notes":       vital_notes,
        "genomic_modifiers": genomic_note,
        "comorbidity_count": len(comorbidities),
        "recommended_actions": actions,
        "choices_remaining": len(actions),
        "fate_axiom":        "Choice(t) >= 1" if actions else "SYSTEM_PAUSE — หาทางออกด่วน",
        "disclaimer":        "นี่คือ decision support เท่านั้น — ไม่ใช่การวินิจฉัยทางการแพทย์ ต้องพบแพทย์จริง",
        "can_decide":        final_score < 80,
        "input": {
            "symptoms": symptoms, "age": age,
            "comorbidities": comorbidities,
            "duration_days": duration_days,
        },
    }


def _build_medical_actions(urgency, systems, vital_notes, genomic_notes):
    """สร้างทางเลือกที่เป็นรูปธรรม ตาม urgency และ systems ที่ affected"""
    actions = []

    if urgency == "IMMEDIATE":
        actions.append({"priority": 1, "action": "โทร 1669 / ไปห้องฉุกเฉินทันที", "type": "emergency"})
        actions.append({"priority": 2, "action": "ห้ามขับรถเอง — โทรหาคนช่วยพา", "type": "safety"})
        if vital_notes:
            actions.append({"priority": 3, "action": f"แจ้งแพทย์: {', '.join(vital_notes[:3])}", "type": "information"})

    elif urgency == "URGENT":
        actions.append({"priority": 1, "action": "พบแพทย์วันนี้ — OPD หรือคลินิกใกล้บ้าน", "type": "medical"})
        actions.append({"priority": 2, "action": "จดบันทึกอาการและเวลาที่เริ่ม", "type": "preparation"})
        if "cardiovascular" in systems:
            actions.append({"priority": 3, "action": "หลีกเลี่ยงกิจกรรมหนัก — พักผ่อน", "type": "self_care"})
        if "metabolic" in systems:
            actions.append({"priority": 3, "action": "วัดน้ำตาลในเลือดถ้าเป็นเบาหวาน", "type": "monitoring"})

    elif urgency == "SOON":
        actions.append({"priority": 1, "action": "นัดพบแพทย์ใน 24-48 ชั่วโมง", "type": "medical"})
        actions.append({"priority": 2, "action": "บันทึกอาการรายวัน", "type": "monitoring"})
        actions.append({"priority": 3, "action": "พักผ่อนให้เพียงพอ ดื่มน้ำมากๆ", "type": "self_care"})

    elif urgency == "MONITOR":
        actions.append({"priority": 1, "action": "ติดตามอาการ 48-72 ชั่วโมง", "type": "monitoring"})
        actions.append({"priority": 2, "action": "ถ้าแย่ลง → พบแพทย์ทันที", "type": "escalation"})
        actions.append({"priority": 3, "action": "พักผ่อน ลดความเครียด", "type": "self_care"})

    else:  # ROUTINE
        actions.append({"priority": 1, "action": "ตรวจสุขภาพประจำปี", "type": "preventive"})
        actions.append({"priority": 2, "action": "ออกกำลังกายสม่ำเสมอ", "type": "wellness"})

    if genomic_notes:
        actions.append({
            "priority": 99,
            "action": f"มีความเสี่ยงทางพันธุกรรม ({', '.join(genomic_notes[:2])}) — ปรึกษา genetic counselor",
            "type": "genomic"
        })

    return sorted(actions, key=lambda x: x["priority"])


# =============================================================================
# LAYER 3 — GLOBAL EVENT SURVIVAL
# FATE™: ไม่ว่าเหตุการณ์ใหญ่แค่ไหน ต้องหาทางรอดขั้นต่ำได้
# =============================================================================

_EVENT_PROFILES = {
    "pandemic": {
        "base_threat": 65,
        "critical_resources": ["food", "water", "medicine", "shelter", "communication"],
        "time_horizon_days": 90,
        "primary_risk": "healthcare_system_collapse",
    },
    "economic_collapse": {
        "base_threat": 55,
        "critical_resources": ["money_equivalent", "food", "community", "skills"],
        "time_horizon_days": 180,
        "primary_risk": "resource_access_loss",
    },
    "war_conflict": {
        "base_threat": 80,
        "critical_resources": ["shelter", "food", "water", "safe_route", "information"],
        "time_horizon_days": 30,
        "primary_risk": "physical_safety",
    },
    "climate_disaster": {
        "base_threat": 70,
        "critical_resources": ["water", "shelter", "food", "evacuation_route"],
        "time_horizon_days": 14,
        "primary_risk": "infrastructure_loss",
    },
    "power_grid_failure": {
        "base_threat": 50,
        "critical_resources": ["water", "food", "warmth_or_cooling", "communication"],
        "time_horizon_days": 14,
        "primary_risk": "supply_chain_disruption",
    },
    "food_shortage": {
        "base_threat": 60,
        "critical_resources": ["food", "water", "seeds_or_substitutes", "community"],
        "time_horizon_days": 60,
        "primary_risk": "nutrition_collapse",
    },
    "epidemic_unknown": {
        "base_threat": 72,
        "critical_resources": ["isolation_space", "medicine", "food", "water"],
        "time_horizon_days": 45,
        "primary_risk": "infection_spread",
    },
    "political_crisis": {
        "base_threat": 45,
        "critical_resources": ["information", "community", "legal_options", "financial_reserve"],
        "time_horizon_days": 120,
        "primary_risk": "institutional_failure",
    },
}


def analyze_global_event(
    event_type: str,
    location_context: Optional[dict] = None,
    personal_resources: Optional[dict] = None,
    severity: float = 50.0,         # 0–100: local incident → civilization-level
    affected_population: int = 1,   # คนที่ต้องดูแล
) -> dict:
    """
    Global event survival analysis — FATE™ layer

    Input:
        event_type:          ประเภทเหตุการณ์ (key ใน _EVENT_PROFILES)
        location_context:    {"urban": True, "has_car": True, "near_hospital": True, ...}
        personal_resources:  {"food_days": 7, "water_liters": 20, "cash": 5000,
                              "medicine_supply": 3, "network_size": 10}
        severity:            0=rumor, 100=civilization collapse
        affected_population: จำนวนคนที่ต้องดูแลรวม (กระทบการคำนวณ resource)

    Output:
        threat_level, days_viable, minimum_viable_path,
        resource_gaps, immediate_actions, 30day_strategy
    """
    location_context  = location_context  or {}
    personal_resources = personal_resources or {}

    event_type_clean = event_type.lower().replace(" ", "_")
    profile = _EVENT_PROFILES.get(event_type_clean, {
        "base_threat": 50,
        "critical_resources": ["food", "water", "shelter"],
        "time_horizon_days": 30,
        "primary_risk": "unknown",
    })

    # ── Threat calculation ────────────────────────────────────────
    base_threat  = profile["base_threat"]
    severity_mod = severity / 100.0
    threat_score = base_threat * (0.4 + 0.6 * severity_mod)

    # Location modifiers
    urban       = bool(location_context.get("urban", True))
    has_vehicle = bool(location_context.get("has_car", False))
    near_hosp   = bool(location_context.get("near_hospital", False))
    near_water  = bool(location_context.get("near_water_source", False))

    if urban and event_type_clean in ("war_conflict", "food_shortage"):
        threat_score *= 1.15   # เมืองเปราะบางกว่าในเหตุการณ์เหล่านี้
    if urban and event_type_clean in ("pandemic", "epidemic_unknown"):
        threat_score *= 1.20   # แพร่เชื้อเร็วกว่าในเมือง

    threat_score = min(100.0, threat_score)

    # ── Resource viability ────────────────────────────────────────
    food_days    = float(personal_resources.get("food_days", 3)) / max(1, affected_population)
    water_liters = float(personal_resources.get("water_liters", 5)) / max(1, affected_population)
    cash         = float(personal_resources.get("cash", 0))
    medicine     = float(personal_resources.get("medicine_supply", 0))   # days
    network      = int(personal_resources.get("network_size", 1))        # คนที่ช่วยได้

    # Minimum viable days before critical resource depletion
    water_days      = water_liters / 2.0   # 2L/person/day minimum
    viable_days     = min(food_days, water_days, medicine if medicine > 0 else 999)
    viable_days     = max(0.5, viable_days)

    # ── Resource gaps ─────────────────────────────────────────────
    critical = profile["critical_resources"]
    gaps     = []

    if food_days < 7:
        gaps.append({"resource": "food", "days_remaining": round(food_days,1), "gap_severity": "high" if food_days < 3 else "medium"})
    if water_days < 3:
        gaps.append({"resource": "water", "days_remaining": round(water_days,1), "gap_severity": "critical" if water_days < 1 else "high"})
    if cash < 1000 and "money_equivalent" in critical:
        gaps.append({"resource": "cash_reserve", "days_remaining": 0, "gap_severity": "medium"})
    if medicine < 7 and event_type_clean in ("pandemic", "epidemic_unknown"):
        gaps.append({"resource": "medicine", "days_remaining": round(medicine,1), "gap_severity": "high"})
    if network < 3:
        gaps.append({"resource": "social_network", "days_remaining": None, "gap_severity": "medium"})

    # ── Immediate actions (first 72 hours) ───────────────────────
    immediate = _build_immediate_actions(
        event_type_clean, threat_score, gaps,
        location_context, profile
    )

    # ── 30-day strategy ──────────────────────────────────────────
    strategy_30d = _build_30day_strategy(
        event_type_clean, viable_days, gaps, network,
        urban, has_vehicle, near_water
    )

    # ── FATE™ minimum viable path ────────────────────────────────
    mvp = _minimum_viable_path(threat_score, viable_days, gaps, event_type_clean)

    threat_label = (
        "EXTREME"   if threat_score >= 80 else
        "HIGH"      if threat_score >= 60 else
        "MODERATE"  if threat_score >= 40 else
        "LOW"       if threat_score >= 20 else
        "MINIMAL"
    )

    return {
        "domain":              "global_event",
        "layer":               "global_survival",
        "timestamp":           time.time(),
        "event_type":          event_type_clean,
        "threat_score":        round(threat_score, 1),
        "threat_level":        threat_label,
        "primary_risk":        profile["primary_risk"],
        "viable_days":         round(viable_days, 1),
        "resource_gaps":       gaps,
        "immediate_actions":   immediate,
        "strategy_30d":        strategy_30d,
        "minimum_viable_path": mvp,
        "choices_remaining":   len(immediate) + len(strategy_30d),
        "fate_axiom":          "Choice(t) >= 1" if (immediate or strategy_30d) else "SYSTEM_PAUSE",
        "fate_principle":      "ทางรอดก่อน ความรู้ทีหลัง",
        "can_decide":          threat_score < 85,
        "input": {
            "event_type": event_type, "severity": severity,
            "affected_population": affected_population,
        },
    }


def _build_immediate_actions(event_type, threat, gaps, location, profile):
    """72-hour immediate action plan"""
    actions = []
    priority = 1

    # Water first — always
    water_gap = next((g for g in gaps if g["resource"] == "water"), None)
    if water_gap:
        actions.append({
            "priority": priority,
            "timeframe": "now",
            "action": "หาแหล่งน้ำสะอาด / เติมน้ำให้ได้ 3–7 วัน",
            "category": "water",
            "non_negotiable": True,
        })
        priority += 1

    # Food second
    food_gap = next((g for g in gaps if g["resource"] == "food"), None)
    if food_gap and food_gap["days_remaining"] < 3:
        actions.append({
            "priority": priority,
            "timeframe": "today",
            "action": "หาอาหารสำหรับ 7 วัน — ข้าวสาร ถั่ว อาหารกระป๋อง",
            "category": "food",
            "non_negotiable": True,
        })
        priority += 1

    # Event-specific immediate
    if event_type == "pandemic":
        actions.append({"priority": priority, "timeframe": "now", "action": "ลด social contact ทันที — work from home ถ้าได้", "category": "isolation"})
        priority += 1
        actions.append({"priority": priority, "timeframe": "today", "action": "เตรียมหน้ากาก ยา paracetamol ORS สำหรับ 14 วัน", "category": "medical_prep"})

    elif event_type == "war_conflict":
        actions.append({"priority": priority, "timeframe": "now", "action": "ประเมิน exit route — รู้ทางออกอย่างน้อย 2 เส้นทาง", "category": "evacuation"})
        priority += 1
        actions.append({"priority": priority, "timeframe": "now", "action": "เตรียม go-bag: เอกสารสำคัญ ยา น้ำ อาหาร 72h", "category": "preparation"})

    elif event_type == "climate_disaster":
        actions.append({"priority": priority, "timeframe": "now", "action": "ติดตาม official alert — พร้อม evacuate ใน 30 นาที", "category": "monitoring"})
        priority += 1
        if not location.get("urban"):
            actions.append({"priority": priority, "timeframe": "soon", "action": "ย้ายไปจุดสูงกว่า / ห่างจากแหล่งน้ำที่เสี่ยง", "category": "evacuation"})

    elif event_type == "economic_collapse":
        actions.append({"priority": priority, "timeframe": "today", "action": "ถอนเงินสดบางส่วน — ระบบธนาคารอาจขัดข้อง", "category": "financial"})
        priority += 1
        actions.append({"priority": priority, "timeframe": "week", "action": "ติดต่อเครือข่าย community — แลกเปลี่ยนทักษะ/สินค้า", "category": "community"})

    elif event_type == "power_grid_failure":
        actions.append({"priority": priority, "timeframe": "now", "action": "ชาร์จอุปกรณ์ทุกชิ้นทันที / เติมน้ำมัน", "category": "preparation"})
        priority += 1
        actions.append({"priority": priority, "timeframe": "today", "action": "เตรียมไฟฉาย เทียน อาหารไม่ต้องแช่เย็น", "category": "supplies"})

    # Information — always important
    actions.append({
        "priority": 99,
        "timeframe": "ongoing",
        "action": "ติดตามข้อมูลจากแหล่งที่เชื่อถือได้ — หลีกเลี่ยง rumor",
        "category": "information",
        "non_negotiable": False,
    })

    return sorted(actions, key=lambda x: x["priority"])


def _build_30day_strategy(event_type, viable_days, gaps, network, urban, has_vehicle, near_water):
    """30-day strategic survival plan"""
    strategy = []

    # Phase 1: Stabilize (days 1–7)
    strategy.append({
        "phase": 1,
        "days": "1–7",
        "objective": "Stabilize",
        "actions": [
            "ประเมิน resource ที่มีอยู่จริง",
            "ติดต่อครอบครัว/เพื่อนสนิท 3–5 คน — สร้าง support network",
            f"ขยาย food/water supply ให้ได้ {max(14, int(viable_days*2))} วัน",
        ]
    })

    # Phase 2: Adapt (days 8–21)
    adapt_actions = ["ปรับ routine ตาม resource ที่มี", "ลดการใช้จ่ายที่ไม่จำเป็น"]

    if event_type == "pandemic":
        adapt_actions.append("ทำงาน/เรียนออนไลน์ถ้าได้ — ลด exposure")
        adapt_actions.append("ออกกำลังกายที่บ้าน ดูแลสุขภาพจิต")
    elif event_type == "economic_collapse":
        adapt_actions.append("หา alternative income — freelance, ขายของ, ทักษะที่มี")
        adapt_actions.append("รวมกลุ่มกับเพื่อนบ้าน — ลดต้นทุนร่วมกัน")
    elif event_type in ("climate_disaster", "war_conflict"):
        adapt_actions.append("ประเมินความปลอดภัยของที่อยู่ทุกวัน")
        if has_vehicle:
            adapt_actions.append("รักษาน้ำมันรถให้เต็มเสมอ — พร้อม relocate")

    strategy.append({
        "phase": 2,
        "days": "8–21",
        "objective": "Adapt",
        "actions": adapt_actions
    })

    # Phase 3: Sustain (days 22–30)
    sustain_actions = [
        "ประเมินสถานการณ์ซ้ำ — ปรับแผนตาม reality",
        f"เครือข่าย {network} คน — ขยายให้ได้ {network + 5}+ คน",
    ]

    if near_water:
        sustain_actions.append("ใช้แหล่งน้ำธรรมชาติใกล้บ้าน — purify ก่อนดื่ม")

    if not urban:
        sustain_actions.append("ปลูกผักสวนครัวเร็ว — ถั่ว ผักบุ้ง ผักกาด ใช้เวลา 14–30 วัน")

    strategy.append({
        "phase": 3,
        "days": "22–30",
        "objective": "Sustain",
        "actions": sustain_actions
    })

    return strategy


def _minimum_viable_path(threat, viable_days, gaps, event_type):
    """
    FATE™ MVP: ทางรอดขั้นต่ำที่อธิบายได้
    "คำตอบของระบบใดที่มนุษย์อยู่รอไม่ถึงวันที่ได้ใช้คำตอบนั้น ไร้ค่า"
    """
    if viable_days >= 30 and threat < 50:
        return {
            "path": "STABLE",
            "summary": "มีเวลาและ resource พอ — วางแผนระยะกลางได้",
            "first_step": "บันทึก resource และสร้างแผนสำรอง",
        }
    elif viable_days >= 7:
        return {
            "path": "ADAPT",
            "summary": f"รอด {round(viable_days,0)} วันได้ด้วย resource ปัจจุบัน — ต้องขยายภายใน 72h",
            "first_step": gaps[0]["resource"] + " — เติมให้ได้ 14 วันก่อน" if gaps else "หา secondary resource",
        }
    elif viable_days >= 2:
        return {
            "path": "CRITICAL",
            "summary": f"Resource เหลือแค่ {round(viable_days,1)} วัน — ต้องแก้ภายใน 24h",
            "first_step": "หา water/food ทันที — ทุกอย่างอื่นรอได้",
        }
    else:
        return {
            "path": "EMERGENCY",
            "summary": "SYSTEM_PAUSE — resource หมดภายใน 24h",
            "first_step": "โทรขอความช่วยเหลือทันที — 1669, เพื่อน, ครอบครัว, หน่วยงานราชการ",
        }


# =============================================================================
# FULL ASSESSMENT — รวมทั้ง 3 layer
# เรียกจาก /run pipeline เมื่อ input มี survival/medical context
# =============================================================================

def full_survival_assessment(
    user_input: str,
    context: Optional[dict] = None,
) -> dict:
    """
    Entry point หลักสำหรับ app.py
    วิเคราะห์ user_input แล้วเลือก layer ที่เหมาะสมอัตโนมัติ

    ตรวจจากคีย์เวิร์ดใน user_input และ context:
    - มี symptoms → medical layer
    - มี event_type → global event layer
    - อื่นๆ → personal survival layer
    """
    context = context or {}
    text    = user_input.lower()
    result  = {"domain": "survival_full", "timestamp": time.time(), "layers": []}

    # ── Medical detection ─────────────────────────────────────────
    medical_keywords = [
        "ปวด", "ไข้", "เจ็บ", "อาเจียน", "หอบ", "แน่นหน้าอก",
        "chest", "fever", "pain", "symptom", "sick", "hospital",
        "โรค", "อาการ", "หมอ", "รักษา", "ยา", "โรงพยาบาล",
    ]
    has_medical = any(kw in text for kw in medical_keywords)
    if has_medical or context.get("symptoms"):
        symptoms = context.get("symptoms", _extract_symptoms(text))
        med = analyze_medical_risk(
            symptoms=symptoms,
            age=context.get("age", 40),
            comorbidities=context.get("comorbidities", []),
            genomic_variants=context.get("genomic_variants", []),
            vital_signs=context.get("vital_signs", {}),
            duration_days=context.get("duration_days", 1),
        )
        result["layers"].append(med)
        result["medical"] = med

    # ── Global event detection ────────────────────────────────────
    event_keywords = {
        "pandemic":         ["ระบาด", "pandemic", "covid", "virus", "โรคระบาด"],
        "war_conflict":     ["สงคราม", "war", "conflict", "ระเบิด", "ยิง"],
        "economic_collapse":["วิกฤตเศรษฐกิจ", "เศรษฐกิจ", "economic", "collapse", "bankruptcy"],
        "climate_disaster": ["น้ำท่วม", "flood", "earthquake", "ไฟป่า", "wildfire", "แผ่นดินไหว"],
        "food_shortage":    ["ขาดแคลนอาหาร", "food shortage", "ข้าวยาก"],
        "power_grid_failure":["ไฟดับ", "power outage", "blackout"],
    }
    detected_event = context.get("event_type")
    if not detected_event:
        for ev, kws in event_keywords.items():
            if any(kw in text for kw in kws):
                detected_event = ev
                break

    if detected_event:
        evt = analyze_global_event(
            event_type=detected_event,
            location_context=context.get("location_context", {}),
            personal_resources=context.get("personal_resources", {}),
            severity=context.get("severity", 50.0),
            affected_population=context.get("affected_population", 1),
        )
        result["layers"].append(evt)
        result["global_event"] = evt

    # ── Personal survival (always run as baseline) ─────────────────
    personal = analyze_survival(context)
    result["layers"].append(personal)
    result["personal"] = personal

    # ── Aggregate risk score ──────────────────────────────────────
    scores = []
    if result.get("medical"):   scores.append(result["medical"]["risk_score"])
    if result.get("global_event"): scores.append(result["global_event"]["threat_score"])
    scores.append(100 - personal.get("waterline", 60))

    agg_score  = max(scores) * 0.6 + (sum(scores) / len(scores)) * 0.4
    agg_score  = min(100.0, agg_score)

    # ── Unified recommendation ────────────────────────────────────
    result["aggregate_risk"]    = round(agg_score, 1)
    result["overall_urgency"]   = _aggregate_urgency(result)
    result["total_choices"]     = sum(
        len(layer.get("recommended_actions", [])) +
        len(layer.get("immediate_actions", []))
        for layer in result["layers"]
    )
    result["fate_axiom"]        = "Choice(t) >= 1" if result["total_choices"] > 0 else "SYSTEM_PAUSE"
    result["context_for_lyla"]  = _build_lyla_context(result)

    return result


def _extract_symptoms(text: str) -> list:
    """Extract symptoms from free text — keyword matching"""
    sym_keywords = {
        "chest_pain":          ["แน่นหน้าอก", "เจ็บหน้าอก", "chest pain"],
        "shortness_of_breath": ["หอบ", "หายใจไม่ออก", "shortness of breath"],
        "high_fever":          ["ไข้สูง", "high fever", "ตัวร้อน"],
        "severe_abdominal_pain":["ปวดท้องรุนแรง", "abdominal pain"],
        "sudden_headache":     ["ปวดหัวรุนแรง", "sudden headache"],
        "confusion":           ["สับสน", "confused", "งง"],
        "fatigue_severe":      ["อ่อนเพลียมาก", "exhausted", "fatigue"],
        "suicidal_ideation":   ["อยากตาย", "ฆ่าตัวตาย", "suicidal"],
    }
    found = []
    text_lower = text.lower()
    for sym, keywords in sym_keywords.items():
        if any(kw in text_lower for kw in keywords):
            found.append(sym)
    return found


def _aggregate_urgency(result: dict) -> str:
    urgencies = []
    if result.get("medical"):   urgencies.append(result["medical"].get("urgency", "MONITOR"))
    if result.get("global_event"):
        thr = result["global_event"].get("threat_level", "LOW")
        urgencies.append("IMMEDIATE" if thr == "EXTREME" else "URGENT" if thr == "HIGH" else "SOON")
    if not urgencies: return "MONITOR"
    order = ["IMMEDIATE", "URGENT", "SOON", "MONITOR", "ROUTINE"]
    return min(urgencies, key=lambda x: order.index(x) if x in order else 99)


def _build_lyla_context(result: dict) -> str:
    parts = []
    if result.get("medical"):
        m = result["medical"]
        parts.append(f"[Medical: risk={m['risk_score']}, urgency={m['urgency']}, systems={','.join(m['affected_systems'][:3])}]")
    if result.get("global_event"):
        e = result["global_event"]
        parts.append(f"[Event: {e['event_type']}, threat={e['threat_level']}, viable={e['viable_days']}days]")
    p = result.get("personal", {})
    if p:
        parts.append(f"[Personal: waterline={p.get('waterline',60)}, can_decide={p.get('can_decide',True)}]")
    parts.append(f"[AggRisk={result.get('aggregate_risk',0)}, TotalChoices={result.get('total_choices',0)}]")
    return " ".join(parts)


# =============================================================================
# HELPERS
# =============================================================================

def _status_to_path(status: str) -> str:
    return {
        "STABLE":              "stable_survival",
        "STRESSED_FUNCTIONAL": "adapt",
        "LOW_ENERGY":          "recover_first",
        "CRITICAL_NO_FOOD":    "find_food_now",
        "CRITICAL_NO_SHELTER": "find_shelter_now",
        "RESET_REQUIRED":      "critical_risk",
    }.get(status, "adapt")


def _count_choices(output) -> int:
    try:    return max(1, 6 - int(output.waterline / 20))
    except: return 3
