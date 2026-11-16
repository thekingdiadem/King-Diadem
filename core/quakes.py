"""แผ่นดินไหวจริงจาก USGS (ข้อมูลสาธารณะ ไม่ต้องใช้ key) — เชื่อมไว้ตั้งแต่ ROADMAP แรกๆ แต่ยังไม่เคยต่อจริง

ใช้ตอนผู้ใช้พูดถึงแผ่นดินไหว: บอกว่าเมื่อกี้มีแผ่นดินไหวจริงไหม ขนาดเท่าไหร่ ที่ไหน ห่างแค่ไหน
เดิมระบบรู้แค่ว่า "ผู้ใช้พูดถึงแผ่นดินไหว" แต่ไม่รู้ว่ามีเกิดขึ้นจริงหรือเปล่า

หลัก:
  · แคช 5 นาที — USGS อัปเดตทุก ~1 นาที แต่ไม่ต้องยิงทุกข้อความ
  · หมดเวลา 4 วินาที / ใช้ไม่ได้ → คืนค่าว่าง แชทไม่ช้าและไม่ล่มเพราะ USGS
  · อ้างอิงกรุงเทพเป็นค่าเริ่มต้น (ผู้ใช้ส่วนใหญ่อยู่ในไทย) — แผ่นดินไหวเมียนมา มี.ค. 2568 รู้สึกถึงกรุงเทพ ~1,000 กม.
"""
from __future__ import annotations

import math
import os
import threading
import time

FEED = os.getenv("QUAKE_FEED", "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson")
TTL, FAIL_TTL, TIMEOUT = 300, 120, 4.0
HOME = (13.7563, 100.5018, "กรุงเทพฯ", "Bangkok")
RADIUS_KM = 2000          # ไทย เมียนมา ลาว กัมพูชา มาเลเซีย สุมาตราตอนเหนือ ทะเลอันดามัน
MIN_MAG_NEAR = 3.5
MIN_MAG_WORLD = 5.5       # ที่อื่นในโลก: ขนาดที่ทำให้ตึกเสียหายได้ (~1–5 ครั้ง/วันทั่วโลก) — เดิม 6.5 เห็นน้อยเกินไป · ไฟล์ที่ดึงเป็นไฟล์เดิม ไม่เพิ่มงบ

# ลูกโลกใช้ฟีด 7 วัน (M4.5+ ทั่วโลก) เพิ่ม — แผ่นดินไหวใหญ่ไม่ได้เกิดทุกวัน 24 ชม. อย่างเดียวลูกโลกมักว่าง
WEEK_FEED = os.getenv("QUAKE_WEEK_FEED", "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_week.geojson")
MAP_DAYS, MAP_MAX = 7, 40

# JMA (สำนักอุตุนิยมวิทยาญี่ปุ่น): แหล่งที่สอง — ให้ "ชินโดะ" (แรงสั่นที่คนรู้สึกจริง มาตราญี่ปุ่น 1–7) ซึ่ง USGS ไม่มี
# ญี่ปุ่นวัดเองละเอียดกว่า และผู้ใช้ภาษาญี่ปุ่นคุ้นกับชินโดะมากกว่าขนาด M · ใช้เสริมเท่านั้น JMA ล่ม USGS ก็ยังตอบได้
JMA_FEED = os.getenv("QUAKE_JMA_FEED", "https://www.jma.go.jp/bosai/quake/data/list.json")
SHINDO = ["1", "2", "3", "4", "5-", "5+", "6-", "6+", "7"]
SHINDO_NOTE = "4"         # ชินโดะ 4 ขึ้นไป: ของบนชั้นตก คนส่วนใหญ่ตกใจ — ถึงจะบอกแม้ขนาด M ไม่ถึงเกณฑ์โลก
MATCH_KM, MATCH_MIN = 150, 5

_cache = {"at": 0.0, "ok": False, "items": []}
_jcache = {"at": 0.0, "ok": False, "items": []}
_wcache = {"at": 0.0, "ok": False, "items": []}
_lock = threading.Lock()


def _http_get(url: str) -> dict:
    import httpx
    r = httpx.get(url, timeout=TIMEOUT, headers={"User-Agent": "KING-DIADEM/1.0"})
    r.raise_for_status()
    return r.json()


def km(lat1, lon1, lat2, lon2) -> float:
    p = math.pi / 180
    a = (math.sin((lat2 - lat1) * p / 2) ** 2 +
         math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin((lon2 - lon1) * p / 2) ** 2)
    return 12742 * math.asin(math.sqrt(a))


def parse(geo: dict) -> list:
    out = []
    for f in (geo or {}).get("features") or []:
        p, g = f.get("properties") or {}, (f.get("geometry") or {}).get("coordinates") or []
        if p.get("mag") is None or len(g) < 2:
            continue
        out.append({"id": f.get("id"), "mag": round(float(p["mag"]), 1), "place": p.get("place") or "",
                    "time": int(p.get("time") or 0), "lon": float(g[0]), "lat": float(g[1]),
                    "depth": float(g[2]) if len(g) > 2 and g[2] is not None else None,
                    "tsunami": bool(p.get("tsunami")), "alert": p.get("alert"), "url": p.get("url") or ""})
    return out


