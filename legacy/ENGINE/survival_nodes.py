# ENGINE/survival_nodes.py
"""
KING DIADEM — Survival Node Scanner
หา food/hospital/water ใกล้ที่สุด — ใช้ Google Maps API จริง
"""
from __future__ import annotations
import math
from typing import Optional

try:
    from INTEGRATIONS.google_maps import search_nearby, find_nearest
    _MAPS_LOADED = True
except ImportError:
    _MAPS_LOADED = False


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


# Node type config
_NODE_TYPES = {
    "food":       {"query": "ร้านอาหาร food restaurant", "radius_m": 2000, "priority": 1},
    "water":      {"query": "น้ำดื่ม convenience store", "radius_m": 1000, "priority": 1},
    "hospital":   {"query": "โรงพยาบาล hospital clinic",  "radius_m": 5000, "priority": 2},
    "shelter":    {"query": "ที่พัก hotel shelter",       "radius_m": 3000, "priority": 2},
    "fuel":       {"query": "ปั๊มน้ำมัน gas station",    "radius_m": 3000, "priority": 3},
    "mechanic":   {"query": "อู่รถ car repair mechanic",  "radius_m": 3000, "priority": 3},
    "police":     {"query": "สถานีตำรวจ police station",  "radius_m": 5000, "priority": 2},
}


def find_survival_nodes(
    lat: float,
    lng: float,
    node_types: Optional[list] = None,
    radius_m: int = 3000,
) -> dict:
    """
    หา survival nodes รอบ lat/lng
    Default: food + water + hospital (critical tier)
    """
    types = node_types or ["food", "water", "hospital"]
    results = {}

    for ntype in types:
        cfg = _NODE_TYPES.get(ntype, {"query": ntype, "radius_m": radius_m, "priority": 3})
        r = cfg["radius_m"]

        if _MAPS_LOADED:
            try:
                found = search_nearby(lat, lng, cfg["query"], radius_m=r)
                results[ntype] = {
                    "status":   "found" if found else "not_found",
                    "results":  found or [],
                    "priority": cfg["priority"],
                    "source":   "google_maps",
                }
                continue
            except Exception:
                pass

        # Fallback — ไม่มี Maps API
        results[ntype] = {
            "status":   "api_unavailable",
            "results":  [],
            "priority": cfg["priority"],
            "fallback": f"ค้นหา '{cfg['query']}' ใน Google Maps ด้วยตัวเอง",
            "maps_url": f"https://www.google.com/maps/search/{cfg['query'].replace(' ','+')}/@{lat},{lng},{r}m",
            "source":   "fallback",
        }

    # สรุป critical nodes
    critical_missing = [
        t for t in ["food", "water"] if t in results
        and results[t]["status"] in ("not_found", "api_unavailable")
    ]

    return {
        "lat":              lat,
        "lng":              lng,
        "nodes":            results,
        "critical_missing": critical_missing,
        "choice_exists":    len(critical_missing) == 0,
        "axiom":            "Choice(t) ≥ 1 → collapse = False",
    }
