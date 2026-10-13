"""ตัวอักษรภาษาไทยบนเว็บ: ใช้ฟอนต์หัวกลม (Noto Sans Thai Looped) และไม่ถ่างตัวอักษร

เคยมีข้อความไทยหลายจุด (เช่น ป้ายแถบเลื่อน "ENTROPY (ความวุ่นวาย)" ในหน้า Universe, หัวการ์ด/ปุ่มในหน้าหลัก)
ที่ฟอนต์ตั้งเป็น DM Mono / Cinzel ล้วน ซึ่งไม่มีตัวไทย เบราว์เซอร์เลยหยิบฟอนต์ระบบมาแทนแบบสุ่มตามเครื่อง
และถ่างตัวอักษร .08–.30em ทำให้สระ/วรรณยุกต์ลอยห่างจากพยัญชนะ อ่านยาก
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"
LATIN_ONLY = ("DM Mono", "IBM Plex Mono", "Cinzel", "Cormorant Garamond")
THAI = ("Noto Sans Thai Looped", "Noto Serif Thai")


def _read(name):
    return (STATIC / name).read_text(encoding="utf-8")


def _font_vars():
    for path in sorted(list(STATIC.glob("*.html")) + list(STATIC.glob("*.css"))):
        text = path.read_text(encoding="utf-8")
        for name, stack in re.findall(r"(--f-[a-z]+)\s*:\s*([^;]+);", text):
            fams = [f.strip().strip("'\"") for f in stack.split(",")]
            yield path.name, name, fams


def test_latin_font_stacks_fall_back_to_a_thai_font_next():
    """ฟอนต์ละติน (ไม่มีตัวไทย) ต้องมีฟอนต์ไทยเป็นตัวถัดไปทันที ไม่ใช่ปล่อยให้ตกไปฟอนต์ระบบ"""
    checked = 0
    for page, name, fams in _font_vars():
        if fams[0] in LATIN_ONLY and not name.endswith("-en"):   # --f-en ใช้กับข้อความอังกฤษล้วน
            checked += 1
            assert len(fams) > 1 and fams[1] in THAI, (page, name, fams)
    assert checked >= 15


def test_universe_thai_labels_are_not_letter_spaced():
    html = _read("king_diadem_universe.html")
    rule = re.search(r"\n([^\n{}]*\.sim-btn[^\n{}]*)\{letter-spacing:\.01em\}", html)
    assert rule, "ไม่พบกฎลดระยะตัวอักษรของข้อความไทย"
    for cls in (".scroll-hint", ".hz-hint", ".ego-tap", ".sec-title", ".sim-sub", ".sim-note",
                ".intent-label", ".sim-btn", ".dignity-text", ".ego-quote cite"):
        assert cls in rule.group(1), cls
    assert ".th-run{font-family:var(--f-body);letter-spacing:.01em}" in html


def test_universe_slider_labels_keep_layout_and_thai_run():
    """ส่วนไทยในป้ายแถบเลื่อนอยู่ใน .th-run และชื่อทั้งก้อนอยู่ใน .sl-name
    (label เป็น flex space-between — ถ้า span ไทยเป็นลูกตรงๆ วงเล็บจะถูกถ่างกระจายเต็มบรรทัด)"""
    html = _read("king_diadem_universe.html")
    labels = re.findall(r'<label for="sl-[a-z]+">(.*?)</label>', html)
    assert len(labels) == 4
    for lab in labels:
        assert re.match(r'<span class="sl-name">[A-Z ]+ \(<span class="th-run">[^<]+</span>\)</span> <span id="[a-z]-val">', lab), lab
    assert ".slider-item label span[id]{color:var(--gold-hi)}" in html


def test_home_page_tightens_spacing_only_in_thai():
    """หน้าหลักสลับภาษาได้ (i18n.js ตั้ง <html lang>) — ภาษาอังกฤษยังถ่างตัวอักษรแบบเดิม"""
    html = _read("index.html")
    m = re.search(r"html:lang\(th\) :is\(([^)]*)\)\{letter-spacing:\.01em\}", html)
    assert m
    for sel in (".acc-link", "#view-title", ".chip", ".seg button", ".card-h h2", ".dlg-h h2"):
        assert sel in m.group(1), sel


def test_portal_submit_button_is_not_letter_spaced():
    css = _read("portal.css")
    rule = re.search(r"\.submit-btn, \.email-form button \{([^}]*)\}", css).group(1)
    assert "letter-spacing: .01em" in rule


def test_offline_page_prefers_looped_font():
    assert 'font-family: "Noto Sans Thai Looped", system-ui, sans-serif;' in _read("offline.html")


def test_letter_thai_toggle_uses_looped_font():
    assert '.lang button[data-set="th"] { font-family: \'Noto Sans Thai Looped\', sans-serif; letter-spacing: .01em; }' in _read("letter.html")
