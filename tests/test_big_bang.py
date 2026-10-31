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
    assert 'id="ec-bang" data-act="bang">บิ๊กแบง</button>' in PAGE
    assert "bang: function(){ if(window.KD_bigBang) KD_bigBang(); }" in PAGE
    assert 'id="bb-cap" aria-live="polite"' in PAGE


def test_cosmic_timeline_is_in_order():
    """ยุคของจักรวาลเรียงตามเวลาจริง: ระเบิด → ขยายตัว → นิวเคลียส → แสงแรก → ดาวดวงแรก → กาแล็กซี → วันนี้"""
    block = JS[JS.index("var PHASES = ["):JS.index("];", JS.index("var PHASES = ["))]
    times = [float(x) for x in re.findall(r"\{ t: ([\d.]+),", block)]
    assert times == sorted(times) and len(times) == 28
    for need in ("10⁻⁴³ วินาที", "10⁻³⁶ วินาที", "10⁻¹² วินาที", "1 ในพันล้าน", "380,000 ปี", "9,200 ล้านปี",
                 "100 ล้านปีก่อน", "66 ล้านปีก่อน", "13,800 ล้านปี", "2.7 K"):
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


def test_scene_is_slow_enough_to_read():
    """เจ้าของโปรเจกต์บอกว่าฉากเลื่อนไวไป แล้วอยากได้ละเอียดราว 60 วินาที
    นาฬิกาของฉาก (เวลาจริง → เวลาในฉาก) ต้องเดินไปข้างหน้าเสมอ และยาวราว 60 วินาที"""
    knots = [tuple(map(float, k)) for k in re.findall(r"\[([\d.]+), ([\d.]+)\]", JS[JS.index("var CLOCK"):JS.index("function sceneTime")])]
    assert all(b[0] > a[0] and b[1] > a[1] for a, b in zip(knots, knots[1:]))
    end = float(re.search(r"END = ([\d.]+)", JS).group(1))
    assert knots[-1][1] == end and 80 <= knots[-1][0] <= 100          # รุ่นเล่าเรื่องยาวราว 90 วินาที
    assert JS.count("sceneTime((") == 2 and "(now - t0) / 1000;" not in JS


def test_asteroid_impact_chapter():
    """เจ้าของโปรเจกต์อยากได้ฉากอุกกาบาตตกเมื่อ 66 ล้านปีก่อน — ชนยูคาทาน คลื่นกระแทก ฝุ่น แล้วชีวิตเริ่มใหม่
    มีทั้งในตัววาดการ์ดจอและตัววาดสำรอง และจังหวะชนตรงกัน (เวลาในฉาก 15.0)"""
    assert "IMPACT = 15.0 + EARTH_SHIFT" in JS and "{ t: 21.6, time: '66 ล้านปีก่อน'" in JS
    assert "ยูคาทาน" in JS and "10 กิโลเมตร" in JS
    assert "vec3 earth(vec2 uv,float t){" in GLJS and "ti=15.;" in GLJS
    assert "function earth2D(t, cx, cy)" in JS and "earth2D(t - EARTH_SHIFT, cx, cy);" in JS
    assert "c=mix(c,earth(uv,t-6.6),eb);" in GLJS and "EARTH_SHIFT = 6.6" in JS             # ภาพกับเสียงเลื่อนเท่ากัน
    assert "if (t > IMPACT && !done.imp) { done.imp = 1; boom(); }" in JS


def test_pleiades_and_particle_pairs():
    """ดาวลูกไก่ 7 ดวงเกิดจากเมฆก๊าซ (และยังอยู่บนฟ้าตอนจบ) · ยุคแรกมีอนุภาคกับปฏิยานุภาคเกิดดับเป็นคู่"""
    assert "ดาวลูกไก่" in JS and "440 ปีแสง" in JS
    assert "vec3 pleiades(vec2 uv,float t){" in GLJS and "for(int i=0;i<7;i++)" in GLJS
    assert "c+=stars7(uv,vec2(-.62,.32),.05,.8,14.);" in GLJS
    assert len(re.findall(r"\[-?[\d.]+, -?[\d.]+\]", JS[JS.index("var M45"):JS.index("function pleiades2D")])) == 7
    assert "float pe=smoothstep(1.6,1.9,t)" in GLJS and "pf=exp(" in GLJS


