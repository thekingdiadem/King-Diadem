"""สะท้อนความจริงให้ผู้ใช้เห็นเอง — ไม่บอกให้ "ตั้งสติ"

เจ้าของโปรเจกต์: คำว่า "ตั้งสติดีๆ" ไม่ใช่ตัวแปรที่ทำให้คนตื่น ไม่ว่าจะพูดแรงหรือเบา
แต่ถ้าแยกให้เขาเห็นความจริง เขาจะมีสติเองโดยไม่ต้องบอก

ที่นี่เอาประโยคของผู้ใช้เองมาแยกเป็นกอง (กฎล้วน ไม่ใช้ AI):
  · เกิดขึ้นแล้ว — สิ่งที่เป็นจริงตอนนี้ แก้ได้หรือรับมือได้
  · ยังไม่เกิด — สิ่งที่กลัวว่าจะเกิด (ความคิด ไม่ใช่เหตุการณ์)
  · อยากมี อยากเป็น (ภวตัณหา) · ไม่อยากมี ไม่อยากเป็น (วิภวตัณหา)
แล้วปิดด้วยหลักว่าเลือกทางไหนก็ไม่ผิด แต่ทางที่เลือกจะเป็นเหตุใหม่

ใช้เฉพาะเมื่อข้อความมีอย่างน้อยสองกอง และหนึ่งในนั้นเป็น "กลัว" หรือ "อยาก/ไม่อยาก"
ไม่ใช้กับเรื่องวิกฤตหรือเรื่องด่วน — ตอนนั้นขั้นตอนความปลอดภัยต้องมาก่อน
"""
from __future__ import annotations

import re

_SPLIT = re.compile(r"\s*(?:[,.!?;\n]+|\s(?:แต่|แล้วก็|และ|เลย|ส่วน)\s|\b(?:but|and|so)\b)\s*", re.I)

# ลำดับสำคัญ: ไม่อยาก ก่อน อยาก · กลัว ก่อน เกิดแล้ว
_WANT_NOT = re.compile(r"ไม่อยาก(?:เป็น|มี|ให้|ไป|ทำ|กลับ|เจอ|อยู่ใน|ทน|รับ)|อยาก(?:หนี|เลิก|ออกจาก|ลาออก|ทิ้ง|หยุด)|"
                       r"\bdon'?t\s+want\s+to\s+(?:be|have|go|do|see|stay|deal)|\bwant\s+to\s+(?:quit|escape|leave|run\s+away|stop)\b", re.I)
_WANT_BE = re.compile(r"อยาก(?:มี|ได้|เป็น|ให้|กลับไป|ทำ|รวย|สำเร็จ)|หวังว่า|ฝันว่าจะ|"
                      r"\bi\s+(?:want|wish|hope)\s+(?:to\s+(?:be|have|get|become|make)|i\s+(?:had|could|was|were))\b|\bi\s+just\s+want\b", re.I)
_FEAR = re.compile(r"กลัว|กังวล|ห่วงว่า|ถ้า\S*\s?\S*จะ|คง(?:จะ)?ต้อง|คงไม่|อาจ(?:จะ)?|เดี๋ยว\S*จะ|ไม่รู้จะ|จะ(?:โดน|ถูก|ไม่มี|ต้อง|เสีย|พัง|ไม่ได้)|"
                   r"\b(?:afraid|scared|worried|worry|what\s+if|might|going\s+to\s+lose|will\s+(?:lose|fail|never)|probably\s+(?:will|won'?t))\b", re.I)
_FACT = re.compile(r"แล้ว|ค้าง|โดน|ถูก|เมื่อวาน|ตอนนี้|เพิ่ง|เมื่อ|ทุกวัน|\d|ไม่ได้\S*มา|หมด|เสีย(?:ไป)?|"
                   r"\b(?:got|was|were|lost|fired|owe|haven'?t|didn'?t|have\s+been|already|today|yesterday|now)\b", re.I)

_TH = re.compile(r"[฀-๿]")
_MIN_LEN = 25


def _clean(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip(" ·-—\"'“”")
    return s[:70] + ("…" if len(s) > 70 else "")


def split_truth(text: str) -> dict:
    """{กอง: [ท่อนประโยคของผู้ใช้]} — ท่อนหนึ่งอยู่กองเดียว"""
    piles = {"fact": [], "fear": [], "want_be": [], "want_not": []}
    t = str(text or "")
    parts = _SPLIT.split(t)
    if _TH.search(t):        # ภาษาไทยเว้นวรรคระหว่างวลี ไม่ใช่ระหว่างคำ — ช่องว่างคือรอยต่อของท่อน
        parts = [q for p in parts for q in re.split(r"\s+", p)]
    for part in parts:
        p = _clean(part)
        if len(p) < 4:
            continue
        if _WANT_NOT.search(p):
            piles["want_not"].append(p)
        elif _WANT_BE.search(p):
            piles["want_be"].append(p)
        elif _FEAR.search(p):
            piles["fear"].append(p)
        elif _FACT.search(p):
            piles["fact"].append(p)
    return piles


def applies(text: str, piles: dict | None = None) -> bool:
    if len(str(text or "")) < _MIN_LEN:
        return False
    piles = piles or split_truth(text)
    filled = [k for k, v in piles.items() if v]
    return len(filled) >= 2 and any(k in filled for k in ("fear", "want_be", "want_not"))


_LABELS = {
    "th": {"head": "ลองดูสิ่งที่คุณเล่า แยกเป็นกองๆ นะ",
           "fact": "เกิดขึ้นแล้ว", "fear": "ยังไม่เกิด — เป็นสิ่งที่กลัว", "want_be": "อยากมี อยากเป็น", "want_not": "ไม่อยากมี ไม่อยากเป็น",
           "tail": "เลือกเอาหรือเลือกวาง ไม่มีทางไหนผิด — แต่ทางที่เลือกวันนี้จะเป็นเหตุของวันพรุ่งนี้ "
                   "กองแรกคือสิ่งที่จับต้องได้จริง ส่วนกองที่สองยังเป็นแค่ความคิด"},
    "en": {"head": "Here's what you wrote, sorted into piles",
           "fact": "Already happened", "fear": "Hasn't happened — it's a fear", "want_be": "Wanting to have / to be", "want_not": "Not wanting to have / to be",
           "tail": "Holding on or letting go — neither is wrong. Whatever you choose today becomes a cause for tomorrow. "
                   "The first pile is what's real and workable; the second is still only a thought."},
}


def block(text: str) -> str | None:
    """ข้อความที่จะแทรกในคำตอบ — ไม่เข้าเงื่อนไขคืน None"""
    piles = split_truth(text)
    if not applies(text, piles):
        return None
    lg = "th" if _TH.search(text) else "en"
    L = _LABELS[lg]
    lines = [L["head"]]
    for k in ("fact", "fear", "want_be", "want_not"):
        for p in piles[k][:2]:
            lines.append(f"· {L[k]}: “{p}”")
    lines.append(L["tail"])
    return "\n".join(lines)
