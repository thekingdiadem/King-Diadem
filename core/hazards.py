"""ภัยพิบัติจริงทั่วโลกจาก GDACS (Global Disaster Alert and Coordination System — UN OCHA + คณะกรรมาธิการยุโรป)
ข้อมูลสาธารณะ ไม่ต้องใช้ key · ครอบคลุม พายุหมุนเขตร้อน (TC) น้ำท่วม (FL) ภูเขาไฟ (VO) ภัยแล้ง (DR) ไฟป่า (WF)
แผ่นดินไหวใช้ core/quakes.py (USGS ละเอียดกว่า อัปเดตทุกนาที) — ที่นี่จึงไม่รวม EQ

หลักเดียวกับ core/quakes.py:
  · แคช 10 นาที · หมดเวลา 5 วินาที · ใช้ไม่ได้ → ok=False แชทไม่ช้า ไม่ล่ม และบอก AI ว่า "ห้ามเดา"
  · ใกล้ไทย (รัศมี RADIUS_KM) แสดงทุกระดับเตือน · ที่อื่นในโลกแสดงเฉพาะระดับส้ม/แดง
  · ระดับเตือนของ GDACS: Green (ผลกระทบน้อย) · Orange (ปานกลาง) · Red (รุนแรง ต้องการความช่วยเหลือระหว่างประเทศ)
"""
from __future__ import annotations

import os
import threading
import time

from core.quakes import HOME, km

FEED = os.getenv("GDACS_FEED", "https://www.gdacs.org/gdacsapi/api/events/geteventlist/MAP")
TTL, FAIL_TTL, TIMEOUT = 600, 180, 5.0
RADIUS_KM = 2500           # ไทย + อาเซียน + ทะเลจีนใต้ (พายุที่เข้าไทยมักก่อตัวที่นี่) + อ่าวเบงกอล
KINDS = {"TC": ("พายุหมุนเขตร้อน", "Tropical cyclone"), "FL": ("น้ำท่วม", "Flood"), "VO": ("ภูเขาไฟ", "Volcano"),
         "DR": ("ภัยแล้ง", "Drought"), "WF": ("ไฟป่า", "Wildfire")}
LEVEL = {"green": 1, "orange": 2, "red": 3}
LEVEL_TH = {"green": "เขียว (ผลกระทบน้อย)", "orange": "ส้ม (ปานกลาง)", "red": "แดง (รุนแรง)"}

_cache = {"at": 0.0, "ok": False, "items": []}
_lock = threading.Lock()


def _http_get(url: str) -> dict:
    import httpx
    r = httpx.get(url, timeout=TIMEOUT, headers={"User-Agent": "KING-DIADEM/1.0", "Accept": "application/json"})
    r.raise_for_status()
    return r.json()


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def parse(geo: dict) -> list:
    """GeoJSON ของ GDACS → รายการเหตุการณ์ (1 แถวต่อเหตุการณ์ · ใช้จุด Point เท่านั้น · ข้ามข้อมูลไม่ครบ)"""
    out, seen = [], set()
    for f in (geo or {}).get("features") or []:
        p, g = f.get("properties") or {}, f.get("geometry") or {}
        kind = str(p.get("eventtype") or "").upper()
        if kind not in KINDS or g.get("type") != "Point":
            continue
        c = g.get("coordinates") or []
        lon, lat = (_num(c[0]), _num(c[1])) if len(c) >= 2 else (None, None)
        level = str(p.get("alertlevel") or "").lower()
        eid = f"{kind}{p.get('eventid')}"
        if lat is None or lon is None or level not in LEVEL or eid in seen or str(p.get("iscurrent", "true")).lower() == "false":
            continue
        seen.add(eid)
        sev = p.get("severitydata") or {}
        url = (p.get("url") or {}).get("report") if isinstance(p.get("url"), dict) else ""
        out.append({"id": eid, "kind": kind, "level": level, "lat": lat, "lon": lon,
                    "name": str(p.get("eventname") or p.get("name") or "")[:120],
                    "country": str(p.get("country") or "")[:120],
                    "severity": str(sev.get("severitytext") or "")[:160] if isinstance(sev, dict) else "",
                    "from": str(p.get("fromdate") or "")[:19], "to": str(p.get("todate") or "")[:19],
                    "url": url if isinstance(url, str) and url.startswith("https://www.gdacs.org/") else ""})
    return out


