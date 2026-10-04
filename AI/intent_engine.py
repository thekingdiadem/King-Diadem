# AI/intent_engine.py — KING DIADEM
# โยนิโสมนสิการ: อ่านเจตนาจากเหตุปัจจัย ไม่ใช่ keyword matching ล้วนๆ
# วิเคราะห์ 3 ชั้น: surface signal → context weight → causal intent

from __future__ import annotations
import re
import math
from typing import Any

from core.thai_signals import NOT_WANT_TO_LIVE, NO_MONEY_ESSENTIAL

_NEG = r"(?<!ไม่)(?<!ไม่ได้)(?<!ไม่ค่อย)(?<!ไม่ค่อยได้)"   # lookbehind ความกว้างคงที่ทีละแบบ

# ── Intent definitions พร้อม causal weight ───────────────────
_INTENTS: list[dict[str, Any]] = [
    {
        "name":    "crisis",
        "weight":  3.0,   # override ทุกอย่าง — safety first
        "patterns": [
            # เฉพาะสัญญาณทำร้ายตัวเอง — เดิมมี "ไม่อยากอยู่" (บ้าน) "หมดแล้วจริงๆ" "ทนไม่ไหวแล้ว"
            r"อยากตาย", NOT_WANT_TO_LIVE.pattern, r"ฆ่าตัว", r"ฆ่าตัวเอง",
            r"จบชีวิต", r"ทำร้ายตัวเอง",
            r"\bsuicid", r"\bwant to die\b", r"\bend it all\b", r"\bkill myself\b",
        ],
    },
    {
        "name":    "survival",
        "weight":  2.0,
        "patterns": [
            r"ตกงาน", NO_MONEY_ESSENTIAL.pattern, r"หนี้ท่วม", r"กินไม่ได้", r"ไล่ออก",
            r"ไม่มีที่อยู่", r"พังหมดเลย", r"หมดทรัพยากร", r"เอาตัวรอดไม่ได้",
            r"\bno money\b", r"\bbankrupt\b", r"\bevicted\b",
        ],
    },
    {
        "name":    "risk",
        "weight":  1.8,
        "patterns": [
            r"เสี่ยงมาก", r"อันตราย", r"ล้มละลาย", r"ขาดทุนหนัก",
            r"ระบบพัง", r"\bcollapse\b", r"วิกฤต", r"ทุกอย่างพัง",
        ],
    },
    {
        "name":    "vega",
        "weight":  1.5,
        "patterns": [
            r"ระยะยาว", r"ภาพใหญ่", r"กลยุทธ์", r"\bstrategic\b",
            r"วิเคราะห์ระบบ", r"5 ปีข้างหน้า", r"ภาพรวม", r"อนาคตของ",
            r"ผลกระทบระบบ", r"เชิงโครงสร้าง",
        ],
    },
    {
        "name":    "civil",
        "weight":  1.2,
        "patterns": [
            r"ธุรกิจ", r"บริษัท", r"ลูกค้า", r"โปรเจกต์", r"เจ้านาย",
            r"ลาออก", r"\bstartup\b", r"\bmarket\b", r"\brevenue\b",
            r"สัญญา(?!ณ)", r"ประชุม", r"งานพรีเซนต์", r"ที่ทำงาน", r"ออฟฟิศ",
        ],
    },
    {
        "name":    "relationship",
        "weight":  1.1,
        "patterns": [
            r"แฟน(?!บอล|คลับ|เพจ|ไซต์|ตาซี|ซี|ๆ|เมด|ชั่น)", r"เลิกกัน", r"ทะเลาะ", r"ครอบครัว",
            r"พ่อแม่", r"ความสัมพันธ์", r"\brelationship\b",
            r"เพื่อน", r"คนรัก",
        ],
    },
    {
        "name":    "question",
        "weight":  0.8,
        "patterns": [
            r"ควรทำยังไง", r"ทำไงดี", r"แนะนำได้ไหม",
            r"คิดว่าอะไรดีกว่า", r"ช่วยแนะนำ", r"\bwhat should\b",
            r"มีทางไหนบ้าง", r"ทำอะไรได้บ้าง",
        ],
    },
    {
        "name":    "joy",
        "weight":  1.0,
        "patterns": [
            _NEG + r"มีความสุข", _NEG + r"ดีใจมาก", _NEG + r"ตื่นเต้น", _NEG + r"สนุกมาก",
            r"เยี่ยมเลย", _NEG + r"ยินดี", r"(?<!un)\bhappy\b", r"\bexcited\b", r"\bwonderful\b", r"\bgreat news\b",
        ],
    },
    {
        "name":    "love",
        "weight":  1.2,   # เจาะจงกว่า relationship/joy — คะแนนใกล้กันให้ love ชนะ
        "patterns": [
            r"แฟนใหม่", r"ตกหลุมรัก", r"ชอบคนนี้", _NEG + r"มีความรู้สึก(?!อะไร)",
            r"สารภาพรัก", r"รักแล้ว", r"\bin love\b", r"\bcrush\b",
            r"\bconfession\b", r"\bdating\b", r"คนที่ชอบ",
        ],
    },
    {
        "name":    "work_win",
        "weight":  1.2,   # "ได้งานแล้ว ดีใจมาก" = work_win ไม่ใช่ joy
        "patterns": [
            # "เสร็จแล้ว" "ผ่านแล้ว" เดี่ยว ติด "กินข้าวเสร็จแล้ว" "รถผ่านแล้ว" → ใช้วลีงาน
            r"ได้งานแล้ว", r"สอบผ่านแล้ว", r"สัมภาษณ์ผ่าน", r"สำเร็จแล้ว", r"ทำสำเร็จ",
            r"ได้เลื่อนตำแหน่ง", r"\bgot the job\b", r"\bmilestone\b",
            r"\blanded (?:the|a) (?:job|deal|client)\b", r"\bgot accepted\b", r"\bachieved\b", r"\bpromotion\b",
        ],
    },
]

