"""ความสบายตา: คนไวต่อแสง · คนตาบอดสี · คนเวียนหัวง่าย (เจ้าของโปรเจกต์ขอให้ใส่ใจทุกกลุ่ม)"""
import math
import re
from pathlib import Path
from tests._front import front_page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HTML = front_page()
BB = (ROOT / "static" / "big_bang.js").read_text(encoding="utf-8")
GL = (ROOT / "static" / "big_bang_gl.js").read_text(encoding="utf-8")

# Machado et al. 2009 (ความรุนแรงเต็ม) — จำลองการมองของคนตาบอดสีแดง/เขียว/น้ำเงิน
_M = {"protan": [[.152286, 1.052583, -.204868], [.114503, .786281, .099216], [-.003882, -.048116, 1.051998]],
      "deutan": [[.367322, .860646, -.227968], [.280085, .672501, .047413], [-.011820, .042940, .968881]],
      "tritan": [[1.255528, -.076749, -.178779], [-.078411, .930809, .147602], [.004733, .691367, .303900]]}


def _lab(hexc, kind=None):
    v = [int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    v = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in v]
    if kind:
        v = [max(0, min(1, sum(_M[kind][i][j] * v[j] for j in range(3)))) for i in range(3)]
    X = .4124 * v[0] + .3576 * v[1] + .1805 * v[2]; Y = .2126 * v[0] + .7152 * v[1] + .0722 * v[2]
    Z = .0193 * v[0] + .1192 * v[1] + .9505 * v[2]
    f = lambda t: t ** (1 / 3) if t > .008856 else 7.787 * t + 16 / 116
    return 116 * f(Y) - 16, 500 * (f(X / .9505) - f(Y)), 200 * (f(Y) - f(Z / 1.089))


def test_risk_colours_stay_apart_for_colour_blind_eyes():
    hi = re.search(r"var RISK_HI = '(#[0-9a-f]{6})';", HTML).group(1)
    body = re.search(r"function riskColor\(r\)\{[^}]+\}", HTML).group(0)
    lo, mid = re.findall(r"'(#[0-9a-f]{6})'", body)[-2:][::-1]
    for kind in (None, "protan", "deutan", "tritan"):
        for other in (lo, mid):
            assert math.dist(_lab(hi, kind), _lab(other, kind)) > 35, (kind, other)
    assert "sw ring" in HTML                                                     # คำอธิบายสีมีวงล้อมเหมือนดาว


def test_in_app_reduce_motion_switch():
    assert 'id="calm-btn" aria-pressed="false"' in HTML
    assert "localStorage.getItem('kd-calm') === '1'" in HTML and "lsSet('kd-calm', on ? '1' : '0')" in HTML
    assert "html.kd-calm *,html.kd-calm *::before,html.kd-calm *::after{animation-duration:.001ms!important" in HTML
    # ค่าเดียวกับหน้า Universe และฉากบิ๊กแบง
    assert "classList.contains('kd-calm')" in BB


def test_big_bang_flashes_are_soft():
    """แสงวาบตอนระเบิดและตอนชนค่อยๆ สว่างขึ้น และไม่ขาวเต็มจอ"""
    assert "smoothstep(0.,.25,t)" in GL and "*.85;" in GL and "fl*fl*.22" in GL
    assert "rs(0.,.18,t-ti)" in GL and "exp(-(t-ti)*2.5)*1.4" not in GL
    assert "Math.min(1, t / .25) * .6" in BB and "* e * .35" in BB
