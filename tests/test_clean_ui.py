"""หน้าแชทแบบคลีน (เจ้าของโปรเจกต์: "คลีนแบบพื้นหลังเดิม เข้าถึงง่าย ฟีลลิ่งเหมือนเข้าแอป Gemini ChatGPT Claude")
· ช่องพิมพ์เป็นการ์ดใบเดียว: ข้อความบน · โหมด ตัวเลือก ส่ง แถวล่าง · ตัวเลือก (W · เส้นทาง · ผู้ตอบ) ซ่อนหลังปุ่ม
· แผงขวาไม่ใช้ศัพท์ศาสนา ("ไม่ต้องแสดงมรรค เพื่อความสากล") — หลักคิดยังทำงานครบที่เซิร์ฟเวอร์"""
import json
import re
import shutil
import subprocess

import pytest

from tests._front import front_page

PAGE = front_page()


def _fn(name):
    i = PAGE.index("function " + name + "(")
    depth, j = 0, PAGE.index("{", i)
    for k in range(j, len(PAGE)):
        depth += {"{": 1, "}": -1}.get(PAGE[k], 0)
        if depth == 0:
            return PAGE[i:k + 1]


def test_composer_is_one_card_with_tools_inside():
    card = PAGE[PAGE.index('<div class="inrow">'):PAGE.index('</section>', PAGE.index('<div class="inrow">'))]
    for need in ('id="input"', 'id="mode-seg"', 'id="opts-btn"', 'id="send"'):
        assert need in card, need
    assert 'aria-controls="comp-opts"' in card and 'id="comp-opts"' in PAGE
    assert "$('#opts-btn').addEventListener('click'" in PAGE                     # CSP: ไม่ใช้ onclick
    assert "#composer:not(.opts-open) .comp-row1{display:none}" in PAGE


def test_options_toggle_is_announced_to_screen_readers():
    assert "setAttribute('aria-expanded', open)" in _fn("setOpts")


def test_starters_fit_small_phones_without_sideways_scroll():
    block = PAGE[PAGE.index("/* ══ CLEAN CHAT"):]
    assert re.search(r"@media \(max-width:520px\)\{\s*\.st-row\{display:grid;grid-template-columns:1fr 1fr", block)


@pytest.mark.skipif(not shutil.which("node"), reason="ต้องใช้ node")
def test_reading_panel_uses_universal_words():
    js = "\n".join(_fn(n) for n in ("esc", "ariyaHTML", "maggaHTML"))
    js = "function _t(s){return s;}\n" + js + """
    var ar = {dukkha: 'หนี้มากกว่ากำลังผ่อน', samudaya: 'ดอกเบี้ยสูง', nirodha: 'ผ่อนไหว', magga: 'คุยธนาคาร', clear: true};
    var good = [{name: 'สัมมาวาจา', ok: true, note: ''}];
    var bad = [{name: 'สัมมาวาจา', ok: false, note: 'คำพูดที่หลอกคนอื่น ทำให้ความไว้ใจพัง'}, {name: 'สัมมาทิฏฐิ', ok: true, note: ''}];
    console.log(JSON.stringify([ariyaHTML({ariya: ar}), maggaHTML({magga: good}), maggaHTML({magga: bad})]));"""
    reading, clean, caution = json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout)
    for word in ("ปัญหา", "สาเหตุ", "ปลายทาง", "ทางไป", "หนี้มากกว่ากำลังผ่อน"):
        assert word in reading
    for word in ("อริยสัจ", "ทุกข์", "สมุทัย", "นิโรธ", "มรรค", "สัมมา"):
        assert word not in reading + caution, word
    assert clean == ""                                                            # ผ่านหมด ไม่ต้องโชว์อะไร
    assert "ข้อควรระวัง" in caution and "ความไว้ใจพัง" in caution


def test_new_words_translate_to_every_language():
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent / "static"
    words = ("อ่านเรื่องนี้", "ปัญหา", "สาเหตุ", "ปลายทาง", "ทางไป", "ข้อควรระวัง", "ตัวเลือกเพิ่มเติม")
    core = (root / "i18n.js").read_text(encoding="utf-8")
    assert all(f"'{w}':" in core for w in words)
    for lang in ("zh", "ko", "es", "vi"):
        pack = (root / "i18n" / f"{lang}.js").read_text(encoding="utf-8")
        assert all(f'"{w}":' in pack for w in words), lang
