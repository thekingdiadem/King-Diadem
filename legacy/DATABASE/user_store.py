# DATABASE/user_store.py
"""
KING DIADEM — User Store (in-memory + DB bridge)
ปัญหาเดิม: in-memory dict หายทุกครั้ง Render restart
แก้: ใช้ user_db.py เป็น persistent layer
in-memory เป็น cache เท่านั้น
"""
from __future__ import annotations
import threading
import time
from typing import Optional

try:
    from DATABASE.user_db import get_user, add_credit, set_plan as _db_set_plan, use_credit
    _DB_LOADED = True
except ImportError:
    _DB_LOADED = False

# ── In-memory cache (per-process, resets on restart) ─────────────
_cache: dict = {}
_lock  = threading.Lock()

PLAN_LIMITS = {
    "free":    10,
    "basic":   100,
    "pro":     500,
    "premium": 9999,
}


# ── Cache helpers ─────────────────────────────────────────────────
def _get_cached(api_key: str) -> dict:
    with _lock:
        return dict(_cache.get(api_key, {}))

_MAX_CACHE = 20000   # เดิมโตไม่จำกัด (หนึ่ง entry ต่อ key ที่เคยเห็น)

def _set_cached(api_key: str, data: dict) -> None:
    with _lock:
        if api_key not in _cache and len(_cache) >= _MAX_CACHE:
            _cache.pop(next(iter(_cache)))
        _cache[api_key] = {**_cache.get(api_key, {}), **data}

def _init_entry(api_key: str) -> dict:
    entry = {
        "plan":          "free",
        "queries_today": 0,
        "queries_reset": time.strftime("%Y-%m-%d"),
    }
    _set_cached(api_key, entry)
    return entry


# ── Daily reset check ─────────────────────────────────────────────
def _check_reset(api_key: str) -> None:
    """Reset queries_today ถ้าเป็นวันใหม่"""
    cached = _get_cached(api_key)
    today  = time.strftime("%Y-%m-%d")
    if cached.get("queries_reset") != today:
        _set_cached(api_key, {"queries_today": 0, "queries_reset": today})


# ── Public API ────────────────────────────────────────────────────
def create_user(api_key: str, plan: str = "free") -> None:
    _init_entry(api_key)
    _set_cached(api_key, {"plan": plan})


def get_plan(api_key: str) -> str:
    # DB first — ถ้า api_key เป็น email
    if _DB_LOADED and "@" in str(api_key):
        user = get_user(api_key)
        if user:
            return user.get("plan", "free")

    cached = _get_cached(api_key)
    return cached.get("plan", "free")


def set_plan(api_key: str, plan: str) -> None:
    _set_cached(api_key, {"plan": plan})
    if _DB_LOADED and "@" in api_key:
        try:
            _db_set_plan(api_key, plan)
        except Exception:
            pass


def get_queries_today(api_key: str) -> int:
    _check_reset(api_key)
    cached = _get_cached(api_key)
    return cached.get("queries_today", 0)


def add_query(api_key: str) -> None:
    _check_reset(api_key)
    with _lock:
        entry = _cache.get(api_key) or _init_entry(api_key)
        entry["queries_today"] = entry.get("queries_today", 0) + 1
        _cache[api_key] = entry


def can_query(api_key: str) -> bool:
    """ตรวจสอบว่ายัง query ได้ไหมตาม plan limit"""
    plan    = get_plan(api_key)
    limit   = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
    used    = get_queries_today(api_key)
    return used < limit


def get_remaining_queries(api_key: str) -> int:
    plan  = get_plan(api_key)
    limit = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
    used  = get_queries_today(api_key)
    return max(0, limit - used)


def get_status(api_key: str) -> dict:
    _check_reset(api_key)
    plan      = get_plan(api_key)
    limit     = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
    used      = get_queries_today(api_key)
    remaining = max(0, limit - used)

    credits = 0
    if _DB_LOADED and "@" in api_key:
        try:
            user = get_user(api_key)
            credits = user.get("credits", 0) if user else 0
        except Exception:
            pass

    return {
        "api_key":           str(api_key)[:8] + "...",   # ไม่ expose key เต็ม
        "plan":              plan,
        "queries_today":     used,
        "queries_limit":     limit,
        "queries_remaining": remaining,
        "credits":           credits,
        "can_query":         remaining > 0 or credits > 0,
    }
