"""หน้าตาคำตอบและแสงบรรยากาศของทั้งแอป
เดิมคำตอบของ LYLA เป็นข้อความก้อนเดียว ("1) … 2) … 3) …" ติดกันเป็นพรืด) อ่านยากบนมือถือ
ตัวเลือกตั้งต้นของเครื่องมือจำลองค้างเป็นภาษาไทยในหน้าอังกฤษ และบรรทัดอธิบายสมการซ้ำกันสองบรรทัด"""
from tests._front import front_page

PAGE = front_page()


def test_replies_are_structured_without_touching_the_words():
    assert "function fmtReply(t){" in PAGE
    assert "telify(key === 'COUNCIL' ? councilFmt(m.t) : fmtReply(m.t))" in PAGE
    body = PAGE[PAGE.index("function fmtReply(t){"):PAGE.index("telify(html)")]
    # ทุกชิ้นของคำตอบผ่าน fmt() ซึ่ง esc ก่อนเสมอ — ไม่มีการต่อข้อความดิบลง HTML
    assert body.count("fmt(") >= 5 and "innerHTML" not in body
    assert "+m[1] === want" in body                         # เลขข้อต้องเรียงต่อกัน ไม่งั้นไม่นับเป็นรายการ
    for cls in ('class="steps"', 'class="ask"', 'class="sig"', 'class="src"'):
        assert cls in body
    for css in (".bubble .steps li::before{content:counter(st)", ".bubble .ask{", ".bubble .sig{"):
        assert css in PAGE


def test_default_options_follow_the_language():
    assert "var SIM_DEFAULTS = [" in PAGE and "document.addEventListener('kd:lang'" in PAGE
    assert "inp.dataset.def === '1' || inp.value === th" in PAGE     # ช่องที่ผู้ใช้แก้แล้วไม่ถูกเขียนทับ


def test_english_page_shows_one_explanation_line_per_equation():
    assert 'html[lang^="en"] .eq .nm[lang="th"]{display:none}' in PAGE


def test_dusk_light_is_code_only_and_dark_theme_only():
    i = PAGE.index("แสงสนธยา")
    block = PAGE[i:PAGE.index("คำตอบที่จัดโครงแล้ว", i)]
    assert 'html:not([data-ink="dark"])::before{' in block and "pointer-events:none" in block
    assert "url(" not in block and "animation" not in block     # ไม่มีไฟล์ภาพ ไม่มีการเคลื่อนไหว
    assert ":root{" not in block                                  # ไม่เพิ่มชุดสีใหม่ ตัวอักษรยังใช้ TIMELESS
