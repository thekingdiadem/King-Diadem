# ENGINE/consensus_engine.py — KING DIADEM
# FIX: ลบ circular import decision_engine ออก ใช้ inline logic แทน

def _f(v, d):
    try:
        return float(v)
    except (TypeError, ValueError):
        return d

def _decision_intelligence(human_state: dict, risk_proxy: dict) -> dict:
    level = str(risk_proxy.get("level", "MEDIUM")).upper()
    score = _f(risk_proxy.get("risk_score"), 0.0)
    res   = _f(human_state.get("resource"), 50.0)
    stab  = _f(human_state.get("stability"), 60.0)
    if level == "CRITICAL" or score >= 85 or res <= 10:
        return {"action": "stabilize",        "message": "ชะลอการตัดสินใจใหญ่ — ดูแลพื้นฐานก่อน"}
    if level == "HIGH"     or score >= 60 or stab < 35:
        return {"action": "stabilize",        "message": "แยกปัญหาเป็นขั้นเล็กๆ แล้วทำทีละขั้น"}
    if res < 30:
        return {"action": "recover_resource", "message": "ทรัพยากรต่ำ — เลือกสิ่งจำเป็นก่อน"}
    if stab < 45:
        return {"action": "expand_choices",   "message": "หาทางเลือกเสริม 2–3 แบบก่อนตัดสินใจ"}
    return     {"action": "maintain",         "message": "ไปต่อได้ — รักษาจังหวะพอประมาณ"}

def _route_to_risk(route: str) -> str:
    return {"collapse":"CRITICAL","survival":"HIGH","risk":"HIGH","civil":"MEDIUM","vega":"MEDIUM"}.get(route,"LOW")

def build_consensus(payload: dict) -> dict:
    payload     = payload if isinstance(payload, dict) else {}
    human_state = payload.get("human_state") or {}
    route       = payload.get("route", "general")
    risk_proxy  = {"level": _route_to_risk(route), "risk_score": _f(human_state.get("risk_score"), 0.0)}
    di = _decision_intelligence(human_state, risk_proxy)
    try:
        from ENGINE.council_engine import council_engine
        council_result = council_engine(di, human_state)
    except Exception:
        council_result = {"decision": di, "votes": [], "score": 50}
    final = consensus_engine(council_result, human_state)
    return {"consensus": final["final_action"], "message": final["message"],
            "confidence": final["confidence"], "action": final["final_action"],
            "voters": final["voters"], "tally": final["tally"]}

def resolve(pattern: dict) -> dict:
    pattern = pattern if isinstance(pattern, dict) else {}
    return {"route": "uncertain", "resolution": "defer_commit",
            "notes": "ยังไม่ควรฟันธง — รวบรวมข้อมูลอีกนิด",
            "entropy": pattern.get("entropy"), "resource": pattern.get("resource"),
            "stability": pattern.get("stability")}

def consensus_engine(council_result: dict, state: dict = None) -> dict:
    council_result = council_result if isinstance(council_result, dict) else {}
    decision = council_result.get("decision", {})
    votes    = council_result.get("votes", [])
    tally = {}
    for vote in votes:
        action = vote.get("action", decision.get("action", "maintain"))
        tally[action] = tally.get(action, 0) + _f(vote.get("score"), 0.0)
    final_action = max(tally, key=tally.get) if tally else decision.get("action", "maintain")
    confidence   = round(min(100.0, max(0.0, _f(council_result.get("score"), 50.0))), 2)
    return {"final_action": final_action, "message": decision.get("message", ""),
            "confidence": confidence, "tally": tally, "voters": len(votes)}
