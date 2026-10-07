# ENGINE/council_engine.py — KING DIADEM
# แก้: Altair → Choice (option preservation)

# สมาชิกมาจากสภาเดียวของระบบ (AI/council_engine.COUNCIL_SEATS) — เดิมมี 7 ชื่อของตัวเอง
# (Choice/Vega/Lyla/Titan/DriftZero/FATE/Pratiya) ไม่ตรงกับสภาที่ผู้ใช้เห็น
from AI.council_engine import COUNCIL_SEATS

MEMBERS = [(name, duty) for name, _, _, duty in COUNCIL_SEATS]
_CHOICE_KEEPER = "LYLA"        # เสียงที่ดูแล Choice(t) — ได้น้ำหนักเพิ่มเมื่อเสี่ยงสูง/ยังขยายทางเลือกได้

def _safe_float(val, default=0.0):
    try: return float(val)
    except (TypeError, ValueError): return default

def council_engine(decision: dict, state: dict = None) -> dict:
    state      = state if isinstance(state, dict) else {}
    decision   = decision if isinstance(decision, dict) else {"action": str(decision or "maintain")}
    risk_score = _safe_float(state.get("risk_score", 0))
    stability  = _safe_float(state.get("stability", 50))
    resource   = _safe_float(state.get("resource",  50))
    action     = decision.get("action", "maintain")
    votes = []
    for idx, (member, role) in enumerate(MEMBERS):
        weight = 100 - idx * 6
        if action == "stabilize":
            vote_action = "stabilize"
            bonus = 12 if member == _CHOICE_KEEPER and risk_score >= 70 else (10 if risk_score >= 80 else 0)
            vote_score = weight + bonus
        elif action == "recover_resource":
            vote_action = "recover_resource"
            vote_score  = weight + (8 if resource < 30 else 0)
        elif action == "expand_choices":
            vote_action = "expand_choices"
            bonus = 10 if member == _CHOICE_KEEPER and stability >= 35 else (6 if stability >= 40 else -5)
            vote_score = weight + bonus
        else:
            vote_action = "maintain"
            vote_score  = weight
        votes.append({"member": member, "role": role, "action": vote_action,
                      "score": max(0, min(100, vote_score))})
    avg = round(sum(v["score"] for v in votes) / len(votes), 2) if votes else 0
    return {"decision": decision, "votes": votes, "score": avg, "council_size": len(votes)}
