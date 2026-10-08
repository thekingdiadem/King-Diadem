"""
scripts/eval_corpus.py — ให้คะแนนระบบด้วยชุดข้อความทดสอบกลาง (tests/corpus/messages.tsv)

รัน:  python scripts/eval_corpus.py          → สรุปคะแนนรายหมวด + ข้อที่พลาด
      python scripts/eval_corpus.py -v       → แสดงทุกข้อ

ไม่ใช้ AI — วัดตัวตรวจจับของระบบ (core/kernel_voice.assess) ซึ่งตัดสินเส้นทาง ความเสี่ยง และขั้นตอนที่ส่งให้ AI
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(ROOT, "tests", "corpus", "messages.tsv")


def load(path: str = CORPUS) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                raise ValueError(f"{path}:{n} ต้องมีอย่างน้อย 2 คอลัมน์ (คั่นด้วย TAB): {line!r}")
            text, expect = parts[0].strip(), parts[1].strip()
            known = expect.endswith("?known")
            expect = expect[:-len("?known")].rstrip(";").strip() if known else expect
            rows.append({"line": n, "text": text, "checks": [c.strip() for c in expect.split(";") if c.strip()],
                         "group": parts[2].strip() if len(parts) > 2 else "-", "known": known})
    return rows


def check(a: dict, c: str) -> bool:
    topics = set(a.get("topics") or [])
    risk = a.get("text_risk", 0) or 0
    scam = set(a.get("scam") or [])
    dis = a.get("disaster") or {}
    if c == "crisis":
        return bool(a.get("crisis"))
    if c == "!crisis":
        return not a.get("crisis")
    if c == "none":
        return risk < 50 and not a.get("crisis") and not dis and not scam
    if c == "!scam":
        return not scam
    if c == "!disaster":
        return not dis
    if c.startswith("!topic:"):
        return c[7:] not in topics
    if c.startswith("topic:"):
        return c[6:] in topics
    if c.startswith("scam:"):
        return c[5:] in scam
    if c.startswith("disaster:"):
        return dis.get("kind") == c[9:]
    if c.startswith("intl:"):                  # เรื่องด่วนภาษาอื่น (core/lang_signals.urgent_intl)
        return c[5:] in (a.get("intl_urgent") or [])
    if c.startswith("risk>="):
        return risk >= float(c[6:])
    if c.startswith("risk<"):
        return risk < float(c[5:])
    raise ValueError(f"ไม่รู้จักเงื่อนไข {c!r}")


def evaluate(rows: list[dict]) -> list[dict]:
    from core.kernel_voice import assess
    out = []
    for r in rows:
        a = assess(r["text"])
        failed = [c for c in r["checks"] if not check(a, c)]
        out.append({**r, "ok": not failed, "failed": failed,
                    "got": {"topics": a.get("topics"), "risk": a.get("text_risk"), "crisis": a.get("crisis"),
                            "scam": a.get("scam"), "disaster": (a.get("disaster") or {}).get("kind")}})
    return out


def main(argv: list[str]) -> int:
    sys.path.insert(0, ROOT)
    res = evaluate(load())
    by = defaultdict(lambda: [0, 0])
    for r in res:
        by[r["group"]][0] += r["ok"]
        by[r["group"]][1] += 1
    hard = [r for r in res if not r["known"]]
    ok = sum(r["ok"] for r in hard)
    print(f"คะแนนรวม: {ok}/{len(hard)} ({100 * ok / max(len(hard), 1):.1f}%)  · ข้อที่รู้ว่ายังทำไม่ได้: "
          f"{sum(1 for r in res if r['known'])} (ผ่านแล้ว {sum(1 for r in res if r['known'] and r['ok'])})")
    for g, (o, n) in sorted(by.items(), key=lambda kv: kv[1][0] / kv[1][1]):
        print(f"  {g:<16} {o}/{n}")
    for r in res:
        if not r["ok"] or "-v" in argv:
            mark = "✓" if r["ok"] else ("~" if r["known"] else "✗")
            print(f"{mark} L{r['line']}: {r['text']}  · พลาด {r['failed']}  · ได้ {r['got']}")
    return 0 if all(r["ok"] for r in hard) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
