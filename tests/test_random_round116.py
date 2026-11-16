"""รอบสุ่ม 116: คนหายที่มีอายุหรือคำขยายคั่น (อังกฤษ)"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "my 15 year old daughter has been missing since yesterday", "my 7-year-old son is missing",
    "my elderly father went missing this morning", "my little brother is missing",
])
def test_missing_with_age_is_urgent(q):
    assert assess(q)["risk_shown"] >= 75


@pytest.mark.parametrize("q", ["my 15 year old daughter is missing her friends at camp", "my little brother is missing a tooth"])
def test_missing_something_stays_calm(q):
    assert assess(q)["risk_shown"] < 60
