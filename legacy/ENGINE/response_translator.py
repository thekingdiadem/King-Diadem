# ENGINE/response_translator.py
"""
KING DIADEM — Response Translator
ไม่ depend on deep_translator (third-party ที่อาจไม่มีใน Render)
ใช้ Google Translate API free endpoint แทน + fallback
"""
from __future__ import annotations
import urllib.request
import urllib.parse
import json
from typing import Optional


def translate(
    text:   str,
    target: str,
    source: str = "auto",
) -> str:
    """
    แปลข้อความ — ใช้ Google Translate unofficial endpoint
    ไม่ต้อง install package — stdlib urllib เท่านั้น
    fallback: return ต้นฉบับถ้า request ไม่สำเร็จ

    ⚠ ความเป็นส่วนตัว: ข้อความถูกส่งไปยัง endpoint ภายนอกที่ไม่เป็นทางการ
      อย่าเรียกกับข้อความส่วนตัวของผู้ใช้โดยไม่บอกเขาก่อน
    """
    if not text or not str(text).strip():
        return text

    try:
        # เดิมต่อ sl/tl เข้า URL ตรงๆ — ค่าอย่าง "en&x=1" แทรกพารามิเตอร์เพิ่มได้
        url = "https://translate.googleapis.com/translate_a/single?" + urllib.parse.urlencode(
            {"client": "gtx", "sl": str(source), "tl": str(target), "dt": "t", "q": str(text)[:5000]}
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            parts = data[0]
            return "".join(p[0] for p in parts if p[0])
    except Exception:
        return text   # fallback — ไม่ crash


def translate_safe(
    text:     str,
    target:   str,
    source:   str = "auto",
    fallback: Optional[str] = None,
) -> dict:
    """
    Return dict พร้อม status — สำหรับ engine ที่ต้องการรู้ว่าแปลสำเร็จไหม
    """
    try:
        result = translate(text, target, source)
        success = result != text or target == source
        return {
            "translated": result,
            "source":     source,
            "target":     target,
            "success":    success,
        }
    except Exception as e:
        return {
            "translated": fallback or text,
            "source":     source,
            "target":     target,
            "success":    False,
            "error":      str(e),
        }


# ── Language detector (basic) ─────────────────────────────────────
def detect_language(text: str) -> str:
    """ตรวจภาษาแบบ lightweight — ไม่ต้องใช้ API"""
    if not text:
        return "unknown"
    thai_chars = sum(1 for c in text if "\u0e00" <= c <= "\u0e7f")
    if thai_chars / max(len(text), 1) > 0.2:
        return "th"
    return "en"
