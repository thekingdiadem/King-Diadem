"""หน้า /learn: บทเรียน 8 บท (ปรับจาก Interactive Tutorial ของเจ้าของโปรเจกต์) + โหมดฝึกจำลองวิกฤต
เดิมเกมจำลองเป็นตัวเลขตายตัว (Entropy 78 · Stability 28 ไม่ขยับ) — ตอนนี้คำนวณด้วยสมการเดียวกับระบบ"""
import re
from pathlib import Path

import pytest

from ENGINE.practice_sim import DAYS, SCENARIOS, WATERLINE, run, waterline

ROOT = Path(__file__).resolve().parent.parent


def test_waterline_formula_is_the_system_one():
    assert waterline({"E": 78, "S": 28, "R": 35}) == 28                      # ตัวอย่างในบทที่ 3
    assert waterline({"E": 90, "S": 10, "R": 5}) == 8                        # คำตอบแบบทดสอบบทที่ 3


@pytest.mark.parametrize("sid", sorted(SCENARIOS))
def test_same_choices_same_result(sid):
    seq = [o["id"] for o in SCENARIOS[sid]["options"][:4]] + [SCENARIOS[sid]["options"][0]["id"]]
    assert run(sid, seq) == run(sid, seq)
    r = run(sid, seq)
    assert r["done"] and len(r["log"]) == DAYS and r["summary"]["th"]


@pytest.mark.parametrize("sid", sorted(SCENARIOS))
def test_every_scenario_has_one_tempting_trap(sid):
    traps = [o for o in SCENARIOS[sid]["options"] if not o["reversible"]]
    assert len(traps) == 1 and traps[0]["closes"]


def test_the_trap_costs_more_than_the_careful_path():
    """ทางลัดที่ดูดีวันแรก ต้องเห็นราคาจริงในวันถัดไป (ดอกเบี้ย · ความไว้ใจ · ทางที่ถูกปิด)"""
    careful = run("shop", ["numbers", "customers", "team", "delivery", "numbers"])
    trap = run("shop", ["allin", "customers", "team", "customers", "team"])
    assert careful["W"] > trap["W"] + 10
    assert "delivery" in trap["closed"] and "numbers" in trap["closed"]
    assert run("jobloss", ["invest"])["collapsed"]                          # ลงทุนการันตี 20% → เงินเก็บหาย พังทันที
    hoard = run("pandemic", ["hoard", "sources", "minimize", "grow", "sources"])
    assert hoard["harm"] == 1 and any("Ethical Kernel" in s for s in hoard["summary"]["th"])


def test_repeating_one_path_gives_less_each_time():
    one = run("pandemic", ["share"] * 5)
    mixed = run("pandemic", ["share", "sources", "minimize", "grow", "share"])
    assert mixed["W"] > one["W"]
    assert any(e["repeat"] for e in one["log"])


def test_closed_or_unknown_choices_are_ignored():
    r = run("pandemic", ["hoard", "share", "share"])                       # share ถูกปิดแล้ว
    assert len(r["log"]) == 1


def test_api_is_free_and_stateless(client):
    lst = client.get("/api/practice").json()["scenarios"]
    assert {s["id"] for s in lst} == set(SCENARIOS)
    d = client.post("/api/practice", json={"scenario": "jobloss", "choices": ["rights", "talk"]}).json()
    assert d["result"]["day"] == 2 and d["result"]["choice_t"] >= 1
    assert "fx" not in str(d["scenario"]["options"])                       # ไม่เปิดตัวเลขผลลัพธ์ล่วงหน้า (ต้องเรียนจากการเล่น)
    assert client.post("/api/practice", json={"scenario": "nope", "choices": []}).status_code == 400


def test_learn_page_is_served_linked_and_csp_safe(client):
    r = client.get("/learn")
    assert r.status_code == 200 and "/api/practice" in r.text and "สภา 6 เสียง" in r.text
    assert "onclick" not in r.text
    assert 'href="/learn"' in (ROOT / "static" / "guide.html").read_text(encoding="utf-8")
    assert "/learn" in client.get("/sitemap.xml").text


def test_lessons_match_the_system_now():
    t = (ROOT / "static" / "learn.html").read_text(encoding="utf-8")
    assert "CIVIL" in t                                                     # สภามี 6 เสียงแล้ว (เดิม 5)
    assert "เส้นขั้นต่ำที่ห้ามให้ต่ำกว่า" in t                                 # Waterline ตามนิยามเจ้าของโปรเจกต์
    assert len(re.findall(r"\bok:\d", t)) == 8                               # 8 บท 8 แบบทดสอบ


def test_fate_doc_maps_every_axiom_to_the_code():
    t = (ROOT / "FATE.md").read_text(encoding="utf-8")
    for k in ("Logic over Persona", "Human Final Authority", "core/human_gate.py", "Know the 99. Respect the 1."):
        assert k in t
    assert "Nithikorn" not in t and "นิธิกร" not in t
