# ENGINE/energy_governor.py
# KING DIADEM — Energy Governor
# Rate limiting + energy model สำหรับ API calls
# Thread-safe, waterline-aware — ไม่ใช่แค่ counter

from __future__ import annotations
import time
from threading import Lock
from typing import Tuple

# ── Config ────────────────────────────────────────────────────────
BASE_ENERGY      = 100.0
RECOVERY_RATE    = 0.8      # energy/second
COST_PER_REQUEST = 3.0
WINDOW_SEC       = 60
RATE_LIMIT       = 30       # max requests per window

# ── Store ─────────────────────────────────────────────────────────
_STORE: dict[str, dict] = {}
_LOCK  = Lock()


def _get_user(api_key: str, now: float) -> dict:
    """Get or init user record — always called under lock"""
    if api_key not in _STORE:
        _STORE[api_key] = {
            "timestamps":   [],
            "energy":       BASE_ENERGY,
            "last_update":  now,
            "total_blocked": 0,
            "total_served":  0,
        }
    return _STORE[api_key]


def allow_request(api_key: str) -> Tuple[bool, dict | str]:
    """
    ตรวจสอบว่า request นี้ผ่านได้ไหม
    return (True, status_dict) หรือ (False, reason_str)
    """
    now = time.time()

    with _LOCK:
        user = _get_user(api_key, now)

        # ── Recover energy ─────────────────────────────────────────
        elapsed         = now - user["last_update"]
        recovered       = elapsed * RECOVERY_RATE
        user["energy"]  = min(BASE_ENERGY, user["energy"] + recovered)
        user["last_update"] = now

        # ── Clean old timestamps ───────────────────────────────────
        user["timestamps"] = [
            t for t in user["timestamps"] if now - t < WINDOW_SEC
        ]

        # ── Rate limit check ───────────────────────────────────────
        if len(user["timestamps"]) >= RATE_LIMIT:
            user["total_blocked"] += 1
            oldest = user["timestamps"][0] if user["timestamps"] else now
            retry_in = max(0, WINDOW_SEC - (now - oldest))
            return False, f"RATE_LIMIT — retry in {retry_in:.0f}s"

        # ── Energy check ───────────────────────────────────────────
        if user["energy"] < COST_PER_REQUEST:
            user["total_blocked"] += 1
            recover_time = (COST_PER_REQUEST - user["energy"]) / RECOVERY_RATE
            return False, f"NO_ENERGY — recover in {recover_time:.1f}s"

        # ── Pass ───────────────────────────────────────────────────
        user["timestamps"].append(now)
        user["energy"]      -= COST_PER_REQUEST
        user["total_served"] += 1

        return True, {
            "energy":             round(user["energy"], 2),
            "remaining_requests": RATE_LIMIT - len(user["timestamps"]),
            "total_served":       user["total_served"],
        }


def get_status(api_key: str) -> dict:
    """สถานะปัจจุบันของ user — ใช้กับ /health หรือ UI"""
    now = time.time()
    with _LOCK:
        if api_key not in _STORE:
            return {
                "energy":             BASE_ENERGY,
                "remaining_requests": RATE_LIMIT,
                "total_served":       0,
                "total_blocked":      0,
            }
        user = _STORE[api_key]
        # recover ก่อนรายงาน
        elapsed        = now - user["last_update"]
        current_energy = min(BASE_ENERGY, user["energy"] + elapsed * RECOVERY_RATE)
        recent_ts      = [t for t in user["timestamps"] if now - t < WINDOW_SEC]
        return {
            "energy":             round(current_energy, 2),
            "remaining_requests": max(0, RATE_LIMIT - len(recent_ts)),
            "total_served":       user["total_served"],
            "total_blocked":      user["total_blocked"],
            "waterline":          round((current_energy / BASE_ENERGY) * 100, 1),
        }


def reset_user(api_key: str) -> None:
    """Reset user state — ใช้สำหรับ test หรือ admin"""
    with _LOCK:
        _STORE.pop(api_key, None)


def global_stats() -> dict:
    """รวม stats ทุก user — ใช้ใน /health endpoint"""
    with _LOCK:
        return {
            "active_users": len(_STORE),
            "total_served": sum(u["total_served"]  for u in _STORE.values()),
            "total_blocked": sum(u["total_blocked"] for u in _STORE.values()),
        }
