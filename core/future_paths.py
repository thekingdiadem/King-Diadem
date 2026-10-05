"""
core/future_paths.py — ภาพจำลองอนาคตของแต่ละทางเลือก (12 เดือน)

ใช้ของที่มีอยู่แล้ว ไม่ให้ AI เดา:
- core/kernel_voice.assess           W ตอนนี้ (ความมั่นคง 0–100)
- ENGINE/choice_optimizer            คะแนนของแต่ละทาง · ย้อนกลับได้ไหม
- SIMULATIONS/montecarlo_engine      ช่วงที่เป็นไปได้ (p10–p90) ในแต่ละเดือน — เดิมไม่มีใครเรียก

สมมติฐาน (บอกผู้ใช้ตรงๆ ว่าเป็นภาพจากสมการ ไม่ใช่คำทำนาย):
- ทุกทางมีช่วงเปลี่ยนผ่านที่ W ลดลงก่อน — ทางที่ย้อนกลับไม่ได้ลดลึกกว่า (ถอยไม่ได้)
- จุดที่ไปถึงใน 12 เดือนขึ้นกับคะแนนของทาง
- ความไม่แน่นอนกว้างขึ้นตามเวลา — ทางที่ย้อนกลับไม่ได้กว้างกว่า (ทั้งขึ้นและลง)
"""
from __future__ import annotations

import math

MONTHS = 12
FLOOR = 30          # ต่ำกว่านี้ = เสี่ยงล้ม (waterline ของระบบ)
MAX_PATHS = 3       # สีที่แยกกันได้แม้ตาบอดสี — เกินนี้แสดงเป็นตาราง


def _curve(w0: float, score: float, reversible: bool) -> list:
    target = w0 + (score - 50) * 0.4                    # จุดที่ไปถึง (ตามคะแนนของทาง)
    dip = 4.0 if reversible else 12.0                   # ช่วงเปลี่ยนผ่าน: ลดลงสุดราวเดือนที่ 1–2
    out = []
    for t in range(MONTHS + 1):
        rise = (target - w0) * (1 - math.exp(-t / 4))
        trough = dip * (t / 1.5) * math.exp(1 - t / 1.5)
        out.append(max(0.0, min(100.0, w0 + rise - trough)))
    return out


def project(text: str, paths: list) -> dict | None:
    paths = [str(p).strip()[:120] for p in (paths if isinstance(paths, list) else []) if str(p).strip()][:7]
    if not paths:
        return None
    try:
        from core.kernel_voice import assess
        from core.engine_bridge import rank_options
        from SIMULATIONS.montecarlo_engine import run_montecarlo
    except Exception as e:  # pragma: no cover
        print(f"⚠ future_paths: {type(e).__name__}")
        return None
    w0 = float(assess(text)["W"])
    ranked = rank_options(paths, waterline=w0)
    letter = {p: chr(65 + i) for i, p in enumerate(paths)}           # A/B/C ตามที่ผู้ใช้พิมพ์
    # ทางที่สมการให้ผลเท่ากัน (ย้อนกลับได้เหมือนกัน คะแนนเท่ากัน) รวมเป็นเส้นเดียว — ไม่วาดเส้นทับกันจนดูเหมือนหาย
    groups = []
    for r in ranked:
        key = (bool(r.get("reversible", True)), round(float(r.get("score", 50)), 1))
        g = next((g for g in groups if g["key"] == key), None)
        if g:
            g["items"].append(r)
        else:
            groups.append({"key": key, "items": [r]})
    out = []
    for g in groups[:MAX_PATHS]:
        rev, score = g["key"]
        mid = _curve(w0, score, rev)
        lo, hi = [], []
        for t, m in enumerate(mid):
            if t == 0:                                      # วันนี้รู้ค่าแน่นอน
                lo.append(round(m, 1)); hi.append(round(m, 1))
                continue
            vol = (0.04 if rev else 0.10) * math.sqrt(t)
            mc = run_montecarlo(m / 100, runs=200, volatility=vol)
            lo.append(round(max(0.0, min(100.0, mc["percentiles"]["p10"] * 100)), 1))
            hi.append(round(max(0.0, min(100.0, mc["percentiles"]["p90"] * 100)), 1))
        below = next((t for t, v in enumerate(lo) if v < FLOOR), None)
        out.append({
            "label": " · ".join(sorted(letter.get(r["action"], "?") for r in g["items"])),
            "action": " / ".join(r["action"] for r in g["items"]), "reversible": rev,
            "same": len(g["items"]) > 1,
            "mid": [round(v, 1) for v in mid], "lo": lo, "hi": hi,
            "end": round(mid[-1]), "worst": round(min(lo)), "below_floor_month": below,
        })
    return {
        "months": MONTHS, "floor": FLOOR, "w0": round(w0), "paths": out,
        "hidden": [r["action"] for g in groups[MAX_PATHS:] for r in g["items"]],
        "method": "choice_optimizer + montecarlo (deterministic)",
    }
