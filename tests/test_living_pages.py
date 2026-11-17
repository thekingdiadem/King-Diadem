"""หน้าเครื่องมือและหน้าระบบ — เจ้าของโปรเจกต์: "ไม่เท่ ไม่คูล ไม่ล้ำ" ใต้ตราเป็นฟอร์มธรรมดา
  · เครื่องมือ: ทางเลือกเป็นดาวโคจรรอบตรา สีตามผลจริงจาก /simulate · ทางที่รอดดีที่สุดมีเส้นแสงลงที่หยดแสง
  · ระบบ: ตัวเลขเป็นหน้าปัดวงแหวน · สมการเป็นการ์ดบนแกนกลาง แตะเพื่อกาง
ต้องไม่มีลูปวาดตลอดเวลา และหยุดการเคลื่อนไหวเมื่อเลือกลดการเคลื่อนไหว"""
from tests._front import front_page

PAGE = front_page()


def test_options_become_stars_colored_by_the_real_simulation():
    assert '<svg id="sim-orbit" viewBox="-110 -110 220 220" aria-hidden="true"></svg>' in PAGE
    assert "drawFuture(d.future); orbitFromFuture(d.future);" in PAGE
    body = PAGE[PAGE.index("function orbitFromFuture(f){"):PAGE.index("drawOrbit();\n", PAGE.index("function orbitFromFuture(f){"))]
    assert "v < floor ? 'risk' : 'safe'" in body and "ORBIT.res[best] = 'best'" in body
    assert "requestAnimationFrame" not in PAGE[PAGE.index("var ORBIT = { res: null };"):]           # วาดเฉพาะตอนพิมพ์/ได้ผล
    assert "html.kd-calm #sim-orbit *{transition:none!important;animation:none!important" in PAGE


def test_editing_options_clears_stale_results():
    assert "$('#sim-paths').addEventListener('input', function(){ ORBIT.res = null; drawOrbit(); });" in PAGE


def test_system_page_uses_gauges_and_an_equation_deck():
    assert '<div class="stats gauges" id="sys-stats"></div>' in PAGE and "$('#sys-eq').outerHTML = eqDeck();" in PAGE
    assert "function ring(v, of, label, cls){" in PAGE and "ring(live, py," in PAGE
    assert '<details class="eqd"><summary>' in PAGE          # กางได้ด้วยคีย์บอร์ด ไม่ต้องมีสคริปต์
