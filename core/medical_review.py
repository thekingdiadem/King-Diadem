"""
core/medical_review.py — โต๊ะแพทย์ตรวจ: รวมข้อความทางการแพทย์ทุกข้อไว้ที่เดียว ให้แพทย์กด "ถูกต้อง/ต้องแก้"

ที่มา: ROADMAP ข้อ 2 — ข้อความสุขภาพทั้งหมด (แผนดูแลไต ค่าเลือด ยาตีกัน) เขียนโดยผู้ช่วยเขียนโค้ด
ยังไม่มีแพทย์ตรวจ ทั้งที่คนอ่านแล้วอาจทำตามจริง

หลัก:
- ข้อความแต่ละข้อมี hash ของเนื้อความ — แพทย์อนุมัติ "ข้อความนี้" ไม่ใช่ "ช่องนี้"
  แก้ข้อความทีหลังเมื่อไร สถานะกลับเป็น "เปลี่ยนแล้ว รอตรวจใหม่" เอง (กันข้อความใหม่แอบใช้ผลอนุมัติเก่า)
- ดึงข้อความจากโค้ดจริงตอนเรียก ไม่คัดลอกไว้ (ไม่มีทางที่รายการตรวจกับของจริงไม่ตรงกัน)
- บันทึกทุกครั้งที่ตรวจ (ไม่เขียนทับ) — ย้อนดูได้ว่าใครตรวจข้อไหนเมื่อไร ว่าอย่างไร
"""
from __future__ import annotations

import ast
import hashlib
import inspect
import re
import threading
import time

VERDICTS = ("approved", "needs_fix")
SOURCES = {"chronic": "แผนดูแลไต เบาหวาน ความดัน ไขมัน", "lab": "อ่านค่าเลือด", "drug": "ยาตีกัน"}
MAX_NOTE = 1000
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_lock = threading.Lock()


def _h(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


# ── รวบรวมข้อความจากโค้ดจริง ─────────────────────────────────────────────────

_NOT_MEDICAL = {"title", "lang_fallback"}         # หัวเรื่อง · แจ้งว่ายังไม่มีภาษานั้น — ไม่ใช่เนื้อหาทางการแพทย์


def _chronic() -> list[dict]:
    from core import chronic_care as cc
    out = []
    for key, row in cc.T.items():
        if key in _NOT_MEDICAL:
            continue
        for lang, text in row.items():
            out.append({"id": f"chronic:{key}:{lang}", "source": "chronic", "topic": key, "lang": lang, "text": text})
    return out


def _drug() -> list[dict]:
    from core import drug_pairs as dp
    out = []
    for a, b, level, th, en in dp._PAIRS:
        topic = "+".join(sorted(a)) + " × " + "+".join(sorted(b))
        base = f"drug:{topic}:{level}"
        out.append({"id": base + ":th", "source": "drug", "topic": f"{topic} ({level})", "lang": "th", "text": th})
        out.append({"id": base + ":en", "source": "drug", "topic": f"{topic} ({level})", "lang": "en", "text": en})
    return out


def _lab() -> list[dict]:
    """ข้อความแปลผลค่าเลือดอยู่ในคำสั่ง return ของ lab_values._grade — อ่านจากโค้ดด้วย ast (ไม่ต้องย้ายข้อความออกมา)"""
    from core import lab_values as lv
    tree = ast.parse(inspect.getsource(lv._grade))
    out, key = [], "?"
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare) and isinstance(node.test.left, ast.Name) \
                and node.test.left.id == "k" and node.test.comparators and isinstance(node.test.comparators[0], ast.Constant):
            key = node.test.comparators[0].value
            for sub in ast.walk(node):
                if isinstance(sub, ast.Return) and isinstance(sub.value, ast.Tuple) and len(sub.value.elts) == 3 \
                        and all(isinstance(e, ast.Constant) and isinstance(e.value, str) for e in sub.value.elts):
                    level, th, en = (e.value for e in sub.value.elts)
                    if level == "ok":
                        continue                      # "ปกติ" ไม่ใช่คำแนะนำทางการแพทย์
                    tag = f"lab:{key}:{level}:{_h(th)[:6]}"
                    out.append({"id": tag + ":th", "source": "lab", "topic": f"{key} ({level})", "lang": "th", "text": th})
                    out.append({"id": tag + ":en", "source": "lab", "topic": f"{key} ({level})", "lang": "en", "text": en})
    seen, uniq = set(), []
    for it in out:
        if it["id"] not in seen:
            seen.add(it["id"])
            uniq.append(it)
    return uniq


