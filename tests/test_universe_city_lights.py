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


def test_lights_come_from_black_marble_2016_in_three_sizes():
    """ไฟเมืองใช้ NASA Black Marble 2016 ทั้ง 2K · 4K · 8K และ 8K โหลดเฉพาะเครื่องที่รองรับ"""
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    for name, w in (("lights.jpg", 2048), ("lights_4k.jpg", 4096), ("lights_8k.jpg", 8192)):
        im = Image.open(Path("static/earth") / name)
        assert im.size == (w, w // 2) and im.mode == "L"
    js = Path("static/cockpit_earth.js").read_text(encoding="utf-8")
    assert "can8k" in js and "lights_8k.jpg" in js
    assert "BlackMarble_2016" in Path("scripts/build_earth_lights_2016.py").read_text(encoding="utf-8")


def test_city_glow_under_clouds_and_red_airglow():
    """เมืองใต้เมฆยังเรืองแสงผ่านเมฆ · ขอบโลกกลางคืนมี airglow สองชั้น (เขียว ~94 กม. · แดงสูงกว่า) แบบภาพจาก ISS"""
    js = Path("static/cockpit_earth.js").read_text(encoding="utf-8")
    assert "smoothstep(.15,.7,cl)" in js                  # แสงเมืองกระเจิงในเมฆ
    assert "vec3(.20,.85,.42)" in js and "vec3(.80,.16,.22)" in js   # เขียว + แดง
