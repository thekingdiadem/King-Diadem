"""ฉากกระโดดหน้าผา: กล้องพุ่งจากอวกาศลงหาโลก เร็วแล้วช้า หัวเรื่องปรากฏตอนช้า · ข้ามได้ · ลดการเคลื่อนไหว = ไม่เล่น"""
from pathlib import Path

JS = Path("static/cockpit_earth.js").read_text(encoding="utf-8")
UNI = Path("static/king_diadem_universe.html").read_text(encoding="utf-8")


def test_dive_fast_then_slow_and_skippable():
    assert "function diveEase(p) { return 1 - Math.pow(1 - p, 2.3); }" in JS
    assert "if (calm() || DIVE.on) return;" in JS                      # ลดการเคลื่อนไหว ไม่เล่น
    assert "['pointerdown', 'wheel', 'keydown'].forEach(function (ev) { window.addEventListener(ev, stopDive" in JS
    assert "if (DIVE.on) diveStep(now);" in JS


def test_waits_for_big_bang_and_hides_title_while_falling():
    assert "classList.contains('bb-on')) window.addEventListener('kd-bang-done', startDive, { once: true })" in JS
    assert "html.kd-dive #hero>div:not(.earth-ctl){opacity:0" in UNI
