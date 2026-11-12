"""ฉากเปิดครั้งแรก — ตราใหญ่ แกนแสงลงจากฟ้า หยดแสงกระทบพื้นสะท้อนเป็นวงคลื่น (ภาพแนวคิดของเจ้าของโปรเจกต์)
ต้องไม่ขวางคน: เล่นครั้งเดียว ข้ามได้ทันที ไม่เล่นเมื่อลดการเคลื่อนไหวหรือมากับลิงก์ที่มีคำสั่ง และไม่มีทางค้างบังหน้าเว็บ"""
from tests._front import front_page

PAGE = front_page()


def test_intro_is_decided_before_first_paint_and_only_once():
    head = PAGE[:PAGE.index("</head>")]
    assert "!localStorage.getItem('kd-intro')" in head and "h.classList.add('kd-intro')" in head
    assert "localStorage.getItem('kd-calm') !== '1'" in head and "prefers-reduced-motion: reduce" in head
    assert "!location.search" in head                         # ?ask=… = มาด้วยเรื่องด่วน ไม่มีฉากคั่น
    assert "lsSet('kd-intro', '1');" in PAGE


def test_intro_is_hidden_by_default_and_cannot_get_stuck():
    assert "#kd-intro{display:none}" in PAGE
    assert "window.addEventListener('pointerdown', end, true); window.addEventListener('keydown', end, true);" in PAGE
    assert "setTimeout(end, 4500);" in PAGE and "e.animationName === 'kd-intro-out'" in PAGE


def test_intro_scene_parts_and_no_looping_animation():
    assert '<div id="kd-intro" aria-hidden="true">' in PAGE
    for part in ("in-crest", "in-mirror", "in-axis", "in-ripple", "in-word"):
        assert 'class="%s"' % part in PAGE, part
    css = PAGE[PAGE.index("ฉากเปิดครั้งแรก (#kd-intro)"):PAGE.index("@keyframes kd-intro-word")]
    assert "infinite" not in css and "url(" not in css