def shindo_rank(v) -> int:
    """ลำดับชินโดะ 1..9 (ไม่รู้ = 0) — "5-" < "5+" เทียบเป็นสตริงตรงๆ ไม่ได้"""
    return SHINDO.index(v) + 1 if v in SHINDO else 0


def _jst_ms(at: str) -> int:
    from datetime import datetime
    return int(datetime.fromisoformat(at).timestamp() * 1000)


def parse_jma(rows) -> list:
    """list.json ของ JMA → รูปแบบเดียวกับ USGS + shindo · หนึ่งเหตุการณ์มีหลายฉบับ (ฉบับแรกในไฟล์ = ล่าสุด)
    ข้ามฉบับที่ยังไม่มีพิกัดหรือขนาด (เช่น 震度速報 ที่ออกก่อนรู้ศูนย์กลาง) — ไม่เดาตำแหน่งเอง"""
    import re
    out, seen = [], set()
    for r in rows if isinstance(rows, list) else []:
        if not isinstance(r, dict) or r.get("eid") in seen:
            continue
        m = re.match(r"([+-]\d+(?:\.\d+)?)([+-]\d+(?:\.\d+)?)(?:([+-]\d+))?", r.get("cod") or "")
        try:
            mag, t = float(r.get("mag")), _jst_ms(r.get("at") or "")
        except (TypeError, ValueError):
            continue
        if not m:
            continue
        seen.add(r.get("eid"))
        out.append({"id": "jma" + str(r.get("eid")), "mag": round(mag, 1), "time": t,
                    "place": (r.get("en_anm") or r.get("anm") or "").replace("\u200b", ""), "place_ja": r.get("anm") or "",
                    "lat": float(m.group(1)), "lon": float(m.group(2)),
                    "depth": abs(int(m.group(3))) / 1000 if m.group(3) else None,
                    "shindo": r.get("maxi") if r.get("maxi") in SHINDO else None,
                    "tsunami": False, "alert": None, "url": "https://www.jma.go.jp/bosai/map.html#contents=earthquake_map"})
    return out


def _fetch(url: str, cache: dict, get=None, parser=None) -> tuple[bool, list]:
    now = time.time()
    with _lock:
        age = now - cache["at"]
        if cache["at"] and age < (TTL if cache["ok"] else FAIL_TTL):
            return cache["ok"], list(cache["items"])
    try:
        items, ok = (parser or parse)((get or _http_get)(url)), True
    except Exception as e:
        print(f"⚠ quakes: {type(e).__name__}")
        items, ok = [], False
    with _lock:
        if ok or not cache["ok"]:                    # ล้มเหลวครั้งเดียว ไม่ทิ้งข้อมูลดีที่มีอยู่
            cache.update(at=now, ok=ok, items=items)
        else:
            cache["at"] = now - TTL + FAIL_TTL
        return cache["ok"], list(cache["items"])


def fetch(get=None) -> tuple[bool, list]:
    """(ใช้ได้ไหม, รายการทั้งหมด) ฟีด 24 ชม. — แคชไว้ ไม่ยิงซ้ำถี่ๆ"""
    return _fetch(FEED, _cache, get)


def fetch_jma(get=None) -> tuple[bool, list]:
    return _fetch(JMA_FEED, _jcache, get, parse_jma)


def _match(q: dict, jma: list):
    """เหตุการณ์ JMA ที่เป็นแผ่นดินไหวเดียวกับ USGS: ห่างไม่เกิน MATCH_KM และเวลาห่างไม่เกิน MATCH_MIN นาที"""
    for j in jma:
        if abs(j["time"] - q["time"]) <= MATCH_MIN * 60000 and km(q["lat"], q["lon"], j["lat"], j["lon"]) <= MATCH_KM:
            return j
    return None


def map_points(lat: float = HOME[0], lon: float = HOME[1], get=None, now_ms: int | None = None) -> dict:
    """จุดบนลูกโลก: ใกล้ไทย M ≥ 3.5 + ทั่วโลก M ≥ MIN_MAG_WORLD ย้อนหลัง MAP_DAYS วัน (ใหม่ก่อน) — ไม่เกิน MAP_MAX จุด
    ok = ดึงได้อย่างน้อยหนึ่งฟีด · updated = เวลาที่ดึงล่าสุด (ให้หน้าเว็บบอกได้ว่าข้อมูลสดแค่ไหน)"""
    ok1, day = fetch(get)
    ok2, week = _fetch(WEEK_FEED, _wcache, get)
    now_ms = now_ms or int(time.time() * 1000)
    since = now_ms - MAP_DAYS * 86400 * 1000
    seen, pts = set(), []
    for q in day + week:
        if q["id"] in seen or q["time"] < since:
            continue
        seen.add(q["id"])
        d = round(km(lat, lon, q["lat"], q["lon"]))
        if (d <= RADIUS_KM and q["mag"] >= MIN_MAG_NEAR) or q["mag"] >= MIN_MAG_WORLD:
            pts.append(dict(q, km=d, hours=round((now_ms - q["time"]) / 3600000, 1)))
    pts.sort(key=lambda q: (-(q["mag"] >= 6.5), -q["time"]))          # ใหญ่มากขึ้นก่อนเสมอ แล้วเรียงใหม่ไปเก่า
    updated = max(_cache["at"], _wcache["at"]) or None
    return {"ok": ok1 or ok2, "source": "USGS", "days": MAP_DAYS, "radius_km": RADIUS_KM, "min_near": MIN_MAG_NEAR,
            "min_world": MIN_MAG_WORLD, "updated": int(updated * 1000) if updated else None, "points": pts[:MAP_MAX]}


