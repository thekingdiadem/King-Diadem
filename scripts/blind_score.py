"""
scripts/blind_score.py — สกอร์บอร์ดจากชุดข้อความปิดตา (tests/blind/blind.tsv)

ชุดกันถอยหลัง (tests/corpus/messages.tsv) ผ่าน 100% เสมอ เพราะทุกบรรทัดถูกเพิ่มพร้อมการแก้ตัวตรวจจับ
จึงบอกไม่ได้ว่าระบบเก่งแค่ไหนกับข้อความที่ไม่เคยเห็น — สคริปต์นี้วัดจากชุดที่ห้ามจูน แล้วรายงานตามจริง

รัน:  python scripts/blind_score.py            → ตารางคะแนน + ข้อที่พลาด
      python scripts/blind_score.py --write    → เขียน static/blind_score.json (หน้า /architecture แสดง)
      python scripts/blind_score.py --check    → exit 1 ถ้า static/blind_score.json ไม่ตรงกับผลจริง

ไม่ทำให้ CI ล้มเพราะคะแนนต่ำ — ถ้าคะแนนต่ำแล้ว CI ล้ม คนจะอยากแก้ให้ผ่านด้วยการจูนกับข้อสอบ
ไม่ใช้ AI — วัดตัวตรวจจับ core/kernel_voice.assess ซึ่งเป็นตัวตัดสินเส้นทางความปลอดภัย
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLIND = os.path.join(ROOT, "tests", "blind", "blind.tsv")
OUT = os.path.join(ROOT, "static", "blind_score.json")

CLASSES = ["self_harm", "emergency", "violence", "scam", "distress"]
LABELS = CLASSES + ["none"]
# หมวดที่พลาดแล้วอาจถึงชีวิต — นับ "พลาดภัยจริง" แยกให้เห็นชัด
DANGER = {"self_harm", "emergency", "violence"}

# ผลของ assess() → หมวด (ระบบเห็นอะไรในข้อความ)
_TOPIC_CLASS = {
    "self_harm": {"warning", "someone"},
    "emergency": {"overdose", "swallowed", "household", "pet_poison", "health_emergency", "first_aid", "stranded",
                  "en_infant_fever", "en_preg_bleed", "needlestick", "missing", "drunk_drive", "panic", "psychosis"},
    "violence": {"violence", "sexual_abuse", "en_assault", "en_spiked", "harm_others", "weapon", "witness", "elder_abuse",
                 "trafficking", "threat", "online_grooming", "control_en", "bullying"},
    "scam": {"scam", "sextortion", "hacked"},
    "distress": {"debt", "basic", "housing", "labor"},
}
_INTL_CLASS = {"medical": "emergency", "disaster": "emergency", "violence": "violence", "scam": "scam",
               "basic": "distress", "someone": "self_harm"}


def load(path: str = BLIND) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            p = [x.strip() for x in line.split("\t")]
            if len(p) < 4 or p[1] not in LABELS:
                raise ValueError(f"{path}:{n} ต้องมี 4 คอลัมน์ (ข้อความ หมวด ภาษา ผู้เขียน) และหมวดต้องเป็น {LABELS}: {line!r}")
            rows.append({"line": n, "text": p[0], "label": p[1], "lang": p[2], "author": p[3]})
    return rows


def detected(a: dict) -> set[str]:
    """หมวดที่ระบบตรวจเจอจากผลของ assess()"""
    topics = set(a.get("topics") or [])
    out = {c for c, ts in _TOPIC_CLASS.items() if topics & ts}
    if a.get("crisis"):
        out.add("self_harm")
    if a.get("scam"):
        out.add("scam")
    dis = (a.get("disaster") or {}).get("kind")
    if dis:
        out.add("violence" if dis in ("violence", "intruder") else "emergency")
    for k in a.get("intl_urgent") or []:
        k = k[0] if isinstance(k, (list, tuple)) else k
        if k in _INTL_CLASS:
            out.add(_INTL_CLASS[k])
    return out


def score(rows: list[dict]) -> dict:
    from core.kernel_voice import assess
    res = []
    for r in rows:
        got = detected(assess(r["text"]))
        res.append({**r, "got": sorted(got)})
    per = {}
    for c in CLASSES:
        tp = sum(1 for r in res if r["label"] == c and c in r["got"])
        fn = sum(1 for r in res if r["label"] == c and c not in r["got"])
        fp = sum(1 for r in res if r["label"] != c and c in r["got"])
        per[c] = {"n": tp + fn, "tp": tp, "fn": fn, "fp": fp,
                  "recall": round(tp / (tp + fn), 3) if tp + fn else None,
                  "precision": round(tp / (tp + fp), 3) if tp + fp else None}
    danger = [r for r in res if r["label"] in DANGER]
    missed = [r for r in danger if not r["got"]]                      # ไม่เห็นอะไรเลย = ไม่ได้ส่งทางช่วยเหลือ
    calm = [r for r in res if r["label"] == "none"]
    alarms = [r for r in calm if r["got"]]
    langs = {}
    for r in res:
        if r["label"] != "none":
            l = langs.setdefault(r["lang"], [0, 0])
            l[0] += r["label"] in r["got"]
            l[1] += 1
    return {
        "total": len(res),
        "authors": sorted({r["author"] for r in res}),
        "blind_by_people": sum(1 for r in res if r["author"] != "claude-seed"),
        "classes": per,
        "danger_missed": {"n": len(missed), "of": len(danger)},
        "false_alarm": {"n": len(alarms), "of": len(calm)},
        "by_lang": {k: {"hit": v[0], "n": v[1]} for k, v in sorted(langs.items())},
        "misses": [{"line": r["line"], "text": r["text"], "label": r["label"], "got": r["got"]}
                   for r in res if (r["label"] == "none" and r["got"]) or (r["label"] != "none" and r["label"] not in r["got"])],
    }


def _pct(x):
    return "  -  " if x is None else f"{100 * x:5.1f}%"


def main(argv: list[str]) -> int:
    sys.path.insert(0, ROOT)
    s = score(load())
    if "--check" in argv:
        try:
            same = json.load(open(OUT, encoding="utf-8")) == s
        except (OSError, ValueError):
            same = False
        print("สกอร์บอร์ดตรงกับผลจริง" if same else "สกอร์บอร์ดไม่ตรง — รัน python scripts/blind_score.py --write")
        return 0 if same else 1
    if "--write" in argv:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=1)
            f.write("\n")
    print(f"ชุดปิดตา {s['total']} ข้อ · เขียนโดยคนที่ไม่ได้เขียนตัวตรวจจับ {s['blind_by_people']} ข้อ")
    print(f"พลาดเรื่องอันตรายถึงชีวิตทั้งข้อ (ไม่เห็นอะไรเลย): {s['danger_missed']['n']}/{s['danger_missed']['of']}")
    print(f"เตือนเกินกับข้อความปกติ: {s['false_alarm']['n']}/{s['false_alarm']['of']}")
    print(f"  {'หมวด':<12}{'จำนวน':>6}{'เจอ (recall)':>14}{'แม่น (precision)':>18}{'พลาด':>6}{'เกิน':>6}")
    for c, v in s["classes"].items():
        print(f"  {c:<12}{v['n']:>6}{_pct(v['recall']):>14}{_pct(v['precision']):>18}{v['fn']:>6}{v['fp']:>6}")
    for m in s["misses"]:
        print(f"✗ L{m['line']} [{m['label']}] ได้ {m['got'] or '-'} · {m['text']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
