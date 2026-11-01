# ENGINE/self_learning.py
"""
KING DIADEM — Self Learning Engine
บันทึก + วิเคราะห์ pattern จากคำถามจริง (ทั้งระบบ ไม่ผูกกับคน)
/run → record_async() · แดชบอร์ดเจ้าของ (/api/admin/metrics) → analyze_patterns()
"""
from __future__ import annotations
from math import isfinite as _isfinite
import threading
import time

MAX_RECORDS = 500
_lock = threading.Lock()

# เดิมเก็บใน data/decision_history.json และไม่มีโค้ดไหนเรียก record_decision เลย → วงจรนี้ไม่เคยได้ข้อมูล
# ตอนนี้เก็บในฐานข้อมูลหลัก (Turso บนเว็บจริง — ไม่หายตอน deploy) · ไม่มีอีเมล ไม่มีข้อความ มีแค่ตัวเลขกับเส้นทาง
_DDL = """CREATE TABLE IF NOT EXISTS learning_samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL NOT NULL, route TEXT NOT NULL,
    risk_level TEXT NOT NULL, risk REAL, waterline REAL, entropy REAL, resource REAL)"""


def _conn():
    from DATABASE.db import get_conn
    c = get_conn()
    c.execute(_DDL)
    return c


# ── I/O ───────────────────────────────────────────────────────────
def load_history() -> list:
    """แถวล่าสุด ≤ 500 เรียงเก่า → ใหม่ · ฐานข้อมูลล่ม = [] (ไม่ทำให้แชทล้ม)"""
    try:
        c = _conn()
        try:
            rows = c.execute("SELECT ts, route, risk_level, risk, waterline, entropy, resource FROM learning_samples "
                             "ORDER BY id DESC LIMIT ?", (MAX_RECORDS,)).fetchall()
        finally:
            c.close()
    except Exception:
        return []
    out = []
    for r in reversed(rows):
        out.append({"timestamp": r[0], "strategy": r[1], "risk_level": r[2], "risk": r[3],
                    "waterline": r[4], "entropy": r[5], "resource": r[6],
                    "survival_score": r[4]})
    return out


# ── Record ────────────────────────────────────────────────────────
def _risk_level(r: float) -> str:
    return "CRITICAL" if r >= 85 else "HIGH" if r >= 65 else "MEDIUM" if r >= 35 else "LOW"


def record_decision(result: dict, has_state: bool = False) -> bool:
    """บันทึก 1 แถวต่อคำถาม · waterline/entropy/resource เก็บเฉพาะเมื่อผู้ใช้กรอกสถานะเอง
    (ค่าเริ่มต้นของ backend ไม่ใช่สภาพจริงของใคร — เก็บไปจะทำให้ค่าเฉลี่ยโกหก)"""
    result = result if isinstance(result, dict) else {}

    def _f(v):
        try:
            v = float(v)
            return v if _isfinite(v) else None
        except (TypeError, ValueError):
            return None
    p = result.get("pattern") if isinstance(result.get("pattern"), dict) else {}
    risk = _f(result.get("risk_score")) or 0.0
    wl, en, rs = ((_f(p.get(k)) if has_state else None) for k in ("waterline", "entropy", "resource"))
    try:
        with _lock:
            c = _conn()
            try:
                c.execute("INSERT INTO learning_samples (ts, route, risk_level, risk, waterline, entropy, resource) "
                          "VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (time.time(), str(result.get("route") or "general")[:20], _risk_level(risk), risk, wl, en, rs))
                c.execute("DELETE FROM learning_samples WHERE id <= (SELECT MAX(id) FROM learning_samples) - ?",
                          (MAX_RECORDS * 4,))
                c.commit()
            finally:
                c.close()
        return True
    except Exception:
        return False


def record_async(result: dict, has_state: bool = False) -> None:
    """เขียนนอกเส้นทางตอบ — ผู้ใช้ไม่ต้องรอฐานข้อมูลบนคลาวด์"""
    threading.Thread(target=record_decision, args=(dict(result), has_state), daemon=True).start()


# ── Analyze ───────────────────────────────────────────────────────
def analyze_patterns() -> dict:
    history = load_history()
    n = len(history)

    if n < 3:
        return {
            "status":   "insufficient_data",
            "records":  n,
            "required": 3,
        }

    # ความเสี่ยงมีทุกแถว · waterline/entropy มีเฉพาะคนที่กรอกสถานะเอง (ไม่เอาค่าเริ่มต้นมาเฉลี่ย)
    risks      = [float(h.get("risk") or 0) for h in history]
    waterlines = [h["waterline"] for h in history if h.get("waterline") is not None]
    entropies  = [h["entropy"]   for h in history if h.get("entropy")   is not None]
    scores     = [100.0 - r for r in risks]          # คะแนนรอด = 100 − ความเสี่ยงของคำถาม

    avg_score = sum(scores) / n
    avg_wl    = sum(waterlines) / len(waterlines) if waterlines else None
    avg_ent   = sum(entropies) / len(entropies) if entropies else None

    # Trend — เทียบ 20% แรก vs 20% หลัง
    split = max(1, n // 5)
    early_avg = sum(scores[:split])  / split
    late_avg  = sum(scores[-split:]) / split

    if late_avg > early_avg + 5:
        trend = "improving"
    elif late_avg < early_avg - 5:
        trend = "degrading"
    else:
        trend = "stable"

    # Most common strategy
    from collections import Counter
    strategy_counts = Counter(str(h.get("strategy", "unknown")) for h in history)
    top_strategy    = strategy_counts.most_common(1)[0][0]

    # High-risk ratio
    high_risk = sum(1 for h in history if h.get("risk_level") in ("HIGH","CRITICAL"))
    high_risk_ratio = round(high_risk / n, 3)

    # Drift detection — entropy เพิ่มต่อเนื่อง 5 records
    drift_detected = False
    if len(entropies) >= 5:
        last5_ent = entropies[-5:]
        drift_detected = all(last5_ent[i] < last5_ent[i+1] for i in range(4))

    return {
        "status":           "active",
        "records":          n,
        "avg_survival":     round(avg_score, 2),
        "avg_waterline":    round(avg_wl, 2) if avg_wl is not None else None,
        "avg_entropy":      round(avg_ent, 2) if avg_ent is not None else None,
        "with_state":       len(waterlines),
        "trend":            trend,
        "top_strategy":     top_strategy,
        "high_risk_ratio":  high_risk_ratio,
        "drift_detected":   drift_detected,
        "drift_warning":    "entropy เพิ่มต่อเนื่อง 5 รอบ — ตรวจ waterline ทันที" if drift_detected else None,
        "axiom":            "Fail less. Harm less. Restore more.",
    }


# ── Query helpers ─────────────────────────────────────────────────
def get_recent(n: int = 10) -> list:
    return load_history()[-n:]
