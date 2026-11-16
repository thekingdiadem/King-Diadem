"""ไฟเมืองบนลูกโลกหน้า Universe ต้องไม่ถูกแถบมืดกลบจนดูหม่น"""
import re
from pathlib import Path


def test_city_light_gain_not_dimmed():
    js = Path("static/cockpit_earth.js").read_text(encoding="utf-8")
    gain = float(re.search(r"vec3 city=mix\(sodium,core,[^)]*\)\)\*pow\(L,[\d.]+\)\*([\d.]+)", js).group(1))
    assert gain >= 3.0


def test_city_colour_follows_real_night_photos():
    """ชานเมืองส้ม (โซเดียม) · ใจกลางขาวอุ่น · จุดสว่างจัดขาวอมฟ้า (LED) และมีแสงฟุ้งวงกว้าง"""
    js = Path("static/cockpit_earth.js").read_text(encoding="utf-8")
    assert "vec3 sodium=" in js and "led=" in js and "float W=" in js


def test_overlay_does_not_bury_the_globe():
    html = Path("static/king_diadem_universe.html").read_text(encoding="utf-8")
    rule = re.findall(r"\.galaxy-overlay\{background:[^}]*\}", html)[-1]
    alphas = [float(a) for a in re.findall(r"rgba\(\d+,\d+,\d+,\s*([\d.]+)\)", rule)]
    assert max(alphas) <= 0.45
