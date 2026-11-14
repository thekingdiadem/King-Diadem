"""
core/self_heal.py — ระบบดูแลตัวเองเมื่อไม่มีใครเฝ้า

เจ้าของโปรเจกต์: "อยากให้ไฟล์ซ่อมแซมตัวเองได้แม้ตอนพี่คิงไม่รู้ตัว · เอาให้สุดๆ"

บทเรียนจาก Microsoft ล่มทั่วโลก (12–13 พ.ย. 2569): ต้นเหตุคือการเปลี่ยนค่าตั้งเซิร์ฟเวอร์หลังอัปเดต
ที่ถูกใช้ทั้งระบบพร้อมกันโดยไม่มีใครตรวจ — ระบบที่ "แก้ตัวเองอัตโนมัติ" แบบเขียนโค้ดใหม่เอง คือความเสี่ยงแบบเดียวกัน
ไฟล์นี้จึงซ่อมแบบที่ไม่สร้างความเสียหายใหม่:

1. แยกส่วน (bulkhead): ความรู้แต่ละชุด (ค่าเลือด ยาตีกัน พันธุกรรมสัตว์ ฯลฯ) ถูกเรียกผ่าน guard()
   ส่วนไหนพัง → ปิดเฉพาะส่วนนั้น ผู้ใช้ยังได้คำตอบจากส่วนอื่น ไม่ใช่ error 500
2. ตัดวงจรแล้วลองใหม่เอง (circuit breaker): พังครบ 3 ครั้งใน 10 นาที → พักส่วนนั้น 5 นาที แล้วลองเปิดใหม่เอง
   ถ้าครั้งแรกหลังเปิดใหม่ยังพัง ก็พักต่อ · ถ้าผ่าน ก็กลับมาทำงานปกติ — ไม่ต้องมีคนกด
3. ตรวจตัวเองเป็นรอบ (self-check): ทุก 10 นาที (ตั้งได้ด้วย SELF_HEAL_INTERVAL_S) รันข้อความทดสอบของแต่ละส่วน
   และข้อความวิกฤต 7 ภาษา (core/last_resort.canary) — พังเมื่อไรจะเห็นที่ /health และใน log ทันที
4. ไม่แตะไฟล์และไม่เขียนโค้ดใหม่เอง: การแก้โค้ดจริงต้องผ่านเทสต์และคนอนุมัติเสมอ (CI: .github/workflows/self-check.yml)

ไม่ import โมดูลความรู้ใดๆ ตอนโหลด — ถ้าโมดูลไหนพังตั้งแต่ import ไฟล์นี้ยังทำงานได้
"""
from __future__ import annotations

import importlib
import os
import threading
import time

FAIL_LIMIT = 3                 # พังกี่ครั้งในหน้าต่างเวลาแล้วตัดวงจร
WINDOW_S = 600
COOLDOWN_S = 300               # พักนานเท่าไรก่อนลองเปิดใหม่

_lock = threading.Lock()
_state: dict[str, dict] = {}   # name → {"fails": [ts...], "open_until": ts, "last_error": str, "trips": n, "calls": n}


def _s(name: str) -> dict:
    return _state.setdefault(name, {"fails": [], "open_until": 0.0, "last_error": "", "trips": 0, "calls": 0, "ok_since": time.time()})


def enabled(name: str) -> bool:
    """ส่วนนี้เปิดใช้อยู่ไหม — ถ้าครบเวลาพักแล้ว เปิดให้ลองใหม่เอง (half-open)"""
    with _lock:
        return time.time() >= _s(name)["open_until"]


def record_ok(name: str) -> None:
    with _lock:
        s = _s(name)
        s["calls"] += 1
        if s["fails"] and s["open_until"] and time.time() >= s["open_until"]:
            s["fails"], s["open_until"], s["ok_since"] = [], 0.0, time.time()      # ลองใหม่ผ่าน = หายแล้ว


def trip(name: str, err: BaseException | str) -> None:
    """บันทึกว่าพัง · ครบเกณฑ์ = ตัดวงจร"""
    now = time.time()
    with _lock:
        s = _s(name)
        s["calls"] += 1
        s["fails"] = [t for t in s["fails"] if now - t < WINDOW_S] + [now]
        s["last_error"] = (type(err).__name__ + ": " + str(err))[:200] if not isinstance(err, str) else err[:200]
        half_open_retry = s["open_until"] and now >= s["open_until"]
        if len(s["fails"]) >= FAIL_LIMIT or half_open_retry:
            s["open_until"] = now + COOLDOWN_S
            s["trips"] += 1
    print(f"⚠ self_heal: {name} พัง ({s['last_error']}) — " + ("พัก 5 นาทีแล้วจะลองใหม่เอง" if s["open_until"] > now else "ยังใช้ต่อ"))


