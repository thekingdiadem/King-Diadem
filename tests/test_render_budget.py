"""หน้าแรกบนมือถือ: เครื่องร้อนและภาพแตก เพราะฉากจักรวาลวาดเต็มจอที่ 2 เท่าของจอ 90 ภาพ/วินาทีตลอดเวลา แม้ไม่มีใครแตะ
(หน้า Universe พักเฟรมตอนไม่มีใครแตะอยู่แล้ว — หน้าแรกยังไม่มี)"""
import re
from pathlib import Path

APP = (Path(__file__).resolve().parent.parent / "static/app.js").read_text(encoding="utf-8")


def test_idle_phone_draws_30_but_user_choice_always_wins():
    m = re.search(r"function perfCap\(now, idleOk\)\{ return (.+?) \? Math\.min\(FPS_CAP, 30\) : FPS_CAP; \}", APP)
    assert m, "perfCap หาย"
    cond = m.group(1)
    assert "!PERF.user" in cond and "PERF.low" in cond and "PERF.light && now - PERF.input > 1500" in cond
    # กดเลือกเฟรมเรตในเมนู = ใช้ค่านั้นเสมอ (ทั้งที่เลือกไว้ก่อน และที่เพิ่งกด)
    assert "FPS_CAP = _fps; PERF.user = true;" in APP
    assert "FPS_CAP = +b.getAttribute('data-fps'); PERF.user = true;" in APP


def test_cinema_and_universe_view_keep_the_full_rate():
    assert "cap = perfCap(now, view !== 'universe' && !CINEMA.on)" in APP


def test_phone_renders_earth_at_one_and_a_half_not_two():
    assert "Math.min(PERF.light ? 1.5 : 2, dp)" in APP


def test_resting_at_30_is_not_mistaken_for_a_slow_device():
    """เดิมนับว่าช้าเมื่อภาพห่างเกิน 1/45 วินาที — ถ้าพักที่ 30 ภาพ/วินาทีจะโดนลดความละเอียดทั้งที่เครื่องไม่ได้ช้า"""
    assert "var late = raw > Math.max(1 / 45, PERF.gap * 1.5);" in APP
    assert "PERF.gap = 1 / cap;" in APP
    assert "PERF.ups < 2" in APP                     # คืนความละเอียดได้ แต่ไม่สลับไปมา


def test_input_listeners_are_passive():
    assert "PERF.input = performance.now(); }, { passive: true, capture: true }" in APP
