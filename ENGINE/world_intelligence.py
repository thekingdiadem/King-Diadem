# ENGINE/world_intelligence.py
"""
KING DIADEM — World Intelligence
DriftZero Waterline Governance
atomic write + real aggregation + waterline per location
"""

from __future__ import annotations
import json
import os
import time
from typing import Optional
from core.paths import data_path


def _f(v, d=0.0):
    """ตัวเลขแบบไม่ล้ม — แถวเสียในไฟล์ประวัติเดิมทำให้ทั้ง map ล้ม"""
    try:
        return float(v)
    except (TypeError, ValueError):
        return float(d)

WORLD_FILE = data_path("world_history.json")   # ดู core/paths.py
MAX_HISTORY = 2000


# ── Atomic I/O (LYLA pattern) ─────────────────────────────────────
def load_world() -> list:
    if not os.path.exists(WORLD_FILE):
        return []
    try:
        with open(WORLD_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
        return [e for e in d if isinstance(e, dict)] if isinstance(d, list) else []
    except Exception:
        return []

def save_world(world: list) -> bool:
    """Atomic write — ป้องกันข้อมูลหายตอน crash"""
    try:
        os.makedirs(os.path.dirname(WORLD_FILE) or ".", exist_ok=True)
        tmp = WORLD_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(world, f, indent=2, ensure_ascii=False)
        os.replace(tmp, WORLD_FILE)   # atomic on all OS
        return True
    except Exception:
        return False


# ── Write ─────────────────────────────────────────────────────────
def update_world(
    location:      str,
    food_score:    float,
    risk_score:    float,
    water_score:   float = 50.0,
    shelter_score: float = 50.0,
) -> bool:
    world = load_world()
    world.append({
        "location":      str(location),
        "food_score":    _f(food_score, 50),
        "risk_score":    _f(risk_score, 50),
        "water_score":   _f(water_score, 50),
        "shelter_score": _f(shelter_score, 50),
        "timestamp":     time.time(),
        "audit_verified": True,
    })
    if len(world) > MAX_HISTORY:
        world = world[-MAX_HISTORY:]
    return save_world(world)


# ── Aggregation helpers ───────────────────────────────────────────
def _avg_by_location(world: list, field: str) -> dict:
    acc: dict = {}
    for e in world:
        loc = e.get("location")
        val = e.get(field)
        if loc and val is not None:
            acc.setdefault(loc, []).append(_f(val))
    return {loc: round(sum(v)/len(v), 2) for loc, v in acc.items()}


# ── Read maps ─────────────────────────────────────────────────────
def build_risk_map() -> dict:
    return _avg_by_location(load_world(), "risk_score")

def build_resource_map() -> dict:
    return _avg_by_location(load_world(), "food_score")

def build_waterline_map() -> dict:
    """
    Composite waterline per location
    สูง = ปลอดภัย / ต่ำ = ต้อง intervene
    """
    world = load_world()
    acc: dict = {}
    for e in world:
        loc = e.get("location")
        if not loc:
            continue
        food    = _f(e.get("food_score"), 50)
        risk    = _f(e.get("risk_score"), 50)
        water   = _f(e.get("water_score"), 50)
        shelter = _f(e.get("shelter_score"), 50)
        wl = food*0.35 + water*0.25 + shelter*0.20 + (100 - risk)*0.20
        acc.setdefault(loc, []).append(wl)
    return {loc: round(sum(v)/len(v), 2) for loc, v in acc.items()}


# ── Decision helpers — LYLA use case ─────────────────────────────
def find_safest_location(top_n: int = 3) -> list:
    """หา safe zone — รถเสียกลางทาง, ภัยพิบัติ"""
    wl = build_waterline_map()
    ranked = sorted(wl.items(), key=lambda x: x[1], reverse=True)
    return [{"location": loc, "waterline": wl_val,
             "status": "STABLE" if wl_val >= 55 else "WARNING"}
            for loc, wl_val in ranked[:top_n]]

def find_critical_locations() -> list:
    """หา location ที่ต้อง intervene ทันที"""
    wl = build_waterline_map()
    return [{"location": loc, "waterline": wl_val, "status": "CRITICAL"}
            for loc, wl_val in wl.items() if wl_val < 30]

def location_summary(location: str) -> dict:
    """ดู history ของ location เดียว + trend"""
    world = load_world()
    entries = [e for e in world if e.get("location") == location]
    if not entries:
        return {"location": location, "status": "NO_DATA", "choice": 0}

    latest = entries[-1]
    food   = _f(latest.get("food_score"), 50)
    risk   = _f(latest.get("risk_score"), 50)
    water  = _f(latest.get("water_score"), 50)
    shelter= _f(latest.get("shelter_score"), 50)
    wl     = food*0.35 + water*0.25 + shelter*0.20 + (100-risk)*0.20

    # Trend: เทียบ 5 entries ล่าสุด
    trend = "stable"
    if len(entries) >= 3:
        recent_wl = []
        for e in entries[-5:]:
            f = _f(e.get("food_score"), 50)
            r = _f(e.get("risk_score"), 50)
            w = _f(e.get("water_score"), 50)
            s = _f(e.get("shelter_score"), 50)
            recent_wl.append(f*0.35 + w*0.25 + s*0.20 + (100-r)*0.20)
        if recent_wl[-1] > recent_wl[0] + 5:
            trend = "improving"
        elif recent_wl[-1] < recent_wl[0] - 5:
            trend = "degrading"

    return {
        "location":  location,
        "waterline": round(wl, 2),
        "status":    "CRITICAL" if wl < 30 else "WARNING" if wl < 55 else "STABLE",
        "trend":     trend,
        "records":   len(entries),
        "latest":    latest,
        "axiom":     "Choice(t) ≥ 1 → collapse = False",
    }
