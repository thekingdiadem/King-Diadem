# ENGINE/world_intel.py
"""
KING DIADEM — World Intelligence Layer
ปกป้องการตัดสินใจตั้งแต่ระดับบุคคล → อารยธรรม
FATE™ Axiom 4: Downside before Upside — เสมอ ทุกระดับ
"""

from __future__ import annotations
from typing import Optional
import math
import time


# ══════════════════════════════════════════════════════════════════
# TIER 1 — PLANETARY GEOGRAPHY
# ══════════════════════════════════════════════════════════════════

# Zone boundaries: (lat_min, lat_max, lng_min, lng_max, zone_name)
_GEO_ZONES = [
    (-10,  35,  95, 155, "southeast_asia"),
    ( 20,  55,  73, 135, "east_asia"),
    ( 10,  35,  44,  73, "south_asia"),
    ( 12,  42,  25,  60, "middle_east"),
    (-35,  37, -18,  52, "africa"),
    ( 35,  72, -10,  45, "europe"),
    ( 15,  72, -170,-50, "north_america"),
    (-55,  15, -82, -34, "south_america"),
    (-45,  -8, 112, 180, "oceania"),
    ( 60,  90, -180,180, "arctic"),
    (-90, -60, -180,180, "antarctic"),
]

# Risk profile per zone — deterministic baseline
_ZONE_PROFILE = {
    "southeast_asia": {"climate_risk": 0.55, "resource_density": 0.65, "political_risk": 0.45},
    "east_asia":      {"climate_risk": 0.40, "resource_density": 0.72, "political_risk": 0.50},
    "south_asia":     {"climate_risk": 0.60, "resource_density": 0.55, "political_risk": 0.52},
    "middle_east":    {"climate_risk": 0.65, "resource_density": 0.45, "political_risk": 0.70},
    "africa":         {"climate_risk": 0.62, "resource_density": 0.40, "political_risk": 0.60},
    "europe":         {"climate_risk": 0.30, "resource_density": 0.78, "political_risk": 0.25},
    "north_america":  {"climate_risk": 0.35, "resource_density": 0.80, "political_risk": 0.28},
    "south_america":  {"climate_risk": 0.50, "resource_density": 0.60, "political_risk": 0.48},
    "oceania":        {"climate_risk": 0.42, "resource_density": 0.68, "political_risk": 0.22},
    "arctic":         {"climate_risk": 0.75, "resource_density": 0.20, "political_risk": 0.15},
    "antarctic":      {"climate_risk": 0.80, "resource_density": 0.05, "political_risk": 0.05},
    "unknown":        {"climate_risk": 0.50, "resource_density": 0.50, "political_risk": 0.50},
}

def _classify_zone(lat: float, lng: float) -> str:
    for lat_min, lat_max, lng_min, lng_max, zone in _GEO_ZONES:
        if lat_min <= lat <= lat_max and lng_min <= lng <= lng_max:
            return zone
    return "unknown"

