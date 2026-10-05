"""Black swan + Monte Carlo หางซ้าย (ROADMAP Phase 4)"""
import pytest
from SIMULATIONS.black_swan_detector import detect_black_swan
from SIMULATIONS.montecarlo_engine import run_montecarlo
from core.future_paths import project


@pytest.mark.parametrize("text, event", [
    ("น้ำท่วมใหญ่ วิกฤตหนัก ทั้งจังหวัด", "environmental disaster"),
    ("โรคระบาดรอบใหม่ ล็อกดาวน์", "pandemic outbreak"),
    ("สงคราม วิกฤต ล่มสลาย", "political instability"),
    ("หุ้นตก วิกฤต market crash", "financial system shock"),
])
def test_thai_events_are_matched_not_all_supply_chain(text, event):
    """เดิมข้อความไทยทุกแบบได้ supply chain collapse"""
    r = detect_black_swan({}, text)
    assert r["black_swan"] and r["event"] == event


@pytest.mark.parametrize("text", ["น้ำท่วม", "วิกฤตชีวิต วิกฤตวัยกลางคน", "software war", "เศรษฐกิจแย่"])
def test_ordinary_text_is_not_a_black_swan(text):
    assert not detect_black_swan({}, text)["black_swan"]


def test_montecarlo_without_shock_is_unchanged():
    r = run_montecarlo(0.5, runs=200, volatility=0.1)
    assert r["shocked_runs"] == 0 and r["percentiles"]["p10"] == 0.4053


def test_montecarlo_shock_fattens_left_tail_only():
    calm = run_montecarlo(0.5, runs=200, volatility=0.1)
    hit = run_montecarlo(0.5, runs=200, volatility=0.1, shock_prob=0.1, shock_size=0.4)
    assert 15 <= hit["shocked_runs"] <= 25
    assert hit["expected_shortfall_10"] < calm["expected_shortfall_10"] - 0.2
    assert hit["percentiles"]["p90"] == calm["percentiles"]["p90"]
    assert hit == run_montecarlo(0.5, runs=200, volatility=0.1, shock_prob=0.1, shock_size=0.4)   # ทำซ้ำได้


def test_future_paths_show_black_swan_tail():
    paths = ["ลาออกไปเปิดร้าน", "ทำงานเดิมต่อ"]
    calm = project("เศรษฐกิจแย่ ควรทำอะไร", paths)
    swan = project("โรคระบาดรอบใหม่ ล็อกดาวน์ ควรทำอะไร", paths)
    assert calm["black_swan"] is None and swan["black_swan"]["event"] == "pandemic outbreak"
    by = {p["action"]: p for p in swan["paths"]}
    assert by["ลาออกไปเปิดร้าน"]["tail_worst"] < by["ทำงานเดิมต่อ"]["tail_worst"]   # ย้อนกลับไม่ได้โดนหนักกว่า
    assert all(p["tail_worst"] <= p["worst"] for p in swan["paths"])


def test_page_mentions_black_swan():
    import pathlib
    page = pathlib.Path(__file__).resolve().parent.parent.joinpath("static", "index.html").read_text(encoding="utf-8")
    assert "f.black_swan" in page and "tail_worst" in page
