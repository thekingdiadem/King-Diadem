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


# ── ตัวเลขเงินของแต่ละทาง ───────────────────────────────────────────
from core.future_paths import basis, path_money

MONEY_TEXT = "ลังเลว่าจะลาออกไปเปิดร้านกาแฟดีไหม มีเงินเก็บ 300,000 เงินเดือน 25,000 รายจ่าย 18,000"
MONEY_PATHS = ["ลาออกไปเปิดร้านกาแฟ ลงทุน 200,000 คาดว่ากำไรเดือนละ 10,000",
               "ทำงานเดิมแล้วขายกาแฟวันหยุด ลงทุน 20,000 ได้เพิ่มเดือนละ 4,000",
               "ขอลดเวลางาน เงินเดือนลดลง 8,000 แล้วขายออนไลน์ได้เพิ่ม 6,000"]


def test_basis_reads_only_what_user_said():
    assert basis(MONEY_TEXT) == {"savings": 300000, "income": 25000, "expense": 18000}
    assert basis("มีเงินเดือน 25,000") == {"savings": None, "income": 25000, "expense": None}


def test_path_money():
    b = basis(MONEY_TEXT)
    quit_ = path_money(MONEY_PATHS[0], b)
    assert quit_["cost"] == 200000 and quit_["monthly"] == -25000 + 10000          # ลาออก = เงินเดือนหาย
    cut = path_money(MONEY_PATHS[2], b)
    assert cut["cost"] == 0 and cut["monthly"] == 6000 - 8000
    assert path_money("ทำงานเดิม", b) is None


def test_money_separates_the_reversible_paths():
    """เดิม B กับ C ได้เส้นเดียวกันเพราะสมการดูแค่ย้อนกลับได้ไหม"""
    f = project(MONEY_TEXT, MONEY_PATHS)
    assert [p["label"] for p in f["paths"]] == ["B", "C", "A"]                     # รอดที่สุดก่อน
    b, c, a = f["paths"]
    assert b["end"] > c["end"] > a["end"] and a["below_floor_month"] == 1
    assert any("ลาออก" in n for n in a["money"]["notes"])


def test_savings_run_out_month():
    f = project("เงินเก็บ 50,000 รายจ่าย 15,000", ["ลาออกไปเรียนต่อ ค่าเรียน 80,000", "ทำงานต่อ"])
    risky = next(p for p in f["paths"] if p["money"])
    assert risky["money"]["runs_out_month"] == 1                                   # เงินก้อนเกินเงินเก็บ


def test_hint_when_numbers_cannot_be_used():
    f = project("ลังเลเรื่องงาน", ["ลาออก ลงทุน 200,000", "ทำงานเดิม"])
    assert "รายได้หรือรายจ่าย" in f["money_hint"]                                  # มีเงินก้อน แต่ไม่รู้ว่าเยอะแค่ไหนสำหรับเขา
    assert project(TEXT, PATHS)["money_hint"].startswith("ใส่ตัวเลข")
    assert project(MONEY_TEXT, MONEY_PATHS)["money_hint"] is None
