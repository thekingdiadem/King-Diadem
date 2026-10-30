"""โหมดสีหน้าแรก: กลางคืน · กลางวัน · คอสมิกลาเต้ · สีที่ผู้ใช้เลือกเอง (จำไว้ในเครื่อง)"""
import re
from pathlib import Path

PAGE = (Path(__file__).resolve().parent.parent / "static" / "index.html").read_text(encoding="utf-8")


def test_mode_is_applied_before_first_paint():
    head = PAGE[:PAGE.index("</head>")]
    assert "window.KD_themeVars = function(t, c){" in head                      # ตั้งก่อนวาด ไม่กะพริบ
    assert "var P = { day: '#eef4ff', latte: '#fff8e7' }" in head               # คอสมิกลาเต้ = #FFF8E7
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
    assert picks == ["night", "day", "latte", "custom"]
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
