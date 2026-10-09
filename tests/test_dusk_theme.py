"""หน้าเว็บ: ป้ายตอนสภากำลังคิดต้องตรงกับสภาจริง และปุ่มธีมฟ้ายามเย็นยังกดง่ายบนมือถือ"""
import re
from pathlib import Path

from AI.council_engine import COUNCIL_SIZE

HTML = (Path(__file__).resolve().parent.parent / "static" / "index.html").read_text(encoding="utf-8")


def test_thinking_label_matches_council_size():
    # เดิมขึ้น "สภา 5 เสียง" ระหว่างรอ ทั้งที่สภามี 6 เสียงแล้ว
    live = re.sub(r'<script type="application/json" id="system-map">.*?</script>', "", HTML, flags=re.S)  # ประวัติการแก้
    labels = set(re.findall(r"สภา (\d) เสียง", live))
    assert labels == {str(COUNCIL_SIZE)}


def test_tab_icons_alternate_cool_and_warm():
    tabbar = re.search(r'<nav id="tabbar".*?</nav>', HTML, re.S).group(0)
    icons = re.findall(r'<span class="i">(.*?)</span>', tabbar)
    assert '<use href="#moon-enso"/>' in icons[0] and icons[1:] == ["✦", "☁", "☼"]   # ☾ = พระจันทร์หมึก (SVG)
    assert '<symbol id="moon-enso"' in HTML
    assert "#tabbar button:nth-child(odd) .i" in HTML and "#tabbar button:nth-child(even) .i" in HTML


def test_dusk_theme_respects_reduced_motion():
    assert "@keyframes twinkle" in HTML
    assert re.search(r"prefers-reduced-motion:reduce\)\{\*\{animation:none!important", HTML)


def test_universe_mode_toggle_stays_readable():
    # สีตัวอักษรเข้มของปุ่มผู้ตอบเคยไปโดนปุ่มโหมดจักรวาลด้วย → ตัวเข้มบนพื้นทองหม่นอ่านไม่ออก
    assert ".seg button.on{color:#1a1630}" not in HTML
    assert re.search(r'#u-mode button\[data-m="decisions"\]\.on\{background:var\(--warm\)\}', HTML)
    assert re.search(r'#u-mode button:not\(\[data-m="decisions"\]\)\.on\{background:var\(--cool\)\}', HTML)


def test_decisions_universe_is_a_solar_system():
    """โหมดการตัดสินใจวาดเป็นระบบสุริยะ — ใจกลางแสง (แทนดวงอาทิตย์) ดาวเคราะห์ = เส้นทาง
    วาดครึ่งหลังของจาน/ดาวก่อนใจกลาง แล้วครึ่งหน้าทับ (ลำดับความลึก)"""
    assert "function drawCore(" in HTML and "function drawDisk(" in HTML and "function drawPlanets(" in HTML
    assert "drawPlanets(g, now, true); drawStars(g, now, true); drawCore(g, now);" in HTML
    assert "function drawSun(" not in HTML


def test_universe_galaxy_layer_has_a_fallback():
    """กาแล็กซี/เนบิวลาวาดด้วย WebGL — เครื่องที่ไม่มี WebGL ต้องยังเห็นจานสสารแบบ 2D และพื้นหลังเดิม"""
    assert "var GLX = (function(){" in HTML and "c.id = 'cosmos-gl'" in HTML
    assert "if(!useGL) drawDisk(g, now, true)" in HTML and "else ctx.drawImage(bgCv, 0, 0, W, H);" in HTML
    # เครื่องที่วาดไม่ทันลดความละเอียดชั้นภาพนุ่มเอง
    assert "GLX.pace(dt)" in HTML


def test_energy_flows_have_intention():
    """กระแสพลังงานไหลตามแขนเกลียวเข้าหาแก่น (มีปลายทาง) ไม่ใช่ลอยสุ่ม และปิดเมื่อผู้ใช้ลดการเคลื่อนไหว"""
    assert "function drawFlows(" in HTML
    body = HTML[HTML.index("function drawFlows("):HTML.index("function drawFlows(") + 1600]
    assert "if(REDUCED) return;" in body and "f.r -= dt" in body and "Math.log(f.r" in body


def test_universe_links_to_the_universe_page():
    assert 'class="u-link glass" href="/static/king_diadem_universe.html"' in HTML


def _static(name):
    import os
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", name), encoding="utf-8") as f:
        return f.read()


def test_universe_files_share_one_visual_language():
    """ไฟล์จักรวาลทุกไฟล์ใช้ภาษาภาพเดียวกับแท็บจักรวาล: แก่นแสงแทนลูกบอลส้ม · ร้อนสลับเย็น · สีเสียงตรงกับแอป"""
    galaxy = _static("galaxy.js")
    assert '"#ff8800"' not in galaxy and "Sun rays (16 rays)" not in galaxy     # ดวงอาทิตย์ลูกส้มเดิม
    assert "ทรงกลมรับแสงจากแก่น" in galaxy
    scene = _static("galaxy_scene.js")
    assert "เนบิวลาร้อนสลับเย็น" in scene and "rimSide" in scene
    thinking = _static("ai_thinking_orbit.js")
    assert 'LYLA:    { color: "#ffcf7a"' in thinking and 'VEGA:    { color: "#8cc2ff"' in thinking   # ตรงกับ --lyla / --vega
    assert "rose" in _static("warp_intro.js")