def items() -> list[dict]:
    out = []
    for fn in (_chronic, _lab, _drug):
        try:
            out += fn()
        except Exception as e:                        # แหล่งหนึ่งพังต้องไม่ทำให้ทั้งหน้าใช้ไม่ได้
            print(f"⚠ medical_review {fn.__name__}: {type(e).__name__}")
    for it in out:
        it["hash"] = _h(it["text"])
    return out


# ── ผลการตรวจ ────────────────────────────────────────────────────────────────

def _conn():
    from DATABASE.db import get_conn
    return get_conn()


def _ensure(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS medical_reviews (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            ts        REAL NOT NULL,
            item_id   TEXT NOT NULL,
            text_hash TEXT NOT NULL,
            verdict   TEXT NOT NULL,
            note      TEXT NOT NULL DEFAULT '',
            reviewer  TEXT NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_medical_reviews_item ON medical_reviews (item_id, id)")
    conn.commit()


def _latest() -> dict:
    conn = _conn()
    try:
        _ensure(conn)
        rows = conn.execute("SELECT item_id, text_hash, verdict, note, reviewer, ts FROM medical_reviews ORDER BY id").fetchall()
    finally:
        conn.close()
    last = {}
    for r in rows:                                    # แถวหลังทับแถวก่อน = ผลล่าสุดของแต่ละข้อ
        last[r[0]] = {"hash": r[1], "verdict": r[2], "note": r[3], "reviewer": r[4], "ts": r[5]}
    return last


def status_of(item: dict, last: dict) -> str:
    r = last.get(item["id"])
    if not r:
        return "pending"
    if r["hash"] != item["hash"]:
        return "changed"                              # ข้อความเปลี่ยนหลังตรวจ → ต้องตรวจใหม่
    return r["verdict"]


def listing(mask_fn=None) -> list[dict]:
    last = _latest()
    out = []
    for it in items():
        r = last.get(it["id"]) or {}
        out.append({**it, "status": status_of(it, last), "note": r.get("note", ""),
                    "reviewer": (mask_fn(r["reviewer"]) if mask_fn and r.get("reviewer") else r.get("reviewer", "")),
                    "reviewed_at": r.get("ts")})
    return out


def review(item_id, verdict, note, reviewer) -> dict:
    verdict = str(verdict or "").strip().lower() if isinstance(verdict, str) else ""
    if verdict not in VERDICTS:
        return {"ok": False, "error": "เลือก ถูกต้อง หรือ ต้องแก้"}
    note = _CTRL.sub("", str(note or ""))[:MAX_NOTE].strip() if isinstance(note, (str, type(None))) else ""
    if verdict == "needs_fix" and not note:
        return {"ok": False, "error": "ถ้าต้องแก้ ช่วยเขียนสั้นๆ ว่าควรแก้อย่างไรด้วยนะคะ"}
    it = next((x for x in items() if x["id"] == item_id), None)
    if not it:
        return {"ok": False, "error": "ไม่พบข้อความนี้ (อาจถูกแก้หรือลบไปแล้ว — โหลดใหม่)"}
    with _lock:
        conn = _conn()
        try:
            _ensure(conn)
            conn.execute("INSERT INTO medical_reviews (ts, item_id, text_hash, verdict, note, reviewer) VALUES (?,?,?,?,?,?)",
                         (time.time(), it["id"], it["hash"], verdict, note, str(reviewer).lower()))
            conn.commit()
        finally:
            conn.close()
    return {"ok": True, "status": verdict}


def summary() -> dict:
    """ตัวเลขรวม — เปิดสาธารณะได้ (ไม่มีชื่อแพทย์หรือหมายเหตุ)"""
    rows = listing()
    out = {"total": len(rows), "approved": 0, "needs_fix": 0, "pending": 0, "changed": 0, "by_source": {}}
    for r in rows:
        out[r["status"]] += 1
        s = out["by_source"].setdefault(r["source"], {"total": 0, "approved": 0})
        s["total"] += 1
        s["approved"] += r["status"] == "approved"
    return out


def export_csv(mask_fn=None) -> str:
    """เก็บเป็นหลักฐานว่าข้อไหนแพทย์ตรวจแล้ว ข้อไหนต้องแก้ — เปิดใน Excel/Google Sheets ได้"""
    import csv
    import io
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "source", "topic", "lang", "status", "text", "note", "reviewer", "reviewed_at"])
    for r in listing(mask_fn):
        when = time.strftime("%Y-%m-%d %H:%M", time.gmtime(r["reviewed_at"])) if r["reviewed_at"] else ""
        w.writerow([r["id"], r["source"], r["topic"], r["lang"], r["status"], r["text"], r["note"], r["reviewer"], when])
    return "﻿" + buf.getvalue()                  # BOM ให้ Excel อ่านภาษาไทยถูก
