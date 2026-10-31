"""มือถือ: กด "ทั่วไป ▾" แล้วเมนูเส้นทางไม่ขึ้น (แลปท็อปขึ้นปกติ)

แถวปุ่มใต้ช่องพิมพ์ (.comp-row1) บนจอแคบเลื่อนแนวนอนได้ (overflow-x:auto) เบราว์เซอร์จึงตัด
เมนูที่ลอยเหนือแถวทิ้งทั้งหมด → เมนูต้องวางตำแหน่งตามจอ (position:fixed) เหนือปุ่ม"""
import re
import shutil
import subprocess
from pathlib import Path

import pytest
from tests._front import front_page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HTML = front_page()


def test_row_still_scrolls_on_phones():
    assert re.search(r"@media \(max-width:899px\)\{[^@]*\.comp-row1\{overflow-x:auto", HTML)


def test_route_menu_escapes_the_scrolling_row():
    fn = HTML[HTML.index("function routeMenu(on){"):HTML.index("addEventListener('resize', function(){ routeMenu(false); });")]
    assert "m.style.position = 'fixed'" in fn and "pill.getBoundingClientRect()" in fn
    assert "m.style.bottom = (innerHeight - r.top + 8) + 'px'" in fn


@pytest.mark.skipif(not shutil.which("node"), reason="ต้องมี node")
def test_menu_opens_above_the_pill_on_a_phone_sized_screen(tmp_path):
    """รันฟังก์ชันจริงจาก index.html กับปุ่มจำลองที่อยู่ล่างจอมือถือ"""
    fn = HTML[HTML.index("function routeMenu(on){"):HTML.index("  addEventListener('resize', function(){ routeMenu(false); });")]
    js = """
    var cls = new Set(['hide']), menu = { style: {}, classList: { toggle: function(c, v){ v ? cls.add(c) : cls.delete(c); } } };
    var pill = { attrs: {}, getBoundingClientRect: function(){ return { left: 120, top: 760 }; }, setAttribute: function(k, v){ this.attrs[k] = v; } };
    var innerWidth = 390, innerHeight = 844;
    function $(q){ return q === '#route-menu' ? menu : pill; }
    """ + fn + """
    routeMenu(true);
    console.log(JSON.stringify({ pos: menu.style.position, left: menu.style.left, bottom: menu.style.bottom, hidden: cls.has('hide'), exp: pill.attrs['aria-expanded'] }));
    """
    f = tmp_path / "m.js"; f.write_text(js, encoding="utf-8")
    out = subprocess.run(["node", str(f)], capture_output=True, text=True, check=True).stdout
    assert '"pos":"fixed"' in out and '"left":"120px"' in out and '"bottom":"92px"' in out
    assert '"hidden":false' in out and '"exp":"true"' in out
