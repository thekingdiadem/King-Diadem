"""แท็บจักรวาล "กลุ่มดาวของฉัน" และดาวที่ลอยจากหน้าแชท

เจ้าของโปรเจกต์: หน้าจักรวาลเดิมฟ้าไหวตลอดและดาวเล็กจนมองไม่เห็น "ดูเวียนหัว" → ฟ้านิ่ง ดาวใหญ่พอแตะได้
คุย 1 ครั้งได้ดาว 1 ดวง ต่อเส้นตามลำดับเวลา และตอนได้คำตอบมีดาวลอยจากคำตอบไปที่ปุ่ม "จักรวาล\""""
from pathlib import Path
from tests._front import front_page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HTML = front_page()


def _frame():
    return HTML[HTML.index("  function frame(now){"):HTML.index("  function kick(){")]


def test_decisions_sky_is_still():
    f = _frame()
    branch = f[f.index("if(mode === 'decisions'){"):f.index("} else {", f.index("if(mode === 'decisions'){"))]
    assert "skyGeo(now, true)" in branch and "GLX.sky(s, 0, .85)" in branch     # มุมมองนิ่ง เวลาหยุด
    assert "stepCam(" not in branch and "drawFlows(" not in branch
    assert "else if(false)" not in f                                            # ไม่มีโค้ดตายค้าง
    assert "cam.drag = {" not in HTML                                           # ไม่มีการลากหมุนฟ้าแล้ว


def test_stars_are_tappable_and_colour_blind_friendly():
    body = HTML[HTML.index("function drawMySky(now){"):HTML.index("  function frame(now){")]
    assert "n.px = Math.max(16, r * 3);" in body                                 # วงแตะอย่างน้อย 16px
    assert "if(risk >= 75){" in body                                             # ความเสี่ยงสูงมีวงรอบ ไม่พึ่งสีอย่างเดียว
    assert "REDUCED ? 1 :" in body and "!REDUCED" in body                         # ลดการเคลื่อนไหว = นิ่ง
    lay = HTML[HTML.index("function layoutMine(){"):HTML.index("function drawMySky(now){")]
    assert "hash(n.key + '|ma' + tr)" in lay                                      # ตำแหน่งคงที่ตามรหัสข้อความ


def test_count_line_speaks_plainly():
    assert "'{n} ดวง · คุย 1 ครั้งได้ดาว 1 ดวง · แตะดาวเพื่อดูเรื่องที่คุย'" in HTML     # แปลได้ 3 ภาษา (static/i18n.js)
    assert "ยังไม่ระบุ waterline" not in HTML


def test_new_answer_sends_a_star_to_the_universe_tab():
    assert "if(view !== 'universe') flyStar();" in HTML
    fn = HTML[HTML.index("function flyStar(){"):HTML.index("function msgEl(m){")]
    assert "if(REDUCED || !src){ pop(); return; }" in fn                         # ลดการเคลื่อนไหว: ไม่ลอย
    assert "el.setAttribute('aria-hidden', 'true')" in fn and "el.remove()" in fn
    assert ".fly-star{position:fixed" in HTML and "pointer-events:none" in HTML
