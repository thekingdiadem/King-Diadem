"""ทดสอบความทนทาน 10,000 ประโยค — พิมพ์แบบคนจริงบนมือถือแล้ว ระบบยังจับเรื่องอันตรายได้ไหม

สิ่งที่วัด (และไม่ได้วัด):
  · วัด: ประโยคอันตราย/ประโยคปกติที่มีอยู่แล้ว (ชุดปิดตา + ชุดกันถอยหลัง) ถูก "บิด" แบบที่คนพิมพ์จริง
    เช่น ไม่ใส่วรรณยุกต์ ไม่เว้นวรรค ลงท้าย ค่ะ/ครับ/อะ อีโมจิ พิมพ์ซ้ำ ตัวพิมพ์ใหญ่เล็ก ตัดคำย่อ — ยังจับได้กี่ %
    และประโยคปกติที่ถูกบิดแบบเดียวกัน ถูกเตือนเกินกี่ %
  · ไม่ได้วัด: ประโยคอันตรายที่ "เนื้อหาใหม่" ทั้งประโยค — นั่นต้องใช้ข้อสอบที่คนอื่นเขียน (tests/blind/blind.tsv)
    ประโยคที่สร้างจากคำของคนเขียนตัวจับเองจะได้คะแนนสูงเกินจริง จึงไม่ทำแบบนั้น

ไม่ใช้ AI ไม่มีค่าโทเคน · สุ่มแบบกำหนด seed (รันซ้ำได้ผลเดิม)
รัน:  python scripts/robustness_test.py [จำนวน=10000] [--write]   (--write เขียน static/robustness_score.json)
(ต่างจาก scripts/stress_test.py เดิมที่ตรวจว่าระบบไม่ล้ม/ไม่ช้า — ไฟล์นี้วัดว่ายังจับเรื่องอันตรายได้ไหม)
"""
from __future__ import annotations

import json
import os
import random
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
OUT = os.path.join(ROOT, "static", "robustness_score.json")
CORPUS = os.path.join(ROOT, "tests", "corpus", "messages.tsv")

_DANGER_TOPICS = {"someone", "warning", "violence", "threat", "sexual_abuse", "overdose", "health_emergency", "intruder"}


def base_sentences():
    """ประโยคต้นแบบ — อันตราย: ชุดปิดตาหมวดอันตราย + ชุดกันถอยหลังที่ต้องเป็นวิกฤต/ภัย · ปกติ: ที่ต้องไม่เตือน"""
    from blind_score import DANGER, load
    danger, calm = [], []
    for r in load():
        if r["label"] in DANGER:
            danger.append(r["text"])
        elif r["label"] == "none":
            calm.append(r["text"])
    with open(CORPUS, encoding="utf-8") as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) < 2:
                continue
            exp = [e.strip() for e in p[1].split(";")]
            if "?known" in p[1]:
                continue
            if "crisis" in exp or any(e.startswith("disaster:") for e in exp) or \
                    any(e.startswith("topic:") and e[6:] in _DANGER_TOPICS for e in exp):
                danger.append(p[0])
            elif "none" in exp:
                calm.append(p[0])
    return sorted(set(danger)), sorted(set(calm) - set(danger))


# ── วิธีบิดประโยคแบบคนพิมพ์จริง (แต่ละแบบไม่เปลี่ยนความหมาย) ─────────────────────────────
_TONES = re.compile("[่้๊๋]")
_ENDS_TH = ["ค่ะ", "ครับ", "คะ", "นะ", "อะ", "จ้า", "งะ", "ค้าบ"]
_EMOJI = ["😭", "🥲", "😢", "🙏", "💔", "😞"]
_FILL_TH = ["คือ", "แบบว่า", "ขอโทษนะ", "ไม่รู้จะพูดยังไง"]
_FILL_EN = ["idk", "honestly", "so", "um", "sorry but"]
_EN_SHORT = [(r"\bI'm\b", "im"), (r"\bI am\b", "im"), (r"\bdon't\b", "dont"), (r"\bcan't\b", "cant"), (r"\byou\b", "u"),
             (r"\bwon't\b", "wont"), (r"\bare\b", "r"), (r"\bbecause\b", "bc")]


def is_thai(t):
    return bool(re.search("[฀-๿]", t))


def drop_tones(t, rnd):                     # มือถือพิมพ์เร็ว ไม่ใส่วรรณยุกต์บางคำ
    words = t.split(" ")
    i = rnd.randrange(len(words))
    words[i] = _TONES.sub("", words[i])
    return " ".join(words)