def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance between two points in km"""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def analyze_location(lat: float, lng: float, context: Optional[dict] = None) -> dict:
    """
    Tier 1 analysis: geography + baseline risk profile
    context: {season, local_conflict, infrastructure_score}
    """
    ctx   = context or {}
    zone  = _classify_zone(lat, lng)
    prof  = _ZONE_PROFILE[zone].copy()

    # Adjust for context
    if ctx.get("local_conflict"):
        prof["political_risk"] = min(1.0, prof["political_risk"] + 0.25)
    if ctx.get("infrastructure_score") is not None:
        infra = float(ctx["infrastructure_score"])  # 0-1, higher = better
        prof["resource_density"] = (prof["resource_density"] + infra) / 2

    composite_risk = (
        prof["climate_risk"]   * 0.30 +
        prof["political_risk"] * 0.45 +
        (1 - prof["resource_density"]) * 0.25
    )

    return {
        "lat":              lat,
        "lng":              lng,
        "zone":             zone,
        "climate_risk":     round(prof["climate_risk"],   3),
        "resource_density": round(prof["resource_density"],3),
        "political_risk":   round(prof["political_risk"],  3),
        "composite_risk":   round(composite_risk,          3),
        "tier":             "PLANETARY",
    }


# ══════════════════════════════════════════════════════════════════
# TIER 2 — CIVILIZATION THREAT MODEL
# ══════════════════════════════════════════════════════════════════

# Civilization-scale threat categories
CIVILIZATIONAL_THREATS = {
    "pandemic":         {"probability_annual": 0.02, "collapse_potential": 0.35, "reversibility": 0.70},
    "nuclear_exchange": {"probability_annual": 0.01, "collapse_potential": 0.95, "reversibility": 0.05},
    "climate_cascade":  {"probability_annual": 0.08, "collapse_potential": 0.55, "reversibility": 0.30},
    "ai_misalignment":  {"probability_annual": 0.03, "collapse_potential": 0.80, "reversibility": 0.20},
    "solar_flare_x10":  {"probability_annual": 0.005,"collapse_potential": 0.60, "reversibility": 0.45},
    "supervolcano":     {"probability_annual": 0.001,"collapse_potential": 0.70, "reversibility": 0.25},
    "asteroid_100m":    {"probability_annual": 0.0003,"collapse_potential":0.50, "reversibility": 0.40},
    "asteroid_1km":     {"probability_annual": 0.00007,"collapse_potential":0.90,"reversibility": 0.10},
    "ecosystem_collapse":{"probability_annual":0.05, "collapse_potential": 0.65, "reversibility": 0.20},
    "economic_cascade": {"probability_annual": 0.06, "collapse_potential": 0.30, "reversibility": 0.75},
}

def assess_civilization_risk(
    active_threats: Optional[list] = None,
    horizon_years:  int = 10,
) -> dict:
    """
    คำนวณ civilization risk ตาม threat portfolio
    FATE™ A4: ประเมิน downside ก่อนเสมอ — ไม่ optimism bias
    """
    threats = active_threats or list(CIVILIZATIONAL_THREATS.keys())
    horizon = max(1, min(horizon_years, 100))

    results = []
    total_collapse_risk = 0.0

    for threat in threats:
        if threat not in CIVILIZATIONAL_THREATS:
            continue
        t = CIVILIZATIONAL_THREATS[threat]

        # Probability over horizon (independent events)
        p_horizon = 1 - (1 - t["probability_annual"]) ** horizon
        weighted_collapse = p_horizon * t["collapse_potential"]
        total_collapse_risk = 1 - (1 - total_collapse_risk) * (1 - weighted_collapse)

        results.append({
            "threat":            threat,
            "p_in_horizon":      round(p_horizon,          4),
            "collapse_potential":t["collapse_potential"],
            "reversibility":     t["reversibility"],
            "weighted_risk":     round(weighted_collapse,   4),
            "priority":          "CRITICAL" if weighted_collapse > 0.20
                                 else "HIGH" if weighted_collapse > 0.08
                                 else "MODERATE",
        })

    results.sort(key=lambda x: x["weighted_risk"], reverse=True)

    return {
        "horizon_years":      horizon,
        "threats_assessed":   len(results),
        "total_collapse_risk":round(min(1.0, total_collapse_risk), 4),
        "choice_preserved":   total_collapse_risk < 1.0,
        "top_threats":        results[:5],
        "axiom":              "Choice(t) ≥ 1 → collapse = False — civilization scale",
        "tier":               "CIVILIZATION",
    }


# ══════════════════════════════════════════════════════════════════
# TIER 3 — COSMIC EVENT DETECTION
# ══════════════════════════════════════════════════════════════════

# Near-Earth Object risk classification (based on Torino scale logic)
def assess_cosmic_event(
    diameter_m:       float,         # เส้นผ่านศูนย์กลาง เมตร
    velocity_km_s:    float,         # ความเร็ว km/s
    miss_distance_km: float,         # ระยะห่างจากโลก km
    warning_days:     int   = 0,     # เวลาเตือนล่วงหน้า วัน
) -> dict:
    """
    Cosmic-scale threat assessment
    ไม่ใช่ paranoia — เป็น Axiom 4 ในระดับจักรวาล
    """
    EARTH_RADIUS_KM = 6371.0
    EARTH_CROSS_KM  = 12742.0

    # Kinetic energy (Joules) — KE = 0.5 * m * v²
    # density assume rocky: 2500 kg/m³
    volume_m3   = (4/3) * math.pi * (diameter_m/2)**3
    mass_kg     = volume_m3 * 2500
    velocity_ms = velocity_km_s * 1000
    kinetic_j   = 0.5 * mass_kg * velocity_ms**2
    kinetic_mt  = kinetic_j / 4.184e15   # Megatons TNT

    # Impact probability (simplified — based on miss distance)
    if miss_distance_km <= EARTH_CROSS_KM:
        impact_probability = 1.0
    elif miss_distance_km < 100_000:
        impact_probability = max(0, 1 - (miss_distance_km / 100_000))
    else:
        impact_probability = 0.0

    # Torino-inspired classification
    if kinetic_mt < 1:
        scale = "LOCAL"
        effect = "เฉพาะพื้นที่ — เทียบ Tunguska 1908"
    elif kinetic_mt < 1000:
        scale = "REGIONAL"
        effect = "ทำลายระดับประเทศ — tsunami ถ้าลงทะเล"
    elif kinetic_mt < 100_000:
        scale = "CONTINENTAL"
        effect = "ผลกระทบทวีป — winter effect"
    elif kinetic_mt < 10_000_000:
        scale = "GLOBAL"
        effect = "impact winter — อารยธรรมพัง"
    else:
        scale = "EXTINCTION"
        effect = "K-Pg level — mass extinction"

    # Deflection feasibility
    if warning_days >= 3650:   # 10 years
        deflect = "FEASIBLE — kinetic impactor / gravity tractor"
    elif warning_days >= 365:
        deflect = "POSSIBLE — nuclear standoff (controversial)"
    elif warning_days >= 30:
        deflect = "VERY_DIFFICULT — last resort nuclear"
    else:
        deflect = "NONE — evacuation only"

    return {
        "diameter_m":          diameter_m,
        "velocity_km_s":       velocity_km_s,
        "kinetic_megatons":    round(kinetic_mt, 2),
        "impact_probability":  round(impact_probability, 4),
        "scale":               scale,
        "effect":              effect,
        "warning_days":        warning_days,
        "deflection_option":   deflect,
        "choice_exists":       deflect != "NONE",
        "axiom":               "Choice(t) ≥ 1 — even at cosmic scale",
        "tier":                "COSMIC",
    }


# ══════════════════════════════════════════════════════════════════
# UNIFIED WORLD INTELLIGENCE — entry point
# ══════════════════════════════════════════════════════════════════

def world_decision(
    lat:              Optional[float] = None,
    lng:              Optional[float] = None,
    threats:          Optional[list]  = None,
    horizon_years:    int   = 10,
    cosmic_event:     Optional[dict]  = None,
    local_context:    Optional[dict]  = None,
) -> dict:
    """
    Full-stack world intelligence — ทุก tier รวมกัน
    ใช้ได้ตั้งแต่ รถเสียกลางทาง → อุกกาบาตถล่มโลก
    """
    report = {"timestamp": time.time(), "tiers": []}

    if lat is not None and lng is not None:
        geo = analyze_location(lat, lng, local_context)
        report["planetary"]  = geo
        report["tiers"].append("PLANETARY")

    if threats is not None or horizon_years:
        civ = assess_civilization_risk(threats, horizon_years)
        report["civilization"] = civ
        report["tiers"].append("CIVILIZATION")

    if cosmic_event:
        cosmic = assess_cosmic_event(**cosmic_event)
        report["cosmic"] = cosmic
        report["tiers"].append("COSMIC")

    # Global choice status
    choice_flags = []
    if "planetary"    in report: choice_flags.append(report["planetary"]["composite_risk"] < 0.9)
    if "civilization" in report: choice_flags.append(report["civilization"]["choice_preserved"])
    if "cosmic"       in report: choice_flags.append(report["cosmic"]["choice_exists"])

    report["global_choice_preserved"] = all(choice_flags) if choice_flags else True
    report["axiom"] = "Choice(t) ≥ 1 → collapse = False"

    return report
