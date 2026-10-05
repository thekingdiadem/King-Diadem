"""ภาพจำลองอนาคต 12 เดือน (core/future_paths + SIMULATIONS/montecarlo_engine)"""
import pathlib

from core.future_paths import project

TEXT = "ลังเลว่าจะลาออกไปเปิดร้านกาแฟดีไหม"
PATHS = ["ลาออกไปเปิดร้านกาแฟ", "ทำงานเดิมแล้วขายกาแฟวันหยุด", "ขอลดเวลางานแล้วลองขายออนไลน์"]


def test_shapes_and_bounds():
    f = project(TEXT, PATHS)
    assert f["months"] == 12 and f["floor"] == 30
    for p in f["paths"]:
        assert len(p["mid"]) == len(p["lo"]) == len(p["hi"]) == 13
        assert p["lo"][0] == p["mid"][0] == p["hi"][0] == f["w0"]          # วันนี้รู้ค่าแน่นอน
        assert all(0 <= lo <= m <= hi <= 100 for lo, m, hi in zip(p["lo"], p["mid"], p["hi"]))


def test_irreversible_path_dips_deeper_and_spreads_wider():
    f = project(TEXT, PATHS)
    quit_ = next(p for p in f["paths"] if not p["reversible"])
    safe = next(p for p in f["paths"] if p["reversible"])
    assert min(quit_["mid"]) < min(safe["mid"])
    assert quit_["hi"][12] - quit_["lo"][12] > safe["hi"][12] - safe["lo"][12]
    assert quit_["below_floor_month"] is not None and safe["below_floor_month"] is None


def test_identical_paths_are_drawn_once():
    """B กับ C ได้ผลเท่ากันตามสมการ — เดิมวาดทับกันจนดูเหมือนเส้นหาย"""
    f = project(TEXT, PATHS)
    assert [p["label"] for p in f["paths"]] == ["B · C", "A"] and f["paths"][0]["same"]


def test_same_input_same_picture():
    assert project(TEXT, PATHS) == project(TEXT, PATHS)


def test_no_paths_no_picture():
    assert project(TEXT, []) is None and project(TEXT, ["  "]) is None


def test_simulate_returns_future(client):
    d = client.post("/simulate", json={"input": TEXT, "paths": PATHS}).json()
    assert d["future"]["paths"] and d["simulation"]


def test_page_draws_future_chart():
    page = pathlib.Path(__file__).resolve().parent.parent.joinpath("static", "index.html").read_text(encoding="utf-8")
    assert 'id="sim-future"' in page and "drawFuture(d.future)" in page and "ไม่ใช่คำทำนาย" in page
