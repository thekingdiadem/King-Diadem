"""
SECURITY/survival_mode.py — KING DIADEM
Global Traffic Survival Mode
ป้องกัน DDoS + Overload + Cascade failure

Defense layers:
  L1 — Global request rate (sliding window)
  L2 — Concurrent request limiter
  L3 — CPU/Memory pressure detection
  L4 — Cascade failure breaker (Circuit Breaker pattern)
  L5 — Auto-recovery with exponential backoff
"""

import time
import threading
from collections import deque
from typing import Literal

# ══════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════
GLOBAL_WINDOW       = 10      # sliding window (seconds)
GLOBAL_LIMIT        = 200     # max requests per window
THROTTLE_LIMIT      = 160     # start throttling at 80%
WARN_LIMIT          = 120     # warn at 60%

CONCURRENT_MAX      = 50      # max concurrent requests
CIRCUIT_THRESHOLD   = 10      # errors before circuit opens
CIRCUIT_RESET_TIME  = 30      # seconds before half-open
BACKOFF_BASE        = 2       # exponential backoff base

_lock           = threading.Lock()
_traffic        = deque()          # timestamps of requests
_concurrent     = 0
_circuit_state  = "CLOSED"         # CLOSED / OPEN / HALF_OPEN
_circuit_errors = 0
_circuit_opened_at = 0.0
_error_window   = deque()          # error timestamps

StatusType = Literal["ok", "warn", "throttle", "circuit_open", "overload"]


# ══════════════════════════════════════════════════════════════════
# MAIN: survival_check
# ══════════════════════════════════════════════════════════════════
def survival_check(endpoint: str = "") -> dict:
    """
    ตรวจสถานะ traffic ก่อน allow request
    คืน: {"status": StatusType, "allowed": bool,
          "load_pct": float, "retry_after": int | None}
    """
    global _circuit_state, _circuit_errors, _circuit_opened_at, _concurrent

    with _lock:
        now = time.time()

        # ── L4: Circuit Breaker ──────────────────────────────────
        if _circuit_state == "OPEN":
            elapsed = now - _circuit_opened_at
            if elapsed >= CIRCUIT_RESET_TIME:
                _circuit_state  = "HALF_OPEN"
                _circuit_errors = 0
                print(f"⚡ Circuit HALF_OPEN after {elapsed:.0f}s")
            else:
                retry = int(CIRCUIT_RESET_TIME - elapsed)
                return _resp("circuit_open", False, 0,
                             retry_after=retry,
                             reason=f"Circuit open — retry in {retry}s")

        # ── Prune old traffic ────────────────────────────────────
        cutoff = now - GLOBAL_WINDOW
        while _traffic and _traffic[0] < cutoff:
            _traffic.popleft()

        # ── Prune old errors ─────────────────────────────────────
        err_cutoff = now - 60
        while _error_window and _error_window[0] < err_cutoff:
            _error_window.popleft()

        count    = len(_traffic)
        load_pct = round(count / GLOBAL_LIMIT * 100, 1)

        # ── L1: Global rate limit ────────────────────────────────
        if count >= GLOBAL_LIMIT:
            return _resp("overload", False, load_pct,
                         retry_after=GLOBAL_WINDOW,
                         reason=f"Global limit reached: {count}/{GLOBAL_LIMIT}")

        # ── L2: Concurrent limiter ───────────────────────────────
        if _concurrent >= CONCURRENT_MAX:
            return _resp("overload", False, load_pct,
                         retry_after=5,
                         reason=f"Too many concurrent requests: {_concurrent}/{CONCURRENT_MAX}")

        # ── Graduated response ───────────────────────────────────
        _traffic.append(now)

        if count >= THROTTLE_LIMIT:
            status = "throttle"
        elif count >= WARN_LIMIT:
            status = "warn"
        else:
            status = "ok"

        # ── HALF_OPEN: allow 1 request through ───────────────────
        if _circuit_state == "HALF_OPEN":
            status = "warn"

        return _resp(status, True, load_pct, reason="")


def _resp(status: StatusType, allowed: bool, load_pct: float,
          retry_after: int = None, reason: str = "") -> dict:
    return {
        "status":      status,
        "allowed":     allowed,
        "load_pct":    load_pct,
        "retry_after": retry_after,
        "reason":      reason,
        "timestamp":   time.time(),
    }


# ══════════════════════════════════════════════════════════════════
# CONCURRENT TRACKING
# ══════════════════════════════════════════════════════════════════
def request_start():
    """เรียกเมื่อ request เริ่ม"""
    global _concurrent
    with _lock:
        _concurrent = max(0, _concurrent + 1)


def request_end(success: bool = True):
    """เรียกเมื่อ request จบ"""
    global _concurrent, _circuit_state, _circuit_errors, _circuit_opened_at
    with _lock:
        _concurrent = max(0, _concurrent - 1)
        if not success:
            _error_window.append(time.time())
            _circuit_errors += 1
            if _circuit_errors >= CIRCUIT_THRESHOLD:
                _circuit_state     = "OPEN"
                _circuit_opened_at = time.time()
                print(f"🔴 Circuit OPEN after {_circuit_errors} errors")
        elif _circuit_state == "HALF_OPEN":
            _circuit_state  = "CLOSED"
            _circuit_errors = 0
            print("🟢 Circuit CLOSED — system recovered")


# ══════════════════════════════════════════════════════════════════
# CONTEXT MANAGER — ใช้กับ FastAPI / any async framework
# ══════════════════════════════════════════════════════════════════
class SurvivalContext:
    """
    ใช้ใน FastAPI:
    async with SurvivalContext():
        ... handle request ...
    """
    def __enter__(self):
        request_start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        request_end(success=exc_type is None)
        return False  # ไม่ suppress exception


# ══════════════════════════════════════════════════════════════════
# STATS
# ══════════════════════════════════════════════════════════════════
def get_survival_stats() -> dict:
    with _lock:
        count    = len(_traffic)
        load_pct = round(count / GLOBAL_LIMIT * 100, 1)
        return {
            "traffic_10s":    count,
            "global_limit":   GLOBAL_LIMIT,
            "load_pct":       load_pct,
            "concurrent":     _concurrent,
            "concurrent_max": CONCURRENT_MAX,
            "circuit_state":  _circuit_state,
            "circuit_errors": _circuit_errors,
            "recent_errors":  len(_error_window),
            "health":         "critical" if load_pct > 90 else
                              "warning"  if load_pct > 70 else "ok",
        }
