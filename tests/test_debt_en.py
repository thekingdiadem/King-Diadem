"""core/engine_bridge.debt_en — หนี้ภาษาอังกฤษ เดิมได้ "Write what happened in one sentence" """
import pytest
from core.engine_bridge import debt_en
from tests.conftest import FAKE_LLM


def _lines(t):
    return " | ".join(debt_en(t)["lines"])


def test_payment_gives_payoff_months():
    out = _lines("I owe 5000 dollars at 20% interest, paying 100 a month")
    assert "paid off in 109 months" in out        # −ln(1 − 0.01667·5000/100)/ln(1.01667) ≈ 108.4


def test_payment_below_interest_warns():
    assert "will never go down" in _lines("I owe 10000 at 24%, I can afford 150 a month")


def test_assumed_rate_is_marked():
    out = _lines("I owe $2,000 on my credit card and can afford 50 per month")
    assert "20% a year*" in out and "typical credit card rate" in out and "paid off in 67 months" in out


def test_monthly_rate_and_predatory_warning():
    out = _lines("payday loan 500 at 15% a month")
    assert "180% a year" in out and "predatory" in out


def test_no_payment_asks_for_it():
    assert "how much you can pay each month" in _lines("my student loan is 20k")


@pytest.mark.parametrize("text", [
    "I earn 3000 a month, rent 1200, car loan 500",    # งบรายเดือน ไม่ใช่ยอดหนี้
    "I owe 5000 and 3000 on two cards",                # หลายก้อน — ไม่จับคู่แบบเดา
    "I want to learn about loans",
])
def test_not_a_single_debt(text):
    assert debt_en(text) is None


def test_years_and_card_counts_are_not_amounts():
    assert debt_en("I borrowed 10k for 5 years at 8%, paying 200 a month")["data"]["balance"] == 10000
    assert debt_en("I have 2 credit cards with 4000 debt")["data"]["balance"] == 4000


def test_chat_answer(client):
    FAKE_LLM["mode"] = "fail"
    out = client.post("/run", json={"input": "I owe 5000 dollars at 20% interest, paying 100 a month"}).json()["ai_response"]
    assert "paid off in 109 months" in out and "Write what happened" not in out
    assert out.count("\n3) ") == 1 and "\n4) " not in out          # ไม่เกิน 3 ทาง
