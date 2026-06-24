# ENGINE/yonisomanasikara_engine.py
"""
KING DIADEM — Yonisomanasikara Engine
โยนิโสมนสิการ: การทำในใจโดยแยบคาย

ไม่ใช่ศาสนา — คือ Causal Reasoning OS
คิดอย่างมีระเบียบ สืบสาวหาเหตุผลจนตลอดสาย
ไม่ปล่อยให้อารมณ์ หรือ bias นำทาง

เชื่อมกับ paticcasamuppada_engine:
  patticca → หา root cause ของความทุกข์
  yoniso   → คิดอย่างถูกวิธีเพื่อตัดสินใจต่อ
"""

from __future__ import annotations
from typing import Optional
import time


# ══════════════════════════════════════════════════════════════════
# 4 วิธีคิด (Yoniso Modes)
# ══════════════════════════════════════════════════════════════════

YONISO_MODES = {

    "causal": {
        "name":        "สืบสาวเหตุปัจจัย",
        "description": "มองย้อนหาต้นตอที่แท้จริง ไม่ใช่หาคนผิด",
        "trigger_when": "ปัญหาเกิดซ้ำ หรือยังไม่รู้ว่า root cause คืออะไร",
        "questions": [
            "เกิดขึ้นได้อย่างไร — อะไรทำให้เกิดสิ่งนี้",
            "มีปัจจัยอะไรที่ยังอยู่ที่ทำให้มันยังเกิดซ้ำ",
            "ถ้าเอาปัจจัยนั้นออก สิ่งนี้ยังเกิดได้ไหม",
        ],
    },

    "analytical": {
        "name":        "แยกแยะส่วนประกอบ",
        "description": "มองปัญหาให้เห็นส่วนย่อย ไม่เหมารวมทั้งก้อน",
        "trigger_when": "รู้สึกว่าทุกอย่างแย่ หรือปัญหาใหญ่เกินจัดการ",
        "questions": [
            "ถ้าแยกปัญหาออกเป็น 3 ส่วน แต่ละส่วนคืออะไร",
            "ส่วนไหนที่แก้ได้ตอนนี้เลย",
            "ส่วนไหนที่ต้องรอ หรือต้องการคนอื่น",
        ],
    },

    "ariyasacca": {
        "name":        "อริยสัจ 4",
        "description": "คิดแบบแก้ปัญหาเป็นระบบ — ทุกข์/เหตุ/เป้าหมาย/วิธี",
        "trigger_when": "มีปัญหาชัดเจน ต้องการแผนปฏิบัติจริง",
        "questions": [
            "ทุกข์: ปัญหาที่แท้จริงคืออะไร — อธิบายให้ตรงที่สุด",
            "สมุทัย: เกิดจากอะไร — ต้นตอที่ควบคุมได้คืออะไร",
            "นิโรธ: ถ้าแก้ได้ สภาพที่ต้องการคืออะไร — วัดได้ยังไง",
            "มรรค: ต้องทำอะไรบ้าง — ขั้นตอนแรกที่ทำได้ตอนนี้คืออะไร",
        ],
    },

    "impermanence": {
        "name":        "รู้เท่าทันธรรมดา",
        "description": "เห็นความไม่เที่ยงของสิ่งต่างๆ ลดความยึดติด",
        "trigger_when": "ทุกข์จากการสูญเสีย หรือยึดติดกับสิ่งที่ผ่านมาแล้ว",
        "questions": [
            "สิ่งนี้จะยังอยู่อีกนานแค่ไหน — มันเปลี่ยนได้ไหม",
            "ถ้ามันหายไปพรุ่งนี้ อะไรที่ยังคงอยู่",
            "ความยึดติดนี้ปกป้องเราจริงๆ หรือแค่กันไม่ให้เดินต่อ",
        ],
    },
}


# ══════════════════════════════════════════════════════════════════
# BIAS DETECTOR — ตรวจ cognitive bias ก่อนตัดสินใจ
# ══════════════════════════════════════════════════════════════════

