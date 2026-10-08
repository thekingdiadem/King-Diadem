# INTEGRATIONS/google_maps.py
# KING DIADEM — Google Maps real integration
# ใช้ Google Maps Platform APIs (Places, Geocoding, Directions)

import os
import json
import urllib.request
import urllib.error
import urllib.parse

PLACES_API   = "https://maps.googleapis.com/maps/api/place"
GEO_API      = "https://maps.googleapis.com/maps/api/geocode/json"
DIRECTIONS_API = "https://maps.googleapis.com/maps/api/directions/json"


def _key() -> str:
    key = os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise EnvironmentError("ไม่พบ GOOGLE_MAPS_API_KEY ใน environment")
    return key


_MODES = ("driving", "walking", "transit", "bicycling")


def _coord(v, lo: float, hi: float) -> float:
    """พิกัดต้องเป็นตัวเลขในช่วง — เดิมต่อ string ตรงเข้า URL (ใส่ '&key=...' แทรกพารามิเตอร์ได้)"""
    x = float(v)
    if not (lo <= x <= hi):
        raise ValueError("coordinate out of range")
    return x


def _get(url: str) -> dict:
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Maps API error {e.code}: {e.read().decode()}")


# ── PUBLIC FUNCTIONS ──────────────────────────────────────────────

def search_nearby(
    lat: float,
    lng: float,
    keyword: str,
    radius_m: int = 1000,
    max_results: int = 5,
) -> list:
    """ค้นหาสถานที่ใกล้ coordinate — เหมาะกับ LYLA ตอน survival route"""
    lat, lng = _coord(lat, -90, 90), _coord(lng, -180, 180)
    radius_m = max(1, min(int(radius_m), 50000))
    max_results = max(1, min(int(max_results), 20))
    url = (
        f"{PLACES_API}/nearbysearch/json"
        f"?location={lat},{lng}"
        f"&radius={radius_m}"
        f"&keyword={urllib.parse.quote(str(keyword)[:200])}"
        f"&key={_key()}"
    )
    data = _get(url)
    results = []
    for p in data.get("results", [])[:max_results]:
        loc = p.get("geometry", {}).get("location", {})
        results.append({
            "name":    p.get("name", ""),
            "address": p.get("vicinity", ""),
            "lat":     loc.get("lat"),
            "lng":     loc.get("lng"),
            "rating":  p.get("rating"),
            "open_now": p.get("opening_hours", {}).get("open_now"),
            "place_id": p.get("place_id", ""),
            "maps_url": f"https://www.google.com/maps/place/?q=place_id:{p.get('place_id','')}",
        })
    return results


def geocode(address: str) -> dict:
    """แปลงที่อยู่เป็น lat/lng"""
    url = f"{GEO_API}?address={urllib.parse.quote(str(address)[:300])}&key={_key()}"
    data = _get(url)
    if not data.get("results"):
        return {"error": "ไม่พบที่อยู่นี้", "address": address}
    loc = data["results"][0]["geometry"]["location"]
    return {
        "address":        data["results"][0].get("formatted_address", address),
        "lat":            loc["lat"],
        "lng":            loc["lng"],
        "maps_url":       f"https://www.google.com/maps?q={loc['lat']},{loc['lng']}",
    }


def reverse_geocode(lat: float, lng: float) -> dict:
    """แปลง lat/lng เป็นที่อยู่"""
    lat, lng = _coord(lat, -90, 90), _coord(lng, -180, 180)
    url = f"{GEO_API}?latlng={lat},{lng}&key={_key()}"
    data = _get(url)
    if not data.get("results"):
        return {"error": "ไม่พบที่อยู่จากพิกัดนี้"}
    return {
        "address":  data["results"][0].get("formatted_address", ""),
        "lat":      lat,
        "lng":      lng,
        "maps_url": f"https://www.google.com/maps?q={lat},{lng}",
    }


def get_directions(
    origin: str,
    destination: str,
    mode: str = "driving",  # driving | walking | transit | bicycling
) -> dict:
    """ขอเส้นทาง — return ระยะทาง เวลา และ summary"""
    if mode not in _MODES:        # เดิมต่อ mode เข้า URL ตรงๆ
        mode = "driving"
    origin, destination = str(origin)[:300], str(destination)[:300]
    url = (
        f"{DIRECTIONS_API}"
        f"?origin={urllib.parse.quote(origin)}"
        f"&destination={urllib.parse.quote(destination)}"
        f"&mode={mode}"
        f"&key={_key()}"
    )
    data = _get(url)
    if data.get("status") != "OK" or not data.get("routes"):
        return {"error": f"ไม่พบเส้นทาง ({data.get('status','UNKNOWN')})"}

    route = data["routes"][0]
    leg   = route["legs"][0]
    return {
        "origin":      leg.get("start_address", origin),
        "destination": leg.get("end_address", destination),
        "distance":    leg["distance"]["text"],
        "duration":    leg["duration"]["text"],
        "mode":        mode,
        "summary":     route.get("summary", ""),
        "maps_url": (
            f"https://www.google.com/maps/dir/"
            f"{urllib.parse.quote(origin)}/"
            f"{urllib.parse.quote(destination)}"
        ),
    }


def find_nearest(lat: float, lng: float, place_type: str) -> dict:
    """หาสถานที่ใกล้ที่สุด 1 แห่ง — เหมาะกับ LYLA survival mode"""
    results = search_nearby(lat, lng, place_type, radius_m=2000, max_results=1)
    if not results:
        return {"error": f"ไม่พบ {place_type} ในรัศมี 2 กม."}
    return results[0]
