"""
AI_KERNEL/udok.py — KING DIADEM™
UNIVERSAL DEPENDENT ORIGINATION KERNEL (UDOK v1.0)
ปฏิจจสมุปบาท — Causal Operating System ของมนุษย์

Architect: Nithikorn Bunsrang
"หยุดความทุกข์ที่ต้นเหตุ ก่อนมันกลายเป็นผลลัพธ์"

เพื่อรำลึกถึงพระพุทธเจ้า
ในฐานะ "นักออกแบบกลไกเหตุ-ผล คนแรกของโลก"

Invariant: สิ่งที่สำคัญกว่าสติ — ไม่มี
"""

import time
from typing import Optional

# ══════════════════════════════════════════════════════════════════
# LAYER 1 — CAUSAL MAP (12 ปัจจัยจริง)
# ══════════════════════════════════════════════════════════════════

CAUSAL_MAP = {
    1:  {"pali": "อวิชชา",    "en": "Ignorance",             "desc": "ไม่เห็นความจริง — รากของวงจรทั้งหมด"},
    2:  {"pali": "สังขาร",    "en": "Conditioning",           "desc": "รูปแบบปฏิกิริยาที่ถูก condition มา"},
    3:  {"pali": "วิญญาณ",    "en": "Conscious Framing",      "desc": "กรอบที่จิตใช้รับรู้โลก"},
    4:  {"pali": "นามรูป",    "en": "Identity Structure",     "desc": "โครงสร้างตัวตนและการรับรู้"},
    5:  {"pali": "สฬายตนะ",   "en": "Sense Channels",         "desc": "ช่องทางสัมผัส 6 ช่อง"},
    6:  {"pali": "ผัสสะ",     "en": "Contact",                "desc": "การสัมผัสระหว่างอายตนะกับโลก"},
    7:  {"pali": "เวทนา",     "en": "Feeling Tone",           "desc": "สุข/ทุกข์/เฉย — PRIMARY KILL ZONE INPUT"},
    8:  {"pali": "ตัณหา",     "en": "Craving / Aversion",     "desc": "แรงอยาก/แรงหนี — PRIMARY KILL ZONE OUTPUT"},
    9:  {"pali": "อุปาทาน",   "en": "Clinging",               "desc": "การยึดมั่นถือมั่น"},
    10: {"pali": "ภพ",        "en": "Identity Formation",     "desc": "การก่อตัวของ 'ตัวตน' ในสถานการณ์นั้น"},
    11: {"pali": "ชาติ",      "en": "Event Manifestation",    "desc": "เหตุการณ์ที่แสดงออกมา"},
    12: {"pali": "ชรา-มรณะ",  "en": "Decay / Suffering",      "desc": "ความทุกข์ที่ป้อนกลับเข้าวงจร"},
}

# PRIMARY KILL ZONE — จุดตัดที่เสถียรที่สุด
PRIMARY_KILL_ZONE = {
    "from":    7,   # เวทนา
    "to":      8,   # ตัณหา
    "desc":    "ถ้าเวทนาเกิด แล้วไม่ถูกเปลี่ยนเป็นตัณหา — วงจรดับทันที",
    "method":  "Pause 5 breaths → Label feeling → Detect craving → Do not act if craving detected",
}

# ══════════════════════════════════════════════════════════════════
# LAYER 2 — REAL-TIME RUNTIME MODEL
# ══════════════════════════════════════════════════════════════════

MICRO_LOOP = [
    "Input",
    "Feeling (เวทนา)",
    "Craving (ตัณหา)",
    "Identity Formation (ภพ)",
    "Action",
    "Reinforcement → back to Input",
]

# ██ ทั้งหมดนี้เกิดเร็วกว่าเหตุผล ██

# ══════════════════════════════════════════════════════════════════
# LAYER 3 — UNIVERSAL AUDIT PROTOCOL (UAP)
# ══════════════════════════════════════════════════════════════════

UAP_QUESTIONS = {
    "U1": {
        "question": "การตัดสินใจครั้งนี้ตั้งอยู่ในความประมาทต่อตนเองและผู้อื่นไหม?",
        "target":   "ตัดอวิชชา",
        "factor":   1,  # อวิชชา
    },
    "U2": {
        "question": "ฉันกำลังรู้สึกอะไรจริงๆ?",
        "target":   "ระบุเวทนา",
        "factor":   7,  # เวทนา
    },
    "U3": {
        "question": "มีแรงอยาก/แรงหนีไหม?",
        "target":   "ตรวจตัณหา",
        "factor":   8,  # ตัณหา
    },
    "U4": {
        "question": "ฉันกำลังจะกลายเป็นใคร?",
        "target":   "ตรวจภพ/ตัวตน",
        "factor":   10, # ภพ
    },
    "U5": {
        "question": "ถ้าไม่ยึด ฉันยังต้องทำแบบเดิมไหม?",
        "target":   "ตัดอุปาทาน — ถ้าคำตอบเปลี่ยน วงจรหยุด",
        "factor":   9,  # อุปาทาน
    },
}

