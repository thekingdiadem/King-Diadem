"""หน้าเข้าสู่ระบบ / สมัคร: ภาพ hero ใหม่ของแบรนด์ · การ์ดกระจกแบบเดียวกับทั้งเว็บ · เลื่อนได้เสมอ"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
S = ROOT / "static"
LOGIN = (S / "login.html").read_text(encoding="utf-8")
REGISTER = (S / "register.html").read_text(encoding="utf-8")
CSS = (S / "portal.css").read_text(encoding="utf-8")
SKY = (S / "cinema_sky.js").read_text(encoding="utf-8")


def test_card_is_never_cut_off_on_short_screens():
    """เดิม html/body ล็อก overflow:hidden และจัดการ์ดกึ่งกลางด้วย flex — บนมือถือที่เปิดฟอร์มอีเมล
    (และโน้ตบุ๊กจอเตี้ย) หัวการ์ดหายไป 60–160px แล้วเลื่อนขึ้นไปดูไม่ได้
    ตอนนี้หน้าเลื่อนได้ และใช้ margin:auto ซึ่งเมื่อการ์ดสูงกว่าจอจะเริ่มจากด้านบนแทนการล้นขึ้นไป"""
    for page in (LOGIN, REGISTER):
        assert "overflow: hidden;" not in page and "<style>" not in page
        assert '<link rel="stylesheet" href="/static/portal.css">' in page
    assert "body { overflow-x: hidden; overflow-y: auto; }" in CSS
    assert ".card { width: 100%; max-width: 420px; margin: auto;" in CSS
    assert "min-height: 100dvh" in CSS and not re.search(r"#app \{[^}]*(?<![-\w])height: 100dvh", CSS)


def test_sharp_hero_is_light_enough_for_phones():
    """ภาพ hero 4K ที่พี่ให้มาถูกย่อเป็นสองขนาด: มือถือโหลดรุ่นเล็ก จอใหญ่/จอความละเอียดสูงโหลดรุ่นคม"""
    big, small = S / "hero.jpg", S / "hero_m.jpg"
    assert big.stat().st_size < 1_000_000 and small.stat().st_size < 300_000
    assert "url('/static/hero_m.jpg')" in CSS and "url('/static/hero.jpg')" in CSS
    for page in (LOGIN, REGISTER):
        assert 'href="/static/hero_m.jpg" media="(max-width: 899px)"' in page


def test_same_visual_language_as_the_app():
    """ฟอนต์ไทยแบบมีหัว (แบบไม่มีหัวทำให้ "ระบบ" อ่านเป็น "ระUU") · ขอบแสงสองโทน · ฟ้าดาวไม่มีศูนย์กลาง"""
    for page in (LOGIN, REGISTER):
        assert "Noto+Sans+Thai+Looped" in page and "Orbitron" not in page
        assert '<canvas id="sky"' in page and '<script src="/static/cinema_sky.js" defer></script>' in page
        assert 'id="particles"' not in page
    assert "--rim: linear-gradient(135deg, rgba(214,224,255,.48)" in CSS
    assert ".card-inner > * { animation: kd-rack .9s var(--ease) backwards; }" in CSS   # ปุ่ม disabled ยังจางตามจริง
    for f in ("ask.html", "guide.html", "report.html"):
        t = (S / f).read_text(encoding="utf-8")
        assert "Noto+Sans+Thai+Looped" in t and "'Noto Sans Thai'" not in t, f


def test_auth_logic_is_untouched():
    """ปรับแค่หน้าตา — ฟอร์ม ID และ endpoint เดิมอยู่ครบ"""
    for i in ("login-email", "login-password", "login-btn", "login-msg", "email-toggle"):
        assert f'id="{i}"' in LOGIN
    assert "fetch('/login'" in LOGIN and 'href="/login/google"' in LOGIN
    for i in ("email", "password", "confirm", "msg"):
        assert f'id="{i}"' in REGISTER
    assert "'/register'" in REGISTER and "async function register()" in REGISTER


def test_shared_sky_has_no_center_and_respects_motion():
    """ดาวสุ่มกระจายทั่วจอ · จำกัด ~30 เฟรม · หยุดเมื่อซ่อนแท็บ · ลดการเคลื่อนไหว = ภาพนิ่ง"""
    assert "x: Math.random() * W0, y: Math.random() * H0" in SKY
    assert "if (t - last < 33) return;" in SKY
    assert "visibilitychange" in SKY
    assert "if (REDUCED) { draw(0); return; }" in SKY