def guard(name: str, fn, *args, **kw):
    """เรียก fn อย่างปลอดภัย — พังหรือถูกพักอยู่ คืน None (ผู้เรียกใช้ทางอื่นต่อ)"""
    if not enabled(name):
        return None
    try:
        out = fn(*args, **kw)
    except Exception as e:  # noqa: BLE001 — จุดประสงค์คือกันทุกอย่าง
        trip(name, e)
        return None
    record_ok(name)
    return out


# ── ข้อความทดสอบของแต่ละส่วน (ต้องได้คำตอบที่มีคำนี้) ─────────────────────────
_PROBES = {
    "lab_values": ("core.lab_values", "reply", ("ผลตรวจ LDL 190",), "LDL"),
    "drug_pairs": ("core.drug_pairs", "reply", ("กินวาร์ฟารินกับไอบูโพรเฟนได้ไหม",), "วาร์ฟาริน"),
    "bio_axiom": ("WORLD_MODEL.bio_axiom", "reply", ("หมามีโครโมโซมกี่แท่ง",), "78"),
    "object_goal": ("core.object_goal", "reply", ("จะเอารถไปล้างที่ร้านห่างไป 100 เมตร ควรเดินหรือขับ",), "รถ"),
    "human_needs": ("core.human_needs", "acknowledge", ("ทำงานหนักแต่ไม่มีใครเห็น",), "เห็น"),
    "problem_lens": ("core.problem_lens", "find", ("แม่ป่วยติดเตียง ต้องลาออกมาดูแล", "th"), None),
}
_last_check: dict = {"at": None, "ok": None, "failed": [], "canary": None}


def check_all() -> dict:
    """รันข้อความทดสอบทุกส่วน · ส่วนที่พังถูกพัก ส่วนที่หายแล้วถูกเปิดคืนเอง"""
    failed = []
    for name, (mod, fn, args, must) in _PROBES.items():
        try:
            out = getattr(importlib.import_module(mod), fn)(*args)
            if must is not None and (not out or must not in str(out)):
                raise AssertionError(f"คำตอบทดสอบไม่มี '{must}'")
            with _lock:
                s = _s(name)
                if s["open_until"]:
                    s["fails"], s["open_until"], s["ok_since"] = [], 0.0, time.time()   # หายแล้ว เปิดคืน
        except Exception as e:  # noqa: BLE001
            failed.append(name)
            with _lock:
                s = _s(name)
                s["last_error"] = (type(e).__name__ + ": " + str(e))[:200]
                s["open_until"] = time.time() + COOLDOWN_S
                s["trips"] += 1
    try:
        from core.last_resort import canary
        can = canary()
    except Exception as e:  # noqa: BLE001
        can = {"ok": False, "failed": ["canary:" + type(e).__name__]}
    if not can.get("ok"):
        failed.append("crisis_canary")
    _last_check.update(at=time.strftime("%Y-%m-%d %H:%M:%S"), ok=not failed, failed=failed, canary=can)
    if failed:
        print(f"⚠⚠ self_heal: ส่วนที่พัง {failed} — พักไว้และจะลองใหม่เองในรอบถัดไป")
    return dict(_last_check)


def status() -> dict:
    """สำหรับ /health"""
    now = time.time()
    with _lock:
        parts = {k: {"enabled": now >= v["open_until"], "trips": v["trips"], "calls": v["calls"],
                     "last_error": v["last_error"] or None,
                     "retry_in_s": max(0, round(v["open_until"] - now)) if v["open_until"] > now else 0}
                 for k, v in _state.items()}
    return {"last_check": dict(_last_check), "parts": parts}


_started = False


def start_background(interval_s: float | None = None) -> bool:
    """ตรวจตัวเองเป็นรอบใน thread เบื้องหลัง (daemon) — เรียกครั้งเดียวตอนเปิดเซิร์ฟเวอร์"""
    global _started
    if _started or os.getenv("SELF_HEAL_OFF") == "1":
        return False
    _started = True
    every = float(interval_s or os.getenv("SELF_HEAL_INTERVAL_S", "600"))

    def _loop():
        while True:
            time.sleep(every)
            try:
                check_all()
            except Exception as e:  # noqa: BLE001 — ตัวตรวจเองต้องไม่ทำให้เซิร์ฟเวอร์ล้ม
                print(f"⚠ self_heal loop: {type(e).__name__}: {e}")

    threading.Thread(target=_loop, name="self-heal", daemon=True).start()
    return True


def reset() -> None:
    """สำหรับเทสต์"""
    with _lock:
        _state.clear()
