"""สภาเดียวของทั้งระบบ: หน้าเว็บ · ENGINE/council_engine · ENGINE/ai_council ใช้ 6 ที่นั่งชุดเดียวกัน + CIVIL ⬡"""
from AI.council_engine import COUNCIL_MEMBERS, COUNCIL_SEATS, COUNCIL_SIZE, COUNCIL_SYMBOLS
from core.kernel_voice import compose_council

SEATS = ["LYLA", "VEGA", "PATICCA", "TITAN", "COSMOS", "CIVIL"]


def test_registry_has_six_seats_with_civil():
    assert [s[0] for s in COUNCIL_SEATS] == SEATS and COUNCIL_SIZE == 6
    assert COUNCIL_SYMBOLS["CIVIL"] == "⬡" and "แรงกระเพื่อม" in COUNCIL_MEMBERS["CIVIL"]


def test_backend_councils_use_same_names():
    from ENGINE.council_engine import council_engine
    from ENGINE.ai_council import ai_council
    votes = council_engine({"action": "stabilize"}, {"risk_score": 80})["votes"]
    assert [v["member"] for v in votes] == SEATS
    voices = [v["voice"] for v in ai_council(context={"entropy": 80})["votes"]]
    assert sorted(voices) == sorted(SEATS)


def test_backend_decisions_unchanged():
    from ENGINE.ai_council import ai_council
    r = ai_council(food=0, money=0, context={"waterline": 10, "energy": 10, "safe_place": False})
    assert r["halt"] and r["final_action"].startswith("HALT")
    r = ai_council(food=1, money=500, risk="low", context={"waterline": 80, "energy": 80})
    assert r["final_action"] == "proceed_with_plan"


def test_civil_names_who_is_affected():
    r = compose_council("จะลาออกไปทำร้าน แต่ลูกยังเล็ก ภรรยาไม่ทำงาน")
    assert "CIVIL ⬡" in r and "ลูก" in r[r.index("CIVIL"):] and "เห็นตรงกัน 5/6" in r   # CIVIL ขอชะลอ


def test_civil_notices_carrying_alone():
    r = compose_council("ไม่มีใครรู้ว่าฉันเป็นหนี้ จะกู้ใหม่ดีไหม")
    civil = r[r.index("CIVIL"):r.index("มติสภา")]
    assert "คนเดียว" in civil and "1300" in civil


def test_llm_council_prompt_has_civil():
    from core.llm_gemini import COUNCIL_SYSTEM
    assert "สภา 6 เสียง" in COUNCIL_SYSTEM and "CIVIL ⬡" in COUNCIL_SYSTEM
