# ENGINE/path_generator.py
"""
KING DIADEM — Path Generator
สร้าง escape/resource paths จากพิกัดจริง
ไม่ใช่ lat+0.01 แบบ hardcode
"""
from __future__ import annotations
import math
from typing import Optional

try:
    from INTEGRATIONS.google_maps import search_nearby, get_directions
    _MAPS_LOADED = True
except ImportError:
    _MAPS_LOADED = False


def _bearing_to_coord(lat: float, lng: float, bearing_deg: float, dist_km: float):
    """คำนวณพิกัดปลายทางจาก bearing + distance"""
    R   = 6371.0
    d   = dist_km / R
    lat1 = math.radians(lat)
    lng1 = math.radians(lng)
    b    = math.radians(bearing_deg)

    lat2 = math.asin(
        math.sin(lat1)*math.cos(d) +
        math.cos(lat1)*math.sin(d)*math.cos(b)
    )
    lng2 = lng1 + math.atan2(
        math.sin(b)*math.sin(d)*math.cos(lat1),
        math.cos(d) - math.sin(lat1)*math.sin(lat2)
    )
    return round(math.degrees(lat2), 6), round(math.degrees(lng2), 6)

def _maps_url(lat: float, lng: float, query: str = "") -> str:
    if query:
        import urllib.parse
        q = urllib.parse.quote(query)
        return f"https://www.google.com/maps/search/{q}/@{lat},{lng},15z"
    return f"https://www.google.com/maps/@{lat},{lng},15z"

def _directions_url(from_lat: float, from_lng: float, to_lat: float, to_lng: float) -> str:
    return f"https://www.google.com/maps/dir/{from_lat},{from_lng}/{to_lat},{to_lng}"


# ── Path types ────────────────────────────────────────────────────
PATH_CONFIGS = {
    "escape": {
        "query":       "ถนนใหญ่ main road highway",
        "bearings":    [0, 90, 180, 270],   # N E S W
        "dist_km":     2.0,
        "priority":    1,
        "description": "เส้นทางออกจากพื้นที่",
    },
    "food": {
        "query":       "ร้านอาหาร food restaurant market",
        "bearings":    [45, 135, 225, 315],
        "dist_km":     1.0,
        "priority":    1,
        "description": "แหล่งอาหารใกล้ที่สุด",
    },
    "hospital": {
        "query":       "โรงพยาบาล hospital clinic",
        "bearings":    [0, 90, 180, 270],
        "dist_km":     3.0,
        "priority":    2,
        "description": "สถานพยาบาล",
    },
    "shelter": {
        "query":       "ที่พัก hotel shelter วัด",
        "bearings":    [45, 135],
        "dist_km":     1.5,
        "priority":    2,
        "description": "ที่พักพิง",
    },
    "water": {
        "query":       "น้ำดื่ม 7-11 convenience store",
        "bearings":    [0, 90, 180, 270],
        "dist_km":     0.5,
        "priority":    1,
        "description": "แหล่งน้ำ/ร้านสะดวกซื้อ",
    },
    "mechanic": {
        "query":       "อู่รถ ช่างรถ car repair",
        "bearings":    [0, 180],
        "dist_km":     2.0,
        "priority":    3,
        "description": "ช่างซ่อมรถ",
    },
}


def generate_paths(
    lat:        float,
    lng:        float,
    path_types: Optional[list] = None,
    context:    Optional[dict] = None,
) -> dict:
    """
    สร้าง paths ตาม path_types
    Default: escape + food + water (critical tier)
    """
    types  = path_types or ["escape", "food", "water"]
    ctx    = context or {}
    routes = {}

    for ptype in types:
        cfg = PATH_CONFIGS.get(ptype)
        if not cfg:
            continue

        if _MAPS_LOADED:
            try:
                results = search_nearby(lat, lng, cfg["query"], radius_m=int(cfg["dist_km"]*1000))
                if results:
                    top = results[0]
                    t_lat = top.get("lat", lat)
                    t_lng = top.get("lng", lng)
                    routes[ptype] = {
                        "type":        ptype,
                        "description": cfg["description"],
                        "priority":    cfg["priority"],
                        "target_lat":  t_lat,
                        "target_lng":  t_lng,
                        "name":        top.get("name", "—"),
                        "directions_url": _directions_url(lat, lng, t_lat, t_lng),
                        "source":      "google_maps",
                    }
                    continue
            except Exception:
                pass

        # Fallback — cardinal direction waypoints
        waypoints = []
        for bearing in cfg["bearings"]:
            wlat, wlng = _bearing_to_coord(lat, lng, bearing, cfg["dist_km"])
            waypoints.append({
                "bearing_deg": bearing,
                "lat":         wlat,
                "lng":         wlng,
                "maps_url":    _maps_url(wlat, wlng, cfg["query"]),
                "directions_url": _directions_url(lat, lng, wlat, wlng),
            })

        routes[ptype] = {
            "type":        ptype,
            "description": cfg["description"],
            "priority":    cfg["priority"],
            "waypoints":   waypoints,
            "search_url":  _maps_url(lat, lng, cfg["query"]),
            "note":        f"ค้นหา '{cfg['query']}' ในแผนที่",
            "source":      "fallback_bearing",
        }

    # Sort by priority
    sorted_routes = sorted(routes.values(), key=lambda x: x["priority"])

    return {
        "origin_lat": lat,
        "origin_lng":  lng,
        "paths":       sorted_routes,
        "path_count":  len(sorted_routes),
        "choice_exists": len(sorted_routes) > 0,
        "axiom":       "Choice(t) ≥ 1 → collapse = False",
}

