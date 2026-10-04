# ENGINE/intent_engine.py
# KING DIADEM — Intent Engine (standalone, ไม่ใช้ intent.py)
# analyze_intent() คืน dict พร้อม intent + confidence จริง
# app.py import: from AI.intent_engine import analyze_intent

from __future__ import annotations
import re


def _hit(k: str, t: str) -> bool:
    # คำอังกฤษต้องตรงทั้งคำ — เดิม "end" ติดใน "friend/spend" (→ collapse 0.90), "war" ติดใน "software"
    if k.isascii():
        return re.search(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])", t) is not None
    return k in t

_PATTERNS: list[tuple[str, list[str], float]] = [
    # (intent, keywords, base_confidence)
    ("collapse_prevention", [
        "พัง","ล้ม","วิกฤต","collapse","หมด","สิ้นหวัง",
        "ไม่มีทางออก","ล่มสลาย","breakdown","end",
    ], 0.90),
    ("survival", [
        "รอด","อยู่รอด","ขาด","survive","หิว","ไม่มีกิน",
        "ฉุกเฉิน","emergency","หลงทาง","lost","อันตราย",
    ], 0.88),
    ("risk_assessment", [
        "เสี่ยง","risk","อันตราย","danger","ประเมิน","assess",
        "โอกาส","probability","ผลกระทบ","impact",
    ], 0.82),
    ("decision_support", [
        "เลือก","ตัดสินใจ","decide","choice","ควรทำ","should i",
        "ดีกว่า","better","เปรียบ","compare","trade-off",
    ], 0.80),
    ("business", [
        "ธุรกิจ","ลงทุน","กำไร","ขาดทุน","business","invest",
        "revenue","profit","market","ตลาด","ลูกค้า",
    ], 0.82),
    ("life_balance", [
        "ชีวิต","สมดุล","ความสุข","life","balance","happiness",
        "ครอบครัว","family","เป้าหมาย","goal","ความหมาย",
    ], 0.75),
    ("world_analysis", [
        "การเมือง","เศรษฐกิจ","โลก","politics","economy","world",
        "สังคม","society","ภัยพิบัติ","disaster","สงคราม","war",
    ], 0.78),
    ("general_governance", [], 0.60),  # fallback
]


def analyze_intent(text: str) -> dict:
    """
    วิเคราะห์ intent จาก text
    return: {"intent": str, "confidence": float, "hits": int}
    """
    if not text:
        return {"intent": "general_governance", "confidence": 0.50, "hits": 0}

    t = str(text).lower()
    best_intent     = "general_governance"
    best_confidence = 0.60
    best_hits       = 0

    for intent, keywords, base_conf in _PATTERNS:
        if not keywords:
            continue
        hits = sum(1 for k in keywords if _hit(k, t))
        if hits == 0:
            continue
        # confidence เพิ่มตาม hits แต่ไม่เกิน 0.98
        confidence = min(0.98, base_conf + (hits - 1) * 0.03)
        if confidence > best_confidence or (confidence == best_confidence and hits > best_hits):
            best_intent     = intent
            best_confidence = confidence
            best_hits       = hits

    return {
        "intent":     best_intent,
        "confidence": round(best_confidence, 2),
        "hits":       best_hits,
    }
