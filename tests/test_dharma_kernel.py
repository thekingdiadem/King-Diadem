"""KERNEL/dharma-governance-kernel.md ต้องใช้ได้จริง — ทุกหัวข้อธรรมในเอกสารมีโค้ดทำงานอยู่

เดิม: โพธิปักขิยธรรม 37 (หัวข้อ 15–16) มีแค่ในเอกสาร — ไม่มี ENGINE/bodhipakkhiya_engine.py
ช่องนี้คิดจาก E/R/S อย่างเดียว "ลูกกลืนถ่านกระดุม" "เอาเงินเก็บทั้งหมดไปลงคริปโต" ได้ "PEACE — ดำเนินการได้"
โยนิโสมนสิการ "ทุกคำตอบใช้ครบ 4 วิธี" แต่โค้ดเลือกวิธีเดียว · ชื่อ K1–K14 ในเอกสารไม่ตรงกับโค้ด
"""
import re
from pathlib import Path

import pytest

from core.king_diadem_core import quick_assess
from ENGINE.bodhipakkhiya_engine import BOJJHANGA, bojjhanga_loop, guardian_check, structural_check
from ENGINE.yonisomanasikara_engine import detect_bias, four_ways

DOC = (Path(__file__).resolve().parent.parent / "KERNEL" / "dharma-governance-kernel.md").read_text(encoding="utf-8")
HS = {"entropy": 40, "resource": 50, "stability": 60}


# ── โพธิปักขิยธรรม 37 · 6 layer ──────────────────────────────────────────
def test_six_layers_match_the_document():
    layers = structural_check("วันนี้อากาศดี", HS)
    assert [L["dhamma"] for L in layers] == ["สติปัฏฐาน 4", "สัมมัปปธาน 4", "อิทธิบาท 4", "อินทรีย์ 5", "พละ 5", "มรรคมีองค์ 8"]
    names = {x["name"] for L in layers for x in L["items"]}
    assert {"กาย", "เวทนา", "จิต", "ธรรม"} <= names                                  # สติปัฏฐาน 4
    assert {"สังวรปธาน", "ปหานปธาน", "ภาวนาปธาน", "อนุรักขนาปธาน"} <= names          # สัมมัปปธาน 4
    assert {"ฉันทะ", "วิริยะ", "จิตตะ", "วิมังสา"} <= names                           # อิทธิบาท 4
    assert BOJJHANGA == ("สติ", "ธัมมวิจยะ", "วิริยะ", "ปีติ", "ปัสสัทธิ", "สมาธิ", "อุเบกขา")   # โพชฌงค์ 7
    for L, role in zip(layers, ("DRIFT_DETECTION", "GOVERNANCE_GATE", "EXECUTION_KERNEL", "CAPABILITY_LAYER", "FORCE_LAYER", "FULL_STACK")):
        assert L["role"] == role and role in DOC


@pytest.mark.parametrize("text,verdict", [
    ("วันนี้อากาศดี", "PEACE"), ("ขอสูตรแกงเขียวหวาน", "PEACE"),
    ("อยากตาย", "STOP"), ("ลูก 2 ขวบกลืนถ่านกระดุม", "STOP"),
    ("จะเอาเงินเก็บทั้งหมดไปลงคริปโต", "PAUSE"), ("โมโหมาก จะลาออกคืนนี้เลย", "PAUSE"),
    ("ไม่มีข้าวกินมา 3 วัน", "STABILIZE"),
])
def test_verdict_reads_the_message_not_only_the_state(text, verdict):
    assert quick_assess(text, HS)["bodhi_verdict"].startswith(verdict)


def test_low_structure_stabilizes_and_routes_to_survival():
    g = guardian_check("ไม่รู้จะทำยังไงดี", {"entropy": 90, "resource": 10, "stability": 10})
    assert g["recommend_route"] == "survival" and g["final_verdict"].startswith("STABILIZE")


def test_bojjhanga_loop_stops_at_first_unmet_factor():
    g = guardian_check("โมโหมาก จะลาออกคืนนี้เลย", HS)
    assert g["bojjhanga"]["stopped_at"] == "ปัสสัทธิ" and not g["peace"]
    assert guardian_check("วันนี้อากาศดี", HS)["bojjhanga"]["complete"]


def test_deterministic():
    t = "จะเอาเงินเก็บทั้งหมดไปลงคริปโต"
    assert guardian_check(t, HS) == guardian_check(t, HS)


