"""เครื่องคิดเลขใน engine_bridge — ลบนำหน้า · หารศูนย์ · เปอร์เซ็นต์ · ค่าเกิน/โดเมนผิด"""
from core.engine_bridge import _calc
from ENGINE.tool_executor import _safe_calc


def _lines(t):
    r = _calc(t)
    return r["lines"] if r else []


def test_leading_minus_is_kept():
    """เดิม "-5 x 3" ตัดเครื่องหมายลบทิ้ง ได้ 15"""
    assert _lines("-5 x 3 เท่าไหร่") == ["คิดเลข: -5 × 3 = -15"]


def test_divide_by_zero_is_said_not_silent():
    assert "หารด้วยศูนย์ไม่ได้" in _lines("100 ÷ 0 เท่าไหร่")[0]


def test_percent_of_amount():
    assert _lines("ดอกเบี้ย 2.5% ของ 100,000 เท่าไหร่") == ["คิดเลข: 2.5% ของ 100,000 = 2,500"]
    assert _lines("ลด 20 เปอร์เซ็นต์ จาก 1,500 เหลือเท่าไหร่") == ["คิดเลข: 20% ของ 1,500 = 300 → เหลือ 1,200"]


def test_ranges_and_slashes_are_not_math():
    assert _calc("1-2 วัน คิดยังไง") is None and _calc("24/7 เท่าไหร่") is None


def test_safe_calc_rejects_inf_and_domain_errors_in_thai():
    assert "ใหญ่เกินไป" in _safe_calc("1e400")["error"]
    assert "คำนวณค่านี้ไม่ได้" in _safe_calc("sqrt(-1)")["error"]
    assert _safe_calc("().__class__")["error"]
