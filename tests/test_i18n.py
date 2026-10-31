"""หน้าเว็บ 3 ภาษา (ไทย · English · 日本語) — ROADMAP Phase 7: Multi-language"""
import pathlib
import re
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
JS = (ROOT / "static" / "i18n.js").read_text(encoding="utf-8")
TH = re.compile("[ก-ฺเ-๙]")                  # ไม่นับ ฿ (สัญลักษณ์เงิน ใช้ได้ทุกภาษา)
ENTRY = re.compile(r"'([^']*[ก-๙][^']*)':\s*\[\s*'([^']*)',\s*'([^']*)'\s*\]")


def _static_thai():
    body = PAGE[PAGE.index("<body"):PAGE.index('<script type="application/json"')]
    found = set()

    class P(HTMLParser):
        skip = False

        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            self.skip = tag == "style" or a.get("id") == "lang-pick" or tag == "option"
            if self.skip:
                return
            for k, v in attrs:
                if k in ("title", "placeholder", "aria-label", "alt") and v and TH.search(v):
                    found.add(v.strip())

        def handle_data(self, d):
            if d.strip() and TH.search(d) and not self.skip:
                found.add(d.strip())

    P().feed(body)
    return found


def test_every_static_thai_text_has_translations():
    """เพิ่มปุ่ม/ป้ายภาษาไทยใหม่ในหน้า ต้องเพิ่มคำแปลใน static/i18n.js ด้วย — ไม่งั้นโหมด EN/JA จะมีไทยโผล่"""
    missing = _static_thai() - {th for th, _, _ in ENTRY.findall(JS)}
    assert not missing, f"ยังไม่มีคำแปล: {sorted(missing)}"


def test_each_entry_has_english_and_japanese():
    entries = ENTRY.findall(JS)
    assert len(entries) == len(re.findall(r"'[^']*[ก-๙][^']*':\s*\[", JS))     # ไม่มีรายการที่ขาดภาษา
    for th, en, ja in entries:
        assert en and not TH.search(en), th
        assert ja and not TH.search(ja), th


def test_page_has_switcher_and_script():
    assert 'id="lang-pick"' in PAGE and "/static/i18n.js" in PAGE
    for v in ("th", "en", "ja"):
        assert f'<option value="{v}">' in PAGE


def test_chat_messages_are_never_translated():
    """คำตอบ/ข้อความผู้ใช้ห้ามถูกแปลงด้วยพจนานุกรม (เช่น "มี" "ปกติ" ในประโยค)"""
    assert ".m,.bubble,#sim-out" in JS


def test_storage_failure_does_not_break_page():
    uses = JS.count("localStorage.")
    assert uses == 2 and len(re.findall(r"try \{[^}]*localStorage\.", JS)) == uses


def _t_keys():
    """ข้อความไทยทุกตัวที่ส่งเข้า _t() ในหน้าแรก (รวมแบบ เงื่อนไข ? 'ก' : 'ข')"""
    keys = set()
    for call in re.finditer(r"_t\(((?:[^()]|\([^()]*\))*)\)", PAGE):
        for lit in re.findall(r"'((?:[^'\\]|\\.)*)'", call.group(1)):
            if TH.search(lit):
                keys.add(lit.strip())
    return keys


def test_every_scripted_thai_text_has_translations():
    """ข้อความที่สคริปต์ประกอบเอง (ตัวเลขแทรก · ป๊อปอัปยืนยัน · ข้อความในกล่องแชท) ต้องมีคำแปลด้วย
    ไม่งั้นคนที่เลือก English/日本語 จะเจอไทยโผล่กลางจอ"""
    have = {th for th, _, _ in ENTRY.findall(JS)}
    missing = _t_keys() - have
    assert not missing, f"ยังไม่มีคำแปล: {sorted(missing)}"


def test_templates_keep_their_placeholders():
    """คำแปลของข้อความที่มี {n} {t} ต้องมีช่องเดียวกันครบ ไม่งั้นตัวเลขหายไปจากประโยค"""
    for th, en, ja in ENTRY.findall(JS):
        want = sorted(re.findall(r"\{\w+\}", th))
        assert sorted(re.findall(r"\{\w+\}", en)) == want, th
        assert sorted(re.findall(r"\{\w+\}", ja)) == want, th


def test_language_switch_redraws_scripted_text():
    assert "kd:lang" in JS and "addEventListener('kd:lang'" in PAGE


def _page_thai(name):
    html = (ROOT / "static" / name).read_text(encoding="utf-8")
    found = set()

    class P(HTMLParser):
        skip = False

        def handle_starttag(self, tag, attrs):
            self.skip = tag in ("style", "script")
            for k, v in attrs:
                if k in ("title", "placeholder", "aria-label", "alt") and v and TH.search(v):
                    found.add(v.strip())

        def handle_endtag(self, tag):
            self.skip = False

        def handle_data(self, d):
            if not self.skip and d.strip() and TH.search(d):
                found.add(d.strip())

    P().feed(html)
    return html, found


import pytest  # noqa: E402


@pytest.mark.parametrize("name", ["login.html", "register.html", "wallet.html", "guide.html"])
def test_other_pages_are_translated_too(name):
    """หน้าเข้าสู่ระบบ · สมัคร · กระเป๋าเงิน · คู่มือ ต้องโหลดตัวแปลและมีคำแปลครบ
    (ภาษาเลือกครั้งเดียวที่หน้าแรก จำไว้ในเครื่อง หน้าอื่นใช้ตาม)"""
    html, found = _page_thai(name)
    assert '<script src="/static/i18n.js" defer></script>' in html
    missing = found - {th for th, _, _ in ENTRY.findall(JS)}
    assert not missing, f"{name} ยังไม่มีคำแปล: {sorted(missing)}"


@pytest.mark.parametrize("name", ["login.html", "register.html", "wallet.html"])
def test_scripted_messages_on_other_pages_have_translations(name):
    html = (ROOT / "static" / name).read_text(encoding="utf-8")
    have = {th for th, _, _ in ENTRY.findall(JS)}
    keys = set()
    for call in re.finditer(r"_t\(((?:[^()]|\([^()]*\))*)\)", html):
        for lit in re.findall(r"'((?:[^'\\]|\\.)*)'", call.group(1)):
            if TH.search(lit):
                keys.add(lit.strip())
    assert not keys - have, sorted(keys - have)
