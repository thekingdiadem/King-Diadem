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
- ตัวเลขเงินที่ผู้ใช้พิมพ์เอง (อ่านเฉพาะที่บอก ไม่เดา):
    สถานการณ์: เงินเก็บ S · รายได้ต่อเดือน I · รายจ่ายต่อเดือน E
    แต่ละทาง:  เงินก้อนที่ต้องใช้ C · รายได้/รายจ่ายที่เปลี่ยนต่อเดือน N ("ลาออก" = เงินเดือนหาย ถ้ารู้ I)
    เงินสำรองที่เปลี่ยน (เดือน) = (−C + N·t) ÷ E   → W ±4 ต่อ 1 เดือนของเงินสำรอง (−30…+15)
    รู้ S ด้วย → เงินที่เหลือ = S − C + (I − E + N)·t  ติดลบเมื่อไหร่ = เงินหมด (W −15 ตั้งแต่เดือนนั้น)
"""
from __future__ import annotations

import math
import re

MONTHS = 12
FLOOR = 30          # ต่ำกว่านี้ = เสี่ยงล้ม (waterline ของระบบ)
MAX_PATHS = 3       # สีที่แยกกันได้แม้ตาบอดสี — เกินนี้แสดงเป็นตาราง


# ── ตัวเลขเงิน ─────────────────────────────────────────────────────────
_SAVINGS = r"เงินเก็บ|เงินออม|เงินสำรอง|มีเงิน(?:อยู่)?(?!เดือน)"
_INCOME = r"เงินเดือน(?!ลด)|รายได้(?!หาย|ลด|เสริม)|ได้เดือนละ"
_EXPENSE = r"รายจ่าย|ค่าใช้จ่าย(?!เพิ่ม)|ใช้จ่าย|ใช้เดือนละ"
_COST = r"ลงทุน|ใช้เงิน|ใช้ทุน|เงินทุน|ค่าเรียน|ค่าคอร์ส|ค่าตกแต่ง|ค่าอุปกรณ์|มัดจำ|ซื้อ"
_GAIN = r"รายได้เสริม|ได้เพิ่ม|กำไร(?:เดือนละ)?|เพิ่มเดือนละ|ขึ้นเงินเดือน"
_LOSS = r"รายได้หาย(?:ไป)?|ขาดรายได้|เงินเดือนลด(?:ลง)?|รายได้ลด(?:ลง)?|ค่าเช่า|ผ่อน|จ่ายเพิ่ม|ค่าใช้จ่ายเพิ่ม"
_QUIT = re.compile(r"ลาออก|ออกจากงาน")


def _amt(text: str, words: str):
    from core.engine_bridge import _after
    v = _after(text, words)
    return v if v and v >= 100 else None


def _baht(v: float) -> str:
    return f"{v:,.0f}"


def basis(text: str) -> dict:
    return {"savings": _amt(text, _SAVINGS), "income": _amt(text, _INCOME), "expense": _amt(text, _EXPENSE)}


def path_money(path: str, base: dict) -> dict | None:
    cost = _amt(path, _COST) or 0.0
    monthly, notes = 0.0, []
    if cost:
        notes.append(f"ใช้เงินก้อน {_baht(cost)}")
    level = _amt(path, _INCOME)
    if level is not None and base.get("income"):
        monthly += level - base["income"]
        notes.append(f"รายได้ใหม่ {_baht(level)}/เดือน")
    elif _QUIT.search(path) and base.get("income"):
        monthly -= base["income"]
        notes.append(f"เงินเดือนหาย {_baht(base['income'])}/เดือน (ลาออก)")
    gain, loss = _amt(path, _GAIN), _amt(path, _LOSS)
    if gain:
        monthly += gain; notes.append(f"ได้เพิ่ม {_baht(gain)}/เดือน")
    if loss:
        monthly -= loss; notes.append(f"จ่าย/หายไป {_baht(loss)}/เดือน")
    if not cost and not monthly:
        return None
    return {"cost": cost, "monthly": monthly, "notes": notes}


def _money_adj(m: dict | None, base: dict) -> tuple[list, int | None]:
    """W ที่เปลี่ยนเพราะเงิน ในแต่ละเดือน + เดือนที่เงินหมด (ถ้ารู้เงินเก็บ)"""
    zero = [0.0] * (MONTHS + 1)
    ref = base.get("expense") or base.get("income")
    if not m or not ref:
        return zero, None
    S, I, E = base.get("savings"), base.get("income"), base.get("expense")
    net = (I - E) if (I and E) else 0.0
    adj, runs_out = [0.0], None
    for t in range(1, MONTHS + 1):
        a = max(-30.0, min(15.0, 4.0 * (-m["cost"] + m["monthly"] * t) / ref))
        if S is not None and S - m["cost"] + (net + m["monthly"]) * t < 0:
            runs_out = t if runs_out is None else runs_out
            a -= 15.0
        adj.append(a)
    if S is not None and S - m["cost"] < 0:
        runs_out = 1
    return adj, runs_out


def _curve(w0: float, score: float, reversible: bool, adj: list | None = None) -> list:
    target = w0 + (score - 50) * 0.4                    # จุดที่ไปถึง (ตามคะแนนของทาง)
    dip = 4.0 if reversible else 12.0                   # ช่วงเปลี่ยนผ่าน: ลดลงสุดราวเดือนที่ 1–2
    out = []
    for t in range(MONTHS + 1):
        rise = (target - w0) * (1 - math.exp(-t / 4))
        trough = dip * (t / 1.5) * math.exp(1 - t / 1.5)
        out.append(max(0.0, min(100.0, w0 + rise - trough + (adj[t] if adj else 0.0))))
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
    base = basis(text)
    money = {r["action"]: path_money(r["action"], base) for r in ranked}
    # ทางที่สมการให้ผลเท่ากัน (ย้อนกลับได้ · คะแนน · ตัวเลขเงินเท่ากัน) รวมเป็นเส้นเดียว — ไม่วาดทับกันจนดูเหมือนหาย
    groups = []
    for r in ranked:
        m = money[r["action"]]
        key = (bool(r.get("reversible", True)), round(float(r.get("score", 50)), 1),
               (m["cost"], m["monthly"]) if m else None)
        g = next((g for g in groups if g["key"] == key), None)
        if g:
            g["items"].append(r)
        else:
            groups.append({"key": key, "items": [r], "money": m})
    for g in groups:
        rev, score, _ = g["key"]
        adj, runs_out = _money_adj(g["money"], base)
        g["runs_out"] = runs_out
        g["mid"] = _curve(w0, score, rev, adj)
    # เรียงจากรอดที่สุด: ทางที่ค่ากลางไม่ลงต่ำกว่าเส้นอันตรายก่อน แล้วดูปลายทาง
    groups.sort(key=lambda g: (min(g["mid"]) >= FLOOR, g["mid"][-1], min(g["mid"])), reverse=True)
    out = []
    for g in groups[:MAX_PATHS]:
        rev, score, _ = g["key"]
        mid = g["mid"]
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
            "money": ({"notes": g["money"]["notes"], "runs_out_month": g["runs_out"]} if g["money"] else None),
        })
    has_money = any(g["money"] for g in groups)
    hint = None
    if has_money and not (base["expense"] or base["income"]):
        hint = "บอกรายได้หรือรายจ่ายต่อเดือนในสถานการณ์ด้วย ระบบจะเอาตัวเลขเงินของแต่ละทางมาคิดในภาพได้"
    elif not has_money:
        hint = "ใส่ตัวเลขในแต่ละทางได้ เช่น \"ลงทุน 200,000\" \"รายได้หายเดือนละ 15,000\" และบอกเงินเก็บ/รายจ่ายในสถานการณ์ ภาพจะแยกกันชัดขึ้น"
    return {
        "months": MONTHS, "floor": FLOOR, "w0": round(w0), "paths": out,
        "money_basis": {k: v for k, v in base.items() if v is not None}, "money_hint": hint,
        "hidden": [r["action"] for g in groups[MAX_PATHS:] for r in g["items"]],
        "method": "choice_optimizer + montecarlo (deterministic)",
    }
