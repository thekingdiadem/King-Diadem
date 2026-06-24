# ENGINE/eternal_runtime.py
"""
KING DIADEM — Eternal Runtime
ลบ while True ออก — มันบล็อก Render worker ทั้งหมด
เก็บ eternal_snapshot() เพื่อให้ API เรียกได้
"""
from __future__ import annotations
import time
from typing import Optional

# ── Safe imports ──────────────────────────────────────────────────
try:
    from core.dependency_cycle import dependent_cycle
    _DC = True
except ImportError:
    _DC = False

try:
    from ENGINE.self_evolution import evolve_system
    _EVO = True
except ImportError:
    _EVO = False

try:
    from core.drift_monitor import detect_drift
    _DRIFT = True
except ImportError:
    _DRIFT = False

try:
    from core.entropy_guard import entropy_guard
    _EG = True
except ImportError:
    _EG = False

try:
    from core.vigilance_protocol import vigilance_check
    _VP = True
except ImportError:
    _VP = False

try:
    from SIMULATIONS.future_simulator import simulate_future
    _SIM = True
except ImportError:
    _SIM = False

try:
    from GLOBAL_NODE.network_sync import sync_state
    _SYNC = True
except ImportError:
    _SYNC = False


# ── Fallbacks ─────────────────────────────────────────────────────
def _dc_fallback(state: dict) -> dict:
    entropy   = float(state.get("entropy",   40))
    stability = float(state.get("stability", 60))
    resource  = float(state.get("resource",  50))
    new_stability = max(0, min(100, stability - entropy*0.08 + resource*0.05))
    new_entropy   = max(0, min(100, entropy + (0 if stability > 60 else 3)))
    return {**state, "stability": round(new_stability,2), "entropy": round(new_entropy,2)}

def _drift_fallback(state: dict) -> dict:
    entropy = float(state.get("entropy", 40))
    return {
        "drift_detected": entropy > 65,
        "entropy":        entropy,
        "level":          "HIGH" if entropy > 65 else "NOMINAL",
    }

def _entropy_guard_fallback(state: dict) -> dict:
    entropy = float(state.get("entropy", 40))
    return {
        "stop_line": entropy > 80,
        "level":     "CRITICAL" if entropy > 80 else "OK",
    }

def _vigilance_fallback() -> dict:
    return {"alerts": [], "safe": True, "source": "fallback"}

def _sim_fallback(state: dict, steps: int) -> dict:
    entropy   = float(state.get("entropy",   40))
    stability = float(state.get("stability", 60))
    futures = []
    for i in range(1, steps+1):
        projected_entropy   = min(100, entropy + i*2)
        projected_stability = max(0,   stability - i*1.5)
        futures.append({
            "step":       i,
            "entropy":    round(projected_entropy,   2),
            "stability":  round(projected_stability, 2),
            "viable":     projected_stability > 20,
        })
    return {"steps": futures, "source": "fallback"}


# ── eternal_runtime — ห้ามเรียกใน production ─────────────────────
def eternal_runtime(system_state: dict):
    """
    ⚠️ ห้ามเรียกใน FastAPI/Render — บล็อก worker ทันที
    ใช้สำหรับ local testing เท่านั้น
    Production ให้ใช้ eternal_snapshot() แทน
    """
    raise RuntimeError(
        "eternal_runtime() ห้ามเรียกใน production — "
        "มัน while True บล็อก Render worker\n"
        "ใช้ eternal_snapshot() แทน หรือ schedule ด้วย APScheduler"
    )


# ── eternal_snapshot — API-safe ───────────────────────────────────
def eternal_snapshot(system_state: Optional[dict] = None) -> dict:
    """
    รันหนึ่ง cycle ของ eternal loop โดยไม่บล็อก
    เรียกจาก /api/kernel_snapshot หรือ background task
    """
    state = dict(system_state or {})
    t0    = time.time()
    errors: dict = {}

    # Step 1 — Dependent cycle
    try:
        state = dependent_cycle(state) if _DC else _dc_fallback(state)
    except Exception as e:
        errors["dependent_cycle"] = str(e)
        state = _dc_fallback(state)

    # Step 2 — Self evolution
    try:
        state = evolve_system(state) if _EVO else state
    except Exception as e:
        errors["evolve"] = str(e)

    # Step 3 — Simulate futures
    future = None
    try:
        future = simulate_future(state, 3) if _SIM else _sim_fallback(state, 3)
    except Exception as e:
        future = _sim_fallback(state, 3)
        errors["simulate"] = str(e)

    # Step 4 — Drift detection
    drift = None
    try:
        drift = detect_drift(state) if _DRIFT else _drift_fallback(state)
    except Exception as e:
        drift = _drift_fallback(state)
        errors["drift"] = str(e)

    # Step 5 — Entropy guard
    guard = None
    try:
        guard = entropy_guard(state) if _EG else _entropy_guard_fallback(state)
    except Exception as e:
        guard = _entropy_guard_fallback(state)
        errors["entropy_guard"] = str(e)

    # Step 6 — Vigilance
    vigilance = None
    try:
        vigilance = vigilance_check() if _VP else _vigilance_fallback()
    except Exception as e:
        vigilance = _vigilance_fallback()
        errors["vigilance"] = str(e)

    # Step 7 — Network sync (optional, fire-and-forget)
    if _SYNC:
        try:
            sync_state(state)
        except Exception as e:
            errors["sync"] = str(e)

    # ── Kernel status ─────────────────────────────────────────────
    stop = (guard or {}).get("stop_line", False)
    drift_flag = (drift or {}).get("drift_detected", False)
    alerts = (vigilance or {}).get("alerts", [])

    kernel_status = (
        "HALTED"  if stop else
        "DRIFT"   if drift_flag else
        "WARNING" if alerts else
        "ACTIVE"
    )

    return {
        "kernel_status":    kernel_status,
        "state_after_cycle":state,
        "future_hint":      future,
        "drift":            drift,
        "entropy_guard":    guard,
        "vigilance":        vigilance,
        "errors":           errors,
        "latency_ms":       round((time.time()-t0)*1000, 1),
        "modules_loaded":   {
            "dependency_cycle": _DC,
            "self_evolution":   _EVO,
            "drift_monitor":    _DRIFT,
            "entropy_guard":    _EG,
            "vigilance":        _VP,
            "future_simulator": _SIM,
            "network_sync":     _SYNC,
        },
        "axiom": "Choice(t) ≥ 1 → collapse = False",
    }
