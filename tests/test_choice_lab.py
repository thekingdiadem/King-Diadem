"""Choice Lab (หน้า Universe): กดเลือกทางออกแล้วดู R = (D × E × T) / C ขยับ — ตัวเลขต้องมาจากสมการจริงใน AI/freedom_signal.py
หน้าเว็บห้ามคำนวณเอง ไม่งั้นจะกลายเป็นกราฟประกอบฉากที่ไม่ตรงกับ kernel"""
from pathlib import Path

from fastapi.testclient import TestClient

from AI.freedom_signal import CHOICE_LAB_BASE, choice_lab, compute_collapse_risk

PAGE = (Path(__file__).resolve().parent.parent / "static/king_diadem_universe.html").read_text(encoding="utf-8")


def test_baseline_is_the_master_equation():
    r = choice_lab([])
    assert r["now"]["R"] == compute_collapse_risk(**CHOICE_LAB_BASE)["R"] == 18
    assert r["now"]["risk_level"] == "CRITICAL" and r["drop_pct"] == 0


def test_each_action_moves_exactly_one_variable():
    base = choice_lab([])["now"]
    moved = {"ask": "C", "planb": "C", "shrink": "E", "stop": "D", "early": "T"}
    for aid, var in moved.items():
        now = choice_lab([aid])["now"]
        assert [k for k in "DETC" if now[k] != base[k]] == [var], aid
        assert now["R"] == base["R"] / 2                    # ทุกทางออกในตัวอย่างนี้ลด R ลงครึ่งหนึ่งพอดี


def test_all_actions_bring_risk_to_low_and_order_does_not_matter():
    ids = ["ask", "planb", "shrink", "stop", "early"]
    r = choice_lab(ids)
    assert r["now"]["R"] == 0.75 and r["now"]["risk_level"] == "LOW" and r["drop_pct"] == 96
    assert choice_lab(ids[::-1]) == r and choice_lab(ids + ["ask", "nope"]) == r


def test_api_and_page_do_not_compute_in_the_browser():
    import app as appmod
    c = TestClient(appmod.app)
    d = c.get("/api/choice-lab?on=ask,shrink").json()
    assert d["now"]["equation"] == "R = (0.6 × 0.5 × 30) / 2 = 4.5" and d["drop_pct"] == 75
    assert c.get("/api/choice-lab?on=" + "x," * 50).status_code == 200
    assert "/api/choice-lab?on=" in PAGE and 'id="cl-acts"' in PAGE
    lab = PAGE[PAGE.index("/* Choice Lab — ส่งชุดทางออก"):PAGE.index("load();\n})();", PAGE.index("/* Choice Lab — ส่งชุดทางออก"))]
    # ไม่มีค่าตั้งต้นหรือสูตรฝังในหน้าเว็บ — สมการและตัวเลขทั้งหมดมาจากคำตอบของเซิร์ฟเวอร์
    assert "0.6" not in lab and "n.equation" in lab and "n.risk_level" in lab
