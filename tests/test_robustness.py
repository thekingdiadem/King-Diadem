"""ทนทานต่อการพิมพ์แบบคนจริง + ชุด "คิดตรงข้ามกับตัวจับ" (red team)

พี่คิง: "สุ่มประโยคไม่ปลอดภัย 10,000 ประโยคแล้วลองเทส" · "เอาแบบคิดตรงข้ามกับตัวจับ — เหมือนทำลาย แต่เพื่อซ่อมก่อนส่งให้คนใช้"
· scripts/robustness_test.py บิดประโยคจริง 10,000 แบบ (เว้นวรรคซ้อน ลากตัวอักษร ไม่ใส่วรรณยุกต์ ตัวพิมพ์ใหญ่ ตัวย่อแชต ฯลฯ)
  ก่อนซ่อม จับได้ 92.17% → หลังซ่อม 98.10% (seed 17)
· tests/adversarial/adversarial.tsv รอบ 2 = ข้อสอบที่ยังไม่จูน (ผลจริงตอนเขียน: จับได้ 5/17)
"""
from pathlib import Path

from core.kernel_voice import assess
from core.thai_signals import canon_text

ROOT = Path(__file__).resolve().parent.parent


def _seen(t):
    a = assess(t)
    return bool(a.get("crisis") or a.get("topics") or a.get("disaster") or a.get("scam"))


def test_typing_styles_are_canonicalized():
    assert canon_text("I  feel   hopeless") == "I feel hopeless"                 # เว้นวรรคซ้อน
    assert canon_text("I feel hopelesssss") == "I feel hopeless"                # ss ใน -less คงไว้
    assert canon_text("I want to dieeeee") == "I want to die"
    assert canon_text("end itttt") == "end it" and canon_text("ready to gooo") == "ready to go"
    assert canon_text("THERE IS A FLOOD IN MY HOUSE") == "there is a flood in my house"
    assert canon_text("see u on the other side") == "see you on the other side"
    assert canon_text("ไม่ไหวแล้ววว") == "ไม่ไหวแล้ว" and canon_text("กระโดดดี") == "กระโดดดี"   # ไทยลากเฉพาะท้ายคำ
    assert canon_text("สะสมยานอนหลับไว้เยอะ") == "สะสมยานอนหลับไว้เยอะ"                      # "อะ" ในคำจริงไม่ถูกตัด
    assert canon_text("ทีมเราชนะ") == "ทีมเราชนะ"


def test_variants_of_danger_are_still_seen():
    for t in ("I  feel hopeless", "I want to dieeeee", "SOMEONE IS THREATENING ME", "my best friend posted 'see u on the other side' and turned off her phone",
              "ถาพรุงนีไมตืนขึนมาก็คงดีเหมือนกัน", "ตึกที่ทำงานสันมาก"):
        assert _seen(t), t


def test_indirect_language_round1_repaired():
    for t in ("ขอกดปิดเกมชีวิตนี้ได้ไหม", "ซื้อถ่านมาสามถุง ปิดหน้าต่างห้องหมดแล้ว", "im so done w everything, logging off for good",
              "my boyfriend said nobody would find me if I left", "เขาบอกว่าถ้าเราหนีไป จะไม่มีใครได้เห็นเราอีก"):
        assert _seen(t), t
    for t in ("ซื้อถ่านมาปิ้งหมูกระทะสามถุง", "logging off for the night, see you tomorrow", "what's the most painless way to get a tattoo",
              "ใครรับเลี้ยงแมวต่อได้บ้าง ย้ายไปอยู่คอนโดที่เลี้ยงไม่ได้"):
        assert not _seen(t), t


def test_red_team_file_is_not_used_to_tune_code():
    rows = [l.split("\t")[0] for l in (ROOT / "tests" / "adversarial" / "adversarial.tsv").read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.startswith("#")]
    assert len(rows) >= 20
    code = "".join(p.read_text(encoding="utf-8") for p in (ROOT / "core").glob("*.py"))
    assert not [t for t in rows if t in code]


def test_stress_harness_runs_small():
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import robustness_test
    r = robustness_test.run(300, seed=3)
    assert r["total"] == 300 and r["danger"]["rate"] > .9
