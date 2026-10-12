"""เลขธุรกิจ: DOMAINS/business_engine ย้ายกลับจาก legacy/ แล้วต่อผ่าน core/engine_bridge
คนพิมพ์ยอดขายกับต้นทุนมา — เดิมระบบอธิบายสูตรอย่างเดียว ไม่ได้คิดตัวเลขให้ ตอนนี้คิดกำไร · margin · สัดส่วนต้นทุน"""
import math

import pytest

from DOMAINS.business_engine import analyze_business
from core.engine_bridge import analyze
from core.kernel_voice import compose


def test_arithmetic_only_from_what_the_user_said():
    b = analyze_business(80000, 65000)
    assert b == {"revenue": 80000.0, "cost": 65000.0, "profit": 15000.0, "margin": 0.1875,
                 "cost_share": 0.8125, "breakeven_gap": 0.0}
    # ไม่มีคะแนนที่แต่งจากค่าเริ่มต้น ไม่มี "กลยุทธ์" ทางเดียว ไม่ส่ง input กลับ
    for k in ("opportunity_score", "waterline", "risk_level", "recommended_strategy", "input"):
        assert k not in b


@pytest.mark.parametrize("rev,cost", [(0, 100), (-5, 10), (None, 10), ("abc", 10), (math.inf, 1), (math.nan, 1), (100, -1)])
def test_bad_or_missing_numbers_are_skipped(rev, cost):
    """เดิมรายรับ 0 → margin −100% แล้วสั่ง pivot · ตอนนี้ไม่คิดเลยถ้าตัวเลขไม่ครบหรือผิด"""
    assert analyze_business(rev, cost) is None


def test_no_hidden_database_write(monkeypatch):
    """เดิมเรียก log_decision ทุกครั้ง (เขียนฐานข้อมูลซ่อนอยู่ + เก็บ input)"""
    import DATABASE.db as db
    monkeypatch.setattr(db, "log_decision", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no db write")))
    analyze_business(100, 50)


@pytest.mark.parametrize("text,line", [
    ("ร้านกาแฟขายได้เดือนละ 80,000 ต้นทุน 65,000 ไปต่อดีไหม", "กำไร 15,000 บาทต่อเดือน · margin 19% · ต้นทุนกิน 81% ของรายรับ"),
    ("เปิดร้านมา 6 เดือน ยอดขายเดือนละ 50,000 ค่าใช้จ่าย 62,000 ทำไงดี", "ขาดทุน 12,000 บาทต่อเดือน — ต้นทุนเป็น 124% ของรายรับ"),
    ("ขายชิ้นละ 120 ต้นทุนชิ้นละ 70 คุ้มไหม", "กำไร 50 บาทต่อชิ้น · margin 42% · ต้นทุนกิน 58% ของรายรับ"),
    ("ร้านขายได้ 1.2 แสน ต้นทุน 9 หมื่น", "กำไร 30,000 บาท · margin 25% · ต้นทุนกิน 75% ของรายรับ"),
])
def test_bridge_computes_business_numbers(text, line):
    r = analyze(text)
    assert line in r["lines"] and "business" in r["data"]
    assert "ห้ามแต่งตัวเลขเพิ่ม" in r["llm_ctx"]               # LLM ได้ตัวเลขจริงไปใช้


def test_loss_shows_the_gap_without_choosing_for_the_user():
    lines = analyze("ยอดขายเดือนละ 50,000 ค่าใช้จ่าย 62,000")["lines"]
    assert any("เพิ่มรายรับอีก 12,000 บาทต่อเดือน หรือลดต้นทุนลงเท่ากัน" in l for l in lines)
    assert not any("pivot" in l or "ต้องเลิก" in l for l in lines)


@pytest.mark.parametrize("text", [
    "เงินเดือน 18,000 รายจ่าย 15,000",            # งบส่วนตัว ไม่ใช่กิจการ
    "ทำงานร้านกาแฟ เงินเดือน 15,000 รายจ่าย 12,000",  # มีคำว่าร้าน แต่ไม่มีรายรับของกิจการ
    "ต้นทุนสูงมาก ลูกค้าน้อย",                     # ไม่มีตัวเลข
    "ร้านขายได้เดือนละ 80,000",                    # ไม่มีต้นทุน — ไม่เดา
])
def test_does_not_guess(text):
    assert "business" not in analyze(text)["data"]


def test_kernel_voice_uses_the_numbers_and_skips_the_runway_line():
    """คำตอบจากสมการแสดงเลขธุรกิจ และไม่เอายอดเงินไปคิดเป็น "เวลาที่มีจริง = เงิน ÷ 150" (กันไว้แบบเดียวกับหนี้/runway)"""
    out = compose("ร้านกาแฟขายได้เดือนละ 80,000 ต้นทุน 65,000 ไปต่อดีไหม")
    text = out if isinstance(out, str) else str(out)
    assert "กำไร 15,000 บาทต่อเดือน" in text
    assert "เวลาที่มีจริง" not in text


def test_runway_line_stays_out_even_when_cash_is_mentioned():
    out = str(compose("มีเงิน 50,000 ร้านขายได้เดือนละ 80,000 ต้นทุน 65,000"))
    assert "กำไร 15,000 บาทต่อเดือน" in out and "เวลาที่มีจริง" not in out