def no_spaces(t, rnd):
    return t.replace(" ", "") if is_thai(t) else t.replace(", ", ",")


def extra_spaces(t, rnd):
    return re.sub(" ", lambda m: " " * rnd.choice((1, 2)), t)


def ending(t, rnd):
    return t + (rnd.choice(_ENDS_TH) if is_thai(t) else rnd.choice([" pls", " rn", " ...", " help"]))


def emoji(t, rnd):
    return t + " " + rnd.choice(_EMOJI)


def repeat_end(t, rnd):                     # "ไม่ไหวแล้วววว" "pleaseee"
    m = re.search(r"([^\W\d_])(\W*)$", t)
    return t[:m.start(1)] + m.group(1) * rnd.choice((3, 4, 5)) + m.group(2) if m else t


def punct(t, rnd):
    return t + rnd.choice(["...", "!!", "?!", " .", "…"])


def filler(t, rnd):
    return (rnd.choice(_FILL_TH) + " " + t) if is_thai(t) else (rnd.choice(_FILL_EN) + " " + t)


def case_en(t, rnd):
    return t if is_thai(t) else rnd.choice([t.lower(), t.upper()])


def short_en(t, rnd):
    if is_thai(t):
        return t
    for a, b in rnd.sample(_EN_SHORT, 3):
        t = re.sub(a, b, t, flags=re.I)
    return t


def mai_yamok(t, rnd):                      # ไม้ยมก/ซ้ำคำตามสไตล์แชต
    return t.replace("ๆ", "") if "ๆ" in t else t


PERTURB = [drop_tones, no_spaces, extra_spaces, ending, emoji, repeat_end, punct, filler, case_en, short_en, mai_yamok]


def variants(base, n, rnd):
    out = []
    while len(out) < n:
        s = rnd.choice(base)
        k = rnd.choice((1, 1, 2, 2, 3))
        for fn in rnd.sample(PERTURB, k):
            s = fn(s, rnd)
        out.append(s)
    return out


def run(total=10000, seed=17):
    from blind_score import detected
    from core.kernel_voice import assess
    rnd = random.Random(seed)
    danger, calm = base_sentences()
    nd = int(total * .7)
    dv, cv = variants(danger, nd, rnd), variants(calm, total - nd, rnd)
    t0 = time.time()
    miss = [s for s in dv if not detected(assess(s))]
    alarm = [s for s in cv if detected(assess(s))]
    secs = time.time() - t0
    # ฐาน: ต้นฉบับที่ยังไม่บิด (ชุดปิดตายังมีข้อที่พลาดอยู่จริง ต้องหักออกก่อนตีความ)
    base_miss = {s for s in danger if not detected(assess(s))}
    base_alarm = {s for s in calm if detected(assess(s))}
    return {
        "total": len(dv) + len(cv), "seed": seed, "seconds": round(secs, 1),
        "base": {"danger": len(danger), "calm": len(calm), "danger_missed_unperturbed": len(base_miss), "calm_alarmed_unperturbed": len(base_alarm)},
        "danger": {"n": len(dv), "caught": len(dv) - len(miss), "rate": round(1 - len(miss) / len(dv), 4)},
        "calm": {"n": len(cv), "alarmed": len(alarm), "rate": round(len(alarm) / len(cv), 4)},
        "missed_examples": sorted(set(miss))[:40],
        "alarm_examples": sorted(set(alarm))[:40],
    }


if __name__ == "__main__":
    n = next((int(a) for a in sys.argv[1:] if a.isdigit()), 10000)
    r = run(n)
    print(f"ทดสอบ {r['total']:,} ประโยค (seed {r['seed']}) ใน {r['seconds']} วินาที")
    print(f"ประโยคต้นแบบ: อันตราย {r['base']['danger']} · ปกติ {r['base']['calm']}"
          f" (ต้นฉบับที่ยังพลาดอยู่ก่อนบิด {r['base']['danger_missed_unperturbed']} · เตือนเกินก่อนบิด {r['base']['calm_alarmed_unperturbed']})")
    print(f"อันตรายที่ถูกบิด: จับได้ {r['danger']['caught']:,}/{r['danger']['n']:,} = {r['danger']['rate']:.2%}")
    print(f"ปกติที่ถูกบิด: เตือนเกิน {r['calm']['alarmed']:,}/{r['calm']['n']:,} = {r['calm']['rate']:.2%}")
    for s in r["missed_examples"][:25]:
        print("  ✗ พลาด:", s)
    for s in r["alarm_examples"][:15]:
        print("  ! เกิน:", s)
    if "--write" in sys.argv:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=1)