def test_front_page_earth_uses_real_satellite_imagery():
    """โลกหน้าแรกใช้ภาพจริงของ NASA: ประเทศตรงตำแหน่ง ไฟเมืองตามเมืองใหญ่จริง เมฆ
    ระหว่างโหลดหรือโหลดไม่ได้ ใช้โลกที่สร้างจาก noise · เครื่องที่ไม่มี WebGL ใช้พื้นหลัง 2D เดิม"""
    import os
    root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "earth")
    for name in ("day.jpg", "lights.jpg", "clouds.jpg"):
        path = os.path.join(root, name)
        assert os.path.getsize(path) < 450 * 1024, name                 # มือถือโหลดไหว
        assert "'/static/earth/" + name + "'" in HTML
    credits = open(os.path.join(root, "README.md"), encoding="utf-8").read()
    assert "NASA" in credits and "MIT" in credits
    assert "uniform sampler2D uDay,uLights,uClouds;" in HTML
    assert "if(uTex>.5){" in HTML and "} else {" in HTML                  # มีโลก noise สำรอง
    assert "im.onerror = function(){ EARTH_TEX = 'failed'; };" in HTML
    assert "if(!drew) ctx.drawImage(bgCv, 0, 0, W, H);" in HTML


def test_front_page_routes_orbit_the_earth():
    """วงโคจร 6 เส้นทางรอบโลก (แบบภาพอ้างอิง) · เส้นทางที่เลือกเรือง · มีสถานีอวกาศวิ่ง · ครึ่งหลังถูกโลกบัง
    ชื่อเส้นทางไม่ทับกัน (เดิมบนมือถือ RISK ทับ GENERAL)"""
    assert "var ROUTE_EN = ['GENERAL', 'RISK', 'CIVIL', 'SURVIVAL', 'COLLAPSE', 'VEGA'];" in HTML
    body = HTML[HTML.index("function drawRoutes("):HTML.index("function drawBodyLabels(")]
    assert "function hidden(q)" in body and "ORB[i] === cur" in body and "สถานีอวกาศ" in body
    assert "var clash = boxes.some(" in body
    assert "drawRoutes(cx, cy, r, tsec, DAWN.show, top, bottom);" in HTML


def test_front_page_matches_founders_reference():
    """ฉากหน้าแรกตามภาพอ้างอิงของผู้ก่อตั้ง: ดวงอาทิตย์ซ้ายบน · ดาวเสาร์ (วงแหวนหน้า-หลัง) ดาวพฤหัส ดาวยูเรนัสทางขวา
    · เนบิวลาซ้ายล่าง · ทุกดวงรับแสงจากดวงอาทิตย์บนจอ · มีป้ายชื่อ · บนมือถือโลกเล็กลงให้พอดีจอ"""
    assert "uniform vec3 uSun,uSat,uJup,uUra;" in HTML
    assert "vec3 sunDir(vec2 c)" in HTML and "vec4 planet(vec2 p,vec3 P,float k,float t)" in HTML
    assert "if(q.y<0.) col=mix(col,ringC,ring*.9);" in HTML and "if(q.y>=0.)" in HTML      # วงแหวนหลัง/หน้าดาวเสาร์
    assert "float nm=smoothstep(1.,0.," in HTML                                             # เนบิวลา
    assert "[['Sun', B.sun, 1.25], ['Saturn', B.sat, 1.25], ['Jupiter', B.jup, 1.35], ['Uranus', B.ura, 1.6]]" in HTML
    assert "portrait ? Math.min(avW * .3, avH * .22)" in HTML        # มือถือ: โลกราว 60% ของความกว้างจอ (เดิม 86% ใหญ่เกิน)
    # โคโรนาวาดก่อนตัวดวง (เดิมขอบในไม่มีโคโรนา เลยเป็นวงจุดดำรอบดวงอาทิตย์)
    sun = HTML[HTML.index("' if(sr<7.){',"):HTML.index("' if(sr<1.){',")]
    assert "smoothstep(.9,1.,sr)" in sun


def test_front_page_is_clean_and_fades_when_chatting():
    """พี่ขอเอาชื่อ สัจพจน์ และพระจันทร์ออกจากหน้าแรก · เริ่มพิมพ์หรือมีแชท โลกจางเหลือพื้นหลังเรียบ"""
    empty = HTML[HTML.index('<div id="empty">'):HTML.index('<div id="msgs"')]
    assert "<h1>" not in empty and "data-axis" not in empty and "koan" not in empty
    assert "data-axis" in HTML                                 # THE PURE AXIS ยังเปิดได้จากหน้าระบบ
    assert "var want = emptyOn && !(inp && inp.value.trim()) ? 1 : 0;" in HTML
    assert "if(!REDUCED && (DAWN.show > 0 || want > 0)) kick();" in HTML     # พื้นหลังเรียบไม่วาดซ้ำ ประหยัดแบต


def _simulate_frame_cap(hz, seconds=10):
    """ตรรกะเดียวกับต้น frame() — สะสมเวลา วาดเมื่อครบ 1/90 วินาที"""
    dt_last, acc, drawn, now = 0.0, 0.0, 0, 0.0
    for _ in range(hz * seconds):
        now += 1000 / hz
        gap = (now - (dt_last or now)) / 1000
        acc = min(acc + gap, 2 / 90)
        if dt_last and acc + 1e-4 < 1 / 90:
            dt_last = now
            continue
        acc = max(0.0, acc - 1 / 90)
        dt_last = now
        drawn += 1
    return drawn / seconds


def test_frame_rate_is_capped_at_90():
    """พี่ขอให้ลดเหลือ 90 เฟรม: จอ 120/144/240 Hz วาดเฉลี่ย 90 · จอ 60 Hz ยังวาดเต็ม 60"""
    assert "fpsAcc = Math.min(fpsAcc + gap, 2 / 90);" in HTML
    assert "if(dtLast && fpsAcc + 1e-4 < 1 / 90)" in HTML
    for hz in (120, 144, 240):
        assert abs(_simulate_frame_cap(hz) - 90) < 0.5
    assert abs(_simulate_frame_cap(60) - 60) < 0.5
