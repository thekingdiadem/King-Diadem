"""DriftZero รอบสุ่ม 6: คำตอบต้องไม่ขัดกับที่คนเล่า · "ไม่ไหวแล้ว" เฉยๆ เป็นเรื่องใจ · ภาษาอังกฤษ"""
import pytest
from ENGINE.driftzero import audit, lyla_voice


def test_no_money_left_is_not_told_to_protect_money_left():
    a = lyla_voice(audit("เงินหมดแล้ว ร้านไปต่อไม่ไหว ไม่รู้จะทำยังไง"))
    assert a["verdict"] == "steady" and "เงินที่เหลืออยู่" not in a["lyla"]["th"]
    assert "จ่ายเร็วที่สุด" in a["asks"][0]["th"]


def test_just_not_coping_goes_to_lyla_not_debt_advice():
    a = audit("ไม่ไหวแล้ว")
    assert a["verdict"] == "steady" and a["talk"] and not a["steps"] and "1323" in a["summary"]["th"]


@pytest.mark.parametrize("t", ["we're going under and I can't pay my 3 staff", "my restaurant is about to collapse, $500 left"])
def test_english_sinking_business_gets_steady(t):
    assert audit(t)["verdict"] == "steady"
