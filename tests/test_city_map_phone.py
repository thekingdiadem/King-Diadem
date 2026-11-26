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


def test_phone_hands_over_to_city_map_before_globe_blurs():
    earth = Path("static/cockpit_earth.js").read_text(encoding="utf-8")
    assert "LMAX = Math.min(screen.width || 1e4, screen.height || 1e4) < 700 ? 3.6 : 4.4" in earth


def test_nasa_layer_fills_gaps_under_sentinel_until_city_zoom():
    i = CITY.index("{ id: 'sat'"); j = CITY.index("{ id: 's2'")
    assert i < j                                   # อยู่ใต้ Sentinel
    assert "maxzoom: 14.2" in CITY[i:j]
