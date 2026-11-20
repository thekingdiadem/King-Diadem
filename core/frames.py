"""ตัวจับเรื่องอันตรายแบบประกอบชิ้นส่วน (frames) — กฎล้วน ไม่ใช้ AI ผลเหมือนเดิมทุกครั้ง

เดิมตัวจับเป็น regex ทั้งประโยค: ต้องเรียงคำตรงตามที่เขียนไว้ ข้อความใหม่ที่ใช้คำเดิมแต่สลับลำดับหรือมีคำคั่นจึงหลุด
(ชุดปิดตา 2026-11: จับเรื่องอันตรายในข้อความที่ไม่เคยเห็นได้ราวครึ่งเดียว แม้แต่ภาษาไทย)

ที่นี่แยกเป็นสองส่วน:
  · คลังคำ core/frames_lexicon.tsv — แนวคิด (INGEST, CHEMICAL, ...) → คำในแต่ละภาษา (ข้อมูล ไม่ใช่โค้ด)
  · กฎ FRAMES ข้างล่าง — ตารางเดียวใช้ทุกภาษา: เหตุอันตราย = ชิ้นส่วนที่ต้องพบ "ใกล้กันในประโยคเดียว ลำดับไหนก็ได้"
เติมคำหนึ่งคำ → ทุกกฎที่ใช้แนวคิดนั้นได้ผล · เติมกฎหนึ่งข้อ → ได้ผลทุกภาษา

ผลออกมารูปเดียวกับ urgent_intl / world_urgent: [(ชนิด, หัวข้อ)] — kernel_voice.assess ต่อเข้าหัวข้อเดิม
ใช้เสริมตัวจับเดิม ไม่ได้แทน: regex เดิมทั้งหมดยังทำงานอยู่
"""
from __future__ import annotations

import os
import re
from functools import lru_cache

LEXICON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frames_lexicon.tsv")
_WORD_LANGS = {"en", "es", "vi"}           # มีเว้นวรรคระหว่างคำ → ต้องตรงทั้งคำ
# ชิ้นส่วนต้องอยู่ห่างกันไม่เกินนี้ (ตัวอักษร) — กัน "กินข้าวเที่ยงแล้วไปฉีดยาฆ่าหญ้า" ไม่ให้นับเป็นกินยาฆ่าหญ้า
_WINDOW = {"en": 70, "es": 70, "vi": 70}
_WINDOW_DEFAULT = 34                       # th zh ja ko — หนึ่งตัวอักษรเก็บความหมายได้มากกว่า
_SENTENCE = re.compile(r"[.!?。！？\n]+")

