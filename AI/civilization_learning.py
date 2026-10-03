# AI/civilization_learning.py — KING DIADEM
# Civilization Learning Engine + Real-World Supply Chain Signal
# เรียนรู้ pattern มนุษย์ควบคู่กับสัญญาณโลกจริง
# FATE™: Determinism · Explainability=100% · Downside First
# Fail less. Harm less. Restore more.

from __future__ import annotations
import time
import json
import urllib.request
import urllib.error
from typing import Optional
from collections import deque

# ── STORES ────────────────────────────────────────────────────────
_learning: deque = deque(maxlen=2000)   # เดิม list โตไม่จำกัด (memory leak)
_world_cache: dict = {}          # cache signal โลก TTL 10 นาที
_CACHE_TTL   = 600               # seconds

# ── OUTCOME LABELS ────────────────────────────────────────────────
_OUTCOME_LABELS = {
    True:  "SUCCESS — ทางเลือกนำไปสู่ผลที่ดีขึ้น",
    False: "FAIL    — ทางเลือกนำไปสู่ผลที่แย่ลง",
    None:  "PENDING — ยังไม่ทราบผล",
}

# ── REAL-WORLD SUPPLY CHAIN ENDPOINTS ─────────────────────────────
# ทุกอันฟรี ไม่ต้อง API key
_SUPPLY_ENDPOINTS = {
    # BTC เป็น proxy สภาพคล่องโลก (key เดิมชื่อ oil_price แต่ไม่เคยเป็นราคาน้ำมัน — คงชื่อไว้เพื่อ compat)
    # coindesk v1 ปิดแล้ว → สถานะจะเป็น offline จนกว่าจะเปลี่ยนแหล่ง
    "oil_price": {
        "url":    "https://api.coindesk.com/v1/bpi/currentprice.json",
        "parser": lambda d: {
            "btc_usd":   d["bpi"]["USD"]["rate"],
            "signal":    "crypto_liquidity",
            "note":      "BTC as global liquidity proxy",
        },
    },
    # อัตราแลกเปลี่ยน USD/THB (ต้นทุน import)
    "forex_thb": {
        "url":    "https://open.er-api.com/v6/latest/USD",
        "parser": lambda d: {
            "usd_thb":   d["rates"].get("THB", "N/A"),
            "usd_cny":   d["rates"].get("CNY", "N/A"),
            "usd_jpy":   d["rates"].get("JPY", "N/A"),
            "signal":    "import_cost",
            "note":      "USD strength → import cost pressure",
        },
    },
    # ราคาสินค้าโภคภัณฑ์โลก (Gold as safe-haven proxy)
    "commodity_gold": {
        "url":    "https://api.metals.live/v1/spot/gold",
        "parser": lambda d: {
            "gold_usd":  d[0].get("gold") if isinstance(d, list) else d.get("price"),
            "signal":    "safe_haven_demand",
            "note":      "Gold rise → global risk aversion",
        },
    },
    # ตรวจว่าเซิร์ฟเวอร์ออกเน็ตได้ — ไม่คืน IP สาธารณะของเซิร์ฟเวอร์ให้ client (เดิมคืน "ip")
    "system_network": {
        "url":    "https://api.ipify.org?format=json",
        "parser": lambda d: {
            "online": bool(d.get("ip")),
            "signal": "system_online",
            "note":   "System connectivity check",
        },
    },
}

_TIMEOUT = 5


def _fetch_signal(key: str, cfg: dict) -> dict:
    """Fetch single endpoint — deterministic error handling"""
    try:
        req = urllib.request.Request(
            cfg["url"],
            headers={"User-Agent": "KING-DIADEM/4.7"}
        )
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:  # nosec B310 — URL คงที่ https ในโค้ด
            data = json.loads(resp.read(1_000_000).decode("utf-8"))
            return {**cfg["parser"](data), "status": "ok", "fetched_at": int(time.time())}
    except urllib.error.HTTPError as e:
        return {"status": "offline", "error": f"HTTP {e.code}", "signal": key}
    except Exception as e:
        # ไม่ส่งรายละเอียดเครือข่าย/exception ภายในออกไป
        return {"status": "offline", "error": type(e).__name__, "signal": key}


