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
