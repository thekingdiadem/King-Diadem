"""ค่าตัวเลขแปลกๆ (nan/inf/1e9/None) และ input ผิดชนิดที่เคยให้ผลผิดเงียบๆ (ตรวจ ENGINE/ และ app.py รอบ 397 ไฟล์)"""
import math

import pytest

from ENGINE.decision_engine import run_decision
from ENGINE.risk_engine import assess
from ENGINE.survival_advisor import survival_advisor
from ENGINE.world_intel import analyze_location

NAN = float("nan")


def test_nan_entropy_does_not_route_harmless_text_to_survival():
    assert run_decision({"input": "x", "entropy": "nan"}).get("route") != "survival"


@pytest.mark.parametrize("args", [(NAN, NAN, NAN), (None, None, None), ("x", 1, 1)])
def test_unknown_survival_inputs_never_claim_stable(args):
    assert survival_advisor(*args)["tier"] != "STABLE"


def test_risk_score_stays_in_range():
    for p in ({"entropy": "nan"}, {"entropy": 1e9}, {"resource": -1e9}, {"entropy": float("inf")}):
        r = assess(p)["risk_score"]
        assert 0 <= r <= 100 and not math.isnan(r)


@pytest.mark.parametrize("lat,lng", [(None, None), (NAN, NAN), (1e9, -1e9)])
def test_location_rejects_impossible_coordinates(lat, lng):
    r = analyze_location(lat, lng)
    assert -90 <= r.get("lat", 0) <= 90


def test_empty_and_wrong_type_inputs_return_400(client):
    assert client.post("/run", json={"input": ""}).status_code == 400
    assert client.post("/simulate", json={"input": ""}).status_code == 400
    assert client.post("/simulate", json={"input": 123}).status_code == 400


def test_simulate_ignores_non_text_paths(client):
    d = client.post("/simulate", json={"input": "ย้ายงานดีไหม", "paths": [{"a": 1}, "อยู่ที่เดิม"]}).json()
    assert "{'a': 1}" not in str(d)


def test_display_name_is_plain_text(client):
    client.cookies.set("kd_name", "%ZZ%3Cscript%3E")
    from app import _safe_name
    assert _safe_name("<script>alert(1)</script>") == "scriptalert(1)/script"
    assert "<" not in _safe_name("a<b>" * 50) and len(_safe_name("x" * 500)) == 80
