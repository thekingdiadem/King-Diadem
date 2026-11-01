"""วัดคำตอบตอนไม่มี AI กับคำถามจริง (tests/everyday_questions.py)
ใช้:  python scripts/eval_everyday.py      → พิมพ์ข้อที่ยังตอบกลางๆ/ไม่ตรงเรื่อง พร้อมสัดส่วนที่ผ่าน"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.kernel_voice import compose                     # noqa: E402
from tests.everyday_questions import CASES             # noqa: E402

GENERIC = ("ขอเรียงเรื่องนี้ให้เห็นเป็นขั้นก่อน",)


def check(q, want):
    out = compose(q)
    head = out.split("\n", 1)[0]
    if any(head.startswith(g) for g in GENERIC):
        return False, "ตอบกลาง: " + head
    if not any(w.lower() in out.lower() for w in want):
        return False, "ไม่ตรงเรื่อง: " + head
    return True, head


if __name__ == "__main__":
    bad = 0
    for q, want in CASES:
        ok, why = check(q, want)
        if not ok:
            bad += 1
            print(f"✗ {q}\n    {why}")
    n = len(CASES)
    print(f"\nผ่าน {n - bad}/{n} ({(n - bad) * 100 // n}%)")