BIAS_PATTERNS = {
    "confirmation": {
        "signals": ["แน่นอนว่า", "ฉันรู้อยู่แล้วว่า", "เห็นไหม", "ที่บอกไว้แล้ว", "i knew it"],
        "description": "มองหาข้อมูลที่ยืนยันสิ่งที่เชื่ออยู่แล้ว",
        "correction":  "ลองหาข้อมูลที่ขัดแย้งกับสิ่งที่เชื่ออยู่ด้วย",
    },
    "sunk_cost": {
        "signals": ["ลงทุนไปแล้ว", "เสียไปแล้ว", "ทำมานานแล้ว", "ถอยไม่ได้แล้ว", "already invested"],
        "description": "ยึดติดกับสิ่งที่ลงทุนไปแล้ว แม้มันไม่คุ้มต่อ",
        "correction":  "ถามว่า ถ้าเริ่มใหม่วันนี้ จะยังเลือกทางนี้ไหม",
    },
    "availability": {
        "signals": ["เห็นข่าว", "เพิ่งเกิดขึ้น", "มีคนบอก", "ได้ยินมาว่า"],
        "description": "ตัดสินใจจากข้อมูลที่เพิ่งเจอ ไม่ใช่ข้อมูลที่ครบถ้วน",
        "correction":  "ถามว่า ข้อมูลนี้ตัวแทนของทั้งหมดจริงไหม",
    },
    "catastrophizing": {
        "signals": ["แย่มาก", "พังทุกอย่าง", "ไม่มีทางออก", "จบแล้ว", "everything is ruined"],
        "description": "มองผลลัพธ์แย่ที่สุดว่าเป็นสิ่งเดียวที่จะเกิด",
        "correction":  "ถามว่า ถ้า 100 คนเจอสถานการณ์นี้ กี่คนที่ผ่านมาได้",
    },
    "black_white": {
        "signals": ["ต้องเลือกอย่างใดอย่างหนึ่ง", "ไม่มีทางกลาง", "ทำแบบนี้หรือแบบนั้น", "either or"],
        "description": "มองว่ามีแค่ 2 ทางเลือก ทั้งที่มีอีกหลายทาง",
        "correction":  "ถามว่า มีทางที่ 3, 4 ไหม — ที่ไม่ใช่ทั้งสอง",
    },
    "personalization": {
        "signals": ["เพราะฉัน", "เป็นความผิดฉัน", "ฉันทำให้", "my fault", "because of me"],
        "description": "รับผิดชอบเหตุการณ์ที่ตัวเองไม่ได้เป็นปัจจัยหลัก",
        "correction":  "ถามว่า ปัจจัยอื่นๆ ที่ทำให้เกิดสิ่งนี้มีอะไรบ้าง",
    },
}


def detect_bias(text: str) -> list:
    t = text.lower()
    found = []
    for bias_name, meta in BIAS_PATTERNS.items():
        hits = [s for s in meta["signals"] if s in t]
        if hits:
            found.append({
                "bias":        bias_name,
                "description": meta["description"],
                "correction":  meta["correction"],
                "triggers":    hits,
            })
    return found


# ══════════════════════════════════════════════════════════════════
# MODE SELECTOR — เลือก yoniso mode ที่เหมาะสมที่สุด
# ══════════════════════════════════════════════════════════════════

def _select_mode(text: str, pattern: dict) -> str:
    t         = text.lower()
    entropy   = float(pattern.get("entropy",   40))
    stability = float(pattern.get("stability", 60))

    # ถ้า stability ต่ำมาก → อริยสัจก่อน เพื่อหา action จริง
    if stability < 30:
        return "ariyasacca"

    # ถ้าพูดถึงการสูญเสีย หรือยึดติด
    if any(k in t for k in ("เสีย", "หาย", "จาก", "ตาย", "ปล่อย", "คิดถึง", "ลืม", "loss", "gone", "miss")):
        return "impermanence"

    # ถ้าพูดว่าทุกอย่างแย่ หรือจัดการไม่ได้
    if any(k in t for k in ("ทุกอย่าง", "ไม่รู้จะ", "ไม่รู้ว่า", "หนักมาก", "overwhelm")):
        return "analytical"

    # ถ้าเกิดซ้ำๆ หรือไม่รู้ต้นตอ
    if any(k in t for k in ("ซ้ำ", "อีกแล้ว", "ทำไมถึง", "again", "why does", "ทำไม")):
        return "causal"

    # default: อริยสัจ — ใช้ได้กับทุกสถานการณ์
    return "ariyasacca"


