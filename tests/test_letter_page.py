"""จดหมายจากผู้ก่อตั้ง (COSMIC LATTE CANON): ต้นฉบับใน LETTER.md · หน้าเว็บ /letter แสดงทุกบรรทัดตรงตัวอักษร"""
import html
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LETTER = (ROOT / "LETTER.md").read_text(encoding="utf-8")
PAGE = (ROOT / "static" / "letter.html").read_text(encoding="utf-8")


def _lines(section):
    body = LETTER.split(section)[1]
    body = body.split("## English Version")[0] if section == "## ภาษาไทย" else body
    return [ln for ln in body.strip().splitlines() if ln.strip()]


def _article(lang):
    m = re.search(r'<article class="letter" lang="%s"[^>]*>(.*?)</article>' % lang, PAGE, re.S)
    assert m, lang
    return [html.unescape(x) for x in re.findall(r'<span class="ln[^"]*">([^<]*)</span>', m.group(1))]


def test_every_line_of_the_letter_is_on_the_page_verbatim():
    """ถ้อยคำของพี่ต้องไม่ถูกดัดแปลง — ทุกบรรทัด ตามลำดับเดิม ทั้งไทยและอังกฤษ"""
    assert _article("th") == _lines("## ภาษาไทย")
    assert _article("en") == _lines("## English Version")
    assert len(_article("th")) == 39 and len(_article("en")) == 57


def test_builder_is_idempotent_and_keeps_both_languages(tmp_path):
    """สคริปต์สร้างเนื้อหาเคยกินบทความภาษาอังกฤษหายไปทั้งก้อน (regex ข้ามแท็กปิด) — รันซ้ำต้องได้ผลเดิม"""
    before = PAGE
    subprocess.run([sys.executable, "scripts/build_letter.py"], cwd=ROOT, check=True, capture_output=True)
    after = (ROOT / "static" / "letter.html").read_text(encoding="utf-8")
    assert after == before
    assert after.count('<article class="letter"') == 2


def test_canon_assertions_are_listed():
    """ข้อยืนยันทั้ง 5 ของ CANON จัดเป็นรายการ ข้อที่ขึ้นสองบรรทัดอยู่ในข้อเดียวกัน"""
    for lang in ("th", "en"):
        art = re.search(r'<article class="letter" lang="%s".*?</article>' % lang, PAGE, re.S).group(0)
        assert art.count("<li>") == 5, lang


def test_route_language_and_motion():
    app = (ROOT / "app.py").read_text(encoding="utf-8")
    assert '@app.get("/letter")' in app and 'FileResponse("static/letter.html")' in app
    assert "localStorage.setItem('kd_letter_lang', l)" in PAGE and "get('lang')" in PAGE
    assert 'aria-pressed="true">ไทย</button>' in PAGE
    assert "@media (prefers-reduced-motion: reduce)" in PAGE and "!REDUCED" in PAGE
    for f in ("guide.html", "king_diadem_universe.html"):
        assert 'href="/letter"' in (ROOT / "static" / f).read_text(encoding="utf-8"), f


def test_old_hero_png_is_gone():
    """พี่ให้ลบ hero.png เดิม — หน้าเข้าสู่ระบบใช้ hero.jpg / hero_m.jpg แล้ว"""
    assert not (ROOT / "static" / "hero.png").exists()


def test_letter_route(client):
    r = client.get("/letter")
    assert r.status_code == 200 and "COSMIC LATTE" in r.text
