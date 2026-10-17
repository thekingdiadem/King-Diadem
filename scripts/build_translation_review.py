"""สร้าง docs/TRANSLATION_REVIEW.md — คำตอบเรื่องด่วนทุกภาษาและเบอร์ฉุกเฉินที่อยู่ในข้อความ
ไว้ส่งให้เจ้าของภาษาตรวจ (คำแปลกับเบอร์ยังไม่มีใครตรวจกับแหล่งจริง)

รัน:  python scripts/build_translation_review.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core.asia_replies import REPLY as ASIA  # noqa: E402
from core.lang_signals import URGENT_REPLY  # noqa: E402
from core.world_replies import WORLD_REPLY  # noqa: E402
from scripts.build_showcase import NAMES  # noqa: E402

OUT = os.path.join(ROOT, "docs", "TRANSLATION_REVIEW.md")
_NUM = re.compile(r"(?<![\w.])\+?\d[\d \-]{1,12}\d(?![\w.])|(?<![\w.])\d{3}(?![\w.])")


def table():
    """{ภาษา: {หัวข้อ: ข้อความ}} รวมทุกแหล่ง"""
    rows = {}
    for topic, by_lang in URGENT_REPLY.items():
        for lang, msg in by_lang.items():
            rows.setdefault(lang, {})[topic] = msg
    for src in (ASIA, WORLD_REPLY):
        for lang, topics in src.items():
            for topic, msg in topics.items():
                rows.setdefault(lang, {})[topic] = msg
    return rows


def numbers(msg):
    return sorted({n.strip() for n in _NUM.findall(msg if isinstance(msg, str) else str(msg))})


def render():
    rows = table()
    out = ["# ตรวจคำแปลและเบอร์ฉุกเฉิน\n",
           "ไฟล์นี้สร้างอัตโนมัติจากโค้ด (`python scripts/build_translation_review.py`) — อย่าแก้ในไฟล์นี้โดยตรง\n",
           "ให้เจ้าของภาษาช่วยเช็ก 3 อย่าง: ① ความหมายถูกและน้ำเสียงอ่อนโยน ② ไม่มีคำที่ทำให้ตกใจหรือดูถูก "
           "③ เบอร์ในประเทศนั้นยังใช้ได้จริง (เทียบกับเว็บทางการ)\n",
           "\n| ภาษา | หัวข้อ | เบอร์ที่พบ |\n|---|---|---|\n"]
    for lang in sorted(rows, key=lambda c: NAMES.get(c, c)):
        nums = sorted({n for m in rows[lang].values() for n in numbers(m)})
        out.append(f"| {NAMES.get(lang, lang)} (`{lang}`) | {len(rows[lang])} | {' · '.join(nums)} |\n")
    for lang in sorted(rows, key=lambda c: NAMES.get(c, c)):
        out.append(f"\n## {NAMES.get(lang, lang)} (`{lang}`)\n\n- [ ] ผู้ตรวจ: ______  วันที่: ______\n")
        for topic, msg in rows[lang].items():
            body = msg if isinstance(msg, str) else str(msg)
            out.append(f"\n**{topic}**\n\n```text\n{body.strip()}\n```\n")
    return "".join(out)


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render())
    print(f"→ {OUT}: {len(table())} ภาษา")


if __name__ == "__main__":
    main()