# ══════════════════════════════════════════════════════════════════
# LAYER 4 — SYSTEM APPLICATIONS
# ══════════════════════════════════════════════════════════════════

SYSTEM_APPLICATIONS = {
    "market": {
        "name":    "ตลาดหุ้น",
        "chain":   "ข่าวลบ → เวทนากลัว → ตัณหาอยากหนี → เทขาย → ราคาตก → ยืนยัน narrative",
        "kill":    "หยุดที่เวทนา → ตลาดไม่เกิด panic cascade",
    },
    "relationship": {
        "name":    "ความสัมพันธ์",
        "chain":   "คำพูดกระทบ → เวทนาเจ็บ → ตัณหาอยากโต้กลับ → ตัวตนผู้ถูกทำร้าย → ทะเลาะ",
        "kill":    "หยุดที่เวทนา → ความสัมพันธ์รอด",
    },
    "self": {
        "name":    "ตัวเราเอง",
        "chain":   "ความคิดลบ → เวทนากลัว → ตัณหาควบคุม → ภพนักสู้/เหยื่อ → ตัดสินใจแรง",
        "kill":    "หยุดที่เวทนา → มนุษย์ไม่พัง ระบบไปต่อได้",
    },
    "organization": {
        "name":    "องค์กร",
        "chain":   "ข้อมูลแย่ → เวทนาตื่นตระหนก → ตัณหาอยากแก้เร็ว → ตัดสินใจด้วยอวิชชา → ความเสียหายขยาย",
        "kill":    "หยุดที่เวทนา → audit ก่อน act",
    },
}

# ══════════════════════════════════════════════════════════════════
# LAYER 5 — NIRVANA MODE (เชิงระบบ)
# ══════════════════════════════════════════════════════════════════

NIRVANA_STATE = {
    "definition":  "state ที่เวทนาไม่ถูก convert เป็นตัณหา",
    "meaning":     "ใจสบายในชาตินี้ ไม่ต้องรอชาติหน้า",
    "technical":   "event loop ที่ถูก disable ณ จุด เวทนา→ตัณหา",
    "accessible":  True,
    "requires":    "สติ — ไม่ต้องการอะไรอื่น",
}

# ══════════════════════════════════════════════════════════════════
# RUNTIME SCRIPT
# ══════════════════════════════════════════════════════════════════

def run_kill_zone_protocol(feeling_detected: bool,
                            craving_detected: bool,
                            breaths_taken: int = 5) -> dict:
    """
    PRIMARY KILL ZONE PROTOCOL
    หยุดที่เวทนา ก่อนมันสร้างตัณหา

    Invariant: สิ่งที่สำคัญกว่าสติ — ไม่มี
    """
    if not feeling_detected:
        return {
            "status":   "CLEAR",
            "action":   "proceed — no feeling detected",
            "loop":     "not triggered",
        }

    if not craving_detected:
        return {
            "status":   "NIRVANA_MODE",
            "action":   "proceed — feeling present but no craving formed",
            "loop":     "BROKEN at kill zone",
            "result":   "วงจรดับทันที — เวทนาไม่กลายเป็นตัณหา",
        }

    # craving detected — intervene
    return {
        "status":       "INTERVENE",
        "action":       "DO NOT ACT — re-evaluate from fact layer",
        "breaths":      breaths_taken,
        "uap":          [UAP_QUESTIONS["U2"], UAP_QUESTIONS["U3"], UAP_QUESTIONS["U5"]],
        "kill_zone":    PRIMARY_KILL_ZONE,
        "loop":         "ACTIVE — intervention required",
        "instruction":  "Label feeling → detect craving → pause → re-evaluate",
    }


