"""พิมพ์ทะเบียนเบอร์ช่วยเหลือ (core/hotlines.py) ให้คนตรวจ — ยังไม่ยืนยันขึ้นก่อน
ใช้: python scripts/hotline_review.py · ตรวจแล้วแก้ verified=True ในทะเบียน พร้อมวันที่ใน REVIEWED"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.hotlines import REGISTRY, REVIEWED  # noqa: E402

rows = [(c, ln) for c, lines in REGISTRY.items() for ln in lines]
rows.sort(key=lambda r: (r[1].verified, r[0], r[1].kind))
print(f"ทะเบียนเบอร์ช่วยเหลือ · ทบทวนล่าสุด {REVIEWED} · ยังไม่ยืนยัน {sum(not ln.verified for _, ln in rows)}/{len(rows)}\n")
for c, ln in rows:
    print(f"{'✓' if ln.verified else '·'} {c:3s} {ln.number:15s} {ln.th}  —  ตรวจที่ {ln.source}")
