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

# ข้อเท็จจริงอื่นในชุดความรู้ (core/knowledge_pack_facts.py) — กฎหมายก่อน เพราะเปลี่ยนตามประกาศใหม่
from core.knowledge_pack_facts import FACTS, KIND_ORDER  # noqa: E402

facts = sorted(FACTS, key=lambda f: (f.verified, KIND_ORDER.index(f.kind), f.topic))
print(f"\nข้อเท็จจริงในชุดความรู้ · ยังไม่ยืนยัน {sum(not f.verified for f in facts)}/{len(facts)}\n")
for f in facts:
    print(f"{'✓' if f.verified else '·'} {f.kind:9s} {f.topic:24s} {f.claim}\n{'':36s}ตรวจที่ {f.source}")
