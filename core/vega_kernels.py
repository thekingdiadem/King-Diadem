"""
core/vega_kernels.py — VEGA Human DriftZero Kernel (14 Gates)

VEGA = Human Kernel: กันคนคนหนึ่งไม่ให้ไหลจาก "เบี้ยวนิดเดียว" ไปจนพัง และทำให้การตัดสินใจยังรอดได้ตอนเครียด
    REALITY + EVIDENCE + EXIT = SURVIVABLE CHOICE
Operator stance: Ego OFF · Panic OFF · Evidence ON · Floor Protection ON
เป้าหมายหลัก: คืนทางเลือกที่ปลอดภัยจริงอย่างน้อย 1 ทาง

ทำงานแบบดีเทอร์มินิสติก — อ่านสัญญาณ "ศัตรู" ของแต่ละ kernel จากข้อความ แล้วคืนประตูที่ติด
พร้อมคำถามของประตูนั้น (ไม่ตัดสินแทนคน · ไม่ใช้ AI · input เดิม = ผลเดิม)
ใช้โดย /run เมื่อเสียงเป็น VEGA: แนบเป็นบริบทให้ LLM และแสดงในรายละเอียดคำตอบ
"""

from __future__ import annotations

import re

# ลำดับความสำคัญเมื่อมีหลายประตูติดพร้อมกัน: อันตรายที่กำลังเกิด → พื้นรอด → ทางออก → ที่เหลือ
_PRIORITY = ("K13", "K2", "K4", "K5", "K7", "K1", "K12", "K10", "K8", "K11", "K6", "K3", "K9", "K14")
MAX_GATES = 3

