# INTELLIGENCE/pattern_engine.py
# KING DIADEM — Pattern Engine v2.0
# FATE™ Axiom A3: Determinism — ไม่มี hardcode ratio, คำนวณจาก text จริง
# -----------------------------------------------------------------

# ── KEYWORD SETS ──────────────────────────────────────────────────
# เพิ่ม keyword ได้โดยไม่ต้องแตะ logic

PIVOT_KEYWORDS = [
    # ไทย
    "เงิน", "ลงทุน", "ตลาด", "หุ้น", "กำไร", "ขาดทุน", "โอกาส",
    "ขาย", "ซื้อ", "ธุรกิจ", "รายได้", "เงินเดือน", "ราคา",
    "เปลี่ยน", "ปรับ", "pivot", "เริ่มใหม่", "ย้าย",
    # English
    "crypto", "invest", "market", "stock", "profit", "loss",
    "trade", "price", "revenue", "opportunity", "pivot", "shift",
]

DEFENSIVE_KEYWORDS = [
    # ไทย
    "กลัว", "เสี่ยง", "ไม่มั่นใจ", "กังวล", "ไม่แน่ใจ", "อันตราย",
    "หนี", "ป้องกัน", "รักษา", "ระวัง", "ไม่อยาก", "เลี่ยง",
    "ไม่ปลอดภัย", "พัง", "ล้มเหลว", "สูญเสีย", "สูญ",
    # English
    "afraid", "risk", "uncertain", "worry", "danger", "protect",
    "avoid", "scared", "unsafe", "fail", "loss", "fear",
]

SURVIVAL_KEYWORDS = [
    # ไทย
    "รอด", "ช่วย", "ฉุกเฉิน", "ด่วน", "ไม่มีเงิน", "หมด",
    "วิกฤต", "อยู่ไม่ได้", "หมดแรง", "ทนไม่ไหว",
    # English
    "survive", "emergency", "urgent", "crisis", "broke", "help",
    "cant go on", "no money",
]

NEUTRAL_KEYWORDS = [
    # context ที่ไม่ได้ push signal ทางใด
    "ข้อมูล", "อธิบาย", "บอก", "รู้", "คิด", "ถาม",
    "explain", "tell", "know", "think", "what", "how",
]


# ══════════════════════════════════════════════════════════════════
# CORE FUNCTION
# ══════════════════════════════════════════════════════════════════

def analyze_patterns(user_input: str) -> dict:
    """
    วิเคราะห์ข้อความ → pattern ratios และ confidence

    Returns
    -------
    {
        pattern_detected   : bool
        pivot_ratio        : float  0.0-1.0
        defensive_ratio    : float  0.0-1.0
        survival_flag      : bool
        dominant_signal    : str    "pivot" | "defensive" | "survival" | "neutral"
        confidence         : float  0.0-1.0
        keyword_hits       : dict   {"pivot": [...], "defensive": [...], …}
        token_count        : int
    }
    """
    text   = (user_input or "").lower().strip()
    tokens = _tokenize(text)
    n      = max(len(tokens), 1)

    # ── Hit detection ─────────────────────────────────────────────
    hits = _collect_hits(text, tokens)

    pivot_hits     = hits["pivot"]
    defensive_hits = hits["defensive"]
    survival_hits  = hits["survival"]
    neutral_hits   = hits["neutral"]

    # ── Raw counts ────────────────────────────────────────────────
    pivot_count     = len(pivot_hits)
    defensive_count = len(defensive_hits)
    survival_count  = len(survival_hits)
    signal_count    = pivot_count + defensive_count + survival_count

    # ── Ratios: relative to signal count (ไม่ใช่ token count) ─────
    # เพราะ text สั้น/ยาวไม่ควรเปลี่ยน meaning ของ intent
    if signal_count > 0:
        pivot_ratio     = round(pivot_count     / signal_count, 4)
        defensive_ratio = round(defensive_count / signal_count, 4)
        survival_ratio  = round(survival_count  / signal_count, 4)
    else:
        pivot_ratio = defensive_ratio = survival_ratio = 0.0

    # ── Survival flag: absolute check (แม้แต่ 1 survival keyword) ─
    survival_flag = survival_count > 0

    # ── Confidence: เชื่อถือได้มากขึ้นถ้า signal หลากหลาย ────────
    confidence = _compute_confidence(signal_count, n, pivot_ratio, defensive_ratio)

    # ── Dominant signal ───────────────────────────────────────────
    dominant_signal = _dominant(
        pivot_ratio, defensive_ratio, survival_ratio,
        survival_flag, signal_count
    )

    # ── Pattern detected ──────────────────────────────────────────
    pattern_detected = signal_count > 0

    return {
        "pattern_detected":  pattern_detected,
        "pivot_ratio":       pivot_ratio,
        "defensive_ratio":   defensive_ratio,
        "survival_flag":     survival_flag,
        "dominant_signal":   dominant_signal,
        "confidence":        confidence,
        "keyword_hits":      hits,
        "token_count":       n,
    }


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

def _tokenize(text: str) -> list[str]:
    """
    Thai text ไม่มี space → ใช้ substring matching แทน split
    ที่นี่ return chars list สำหรับนับ length เท่านั้น
    """
    # ตัด whitespace แล้ว return list of words (สำหรับ EN)
    # สำหรับ TH ใช้ substring match ใน _collect_hits แทน
    import re
    tokens = re.findall(r'\S+', text)
    return tokens if tokens else list(text)


def _collect_hits(text: str, tokens: list) -> dict[str, list]:
    """
    Return keyword hits per category (deduplicated)
    ใช้ substring matching รองรับทั้ง Thai และ English
    """
    def hits_for(kw_list):
        found = []
        for kw in kw_list:
            if kw in text and kw not in found:
                found.append(kw)
        return found

    return {
        "pivot":     hits_for(PIVOT_KEYWORDS),
        "defensive": hits_for(DEFENSIVE_KEYWORDS),
        "survival":  hits_for(SURVIVAL_KEYWORDS),
        "neutral":   hits_for(NEUTRAL_KEYWORDS),
    }


def _compute_confidence(
    signal_count: int,
    token_count:  int,
    pivot_ratio:  float,
    defensive_ratio: float,
) -> float:
    """
    Confidence สูงขึ้นเมื่อ:
    - signal_count มาก (more evidence)
    - ratios ไม่ 50/50 (clear dominance)
    """
    if signal_count == 0:
        return 0.0

    # Base: signal density ใน text
    density = min(signal_count / max(token_count, 1), 1.0)

    # Dominance: ยิ่งไม่กึ่งๆ ยิ่ง confident
    balance = abs(pivot_ratio - defensive_ratio)  # 0 = tie, 1 = full dominance

    confidence = 0.4 * density + 0.4 * balance + 0.2 * min(signal_count / 5, 1.0)
    return round(min(confidence, 1.0), 4)


def _dominant(
    pivot_ratio:     float,
    defensive_ratio: float,
    survival_ratio:  float,
    survival_flag:   bool,
    signal_count:    int,
) -> str:
    if signal_count == 0:
        return "neutral"
    if survival_flag and survival_ratio >= max(pivot_ratio, defensive_ratio):
        return "survival"
    if pivot_ratio > defensive_ratio:
        return "pivot"
    if defensive_ratio > pivot_ratio:
        return "defensive"
    # tie → defensive wins (Downside First axiom)
    return "defensive"
