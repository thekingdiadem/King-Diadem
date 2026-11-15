"""
SECURITY/shield.py — โล่แบบแบน "เงื่อนไข" ไม่ใช่แบน "คำ"

เจ้าของโปรเจกต์: "แพลตฟอร์มส่วนมากแบนคำ แต่ไม่แบนเงื่อนไข คนโกงเลยลอยนวล · แฮกเกอร์หาได้นับล้านรูปแบบในเสี้ยววิ
เราไม่ต้องสร้างรูปแบบมากกว่าเพื่อชนะ แต่ทำให้รูปแบบแฮ็กไม่ได้แต่แรก · บังคับให้ฝั่งนั้นต้องสร้างรูปแบบไม่จำกัดแทนเรา
ทำให้รูปแบบกับการไม่มีรูปแบบเป็นของเดียวกัน · ต่อให้คอมแรงระดับแสง มาที่นี่ก็ช้าเหมือนเต่าคลาน"

ทำยังไง:
1. รู้จักตัวเอง ไม่ไล่จดศัตรู (positive model) — เราจดแค่ "รูปร่างของเรา": เส้นทางที่มีจริงและ method ที่รับจริง
   (อ่านจากแอปเองตอนเปิด ไม่ต้องดูแลรายการมือ) สิ่งที่อยู่นอกรูปร่างนี้ จะเป็นช่องโหว่แบบที่ 1 หรือแบบที่ 1,000,000
   ก็ตกถังเดียวกัน — เราไม่ต้องรู้จักมันเลย
2. ไม่มีสัญญาณให้เรียนรู้ — สิ่งที่อยู่นอกรูปร่างได้คำตอบหน้าตาเดียวกันทุกครั้ง (404 ข้อความเดียว ไม่บอกว่าเพราะอะไร)
   ยิงล้านแบบก็ได้คำตอบเดียวกันล้านครั้ง ไม่มีอะไรบอกว่า "ใกล้แล้ว" (ทางเข้าจริงของผู้ใช้ไม่ถูกแตะ)
3. แบนเงื่อนไข ไม่แบนคำ — นับ "พฤติกรรม" ไม่ใช่เนื้อหา: เคาะประตูที่ไม่มีอยู่จริง · รหัสผ่าน/สิทธิ์ผิดซ้ำ · ส่งข้อมูลรูปร่างผิด
   · ใช้ method ผิด · คนจริงแทบไม่ทำแบบนี้ติดกันหลายครั้ง แต่เครื่องสแกนต้องทำ (มันไม่มีทางอื่นจะหาช่อง)
   คะแนนจางลงเองตามเวลา (ครึ่งชีวิต 10 นาที) — ไม่มีใครถูกตราหน้าถาวร
4. เต่าคลาน (tarpit) — เกินเกณฑ์แล้ว ทุกคำขอจาก IP นั้นถูกหน่วงแบบทวีคูณ (สูงสุด 15 วิ) และทำได้ทีละคำขอ
   ยิงขนานไม่ได้ · คอมเร็วแค่ไหนก็ได้แค่ไม่กี่คำขอต่อนาที · ฝั่งเราไม่เปลืองแรง (asyncio.sleep ไม่กิน CPU/thread)
   ถ้าถูกหน่วงพร้อมกันเกิน 200 คำขอ ตอบ 429 ทันที (ไม่ให้การหน่วงกลายเป็นช่องให้ถล่มเรา)

ความเมตตาที่ตั้งใจใส่ไว้ (คนจริงต้องไม่เดือดร้อน):
- ไม่บล็อกถาวร ไม่ตัดใครออก — แค่ช้าลง · คนไทยหลายคนใช้ IP มือถือร่วมกัน (CGNAT) ห้ามให้คนหนึ่งทำอีกคนเข้าไม่ได้
- ทางแชท (/run ฯลฯ) ไม่ถูกหน่วงเลย — คนในวิกฤตต้องได้เบอร์ทันที เส้นนี้มี rate limit ของตัวเองอยู่แล้ว
- คำขอที่สำเร็จ (2xx) ลดคะแนนลง — คนจริงใช้เว็บจริง สแกนเนอร์ไม่ค่อยได้ 2xx
- ไฟล์ static ที่ไม่มี (ลิงก์เก่า) นับเบามาก

ข้อจำกัดที่ต้องบอกตรงๆ: ไม่มีระบบไหน "แฮ็กไม่ได้" 100% — โล่นี้ทำให้การหาช่อง "แพงและมืด" มาก
แต่ช่องที่อยู่ในรูปร่างของเราเอง (บั๊กในเส้นทางที่มีจริง) ยังต้องปิดด้วยเทสต์และการตรวจโค้ดเหมือนเดิม
"""
from __future__ import annotations

import asyncio
import json
import math
import re
import time
from collections import OrderedDict

