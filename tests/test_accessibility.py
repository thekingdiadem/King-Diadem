"""การเข้าถึง (accessibility) ของหน้าเว็บ — พบจากการตรวจทุกหน้าด้วย axe-core

- แถบเลื่อน 4 อันในหน้า Universe มีป้ายชื่อแต่ไม่ได้ผูกกับช่อง (ไม่มี for=) โปรแกรมอ่านหน้าจอเลยอ่านว่า "slider" เฉยๆ
- หลายหน้าไม่มี <main> และไม่มี <h1> คนที่ใช้โปรแกรมอ่านหน้าจอกระโดดไปเนื้อหาหลัก/หัวเรื่องไม่ได้
- ตัวอักษรเล็กบางจุดจางเกิน (contrast ~1.3–3.1) อ่านยากบนจอมือถือกลางแดด — เกณฑ์ WCAG AA คือ 4.5:1
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _page(name):
    return (ROOT / "static" / name).read_text(encoding="utf-8")


def _rule(html, selector):
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", html)
    assert m, selector
    return m.group(1)


def _contrast(rgba, bg):
    def lum(c):
        def f(v):
            v /= 255
            return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
        return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])
    *fg, a = rgba
    mixed = [fg[i] * a + bg[i] * (1 - a) for i in range(3)]
    hi, lo = sorted((lum(mixed), lum(bg)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def _rgba(text):
    h = re.fullmatch(r"#([0-9a-fA-F]{6})", text.strip())
    if h:                                    # สีทึบ (ชุดสี TIMELESS ใช้ hex แทน rgba จาง)
        v = h.group(1)
        return float(int(v[0:2], 16)), float(int(v[2:4], 16)), float(int(v[4:6], 16)), 1.0
    r, g, b, a = re.search(r"rgba\(([\d.]+),\s*([\d.]+),\s*([\d.]+),\s*([\d.]+)\)", text).groups()
    return float(r), float(g), float(b), float(a)


@pytest.mark.parametrize("name", ["ask.html", "guide.html", "login.html", "register.html",
                                  "report.html", "wallet.html", "king_diadem_universe.html"])
def test_page_has_one_main_landmark(name):
    html = _page(name)
    assert html.count("<main") == 1 and html.count("</main>") == 1, name


@pytest.mark.parametrize("name", ["ask.html", "guide.html", "login.html", "register.html",
                                  "report.html", "wallet.html", "king_diadem_universe.html"])
def test_page_has_a_level_one_heading(name):
    assert re.search(r"<h1[ >]", _page(name)), name


def test_universe_sliders_are_labelled():
    html = _page("king_diadem_universe.html")
    for sid in re.findall(r'<input type="range" id="([^"]+)"', html):
        assert f'<label for="{sid}"' in html, sid


def test_decorative_galaxy_is_hidden_from_screen_readers():
    html = _page("king_diadem_universe.html")
    assert '<div id="galaxy-wrap" aria-hidden="true">' in html


UNI_BG = (8, 13, 26)       # #080d1a
REPORT_BG = (6, 7, 19)     # #060713
ARCH_BG = (2, 3, 9)        # #020309


@pytest.mark.parametrize("selector", [".wl-label", ".wl-val", ".ego-tap", ".footer-text", ".footer-axiom"])
def test_universe_small_text_meets_aa_contrast(selector):
    assert _contrast(_rgba(_rule(_page("king_diadem_universe.html"), selector)), UNI_BG) >= 4.5


def test_report_and_architecture_small_text_use_readable_tone():
    report = _page("report.html")
    mid = _rgba(re.search(r"--tx-mid:\s*(rgba\([^)]*\)|#[0-9a-fA-F]{6})", report).group(1))
    assert _contrast(mid, REPORT_BG) >= 4.5
    assert "var(--tx-mid)" in _rule(report, ".aud-label")
    assert "var(--tx-mid)" in _rule(report, ".report-footer")

    arch = _page("architecture.html")
    mid = _rgba(re.search(r"--tx-mid:\s*(rgba\([^)]*\)|#[0-9a-fA-F]{6})", arch).group(1))
    assert _contrast(mid, ARCH_BG) >= 4.5
    assert "var(--tx-mid)" in _rule(arch, ".foot")
