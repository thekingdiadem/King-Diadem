"""core/engine_bridge — ค่างวดที่ผู้ใช้บอกต้องถูกใช้คำนวณ และดอกที่ซ่อนในยอดคืนต้องไม่กลายเป็น 0%"""
import pytest
from core.engine_bridge import _debt, _payment
from tests.conftest import FAKE_LLM


def _lines(text):
    return " | ".join(_debt(text)["lines"])


def test_monthly_payment_gives_payoff_months():
    out = _lines("หนี้บัตร 50000 ดอก 18% ผ่อนเดือนละ 2000 กี่เดือนหมด")
    assert "หมดใน 32 เดือน" in out              # สูตรผ่อนชำระ: −ln(1 − 0.015·50000/2000)/ln(1.015) ≈ 31.6
    assert "บอกรายได้" not in out                 # เดิมไม่ใช้ค่างวด แต่ถามรายได้แทน


def test_zero_interest_payoff():
    assert "หมดใน 10 เดือน" in _lines("กู้ 100000 ดอกเบี้ย 0% ผ่อน 10000 ต่อเดือน")


def test_payment_below_interest_warns_debt_never_shrinks():
    out = _lines("หนี้ 30000 ดอก 25% ต่อปี จ่ายได้เดือนละ 500")
    assert "ยอดหนี้จะไม่ลดเลย" in out and "625" in out
    assert _debt("หนี้ 30000 ดอก 25% ต่อปี จ่ายได้เดือนละ 500")["data"]["income"] is None   # 500 ไม่ใช่รายได้


@pytest.mark.parametrize("text, pay", [
    ("ผ่อนเดือนละ 2,000", 2000), ("ผ่อน 1.5 หมื่น ต่อเดือน", 15000), ("โปะได้เดือนละ 3k", 3000),
    ("ใช้จ่ายเดือนละ 15000", None), ("รายจ่ายเดือนละ 9000", None), ("ผ่อนเดือนละ 12 งวด", None),
])
def test_payment_parser(text, pay):
    assert _payment(text) == pay


def test_multiple_debts_do_not_share_one_installment():
    out = _lines("หนี้บ้าน 1,200,000 ผ่อนเดือนละ 12,000 หนี้บัตร 50,000")
    assert "หมดใน" not in out                     # ค่างวดเป็นของหนี้บ้าน ไม่ใช่ทั้งหมด


def test_repay_more_than_borrowed_shows_real_interest():
    d = _debt("ยืม 1000 คืน 1500 ภายใน 1 อาทิตย์ ดอกกี่เปอร์เซ็นต์")
    out = " | ".join(d["lines"])
    assert "ดอก 0%" not in out
    assert "ดอก 500 บาท (50% ภายใน 1 อาทิตย์" in out and "2,607% ต่อปี" in out
    assert "15% ต่อปี" in out                       # เกินที่กฎหมายกำหนด


def test_repay_without_period_and_equal_repay():
    assert "ดอก 500 บาท (10%)" in _lines("ยืมเพื่อน 5000 ต้องคืน 5500")
    assert "ดอก 0%*" in _lines("ยืมแม่ 3000 คืน 3000")


def test_fixed_total_loan_is_not_amortized():
    out = _lines("ยืม 2,000 คืน 2,600 ใน 30 วัน ผ่อนเดือนละ 1000")
    assert "หมดใน" not in out                     # ยอดคืนตายตัว — คิดแบบผ่อนจะได้ดอกรวมผิด


def test_chat_answer_uses_payment(client):
    FAKE_LLM["mode"] = "fail"
    r = client.post("/run", json={"input": "หนี้บัตร 50000 ดอก 18% ผ่อนเดือนละ 2000 กี่เดือนหมด"}).json()
    assert "หมดใน 32 เดือน" in r["ai_response"]
