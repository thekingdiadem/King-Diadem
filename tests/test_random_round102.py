"""รอบสุ่ม 102: เจ้าหนี้ขู่จะเผาบ้าน/ทำร้าย (อังกฤษ)"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", ["loan shark said he'll burn my house", "they said they'll kill me if i don't pay"])
def test_debt_threat_in_english_is_urgent(q):
    # "loan shark said he'll burn my house" เคยได้ 0 ขณะที่ฉบับไทยได้ 85
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", ["he said he'll break my heart", "the lender said they'll come for my car", "he said he'll hurt my feelings"])
def test_figurative_or_property_is_calm(q):
    assert assess(q)["risk_shown"] < 60


@pytest.mark.parametrize("q", ["my mom said she'll kill me if i'm late", "she said she'll kill me if i spoil the ending"])
def test_family_idiom_not_escalated(q):
    assert assess(q)["risk_shown"] < 80
