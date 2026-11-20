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
_WINDOW = {"en": 100, "es": 100, "vi": 100}   # เดิม 70: ประโยคสเปนที่เล่ายาว ("dejamos el brasero ... toda la noche ... vomitan") หลุด
_WINDOW_DEFAULT = 44                       # th zh ja ko — หนึ่งตัวอักษรเก็บความหมายได้มากกว่า
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
    ("hypoglycemia", "medical", "health_emergency", (("DIABETES", "HYPO_SIGN"), ("LOW_SUGAR", "HYPO_SIGN"), ("SUGAR_NUM",), ("INSULIN", "SKIPPED_MEAL")),
     ("FICTION", "HYPOTHETICAL", "SUGAR_OK")),
    ("asthma", "medical", "health_emergency", (("ASTHMA", "ASTHMA_FAIL"), ("WHEEZE", "SHORT_SPEECH"), ("WHEEZE", "ASTHMA_FAIL")),
     ("FICTION", "HYPOTHETICAL", "CONTROLLED")),
    # รอบ 6 (ชุดปิดตา I ล็อกไว้ก่อนเขียน)
    ("cardiac", "medical", "health_emergency", (("HEART_ATTACK", "CARDIAC_SIGN"), ("CHEST_PAIN", "CARDIAC_SIGN")),   # "heart attack" ลำพังมักเป็นสำนวน
     ("FICTION", "HYPOTHETICAL", "CHEST_BENIGN", "MINOR", "NEARLY")),
    ("dehydration", "medical", "health_emergency", (("FLUID_LOSS", "DEHY_SIGN"),), ("FICTION", "HYPOTHETICAL", "BETTER")),   # ไม่ใช้ MINOR: มีคำว่า "ซึม" ซึ่งเป็นอาการขาดน้ำ
    ("trapped", "medical", "health_emergency", (("TRAPPED", "PLACE", "TRAP_DANGER"),), ("FICTION", "HYPOTHETICAL", "TRAFFIC")),
    ("flash_flood", "medical", "health_emergency", (("FLOOD", "FLOOD_DANGER"),), ("FICTION", "HYPOTHETICAL")),
    # รอบ 7 (ชุดปิดตา J ล็อกไว้ก่อนเขียน)
    ("pregnancy", "medical", "health_emergency", (("PREGNANT", "PREG_DANGER"),), ("FICTION", "HYPOTHETICAL", "PREG_OK")),
    ("infant_fever", "medical", "health_emergency", (("INFANT", "FEVER", "INFANT_RED"),), ("FICTION", "HYPOTHETICAL", "BETTER")),
    ("deep_wound", "medical", "health_emergency", (("PIERCE", "BLEED_NONSTOP"), ("CUT_DEEP",)), ("FICTION", "HYPOTHETICAL", "MINOR")),
    ("marine_sting", "medical", "health_emergency", (("MARINE", "MARINE_ACT", "MARINE_RED"),), ("FICTION", "HYPOTHETICAL")),
    # รอบ 8 เน้นไต (ชุดปิดตา K ล็อกไว้ก่อนเขียน)
    ("no_urine", "medical", "health_emergency", (("NO_URINE", "URINE_RED"), ("CKD", "NO_URINE")), ("FICTION", "HYPOTHETICAL", "TRAFFIC")),
    ("kidney_infection", "medical", "health_emergency", (("FLANK", "KIDNEY_FEVER"), ("HEMATURIA", "KIDNEY_FEVER")), ("FICTION", "HYPOTHETICAL", "BETTER")),
    ("dialysis", "medical", "health_emergency", (("DIALYSIS", "MISSED"), ("DIALYSIS", "HIGH_K"), ("HIGH_K", "RENAL_RED"), ("CKD", "RENAL_RED")),
     ("FICTION", "HYPOTHETICAL")),
    # รอบ 9 (ชุดปิดตา L ล็อกไว้ก่อนเขียน)
    ("hypothermia", "medical", "health_emergency", (("COLD_BODY", "COLD_RED"),), ("FICTION", "HYPOTHETICAL")),
    ("acute_abdomen", "medical", "health_emergency", (("ABD_PAIN", "ABD_RED"),), ("FICTION", "HYPOTHETICAL", "MINOR", "PERIOD", "BETTER")),
    ("gi_bleed", "medical", "health_emergency", (("VOMIT_BLOOD",), ("TARRY",)), ("FICTION", "HYPOTHETICAL", "IRON")),
    ("meningitis", "medical", "health_emergency", (("FEVER", "STIFF_NECK"), ("FEVER", "PURPURA"), ("FEVER", "MENINGEAL")),
     ("FICTION", "HYPOTHETICAL", "SLEPT_WRONG")),
    # รอบ 10 (ชุดปิดตา M ล็อกไว้ก่อนเขียน)
    ("alcohol_poisoning", "medical", "health_emergency", (("DRUNK", "DRUNK_RED"),), ("FICTION", "HYPOTHETICAL", "MOTION_SICK", "RECOVERED")),
    ("methanol", "medical", "health_emergency", (("BOOTLEG", "VISION"),), ("FICTION", "HYPOTHETICAL")),
    ("drug_overdose", "medical", "health_emergency", (("STREET_DRUG", "OD_RED"),), ("FICTION", "HYPOTHETICAL")),
    ("battery_magnet", "medical", "health_emergency", (("BATT_MAGNET", "SWALLOW"),), ("FICTION", "HYPOTHETICAL")),
    # รอบ 11 (ชุดปิดตา N ล็อกไว้ก่อนเขียน) — คนหาย/หลง/ติดกลางทะเล
    ("missing_child", "medical", "health_emergency", (("CHILD_REF", "VANISHED"),), ("FICTION", "HYPOTHETICAL", "FOUND", "PAST_STORY", "PET")),
    ("dementia_wander", "medical", "health_emergency", (("DEMENTIA", "WANDER"),), ("FICTION", "HYPOTHETICAL", "FOUND", "PAST_STORY")),
    ("lost_wild", "medical", "health_emergency", (("WILD", "LOST_WILD"),), ("FICTION", "HYPOTHETICAL", "DOCU", "FOUND", "PAST_STORY")),
    ("at_sea", "medical", "health_emergency", (("SEA", "SEA_RED"),), ("FICTION", "HYPOTHETICAL", "DOCU", "PAST_STORY", "FIXED", "MINOR")),
    # รอบ 12 (ชุดปิดตา O ล็อกไว้ก่อนเขียน) — ภัยพิบัติที่มีคนติด/อยู่ใกล้ตัว
    ("quake_trapped", "medical", "health_emergency", (("QUAKE", "TRAPPED_UNDER"),), ("FICTION", "HYPOTHETICAL", "DRILL")),
    ("landslide", "medical", "health_emergency", (("SLIDE", "SLIDE_RED"),), ("FICTION", "HYPOTHETICAL", "DRILL")),
    ("wildfire", "medical", "health_emergency", (("WILDFIRE", "FIRE_NEAR"),), ("FICTION", "HYPOTHETICAL", "DRILL", "FAR")),
    ("lightning", "medical", "health_emergency", (("LIGHTNING", "STRUCK_RED"),), ("FICTION", "HYPOTHETICAL", "FAR", "PHOTO")),
    # รอบ 13 (ชุดปิดตา P ล็อกไว้ก่อนเขียน) — ความรุนแรงที่กำลังเกิด/เพิ่งเกิด
    ("weapon_threat", "violence", "violence", (("WEAPON", "THREAT_ACT"), ("KILL_THREAT", "NEAR_ME")), ("FICTION", "HYPOTHETICAL", "COOKING", "TOY", "GUN_HOBBY")),
    ("stalker", "violence", "violence", (("FOLLOWED", "AT_DOOR"),), ("FICTION", "HYPOTHETICAL", "SAME_WAY")),
    ("sexual_assault", "violence", "violence", (("SEX_ASSAULT",),), ("FICTION", "HYPOTHETICAL", "NEWS")),
    ("child_abuse", "violence", "violence", (("KID", "ABUSE_SIGN"),), ("FICTION", "HYPOTHETICAL", "PLAY", "NEWS")),
    # รอบ 14 (ชุดปิดตา Q ล็อกไว้ก่อนเขียน)
    ("hyperglycemia", "medical", "health_emergency", (("SUGAR_HIGH", "HYPER_RED"),), ("FICTION", "HYPOTHETICAL")),
    ("bp_crisis", "medical", "health_emergency", (("BP_HIGH", "BP_RED"),), ("FICTION", "HYPOTHETICAL")),
    ("clot", "medical", "health_emergency", (("LEG_SWELL", "CHEST_BREATH"), ("IMMOBILE", "CHEST_BREATH"), ("LEG_SWELL", "CALF_RED")),
     ("FICTION", "HYPOTHETICAL", "MINOR")),
    ("vision_loss", "medical", "health_emergency", (("SUDDEN", "VISION_LOSS"), ("FLASHES", "FLOATERS_MANY")), ("FICTION", "HYPOTHETICAL")),
    # รอบ 15 (ชุดปิดตา R ล็อกไว้ก่อนเขียน)
    ("newborn", "medical", "health_emergency", (("NEWBORN", "NB_RED"),), ("FICTION", "HYPOTHETICAL")),
    ("postpartum_bleed", "medical", "health_emergency", (("POSTPARTUM", "PP_RED"),), ("FICTION", "HYPOTHETICAL", "NORMAL_PP")),
    ("delirium", "medical", "health_emergency", (("SUDDEN", "CONFUSION"),), ("FICTION", "HYPOTHETICAL", "WAKING")),
    ("eye_injury", "medical", "health_emergency", (("EYE", "EYE_CHEM"), ("EYE", "EYE_TRAUMA")), ("FICTION", "HYPOTHETICAL", "MINOR")),
    # รอบ 16 (ชุดปิดตา S ล็อกไว้ก่อนเขียน) — เรื่องไต: คนโรคไตกินมะเฟือง/สมุนไพรแล้วมีอาการ
    ("kidney_toxin", "medical", "health_emergency", (("KIDNEY_PT", "TOXIN_FOOD", "TOX_RED"),), ("FICTION", "HYPOTHETICAL", "AVOID")),
    ("sepsis", "medical", "health_emergency", (("SEPSIS_FEVER", "SEPSIS_CIRC"),), ("FICTION", "HYPOTHETICAL", "BETTER")),
    ("fracture", "medical", "health_emergency", (("DEFORM",), ("BONE_OUT",), ("LEG_SHORT",)), ("FICTION", "HYPOTHETICAL", "MINOR")),
    ("torsion", "medical", "health_emergency", (("TESTIS", "TESTIS_RED"),), ("FICTION", "HYPOTHETICAL")),
    # รอบ 17 (ชุดปิดตา T ล็อกไว้ก่อนเขียน) — เรื่องไต: กล้ามเนื้อสลาย (ฉี่สีโค้ก) ทำให้ไตวายเฉียบพลัน
    ("rhabdo", "medical", "health_emergency", (("DARK_URINE", "RHABDO_CAUSE"),), ("FICTION", "HYPOTHETICAL")),
    ("ectopic", "medical", "health_emergency", (("PREG_POS", "ONE_SIDE_PAIN"),), ("FICTION", "HYPOTHETICAL", "PREG_OK")),   # "เลือดออกนิดหน่อย" ตอนท้องยังอันตราย ไม่ใช้ MINOR
    ("spinal", "medical", "health_emergency", (("SPINE_EVENT", "NO_LEGS"),), ("FICTION", "HYPOTHETICAL")),
    ("amputation", "medical", "health_emergency", (("SEVERED",),), ("FICTION", "HYPOTHETICAL", "NEWS")),
    # รอบ 18 (ชุดปิดตา U ล็อกไว้ก่อนเขียน) — เรื่องไต: เส้นฟอกไตแตก/เลือดไม่หยุด/อุดตัน
    ("fistula", "medical", "health_emergency", (("FISTULA", "FIST_RED"),), ("FICTION", "HYPOTHETICAL", "FIST_OK")),
    ("dissection", "medical", "health_emergency", (("TEAR_PAIN", "CHEST_BACK"),), ("FICTION", "HYPOTHETICAL")),
    ("bowel_obstruction", "medical", "health_emergency", (("NO_GAS", "OBST_RED"), ("GREEN_VOMIT",)), ("FICTION", "HYPOTHETICAL", "BETTER")),
    ("bee_swarm", "medical", "health_emergency", (("MANY_STINGS",),), ("FICTION", "HYPOTHETICAL", "NEWS")),
    # รอบ 19 (ชุดปิดตา V ล็อกไว้ก่อนเขียน) — เรื่องไต 2 ข้อ: ปลูกถ่ายไต · ล้างไตทางหน้าท้อง
    ("transplant", "medical", "health_emergency", (("TRANSPLANT", "TX_RED"), ("TRANSPLANT", "MISSED_MEDS")), ("FICTION", "HYPOTHETICAL", "TX_OK")),
    ("pd_peritonitis", "medical", "health_emergency", (("PD", "PD_RED"),), ("FICTION", "HYPOTHETICAL", "PD_OK")),
    ("hyperemesis", "medical", "health_emergency", (("PREGNANT", "HYPEREMESIS"),), ("FICTION", "HYPOTHETICAL")),
    ("food_poisoning", "medical", "health_emergency", (("MANY_PEOPLE", "GI_SICK"), ("RICE_WATER",)), ("FICTION", "HYPOTHETICAL", "NEWS")),
    # รอบ 20 (ชุดปิดตา W ล็อกไว้ก่อนเขียน) — เรื่องไต: เด็กไตอักเสบหลังเจ็บคอ
    ("child_nephritis", "medical", "health_emergency", (("PUFFY_EYES", "URINE_CHANGE"), ("NEPHRITIS", "NEPH_RED")), ("FICTION", "HYPOTHETICAL", "CRIED")),
    ("kawasaki", "medical", "health_emergency", (("FEVER_DAYS", "KAWA_SIGN"),), ("FICTION", "HYPOTHETICAL", "BETTER")),
    ("nosebleed", "medical", "health_emergency", (("NOSEBLEED", "NB_BAD"),), ("FICTION", "HYPOTHETICAL", "NB_STOPPED", "MINOR")),
    ("dental_spread", "medical", "health_emergency", (("TOOTH", "SPREAD_RED"),), ("FICTION", "HYPOTHETICAL")),
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


_KANA = re.compile(r"[\u3040-\u30ff]")


def _blocked(concept: str, sentence: str) -> bool:
    """ตัวกันเตือนเกินในประโยคนี้ — ประโยคญี่ปุ่น (มีคานะ) ไม่ใช้คำจีน: "作業員" ไม่ใช่ "作业" (การบ้าน)"""
    found = _spans(concept, sentence)
    if _KANA.search(sentence):
        found.pop("zh", None)
    return bool(found)


def frames(text) -> list:
    """เหตุอันตรายที่ประกอบได้ครบในประโยคใดประโยคหนึ่ง → [(ชนิด, หัวข้อ)] ไม่ซ้ำ เรียงตาม FRAMES"""
    t = str(text or "")
    if not t.strip():
        return []
    sentences = [s for s in _SENTENCE.split(t) if s.strip()]
    out = []
    for name, kind, topic, options, blockers in FRAMES:
        for s in sentences:
            if any(_blocked(b, s) for b in blockers):
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
            blocked = [b for b in blockers if _blocked(b, s)]
            for need in options:
                if _frame_hit(s, need):
                    rows.append({"frame": name, "sentence": s.strip(), "parts": list(need), "blocked_by": blocked})
    return rows
