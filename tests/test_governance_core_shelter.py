"""KERNEL/governance-core.md — ZERO_CHOICE ต้องนับการไม่มีที่พักด้วย (MIN_SHELTER)"""
from core.emptiness_guard import titan_zero_choice_condition, titan_minimal_intervention


def test_missing_shelter_is_zero_choice():
    r = titan_zero_choice_condition(2, True, True, False, shelter_ok=False)
    assert r["zero_choice"] is True
    assert r["shelter_ok"] is False
    assert r["required_action"] == "MINIMAL_INTERVENTION_RESTORE_O"
    assert titan_minimal_intervention(r["zero_choice"])["action"] == "MINIMUM_FORCE_TO_RESTORE"


def test_all_floors_met_stays_silent():
    r = titan_zero_choice_condition(1, True, True, False, shelter_ok=True)
    assert r["zero_choice"] is False
    assert r["required_action"] == "SILENCE"


def test_old_four_arg_call_still_works():
    r = titan_zero_choice_condition(1, True, True, False)
    assert r["zero_choice"] is False
    assert r["shelter_ok"] is True


def test_negative_choice_count_is_still_zero_choice():
    assert titan_zero_choice_condition(-1, True, True, False)["zero_choice"] is True
