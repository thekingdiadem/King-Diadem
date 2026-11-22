"""
core/secret_audit.py — บันทึกหลักฐานทุกครั้งที่ระบบซ่อนข้อมูลลับก่อนส่งให้ AI (Deterministic Secret Audit Log)

ใช้ออกรายงานให้ลูกค้า/ผู้ตรวจว่า "ระบบไม่เคยส่งข้อมูลลับของผู้ใช้ไปให้ผู้ให้บริการ AI" พร้อมหลักฐานที่ตรวจย้อนได้

เก็บ (ต่อการส่งหนึ่งข้อความที่มีการซ่อน):
  เวลา · ผู้ให้บริการ + โดเมนปลายทาง · ชนิดและจำนวนที่ซ่อน (email / password / long_number)
  sha256 ของข้อความ "หลังซ่อนแล้ว" (ตรงกับสิ่งที่ส่งออกไปจริง — ใช้ยืนยันกับ log ของผู้ให้บริการได้)
  โซ่ hash: แต่ละแถวมี prev = h ของแถวก่อน และ h = sha256(prev + เนื้อแถว) — แก้/ลบแถวกลางทางจะเห็นทันที

ไม่เก็บ: ค่าจริงของข้อมูลลับ · hash ของค่าจริง (OTP 6 หลักมีแค่ 1 ล้านแบบ ไล่ hash ย้อนได้ในไม่กี่วินาที)
         · ข้อความก่อนซ่อน · อีเมลหรือตัวตนของผู้ใช้

เขียนลงฐานข้อมูลแบบรวมเป็นชุดในเธรดแยก — ไม่ทำให้การตอบผู้ใช้ช้าลง · พลาดแล้วงานหลักไม่ล้ม
"""
from __future__ import annotations

import hashlib
import json
import queue
import threading
import time

GENESIS = "0" * 64
KINDS = ("email", "password", "long_number")
KEEP_DAYS = 400                                    # เกิน 1 ปีเล็กน้อย — พอสำหรับรอบตรวจประจำปี
_q: "queue.Queue[dict]" = queue.Queue(maxsize=10000)
_writer_lock = threading.Lock()
_writer: threading.Thread | None = None


def _provider() -> tuple[str, str]:
    try:
        from core.llm_provider_policy import status
        st = status()
        return st.get("provider", ""), st.get("host", "")
    except Exception:
        return "", ""


def note(counts: dict, scrubbed_text: str) -> None:
    """เรียกจาก llm_gemini._msg ทุกครั้งที่ซ่อนอะไรได้ — ใส่คิวแล้วกลับทันที"""
    counts = {k: int(v) for k, v in (counts or {}).items() if k in KINDS and v}
    if not counts:
        return
    provider, host = _provider()
    ev = {"ts": round(time.time(), 3), "provider": provider, "host": host, "kinds": counts,
          "text_sha": hashlib.sha256((scrubbed_text or "").encode("utf-8")).hexdigest()}
    try:
        _q.put_nowait(ev)
    except queue.Full:                              # ล้นจริงๆ = ฐานข้อมูลค้างนาน — ทิ้งเหตุการณ์ดีกว่าทำให้แชทช้า
        print("⚠ secret_audit: queue full")
        return
    _ensure_writer()


def _ensure_writer() -> None:
    global _writer
    with _writer_lock:
        if _writer is None or not _writer.is_alive():
            _writer = threading.Thread(target=_loop, name="secret-audit", daemon=True)
            _writer.start()


def _loop() -> None:
    while True:
        batch = [_q.get()]
        time.sleep(2)                               # รวมเหตุการณ์ 2 วินาทีเป็นชุดเดียว (Turso ผ่าน HTTPS)
        while not _q.empty() and len(batch) < 500:
            batch.append(_q.get_nowait())
        try:
            _write(batch)
        except Exception as e:
            print(f"⚠ secret_audit write: {type(e).__name__}")


def flush(timeout: float = 5.0) -> None:
    """เขียนที่ค้างในคิวให้หมด (รายงาน/เทสต์เรียกก่อนอ่าน)"""
    batch = []
    while not _q.empty():
        batch.append(_q.get_nowait())
    if batch:
        _write(batch)


def _conn():
    from DATABASE.db import get_conn
    return get_conn()