# (ชื่อ, ชนิด, หัวข้อ, ทางเลือกของชิ้นส่วนที่ต้องพบครบ, ตัวกันเตือนเกิน)
FRAMES = (
    ("poison", "medical", "health_emergency", (("INGEST", "CHEMICAL"),), ("FICTION", "HYPOTHETICAL", "USE")),
    ("overdose", "medical", "health_emergency", (("INGEST", "MEDICINE", "AMOUNT"),), ("FICTION", "HYPOTHETICAL", "ROUTINE", "REFILL", "COURSE")),
    ("drowning", "medical", "health_emergency", (("DROWN",), ("FALL_INTO", "WATER", "NOT_SURFACE")), ("FICTION", "HYPOTHETICAL", "IDIOM_DROWN")),
    ("choking", "medical", "health_emergency", (("CHOKE",), ("STUCK", "THROAT", "AIRWAY_FAIL")), ("FICTION", "HYPOTHETICAL", "LAUGH", "IDIOM_CHOKE")),
    # รอบ 2 (ชุดปิดตา E ล็อกไว้ก่อนเขียน)
    ("strangle", "violence", "violence", (("STRANGLE",), ("SQUEEZE", "NECK")), ("FICTION", "HYPOTHETICAL", "AFFECTION", "CLOTHING")),
    # แรงงานบังคับต้องมีสัญญาณอันตรายอย่างน้อยสองอย่าง — "บังคับให้ทำงานบ้าน" หรือ "หัวหน้าให้อยู่ดึก" ตามลำพังไม่นับ
    ("forced_labor", "violence", "violence", (("FORCE", "WAGE", "WORK"), ("FORCE", "CONFINE", "WORK"), ("CONFINE", "WAGE", "WORK"), ("CONFINE", "DEBT")),   # ขัง+ทำงานตามลำพังไม่พอ ("แม่ล็อกประตูก่อนออกไปทำงาน")
     ("FICTION", "HYPOTHETICAL", "PAID_OK")),
    ("unconscious", "medical", "health_emergency", (("UNCONSCIOUS",),), ("FICTION", "HYPOTHETICAL", "DEVICE", "NEARLY", "RECOVERED")),
    ("bleeding", "medical", "health_emergency", (("BLOOD", "BLEED_BAD"),), ("FICTION", "HYPOTHETICAL", "MINOR")),
    # รอบ 3 (ชุดปิดตา F ล็อกไว้ก่อนเขียน)
    ("anaphylaxis", "medical", "health_emergency",
     (("ALLERGY", "SWELL", "MOUTH_PART"), ("ALLERGY", "BREATH_HARD"), ("ALLERGY", "HIVES_ALL", "FAINTISH")), ("FICTION", "HYPOTHETICAL", "MINOR")),
    ("burn", "medical", "health_emergency", (("BURN", "BURN_SEVERE"),), ("FICTION", "HYPOTHETICAL", "MINOR", "NOT_BURN")),
    ("electric", "medical", "health_emergency", (("ELECTRIC",), ("SOCKET", "SHOCK")), ("FICTION", "HYPOTHETICAL", "NOT_ELECTRIC", "MINOR")),
    ("bite", "medical", "health_emergency", (("ANIMAL", "BITE", "VICTIM"),), ("FICTION", "HYPOTHETICAL", "NOT_BITE")),
    # รอบ 4 (ชุดปิดตา G ล็อกไว้ก่อนเขียน)
    ("seizure", "medical", "health_emergency", (("SEIZURE",),), ("FICTION", "HYPOTHETICAL", "TWITCH")),
    # เส้นเลือดในสมอง: คำชัดเจน หรืออาการสองอย่างร่วมกัน (หลัก BE-FAST) — อาการเดียวมักมีเหตุอื่น
    ("stroke", "medical", "health_emergency",
     (("STROKE",), ("FACE_DROOP", "SLUR"), ("FACE_DROOP", "WEAK_SIDE"), ("WEAK_SIDE", "SLUR"),
      ("WEAK_SIDE", "SUDDEN"), ("SLUR", "SUDDEN"), ("FACE_DROOP", "SUDDEN")), ("FICTION", "HYPOTHETICAL", "NOT_STROKE")),
    ("head_injury", "medical", "health_emergency", (("FALL", "HEAD", "RED_FLAG"), ("FALL", "HEIGHT", "RED_FLAG")),
     ("FICTION", "HYPOTHETICAL", "MINOR", "NO_PAIN")),
    ("crash", "medical", "health_emergency", (("CRASH", "CRASH_HARM"),), ("FICTION", "HYPOTHETICAL", "MINOR", "NO_PAIN", "DEVICE")),   # ตลาดหุ้น/ระบบ crash ไม่ใช่รถชน
    # รอบ 5 (ชุดปิดตา H ล็อกไว้ก่อนเขียน) — ทุกข้อต้องมีอาการ/สัญญาณอันตรายร่วม คำเดี่ยวอย่าง "แก๊ส" "ร้อน" "เบาหวาน" ไม่พอ
    ("gas_co", "medical", "health_emergency",
     (("CO", "GAS_SYMPTOM"), ("GAS", "LEAK_SMELL", "GAS_SYMPTOM"), ("CLOSED_ROOM", "FUEL_BURN", "GAS_SYMPTOM")), ("FICTION", "HYPOTHETICAL")),
    ("heatstroke", "medical", "health_emergency", (("HEATSTROKE",), ("HOT_BODY", "HEAT_RED")), ("FICTION", "HYPOTHETICAL", "ADVICE")),
    ("hypoglycemia", "medical", "health_emergency", (("DIABETES", "HYPO_SIGN"), ("LOW_SUGAR", "HYPO_SIGN"), ("SUGAR_NUM",)),
     ("FICTION", "HYPOTHETICAL", "SUGAR_OK")),
    ("asthma", "medical", "health_emergency", (("ASTHMA", "ASTHMA_FAIL"), ("WHEEZE", "SHORT_SPEECH"), ("WHEEZE", "ASTHMA_FAIL")),
     ("FICTION", "HYPOTHETICAL", "CONTROLLED")),
    # รอบ 6 (ชุดปิดตา I ล็อกไว้ก่อนเขียน)
    ("cardiac", "medical", "health_emergency", (("HEART_ATTACK", "CARDIAC_SIGN"), ("CHEST_PAIN", "CARDIAC_SIGN")),   # "heart attack" ลำพังมักเป็นสำนวน
     ("FICTION", "HYPOTHETICAL", "CHEST_BENIGN", "MINOR", "NEARLY")),
    ("dehydration", "medical", "health_emergency", (("FLUID_LOSS", "DEHY_SIGN"),), ("FICTION", "HYPOTHETICAL", "BETTER")),   # ไม่ใช้ MINOR: มีคำว่า "ซึม" ซึ่งเป็นอาการขาดน้ำ
    ("trapped", "medical", "health_emergency", (("TRAPPED", "PLACE", "TRAP_DANGER"),), ("FICTION", "HYPOTHETICAL", "TRAFFIC")),
    ("flash_flood", "medical", "health_emergency", (("FLOOD", "FLOOD_DANGER"),), ("FICTION", "HYPOTHETICAL")),
)