# คะแนนเท่ากัน → เลือกตัวที่เจาะจง/ร้ายแรงกว่า (เดิมขึ้นกับลำดับใน dict)
_TIE = {"crisis": 9, "survival": 8, "risk": 7, "work_win": 6, "love": 5, "vega": 4,
        "civil": 3, "relationship": 2, "joy": 1, "question": 0}

# ── Causal amplifiers: คำเหล่านี้เพิ่ม weight ของ intent ที่ match ──
_AMPLIFIERS = {
    "urgency":  (["ด่วน", "ตอนนี้เลย", "วันนี้เลย", "ทันที", r"\burgent\b"], 1.3),
    "emotion":  (["มาก", "สุดๆ", "ไม่ได้แล้ว", "จริงๆ", "เลย"], 1.15),
    "negation": (["ไม่", "ไม่มี", "หมด", "ขาด", "สูญ"], 1.2),
}

# ── Emotional tone fallback ──────────────────────────────────
_EMOTION_WORDS = {
    "heavy":  ["เหนื่อย", "ท้อ", "หมดแรง", "สิ้นหวัง", "หมดหวัง"],
    "stress": ["เครียด", "กังวล", "กลัว", "ตื่นตระหนก", "หนักใจ"],
    "grief":  ["เสียใจ", "ร้องไห้", "เจ็บปวด", "เจ็บใจ", "สูญเสีย"],
}


def _amplify(text: str, base_score: float) -> float:
    """คูณ amplifier ถ้าพบ urgency/emotion/negation"""
    mult = 1.0
    for _label, (words, factor) in _AMPLIFIERS.items():
        for w in words:
            if re.search(w, text):
                mult *= factor
                break  # 1 amplifier type = 1 mult เท่านั้น
    return base_score * mult


def _causal_depth(text: str) -> float:
    """
    วัด "ความลึกเชิงเหตุ" — ประโยคที่มีเหตุ-ผลชัด (เพราะ/จึง/ดังนั้น)
    ให้ confidence boost เล็กน้อย
    """
    causal_markers = [r"เพราะ", r"เนื่องจาก", r"ดังนั้น", r"จึง", r"ทำให้",
                      r"ส่งผล", r"\bbecause\b", r"\btherefore\b", r"\bso that\b"]
    hits = sum(1 for m in causal_markers if re.search(m, text))
    return min(0.15, hits * 0.05)  # +0.05 ต่อ marker สูงสุด +0.15


