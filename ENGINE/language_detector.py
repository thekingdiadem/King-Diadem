# ENGINE/language_detector.py
"""
KING DIADEM — Language Detector
Unicode range detection — ไม่ใช่ตรวจแค่ 4 ตัวอักษร
"""
from __future__ import annotations


# Unicode ranges per language
_RANGES = {
    "th": (0x0E00, 0x0E7F),    # Thai
    "ja": (0x3040, 0x30FF),    # Hiragana + Katakana
    "zh": (0x4E00, 0x9FFF),    # CJK Unified Ideographs
    "ko": (0xAC00, 0xD7AF),    # Hangul
    "ar": (0x0600, 0x06FF),    # Arabic
    "ru": (0x0400, 0x04FF),    # Cyrillic
    "hi": (0x0900, 0x097F),    # Devanagari
}

def detect_language(text: str) -> str:
    """
    ตรวจภาษาจาก Unicode range ratio
    return ISO 639-1 code: 'th', 'en', 'ja', 'zh', 'ko', 'ar', 'ru', 'hi'
    """
    if not text or not text.strip():
        return "unknown"

    total = len([c for c in text if not c.isspace()])
    if total == 0:
        return "unknown"

    counts: dict = {}
    for ch in text:
        cp = ord(ch)
        for lang, (lo, hi) in _RANGES.items():
            if lo <= cp <= hi:
                counts[lang] = counts.get(lang, 0) + 1
                break

    if not counts:
        return "en"

    # ภาษาที่มีสัดส่วนสูงสุด ต้องเกิน 10% ถึงจะนับ
    top_lang = max(counts, key=counts.get)
    ratio    = counts[top_lang] / total

    return top_lang if ratio > 0.10 else "en"


def detect_multi(text: str) -> dict:
    """
    ตรวจทุกภาษาในข้อความ — สำหรับ mixed-language input
    เช่น Thai + English ที่พี่ใช้
    """
    if not text or not text.strip():
        return {"primary": "unknown", "languages": {}}

    total = max(1, len([c for c in text if not c.isspace()]))
    counts: dict = {}
    en_chars = 0

    for ch in text:
        cp = ord(ch)
        matched = False
        for lang, (lo, hi) in _RANGES.items():
            if lo <= cp <= hi:
                counts[lang] = counts.get(lang, 0) + 1
                matched = True
                break
        if not matched and ch.isalpha():
            en_chars += 1

    if en_chars > 0:
        counts["en"] = en_chars

    ratios = {lang: round(n/total, 3) for lang, n in counts.items() if n/total > 0.05}
    primary = max(ratios, key=ratios.get) if ratios else "en"

    return {
        "primary":   primary,
        "languages": ratios,
        "mixed":     len(ratios) > 1,
    }
