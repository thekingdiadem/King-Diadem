"""วัดผลชั้นของระบบเอง (ตอนไม่มี AI) ด้วยชุด 500+ ข้อ — tests/eval_set.py + tests/everyday_questions.py
ใช้:
  python scripts/eval_500.py           → คะแนนรายหมวด + ข้อที่ตก
  python scripts/eval_500.py --save    → บันทึกคะแนนเป็นเส้นฐาน (tests/eval_baseline.json) หลังปรับปรุงระบบ
เทสต์ tests/test_eval_baseline.py ล้มถ้าคะแนนหมวดไหนต่ำกว่าเส้นฐาน = แก้แล้วแย่ลง"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from core.kernel_voice import compose                     # noqa: E402
from tests.eval_set import CASES as SET_CASES              # noqa: E402
from tests.everyday_questions import CASES as EVERYDAY    # noqa: E402

BASELINE = os.path.join(ROOT, "tests", "eval_baseline.json")
GENERIC = ("ขอเรียงเรื่องนี้ให้เห็นเป็นขั้นก่อน",)


def all_cases():
    return [("everyday", q, w) for q, w in EVERYDAY] + list(SET_CASES)


def check(q, want):
    out = compose(q)
    head = out.split("\n", 1)[0]
    if any(head.startswith(g) for g in GENERIC):
        return False, "ตอบกลาง: " + head
    if not any(w.lower() in out.lower() for w in want):
        return False, "ไม่ตรงเรื่อง: " + head[:70]
    return True, head


def score():
    by, fails = {}, []
    for cat, q, want in all_cases():
        ok, why = check(q, want)
        p, n = by.get(cat, (0, 0))
        by[cat] = (p + ok, n + 1)
        if not ok:
            fails.append((cat, q, why))
    return by, fails


if __name__ == "__main__":
    by, fails = score()
    total_p, total_n = sum(p for p, _ in by.values()), sum(n for _, n in by.values())
    for cat, q, why in fails:
        print(f"✗ [{cat}] {q}\n    {why}")
    print()
    for cat, (p, n) in by.items():
        print(f"{cat:13s} {p:3d}/{n:<3d} {p * 100 // n:3d}%")
    print(f"\nรวม {total_p}/{total_n} ({total_p * 100 // total_n}%)")
    if "--save" in sys.argv:
        with open(BASELINE, "w", encoding="utf-8") as f:
            json.dump({c: p for c, (p, _) in by.items()}, f, ensure_ascii=False, indent=1, sort_keys=True)
            f.write("\n")
        print("บันทึกเส้นฐานแล้ว →", os.path.relpath(BASELINE, ROOT))
