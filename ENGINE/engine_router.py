# ============================================================
# ENGINE/engine_router.py — v2
# ศูนย์กลางเชื่อม engine ทั้งหมด
# ตรรกะ: paticcasamuppada -> risk -> consensus -> simulation -> escape -> response
# ห้ามขัดกัน — แต่ละ engine ต่างหน้าที่
#
# v2 — wire ENGINE/escape_routes.py เข้า route collapse/survival/risk
#       normalize risk_score (0-100) -> scale 0-10 ที่ escape_routes คาด
# ============================================================

from __future__ import annotations
import traceback

# ── Safe import helpers ───────────────────────────────────
def _try_import(module_path: str, fn_name: str):
    try:
        import importlib
        mod = importlib.import_module(module_path)
        return getattr(mod, fn_name, None)
    except Exception:
        return None


# ── Load engines ──────────────────────────────────────────
_paticca_analyze   = _try_import("ENGINE.paticcasamuppada_engine", "analyze")
_risk_assess       = _try_import("ENGINE.risk_engine",             "assess")
_consensus_resolve = _try_import("ENGINE.consensus_engine",        "resolve")
_consensus_engine  = _try_import("ENGINE.consensus_engine",        "consensus_engine")
_decision_intel    = _try_import("ENGINE.consensus_engine",        "_decision_intelligence")
# เดิม import "consensus_engine.run_simulation" และ "council_engine.run" ซึ่งไม่มีอยู่จริง
# → สภาไม่เคยประชุม (consensus = maintain ทุกครั้ง) และการจำลองเป็นค่าคงที่เสมอ
# simulation_engine.simulate() เรียก LLM อีกรอบ จึงไม่ต่อในเส้นทางของ /run (คง 1 LLM/ข้อความ)
_simulate_future   = None
_council_run       = _try_import("ENGINE.council_engine",          "council_engine")
_strategy_plan     = _try_import("ENGINE.strategy_planner",        "plan")
_survival_advise   = _try_import("ENGINE.survival_advisor",        "advise")
_situation_analyze = _try_import("ENGINE.situation_analyzer",      "analyze_situation")   # เดิมชื่อ "analyze" (ไม่มี)
_escape_routes     = _try_import("ENGINE.escape_routes",           "generate_escape_routes")


# ── Fallbacks ─────────────────────────────────────────────
def _fallback_paticca(pattern: dict) -> dict:
    return {
        "root_cause":   "ignorance",
        "feeling_tone": "unpleasant",
        "intensity":    1.0,
        "nirvana_mode": False,
        "uap":          {"should_pause": False, "audit_note": "fallback"},
        "kill_zone":    {"outcome": "chain_full", "craving_risk": 0.5},
        "summary":      "paticca fallback",
    }

def _fallback_risk(pattern: dict) -> dict:
    return {
        "risk_score": 50.0,
        "level":      "MEDIUM",
        "decision_level": "MEDIUM",
        "remaining_choices": 3,
        "stability":  float(pattern.get("stability", 60)),
        "resource":   float(pattern.get("resource",  70)),
        "entropy":    float(pattern.get("entropy",   40)),
        "drift":      float(pattern.get("drift",      0)),
    }

def _fallback_simulation(state: dict) -> list:
    # แม่แบบคงที่ ไม่ได้คำนวณจาก input — ติดป้าย source ไว้ ไม่ให้ใครเข้าใจว่าเป็นการจำลองจริง
    return [
        {"future": "stable",        "risk": 2, "action": "maintain",         "source": "static_template"},
        {"future": "resource_drop", "risk": 5, "action": "secure_resources", "source": "static_template"},
        {"future": "high_risk",     "risk": 8, "action": "escape",           "source": "static_template"},
    ]