def _ensure(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS secret_audit (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            ts       REAL NOT NULL,
            provider TEXT NOT NULL DEFAULT '',
            host     TEXT NOT NULL DEFAULT '',
            kinds    TEXT NOT NULL,
            text_sha TEXT NOT NULL,
            prev     TEXT NOT NULL,
            h        TEXT NOT NULL
        )
    """)
    conn.commit()


def _body(ev: dict) -> str:
    return json.dumps({k: ev[k] for k in ("ts", "provider", "host", "kinds", "text_sha")}, sort_keys=True, ensure_ascii=False)


def _digest(prev: str, ev: dict) -> str:
    return hashlib.sha256((prev + _body(ev)).encode("utf-8")).hexdigest()


_chain_lock = threading.Lock()


def _write(batch: list) -> None:
    with _chain_lock:
        conn = _conn()
        try:
            _ensure(conn)
            row = conn.execute("SELECT h FROM secret_audit ORDER BY id DESC LIMIT 1").fetchone()
            prev = row[0] if row else GENESIS
            for ev in batch:
                h = _digest(prev, ev)
                conn.execute("INSERT INTO secret_audit (ts, provider, host, kinds, text_sha, prev, h) VALUES (?,?,?,?,?,?,?)",
                             (ev["ts"], ev["provider"], ev["host"], json.dumps(ev["kinds"], sort_keys=True), ev["text_sha"], prev, h))
                prev = h
            conn.commit()
        finally:
            conn.close()


def _rows(since: float = 0.0) -> list:
    conn = _conn()
    try:
        _ensure(conn)
        return conn.execute("SELECT id, ts, provider, host, kinds, text_sha, prev, h FROM secret_audit WHERE ts >= ? ORDER BY id",
                            (since,)).fetchall()
    finally:
        conn.close()


def verify() -> dict:
    """ตรวจโซ่ทั้งตาราง — {ok, rows, broken_at}"""
    conn = _conn()
    try:
        _ensure(conn)
        rows = conn.execute("SELECT id, ts, provider, host, kinds, text_sha, prev, h FROM secret_audit ORDER BY id").fetchall()
    finally:
        conn.close()
    prev = rows[0][6] if rows else GENESIS            # แถวแรกหลังลบตามรอบเก็บ = ต้นโซ่ใหม่
    for r in rows:
        ev = {"ts": r[1], "provider": r[2], "host": r[3], "kinds": json.loads(r[4]), "text_sha": r[5]}
        if r[6] != prev or _digest(prev, ev) != r[7]:
            return {"ok": False, "rows": len(rows), "broken_at": r[0]}
        prev = r[7]
    return {"ok": True, "rows": len(rows), "broken_at": None}


def report(days: int = 30) -> dict:
    """สรุปสำหรับลูกค้า/ผู้ตรวจ: ซ่อนอะไรไปกี่ครั้ง ส่งไปผู้ให้บริการไหน โซ่สมบูรณ์ไหม"""
    flush()
    days = max(1, min(int(days or 30), KEEP_DAYS))
    since = time.time() - days * 86400
    rows = _rows(since)
    total = {k: 0 for k in KINDS}
    by_day, hosts = {}, {}
    for r in rows:
        kinds = json.loads(r[4])
        day = time.strftime("%Y-%m-%d", time.gmtime(r[1]))
        d = by_day.setdefault(day, {k: 0 for k in KINDS} | {"messages": 0})
        d["messages"] += 1
        for k, v in kinds.items():
            total[k] = total.get(k, 0) + v
            d[k] = d.get(k, 0) + v
        hosts[r[3] or "?"] = hosts.get(r[3] or "?", 0) + 1
    try:
        from core.llm_provider_policy import status
        prov = status()
    except Exception:
        prov = {}
    return {"days": days, "messages_with_secrets": len(rows), "masked": total, "by_day": by_day, "hosts": hosts,
            "chain": verify(), "provider": prov,
            "stored": "ชนิดและจำนวนที่ซ่อน · sha256 ของข้อความหลังซ่อน · เวลา · ปลายทาง",
            "never_stored": "ค่าจริงของข้อมูลลับ · hash ของค่าจริง · ข้อความก่อนซ่อน · ตัวตนผู้ใช้"}


def export_csv(days: int = 30) -> str:
    import csv
    import io
    flush()
    since = time.time() - max(1, min(int(days or 30), KEEP_DAYS)) * 86400
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "time_utc", "provider", "host", "email", "password", "long_number", "text_sha256", "prev_hash", "hash"])
    for r in _rows(since):
        k = json.loads(r[4])
        w.writerow([r[0], time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(r[1])), r[2], r[3],
                    k.get("email", 0), k.get("password", 0), k.get("long_number", 0), r[5], r[6], r[7]])
    return "﻿" + buf.getvalue()


def prune(now: float | None = None) -> int:
    cut = (now or time.time()) - KEEP_DAYS * 86400
    with _chain_lock:
        conn = _conn()
        try:
            _ensure(conn)
            n = conn.execute("DELETE FROM secret_audit WHERE ts < ?", (cut,)).rowcount
            conn.commit()
        finally:
            conn.close()
    return n
