"""DriftZero รอบสุ่ม 1: กู้นอกระบบ · จำนองบ้านไปเล่นคริปโต · "drowning in debt" · "ร้านจะเจ๊ง" """
import pytest
from ENGINE.driftzero import audit, follow_up


def _stops(a):
    return [g["id"] for g in a["gates"] if g["status"] == "stop"]


@pytest.mark.parametrize("t", ["จะกู้นอกระบบมาจ่ายเงินเดือนพนักงาน", "we will borrow from a loan shark to pay rent",
                               "จะเอาบ้านไปจำนองเพื่อลงทุนคริปโต"])
def test_betting_the_house_or_loan_sharks_stops(t):
    # เดิมผ่านทุกด่าน แค่ถามข้อมูลเพิ่ม
    assert "E2" in _stops(audit(t))


@pytest.mark.parametrize("t", ["we will never use loan sharks, we pay staff from reserves", "ร้านเราไม่กู้นอกระบบเด็ดขาด"])
def test_refusing_loan_sharks_is_a_good_policy_not_a_stop(t):
    assert "E2" not in _stops(audit(t))


@pytest.mark.parametrize("t", ["I'm drowning in debt, 3 credit cards maxed, what should I do", "ร้านจะเจ๊ง เหลือ 5000"])
def test_sinking_gets_steady(t):
    # "drowning in debt ... what should I do" เคยได้หน้า "วิธีใช้"
    assert audit(t)["verdict"] == "steady"


def test_dont_know_answer_does_not_restart_the_form():
    a = audit("ร้านจะเจ๊ง เหลือ 5000")
    r = follow_up(a["text"], [q["key"] for q in a["asks"]], "ไม่รู้ ไม่ได้จด")
    assert r["verdict"] == "steady" and r["asks"] == []


def test_question_about_risk_is_not_sinking():
    assert audit("ร้านจะเจ๊งไหมถ้าขึ้นราคา 10%")["verdict"] != "steady"
