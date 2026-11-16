"""DriftZero: คนที่กำลังจะล้ม ได้ "ตั้งหลักก่อน" ไม่ใช่แบบฟอร์มองค์กร

เจ้าของโปรเจกต์ลองพิมพ์ "ธุรกิจกำลังจะพังขาดทุนต่อเนื่อง เงินเหลือ3000 กู้ใครก็ๆม่ได้แล้วกำลังล้ม"
แล้วได้ "Waterline คือเท่าไหร่ · DHD · ใครเซ็นรับผิดชอบ" ทั้งที่บอกตัวเลขมาแล้ว และกำลังจะไม่ไหว
"""
import pytest

from ENGINE.driftzero import audit, follow_up

OWNER = "ธุรกิจกำลังจะพังขาดทุนต่อเนื่อง เงินเหลือ3000 กู้ใครก็ๆม่ได้แล้วกำลังล้ม"


@pytest.mark.parametrize("t", [OWNER, "my shop is going under, 200 dollars left and no one will lend me money",
                               "ร้านจะเจ๊งแล้ว ไม่รู้จะทำยังไง หนี้เต็มไปหมด"])
def test_sinking_person_gets_steady_not_a_form(t):
    a = audit(t)
    assert a["verdict"] == "steady" and a["talk"]
    assert len(a["asks"]) == 1                                   # ถามแค่ข้อเดียว
    words = " ".join(q["th"] + q["en"] for q in a["asks"])
    assert "Waterline" not in words and "DHD" not in words and "รับผิดชอบ" not in words
    assert len(a["steps"]) >= 3


def test_uses_the_number_they_already_gave():
    a = audit(OWNER)
    assert "3,000" in a["summary"]["th"] and "3,000" in a["asks"][0]["th"]


def test_answer_turns_into_runway_days_and_no_more_questions():
    a = audit(OWNER)
    r = follow_up(a["text"], [q["key"] for q in a["asks"]], "วันละ 500 ไม่มีเงินเข้าเลย")
    assert r["verdict"] == "steady" and r["runway_days"] == 6 and r["asks"] == []
    assert "6 วัน" in r["summary"]["th"]


def test_steady_mentions_safe_help_and_warns_against_loan_sharks():
    s = " ".join(x["th"] for x in audit(OWNER)["steps"])
    assert "1323" in s and "นอกระบบ" in s


@pytest.mark.parametrize("t", ["จะใช้เงินสำรองทั้งหมดขยาย 10 สาขาในปีนี้", "บริษัทจะลงทุน 2 ล้านเปิดโรงงานใหม่"])
def test_organisation_plans_still_go_through_gates(t):
    assert audit(t)["verdict"] in ("ask", "stop", "pass")


def test_life_danger_still_wins_over_steady():
    assert audit("ธุรกิจพังหมดแล้ว หมดทาง อยากตาย")["verdict"] == "urgent"