# ── ENGINE PIPELINE ────────────────────────────────────────
def route(pattern: dict) -> dict:
    """
    Main pipeline:
    1. paticcasamuppada — หาต้นเหตุ, เวทนา, kill zone
    2. risk_engine       — ประเมิน risk score
    3. situation_analyzer — วิเคราะห์สถานการณ์ (optional)
    4. council / consensus — ลงมติ
    5. simulation        — จำลองอนาคต
    6. strategy_planner  — วางแผน
    7. survival_advisor  — คำแนะนำเร่งด่วน
    8. escape_routes     — เส้นทางหนี (collapse/survival/risk)
    """
    # เดิมเก็บ pattern ทั้งก้อน (รวม prompt ภายใน) ไว้ใน result["input"] แล้วส่งกลับหน้าเว็บ
    result: dict = {}

    # ── STEP 1: Paticcasamuppada ────────────────────────
    try:
        paticca = (_paticca_analyze or _fallback_paticca)(pattern)
    except Exception:
        paticca = _fallback_paticca(pattern)
    result["paticca"] = paticca

    # ถ้า UAP บอกให้หยุด → ไม่ push ต่อ ส่งกลับทันที
    if paticca.get("uap", {}).get("should_pause") and \
       paticca.get("kill_zone", {}).get("outcome") == "chain_cut":
        result["route"]   = "pause"
        result["message"] = paticca.get("uap", {}).get("audit_note", "หยุดก่อน")
        result["action"]  = "wait_observe"
        return result

    # ── STEP 2: Risk Engine ─────────────────────────────
    try:
        risk = (_risk_assess or _fallback_risk)(pattern)
    except Exception:
        risk = _fallback_risk(pattern)
    result["risk"] = risk

    risk_level     = risk.get("level", "MEDIUM")
    decision_level = risk.get("decision_level", "MEDIUM")

    # ── STEP 3: Situation Analyzer (เฉพาะเมื่อมีข้อมูลจริงครบ ไม่เดาตัวเลขแทน) ──
    if _situation_analyze and "food_score" in pattern:
        try:
            result["situation"] = _situation_analyze(
                food_score=float(pattern.get("food_score")),
                risk_score=float(risk.get("risk_score", 50)),
                money=float(pattern.get("money_score", 50)),
                energy=float(pattern.get("energy", 50)),
                shelter=pattern.get("safe_place", True) is not False,
            )
        except Exception:
            pass

    # ── STEP 4: Council / Consensus ─────────────────────
    council_result = {"decision": {"action": "maintain", "message": ""}, "votes": [], "score": 50}

    if _council_run and _decision_intel:
        try:
            decision = _decision_intel(pattern, risk)
            council_result = _council_run(decision, pattern) or council_result
        except Exception:
            pass

    if _consensus_engine:
        try:
            consensus = _consensus_engine(council_result, pattern)
        except Exception:
            consensus = {"final_action": "maintain", "confidence": 50, "message": ""}
    else:
        consensus = {"final_action": "maintain", "confidence": 50, "message": ""}

    result["consensus"] = consensus

    # ── กำหนด route จาก risk + paticca ────────────────
    nirvana    = paticca.get("nirvana_mode", False)
    craving_risk = paticca.get("kill_zone", {}).get("craving_risk", 0.5)

    if risk_level == "CRITICAL":
        route_name = "collapse"
    elif risk_level == "HIGH" or craving_risk > 0.75:
        route_name = "risk"
    elif nirvana or craving_risk < 0.35:
        route_name = "stable"
    elif decision_level == "MEDIUM":
        route_name = "uncertain"
    else:
        route_name = "general"

    result["route"] = route_name

    # ── STEP 5: Simulation ──────────────────────────────
    try:
        simulations = (_simulate_future or _fallback_simulation)(pattern)
    except Exception:
        simulations = _fallback_simulation(pattern)
    result["simulations"] = simulations

    # ── STEP 6: Strategy ────────────────────────────────
    if _strategy_plan:
        try:
            result["strategy"] = _strategy_plan({
                **pattern,
                "route":    route_name,
                "risk":     risk,
                "paticca":  paticca,
                "consensus": consensus,
            })
        except Exception:
            pass

    # ── STEP 7: Survival Advisor ────────────────────────
    if _survival_advise:
        try:
            result["survival"] = _survival_advise({
                **pattern,
                "risk_level": risk_level,
                "route":      route_name,
            })
        except Exception:
            pass

    # ── STEP 8: Escape Routes (collapse/survival/risk) ──
    # generate_escape_routes(location, risk) คาด risk เป็น scale 0-10
    # แต่ risk_score ในระบบนี้เป็น scale 0-100 → normalize หาร 10
    if route_name in ("collapse", "survival", "risk") and _escape_routes:
        try:
            risk_score_100 = float(risk.get("risk_score", 50))
            risk_score_10  = max(0.0, min(10.0, risk_score_100 / 10.0))
            location = pattern.get("location") or pattern.get("input", "")
            result["escape_routes"] = _escape_routes(location, risk_score_10)
        except Exception:
            pass

    # ── STEP 9: Uncertain route → defer ─────────────────
    if route_name == "uncertain" and _consensus_resolve:
        try:
            result["defer"] = _consensus_resolve(pattern)
        except Exception:
            pass

    # ── Final message assembly ───────────────────────────
    result["action"]  = consensus.get("final_action", "maintain")
    result["message"] = _build_message(result)

    return result


