"""FATE™ Axiom Audit ต้องมีที่เดียว — เดิมรายงานมีชุดตรวจของตัวเอง ส่วน core/fate_core.py ไม่มีโค้ดไหนเรียกใช้
(สองที่แก้ไม่ตรงกันได้: ชื่อ axiom 5 ในไฟล์หนึ่งเป็น "Explainability = 100%" อีกที่เป็น "= Usability")"""
import pathlib

from core import fate_core
from report_engine import _run_fate_audit


def test_report_audit_is_fate_core():
    r = {"route": "risk", "risk_score": 80, "ai_response": "x" * 60}
    assert _run_fate_audit(r, "hi") == fate_core.axiom_audit(r)


def test_axiom_names_come_from_one_table():
    out = fate_core.axiom_audit({"ai_response": "x" * 60})
    assert [c["name"] for c in out["checks"]] == [fate_core.AXIOMS[i].split(" — ")[0] for i in range(1, 7)]
    prompt = (pathlib.Path(__file__).resolve().parent.parent / "core" / "llm_gemini.py").read_text(encoding="utf-8")
    for i in range(1, 7):
        assert f"Axiom {i} — {fate_core.AXIOMS[i].split(' — ')[0]}" in prompt


def test_verdicts():
    assert fate_core.axiom_audit({"risk_score": 80, "ai_response": "x" * 60})["verdict"] == "REJECTED"
    assert fate_core.axiom_audit({"risk_score": 10, "ai_response": "x" * 60})["verdict"] == "APPROVED"
    assert fate_core.axiom_audit({})["verdict"] == "DEFERRED"
    assert fate_core.axiom_audit(None)["verdict"] == "DEFERRED"
