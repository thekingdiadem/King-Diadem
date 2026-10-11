"""หน้ารอง Guide · Ask · Report: ชั้นภาพยนตร์เดียวกับทั้งเว็บ (cinema.css) · เนื้อหาตรงกับแอปจริง · อ่านง่าย กดด้วยคีย์บอร์ดได้"""
import re
from pathlib import Path

S = Path(__file__).resolve().parent.parent / "static"
GUIDE = (S / "guide.html").read_text(encoding="utf-8")
ASK = (S / "ask.html").read_text(encoding="utf-8")
REPORT = (S / "report.html").read_text(encoding="utf-8")
CINEMA = (S / "cinema.css").read_text(encoding="utf-8")


def test_pages_share_the_cinema_layer():
    for page in (GUIDE, ASK, REPORT):
        assert '<link rel="stylesheet" href="/static/cinema.css">' in page
        assert '<canvas id="sky"' in page and '<script src="/static/cinema_sky.js" defer></script>' in page
    # ขอบแสงสองโทนแบบไม่ใช้ pseudo — ใส่กับการ์ดที่ใช้ ::before/::after อยู่แล้ว (โมดูลของ Guide) ได้
    assert ".kd-rim { border: 1px solid transparent !important; background: var(--kd-pane) padding-box, var(--kd-rim) border-box !important;" in CINEMA
    assert GUIDE.count('kd-rim"') >= 6 and ASK.count("kd-rim") >= 2
    assert REPORT.count("'<div class=\"card kd-rim\">") == 7 and "'<div class=\"card\">" not in REPORT


def test_guide_describes_the_app_as_it_is_today():
    """คู่มือเดิมเป็นภาษาอังกฤษและพูดถึง BRAIN กับ "ดาวเคราะห์แต่ละดวงคือเส้นทาง" ซึ่งไม่มีในแอปแล้ว
    ตอนนี้ตรงกับแท็บจริง: ปรึกษา · จักรวาล · เครื่องมือ · Wallet · ระบบจริง"""
    assert "BRAIN" not in GUIDE and "planet" not in GUIDE.lower()
    for th in ("ปรึกษา", "จักรวาล", "เครื่องมือ", "กระเป๋าเครดิต", "ระบบจริง"):
        assert f'<span class="module-th">{th}</span>' in GUIDE
    assert "ฟรีวันละ 20 ข้อความ" in GUIDE and "PromptPay" in GUIDE
    assert "จักรวาลไม่ได้หมุนรอบใคร แต่ทุกคนร่วมกันเป็นส่วนหนึ่งของทั้งจักรวาล" in GUIDE
    assert 'href="/ask"' in GUIDE and 'href="/wallet"' in GUIDE
    assert "s.className = 'star'" not in GUIDE          # เลิกสร้างดาว DOM 180 จุดที่แอนิเมตทุกจุด


def test_free_quota_in_guide_matches_the_server_default():
    app = (S.parent / "app.py").read_text(encoding="utf-8")
    assert 'FREE_DAILY_RUNS = max(0, int(os.getenv("FREE_DAILY_RUNS", "20")))' in app


def test_route_choice_works_with_a_keyboard():
    """เส้นทางการวิเคราะห์เดิมเป็น <span onclick> กด Tab ไปไม่ถึง · ตอนนี้เป็นปุ่มที่บอกสถานะ aria-pressed"""
    pills = re.findall(r'<button type="button" class="rpill( active)?" data-r="(\w+)" aria-pressed="(true|false)"', ASK)
    assert len(pills) == 6 and [p[2] for p in pills].count("true") == 1
    assert '<span class="rpill' not in ASK
    assert "r.setAttribute('aria-pressed','false')" in ASK and "el.setAttribute('aria-pressed','true')" in ASK
    assert '<label for="situation">' in ASK and 'onmouseover=' not in ASK


def test_small_text_is_readable():
    """ตัวหนังสือเล็ก (ROUTE · PASS · หัวข้อส่วน) เดิมใช้สีทึบแค่ 26% บนพื้นมืด แทบมองไม่เห็น
    และหัวข้อภาษาไทยถูกยืดระยะตัวอักษรแบบภาษาอังกฤษ"""
    for page in (ASK, REPORT):
        assert "rgba(60,95,170,0.26)" not in page
    assert "--tx-lo:  rgba(160,172,215,0.52);" in REPORT
    assert ".kd-th { font-family: 'Noto Sans Thai Looped'" in CINEMA
    assert "font-family:var(--f-body);font-size:13px;letter-spacing:.01em;" in ASK      # label ของฟอร์ม
    assert "'<div class=\"sec-title kd-th\">แชร์ REPORT นี้</div>'" in REPORT