# ── Build message ──────────────────────────────────────────
def _build_message(r: dict) -> str:
    route    = r.get("route", "general")
    paticca  = r.get("paticca", {})
    risk     = r.get("risk", {})
    uap      = paticca.get("uap", {})
    summary  = paticca.get("summary", "")
    consensus = r.get("consensus", {})

    lines = []

    # UAP note ถ้ามี
    if uap.get("audit_note"):
        lines.append(f"[UAP] {uap['audit_note']}")

    # Paticca summary
    if summary:
        lines.append(f"[สาเหตุ] {summary}")

    # Risk
    try:
        rs = float(risk.get("risk_score", 50))
    except (TypeError, ValueError):
        rs = 50.0
    rl = risk.get("level", "MEDIUM")
    lines.append(f"[ความเสี่ยง] {rl} ({rs:.0f}/100)")

    # Route action
    route_msg = {
        "collapse":  "⚠️ สถานการณ์วิกฤต — ต้องดำเนินการทันที",
        "risk":      "🔴 ความเสี่ยงสูง — ระวังและเตรียมทางออก",
        "uncertain": "🟡 ยังไม่ชัดเจน — รวบรวมข้อมูลเพิ่ม",
        "stable":    "🟢 สถานะสงบ — สามารถดำเนินการได้",
        "general":   "🔵 ดำเนินต่อด้วยความระมัดระวัง",
        "pause":     "⏸ หยุดสังเกต — วงจรตัดที่เวทนา",
    }.get(route, "")

    if route_msg:
        lines.append(route_msg)

    # Escape routes (ถ้ามี)
    escapes = r.get("escape_routes")
    if escapes:
        names = ", ".join(e.get("route", "") for e in escapes if isinstance(e, dict))
        if names:
            lines.append(f"[ทางหนี] {names}")

    # Confidence
    try:
        conf = float(consensus.get("confidence", 50))
    except (TypeError, ValueError):
        conf = 50.0
    lines.append(f"[ความมั่นใจ] {conf:.0f}%")

    return "\n".join(lines)


# ── Public API ─────────────────────────────────────────────
def run(pattern: dict) -> dict:
    """Entry point หลัก — DecisionEngine เรียกที่นี่"""
    try:
        return route(pattern)
    except Exception as e:
        # traceback เดิมถูกส่งกลับไปถึงหน้าเว็บผ่าน /run — log ฝั่ง server เท่านั้น
        print(f"⚠ engine_router error: {e}\n{traceback.format_exc()}")
        return {
            "route":   "error",
            "action":  "maintain",
            "message": "engine_router error",
        }