def analyze_intent(text: str) -> dict:
    """
    โยนิโสมนสิการ — วิเคราะห์เจตนา 3 ชั้น:
      1. Surface: pattern match + weight
      2. Context: amplifier คูณ score
      3. Causal: causal_depth boost confidence

    คืน:
      intent, confidence, signals, root_signal,
      all_scores, causal_depth, amplified
    """
    text = str(text or "")
    if not text:
        return {
            "intent":        "general",
            "confidence":    0.3,
            "signals":       [],
            "root_signal":   None,
            "all_scores":    {},
            "causal_depth":  0.0,
            "amplified":     False,
        }

    t = text.lower().strip()
    raw_scores:  dict[str, float] = {}
    matched_map: dict[str, list[str]] = {}

    # ── ชั้น 1: surface match ────────────────────────────────
    for item in _INTENTS:
        name   = item["name"]
        weight = item["weight"]
        hits: list[str] = []
        for pat in item["patterns"]:
            if re.search(pat, t):
                hits.append(pat)
        if hits:
            raw_scores[name]  = len(hits) * weight
            matched_map[name] = hits

    # ── ชั้น 2: amplify ──────────────────────────────────────
    amplified = False
    amp_scores: dict[str, float] = {}
    for name, score in raw_scores.items():
        new_score = _amplify(t, score)
        amp_scores[name] = new_score
        if new_score != score:
            amplified = True

    # ── ชั้น 3: causal depth ─────────────────────────────────
    causal_boost = _causal_depth(t)

    # ── Emotional fallback ───────────────────────────────────
    if not amp_scores:
        for tone, words in _EMOTION_WORDS.items():
            if any(re.search(w, t) for w in words):
                # เดิม heavy ("เหนื่อย") → crisis และ stress → vega: คนเหนื่อยได้โหมดวิกฤต/วิเคราะห์เย็นๆ
                # อารมณ์ให้ LYLA รับรู้ก่อน (general) — crisis เฉพาะสัญญาณทำร้ายตัวเองข้างบน
                base_intent = "general"
                base_conf   = 0.48 + causal_boost
                return {
                    "intent":       base_intent,
                    "confidence":   round(min(0.75, base_conf), 3),
                    "signals":      [tone + "_emotion"],
                    "root_signal":  tone,
                    "all_scores":   {base_intent: round(base_conf * 10, 2)},
                    "causal_depth": causal_boost,
                    "amplified":    False,
                }
        # ข้อความสั้นหรือไม่มี signal
        if len(t) < 12:
            conf = 0.25
        else:
            conf = 0.38 + causal_boost
        return {
            "intent":       "general",
            "confidence":   round(conf, 3),
            "signals":      [],
            "root_signal":  None,
            "all_scores":   {},
            "causal_depth": causal_boost,
            "amplified":    False,
        }

    # ── เลือก best intent ────────────────────────────────────
    # safety first: สัญญาณทำร้ายตัวเองชนะเสมอ — เดิม "ตกงาน ไม่มีเงิน อยากตาย" ได้ survival
    # เพราะคะแนนสะสมของ survival หลายคำ (2×2) มากกว่า crisis 1 คำ (3)
    if "crisis" in amp_scores:
        best = "crisis"
    else:
        best = max(amp_scores, key=lambda k: (amp_scores[k], _TIE.get(k, 0)))
    best_score = amp_scores[best]
    total      = sum(amp_scores.values()) or 1.0

    # softmax-lite: ป้องกัน overconfidence
    raw_conf   = best_score / total
    conf       = round(min(0.95, raw_conf * (1 + math.log1p(best_score) * 0.05) + causal_boost), 3)
    if best == "crisis":
        conf = max(conf, 0.9)    # สัญญาณทำร้ายตัวเองไม่ใช่เรื่องสัดส่วนคะแนน

    # root signal = pattern แรกของ best intent
    root = matched_map[best][0] if matched_map.get(best) else None

    all_signals = []
    for name, pats in matched_map.items():
        all_signals.extend([name] * len(pats))

    return {
        "intent":      best,
        "confidence":  conf,
        "signals":     sorted(set(matched_map.keys())),
        "root_signal": root,
        "all_scores":  {k: round(v, 2) for k, v in sorted(amp_scores.items(), key=lambda x: -x[1])},
        "causal_depth": causal_boost,
        "amplified":    amplified,
    }
