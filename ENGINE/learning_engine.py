# ENGINE/learning_engine.py
"""
KING DIADEM — Learning Engine
เรียนรู้บริบทผู้ใช้จริง + เชื่อม supply chain
ไม่ใช่แค่นับ pattern — คืนทางเลือกจากทรัพยากรในโลกจริง

Architecture:
  User context → pattern analysis → supply chain query → ranked options
  ทุก option ต้องมี real-world resource backing — ไม่คืน string เปล่า
"""
from __future__ import annotations
import json
import os
import time
import math
from typing import Optional
from collections import defaultdict

LOG_FILE   = "data/decision_log.jsonl"   # JSONL — append-safe กว่า JSON
MODEL_FILE = "data/learning_model.json"

# ── Safe I/O ──────────────────────────────────────────────────────
def _load_jsonl(path: str) -> list:
    if not os.path.exists(path):
        return []
    entries = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except Exception:
                        pass
    except Exception:
        pass
    return entries

def _load_model() -> dict:
    try:
        if os.path.exists(MODEL_FILE):
            with open(MODEL_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {
        "user_contexts":     {},   # email → context profile
        "location_patterns": {},   # location → resource patterns
        "decision_outcomes": {},   # decision_type → success_rate
        "supply_cache":      {},   # query → cached supply chain result
        "supply_cache_ttl":  {},   # query → cache timestamp
        "last_trained":      0,
        "version":           "2.0",
    }

def _save_model(model: dict) -> bool:
    try:
        os.makedirs(os.path.dirname(MODEL_FILE) or ".", exist_ok=True)
        tmp = MODEL_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(model, f, indent=2, ensure_ascii=False)
        os.replace(tmp, MODEL_FILE)
        return True
    except Exception:
        return False

def _append_log(entry: dict) -> bool:
    try:
        os.makedirs(os.path.dirname(LOG_FILE) or ".", exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return True
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════════
# SUPPLY CHAIN LAYER
# เชื่อมแหล่งทรัพยากรจริงในโลก — food/water/medicine/fuel/shelter
# ══════════════════════════════════════════════════════════════════

# Supply chain providers — real APIs ที่มีอยู่
try:
    from INTEGRATIONS.google_maps import search_nearby
    _MAPS = True
except ImportError:
    _MAPS = False

try:
    from INTEGRATIONS.google_search import search as web_search
    _SEARCH = True
except ImportError:
    _SEARCH = False

# Resource categories + supply chain mapping
SUPPLY_CATEGORIES = {
    "food": {
        "queries":    ["ร้านอาหาร", "ตลาดสด", "ร้านสะดวกซื้อ", "food market"],
        "radius_m":   2000,
        "urgency":    "HIGH",
        "unit":       "มื้อ",
    },
    "water": {
        "queries":    ["น้ำดื่ม", "ร้านสะดวกซื้อ", "ปั๊มน้ำ", "water supply"],
        "radius_m":   1000,
        "urgency":    "HIGH",
        "unit":       "ลิตร",
    },
    "medicine": {
        "queries":    ["ร้านขายยา", "pharmacy", "drugstore", "เภสัชกรรม"],
        "radius_m":   3000,
        "urgency":    "MEDIUM",
        "unit":       "ร้าน",
    },
    "fuel": {
        "queries":    ["ปั๊มน้ำมัน", "gas station", "PTT", "Shell"],
        "radius_m":   5000,
        "urgency":    "MEDIUM",
        "unit":       "ปั๊ม",
    },
    "shelter": {
        "queries":    ["ที่พัก", "hotel", "วัด", "shelter", "โรงแรม"],
        "radius_m":   3000,
        "urgency":    "HIGH",
        "unit":       "ที่",
    },
    "income": {
        "queries":    ["งานพาร์ทไทม์", "หางาน", "part time", "งานด่วน"],
        "radius_m":   10000,
        "urgency":    "MEDIUM",
        "unit":       "ตำแหน่ง",
    },
    "medical": {
        "queries":    ["โรงพยาบาล", "คลินิก", "hospital", "clinic"],
        "radius_m":   5000,
        "urgency":    "CRITICAL",
        "unit":       "แห่ง",
    },
}

SUPPLY_CACHE_TTL = 3600  # 1 ชั่วโมง


def _query_supply_chain(
    category: str,
    lat:      Optional[float] = None,
    lng:      Optional[float] = None,
    context:  Optional[dict]  = None,
) -> dict:
    """
    Query supply chain จริง — Google Maps + Web Search
    พร้อม cache 1 ชั่วโมง
    """
    model    = _load_model()
    cache_key = f"{category}:{lat:.4f},{lng:.4f}" if lat and lng else f"{category}:global"
    now      = time.time()

    # ── Cache hit ────────────────────────────────────────────────
    cached_ttl = model["supply_cache_ttl"].get(cache_key, 0)
    if now - cached_ttl < SUPPLY_CACHE_TTL and cache_key in model["supply_cache"]:
        return {**model["supply_cache"][cache_key], "cached": True}

    cfg     = SUPPLY_CATEGORIES.get(category, SUPPLY_CATEGORIES["food"])
    results = []

    # ── Maps API ─────────────────────────────────────────────────
    if _MAPS and lat and lng:
        for query in cfg["queries"][:2]:
            try:
                found = search_nearby(lat, lng, query, radius_m=cfg["radius_m"])
                if found:
                    for item in found[:3]:
                        results.append({
                            "name":     item.get("name",    "—"),
                            "address":  item.get("address", "—"),
                            "lat":      item.get("lat",     lat),
                            "lng":      item.get("lng",     lng),
                            "open_now": item.get("open_now", None),
                            "rating":   item.get("rating",  None),
                            "maps_url": f"https://www.google.com/maps/search/{query.replace(' ','+')}/@{lat},{lng},15z",
                            "source":   "google_maps",
                        })
            except Exception:
                pass

    # ── Web Search fallback ───────────────────────────────────────
    if not results and _SEARCH:
        try:
            loc_hint = f"ใกล้ {lat},{lng}" if lat else ""
            hits = web_search(f"{cfg['queries'][0]} {loc_hint}", num=3)
            for h in (hits.get("results") or [])[:3]:
                results.append({
                    "name":    h.get("title",   "—"),
                    "address": h.get("snippet", "—"),
                    "url":     h.get("url",     ""),
                    "source":  "web_search",
                })
        except Exception:
            pass

    # ── Fallback URL ──────────────────────────────────────────────
    if not results:
        import urllib.parse
        for q in cfg["queries"][:1]:
            enc = urllib.parse.quote(q)
            url = (f"https://www.google.com/maps/search/{enc}/@{lat},{lng},14z"
                   if lat else f"https://www.google.com/maps/search/{enc}")
            results.append({
                "name":    q,
                "maps_url": url,
                "source":  "fallback_url",
                "note":    "ค้นหาด้วยตัวเองผ่านลิงก์นี้",
            })

    supply_result = {
        "category":   category,
        "urgency":    cfg["urgency"],
        "unit":       cfg["unit"],
        "results":    results[:5],
        "count":      len(results),
        "lat":        lat,
        "lng":        lng,
        "queried_at": now,
        "cached":     False,
    }

    # Save to cache
    model["supply_cache"][cache_key]     = supply_result
    model["supply_cache_ttl"][cache_key] = now
    _save_model(model)

    return supply_result


# ══════════════════════════════════════════════════════════════════
# USER CONTEXT LEARNING
# ══════════════════════════════════════════════════════════════════

def record_context(
    user_email:  str,
    context:     dict,
    decision:    str,
    outcome:     Optional[str] = None,   # "success" | "failure" | None
) -> bool:
    """บันทึก context + decision — เรียนรู้ทุก interaction"""
    entry = {
        "user":      user_email,
        "context":   context,
        "decision":  decision,
        "outcome":   outcome,
        "timestamp": time.time(),
    }
    return _append_log(entry)


def _train_from_logs(logs: list) -> dict:
    """
    วิเคราะห์ pattern จาก logs จริง
    - location → resource availability
    - context pattern → decision success rate
    - entropy/resource → outcome correlation
    """
    model = _load_model()

    user_contexts:     dict = defaultdict(lambda: {
        "visit_count": 0, "locations": [], "avg_entropy": 0,
        "avg_resource": 0, "decisions": [], "last_seen": 0,
    })
    location_patterns: dict = defaultdict(lambda: {
        "visit_count": 0, "avg_food": 0, "avg_risk": 0, "outcomes": [],
    })
    decision_outcomes: dict = defaultdict(lambda: {"total": 0, "success": 0})

    for entry in logs:
        user    = entry.get("user",     "anonymous")
        ctx     = entry.get("context",  {})
        dec     = entry.get("decision", "unknown")
        outcome = entry.get("outcome")
        loc     = ctx.get("location",   "")
        ts      = entry.get("timestamp", 0)

        # User profile
        uc = user_contexts[user]
        uc["visit_count"] += 1
        uc["last_seen"]    = max(uc["last_seen"], ts)
        if loc:
            if loc not in uc["locations"]:
                uc["locations"].append(loc)
        # Running average entropy/resource
        n = uc["visit_count"]
        uc["avg_entropy"]  = (uc["avg_entropy"]  * (n-1) + float(ctx.get("entropy",  40))) / n
        uc["avg_resource"] = (uc["avg_resource"] * (n-1) + float(ctx.get("resource", 50))) / n
        if dec not in uc["decisions"]:
            uc["decisions"].append(dec)

        # Location patterns
        if loc:
            lp = location_patterns[loc]
            lp["visit_count"] += 1
            m = lp["visit_count"]
            lp["avg_food"] = (lp["avg_food"] * (m-1) + float(ctx.get("food", 50))) / m
            lp["avg_risk"] = (lp["avg_risk"] * (m-1) + float(ctx.get("risk", 50))) / m
            if outcome:
                lp["outcomes"].append(outcome)

        # Decision outcomes
        do = decision_outcomes[dec]
        do["total"] += 1
        if outcome == "success":
            do["success"] += 1

    # Compute success rates
    for dec, do in decision_outcomes.items():
        do["success_rate"] = round(do["success"] / max(1, do["total"]), 3)

    model["user_contexts"]     = {k: dict(v) for k, v in user_contexts.items()}
    model["location_patterns"] = {k: dict(v) for k, v in location_patterns.items()}
    model["decision_outcomes"] = {k: dict(v) for k, v in decision_outcomes.items()}
    model["last_trained"]      = time.time()

    _save_model(model)
    return model


def train_model() -> dict:
    logs = _load_jsonl(LOG_FILE)
    return _train_from_logs(logs)


# ══════════════════════════════════════════════════════════════════
# MAIN: get_options — คืนทางเลือกจากทรัพยากรจริง
# ══════════════════════════════════════════════════════════════════

def get_options(
    user_email:  str,
    context:     dict,
    max_options: int = 5,
) -> dict:
    """
    Entry point หลัก — เรียนรู้บริบท + คืนทางเลือกจากโลกจริง

    context keys:
        entropy, resource, stability, choices,
        food, money, energy, water,
        location, lat, lng,
        need (str: "food"|"water"|"income"|"shelter"|"medicine"|"medical")
    """
    t0    = time.time()
    model = _load_model()
    lat   = context.get("lat")
    lng   = context.get("lng")
    need  = context.get("need", _infer_need(context))

    # ── User context profile ──────────────────────────────────────
    user_profile = model["user_contexts"].get(user_email, {})
    location_key = context.get("location", "")
    loc_pattern  = model["location_patterns"].get(location_key, {})

    # ── Supply chain query ────────────────────────────────────────
    supply = _query_supply_chain(need, lat, lng, context)

    # ── Rank options ──────────────────────────────────────────────
    options = []
    for item in supply["results"][:max_options]:
        score = _score_option(item, context, loc_pattern, model)
        options.append({**item, "relevance_score": score})

    options.sort(key=lambda x: x["relevance_score"], reverse=True)

    # ── Survival floor check ──────────────────────────────────────
    entropy  = float(context.get("entropy",  40))
    resource = float(context.get("resource", 50))
    money    = float(context.get("money",    100))

    waterline = round(
        (100 - entropy) * 0.40 +
        resource        * 0.35 +
        min(100, money/10) * 0.25,
        2
    )

    # ── Record this query for learning ───────────────────────────
    record_context(user_email, context, need)

    return {
        "user":             user_email,
        "need":             need,
        "options":          options,
        "option_count":     len(options),
        "waterline":        waterline,
        "status":           "CRITICAL" if waterline < 30 else "WARNING" if waterline < 55 else "STABLE",
        "supply_source":    supply.get("cached") and "cache" or "live",
        "user_visits":      user_profile.get("visit_count", 0),
        "location_known":   bool(loc_pattern),
        "latency_ms":       round((time.time()-t0)*1000, 1),
        "choice_count":     len(options),
        "choice_preserved": len(options) > 0,
        "axiom":            "Choice(t) ≥ 1 → collapse = False",
    }


def _infer_need(context: dict) -> str:
    """อนุมาน need จาก context ถ้าไม่ได้ระบุ"""
    food   = float(context.get("food",   3))
    money  = float(context.get("money",  100))
    energy = float(context.get("energy", 50))

    if food <= 1:
        return "food"
    if money < 50:
        return "income"
    if energy < 20:
        return "shelter"
    return "food"   # default


def _score_option(
    item:        dict,
    context:     dict,
    loc_pattern: dict,
    model:       dict,
) -> float:
    """
    Score option 0-1 จาก:
    - open_now (ถ้ารู้)
    - rating
    - distance (ถ้ามี)
    - location pattern (เคยใช้ได้ผลไหม)
    """
    score = 0.5   # base

    if item.get("open_now") is True:
        score += 0.20
    elif item.get("open_now") is False:
        score -= 0.20

    rating = item.get("rating")
    if rating:
        score += (float(rating) - 3.0) * 0.08   # 5.0 → +0.16, 1.0 → -0.16

    # location success rate
    outcomes = loc_pattern.get("outcomes", [])
    if outcomes:
        success_rate = outcomes.count("success") / len(outcomes)
        score += (success_rate - 0.5) * 0.20

    # source quality
    if item.get("source") == "google_maps":
        score += 0.10
    elif item.get("source") == "fallback_url":
        score -= 0.10

    return round(max(0.0, min(1.0, score)), 3)


# ══════════════════════════════════════════════════════════════════
# BACKWARD COMPAT — ชื่อเดิมยังใช้ได้
# ══════════════════════════════════════════════════════════════════

def predict_risk(risk_value) -> float:
    model = _load_model()
    # ใช้ decision_outcomes แทน risk_patterns เดิม
    outcomes = model["decision_outcomes"]
    key = str(risk_value)
    if key in outcomes:
        return outcomes[key].get("success_rate", 0.5)
    return 0.5

def predict_food(food_value) -> float:
    model = _load_model()
    locs  = model["location_patterns"]
    # หา location ที่มี avg_food ใกล้เคียงที่สุด
    target = float(food_value) if isinstance(food_value, (int, float)) else 50.0
    best   = min(locs.values(), key=lambda x: abs(x.get("avg_food", 50) - target), default=None)
    return best["avg_food"] if best else target

def load_logs() -> list:
    return _load_jsonl(LOG_FILE)
