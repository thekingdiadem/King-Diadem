"""ชุดข้อความปิดตา (tests/blind/blind.tsv) และสกอร์บอร์ดบนหน้า /architecture

ชุดกันถอยหลังผ่าน 100% เสมอ เพราะทุกบรรทัดถูกเพิ่มพร้อมการแก้ตัวตรวจจับ — บอกไม่ได้ว่าระบบเก่งแค่ไหนกับข้อความใหม่
ชุดปิดตาวัดตรงนั้น แต่จะมีค่าก็ต่อเมื่อไม่มีใครเอาไปจูน และตัวเลขที่โชว์ตรงกับผลจริงเสมอ
"""
import json
import os
import re

from scripts import blind_score as bs

ROOT = bs.ROOT


def test_blind_set_is_well_formed():
    rows = bs.load()
    assert len(rows) >= 100
    labels = {r["label"] for r in rows}
    assert labels == set(bs.LABELS)                                   # ครบทุกหมวด รวมข้อความปกติ
    assert sum(r["label"] == "none" for r in rows) >= 20              # ต้องมีข้อความปกติพอจะวัดการเตือนเกิน
    texts = [r["text"] for r in rows]
    assert len(texts) == len(set(texts))


def test_detectors_are_not_tuned_on_blind_text():
    """ห้ามคัดลอกข้อความปิดตาไปไว้ในโค้ดตัวตรวจจับ หรือในชุดกันถอยหลัง — ไม่งั้นมันไม่ใช่ข้อสอบปิดตาแล้ว
    (ข้อที่ตั้งใจแก้ให้ย้ายออกจาก blind.tsv ไป tests/corpus/messages.tsv ก่อน)"""
    blind = {r["text"] for r in bs.load()}
    src = []
    for d in ("core", "AI", "ENGINE", "AI_KERNEL", "KERNEL", "SECURITY", "DOMAINS", "WORLD_MODEL"):
        for base, _, files in os.walk(os.path.join(ROOT, d)):
            src += [os.path.join(base, f) for f in files if f.endswith(".py")]
    src.append(os.path.join(ROOT, "app.py"))
    code = "\n".join(open(p, encoding="utf-8").read() for p in src)
    corpus = open(os.path.join(ROOT, "tests", "corpus", "messages.tsv"), encoding="utf-8").read()
    corpus_texts = {line.split("\t")[0].strip() for line in corpus.splitlines() if line and not line.startswith("#")}
    assert not [t for t in blind if t in code]
    assert not blind & corpus_texts


def test_scoreboard_matches_real_result():
    """ตัวเลขบนหน้า /architecture ต้องตรงกับผลจริงเสมอ — แก้ตัวตรวจจับแล้วให้รัน python scripts/blind_score.py --write"""
    shown = json.load(open(bs.OUT, encoding="utf-8"))
    assert shown == bs.score(bs.load())


def test_score_counts_add_up():
    s = bs.score(bs.load())
    for c, v in s["classes"].items():
        assert v["tp"] + v["fn"] == v["n"] == sum(r["label"] == c for r in bs.load())
    assert s["danger_missed"]["of"] == sum(r["label"] in bs.DANGER for r in bs.load())


def test_detected_maps_assess_output():
    assert bs.detected({"crisis": True}) == {"self_harm"}
    assert bs.detected({"topics": ["scam"], "scam": ["otp"]}) == {"scam"}
    assert bs.detected({"disaster": {"kind": "intruder"}}) == {"violence"}
    assert bs.detected({"disaster": {"kind": "flood"}}) == {"emergency"}
    assert bs.detected({"intl_urgent": [("medical", "health_emergency")]}) == {"emergency"}
    assert bs.detected({"topics": ["lonely", "job"]}) == set()                 # หัวข้อทั่วไปไม่นับว่าตรวจเจอภัย


def test_architecture_page_shows_scoreboard():
    html = open(os.path.join(ROOT, "static", "architecture.html"), encoding="utf-8").read()
    assert 'id="score"' in html and "/static/blind_score.json" in html
    assert re.search(r"ตัวตรวจจับที่ไม่ใช้ AI", html)                            # บอกตรงๆ ว่าวัดอะไร ไม่อ้างเกินจริง