def fetch(get=None) -> tuple[bool, list]:
    now = time.time()
    with _lock:
        if _cache["at"] and now - _cache["at"] < (TTL if _cache["ok"] else FAIL_TTL):
            return _cache["ok"], list(_cache["items"])
    try:
        items, ok = parse((get or _http_get)(FEED)), True
    except Exception as e:
        print(f"⚠ hazards: {type(e).__name__}")
        items, ok = [], False
    with _lock:
        if ok or not _cache["ok"]:
            _cache.update(at=now, ok=ok, items=items)
        else:                                          # ล้มครั้งเดียว ไม่ทิ้งข้อมูลดีที่มีอยู่
            _cache["at"] = now - TTL + FAIL_TTL
        return _cache["ok"], list(_cache["items"])


def recent(kinds=None, lat: float = HOME[0], lon: float = HOME[1], get=None) -> dict:
    """ภัยที่ควรบอกผู้ใช้: ใกล้ (ทุกระดับ) + ไกล (ส้ม/แดง) · kinds = จำกัดชนิด (เช่น ["TC", "FL"])"""
    ok, items = fetch(get)
    want = {k for k in (kinds or KINDS) if k in KINDS}
    near, world = [], []
    for h in items:
        if h["kind"] not in want:
            continue
        row = dict(h, km=round(km(lat, lon, h["lat"], h["lon"])))
        if row["km"] <= RADIUS_KM:
            near.append(row)
        elif LEVEL[h["level"]] >= 2:
            world.append(row)
    key = lambda h: (-LEVEL[h["level"]], h["km"])
    near.sort(key=key)
    world.sort(key=key)
    return {"ok": ok, "source": "GDACS", "home": {"th": HOME[2], "en": HOME[3]}, "radius_km": RADIUS_KM,
            "kinds": sorted(want), "near": near[:5], "world": world[:4]}


def llm_note(r: dict) -> str:
    """บริบทให้ AI — ข้อมูลจริง ห้ามเดาเกินนี้"""
    if not r or not r.get("ok"):
        return "[ข้อมูลภัยพิบัติจริงทั่วโลก (GDACS) ตอนนี้ดึงไม่ได้: ห้ามเดาว่ามีหรือไม่มี — แนะนำให้ติดตาม tmd.go.th และ disaster.go.th]"
    rows = r["near"] + r["world"]
    names = "/".join(KINDS[k][0] for k in r["kinds"])
    if not rows:
        return (f"[ข้อมูลจริงจาก GDACS: ตอนนี้ไม่มีประกาศ{names}ในรัศมี {RADIUS_KM:,} กม. จาก{HOME[2]} "
                "และไม่มีระดับส้ม/แดงที่อื่น — ถ้าผู้ใช้เจอเหตุในพื้นที่ อาจเป็นเหตุเฉพาะจุดที่ GDACS ไม่ได้ติดตาม ให้ดูกรมอุตุฯ/ปภ. ด้วย]")
    parts = [f"{KINDS[h['kind']][0]} {h['name'] or h['country']} ระดับ{LEVEL_TH[h['level']]} ห่าง{HOME[2]} {h['km']:,} กม."
             + (f" ({h['severity']})" if h["severity"] else "") for h in rows[:4]]
    return "[ข้อมูลจริงจาก GDACS: " + " · ".join(parts) + " — ใช้ข้อมูลนี้เท่านั้น ห้ามเพิ่มตัวเลขอื่น]"
