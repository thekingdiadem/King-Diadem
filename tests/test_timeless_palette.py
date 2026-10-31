"""เฉดสีชุดเดียวของทั้งแอป (TIMELESS) — อ่านง่ายสำหรับผู้สูงอายุ

เจ้าของโปรเจกต์อยากให้ "ทุกสีรวมกันเป็นหนึ่งสไตล์ที่ไม่มีวันตกยุค" และ "คนแก่ใช้ได้"
เทสต์นี้กันไม่ให้ใครเผลอทำตัวหนังสือจางลงจนอ่านยาก: ทุกระดับต้องคมกว่าพื้น ≥ 7:1 (WCAG AAA)
"""
import re
from pathlib import Path
from tests._front import front_page  # noqa: E402

SRC = front_page()
BLOCK = SRC[SRC.index("TIMELESS · เฉดสีชุดเดียว"):SRC.index("ดาวลูกไก่ใกล้ๆ (static/pleiades_view.js)")]


def _lum(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]


def _cr(a, b):
    a, b = sorted([_lum(a), _lum(b)], reverse=True)
    return (a + .05) / (b + .05)


def _var(scope, name):
    m = re.search(r"--" + name + r":(#[0-9a-fA-F]{6})", scope)
    assert m, name
    return m.group(1)


def test_palette_layer_is_last_word_on_colour():
    assert BLOCK.count(":root{") == 1
    assert SRC.index("TIMELESS · เฉดสีชุดเดียว") > SRC.rindex("--dusk:linear-gradient")


def test_dark_text_is_aaa_on_midnight():
    root = BLOCK[BLOCK.index(":root{"):]
    bg = _var(root, "bg")
    for name in ("ink", "ink-2", "ink-3", "gold", "gold-hi", "bad", "ok", "vega"):
        assert _cr(_var(root, name), bg) >= 7, name


def test_light_themes_text_is_aaa():
    light = BLOCK[BLOCK.index('html[data-ink="dark"] body:not([data-view="universe"]){'):]
    for paper in ("#eef4ff", "#fff8e7"):              # กลางวัน · คอสมิกลาเต้
        for name in ("ink", "ink-2", "ink-3", "gold-hi"):
            assert _cr(_var(light, name), paper) >= 7, (name, paper)


def test_primary_button_text_is_readable():
    assert _cr("#1c1810", "#d8b878") >= 7


def test_toast_stays_readable_on_light_themes():
    """แจ้งเตือนลอยต้องเป็นพื้นมืด + ตัวสว่างตายตัว ไม่ตาม --ink (ซึ่งเป็นสีเข้มในโหมดสว่าง)"""
    m = re.search(r"#toast\{background:rgba\((\d+),(\d+),(\d+),[.\d]+\);color:(#[0-9a-f]{6})\}", BLOCK)
    assert m
    bg = "#%02x%02x%02x" % tuple(int(m.group(i)) for i in (1, 2, 3))
    assert _cr(m.group(4), bg) >= 7