def test_cretaceous_story_and_rise_of_mammals():
    """เล่าเป็นเรื่อง: ยุคครีเทเชียส (ลมร้อน ไดโนเสาร์ นกยุคแรก) → ชน → สัตว์เลี้ยงลูกด้วยนมแพร่พันธุ์
    คำบรรยายต้องถูกข้อเท็จจริง: สัตว์เลี้ยงลูกด้วยนมและนกมีมาก่อนการชน ไม่ได้เกิดเพราะการชน"""
    for need in ("ยุคครีเทเชียส", "ลมร้อน", "นกยุคแรก", "มีมาแล้วกว่าร้อยล้านปี", "3 ใน 4", "แตกแขนง", "ลูกหลานไดโนเสาร์"):
        assert need in JS, need
    for fn in ("float sauro(vec2 p,float w)", "float mammal(vec2 p,float w,float k)", "float flyer(vec2 p,float w,float s)",
               "vec3 land(vec2 uv,float lc,float af,float gr)", "vec3 actors(vec2 uv,vec3 c,float lc,float af,float gr)"):
        assert fn in GLJS, fn
    blk = GLJS[GLJS.index("บทพื้นโลก"):GLJS.index("'vec3 earth(vec2 uv,float t){'")]
    assert "smoothstep(" not in blk                     # ขอบกลับด้านต้องใช้ rs() — smoothstep ของ GLSL ไม่รองรับ
    assert "function land2D(lc, af, cx, cy)" in JS and "function wind()" in JS and "function birds()" in JS


def test_text_can_be_hidden_for_pure_visuals():
    """ปุ่ม "ข้อความ" ซ่อนคำบรรยายให้ดูภาพล้วนๆ และจำค่าไว้"""
    assert 'id="bb-txt" aria-pressed="true">ข้อความ: เปิด</button>' in PAGE
    assert "#big-bang.notext .bb-cap" in PAGE
    assert "localStorage.getItem('kd-bang-text') !== '0'" in JS


def test_phone_buzzes_at_the_big_moments_only_when_motion_is_allowed():
    assert "function buzz(pat) { if (CALM()) return; try { if (navigator.vibrate) navigator.vibrate(pat); } catch (e) {} }" in JS
    assert JS.count("buzz([220, 60, 120, 60, 400])") == 2 and "buzz([60, 40, 160])" in JS


def test_background_shader_uses_high_precision_and_real_earth():
    """หน้าจอจริงบน iPhone: โลกเป็นลูกบอลสีฟ้าเปล่า ไม่มีทวีป ไม่มีดาว ไม่มีตอไม้ — mediump ทำให้ลายสุ่มหาย
    และเจ้าของโปรเจกต์บอกว่าโลกไม่สมจริง → ใช้ภาพโลกของ NASA (สาธารณสมบัติ) ไฟล์เดียวกับหน้า Universe"""
    bg = GLJS[GLJS.index("var FS_BG"):]
    assert "#ifdef GL_FRAGMENT_PRECISION_HIGH" in bg and "precision highp float;" in bg
    for f in ("day.jpg", "clouds.jpg", "lights.jpg"):
        assert "'" + f + "'" in GLJS and (ROOT / "static" / "earth" / f).exists()
    assert "img.src = '/static/earth/' + f;" in GLJS                 # ไฟล์ในเว็บเราเอง (CSP)
    assert "if(uTex>.5){" in GLJS and "}else{" in GLJS               # โหลดภาพไม่ได้ก็ยังมีโลกจากโค้ด
    assert "smoothstep(19.6,20.4,t)" in GLJS                         # แสงเมืองมีแค่ตอน "วันนี้" ไม่ใช่ 66 ล้านปีก่อน
