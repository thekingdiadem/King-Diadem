"""core/choice_dynamics — Choice(t+Δ) = Choice(t) − Drift(t) − Entropy(t) + Intervention(t) · Drift = Σ DHD · domain ของตัวแปรระบบ"""
import pytest
from core.choice_dynamics import (
    accumulate_drift, choice_next, steps_to_collapse, validate_state, check_invariants,
)


def test_drift_is_sum_of_dhd_and_never_negative():
    assert accumulate_drift([0.1, 0.2, 0.3]) == 0.6
    assert accumulate_drift([0.5, -0.4, "x", None]) == 0.5   # DHD ติดลบ/อ่านไม่ได้ไม่ลด drift
    assert accumulate_drift(None) == 0.0


def test_choice_next_follows_equation_and_stays_natural():
    r = choice_next(5, 1, 1, 0)
    assert r["choice_next"] == 3 and r["status"] == "STABLE"
    r = choice_next(3, 0.2, 0, 0)            # ทางเลือกที่ถูกกัดไปบางส่วนไม่นับ
    assert r["choice_next"] == 2 and r["choice_next_raw"] == 2.8
    r = choice_next(3, 0.1, 0.2, 0.3)        # ทศนิยมลอยตัวไม่ทำให้หายไป 1 ทาง
    assert r["choice_next"] == 3


def test_choice_next_warns_and_pauses():
    w = choice_next(2, 1, 0, 0)
    assert w["choice_next"] == 1 and w["early_warning"] and not w["system_pause"]
    z = choice_next(1, 1, 1, 0)
    assert z["choice_next"] == 0 and z["system_pause"] and z["status"] == "COLLAPSE"


def test_intervention_greater_than_drift_is_stabilizing():
    r = choice_next(2, 0.5, 0, 1)
    assert r["stabilizing"] and r["choice_next"] >= 2


def test_bad_input_is_treated_as_no_choice():
    assert choice_next("?", 0, 0, 0)["system_pause"] is True
    assert choice_next(3, -5, -5, -5)["choice_next"] == 3        # ค่าติดลบตัดเป็น 0


@pytest.mark.parametrize("args, steps", [
    ((5, 1, 0, 0), 5),
    ((3, 0.5, 0, 0), 5),
    ((3, 1, 0, 1), None),
    ((0, 1, 0, 0), 0),
])
def test_steps_to_collapse(args, steps):
    assert steps_to_collapse(*args) == steps


def test_steps_to_collapse_matches_stepping():
    c, d = 4, 0.7
    for k in range(1, 20):
        c = choice_next(c, d, 0, 0)["choice_next_raw"]
        if c < 1:
            break
    assert steps_to_collapse(4, 0.7, 0, 0) == k


def test_state_in_domain_is_valid():
    s = {"Choice": 2, "Cycle": 0, "Seal": 1, "Motion": 1, "Authority": 0.0, "Force": 3.5,
         "Existence": 9, "Decision": 1, "Silence": 1, "SYSTEM_PAUSE": 0}
    r = validate_state(s)
    assert r["valid"] and r["violations"] == [] and r["invariant_violations"] == []


@pytest.mark.parametrize("key, bad", [
    ("Choice", -1), ("Choice", 1.5), ("Choice", True),
    ("Cycle", 2), ("Seal", 0.5), ("Motion", True), ("Decision", 0.7), ("Silence", -1), ("SYSTEM_PAUSE", "1"),
    ("Authority", -0.1), ("Force", float("inf")), ("Force", float("nan")),
    ("Existence", 9.01), ("Existence", -1), ("Existence", "5"),
])
def test_state_out_of_domain_is_rejected(key, bad):
    r = validate_state({key: bad})
    assert not r["valid"] and r["violations"][0].startswith(key)


def test_invariants_from_existing_canon():
    assert check_invariants({"Choice": 1, "Cycle": 1}) == ["|Choice| ≥ 1 ⇒ Cycle = 0"]
    assert check_invariants({"Choice": 0, "SYSTEM_PAUSE": 0}) == ["Choice = 0 ⇒ SYSTEM_PAUSE = 1"]
    assert check_invariants({"Choice": 2, "Silence": 0}) == []   # เงียบหรือไม่ขึ้นกับปัจจัยพื้นฐานด้วย
    assert validate_state("x")["valid"] is False

def test_check_invariants_ignores_non_dict():
    assert check_invariants(None) == [] and check_invariants("x") == []


def test_pause_blocks_decision_and_spec_covers_every_variable():
    from core.choice_dynamics import STATE_SPEC, BINARY_VARS, NONNEG_VARS
    assert check_invariants({"SYSTEM_PAUSE": 1, "Decision": 1}) == ["SYSTEM_PAUSE = 1 ⇒ Decision = 0"]
    assert check_invariants({"SYSTEM_PAUSE": 1, "Decision": 0}) == []
    assert set(STATE_SPEC) == {"Choice", "Existence", *BINARY_VARS, *NONNEG_VARS}


def test_decision_quality_is_a_binary_gate():
    from core.emptiness_guard import decision_quality
    assert decision_quality(1.0, 1.0)["decision"] == 1          # 1.0 → VIABLE
    assert decision_quality(0.3, 1.0)["decision"] == 0          # DEGRADED → ระงับ
    assert decision_quality(0.1, 1.0)["decision"] == 0          # COLLAPSED


def test_compounded_drift_one_year():
    from core.choice_dynamics import compounded_drift
    assert compounded_drift(365) == pytest.approx(0.44, abs=0.001)      # (1.001)^365 − 1
    assert compounded_drift(0) == 0 and compounded_drift(None) == 0


def test_time_windows_in_real_days():
    from core.choice_dynamics import time_windows
    r = time_windows(5, 0.1, compound=0)            # ไม่ทบต้น: 5 − 0.1k
    assert r["time_to_intervention_days"] == 31      # วันแรกที่เหลือ ≤ 1 ทาง (5 − 3.1 = 1.9)
    assert r["time_to_failure_days"] == 41           # วันแรกที่เหลือ 0 ทาง
    assert r["decision_window_days"] == 31
    c = time_windows(5, 0.1)                        # ทบต้น 0.1%/วัน ต้องพังเร็วกว่า
    assert c["time_to_failure_days"] < 41 and c["time_to_intervention_days"] < 31


def test_time_windows_matches_choice_next_stepping():
    from core.choice_dynamics import time_windows
    c, k = 4.0, 0
    while choice_next(c, 0.3, 0.05, 0.1)["choice_next"] > 0:
        c = choice_next(c, 0.3, 0.05, 0.1)["choice_next_raw"]; k += 1
    assert time_windows(4, 0.3, 0.05, 0.1, compound=0)["time_to_failure_days"] == k + 1


def test_time_windows_edges():
    from core.choice_dynamics import time_windows
    assert time_windows(0, 0)["status"] == "COLLAPSE"
    assert time_windows(1, 0.1)["time_to_intervention_days"] == 0       # เหลือทางเดียวอยู่แล้ว
    s = time_windows(5, 0.1, 0, 0.5, compound=0)                       # intervention > drift
    assert s["time_to_failure_days"] is None and s["status"] == "STABLE"
    assert time_windows("?", 0.1)["status"] == "COLLAPSE"              # อ่านไม่ได้ → ไม่มีทางเลือก
    # intervention ชดเชยได้ตอนนี้ แต่ drift ทบต้นจนแซงในที่สุด — ระบบต้องเห็น
    assert time_windows(5, 0.1, 0, 0.2)["time_to_failure_days"] is not None
