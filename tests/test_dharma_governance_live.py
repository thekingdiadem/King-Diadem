"""Dharma Governance ทำงานจริงตามที่ KERNEL/dharma-governance-kernel.md เขียน — ไม่ใช่แค่เอกสาร"""
from core.king_diadem_core import quick_assess, core_status
from ENGINE.collapse_predictor import predict_collapse


def test_all_three_engines_load():
    s = core_status()
    assert s["bodhipakkhiya"] == "ok" and s["paticcasamuppada"] == "ok" and s["yonisomanasikara"] == "ok"


def test_quick_assess_produces_causal_and_wise_context():
    r = quick_assess({"text": "อยากลาออกไปเปิดร้าน ลงทุนเงินเก็บทั้งหมด"}, {})
    assert r["causal_ctx"] and r["bodhi_verdict"]
    assert "yoniso_four" in r


def test_collapse_warning_matches_documented_contract():
    assert predict_collapse(90).startswith("high") and predict_collapse(30).startswith("low")


def test_app_injects_governance_context_before_llm():
    src = open("app.py", encoding="utf-8").read()
    i = src.index("extra_ctx = \" \".join(")
    block = src[i:i + 400]
    for k in ("paticca_ctx", "wise_ctx_str", "risk_ctx", "collapse_ctx"):
        assert k in block, k