HALF_LIFE_S = 600.0
THRESHOLD = 8.0
MAX_DELAY_S = 15.0
MAX_TRAPPED = 200
MAX_IPS = 20000
NO_DELAY = ("/run", "/decision", "/simulate", "/health", "/api/crisis")
WEIGHT = {404: 1.0, 405: 1.0, 401: 2.0, 403: 2.0, 400: 0.5, 413: 1.0, 422: 0.5}
_UNIFORM = json.dumps({"detail": "Not Found"}, separators=(",", ":")).encode()   # ตรงกับ 404 ของแอปทุกไบต์ — แยกไม่ออกว่าเจอโล่หรือเจอแอป


class _Ledger:
    def __init__(self):
        self.d: "OrderedDict[str, list]" = OrderedDict()   # ip → [score, t, busy]

    def get(self, ip: str, now: float) -> list:
        e = self.d.get(ip)
        if e is None:
            e = self.d[ip] = [0.0, now, 0]
            while len(self.d) > MAX_IPS:
                self.d.popitem(last=False)
        else:
            e[0] *= math.pow(.5, (now - e[1]) / HALF_LIFE_S)
            e[1] = now
            self.d.move_to_end(ip)
        return e


def delay_for(score: float) -> float:
    if score < THRESHOLD:
        return 0.0
    return min(MAX_DELAY_S, 0.5 * 2 ** ((score - THRESHOLD) / 2))


def shape_of(app) -> list:
    """รูปร่างของเรา: (regex เส้นทาง, methods) อ่านจากแอปเอง"""
    out = []
    for r in getattr(app, "routes", []):
        rx = getattr(r, "path_regex", None)
        if rx is None:
            continue
        ms = getattr(r, "methods", None)
        out.append((rx, set(ms) if ms else None))
    return out


class ShieldMiddleware:
    def __init__(self, app, ip_of=None, shape_from=None, clock=time.monotonic, sleep=asyncio.sleep):
        self.app, self.ip_of, self.shape_from = app, ip_of, shape_from
        self.clock, self.sleep = clock, sleep
        self.book, self.trapped, self._shape = _Ledger(), 0, None

    def _known(self, path: str, method: str) -> bool:
        if path.startswith("/static/"):
            return True                        # ไฟล์ static: StaticFiles ตัดสินเอง (ลิงก์เก่านับเบา)
        if self._shape is None and self.shape_from is not None:
            self._shape = shape_of(self.shape_from())
        # เส้นทางที่มีจริงแต่ method ผิด ปล่อยให้แอปตอบ 405 ตามมาตรฐาน (นับคะแนนตอนตอบกลับ)
        return any(rx.match(path) for rx, _ in self._shape or ())

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            return await self.app(scope, receive, send)
        try:
            ip = self.ip_of(scope) if self.ip_of else (scope.get("client") or ("?",))[0]
        except Exception:  # noqa: BLE001
            ip = "?"
        path, method = scope.get("path", ""), scope.get("method", "GET")
        e = self.book.get(ip, self.clock())

        wait = 0.0 if path.startswith(NO_DELAY) else delay_for(e[0])
        if wait:
            if self.trapped >= MAX_TRAPPED or e[2] >= 1:
                e[0] += .5
                return await _plain(send, 429, b'{"detail":"Too Many Requests"}')
            self.trapped += 1
            e[2] += 1
            try:
                await self.sleep(wait)
            finally:
                self.trapped -= 1
                e[2] -= 1

        if self._shape is not None or self.shape_from is not None:
            if not self._known(path, method):
                e[0] += WEIGHT[404]
                accept = dict(scope.get("headers") or ()).get(b"accept", b"")
                if not (method == "GET" and b"text/html" in accept):
                    return await _plain(send, 404, _UNIFORM)  # นอกรูปร่าง = คำตอบเดียวกันเสมอ
                # คนเปิดลิงก์ผิดด้วยเบราว์เซอร์ ยังได้หน้า 404 สวยๆ ตามเดิม (แต่นับคะแนนเหมือนกัน)

        code = {"c": 500}

        async def _send(m):
            if m.get("type") == "http.response.start":
                code["c"] = int(m.get("status", 500))
            await send(m)

        await self.app(scope, receive, _send)
        c = code["c"]
        if 200 <= c < 300:
            e[0] = max(0.0, e[0] - .5)
        else:
            w = WEIGHT.get(c, 0.0)
            e[0] += w * (.25 if path.startswith("/static/") else 1)

    def stats(self) -> dict:
        now = self.clock()
        slow = sum(1 for ip in list(self.book.d) if delay_for(self.book.get(ip, now)[0]) > 0)
        return {"watched_ips": len(self.book.d), "slowed_ips": slow, "trapped_now": self.trapped}


async def _plain(send, status: int, body: bytes):
    await send({"type": "http.response.start", "status": status,
                "headers": [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode())]})
    await send({"type": "http.response.body", "body": body})
