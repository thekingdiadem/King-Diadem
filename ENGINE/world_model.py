# ENGINE/world_model.py
"""
KING DIADEM — World Model
Node registry + real risk aggregation
ไม่ใช่แค่ load JSON — คำนวณ waterline จริง
"""

from __future__ import annotations
import json
import os
import time
from typing import Optional


def _f(v, d=0.0):
    """ตัวเลขแบบไม่ล้ม — แถวเสียในไฟล์ประวัติเดิมทำให้ทั้ง map ล้ม"""
    try:
        return float(v)
    except (TypeError, ValueError):
        return float(d)

NODE_FILE  = "data/node_registry.json"
WORLD_FILE = "data/world_history.json"

# ── Safe file I/O ─────────────────────────────────────────────────
def _load_json(path: str, default):
    try:
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def _save_json(path: str, data) -> bool:
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        tmp = path + ".tmp"                     # atomic — เดิมเขียนทับตรง ถ้าล้มกลางทางไฟล์เสีย
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
        return True
    except Exception:
        return False


# ── Node registry ─────────────────────────────────────────────────
def load_nodes() -> dict:
    d = _load_json(NODE_FILE, {})
    return {k: v for k, v in d.items() if isinstance(v, dict)} if isinstance(d, dict) else {}

def register_node(location: str, data: dict) -> bool:
    nodes = load_nodes()
    nodes[location] = {
        **data,
        "updated_at": time.time(),
    }
    return _save_json(NODE_FILE, nodes)

def build_world_state() -> dict:
    nodes = load_nodes()
    locations = {}

    for location, data in nodes.items():
        food    = _f(data.get("food"), 50)
        risk    = _f(data.get("risk"), 50)
        water   = _f(data.get("water"), 50)
        shelter = _f(data.get("shelter"), 50)

        # Waterline score: ต่ำ = อันตราย
        waterline = (
            food    * 0.35 +
            water   * 0.25 +
            shelter * 0.20 +
            (100 - risk) * 0.20
        )

        locations[location] = {
            "food":      food,
            "water":     water,
            "shelter":   shelter,
            "risk":      risk,
            "waterline": round(waterline, 2),
            "status":    "CRITICAL" if waterline < 30
                         else "WARNING" if waterline < 55
                         else "STABLE",
        }

    return {
        "total_nodes": len(nodes),
        "locations":   locations,
        "timestamp":   time.time(),
    }


# ── World history ─────────────────────────────────────────────────
def load_world() -> list:
    # ไฟล์เดียวกับ world_intelligence — ข้อมูลเสีย/ผิดชนิดเดิมทำให้ .append() ล้ม
    d = _load_json(WORLD_FILE, [])
    return [e for e in d if isinstance(e, dict)] if isinstance(d, list) else []

def save_world(world: list) -> bool:
    return _save_json(WORLD_FILE, world)

def update_world(
    location:   str,
    food_score: float,
    risk_score: float,
    water_score:  float = 50.0,
    shelter_score:float = 50.0,
) -> bool:
    world = load_world()
    world.append({
        "location":     str(location),
        "food_score":   _f(food_score, 50),
        "risk_score":   _f(risk_score, 50),
        "water_score":  _f(water_score, 50),
        "shelter_score":_f(shelter_score, 50),
        "timestamp":    time.time(),
    })
    # ไฟล์เดียวกับ world_intelligence (เก็บ 2000) — เดิมตัดเหลือ 1000 ทำให้ข้อมูลอีกโมดูลหาย
    if len(world) > 2000:
        world = world[-2000:]
    return save_world(world)


# ── Aggregated maps ───────────────────────────────────────────────
def _aggregate(world: list, field: str) -> dict:
    """Average field value per location"""
    acc: dict = {}
    for entry in world:
        loc = entry.get("location")
        val = entry.get(field)
        if loc and val is not None:
            acc.setdefault(loc, []).append(_f(val))
    return {loc: round(sum(v)/len(v), 2) for loc, v in acc.items()}

def build_risk_map() -> dict:
    return _aggregate(load_world(), "risk_score")

def build_resource_map() -> dict:
    return _aggregate(load_world(), "food_score")

def build_waterline_map() -> dict:
    """Composite waterline per location from history"""
    world = load_world()
    acc: dict = {}
    for entry in world:
        loc = entry.get("location")
        if not loc:
            continue
        food    = _f(entry.get("food_score"), 50)
        risk    = _f(entry.get("risk_score"), 50)
        water   = _f(entry.get("water_score"), 50)
        shelter = _f(entry.get("shelter_score"), 50)
        wl = food*0.35 + water*0.25 + shelter*0.20 + (100-risk)*0.20
        acc.setdefault(loc, []).append(wl)
    return {loc: round(sum(v)/len(v), 2) for loc, v in acc.items()}

def find_safest_location(top_n: int = 3) -> list:
    """หา location ที่ waterline สูงสุด — LYLA use case: หา safe zone"""
    wl_map = build_waterline_map()
    if not wl_map:
        return []
    sorted_locs = sorted(wl_map.items(), key=lambda x: x[1], reverse=True)
    return [{"location": loc, "waterline": wl} for loc, wl in sorted_locs[:top_n]]

def find_critical_locations() -> list:
    """หา location ที่ต้องการ intervention ทันที"""
    wl_map = build_waterline_map()
    return [
        {"location": loc, "waterline": wl, "status": "CRITICAL"}
        for loc, wl in wl_map.items()
        if wl < 30
    ]