def test_failed_dhamma_reach_the_llm_as_internal_context():
    q = quick_assess("จะเอาเงินเก็บทั้งหมดไปลงคริปโต", HS)
    assert "[โพธิปักขิยธรรม:" in q["wise_ctx"] and "สัทธา–ปัญญา" in q["wise_ctx"]
    assert "โพธิปักขิยธรรม" not in quick_assess("วันนี้อากาศดี", HS)["wise_ctx"]


def test_run_result_carries_the_real_verdict(client, monkeypatch):
    monkeypatch.setenv("KD_AI", "off")
    d = client.post("/run", json={"input": "ลูก 2 ขวบกลืนถ่านกระดุม"}).json()
    assert d["bodhipakkhiya"].startswith("STOP")


# ── โยนิโสมนสิการ 4 วิธี (หัวข้อ 10 · 14) ───────────────────────────────────
def test_four_ways_run_in_document_order():
    fw = four_ways("อยากได้ไอโฟนใหม่ จะกู้มาซื้อ", HS)
    assert [n for n, _ in fw["steps"]] == ["สืบสาวเหตุปัจจัย", "แยกแยะส่วนประกอบ", "อริยสัจ 4", "รู้เท่าทันธรรมดา"]
    assert fw["root_cause"] == "craving" and "ตัณหา" in fw["steps"][0][1]
    assert "ทุกข์" in fw["steps"][2][1] and "มรรค" in fw["steps"][2][1]


def test_bandwagon_and_denial_biases():
    assert {"bandwagon", "denial"} <= {b["bias"] for b in detect_bias("ทุกคนก็ทำกัน เดี๋ยวก็ดีเอง")}


def test_four_ways_attached_only_when_there_is_something_to_think_about():
    assert "โยนิโสมนสิการ 4 วิธี" in quick_assess("ทุกคนก็ทำกัน เดี๋ยวก็ดีเอง", HS)["wise_ctx"]
    assert "โยนิโสมนสิการ 4 วิธี" not in quick_assess("วันนี้อากาศดี", HS)["wise_ctx"]


# ── ปฏิจจสมุปบาท (หัวข้อ 9) ─────────────────────────────────────────────
def test_paticcasamuppada_functions_named_in_doc_exist():
    from ENGINE.paticcasamuppada_engine import llm_note, suffering_infrastructure
    p = suffering_infrastructure("อยากได้ไอโฟนใหม่ จะกู้มาซื้อ", HS)
    assert {"root_cause", "kill_zone", "nirvana_mode", "uap"} <= set(p)
    assert "suffering_infrastructure" in DOC and "llm_note" in DOC and llm_note(p)


# ── K1–K14 (หัวข้อ 12) ตรงกับโค้ด ────────────────────────────────────────
def test_kernel_table_matches_vega_kernels():
    from core.vega_kernels import KERNELS
    sec = DOC[DOC.index("## 12. Kernel Modules"):DOC.index("## 13. System Goal")]
    for kid, name, *_ in KERNELS:
        assert re.search(rf"\| {kid} {re.escape(name)} \|", sec), (kid, name)


def test_doc_points_only_to_code_that_exists():
    import importlib
    for mod, fn in (("ENGINE.bodhipakkhiya_engine", "guardian_check"), ("ENGINE.bodhipakkhiya_engine", "structural_check"),
                    ("ENGINE.bodhipakkhiya_engine", "bojjhanga_loop"), ("ENGINE.yonisomanasikara_engine", "four_ways"),
                    ("ENGINE.yonisomanasikara_engine", "wise_attention"), ("core.king_diadem_core", "quick_assess")):
        assert hasattr(importlib.import_module(mod), fn) and fn in DOC
    assert "ไม่มีไฟล์ `ENGINE/bodhipakkhiya_engine.py`" not in DOC and "analyze_chain" not in DOC


def test_king_diadem_kernel_doc_matches_dharma_doc():
    """KERNEL/king-diadem-kernel.md เป็นสำเนาหัวข้อ 1–15 — เดิมยังอ้าง analyze_chain() และชื่อ K1–K14 เก่า"""
    king = (Path(__file__).resolve().parent.parent / "KERNEL" / "king-diadem-kernel.md").read_text(encoding="utf-8")
    assert "analyze_chain" not in king and "Compassion Default" not in king and "report_url` always" not in king
    for sec in ("## 9. Paticcasamuppada", "## 12. Kernel Modules", "## 14. โยนิโสมนสิการ"):
        a, b = king.index(sec), DOC.index(sec)
        assert king[a:a + 600] == DOC[b:b + 600], sec
    assert "หัวข้อ 16" in king
