# ============================================================
# ENGINE/paticcasamuppada_engine.py
# UDOK v2.0 — Universal Dependent Origination Kernel
# ตรรกะ: ตัดที่เวทนา→ตัณหา ก่อนสร้างตัวตน
# ไม่ใช่ศาสนา — คือ Causal Operating System
# ============================================================

# ── 12 ปัจจัย (ลำดับจริงตามพระไตรปิฎก) ──────────────────
CHAIN_12 = [
    "ignorance",       # 1 อวิชชา
    "formations",      # 2 สังขาร
    "consciousness",   # 3 วิญญาณ
    "name_form",       # 4 นามรูป
    "sense_bases",     # 5 สฬายตนะ
    "contact",         # 6 ผัสสะ
    "feeling",         # 7 เวทนา  ← PRIMARY KILL ZONE
    "craving",         # 8 ตัณหา  ← ถ้าข้ามได้ วงจรดับ
    "clinging",        # 9 อุปาทาน
    "becoming",        # 10 ภพ
    "birth",           # 11 ชาติ
    "decay_suffering"  # 12 ชรา-มรณะ
]

# ── Feeling tone (เวทนา 3 แบบ) ────────────────────────────
FEELING_TONE = {
    "pleasant":   {"craving_risk": 0.85, "direction": "toward"},
    "unpleasant": {"craving_risk": 0.90, "direction": "away"},
    "neutral":    {"craving_risk": 0.20, "direction": "none"},
}

# ── Keyword → root cause + feeling tone ───────────────────
ROOT_MAP = {
    "ignorance":       {
        "keywords": ["ไม่รู้", "ไม่เข้าใจ", "ไม่ชัด", "งง", "ignorance", "unclear"],
        "feeling": "unpleasant", "intensity_weight": 0.8
    },
    "fear":            {
        "keywords": ["กลัว", "fear", "panic", "ตื่นตระหนก", "วิตก"],
        "feeling": "unpleasant", "intensity_weight": 1.1
    },
    "craving":         {
        # "หิว" เอาออก: ความหิวคือความต้องการเพื่อรอด ไม่ใช่ตัณหา (เดิมทำให้คนหิวถูกสั่ง "หยุดก่อน")
        "keywords": ["อยาก", "ต้องการ", "desire", "want", "โลภ"],
        "feeling": "pleasant", "intensity_weight": 1.0
    },
    "clinging":        {
        # "ติด" เดี่ยวๆ ไปติดใน "ติดต่อ" "ติดตาม" — ใช้คำเต็ม
        "keywords": ["ยึด", "ปล่อยไม่ได้", "cling", "ยึดติด", "ติดใจ", "ติดกับ", "เกาะ"],
        "feeling": "unpleasant", "intensity_weight": 1.2
    },
    "aversion":        {
        "keywords": ["เกลียด", "โกรธ", "hate", "anger", "รำคาญ", "reject"],
        "feeling": "unpleasant", "intensity_weight": 1.15
    },
    "bias":            {
        "keywords": ["ลำเอียง", "bias", "อคติ", "prejudice"],
        "feeling": "neutral", "intensity_weight": 0.7
    },
    "misinformation":  {
        # "ผิด" เดี่ยวๆ ไปติดใน "รับผิดชอบ" "ผิดหวัง" — ใช้คำเต็ม
        "keywords": ["ข้อมูลผิด", "ข่าวปลอม", "fake", "misinformation", "หลอก"],
        "feeling": "unpleasant", "intensity_weight": 0.9
    },
}


import re

# อยาก + รู้/ถาม/ทราบ = ความใคร่รู้ ไม่ใช่ตัณหา
# และคำปฏิเสธของความอยาก ("ไม่อยากได้", "ไม่ต้องการ") ไม่ใช่ตัณหา
_CURIOUS = ("อยากรู้", "อยากถาม", "อยากทราบ", "อยากเข้าใจ", "อยากปรึกษา",
            "ไม่อยากได้", "ไม่ต้องการ", "don't want", "do not want")

