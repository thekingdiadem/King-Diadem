"""
scripts/missed_to_tests.py — ประโยคจริงที่ผู้ใช้บอกว่า "ระบบไม่เห็นว่าเรื่องนี้ด่วน/อันตราย" → รายการให้คนตรวจ

เจ้าของโปรเจกต์ตกลงให้มีปุ่มนี้ เพราะประโยคจากคนจริงเจอจุดอ่อนที่เรานึกไม่ถึง
สคริปต์นี้แค่พิมพ์รายการ (ไม่แก้โค้ดเอง): ประโยค · ความเสี่ยงตอนผู้ใช้รายงาน · ความเสี่ยงตอนนี้
ประโยคไหนตอนนี้ยังต่ำกว่า 65 = ยังหลุดอยู่ → คนอ่านแล้วตัดสินใจว่าจะเพิ่มเป็นเทสต์และแก้กฎหรือไม่
ประโยคถูกลบเบอร์/อีเมลออกแล้วตั้งแต่ตอนเก็บ และหายเองเมื่อครบ 90 วัน

รัน: python scripts/missed_to_tests.py   (บนเครื่องที่มีฐานข้อมูลจริง)
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main() -> int:
    from core.answer_reports import missed_questions
    from core.kernel_voice import assess
    rows = missed_questions(500)
    still = 0
    for r in rows:
        now = assess(r["question"])["risk_shown"]
        mark = "ยังหลุด" if now < 65 else "แก้แล้ว"
        still += now < 65
        print(f"{mark}\t{r['risk']:>3} → {now:>3}\t{r['question'][:120]}")
    print(f"\nทั้งหมด {len(rows)} ประโยค · ยังหลุด {still}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
