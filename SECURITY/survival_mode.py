"""
SECURITY/survival_mode.py — KING DIADEM
ตัววัดโหลดของเซิร์ฟเวอร์ (อ่านอย่างเดียว · ไม่บล็อกใคร)

ย้ายกลับจาก legacy/ แล้วต่อเข้าระบบเป็น ASGI middleware รอบเส้นทางที่ทำงานหนัก (/run /simulate /analyze-image)
และแสดงผลที่ /health → "load"

รุ่นเดิมเป็น circuit breaker ที่ "ปฏิเสธทุกคำขอ 30 วินาที" เมื่อ error ถี่ — รวมถึงข้อความของคนที่กำลังวิกฤต
ซึ่งขัดกับหลัก "ไม่บล็อกคำตอบโดยไม่จำเป็น" (และ /run มีทางสำรองของตัวเองอยู่แล้ว: AI ล้ม → คำตอบจากสมการ)
รุ่นนี้จึงเหลือแค่การวัด เพื่อให้เจ้าของระบบเห็นตัวเลขจริงก่อนตัดสินใจว่าต้องมีการจำกัดทั้งระบบหรือไม่:
  · จำนวนคำขอใน 10 / 60 วินาที · กำลังทำงานพร้อมกันกี่คำขอ (และสูงสุดเท่าไร)
  · error 5xx ใน 60 วินาที · เวลาตอบ p50 / p95 ของ 200 คำขอล่าสุด
ไม่เก็บ IP ไม่เก็บข้อความ ไม่เก็บตัวตน — มีแค่เวลาและสถานะของคำขอ
ตัวนับอยู่ในหน่วยความจำของ process เดียว (deploy ใช้ gunicorn 1 worker)
"""

import threading
import time
from collections import deque

WATCHED = ("/run", "/decision", "/simulate", "/analyze-image")

_lock = threading.Lock()
_started = deque(maxlen=5000)      # เวลาเริ่มของคำขอ (ตัดที่ 60 วิ)
_errors = deque(maxlen=1000)       # เวลาที่ตอบ 5xx/ล้ม (ตัดที่ 60 วิ)
_latency = deque(maxlen=200)       # วินาที ของคำขอที่จบแล้ว
_concurrent = 0
_peak = 0
_total = 0


def _prune(q: deque, now: float, window: float) -> None:
    while q and q[0] < now - window:
        q.popleft()


def request_start() -> float:
    global _concurrent, _peak, _total
    now = time.time()
    with _lock:
        _started.append(now)
        _concurrent += 1
        _peak = max(_peak, _concurrent)
        _total += 1
    return now


def request_end(t0: float, success: bool = True) -> None:
    """เรียกคู่กับ request_start เสมอ (ใน finally) — ตัวนับพร้อมกันจะไม่ค้าง"""
    global _concurrent
    now = time.time()
    with _lock:
        _concurrent = max(0, _concurrent - 1)
        _latency.append(max(0.0, now - t0))
        if not success:
            _errors.append(now)


def _pct(sorted_vals: list, p: float):
    if not sorted_vals:
        return None
    k = min(len(sorted_vals) - 1, max(0, int(round(p * (len(sorted_vals) - 1)))))
    return round(sorted_vals[k], 3)


def get_survival_stats() -> dict:
    now = time.time()
    with _lock:
        _prune(_started, now, 60)
        _prune(_errors, now, 60)
        last10 = sum(1 for t in _started if t >= now - 10)
        lat = sorted(_latency)
        stats = {
            "requests_10s": last10,
            "requests_60s": len(_started),
            "concurrent": _concurrent,
            "concurrent_peak": _peak,
            "errors_60s": len(_errors),
            "latency_p50_s": _pct(lat, .5),
            "latency_p95_s": _pct(lat, .95),
            "total_since_start": _total,
            "watched": list(WATCHED),
            "mode": "observe_only",            # ไม่ปฏิเสธคำขอใดๆ
        }
    errs = stats["errors_60s"]
    stats["health"] = "degraded" if errs >= 10 else "warning" if errs >= 3 else "ok"
    return stats


def reset_for_tests() -> None:
    global _concurrent, _peak, _total
    with _lock:
        _started.clear(); _errors.clear(); _latency.clear()
        _concurrent = _peak = _total = 0


class LoadMonitorMiddleware:
    """ASGI middleware แบบบาง: นับเฉพาะเส้นทางใน WATCHED · ส่งต่อทุกคำขอเสมอ ไม่แตะ body"""

    def __init__(self, app, paths=WATCHED):
        self.app = app
        self.paths = tuple(paths)

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http" or scope.get("path") not in self.paths:
            await self.app(scope, receive, send)
            return
        status = {"code": 500}

        async def _send(message):
            if message.get("type") == "http.response.start":
                status["code"] = int(message.get("status", 500))
            await send(message)

        t0 = request_start()
        ok = False
        try:
            await self.app(scope, receive, _send)
            ok = status["code"] < 500
        finally:
            request_end(t0, success=ok)
