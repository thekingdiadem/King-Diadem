# ENGINE/map_bridge.py
"""
KING DIADEM — Map Bridge
URL builder + deep link สำหรับทุก map provider
ไม่ใช่แค่ return URL เดียว
"""
from __future__ import annotations
import urllib.parse
from typing import Optional


def open_google_maps(lat: float, lng: float, query: str = "") -> str:
    """backward compat — return search URL"""
    lat, lng = float(lat), float(lng)
    if query:
        q = urllib.parse.quote(query)
        return f"https://www.google.com/maps/search/{q}/@{lat},{lng},15z"
    return f"https://www.google.com/maps/@{lat},{lng},15z"


def build_map_links(
    lat:   float,
    lng:   float,
    query: str = "",
    to_lat: Optional[float] = None,
    to_lng: Optional[float] = None,
) -> dict:
    """
    Build links สำหรับทุก provider + deep link mobile
    """
    # บังคับเป็นตัวเลข — กันข้อความแปลกปลอมถูกต่อเข้า URL; และ 0.0 (เส้นศูนย์สูตร) ไม่ใช่ "ไม่มีค่า"
    lat, lng = float(lat), float(lng)
    to_lat = float(to_lat) if to_lat is not None else None
    to_lng = float(to_lng) if to_lng is not None else None
    q_enc = urllib.parse.quote(str(query)) if query else ""

    links = {}

    # ── Google Maps ───────────────────────────────────────────────
    if to_lat is not None and to_lng is not None:
        links["google_maps"] = (
            f"https://www.google.com/maps/dir/{lat},{lng}/{to_lat},{to_lng}"
        )
        links["google_maps_mobile"] = (
            f"comgooglemaps://?saddr={lat},{lng}&daddr={to_lat},{to_lng}&directionsmode=driving"
        )
    elif query:
        links["google_maps"] = (
            f"https://www.google.com/maps/search/{q_enc}/@{lat},{lng},15z"
        )
        links["google_maps_mobile"] = (
            f"comgooglemaps://?q={q_enc}&center={lat},{lng}"
        )
    else:
        links["google_maps"] = f"https://www.google.com/maps/@{lat},{lng},16z"

    # ── Apple Maps ────────────────────────────────────────────────
    if to_lat is not None and to_lng is not None:
        links["apple_maps"] = (
            f"https://maps.apple.com/?saddr={lat},{lng}&daddr={to_lat},{to_lng}&dirflg=d"
        )
    elif query:
        links["apple_maps"] = (
            f"https://maps.apple.com/?q={q_enc}&ll={lat},{lng}"
        )

    # ── OpenStreetMap ─────────────────────────────────────────────
    links["openstreetmap"] = (
        f"https://www.openstreetmap.org/?mlat={lat}&mlon={lng}&zoom=16"
    )

    # ── Grab / LINE MAN (Thai context) ───────────────────────────
    if query:
        links["grab_food_search"] = (
            f"https://food.grab.com/th/en/search?keyword={q_enc}"
        )

    return {
        "lat":   lat,
        "lng":   lng,
        "query": query,
        "links": links,
        "primary": links.get("google_maps"),
    }


def nearest_search_url(lat: float, lng: float, category: str, radius_m: int = 2000) -> str:
    """Quick search URL สำหรับ category"""
    lat, lng = float(lat), float(lng)
    q = urllib.parse.quote(str(category))
    return (
        f"https://www.google.com/maps/search/{q}/@{lat},{lng},15z"
        f"?hl=th"
    )