# ไม่พบสัญญาณใดเลย = อทุกขมสุขเวทนา (neutral) — เดิมเดาเป็น unpleasant (craving 0.90)
# ทำให้แทบทุกข้อความได้ "หยุดก่อน — ยังมีตัณหาหรืออวิชชา" และถูกส่งไปเส้นทาง risk
_NO_SIGNAL = {"root": "ignorance", "feeling": "neutral", "intensity_weight": 0.5, "evidence": False}


def _f(v, d):
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def _hit(k: str, text: str) -> bool:
    if k.isascii():
        return re.search(r"(?<![a-z])" + re.escape(k) + r"(?![a-z])", text) is not None
    return k in text


# ── ตรวจ root cause จาก text ──────────────────────────────
def detect_root_cause(context: str) -> dict:
    if not context:
        return dict(_NO_SIGNAL)

    text = str(context).lower()
    for c in _CURIOUS:
        text = text.replace(c, " ")
    scores = {}
    for root, meta in ROOT_MAP.items():
        hit = sum(1 for k in meta["keywords"] if _hit(k, text))
        if hit:
            scores[root] = hit * meta["intensity_weight"]

    if not scores:
        return dict(_NO_SIGNAL)

    best = max(scores, key=scores.get)
    meta = ROOT_MAP[best]
    return {
        "root":             best,
        "feeling":          meta["feeling"],
        "intensity_weight": meta["intensity_weight"],
        "score":            round(scores[best], 3),
    }


# ── วิเคราะห์ KILL ZONE (เวทนา→ตัณหา) ─────────────────────
def analyze_kill_zone(feeling_tone: str, pattern: dict) -> dict:
    """
    PRIMARY KILL ZONE:
    ถ้าเวทนาเกิดแล้วไม่ถูกแปลงเป็นตัณหา → วงจรดับ
    ถ้าตัณหาเกิดแล้ว → clinging, becoming, suffering
    """
    tone_meta     = FEELING_TONE.get(feeling_tone, FEELING_TONE["unpleasant"])
    craving_risk  = tone_meta["craving_risk"]

    # entropy สูง = ความไม่รู้ชัด = risk สูงขึ้น
    entropy   = _f(pattern.get("entropy"),   40)
    stability = _f(pattern.get("stability"), 60)
    resource  = _f(pattern.get("resource"),  70)

    # ปรับ risk ตาม context
    context_factor = (entropy / 100) * (1 - stability / 100)
    adjusted_risk  = round(min(1.0, craving_risk + context_factor * 0.3), 3)

    # chain จะขาดที่ไหน?
    if adjusted_risk < 0.35:
        cut_point  = "feeling"          # ตัดได้ที่เวทนา — วงจรดับสนิท
        propagates = False
        outcome    = "chain_cut"
    elif adjusted_risk < 0.65:
        cut_point  = "craving"          # ตัณหาเกิดแต่อุปาทานยังไม่แน่น
        propagates = True
        outcome    = "chain_partial"
    else:
        cut_point  = None               # วงจรวิ่งเต็ม
        propagates = True
        outcome    = "chain_full"

    return {
        "feeling_tone":   feeling_tone,
        "craving_risk":   adjusted_risk,
        "cut_point":      cut_point,
        "propagates":     propagates,
        "outcome":        outcome,
        "direction":      tone_meta["direction"],
    }


# ── จำลอง chain 12 ปัจจัย ─────────────────────────────────
def simulate_chain(root: str, intensity: float, propagates: bool, cut_point: str) -> list:
    results = []
    cut_index = CHAIN_12.index(cut_point) if cut_point in CHAIN_12 else len(CHAIN_12)

    for i, stage in enumerate(CHAIN_12):
        active = (i <= cut_index) if not propagates else True

        stage_intensity = round(intensity * (i + 1) / len(CHAIN_12), 3) if active else 0.0

        results.append({
            "index":     i + 1,
            "stage":     stage,
            "active":    active,
            "intensity": stage_intensity,
            "cut_here":  (stage == cut_point and not propagates),
        })

    return results


