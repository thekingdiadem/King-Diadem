"""วัดเวลาตอบของแชท (/run) เป็น p50 / p95 / p99 — จะทำให้ตอบไวขึ้นได้ต้องเห็นตัวเลขก่อน

ที่มา: ความเห็นจากผู้อ่านโพสต์ LinkedIn (CTO ที่ทำระบบแบบเดียวกัน) ว่าเวลาตอบของ LLM ที่แกว่งมาก
ทำลาย "ความนิ่ง" ที่ระบบช่วยคนในวิกฤตต้องมี — ในวิกฤต ตอบช้าก็รู้สึกเหมือนไม่ตอบ
เดิมระบบไม่ได้วัดเวลาตอบเลย รู้แค่ว่าเพดานต่อข้อความคือ 45 วินาที (LLM_CALL_BUDGET_S)

เก็บเฉพาะตัวเลขเวลา 500 ค่าล่าสุดในหน่วยความจำ — ไม่เก็บข้อความ ไม่เก็บว่าใครถาม · รีสตาร์ตแล้วเริ่มนับใหม่
"""
from __future__ import annotations

import threading
from collections import deque

_KEEP = 500
_ms: deque = deque(maxlen=_KEEP)
_lock = threading.Lock()


def record(ms: float) -> None:
    if ms >= 0:
        with _lock:
            _ms.append(float(ms))


def _pct(sorted_ms: list, p: float) -> int:
    """เปอร์เซ็นไทล์แบบ nearest-rank: p99 ของ 100 ค่า = ค่าที่ช้าเป็นอันดับ 2 จากท้าย"""
    k = max(0, min(len(sorted_ms) - 1, int(-(-p * len(sorted_ms) // 100)) - 1))
    return round(sorted_ms[k])


def summary() -> dict:
    with _lock:
        v = sorted(_ms)
    if not v:
        return {"n": 0}
    return {"n": len(v), "p50": _pct(v, 50), "p95": _pct(v, 95), "p99": _pct(v, 99), "max": round(v[-1]),
            "over_10s": sum(1 for x in v if x > 10_000)}


def reset() -> None:
    with _lock:
        _ms.clear()
        _by_model.clear()


# เวลาของการเรียก AI แยกตามรุ่น (เฉพาะครั้งที่ได้คำตอบ) — ใช้เทียบรุ่นใหม่กับรุ่นเดิมด้วยตัวเลขจริง ไม่ใช่ตัวเลขโฆษณา
_by_model: dict = {}


def record_model(model: str, ms: float) -> None:
    if ms >= 0 and model:
        with _lock:
            _by_model.setdefault(str(model)[:60], deque(maxlen=200)).append(float(ms))


def by_model() -> dict:
    with _lock:
        snap = {k: sorted(v) for k, v in _by_model.items() if v}
    return {k: {"n": len(v), "p50": _pct(v, 50), "p95": _pct(v, 95), "p99": _pct(v, 99)} for k, v in snap.items()}


class ReplyTimer:
    """ASGI middleware: จับเวลาเฉพาะ POST /run ตั้งแต่รับคำขอจนส่งคำตอบเสร็จ · ใส่ Server-Timing ให้ดูได้ในเบราว์เซอร์"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http" or scope.get("path") != "/run" or scope.get("method") != "POST":
            return await self.app(scope, receive, send)
        import time
        t0 = time.perf_counter()

        async def _send(msg):
            if msg.get("type") == "http.response.start":
                dur = (time.perf_counter() - t0) * 1000
                msg = dict(msg, headers=list(msg.get("headers") or []) + [(b"server-timing", b"app;dur=%d" % dur)])
                if 200 <= int(msg.get("status", 0)) < 400:
                    record(dur)
            await send(msg)

        await self.app(scope, receive, _send)