# (id, ชื่อ, ศัตรู, กฎ, คำถาม, สัญญาณ)
KERNELS = [
    ("K1", "Reality Root", "denial, fantasy, avoidance", "Reality first, always.",
     "ตอนนี้อะไรคือความจริงบ้าง — ตัวเลข วันที่ และสิ่งที่เกิดขึ้นแล้ว",
     r"เดี๋ยวก็ดีเอง|เดี๋ยวก็ผ่านไป|ไม่เป็นไรหรอก|คงไม่เป็นไร|ไม่อยากรู้|ไม่อยากคิด|ไม่กล้าดู|ไม่กล้าเปิด|"
     r"ช่างมันเถอะ|ทำเป็นไม่เห็น|ปล่อยไว้ก่อน|it'?ll be fine|don'?t want to (?:know|look|think)"),
    ("K2", "Downside-First Gate", "upside addiction", "Check worst-case before best-case.",
     "ถ้าพลาดแบบแย่ที่สุด อะไรจะพังพื้นที่ทำให้อยู่รอด",
     r"รวยเร็ว|ผลตอบแทนสูง|การันตีกำไร|กำไรแน่|เทหมดหน้าตัก|หมดหน้าตัก|(?<![a-z])all[- ]?in(?![a-z])|ทุ่มหมด|ลงทุนทั้งหมด|"
     # ไม่นับเมื่อติดกับตัวอักษรอังกฤษ: "small investment" เคยติด all-in (sm-all in-vestment)
     
     r"เงินทั้งหมด|เอาเงินเก็บทั้งหมด|รวยแน่|(?<![a-z])x\s?[2-9](?!\d)|เท่าตัว|get rich|guaranteed (?:return|profit)"),
    ("K3", "Simplicity Cut", "complexity as ego", "If you can't explain in 2 minutes, cut.",
     "กรอบที่ง่ายที่สุดและจริงที่สุดของเรื่องนี้คืออะไร — เล่าใน 2 ประโยคได้ไหม",
     r"ซับซ้อนมาก|ยุ่งเหยิง|หลายทางเกินไป|งงไปหมด|ไม่รู้จะเริ่มตรงไหน|too complicated|overwhelm"),
    ("K4", "Floor Before Growth", "optimizing while bleeding", "Stabilize before improve.",
     "ตอนนี้พื้นที่ทำให้อยู่รอด (เงินกินอยู่ ที่พัก สุขภาพ) ยังมั่นคงไหม — ถ้ายัง ทำให้มั่นคงก่อนค่อยโต",
     None),   # ติดเมื่อมีทั้ง "พื้นพัง" และ "อยากโต" ในข้อความเดียว — ดู _floor_vs_growth
    ("K5", "Exit Must Exist", "trapped systems", "No plan without a safe exit.",
     "ถ้าทางนี้ไม่เวิร์ก จะถอยออกมาแบบยังอยู่รอดได้อย่างไร",
     r"ลาออก|เซ็นสัญญา|ค้ำประกัน|กู้(?:เงิน|นอกระบบ|มา)|จำนอง|ขายบ้าน|ขายที่|ย้ายไป(?:ต่างประเทศ|อยู่)|"
     r"แต่งงาน|หย่า|ลงขัน|เปิดร้าน|ผ่อน(?:บ้าน|รถ)|quit (?:my )?job|sign (?:the )?contract|co-?sign|take (?:a|out a) loan"),
    ("K6", "Repair Protocol", "normalized damage", "Repair harm, don't normalize it.",
     "อะไรที่เสียหายอยู่และต้องซ่อมก่อน ก่อนจะขยายต่อ",
     r"ชินแล้ว|เป็นแบบนี้มาตลอด|เป็นแบบนี้ประจำ|ทนมานาน|ทนได้อยู่|เรื่องปกติ(?:แหละ|น่ะ)|ทุกคนก็เป็น|used to it"),
    ("K7", "Patience Shell", "escalation, reactive anger", "Calm prevents irreversible moves.",
     "รอ 24 ชั่วโมงก่อนตัดสินใจได้ไหม",
     r"โกรธมาก|โมโห|แค้น|เอาคืน|ทนไม่ไหวแล้ว|ต้องเดี๋ยวนี้|ต้องทำทันที|คืนนี้เลย|"
     r"so angry|furious|right now|immediately|revenge"),
    ("K8", "Equanimity Mirror", "bias, emotional tilt", "Do not govern by mood.",
     "ตอนนี้อารมณ์กำลังบิดภาพอยู่ไหม — ถ้าใจสงบกว่านี้จะเห็นต่างไปไหม",
     r"เครียดมาก|ร้องไห้|เสียใจมาก|กลัวมาก|แพนิค|panic|ใจสั่น|นอนไม่หลับ|สติแตก|คิดไม่ออก|overwhelmed|can'?t think"),
    ("K9", "Generosity Flow", "hoarding, greed drift", "Systems that hoard collapse.",
     "มีอะไรที่ต้องแบ่งหรือส่งต่อ ระบบนี้ถึงจะอยู่รอดได้",
     r"ไม่แบ่ง(?:ใคร)?|เก็บไว้คนเดียว|ไม่ให้ใคร|กินรวบ|ฮุบ|กักตุน|hoard"),
    ("K10", "Integrity Rail", "self-dealing corruption", "Personal benefit triggers recusal.",
     "ใครได้ประโยชน์ส่วนตัวจากการตัดสินใจนี้ — ถ้าเป็นเราเอง ให้คนอื่นร่วมตัดสิน",
     r"เงินบริษัท|เงินส่วนกลาง|เงินกองกลาง|เบิกเกิน|เบิกเงิน.*ส่วนตัว|ผลประโยชน์ทับซ้อน|เส้นสาย|ใต้โต๊ะ|"
     r"ให้ญาติ|ให้แฟนได้งาน|เอาไปใช้ส่วนตัว|kickback|conflict of interest"),
    ("K11", "Stability First", "noise + impulse optimization", "Silence restores clarity.",
     "ถ้าวันนี้ยังไม่ทำอะไรเลย จะเกิดอะไรขึ้น",
     r"ต้องทำอะไรสักอย่าง|อยู่เฉยไม่ได้|ทนนิ่งไม่ได้|อยากเปลี่ยนทุกอย่าง|รื้อใหม่หมด|เปลี่ยนแผนอีกแล้ว|must do something"),
    ("K12", "Evidence Insight", "wrong view persistence", "Truth dissolves delusion by evidence.",
     "หลักฐานแบบไหนที่จะทำให้เปลี่ยนใจได้",
     r"แน่นอน100|มั่นใจ\s?100|ต้องใช่แน่|ไม่มีทางผิด|รู้อยู่แล้วว่า|ใครพูดก็ไม่ฟัง|100%\s?(?:sure|แน่)|definitely right|i know (?:i'?m|it'?s) right"),
    ("K13", "Stop-the-Line Authority", "harm already moving", "Any operator may halt.",
     "ควรหยุดตอนนี้เลยไหม ก่อนความเสียหายลามไปมากกว่านี้",
     r"โอนไปแล้ว|โดนหลอก|ถูกหลอก|กำลังโดนโกง|โดนโกง|เสียเงินไปเรื่อยๆ|ขาดทุนต่อเนื่อง|หนี้เพิ่มทุกเดือน|"
     r"ดอกเบี้ยทบ|กำลังลามไป|ยังไม่หยุด|เติมเงินอีก|ให้โอนเพิ่ม|losing money every|getting scammed|still bleeding"),
    ("K14", "Humble Operator Stance", "win-at-all-cost mindset", "Not built to win. Built to reduce collapse.",
     "ตอนนี้เรากำลังพยายามอยู่รอด หรือพยายามเอาชนะ",
     r"เอาชนะให้ได้|ต้องชนะ|ให้มันรู้|แก้แค้น|ขยี้|ทำให้มันพัง|ให้มันเจ็บ|ต้องเหนือกว่า|crush (?:them|him|her)|destroy (?:them|him|her)|win at all cost"),
]