# ── UAP — Universal Audit Protocol ────────────────────────
def run_uap(context: str, pattern: dict) -> dict:
    """
    5 คำถาม audit ก่อนตัดสินใจ
    คืน flag ที่ engine อื่นอ่านได้
    """
    root_info  = detect_root_cause(context)
    feeling    = root_info["feeling"]
    entropy    = _f(pattern.get("entropy"),   40)
    stability  = _f(pattern.get("stability"), 60)

    u1_ignorance = entropy > 55                        # ยังไม่รู้พอ
    u2_feeling   = feeling                             # ระบุเวทนา
    u3_craving   = FEELING_TONE[feeling]["craving_risk"] > 0.6
    u4_becoming  = stability < 40                      # กำลังสร้างตัวตนใหม่อยู่
    u5_clinging  = u3_craving and not u4_becoming      # ยึดแต่ยังไม่แน่นพอ

    should_pause = u1_ignorance or u3_craving

    return {
        "U1_ignorance_present": u1_ignorance,
        "U2_feeling_tone":      u2_feeling,
        "U3_craving_detected":  u3_craving,
        "U4_becoming":          u4_becoming,
        "U5_clinging":          u5_clinging,
        "should_pause":         should_pause,
        "audit_note": (
            "หยุดก่อน — ยังมีตัณหาหรืออวิชชาอยู่ ไม่ควรตัดสินใจทันที"
            if should_pause else
            "สถานะสงบพอ — สามารถดำเนินการได้"
        ),
    }


# ── MAIN: suffering_infrastructure ────────────────────────
def suffering_infrastructure(context: str, pattern: dict = None) -> dict:
    pattern = pattern if isinstance(pattern, dict) else {}

    # 1. หา root cause + feeling
    root_info = detect_root_cause(context)
    root      = root_info["root"]
    feeling   = root_info["feeling"]

    # 2. คำนวณ intensity จาก pattern
    entropy   = _f(pattern.get("entropy"),   40)
    stability = _f(pattern.get("stability"), 60)
    iw        = root_info.get("intensity_weight", 1.0)
    intensity = round(max(0.3, min(2.0, iw * (entropy / 60) * (1 - stability / 120))), 3)

    # 3. วิเคราะห์ kill zone
    kz = analyze_kill_zone(feeling, pattern)
    evidence = root_info.get("evidence", True)
    if not evidence:
        # ไม่มีหลักฐานของเวทนา/ตัณหาในข้อความ ≠ วงจรดับ (นิพพาน) — บอกตรงๆ ว่าไม่มีสัญญาณ
        kz = {**kz, "outcome": "no_signal", "cut_point": None, "craving_risk": 0.5}

    # 4. จำลอง chain
    chain = simulate_chain(root, intensity, kz["propagates"], kz["cut_point"] or "decay_suffering")

    # 5. UAP
    uap = run_uap(context, pattern)

    # 6. Nirvana check (ต้องมีหลักฐานว่าวงจรถูกตัดจริง)
    nirvana_mode = (kz["outcome"] == "chain_cut")

    return {
        "root_cause":       root,
        "feeling_tone":     feeling,
        "intensity":        intensity,
        "kill_zone":        kz,
        "collapse_chain":   chain,
        "uap":              uap,
        "nirvana_mode":     nirvana_mode,
        "evidence":         evidence,
        "summary": (
            "ไม่พบสัญญาณเวทนา/ตัณหาที่ชัดในข้อความ"
            if not evidence else
            "วงจรดับที่เวทนา — ไม่เกิดตัณหา ระบบสงบ"
            if nirvana_mode else
            f"วงจรวิ่งถึง {kz['cut_point'] or 'decay_suffering'} — ต้องการการแทรกแซง"
        ),
    }


# ── ADAPTER สำหรับ DecisionEngine ─────────────────────────
def analyze(pattern: dict) -> dict:
    """DecisionEngine เรียกผ่าน adapter นี้"""
    try:
        pattern = pattern if isinstance(pattern, dict) else {"input": str(pattern or "")}
        context = str(pattern.get("raw_input") or pattern.get("input", ""))
        return suffering_infrastructure(context, pattern)
    except Exception:
        return {"error": "PATICCA_UNAVAILABLE"}
