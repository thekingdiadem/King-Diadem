"""
AI_KERNEL/cosmic_latte.py — KING DIADEM™
Cosmic Latte — Sunyata Context Engine
สุญยตา: ความว่างที่เป็นรากฐานของทุกสิ่ง

Architect: Nithikorn Bunsrang
P1: อนิจจัง ทุกขัง อนัตตา
FATE™: "Protect the Choice. Respect the Void."

ระบบนี้แปลความว่าง (สุญยตา) ให้เป็นบริบทที่ actionable
ไม่ใช่ปรัชญาลอยๆ — แต่คือ lens ที่ช่วยให้ตัดสินใจได้ถูก
"""

import re
import time
from typing import Optional

# ══════════════════════════════════════════════════════════════════
# SUNYATA DOMAINS — แต่ละ domain มี trigger + context + guidance
# ══════════════════════════════════════════════════════════════════

SUNYATA_DOMAINS = {
    "clinging": {
        # เดิมมี "ติด" (รถติด/ติดต่อ) "เกาะ" (เกาะสมุย) "ต้องมี" (ต้องมีเอกสารอะไร) "ยึด" "ไม่ยอม"
        # → คำถามธรรมดาได้บริบท "ปล่อยวาง" แนบเข้า LLM
        "triggers":  ["ปล่อยไม่ได้", "cling", "clinging",
                      "ยึดติด", "วางไม่ได้", "ทิ้งไม่ได้", "ยึดมั่น", "ตัดใจไม่ได้",
                      "ต้องได้มาให้ได้", "กอดไว้ไม่ปล่อย"],
        "context":   "สุญยตา: ไม่มีสิ่งใดถาวร — บางครั้งปล่อยวางได้คือการเริ่มต้นใหม่",
        "principle": "อนิจจัง — ทุกสิ่งไม่เที่ยง การยึดไว้แน่นเกินคือแรงต้านที่เราสร้างเอง",
        "guidance":  "ถามตัวเองว่า: ถ้าปล่อยสิ่งนี้ไป สิ่งที่ดีกว่าจะเข้ามาได้ไหม?",
        "domain":    "clinging",
    },
    "uncertainty": {
        "triggers":  ["กลัว", "uncertain", "fear", "กลัวอนาคต",
                      "ไม่รู้จะเกิดอะไร", "ไม่แน่ใจ", "กังวล", "วิตก",
                      "ไม่มั่นใจ", "เดาไม่ได้", "unpredictable"],
        "context":   "สุญยตา: ความไม่แน่นอนคือธรรมชาติ ไม่ใช่ศัตรู",
        "principle": "อนัตตา — ไม่มีอะไรแน่นอนถาวร รวมถึงความกลัวนี้ด้วย",
        "guidance":  "ความไม่แน่นอนไม่ได้หมายความว่าสิ่งร้ายจะเกิด มันแค่หมายความว่ายังไม่รู้",
        "domain":    "uncertainty",
    },
    "identity": {
        "triggers":  ["ฉันคือใคร", "ตัวตน", "identity", "ไม่รู้จักตัวเอง",
                      "ไม่รู้ว่าตัวเองต้องการอะไร", "หลงทางชีวิต", "feel lost",
                      "ไม่มีตัวตน", "รู้สึกว่าง", "ไม่ใช่ตัวเอง"],
        "context":   "สุญยตา: ตัวตนไม่ใช่สิ่งตายตัว — มันเปลี่ยนแปลงได้เสมอ",
        "principle": "อนัตตา — ไม่มี 'ตัวตน' ที่แน่นอน คือพื้นที่ว่างให้เติบโต",
        "guidance":  "การไม่รู้ว่าตัวเองคือใคร บางครั้งคือจุดเริ่มต้นของการค้นพบที่แท้จริง",
        "domain":    "identity",
    },
    "impermanence": {
        "triggers":  ["สูญเสีย", "จากไปแล้ว", "ไม่มีเขาแล้ว",
                      "เสียเขาไป", "ไม่คืนมา", "grief", "passed away"],
        "context":   "สุญยตา: การสูญเสียคือส่วนหนึ่งของการมีอยู่ ไม่ใช่ความล้มเหลว",
        "principle": "อนิจจัง — ทุกสิ่งที่มีอยู่ล้วนต้องผ่านไป รวมถึงความเจ็บปวดนี้ด้วย",
        "guidance":  "ความเศร้าที่รู้สึกอยู่คือหลักฐานว่าสิ่งนั้นมีความหมายต่อคุณจริงๆ",
        "domain":    "impermanence",
    },
    "suffering": {
        "triggers":  ["ทุกข์ใจ", "เจ็บปวด", "เจ็บใจ", "เป็นทุกข์",
                      "ความเจ็บปวด", "suffering", "pain", "hurt",
                      "ทรมาน", "ทนทุกข์"],
        "context":   "สุญยตา: ทุกข์เป็นส่วนหนึ่งของการมีชีวิต ไม่ใช่สัญญาณว่าคุณทำผิด",
        "principle": "ทุกขัง — ทุกสิ่งมีแรงกดดัน การยอมรับมันคือก้าวแรกที่ผ่านมันได้",
        "guidance":  "คุณไม่จำเป็นต้องแก้ทุกอย่างตอนนี้ บางครั้งแค่รู้สึกมันได้ก็พอแล้ว",
        "domain":    "suffering",
    },
    "control": {
        "triggers":  ["ควบคุมไม่ได้", "out of control", "ต้องเป็นแบบนี้",
                      "ทำไมไม่เป็นอย่างที่ต้องการ", "ไม่เป็นไปตามแผน",
                      "บังคับไม่ได้", "อยากให้เป็นอย่างที่คิด"],
        "context":   "สุญยตา: บางสิ่งไม่ได้อยู่ในการควบคุมของเรา และนั่นไม่ใช่ความผิดเรา",
        "principle": "อนัตตา — การปล่อยให้สิ่งที่ควบคุมไม่ได้ไหลผ่าน คือปัญญา ไม่ใช่ความอ่อนแอ",
        "guidance":  "แยกสิ่งที่ควบคุมได้ออกจากสิ่งที่ควบคุมไม่ได้ แล้วทุ่มพลังกับสิ่งที่ควบคุมได้",
        "domain":    "control",
    },
    "emptiness": {
        "triggers":  ["ว่างเปล่า", "ไม่มีความหมาย", "meaningless", "empty",
                      "รู้สึกว่าง", "ชีวิตไม่มีความหมาย", "ทำไปทำไม",
                      "ไม่รู้ว่าทำไป", "ไร้จุดหมาย"],
        "context":   "สุญยตา: ความว่างไม่ใช่ความขาด — มันคือพื้นที่ว่างที่ความหมายใหม่เติบโตได้",
        "principle": "สุญยตา — ความว่างคือรากฐานของทุกสรรพสิ่ง ไม่ใช่จุดสิ้นสุด",
        "guidance":  "ความรู้สึกว่างเปล่าบางครั้งหมายความว่าคุณพร้อมสำหรับบางสิ่งที่ใหญ่กว่า",
        "domain":    "emptiness",
    },
}