def recent(hours: float = 24, lat: float = HOME[0], lon: float = HOME[1], get=None, now_ms: int | None = None,
           jma: bool = False) -> dict:
    """แผ่นดินไหวที่ควรบอกผู้ใช้: ใกล้ (รัศมี RADIUS_KM, M ≥ 3.5) + ใหญ่ที่ไหนก็ได้ในโลก (M ≥ MIN_MAG_WORLD = 5.5)
    jma=True: เติมชินโดะให้เหตุที่ JMA วัดด้วย + "japan" = เหตุในญี่ปุ่นชินโดะ ≥ 4 ที่ไม่อยู่ในรายการข้างบน"""
    ok, items = fetch(get)
    now_ms = now_ms or int(time.time() * 1000)
    since = now_ms - int(hours * 3600 * 1000)
    near, world = [], []
    for q in items:
        if q["time"] < since:
            continue
        d = round(km(lat, lon, q["lat"], q["lon"]))
        row = dict(q, km=d)
        if d <= RADIUS_KM and q["mag"] >= MIN_MAG_NEAR:
            near.append(row)
        elif q["mag"] >= MIN_MAG_WORLD:
            world.append(row)
    near.sort(key=lambda q: (-q["mag"], -q["time"]))
    world.sort(key=lambda q: (-q["mag"], -q["time"]))
    near, world = near[:5], world[:3]
    out = {"ok": ok, "source": "USGS", "hours": hours, "home": {"th": HOME[2], "en": HOME[3]},
           "radius_km": RADIUS_KM, "near": near, "world": world}
    if jma:
        jok, jitems = fetch_jma(get)
        jitems = [j for j in jitems if j["time"] >= since]
        used = set()
        for q in near + world:
            j = _match(q, jitems)
            if j and j["shindo"]:
                q["shindo"] = j["shindo"]
                used.add(j["id"])
        japan = [dict(j, km=round(km(lat, lon, j["lat"], j["lon"]))) for j in jitems
                 if j["id"] not in used and shindo_rank(j["shindo"]) >= shindo_rank(SHINDO_NOTE)]
        japan.sort(key=lambda j: (-shindo_rank(j["shindo"]), -j["time"]))
        out.update(japan=japan[:3], jma_ok=jok, ok=ok or jok)
    return out


def llm_note(r: dict, now_ms: int | None = None) -> str:
    """บริบทสั้นๆ ให้ AI — ข้อมูลจริง ห้ามเดาเกินนี้"""
    if not r or not r.get("ok"):
        return "[ข้อมูลแผ่นดินไหวจริงตอนนี้ดึงไม่ได้: ห้ามเดาว่ามีหรือไม่มี — แนะนำให้ดูกรมอุตุนิยมวิทยา earthquake.tmd.go.th]"
    now_ms = now_ms or int(time.time() * 1000)
    src = "USGS" + (" และ JMA (ญี่ปุ่น)" if r.get("jma_ok") else "")
    rows = r["near"] + r["world"] + r.get("japan", [])
    if not rows:
        return (f"[ข้อมูลจริงจาก {src}: ไม่พบแผ่นดินไหวขนาด {MIN_MAG_NEAR}+ ในรัศมี {RADIUS_KM:,} กม. จาก{HOME[2]} "
                f"ใน {int(r['hours'])} ชม.ที่ผ่านมา — ถ้าผู้ใช้รู้สึกสั่น อาจเป็นแรงสั่นอื่น หรือเหตุที่ยังไม่เข้าระบบ ให้ดูกรมอุตุฯ ด้วย]")
    parts = []
    for q in rows[:4]:
        mins = max(0, (now_ms - q["time"]) // 60000)
        ago = f"{mins} นาทีก่อน" if mins < 120 else f"{mins // 60} ชม.ก่อน"
        parts.append(f"M{q['mag']} {q['place']} ห่าง{HOME[2]} {q['km']:,} กม. เมื่อ {ago}"
                     + (f" ชินโดะสูงสุด {q['shindo']} (JMA)" if q.get("shindo") else "")
                     + (" (USGS แจ้งเตือนสึนามิ)" if q.get("tsunami") else ""))
    return f"[ข้อมูลจริงจาก {src}: " + " · ".join(parts) + " — ใช้ตัวเลขนี้เท่านั้น ห้ามเพิ่มตัวเลขอื่น]"
