"""โหมดสีหน้าแรก: กลางคืน · กลางวัน · คอสมิกลาเต้ · สีที่ผู้ใช้เลือกเอง (จำไว้ในเครื่อง)"""
import re
from pathlib import Path
from tests._front import front_page  # noqa: E402

PAGE = front_page()


def test_mode_is_applied_before_first_paint():
    head = PAGE[:PAGE.index("</head>")]
    assert "window.KD_themeVars = function(t, c){" in head                      # ตั้งก่อนวาด ไม่กะพริบ
    assert "var P = { day: '#eef4ff', latte: '#fff8e7', pastel: '#1c1a2e' }" in head   # คอสมิกลาเต้ = #FFF8E7 · พาสเทลมืด = ม่วงครามเข้ม
    assert "localStorage.getItem('kd-theme')" in head and "localStorage.getItem('kd-theme-color')" in head
    assert "/^#[0-9a-f]{6}$/i.test(p)" in head                                  # สีจาก localStorage ต้องเป็น #rrggbb เท่านั้น


def test_ink_follows_background_brightness():
    # สีอ่อน → ตัวหนังสือเข้ม · สีเข้มที่เลือกเอง → ตัวหนังสือสว่างแบบเดิม
    assert "ink: .2126 * r + .7152 * g + .0722 * b > .45 ? 'dark' : 'light'" in PAGE
    assert 'html[data-ink="dark"] body:not([data-view="universe"]){' in PAGE      # หน้าจักรวาลยังเป็นอวกาศมืด
    for sel in (".bubble{color:var(--ink)}", ":is(.inp,.out,.drop)", "#view-title{color:var(--ink-2)"):
        assert sel in PAGE, sel


def test_picker_has_four_modes_and_custom_color():
    picks = re.findall(r'data-theme-pick="(\w+)"', PAGE)
    assert picks == ["night", "day", "latte", "pastel", "custom"]
    assert '<input type="color" id="theme-color"' in PAGE
    assert "$('#theme-color').addEventListener('input', function(){ applyTheme('custom', this.value); });" in PAGE
    assert "localStorage.setItem('kd-theme', THEME.t); localStorage.setItem('kd-theme-color', THEME.c);" in PAGE


def test_space_scene_turns_into_paper():
    assert "uniform vec3 uPaper;uniform float uLight;" in PAGE
    assert "' vec3 bg=mix(vec3(.006,.008,.016),uPaper,uLight);'" in PAGE
    assert "' stars*=(1.-uLight)*.6;'," in PAGE and "' nm*=1.-uLight;'," in PAGE   # พื้นสว่างไม่มีดาว/ฝุ่น
    assert "gl.uniform1f(u.uLight, tv ? 1 : 0);" in PAGE
    assert "window.KD_kick = kick;" in PAGE                                      # เปลี่ยนโหมดแล้ววาดใหม่ทันที
    assert "THEME.dark ? '#3d3558' : '#eef1f8'" in PAGE                         # ป้ายดาวเคราะห์อ่านได้บนพื้นสว่าง


def test_dark_pastel_theme_keeps_text_sharp():
    """พาสเทลมืด: เปลี่ยนเฉพาะสีเน้นและพื้น ตัวอักษรงาช้างชุดเดิมต้องคมกว่าพื้นเกิน 7:1 (เกณฑ์เดียวกับ TIMELESS)"""
    def lum(h):
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
        return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]
    def cr(a, b):
        a, b = sorted([lum(a), lum(b)], reverse=True)
        return (a + .05) / (b + .05)
    assert 'html[data-theme="pastel"]{' in PAGE
    assert "--ink-2:#cfc9de; --ink-3:#b8b2c8;" in PAGE         # ตัวอักษรรองของชุดเดิม (#a39d92) ได้แค่ 6.3:1 บนพื้นนี้
    for ink in ("#f1ede4", "#cfc9de", "#b8b2c8", "#cdbdf2", "#e4daff", "#a8dcc4"):
        assert cr(ink, "#1c1a2e") >= 7, ink
    assert cr("#1f1a33", "#c9b6f0") >= 7                      # ตัวอักษรบนปุ่มหลักสีลาเวนเดอร์
