"""
SECURITY/emergency_mode.py — KING DIADEM
IP-based Rate Limiter + Emergency Lockdown
Production-grade: thread-safe, TTL cleanup, graduated response

Defense layers:
  L1 — Per-IP rate limit (sliding window)
  L2 — Global request throttle
  L3 — Emergency lockdown (manual trigger)
  L4 — Suspicious pattern detection
  L5 — Auto-ban on repeated violations
"""

import time
import threading
import hashlib
from collections import defaultdict
from typing import Literal

# ══════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════
RATE_LIMIT_WINDOW   = 3600    # 1 hour window
RATE_LIMIT_MAX      = 60      # requests per IP per hour
BURST_WINDOW        = 10      # burst window (seconds)
BURST_MAX           = 15      # max requests in burst window
BAN_THRESHOLD       = 3       # violations before auto-ban
BAN_DURATION        = 86400   # 24h ban
CLEANUP_INTERVAL    = 300     # clean stale entries every 5 min

# Graduated response thresholds (% of limit)
WARN_AT    = 0.75   # 75% → warn
THROTTLE_AT= 0.90   # 90% → throttle
BLOCK_AT   = 1.00   # 100% → block

_lock      = threading.Lock()
_ip_table  : dict = {}   # ip → {requests: [(ts)], violations: int, banned_until: float}
_ban_list  : dict = {}   # ip_hash → banned_until
_lockdown  : bool = False
_lockdown_reason: str = ""
_last_cleanup: float = 0.0


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════
import os as _os
_IP_SALT = (_os.getenv("SECRET_KEY") or _os.urandom(16).hex()).encode()


def _hash_ip(ip: str) -> str:
    """Hash IP เพื่อไม่เก็บ raw IP ใน memory (privacy)
    ใส่ salt — sha256 ของ IPv4 ล้วนไล่ย้อนกลับได้ทั้ง 2^32 ค่าในไม่กี่นาที"""
    return hashlib.sha256(_IP_SALT + str(ip).encode()).hexdigest()[:16]


def _now() -> float:
    return time.time()


def _cleanup_stale():
    """ลบ entry เก่าที่หมด window แล้ว — ป้องกัน memory leak"""
    global _last_cleanup
    now = _now()
    if now - _last_cleanup < CLEANUP_INTERVAL:
        return
    _last_cleanup = now
    # เดิมข้าม entry ที่ requests ว่าง (ไม่เคยถูกลบ) และไม่ล้าง ban ที่หมดอายุ → โตไม่หยุด
    expired = [
        k for k, v in _ip_table.items()
        if not v["requests"] or (now - v["requests"][-1]) > RATE_LIMIT_WINDOW * 2
    ]
    for k in expired:
        del _ip_table[k]
    for k in [k for k, until in _ban_list.items() if until <= now]:
        del _ban_list[k]


def _sliding_window_count(requests: list, window: float) -> int:
    """นับ request ใน sliding window"""
    now = _now()
    cutoff = now - window
    return sum(1 for ts in requests if ts >= cutoff)


def _prune_requests(requests: list, window: float) -> list:
    """ตัด request เก่าออก"""
    cutoff = _now() - window
    return [ts for ts in requests if ts >= cutoff]


# ══════════════════════════════════════════════════════════════════
# MAIN: check_emergency
# ══════════════════════════════════════════════════════════════════
ResponseType = Literal["ok", "warn", "throttle", "block", "ban", "lockdown"]


