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
GLJS = (ROOT / "static" / "big_bang_gl.js").read_text(encoding="utf-8")


def test_page_has_overlay_skip_and_replay():
    # ตัววาดการ์ดจอต้องโหลดก่อนตัวควบคุม — canvas ใบเดียวขอบริบทได้แบบเดียว
    assert '<script src="/static/big_bang_gl.js"></script>\n<script src="/static/big_bang.js"></script>' in PAGE
    assert 'id="big-bang" role="dialog" aria-modal="true"' in PAGE and "hidden>" in PAGE
    assert 'id="bb-skip">ข้าม ›</button>' in PAGE
    assert 'id="ec-bang" onclick="window.KD_bigBang&&KD_bigBang()">บิ๊กแบง</button>' in PAGE
    assert 'id="bb-cap" aria-live="polite"' in PAGE


def test_cosmic_timeline_is_in_order():
    """ยุคของจักรวาลเรียงตามเวลาจริง: ระเบิด → ขยายตัว → นิวเคลียส → แสงแรก → ดาวดวงแรก → กาแล็กซี → วันนี้"""
    block = JS[JS.index("var PHASES = ["):JS.index("];", JS.index("var PHASES = ["))]
    times = [float(x) for x in re.findall(r"\{ t: ([\d.]+),", block)]
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
    for src in (JS, GLJS):
        assert not re.search(r"https?://", src)                     # ไม่โหลดอะไรจากเว็บอื่น (CSP)
        assert "innerHTML" not in src


def test_gpu_renderer_with_canvas_fallback():
    """รุ่นที่ 2: อนุภาคหลักแสนบนการ์ดจอ · ไม่มี WebGL ใช้ Canvas 2D เดิม · บริบทหลุดก็ปิดฉากให้"""
    assert "try { GL = window.KD_BigBangGL ? window.KD_BigBangGL(cv) : null; } catch (e) { GL = null; }" in JS
    assert "var ctx = GL ? null : (cv.getContext && cv.getContext('2d'));" in JS
    assert "if (GL.lost()) { close(); return; }" in JS
    assert "Math.min(260000, Math.max(70000, w * h * .3))" in GLJS
    assert "webglcontextlost" in GLJS
    assert "Math.min(1.25, window.devicePixelRatio || 1)" in JS


def test_sound_is_off_until_the_viewer_turns_it_on():
    assert 'id="bb-snd" aria-pressed="false">เสียง: ปิด</button>' in PAGE
    assert "on = localStorage.getItem('kd-bang-sound') === '1';" in JS
    assert "snd.stop();" in JS                                       # ปิดฉากแล้วเสียงหยุด


@pytest.mark.skipif(not shutil.which("node"), reason="ต้องมี node")
def test_script_parses():
    for f in ("big_bang.js", "big_bang_gl.js"):
        subprocess.run(["node", "--check", str(ROOT / "static" / f)], check=True)
