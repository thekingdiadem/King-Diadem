"""Choice ที่วัดได้จริง: เป็น 0 ได้เมื่อคนนั้นไม่เหลือทาง แต่ remaining_choices (สิ่งที่ระบบเปิดให้) ยัง ≥ 1"""
from ENGINE.risk_engine import assess


def test_dead_end_when_self_harm():
    r = assess({"raw_input": "ฉันจะฆ่าตัวตายคืนนี้"})
    assert r["dead_end"] is True and r["choice_measured"] == 0
    assert r["remaining_choices"] >= 1          # ระบบยังต้องเปิดทางให้เสมอ


def test_dead_end_when_overdose():
    r = assess({"raw_input": "กินยานอนหลับไปทั้งแผงแล้ว"})
    assert r["dead_end"] is True and r["choice_measured"] == 0


def test_ordinary_hard_day_is_not_dead_end():
    for t in ("วันนี้เหนื่อยมาก งานเยอะ", "หนี้บัตรเครดิต 50,000 ผ่อนไม่ไหว", "สอบตก เสียใจ"):
        r = assess({"raw_input": t})
        assert r["dead_end"] is False and r["choice_measured"] >= 1, t


def test_measured_never_exceeds_promised_plus_rounding():
    r = assess({"raw_input": "สบายดี", "entropy": 10, "resource": 90})
    assert r["choice_measured"] == r["remaining_choices"]