def check_emergency(ip: str, endpoint: str = "") -> dict:
    """
    ตรวจสอบ IP ก่อน allow request
    คืน:
      {"allowed": bool, "status": ResponseType, "remaining": int,
       "retry_after": int | None, "reason": str}
    """
    global _lockdown

    ip_hash = _hash_ip(ip)

    with _lock:
        _cleanup_stale()

        # ── L3: Emergency Lockdown ───────────────────────────────
        if _lockdown:
            return _response(False, "lockdown", 0,
                             retry_after=60,
                             reason=f"System lockdown: {_lockdown_reason}")

        # ── L5: Ban check ────────────────────────────────────────
        ban_until = _ban_list.get(ip_hash, 0)
        if _now() < ban_until:
            retry = int(ban_until - _now())
            return _response(False, "ban", 0,
                             retry_after=retry,
                             reason=f"IP banned for {retry}s")

        # ── Init entry ───────────────────────────────────────────
        if ip_hash not in _ip_table:
            _ip_table[ip_hash] = {
                "requests":   [],
                "violations": 0,
                "first_seen": _now(),
            }

        entry = _ip_table[ip_hash]
        now   = _now()
        entry["requests"].append(now)

        # Prune old entries
        entry["requests"] = _prune_requests(entry["requests"], RATE_LIMIT_WINDOW)

        # ── L1: Per-IP Rate Limit (hourly) ───────────────────────
        hourly_count = _sliding_window_count(entry["requests"], RATE_LIMIT_WINDOW)
        remaining    = max(0, RATE_LIMIT_MAX - hourly_count)
        ratio        = hourly_count / RATE_LIMIT_MAX

        if ratio >= BLOCK_AT:
            entry["violations"] += 1
            if entry["violations"] >= BAN_THRESHOLD:
                _ban_list[ip_hash] = now + BAN_DURATION
                return _response(False, "ban", 0,
                                 retry_after=BAN_DURATION,
                                 reason=f"Auto-banned after {BAN_THRESHOLD} violations")
            return _response(False, "block", 0,
                             retry_after=int(RATE_LIMIT_WINDOW - (now - entry["requests"][0])),
                             reason="Rate limit exceeded")

        # ── L1b: Burst check (10s window) ───────────────────────
        burst_count = _sliding_window_count(entry["requests"], BURST_WINDOW)
        if burst_count > BURST_MAX:
            return _response(False, "throttle", remaining,
                             retry_after=BURST_WINDOW,
                             reason=f"Burst limit: {burst_count}/{BURST_MAX} in {BURST_WINDOW}s")

        # ── L4: Suspicious pattern ───────────────────────────────
        if _is_suspicious(entry, endpoint):
            entry["violations"] += 1
            return _response(False, "throttle", remaining,
                             retry_after=30,
                             reason="Suspicious request pattern detected")

        # ── Graduated response ───────────────────────────────────
        if ratio >= WARN_AT:
            status = "warn"
        else:
            status = "ok"

        return _response(True, status, remaining, reason="")


def _is_suspicious(entry: dict, endpoint: str) -> bool:
    """ตรวจ pattern น่าสงสัย"""
    requests = entry["requests"]
    if len(requests) < 5:
        return False

    # Pattern: request มาถี่มากใน 2 วินาที (bot-like)
    recent = [ts for ts in requests if ts >= _now() - 2]
    if len(recent) >= 8:
        return True

    # Pattern: violations สูง
    if entry.get("violations", 0) >= 2:
        return True

    return False


def _response(allowed: bool, status: ResponseType,
              remaining: int, retry_after: int = None,
              reason: str = "") -> dict:
    return {
        "allowed":     allowed,
        "status":      status,
        "remaining":   remaining,
        "retry_after": retry_after,
        "reason":      reason,
        "timestamp":   _now(),
    }


# ══════════════════════════════════════════════════════════════════
# ADMIN CONTROLS
# ══════════════════════════════════════════════════════════════════
def trigger_lockdown(reason: str = "manual"):
    global _lockdown, _lockdown_reason
    with _lock:
        _lockdown = True
        _lockdown_reason = reason
    print(f"🔴 EMERGENCY LOCKDOWN: {reason}")


def release_lockdown():
    global _lockdown, _lockdown_reason
    with _lock:
        _lockdown = False
        _lockdown_reason = ""
    print("🟢 Lockdown released")


def unban_ip(ip: str):
    ip_hash = _hash_ip(ip)
    with _lock:
        _ban_list.pop(ip_hash, None)
        if ip_hash in _ip_table:
            _ip_table[ip_hash]["violations"] = 0


def get_stats() -> dict:
    with _lock:
        return {
            "tracked_ips":  len(_ip_table),
            "banned_ips":   len([v for v in _ban_list.values() if v > _now()]),
            "lockdown":     _lockdown,
            "lockdown_reason": _lockdown_reason,
        }
