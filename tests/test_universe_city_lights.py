"""ไฟเมืองบนลูกโลกหน้า Universe ต้องไม่ถูกแถบมืดกลบจนดูหม่น"""
import re
from pathlib import Path


def test_city_light_gain_not_dimmed():
    js = Path("static/cockpit_earth.js").read_text(encoding="utf-8")
    gain = float(re.search(r"vec3 city=vec3\(1\.,\.48,\.10\)\*pow\(L,[\d.]+\)\*([\d.]+)", js).group(1))
    assert gain >= 3.0


def test_overlay_does_not_bury_the_globe():
    html = Path("static/king_diadem_universe.html").read_text(encoding="utf-8")
    rule = re.findall(r"\.galaxy-overlay\{background:[^}]*\}", html)[-1]
    alphas = [float(a) for a in re.findall(r"rgba\(\d+,\d+,\d+,\s*([\d.]+)\)", rule)]
    assert max(alphas) <= 0.45