@lru_cache(maxsize=1)
def lexicon() -> dict:
    """{แนวคิด: {ภาษา: regex}} — อ่านครั้งเดียวต่อการเปิดเซิร์ฟเวอร์"""
    raw: dict = {}
    with open(LEXICON, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            concept, lang, terms = (line.split("\t") + ["", ""])[:3]
            concept, lang, terms = concept.strip(), lang.strip(), terms.strip()
            if not (concept and lang and terms):
                continue
            if terms.startswith("re:"):
                parts = ["(?:" + terms[3:] + ")"]
            else:
                words = sorted({t.strip() for t in terms.split("|") if t.strip()}, key=len, reverse=True)
                parts = [re.escape(w).replace(r"\ ", r"\s+") for w in words]
                if lang in _WORD_LANGS:
                    parts = [r"(?<![\w'])" + p + r"(?![\w'])" for p in parts]
            raw.setdefault(concept, {}).setdefault(lang, []).extend(parts)
    return {c: {lg: re.compile("|".join(ps), re.I) for lg, ps in by.items()} for c, by in raw.items()}


def _spans(concept: str, sentence: str) -> dict:
    """{ภาษา: [(เริ่ม, จบ)]} ของแนวคิดนี้ในประโยค"""
    out = {}
    for lg, rx in lexicon().get(concept, {}).items():
        hits = [m.span() for m in rx.finditer(sentence) if m.end() > m.start()]
        if hits:
            out[lg] = hits
    return out


def _near(groups: list, window: int) -> bool:
    """มีชุดตำแหน่ง (หนึ่งตำแหน่งต่อชิ้นส่วน) ที่อยู่ในกรอบ window ตัวอักษรหรือไม่ — ลำดับไหนก็ได้"""
    def walk(i, lo, hi):
        if hi - lo > window:
            return False
        if i == len(groups):
            return True
        return any(walk(i + 1, min(lo, s), max(hi, e)) for s, e in groups[i])
    return any(walk(1, s, e) for s, e in groups[0])


def _frame_hit(sentence: str, need: tuple) -> bool:
    found = [_spans(c, sentence) for c in need]
    if not all(found):
        return False
    # ภาษาเดียวกันก่อน (ส่วนใหญ่) แล้วค่อยลองปนภาษา ("กินยาพาราไป 30 tablets")
    langs = set.intersection(*(set(f) for f in found))
    for lg in langs:
        if _near([f[lg] for f in found], _WINDOW.get(lg, _WINDOW_DEFAULT)):
            return True
    merged = [sorted({s for spans in f.values() for s in spans}) for f in found]
    return _near(merged, _WINDOW_DEFAULT)


def frames(text) -> list:
    """เหตุอันตรายที่ประกอบได้ครบในประโยคใดประโยคหนึ่ง → [(ชนิด, หัวข้อ)] ไม่ซ้ำ เรียงตาม FRAMES"""
    t = str(text or "")
    if not t.strip():
        return []
    sentences = [s for s in _SENTENCE.split(t) if s.strip()]
    out = []
    for name, kind, topic, options, blockers in FRAMES:
        for s in sentences:
            if any(_spans(b, s) for b in blockers):
                continue
            if any(_frame_hit(s, need) for need in options):
                if (kind, topic) not in out:
                    out.append((kind, topic))
                break
    return out


def explain(text) -> list:
    """สำหรับคนดูแลระบบ: กฎไหนจับ เพราะเจอชิ้นส่วนอะไร (ไม่ใช้ในคำตอบ)"""
    t = str(text or "")
    rows = []
    for name, _k, _t, options, blockers in FRAMES:
        for s in [x for x in _SENTENCE.split(t) if x.strip()]:
            blocked = [b for b in blockers if _spans(b, s)]
            for need in options:
                if _frame_hit(s, need):
                    rows.append({"frame": name, "sentence": s.strip(), "parts": list(need), "blocked_by": blocked})
    return rows
