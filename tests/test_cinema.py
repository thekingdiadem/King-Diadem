"""หน้าเว็บระดับหนัง: เปิดเรื่องจอกว้างครั้งเดียว · กระจกขอบแสงสองสี · ข้อความใหม่ดึงโฟกัส
ทุกอย่างต้องไม่กินแบต ไม่บังการใช้งาน และหยุดทั้งหมดเมื่อผู้ใช้ขอลดการเคลื่อนไหว"""
import re
from pathlib import Path

HTML = (Path(__file__).resolve().parent.parent / "static" / "index.html").read_text(encoding="utf-8")
HEAD = HTML[:HTML.index("</head>")]
CSS = HTML[HTML.index("<style>"):HTML.index("</style>")]


def test_opening_plays_once_per_tab_and_can_be_skipped():
    """ฉากเปิดเรื่องเล่นครั้งเดียวต่อแท็บ ไม่เล่นตอนกลับจากหน้าจ่ายเงิน · แตะ/กดปุ่มข้ามได้ · หายเองใน 3.4 วินาที"""
    assert "sessionStorage.getItem('kd_opened')" in HEAD and "sessionStorage.setItem('kd_opened', '1')" in HEAD
    assert "/[?&]payment=/.test(location.search)" in HEAD
    assert "matchMedia('(prefers-reduced-motion: reduce)').matches" in HEAD
    assert "setTimeout(end, 3400);" in HEAD
    assert "addEventListener('pointerdown', end" in HEAD and "addEventListener('keydown', end" in HEAD
    # ม่านไม่รับคลิก — ระหว่างเปิดเรื่องยังพิมพ์/กดได้ · ชื่อแบรนด์ไม่ถูกแปล
    assert "html.opening #lb{display:block;position:fixed;inset:0;z-index:97;pointer-events:none;" in CSS
    assert '<div id="lb" aria-hidden="true" data-i18n-skip>' in HTML


def test_reduced_motion_also_stops_pseudo_element_effects():
    """กฎเดิม *{animation:none} ไม่ครอบ ::before/::after — แสงวิ่งรอบช่องพิมพ์ เม็ดฟิล์ม แสงวาบ ต้องหยุดด้วย"""
    assert re.search(r"prefers-reduced-motion:reduce\)\{ \*::before,\*::after\{animation:none!important;transition:none!important\}", CSS)
    assert "if(!REDUCED && i >= last - 6)" in HTML
    assert "th.className = 'm a' + (REDUCED ? '' : ' enter')" in HTML


def test_decorative_motion_does_not_drain_battery():
    """เม็ดฟิล์มขยับเฉพาะจอคอมตอนเห็นฉาก (หน้าแรก/จักรวาล) — มือถือและหน้าข้อมูลนิ่ง
    แสงวาบบนชื่อแบรนด์เล่น 4 รอบแล้วพัก ไม่ปลุกการวาดทุกเฟรมตลอดไป"""
    assert '@media (hover:hover) and (pointer:fine){ body[data-veil="0"]::after{animation:kd-grain' in CSS
    assert len(re.findall(r"animation:kd-grain", CSS)) == 1
    assert "animation:kd-gleam 12s var(--ease-io) 3s 4}" in CSS
    assert "mix-blend-mode:overlay" in CSS                                 # พื้นมืดแทบไม่เปลี่ยน คงความคลีน


def test_messages_focus_in_once():
    """ข้อความใหม่ดึงโฟกัสจากเบลอเป็นคม แต่ข้อความเก่าไม่ขยับซ้ำทุกครั้งที่วาดใหม่ (ตอนส่ง/ได้คำตอบ)"""
    assert "var SEEN = Object.create(null);" in HTML
    assert "if(!SEEN[k]){ SEEN[k] = 1;" in HTML
    assert ".m.enter{animation:kd-focus" in CSS
    assert "@keyframes kd-focus{from{opacity:0;transform:translateY(12px);filter:blur(8px)}to{opacity:1;transform:none;filter:none}}" in CSS


def test_thinking_ring_follows_the_real_request():
    """แสงโคจรรอบช่องพิมพ์ผูกกับ KD:thinking ที่ยิงจริงตอนเริ่ม/จบคำขอ /run"""
    assert "addEventListener('KD:thinking', function(e){ document.body.classList.toggle('kd-busy', !!(e.detail && e.detail.on)); });" in HTML
    assert "body.kd-busy .inrow::after{opacity:1;animation:kd-orbit" in CSS
    assert '@property --kd-a{syntax:"<angle>"' in CSS
    assert "conic-gradient(from var(--kd-a,0deg)" in CSS                   # เบราว์เซอร์ที่ไม่รู้จัก @property ยังเห็นวงแสง


def test_mobile_dock_keeps_the_reserved_space():
    """แท็บล่างลอยเป็นแท่นกระจก แต่กินพื้นที่เท่าเดิม (--tab-h) ช่องพิมพ์/เมนู/การ์ดจักรวาลไม่ถูกบัง"""
    block = CSS[CSS.index("แท็บล่างมือถือ: แท่นกระจกลอย"):]
    assert "bottom:calc(8px + var(--sab));height:calc(var(--tab-h) - 8px);padding-bottom:0" in block


def test_toast_is_as_wide_as_its_message():
    """เดิม left:50% ทำให้แจ้งเตือนกว้างได้แค่ครึ่งจอ ข้อความสั้นๆ ก็ตัดเป็น 3 บรรทัดบนมือถือ"""
    assert "#toast{width:max-content;" in CSS
    assert "max-width:min(92vw,560px)" in CSS


def test_view_title_animates_only_on_real_view_change():
    """การ์ดชื่อฉากเล่นตอนเปลี่ยนหน้า — เลือกแชทเดิมซ้ำ (Chat.select เรียก setView('chat')) ไม่กระพริบ"""
    assert "var prev = curView; curView = v;" in HTML
    assert "if(prev !== v || !vt.classList.contains('cut'))" in HTML


def test_depth_parallax_does_not_jump():
    """ดาวไกลกับเนบิวลาเลื่อนต่างกันให้ฉากมีความลึก · เวลาของกล้องเดินเฉพาะตอนวาด กลับมาวาดใหม่ดาวไม่กระโดด
    · เมาส์เท่านั้นที่ขยับมุมกล้อง นิ้วปัดยังใช้หมุนโลกตามเดิม"""
    assert "uniform vec2 uPar;" in HTML and "'uNeb','uPar']" in HTML
    assert "vec2 sp=p+uPar*.4;" in HTML and "vec2 np=p+uPar*.85;" in HTML
    assert "PAR.t += dt;" in HTML and "drew = GLX.dawn({ par: par," in HTML
    assert "e.pointerType === 'mouse'" in HTML
    assert "float nm=smoothstep(1.,0.," in HTML                            # เนบิวลาเดิมยังอยู่


def test_display_serif_is_looped_thai():
    """หัวข้อละตินเป็น Orbitron (แนว "อนาคตลึกลับ" ที่เจ้าของโปรเจกต์เลือก) แต่ตัวไทยยังเป็นแบบมีหัว
    — แบบไม่มีหัวทำให้ "ระบบ" อ่านเป็น "ระUU" บนมือถือ"""
    assert "family=Orbitron:wght@500;600;700" in HTML and "Cinzel" not in HTML
    assert '--f-title:"Orbitron","Noto Sans Thai Looped","Noto Serif Thai",system-ui,sans-serif;' in CSS
