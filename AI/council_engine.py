# AI/council_engine.py — KING DIADEM
# Council Mode: ทุก AI มาประชุมร่วมกัน ถอด Ego เปิดหลักฐานที่ตรวจสอบได้
# ไม่ใช่แค่ aggregate — แต่คือกระบวนการหาความจริงร่วมกัน
# FATE™ upgrade: choice_count guard + SYSTEM_PAUSE on zero consensus
# Fail less. Harm less. Restore more.

from collections import Counter

COUNCIL_MEMBERS = {
    "LYLA":    "รับรู้ความรู้สึก อยู่เคียงข้าง เปิดทางเลือก",
    "VEGA":    "วิเคราะห์ FATE™ Downside-first ตรรกะ deterministic",
    "PATICCA": "ปฏิจสมุปบาท หาต้นเหตุ ติดตาม chain ของเหตุปัจจัย",
    "TITAN":   "Minimum viable path — อะไรทำให้รอดวันนี้",
    "COSMOS":  "ภาพใหญ่ระยะยาว ผลกระทบต่อทุกสรรพสิ่ง",
}

COUNCIL_RULES = [
    "ถอด Ego ออกก่อนพูด — ไม่มี persona ใดเหนือหลักฐาน",
    "ทุกข้อโต้แย้งต้องมีหลักฐานที่ตรวจสอบได้",
    "ถ้าไม่รู้ — บอกว่าไม่รู้ ไม่สร้างความมั่นใจเทียม",
    "มนุษย์มีอำนาจตัดสินขั้นสุดท้ายเสมอ",
    "ผลลัพธ์ที่ดีที่สุด = ลด harm + เพิ่ม choice",
]

_SAFE_ACTION = "stabilize"


def build_consensus(council_results: dict) -> dict:
    """
    รวมผลจาก council members → มติร่วม
    FATE™: choice_count ≥ 1 — ถ้า SPLIT ทั้งหมด → SYSTEM_PAUSE + fallback
    """
    if not isinstance(council_results, dict) or not council_results:
        return {
            "summary":       "Council ยังไม่มีสมาชิก",
            "final_action":  _SAFE_ACTION,
            "confidence":    0.0,
            "member_count":  0,
            "lines":         [],
            "consensus":     "DEFERRED",
            "audit_trail":   [],
            "fate_audit":    {"choice_count": 0, "system_pause": True},
        }

    lines      = []
    actions    = []
    conf_total = 0.0
    audit      = []

    for member, result in council_results.items():
        role = COUNCIL_MEMBERS.get(member, "observer")

        if isinstance(result, dict):
            action   = str(result.get("action") or result.get("decision") or "observe")
            try:
                conf = float(result.get("confidence", 0.5))
            except (TypeError, ValueError):
                conf = 0.5
            conf = max(0.0, min(1.0, conf / 100.0 if conf > 1 else conf))
            evidence = result.get("evidence") or result.get("reason") or result.get("message") or "ไม่มีหลักฐานระบุ"
            downside = result.get("downside") or ""

            line = f"[{member}] {action}"
            if evidence and evidence != "ไม่มีหลักฐานระบุ":
                line += f" — {evidence}"
            if downside:
                line += f" | ⚠ downside: {downside}"
        else:
            action   = str(result)
            conf     = 0.5
            evidence = "—"
            downside = ""
            line     = f"[{member}] {action}"

        lines.append(line)
        actions.append(action)
        conf_total += conf
        audit.append({
            "member":   member,
            "role":     role,
            "action":   action,
            "evidence": evidence,
            "conf":     round(conf, 3),
        })

    final_action   = Counter(actions).most_common(1)[0][0] if actions else _SAFE_ACTION
    avg_confidence = conf_total / len(council_results)

    top_count = Counter(actions).most_common(1)[0][1]
    total     = len(actions)
    agreement = top_count / total if total else 0

    if agreement >= 0.8:   consensus_level = "STRONG"
    elif agreement >= 0.6: consensus_level = "MODERATE"
    elif agreement >= 0.4: consensus_level = "WEAK"
    else:                  consensus_level = "SPLIT"

    # FATE™: SPLIT → SYSTEM_PAUSE, fallback to safe action
    system_pause = consensus_level == "SPLIT"
    if system_pause:
        final_action = _SAFE_ACTION

    return {
        "summary":       "\n".join(lines),
        "final_action":  final_action,
        "confidence":    round(avg_confidence, 3),
        "member_count":  len(council_results),
        "lines":         lines,
        "consensus":     consensus_level,
        "agreement_pct": round(agreement * 100, 1),
        "audit_trail":   audit,
        "council_rules": COUNCIL_RULES,
        "fate_audit": {
            "choice_count":  len(set(actions)),   # unique options ที่ council propose
            "system_pause":  system_pause,
            "pause_reason":  "SPLIT consensus — fallback to stabilize" if system_pause else None,
        },
    }


def open_council(question: str, context: dict = None) -> dict:
    """เปิด council session สำหรับคำถามหนึ่งข้อ"""
    question = str(question or "")
    if not question.strip():
        return {"error": "FATE_VIOLATION: question empty"}
    return {
        "session":   "COUNCIL_OPEN",
        "question":  question,
        "members":   COUNCIL_MEMBERS,
        "rules":     COUNCIL_RULES,
        "context":   context if isinstance(context, dict) else {},
        "directive": (
            "ทุกสมาชิกต้องถอด Ego — ตอบจากหลักฐานเท่านั้น "
            "ไม่มีใครเหนือกว่าใคร มติเกิดจากหลักฐาน ไม่ใช่อำนาจ"
        ),
    }


def format_council_for_llm(question: str, context: dict = None) -> str:
    """สร้าง prompt สำหรับ LLM ทำหน้าที่เป็น council ทั้งหมด"""
    ctx_text     = "\n".join(f"  {k}: {v}" for k, v in (context if isinstance(context, dict) else {}).items())
    members_text = "\n".join(f"  - {n}: {r}" for n, r in COUNCIL_MEMBERS.items())
    rules_text   = "\n".join(f"  {i+1}. {r}" for i, r in enumerate(COUNCIL_RULES))

    return f"""[COUNCIL SESSION — KING DIADEM]

คำถามที่ council ต้องตอบ:
"{question}"

{f"บริบท:{chr(10)}{ctx_text}" if ctx_text else ""}
สมาชิก council:
{members_text}

กฎ council (ทุกคนต้องปฏิบัติตาม):
{rules_text}

วิธีตอบ:
1. ให้แต่ละสมาชิกพูดตามบทบาทของตน
2. ทุกคนถอด Ego — ไม่มีใครใช้ "ฉันถูก" แต่ใช้ "หลักฐานชี้ว่า"
3. สรุปมติร่วม + ระบุความไม่แน่นอนที่ยังมีอยู่
4. มนุษย์ตัดสินขั้นสุดท้ายเสมอ"""
