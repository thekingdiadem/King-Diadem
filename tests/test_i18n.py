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
