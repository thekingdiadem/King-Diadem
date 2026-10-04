"""
KING DIADEM CORE
Civilization Decision Infrastructure

Architect: Nithikorn Bunsrang

v2.1 — app.py / INTERFACE/api.py เรียก quick_assess / core_status จากโมดูลนี้
แต่เดิมไม่มีฟังก์ชันทั้งสองอยู่จริงที่ไหนเลย (import ชื่อ "king_diadem_core" ล้มทุกครั้ง)
→ ใน production ใช้ตัวสำรองที่คืนค่าว่าง: บริบทเหตุปัจจัย/โยนิโสมนสิการไม่เคยถึง LLM
ตอนนี้ต่อเข้ากับ engine ที่มีจริง (ไม่มี LLM call, ไม่มี side effect)
"""

from __future__ import annotations

CORE_VERSION = "2.1"


def _f(v, d: float) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


# =========================
# NORTH PRINCIPLE
# =========================

def north_principle(actions):
    """
    Filter actions based on KING DIADEM core law
    เดิมใช้ action["harm_life"] → KeyError กับทุก action จาก survival_advisor (ไม่มี key นี้)
    ไม่ระบุ = ไม่ได้ละเมิด
    """
    filtered = []

    for action in actions or []:
        if not isinstance(action, dict):
            continue

        if action.get("harm_life") is True:
            continue

        if action.get("break_ethics") is True:
            continue

        if action.get("reality_violation") is True:
            continue

        filtered.append(action)

    return filtered


# =========================
# CHOICE PRESERVATION
# =========================

def preserve_choice(actions):
    """
    Ensure at least one option always exists
    """
    if len(actions) == 0:

        return [{
            "action": "SYSTEM_PAUSE",
            "reason": "No safe action available. Preserve existence."
        }]

    return actions


# =========================
# DECISION CORE
# =========================

def king_diadem_decision(location, lat, lng, food, money, risk):
    from ENGINE.survival_advisor import survival_advisor
    from ENGINE.world_intel import analyze_location
    from ENGINE.choice_optimizer import optimize_choice

    world = analyze_location(_f(lat, 0.0), _f(lng, 0.0))

    survival = survival_advisor(_f(food, 0.0), _f(money, 0.0), _f(risk, 0.0))

    actions = survival.get("recommended_actions") or []

    actions = north_principle(actions)

    actions = preserve_choice(actions)

    ranked = optimize_choice(actions, {"money": _f(money, 0.0)}) or actions

    best = ranked[0]

    return {
        "system": "KING DIADEM",
        "location": location,
        "zone": world.get("zone"),
        "survival_score": survival.get("survival_score"),
        "north_direction": best.get("action"),
        "alternatives": ranked
    }


# =========================
# QUICK ASSESS — ช่องบริบทก่อน LLM
# =========================

def _structure(pattern: dict) -> float:
    """สุขภาพโครงสร้าง 0–1 จาก E/R/S: ((100−E) + R + S) / 300"""
    e = max(0.0, min(100.0, _f(pattern.get("entropy"), 40)))
    r = max(0.0, min(100.0, _f(pattern.get("resource"), 50)))
    s = max(0.0, min(100.0, _f(pattern.get("stability"), 60)))
    return round(((100.0 - e) + r + s) / 300.0, 3)


def quick_assess(context, pattern=None) -> dict:
    """
    context: ข้อความดิบของผู้ใช้   pattern: human_state {entropy, resource, stability, ...}
    → {peace, causal_ctx, wise_ctx, recommend_route, should_pause,
       bodhi_verdict, drift_alert, bodhi_structure}

    สงบ > ทำลาย: ไม่สงบ = ให้ LLM ชะลอ/ทบทวน; route ยกไป survival เฉพาะเมื่อโครงสร้างต่ำจริง
    """
    text    = str(context or "")
    pattern = pattern if isinstance(pattern, dict) else {}

    structure = _structure(pattern)
    entropy   = _f(pattern.get("entropy"), 40)
    stability = _f(pattern.get("stability"), 60)

    causal_ctx = ""
    should_pause = False
    try:
        from ENGINE.paticcasamuppada_engine import suffering_infrastructure, llm_note
        p = suffering_infrastructure(text, pattern)
        should_pause = bool((p.get("uap") or {}).get("should_pause"))
        causal_ctx = llm_note(p)
    except Exception:
        pass

    wise_ctx = ""
    try:
        from ENGINE.yonisomanasikara_engine import wise_attention
        w = wise_attention(text, pattern)
        biases = [b.get("bias") for b in w.get("bias_detected", [])]
        q = (w.get("questions") or [""])[0]
        # ใส่เฉพาะเมื่อข้อความมีสัญญาณ (bias หรือ mode ที่เลือกจากคำ) — ไม่งั้นทุกข้อความทั่วไป
        # เช่น "วันนี้อากาศดี" จะถูกดันให้ LLM ตอบแบบแก้ปัญหาอริยสัจ
        if biases or w.get("mode") != "ariyasacca":
            wise_ctx = f"[Wise attention: {w.get('mode_name', '')} — {q}"
            if biases:
                wise_ctx += f" | bias: {', '.join(biases)} → {'; '.join(w.get('corrections', []))}"
            wise_ctx += "]"
        should_pause = should_pause or bool(w.get("should_pause"))
    except Exception:
        pass

    drift_alert = entropy > 65 and stability < 40
    peace = not should_pause and structure >= 0.4
    recommend_route = "survival" if structure < 0.35 else None

    if peace:
        verdict = "PEACE — โครงสร้างพอ ดำเนินการได้"
    elif recommend_route:
        verdict = "STABILIZE — โครงสร้างต่ำ ประคองก่อนตัดสินใจใหญ่"
    else:
        verdict = "PAUSE — ทบทวนเหตุก่อนตัดสินใจ"

    return {
        "peace":           peace,
        "causal_ctx":      causal_ctx,
        "wise_ctx":        wise_ctx,
        "recommend_route": recommend_route,
        "should_pause":    should_pause,
        "bodhi_verdict":   verdict,
        "drift_alert":     drift_alert,
        "bodhi_structure": structure,
    }


def core_status() -> dict:
    status = {"core_version": CORE_VERSION}
    for name, mod in (("paticcasamuppada", "ENGINE.paticcasamuppada_engine"),
                      ("yonisomanasikara", "ENGINE.yonisomanasikara_engine")):
        try:
            __import__(mod)
            status[name] = "ok"
        except Exception:
            status[name] = "unavailable"
    return status
