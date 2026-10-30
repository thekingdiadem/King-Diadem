"""ซูมลงลึกบนหน้า Universe → แผนที่เมืองกลางคืน 3 มิติจาก OpenStreetMap (OpenFreeMap — ฟรี ใช้เชิงพาณิชย์ได้)"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CITY = (ROOT / "static" / "city_map.js").read_text(encoding="utf-8")
EARTH = (ROOT / "static" / "cockpit_earth.js").read_text(encoding="utf-8")
PAGE = (ROOT / "static" / "king_diadem_universe.html").read_text(encoding="utf-8")
VENDOR = ROOT / "static" / "vendor" / "maplibre-gl-5.24.0"


def test_maplibre_is_self_hosted_csp_build_with_license():
    for f in ("maplibre-gl-csp.js", "maplibre-gl-csp-worker.js", "maplibre-gl.css", "LICENSE.txt"):
        assert (VENDOR / f).exists(), f
    js = (VENDOR / "maplibre-gl-csp.js").read_text(encoding="utf-8")
    assert "eval(" not in js and "new Function" not in js                # CSP ไม่ต้องเปิด unsafe-eval
    assert "setWorkerUrl(BASE + 'maplibre-gl-csp-worker.js')" in CITY       # worker จากเว็บเราเอง (worker-src 'self')


def test_csp_allows_only_openfreemap_for_tiles(client):
    csp = client.get("/").headers["content-security-policy"]
    assert "connect-src 'self' https://tiles.openfreemap.org;" in csp
    assert "script-src 'self' 'unsafe-inline';" in csp                      # ไม่มีสคริปต์จากที่อื่นเพิ่ม
    assert "worker-src 'self'" in csp


def test_map_library_loads_only_when_zooming_deep():
    assert '<script src="/static/city_map.js" defer>' in PAGE and "maplibre-gl-csp.js" not in PAGE
    assert "S.tL > LMAX - 1 && window.KD_cityMap" in EARTH                 # ใกล้ถึงระดับเมืองค่อยโหลด


def test_handoff_both_ways_at_same_place():
    assert "function toCity()" in EARTH and "78271.517" in EARTH           # ระยะกล้องโลก → ระดับซูมแผนที่
    assert "if (L > LMAX + .02 && toCity()) return;" in EARTH
    assert "fromCity: function (c)" in EARTH and "S.city" in EARTH
    assert "map.getZoom() < exitZ" in CITY and "KD_earth.fromCity" in CITY  # ซูมออกพ้นจุดที่เข้า = กลับมาเป็นโลก


def test_falls_back_to_globe_when_map_cannot_run():
    assert "getContext('webgl2')" in CITY                                  # MapLibre 5 ต้องใช้ WebGL2
    assert "failed = true; exit();" in CITY and "12000" in CITY            # โหลดไม่ขึ้น 12 วินาที → กลับไปโลก
    assert "s.onerror" in CITY


def test_night_style_and_attribution():
    assert "https://tiles.openfreemap.org" in CITY and "© OpenStreetMap contributors" in CITY
    assert "'fill-extrusion'" in CITY and "render_height" in CITY          # ตึก 3 มิติตามความสูงจริง
    assert "road-glow" in CITY and "'line-blur'" in CITY                    # ถนนเรืองแสง
    assert "['get', 'name:en']" in CITY


def test_map_canvas_not_caught_by_globe_css():
    """กฎ .cockpit canvas (touch-action:pan-y, opacity 0) เคยจะไปโดน canvas ของแผนที่ด้วย — จำกัดเฉพาะลูกตรง"""
    assert ".cockpit>canvas{pointer-events:auto;touch-action:pan-y" in PAGE
    assert ".cockpit canvas{" not in PAGE and '<div id="city-map"' in PAGE