# ══════════════════════════════════════════════════════════════════
# MAIN: wise_attention — entry point
# ══════════════════════════════════════════════════════════════════

def wise_attention(
    context: str,
    pattern: Optional[dict] = None,
    mode:    Optional[str]  = None,
) -> dict:
    """
    Yonisomanasikara — คิดอย่างถูกวิธี

    Args:
        context: ข้อความ / สถานการณ์ที่ต้องการวิเคราะห์
        pattern: {entropy, stability, resource, ...} จาก DecisionEngine
        mode:    บังคับ mode ถ้าต้องการ (causal/analytical/ariyasacca/impermanence)

    Returns:
        {
          mode, mode_meta, questions,
          bias_detected, corrections,
          patticca_link,         # เชื่อมกับ paticcasamuppada ถ้ามี
          should_pause,
          summary,
        }
    """
    pattern   = pattern or {}
    t0        = time.time()

    # เลือก mode
    selected_mode = mode if mode in YONISO_MODES else _select_mode(context, pattern)
    mode_meta     = YONISO_MODES[selected_mode]

    # ตรวจ bias
    biases    = detect_bias(context)
    corrections = [b["correction"] for b in biases]

    # เชื่อมกับ paticcasamuppada ถ้ามี
    patticca_link = None
    try:
        from ENGINE.paticcasamuppada_engine import detect_root_cause, run_uap
        root_info     = detect_root_cause(context)
        uap           = run_uap(context, pattern)
        patticca_link = {
            "root_cause":   root_info["root"],
            "feeling_tone": root_info["feeling"],
            "should_pause": uap["should_pause"],
            "uap_note":     uap["audit_note"],
        }
        should_pause = uap["should_pause"] or len(biases) >= 2
    except ImportError:
        should_pause = len(biases) >= 2

    # สร้าง questions ที่ context-aware
    questions = _contextualize_questions(mode_meta["questions"], context, pattern)

    # Summary
    bias_names = [b["bias"] for b in biases]
    if should_pause:
        summary = f"ควรหยุดคิดทบทวนก่อน — พบ bias: {', '.join(bias_names) or 'ไม่พบ'} | mode: {mode_meta['name']}"
    else:
        summary = f"พร้อมดำเนินการ — ใช้วิธีคิดแบบ {mode_meta['name']}"

    return {
        "mode":           selected_mode,
        "mode_name":      mode_meta["name"],
        "mode_description": mode_meta["description"],
        "trigger_when":   mode_meta["trigger_when"],
        "questions":      questions,
        "bias_detected":  biases,
        "bias_count":     len(biases),
        "corrections":    corrections,
        "patticca_link":  patticca_link,
        "should_pause":   should_pause,
        "summary":        summary,
        "latency_ms":     round((time.time() - t0) * 1000, 1),
        "axiom":          "โยนิโสมนสิการ — ตัดที่เหตุ ไม่ตัดที่ผล",
    }


def _contextualize_questions(questions: list, context: str, pattern: dict) -> list:
    """ปรับ questions ให้ specific กับ context จริง"""
    entropy  = float(pattern.get("entropy",  40))
    resource = float(pattern.get("resource", 50))
    result   = []

    for q in questions:
        # เพิ่ม urgency note ถ้า entropy สูง
        if entropy > 65 and "ต้นตอ" in q:
            q = q + " (ด่วน — entropy สูง ต้องตัดสาเหตุก่อน)"
        if resource < 30 and "ทำอะไร" in q:
            q = q + " — โดยใช้ทรัพยากรน้อยที่สุด"
        result.append(q)

    return result


# ══════════════════════════════════════════════════════════════════
# ADAPTER สำหรับ DecisionEngine
# ══════════════════════════════════════════════════════════════════

def analyze(pattern: dict) -> dict:
    """DecisionEngine เรียกผ่าน adapter นี้"""
    try:
        context = str(pattern.get("input", ""))
        return wise_attention(context, pattern)
    except Exception as e:
        return {"error": f"yonisomanasikara fail: {str(e)}"}


# ── All modes info — สำหรับ UI ───────────────────────────────────
def get_all_modes() -> dict:
    return {
        mode: {
            "name":        meta["name"],
            "description": meta["description"],
            "trigger_when":meta["trigger_when"],
        }
        for mode, meta in YONISO_MODES.items()
    }
