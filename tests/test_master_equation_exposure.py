"""AI/freedom_signal — R = (D × E × T) / C · Risk = Drift × Exposure × Time / Remaining Choice
เอกสารเคยเขียน Drift × Exposure / Remaining Choice (ไม่มีเวลา) ส่วนโค้ดเป็น (D × T) / C (ไม่มี Exposure)"""
import pytest
from AI.freedom_signal import compute_collapse_risk


@pytest.mark.parametrize("d, t, c", [(0.0, 1, 5), (0.3, 5, 3), (0.8, 10, 1), (0.5, 30, 2), (1.0, 100, 7)])
def test_exposure_one_is_the_old_equation(d, t, c):
    old = round(d * t / c, 6)
    assert compute_collapse_risk(d, t, c)["R"] == old
    assert compute_collapse_risk(d, t, c, exposure=1)["R"] == old


def test_exposure_scales_risk():
    assert compute_collapse_risk(0.6, 10, 2, exposure=0.5)["R"] == 1.5
    assert compute_collapse_risk(0.6, 10, 2, exposure=0)["R"] == 0
    assert compute_collapse_risk(0.6, 10, 2, exposure=0.5)["equation"] == "R = (0.6 × 0.5 × 10) / 2 = 1.5"


def test_time_still_grows_risk():
    a = compute_collapse_risk(0.5, 1, 2, exposure=0.8)["R"]
    b = compute_collapse_risk(0.5, 10, 2, exposure=0.8)["R"]
    assert b == 10 * a


def test_zero_choice_is_collapse_even_with_zero_exposure():
    r = compute_collapse_risk(0.5, 10, 0, exposure=0)
    assert r["collapse"] is True and r["risk_level"] == "COLLAPSE"


@pytest.mark.parametrize("bad, used", [(None, 1.0), ("x", 1.0), (float("nan"), 1.0), (-2, 0.0), (5, 1.0)])
def test_bad_exposure_is_clamped_safely(bad, used):
    assert compute_collapse_risk(0.5, 4, 2, exposure=bad)["E"] == used    # อ่านไม่ได้ → ถือว่าโดนเต็มที่


def test_docs_and_code_use_the_same_equation():
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    for f in ("README.md", "WHITEPAPER.md", "SYSTEM_OVERVIEW.md"):
        s = (root / f).read_text(encoding="utf-8")
        assert "Risk = Drift × Exposure × Time / Remaining Choice" in s, f
        assert "Risk = Drift × Exposure / Remaining Choice" not in s, f
