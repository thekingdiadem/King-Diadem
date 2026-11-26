"""แผนที่เมืองบนมือถือ — ไม่เปิดภูเขา 3 มิติ ไม่วาดเต็มความละเอียดจอ 3 เท่า ไม่เอียงจนเห็นไทล์ถึงขอบฟ้า"""
from pathlib import Path

CITY = Path("static/city_map.js").read_text(encoding="utf-8")


def test_phone_counts_as_light_device_so_no_3d_terrain():
    assert "var phone = Math.min(screen.width" in CITY
    assert "var lightDevice = phone ||" in CITY and "if (!lightDevice) st.terrain" in CITY


def test_map_pixel_ratio_capped():
    assert "var MAP_DPR = Math.min(window.devicePixelRatio || 1, phone ? 1.5 : 2)" in CITY
    assert "pixelRatio: MAP_DPR" in CITY


def test_phone_dive_pitch_lower():
    assert "pitch: Math.min(phone ? 45 : 60, at.pitch + 8)" in CITY
