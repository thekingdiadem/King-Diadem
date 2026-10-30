"""ฉากกำเนิดจักรวาลก่อนเข้าหน้า The Universe (static/big_bang.js)

เจ้าของโปรเจกต์อยากได้หน้าจักรวาลแบบอลังการ "เหมือนตอนบิ๊กแบง" และมีลูกเล่น
ฉากนี้ต้องข้ามได้เสมอ ไม่เล่นเองกับคนที่ตั้งลดการเคลื่อนไหว และไม่โหลดอะไรจากเว็บอื่น"""
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PAGE = (ROOT / "static" / "king_diadem_universe.html").read_text(encoding="utf-8")
JS = (ROOT / "static" / "big_bang.js").read_text(encoding="utf-8")


def test_page_has_overlay_skip_and_replay():
    assert '<script src="/static/big_bang.js"></script>' in PAGE
    assert 'id="big-bang" role="dialog" aria-modal="true"' in PAGE and "hidden>" in PAGE
    assert 'id="bb-skip">ข้าม ›</button>' in PAGE
    assert 'id="ec-bang" onclick="window.KD_bigBang&&KD_bigBang()">บิ๊กแบง</button>' in PAGE
    assert 'id="bb-cap" aria-live="polite"' in PAGE


def test_cosmic_timeline_is_in_order():
    """ยุคของจักรวาลเรียงตามเวลาจริง: ระเบิด → ขยายตัว → นิวเคลียส → แสงแรก → ดาวดวงแรก → กาแล็กซี → วันนี้"""
    times = [float(x) for x in re.findall(r"\{ t: ([\d.]+),", JS)]
    assert times == sorted(times) and len(times) == 7
    for need in ("10⁻³⁶ วินาที", "380,000 ปี", "13,800 ล้านปี", "2.7 K"):
        assert need in JS


def test_respects_calm_and_plays_once_per_visit():
    assert "function CALM() { return MQ.matches || document.documentElement.classList.contains('kd-calm'); }" in JS
    assert "if (!seen && !CALM()) open(true);" in JS
    assert "if (CALM()) { stillShow(); return; }" in JS            # กดเล่นตอนลดการเคลื่อนไหว = ภาพนิ่งทีละช่วง
    assert "sessionStorage" in JS and "try {" in JS


def test_can_always_escape_and_is_light():
    assert "e.key === 'Escape'" in JS and "skipEl.addEventListener('click', skip);" in JS
    assert "Math.min(1.5, window.devicePixelRatio || 1)" in JS     # จำกัดความละเอียด ประหยัดแบต
    assert "document.hidden" in JS
    assert not re.search(r"https?://", JS)                          # ไม่โหลดอะไรจากเว็บอื่น (CSP)
    assert "innerHTML" not in JS


@pytest.mark.skipif(not shutil.which("node"), reason="ต้องมี node")
def test_script_parses():
    subprocess.run(["node", "--check", str(ROOT / "static" / "big_bang.js")], check=True)