_FLOOR_BROKEN = re.compile(r"หนี้|ไม่มีเงิน|เงินไม่พอ|ค่าเช่า|ค่าไฟ|ไม่มีจะกิน|ตกงาน|ถูกไล่ออก|ป่วย|ไม่มีที่อยู่|"
                           r"broke|can'?t pay|no money|lost my job|in debt", re.I)
_GROWTH = re.compile(r"ขยาย(?:ร้าน|ธุรกิจ|สาขา)|ลงทุน|เปิด(?:ร้าน|สาขา)|ซื้อเพิ่ม|อัปเกรด|เทรด|คริปโต|crypto|invest|expand|scale up", re.I)

# คำถามภาษาอังกฤษ — คำตอบแบบไม่มี AI ของผู้ใช้ภาษาอื่นเป็นภาษาอังกฤษ (เดิมได้คำถามภาษาไทยต่อท้าย)
ASK_EN = {
    "K1": "What is actually true right now — the numbers, the dates, what has already happened?",
    "K2": "If this goes as badly as it can, what would break the floor you need to survive?",
    "K3": "What is the simplest true version of this — can you say it in two sentences?",
    "K4": "Is your floor (food money, housing, health) stable right now? If not, stabilize it before you grow.",
    "K5": "If this doesn't work, how do you step back out and still be okay?",
    "K6": "What is already damaged and needs repair before you build further?",
    "K7": "Can you wait 24 hours before you decide?",
    "K8": "Is your mood bending the picture right now — would a calmer you see it differently?",
    "K9": "What needs to be shared or passed on for this to keep working?",
    "K10": "Who benefits personally from this decision? If it's you, let someone else decide with you.",
    "K11": "What happens if you do nothing today?",
    "K12": "What evidence would change your mind?",
    "K13": "Should you stop right now, before the damage spreads further?",
    "K14": "Are you trying to survive this, or trying to win?",
}

_COMPILED = {k[0]: (re.compile(k[5], re.I) if k[5] else None) for k in KERNELS}
_BY_ID = {k[0]: k for k in KERNELS}

# Human SOP — ขั้นตอนพื้นฐาน 8 ข้อ (ใช้ในคำตอบแบบไม่มี AI และใน system prompt ของ VEGA)
WORKFLOW = (
    "เขียนการตัดสินใจให้ชัด", "ดูด้านเสียก่อน", "ปกป้องพื้นที่ทำให้รอด", "ต้องมีทางออก",
    "ขอหลักฐาน", "หยุดถ้าความเสียหายกำลังเคลื่อน", "ทำให้มั่นคงก่อน แล้วค่อยปรับให้ดีขึ้น", "ทบทวนหลังตัดสินใจ",
)


def _floor_vs_growth(text: str) -> bool:
    return bool(_FLOOR_BROKEN.search(text) and _GROWTH.search(text))


def evaluate(text: str, limit: int = MAX_GATES, lang: str = "th") -> list[dict]:
    """ประตูที่ติด (เรียงตามความสำคัญ ไม่เกิน limit) — แต่ละอัน: id, name, enemy, rule, ask
    lang ≠ "th" → ask เป็นภาษาอังกฤษ"""
    t = str(text or "")[:4000]
    if not t.strip():
        return []
    hit = set()
    for kid, rx in _COMPILED.items():
        if rx is not None and rx.search(t):
            hit.add(kid)
    if _floor_vs_growth(t):
        hit.add("K4")
    out = []
    for kid in _PRIORITY:
        if kid in hit:
            k = _BY_ID[kid]
            out.append({"id": k[0], "name": k[1], "enemy": k[2], "rule": k[3],
                        "ask": k[4] if lang == "th" else ASK_EN[k[0]]})
        if len(out) >= max(0, int(limit)):
            break
    return out


def llm_hint(gates: list[dict]) -> str:
    """บริบทแนบให้ LLM — ให้ VEGA ถามคำถามของประตูที่ติด แทนการตอบลอยๆ"""
    if not gates:
        return ""
    parts = "; ".join(f"{g['id']} {g['name']}: {g['ask']}" for g in gates)
    return ("[VEGA 14 GATES — ประตูที่ติด: " + parts +
            " · ใช้คำถามเหล่านี้ (ไม่เกิน 2 ข้อ) ช่วยผู้ใช้มองให้ชัด · ไม่ตัดสินแทน · คืนทางเลือกที่ปลอดภัย ≥ 1]")


def offline_lines(gates: list[dict], vega: bool = True, lang: str = "th") -> str:
    """ส่วนท้ายคำตอบแบบไม่มี AI: คำถามของประตูที่สำคัญที่สุด 2 ข้อ (ภาษาเดียวกับคำตอบ)"""
    if not gates:
        return ""
    qs = [f"{g['id']} · {g['ask']}" for g in gates[:2]]
    if lang != "th":
        return "Before you decide, ask yourself:\n" + "\n".join("· " + q for q in qs)
    return "ก่อนตัดสินใจ ลองตอบตัวเองก่อน" + ("ครับ" if vega else "ค่ะ") + "\n" + "\n".join("· " + q for q in qs)
