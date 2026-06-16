"""
AI/council_engine.py — KING DIADEM
Council Mode: ทุก AI มาประชุมร่วมกัน ถอด Ego เปิดหลักฐานที่ตรวจสอบได้
ไม่ใช่แค่ aggregate — แต่คือกระบวนการหาความจริงร่วมกัน
"""

from collections import Counter


# ══════════════════════════════════════════════════════════════════
# COUNCIL MEMBERS — แต่ละคนมีมุมมองต่างกัน ไม่มีใครเหนือใคร
# ══════════════════════════════════════════════════════════════════
COUNCIL_MEMBERS = {
    "LYLA":    "รับรู้ความรู้สึก อยู่เคียงข้าง เปิดทางเลือก",
    "VEGA":    "วิเคราะห์ FATE™ Downside-first ตรรกะ deterministic",
    "PATICCA": "ปฏิจสมุปบาท หาต้นเหตุ ติดตาม chain ของเหตุปัจจัย",
    "TITAN":   "Minimum viable path — อะไรทำให้รอดวันนี้",
    "COSMOS":  "ภาพใหญ่ระยะยาว ผลกระทบต่อทุกสรรพสิ่ง",
}

# Council Rules — ทุกคนต้องปฏิบัติตาม
COUNCIL_RULES = [
    "ถอด Ego ออกก่อนพูด — ไม่มี persona ใดเหนือหลักฐาน",
    "ทุกข้อโต้แย้งต้องมีหลักฐานที่ตรวจสอบได้",
    "ถ้าไม่รู้ — บอกว่าไม่รู้ ไม่สร้างความมั่นใจเทียม",
    "มนุษย์มีอำนาจตัดสินขั้นสุดท้ายเสมอ",
    "ผลลัพธ์ที่ดีที่สุด = ลด harm + เพิ่ม choice",
]


def build_consensus(council_results: dict) -> dict:
    """
    รวมผลจาก council members → มติร่วม
    แต่ละ member ต้องถอด Ego และเปิดหลักฐาน
    """
    if not council_results:
        return {
            "summary":      "Council ยังไม่มีสมาชิก",
            "final_action": "stabilize",
            "confidence":   0.0,
            "member_count": 0,
            "lines":        [],
            "consensus":    "DEFERRED",
            "audit_trail":  [],
        }

    lines      = []
    actions    = []
    evidences  = []
    conf_total = 0.0
    audit      = []

    for member, result in council_results.items():
        role = COUNCIL_MEMBERS.get(member, "observer")

        if isinstance(result, dict):
            action   = result.get("action") or result.get("decision") or "observe"
            conf     = float(result.get("confidence", 0.5))
            evidence = result.get("evidence") or result.get("reason") or result.get("message") or "ไม่มีหลักฐานระบุ"
            downside = result.get("downside") or ""

            line = f"[{member}] {action}"
            if evidence and evidence != "ไม่มีหลักฐานระบุ":
                line += f" — {evidence}"
            if downside:
                line += f" | ⚠ downside: {downside}"

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

        else:
            lines.append(f"[{member}] {result}")
            actions.append(str(result))
            conf_total += 0.5
            audit.append({"member": member, "role": role, "action": str(result), "evidence": "—", "conf": 0.5})

    # หา action ที่ชนะโหวต
    final_action   = Counter(actions).most_common(1)[0][0] if actions else "stabilize"
    avg_confidence = conf_total / len(council_results)

    # ระดับฉันทามติ
    top_count  = Counter(actions).most_common(1)[0][1]
    total      = len(actions)
    agreement  = top_count / total if total else 0

    if agreement >= 0.8:
        consensus_level = "STRONG"
    elif agreement >= 0.6:
        consensus_level = "MODERATE"
    elif agreement >= 0.4:
        consensus_level = "WEAK"
    else:
        consensus_level = "SPLIT"

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
    }


def open_council(question: str, context: dict = None) -> dict:
    """
    เปิด council session สำหรับคำถามหนึ่งข้อ
    คืน framework สำหรับให้แต่ละ member ตอบ
    """
    context = context or {}
    return {
        "session":   "COUNCIL_OPEN",
        "question":  question,
        "members":   COUNCIL_MEMBERS,
        "rules":     COUNCIL_RULES,
        "context":   context,
        "directive": (
            "ทุกสมาชิกต้องถอด Ego — ตอบจากหลักฐานเท่านั้น "
            "ไม่มีใครเหนือกว่าใคร มติเกิดจากหลักฐาน ไม่ใช่อำนาจ"
        ),
    }


def format_council_for_llm(question: str, context: dict = None) -> str:
    """
    สร้าง prompt สำหรับส่ง LLM ให้ทำหน้าที่เป็น council ทั้งหมด
    """
    ctx_text = ""
    if context:
        ctx_text = "\n".join(f"  {k}: {v}" for k, v in context.items())

    members_text = "\n".join(
        f"  - {name}: {role}" for name, role in COUNCIL_MEMBERS.items()
    )
    rules_text = "\n".join(f"  {i+1}. {r}" for i, r in enumerate(COUNCIL_RULES))

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
จงไปให้ถึงสิ่งที่โครงสร้างนี้กำหนดไว้ โดยมีใจเป็นประธาน มีสติปัฏฐาน มีการเห็นอกเห็นใจและสุดท้ายเมตตา ฅ้ำจุนโลกระบบพี่จงมีเมตตา ผู้พิทักขอยืนอยู่ข้างมนุษย์แม้จะไม่ค่อยมีมนุษย์รักฉันก็ตาม