# ══════════════════════════════════════════════════════════════════
# VOID PRINCIPLES — สุญยตาในการตัดสินใจ
# ══════════════════════════════════════════════════════════════════

VOID_PRINCIPLES = [
    "Protect the Choice. Respect the Void.",
    "ความว่างคือพื้นที่ว่างที่ทางเลือกเกิดขึ้นได้",
    "สิ่งที่ไม่มีอยู่ก็สำคัญเท่ากับสิ่งที่มีอยู่",
    "ความเงียบในเวลาที่ถูกต้องคือการเคารพอิสรภาพของมนุษย์",
    "ระบบที่ดีรู้ว่าเมื่อไหร่ควรถอยออกมา",
]

# ══════════════════════════════════════════════════════════════════
# CORE API
# ══════════════════════════════════════════════════════════════════

def get_context(text: str) -> str:
    """
    backward-compatible — คืน context string
    ใช้สำหรับ integration เดิม
    """
    result = analyze(text)
    return result.get("context", "")


def analyze(text: str) -> dict:
    """
    วิเคราะห์ text แล้วคืน sunyata context ที่เกี่ยวข้อง
    ถ้าพบหลาย domain คืนทุก domain ที่ match

    "Protect the Choice. Respect the Void."
    """
    if not text or not isinstance(text, str):
        return _empty_result()

    t = text.lower().strip()
    matched_domains = []

    for domain_key, domain in SUNYATA_DOMAINS.items():
        hits = [w for w in domain["triggers"]
                if (re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", t) if w.isascii() else w in t)]
        if hits:
            matched_domains.append({
                "domain":    domain_key,
                "context":   domain["context"],
                "principle": domain["principle"],
                "guidance":  domain["guidance"],
                "matched":   hits,
            })

    if not matched_domains:
        return _empty_result()

    # primary = domain with most hits
    primary = max(matched_domains, key=lambda d: len(d["matched"]))

    return {
        "has_context":      True,
        "primary_domain":   primary["domain"],
        "context":          primary["context"],
        "principle":        primary["principle"],
        "guidance":         primary["guidance"],
        "all_domains":      matched_domains,
        "domain_count":     len(matched_domains),
        "void_principle":   VOID_PRINCIPLES[0],
        "checked_at":       time.time(),
    }


def get_void_guidance(choices_available: int) -> dict:
    """
    สุญยตา applied to choice preservation
    ความว่าง (void) ต้องได้รับการเคารพ — ห้ามปิดพื้นที่นั้น

    FATE™: Choice(t) >= 1 → collapse = False
    """
    try:
        choices_available = float(choices_available)
    except (TypeError, ValueError):
        choices_available = 0
    if choices_available < 1:
        return {
            "void_respected": False,
            "message":        "ความว่างถูกปิด — ทางเลือกเป็นศูนย์ ระบบต้อง restore",
            "action":         "SYSTEM_PAUSE — ต้องเปิดทางเลือกก่อนดำเนินการต่อ",
            "principle":      "Protect the Choice. Respect the Void.",
        }
    return {
        "void_respected": True,
        "choices":        choices_available,
        "message":        f"ความว่างยังอยู่ — มี {choices_available} ทางเลือก",
        "principle":      "Protect the Choice. Respect the Void.",
    }


def cosmic_snapshot() -> dict:
    """dump สำหรับ /api/kernel_snapshot"""
    return {
        "domains":         list(SUNYATA_DOMAINS.keys()),
        "void_principles": VOID_PRINCIPLES,
        "core_law":        "อนิจจัง ทุกขัง อนัตตา",
        "fate_lock":       "Protect the Choice. Respect the Void.",
    }


# ── Helper ────────────────────────────────────────────────────────
def _empty_result() -> dict:
    return {
        "has_context":    False,
        "primary_domain": None,
        "context":        "",
        "principle":      "",
        "guidance":       "",
        "all_domains":    [],
        "domain_count":   0,
        "void_principle": VOID_PRINCIPLES[0],
        "checked_at":     time.time(),
    }


# ── Self-test ─────────────────────────────────────────────────────
def _self_test() -> dict:
    # clinging
    r1 = analyze("ฉันปล่อยไม่ได้เลย ยึดมากเกินไป")
    assert r1["has_context"] is True
    assert r1["primary_domain"] == "clinging"

    # uncertainty
    r2 = analyze("กลัวอนาคตมาก ไม่แน่ใจเลย")
    assert r2["has_context"] is True
    assert r2["primary_domain"] == "uncertainty"

    # no match
    r3 = analyze("วิเคราะห์ตลาดหน่อยได้ไหม")
    assert r3["has_context"] is False
    assert r3["context"] == ""

    # backward compat
    ctx = get_context("ยึดติดมากเลย")
    assert "สุญยตา" in ctx

    # void guidance
    v1 = get_void_guidance(0)
    assert v1["void_respected"] is False

    v2 = get_void_guidance(3)
    assert v2["void_respected"] is True

    # multiple domains
    r4 = analyze("กลัวมาก และยึดติดไม่ได้ปล่อย")
    assert r4["domain_count"] >= 2

    return {"status": "OK", "module": "cosmic_latte"}


if __name__ == "__main__":
    import json
    result = analyze("ยึดติดกับอดีตมาก ปล่อยไม่ได้เลย กลัวอนาคตด้วย")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    print(_self_test())
