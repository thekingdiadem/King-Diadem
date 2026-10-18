"""ตัวเลขเงินและค่าขอบใน ENGINE/core ที่เคยคิดผิด"""
from core.emptiness_guard import classify_severity, strip_label
from core.engine_bridge import _budget, _pct, _spend_items, analyze, budget_en
from ENGINE.resource_estimator import estimate_resources
from ENGINE.survival_advisor import survival_advisor


def test_million_unit_in_spend_items():
    """"ค่าเทอม 1 ล้าน" เคยอ่านเป็น 1 บาท → บอกว่าเหลือเงิน ทั้งที่ขาด 920,000"""
    assert _spend_items("ค่าเทอม 1 ล้าน") == [1_000_000.0]
    assert "ขาด 920,000" in _budget("เงินเดือน 1 แสน ผ่อนคอนโด 2 หมื่น ค่าเทอม 1 ล้าน")["lines"][0]


def test_stated_total_smaller_than_listed_item_does_not_drop_it():
    assert "300 left" in budget_en("I make 4000, rent 3,500. I spend 200")["line"]
    assert "1,000 left" in budget_en("I make 4000, I spend 3000, rent 1000")["line"]      # ยอดรวมครอบคลุมแล้ว ไม่นับซ้ำ


def test_percent_never_rounds_up_to_100():
    assert _pct(0.9967) == "99.7%" and _pct(0.5) == "50%" and _pct(0.05) == "5.0%"


def test_equal_income_and_expense_is_not_called_a_shortfall():
    lines = " ".join(analyze("ยืมเพื่อน 5000 เงินเดือน 15000 รายจ่าย 15000")["lines"])
    assert "เท่ากับรายจ่ายพอดี" in lines and "ไม่พอรายจ่าย" not in lines


def test_engine_edge_inputs():
    assert "RISK_HIGH" not in survival_advisor(food=5, money=1000, risk=None)["warnings"]   # ไม่รู้ค่า ≠ เสี่ยงสูง
    assert estimate_resources(food=30, money=1000, daily_expense=-5)["money_days"] < 999
    assert classify_severity(-0.001)["level"] == "S0"
    assert strip_label(None)["choice_count"] == 1