def fetch_world_signals(force: bool = False) -> dict:
    """
    ดึงสัญญาณ Supply Chain โลกจริง — cached 10 นาที
    ดึง: forex (ต้นทุน import), crypto (liquidity), gold (risk aversion), network

    Returns: dict ของ signals พร้อม fate_note
    """
    global _world_cache

    now = int(time.time())
    if not force and _world_cache.get("_fetched_at", 0) + _CACHE_TTL > now:
        return _world_cache   # return cache

    signals: dict[str, dict] = {}
    offline: list[str] = []

    for key, cfg in _SUPPLY_ENDPOINTS.items():
        result = _fetch_signal(key, cfg)
        signals[key] = result
        if result.get("status") == "offline":
            offline.append(key)

    # Synthesize supply chain pressure score
    pressure = _compute_supply_pressure(signals)

    _world_cache = {
        "signals":          signals,
        "supply_pressure":  pressure,
        "online_count":     len(_SUPPLY_ENDPOINTS) - len(offline),
        "offline":          offline,
        "fate_note": (
            f"OFFLINE: {', '.join(offline)}" if offline
            else "✅ world signals active"
        ),
        "_fetched_at":      now,
    }
    return _world_cache


def _compute_supply_pressure(signals: dict) -> dict:
    """
    คำนวณ supply chain pressure จาก signals ที่ได้
    — deterministic, ไม่ใช้ random
    """
    pressure_level = "UNKNOWN"
    notes = []

    forex = signals.get("forex_thb", {})
    if forex.get("status") == "ok":
        thb = forex.get("usd_thb", 0)
        try:
            thb_val = float(str(thb).replace(",", ""))
            if thb_val > 36.0:
                notes.append("USD แข็ง → ต้นทุน import สูง")
                pressure_level = "HIGH"
            elif thb_val > 34.0:
                notes.append("USD ปานกลาง → ต้นทุน import ปกติ")
                pressure_level = "MODERATE"
            else:
                pressure_level = "LOW"
        except (ValueError, TypeError):
            pass

    gold = signals.get("commodity_gold", {})
    if gold.get("status") == "ok" and gold.get("gold_usd"):
        notes.append("Gold signal active → risk aversion ตรวจได้")

    return {
        "level":   pressure_level,
        "notes":   notes,
        "sources": [k for k, v in signals.items() if v.get("status") == "ok"],
    }


# ── HUMAN PATTERN LEARNING ────────────────────────────────────────

def record_learning(
    question: str = "",
    decision: str = "",
    planet_context: Optional[dict] = None,
    success: Optional[bool] = None,
    attach_world_signal: bool = False,
) -> dict:
    """
    บันทึก pattern การตัดสินใจ + embed world signal ณ เวลานั้น
    attach_world_signal=True → ฝัง snapshot ของ supply chain ไว้ใน entry

    FATE™: Determinism — entry เดิมแก้ไม่ได้ append only
    """
    question = str(question or "")
    decision = str(decision or "")
    if not question.strip():
        return {"error": "FATE_VIOLATION: question must not be empty"}

    world_snapshot = None
    if attach_world_signal:
        ws = fetch_world_signals()
        world_snapshot = {
            "supply_pressure": ws.get("supply_pressure", {}),
            "online_count":    ws.get("online_count", 0),
            "fetched_at":      ws.get("_fetched_at", 0),
        }

    entry = {
        "id":             (_learning[-1]["id"] + 1) if _learning else 1,
        "timestamp":      int(time.time()),
        "question":       question.strip(),
        "decision":       decision.strip() or "ไม่ระบุ",
        "context":        planet_context if isinstance(planet_context, dict) else {},
        "success":        success,
        "outcome_label":  _OUTCOME_LABELS.get(success, "UNKNOWN"),
        "world_signal":   world_snapshot,
        "axiom_check": {
            "has_question":        bool(question.strip()),
            "has_decision":        bool(decision.strip()),
            "has_context":         bool(planet_context),
            "outcome_known":       success is not None,
            "has_world_signal":    world_snapshot is not None,
        },
    }
    _learning.append(entry)
    return entry


def get_learning() -> list[dict]:
    """Return all learning records"""
    return list(_learning)


def get_learning_summary() -> dict:
    """
    สรุป pattern + correlate กับ world signal
    ใช้ใน /dashboard
    """
    total   = len(_learning)
    success = sum(1 for e in _learning if e.get("success") is True)
    failed  = sum(1 for e in _learning if e.get("success") is False)
    pending = total - success - failed
    success_rate = round(success / total * 100, 1) if total > 0 else 0.0

    # Cross-correlate: decisions made during HIGH supply pressure
    high_pressure_decisions = [
        e for e in _learning
        if e.get("world_signal", {})
        and e["world_signal"].get("supply_pressure", {}).get("level") == "HIGH"
    ]

    return {
        "total_records":              total,
        "success_count":              success,
        "fail_count":                 failed,
        "pending_count":              pending,
        "success_rate":               success_rate,
        "fate_signal":                "STABLE" if success_rate >= 60 else "DRIFT_WARNING",
        "high_pressure_decisions":    len(high_pressure_decisions),
        "world_signal_attached":      sum(1 for e in _learning if e.get("world_signal")),
        "recent_5":                   list(_learning)[-5:],
    }
