"""สร้าง static/showcase.json — ตัวเลขจริงที่หน้า Universe เอาไปโชว์ (ไม่ได้พิมพ์ตัวเลขเองในหน้าเว็บ)

- ภาษาที่ระบบตอบเรื่องด่วนเป็นภาษาของผู้ใช้ได้ (นับจาก core/lang_signals · asia_replies · world_replies)
- ผลชุดกวาดทุกชุดของ scripts/sweep_all.py (จำนวนข้อความ · หลุด)

รัน:  python scripts/build_showcase.py        (ราว 2–3 นาที เพราะรันชุดกวาดเต็มจำนวน)
"""
import datetime
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core.asia_replies import REPLY as ASIA  # noqa: E402
from core.lang_signals import URGENT_REPLY  # noqa: E402
from core.world_replies import WORLD_REPLY  # noqa: E402
from scripts import sweep_all  # noqa: E402

OUT = os.path.join(ROOT, "static", "showcase.json")

NAMES = {
    "th": "ไทย", "en": "English", "zh": "中文", "ja": "日本語", "ko": "한국어", "es": "Español",
    "my": "မြန်မာ", "km": "ខ្មែរ", "lo": "ລາວ", "vi": "Tiếng Việt", "id": "Indonesia", "ms": "Melayu", "tl": "Tagalog",
    "hi": "हिन्दी", "ne": "नेपाली", "bn": "বাংলা", "ur": "اردو", "ta": "தமிழ்", "si": "සිංහල", "fa": "فارسی",
    "ar": "العربية", "tr": "Türkçe", "fr": "Français", "de": "Deutsch", "pt": "Português", "it": "Italiano",
    "ru": "Русский", "uk": "Українська", "pl": "Polski", "nl": "Nederlands", "sw": "Kiswahili", "am": "አማርኛ",
    "ha": "Hausa", "yo": "Yorùbá", "zu": "isiZulu", "af": "Afrikaans", "so": "Soomaali", "el": "Ελληνικά",
    "ro": "Română", "sv": "Svenska", "he": "עברית", "mn": "Монгол", "kk": "Қазақ", "uz": "Oʻzbek",
    "cs": "Čeština", "sk": "Slovenčina", "hu": "Magyar", "fi": "Suomi", "da": "Dansk", "no": "Norsk",
    "sh": "Hrvatski / Srpski / Bosanski", "bg": "Български", "ka": "ქართული", "hy": "Հայերեն",
}
REGION = {
    "asia": ["th", "zh", "ja", "ko", "my", "km", "lo", "vi", "id", "ms", "tl", "hi", "ne", "bn", "ur", "ta", "si", "mn", "kk", "uz"],
    "middle_east": ["fa", "ar", "tr", "he", "ka", "hy"],
    "europe": ["en", "fr", "de", "it", "ru", "uk", "pl", "nl", "el", "ro", "sv", "cs", "sk", "hu", "fi", "da", "no", "sh", "bg", "es", "pt"],
    "africa": ["sw", "am", "ha", "yo", "zu", "af", "so"],
}


def languages() -> list:
    main = {"th", "en"} | set(next(iter(URGENT_REPLY.values())).keys())
    codes = main | set(ASIA) | set(WORLD_REPLY)
    unknown = codes - set(NAMES)
    assert not unknown, f"ภาษาใหม่ยังไม่มีชื่อแสดง: {unknown}"
    return sorted(codes, key=lambda c: NAMES[c])


def main():
    os.environ.setdefault("KD_AI", "off")         # ตั้งเฉพาะตอนรันสคริปต์ — import เฉยๆ (ในเทสต์) ต้องไม่ปิด AI ของคนอื่น
    langs = languages()
    suites = []
    for name, fn in sweep_all.SUITES.items():
        if name == "followup":                       # ต้องเปิดเซิร์ฟเวอร์ทดสอบ — ชุดนี้รันใน pytest แทน
            continue
        total, bad = fn(0)
        suites.append({"name": name, "messages": total, "slips": len(bad)})
        print(f"{name:12s} {total:6d} ข้อความ · หลุด {len(bad)}")
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except Exception:
        commit = ""
    data = {
        "generated": datetime.date.today().isoformat(), "commit": commit,
        "languages": [{"code": c, "name": NAMES[c]} for c in langs],
        "regions": {k: [c for c in v if c in langs] for k, v in REGION.items()},
        "suites": suites,
        "messages_total": sum(s["messages"] for s in suites),
        "slips_total": sum(s["slips"] for s in suites),
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"→ {OUT}: {len(langs)} ภาษา · {data['messages_total']} ข้อความ · หลุด {data['slips_total']}")


if __name__ == "__main__":
    main()