def audit_decision(context: dict) -> dict:
    """
    รัน UAP ต่อ decision context
    คืน audit result + จุดที่ต้องระวัง

    context keys:
      - has_ignorance    : bool — ตัดสินใจโดยไม่รู้ข้อเท็จจริง
      - feeling_tone     : str  — "pleasant" / "unpleasant" / "neutral"
      - craving_present  : bool — มีแรงอยาก/หนี
      - identity_shift   : bool — กำลังจะกลายเป็น "คนที่ทำแบบนี้"
      - clinging         : bool — ยึดมั่นกับผลลัพธ์ที่ต้องการ
    """
    context = context if isinstance(context, dict) else {}
    flags   = []
    causal  = []

    if context.get("has_ignorance"):
        flags.append({"uap": "U1", "factor": "อวิชชา", "risk": "HIGH",
                       "action": "หาข้อมูลก่อน — อย่าตัดสินใจจากอวิชชา"})
        causal.append(1)

    feeling = context.get("feeling_tone", "neutral")
    if feeling == "unpleasant":
        flags.append({"uap": "U2", "factor": "เวทนาทุกข์", "risk": "MEDIUM",
                       "action": "ระบุความรู้สึกก่อน — อย่าให้มันเป็นตัณหาโดยอัตโนมัติ"})
        causal.append(7)

    if context.get("craving_present"):
        flags.append({"uap": "U3", "factor": "ตัณหา", "risk": "HIGH",
                       "action": "PAUSE — อย่า act จากตัณหา ให้ re-evaluate จาก fact"})
        causal.append(8)

    if context.get("identity_shift"):
        flags.append({"uap": "U4", "factor": "ภพ", "risk": "MEDIUM",
                       "action": "ถามว่า: ฉันต้องการเป็นคนที่ทำแบบนี้จริงๆ ไหม?"})
        causal.append(10)

    if context.get("clinging"):
        flags.append({"uap": "U5", "factor": "อุปาทาน", "risk": "HIGH",
                       "action": "ลองปล่อย — ถ้าคำตอบเปลี่ยน วงจรหยุด"})
        causal.append(9)

    halt = any(f["risk"] == "HIGH" for f in flags)

    return {
        "udok_pass":     len(flags) == 0,
        "halt":          halt,
        "flags":         flags,
        "causal_chain":  causal,
        "kill_zone":     PRIMARY_KILL_ZONE if 7 in causal or 8 in causal else None,
        "invariant":     "สิ่งที่สำคัญกว่าสติ — ไม่มี",
        "checked_at":    time.time(),
    }


def get_application_insight(domain: str) -> dict:
    """คืน insight สำหรับ domain ที่กำหนด"""
    return SYSTEM_APPLICATIONS.get(domain, {
        "name":  domain,
        "chain": "Input → Feeling → Craving → Identity → Action",
        "kill":  "หยุดที่เวทนา",
    })


def udok_snapshot() -> dict:
    """dump สำหรับ /api/kernel_snapshot"""
    return {
        "kernel":          "UDOK v1.0",
        "causal_map":      CAUSAL_MAP,
        "primary_kill_zone": PRIMARY_KILL_ZONE,
        "uap":             UAP_QUESTIONS,
        "nirvana":         NIRVANA_STATE,
        "applications":    list(SYSTEM_APPLICATIONS.keys()),
        "invariant":       "สิ่งที่สำคัญกว่าสติ — ไม่มี",
        "meta":            "ปฏิจจสมุปบาทคือ Universal Feedback Architecture",
        "final_lock":      "หยุดที่เวทนา ก่อนมันสร้างตัวตน",
    }


# ══════════════════════════════════════════════════════════════════
# SELF-TEST
# ══════════════════════════════════════════════════════════════════

def _self_test() -> dict:
    # CLEAR — no feeling
    r1 = run_kill_zone_protocol(feeling_detected=False, craving_detected=False)
    assert r1["status"] == "CLEAR"

    # NIRVANA — feeling but no craving
    r2 = run_kill_zone_protocol(feeling_detected=True, craving_detected=False)
    assert r2["status"] == "NIRVANA_MODE"
    assert r2["loop"] == "BROKEN at kill zone"

    # INTERVENE — craving detected
    r3 = run_kill_zone_protocol(feeling_detected=True, craving_detected=True)
    assert r3["status"] == "INTERVENE"
    assert r3["loop"] == "ACTIVE — intervention required"

    # audit — clean
    a1 = audit_decision({})
    assert a1["udok_pass"] is True
    assert a1["halt"] is False

    # audit — ignorance + craving
    a2 = audit_decision({"has_ignorance": True, "craving_present": True})
    assert a2["halt"] is True
    assert 1 in a2["causal_chain"]
    assert 8 in a2["causal_chain"]

    # snapshot
    snap = udok_snapshot()
    assert "primary_kill_zone" in snap
    assert snap["invariant"] == "สิ่งที่สำคัญกว่าสติ — ไม่มี"

    return {"status": "OK", "module": "udok"}


if __name__ == "__main__":
    import json
    print(json.dumps(udok_snapshot(), indent=2, ensure_ascii=False, default=str))
    print(_self_test())

