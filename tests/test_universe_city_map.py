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
    assert "connect-src 'self' https://tiles.openfreemap.org https://s3.amazonaws.com;" in csp
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
    assert "failed = true; exit();" in CITY and "15000" in CITY            # ไม่มีไทล์เมืองมาเลย 15 วินาที → กลับไปโลก
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


def test_round2_feedback_from_real_phone():
    """ปรับตามภาพจริงจากมือถือของเจ้าของโปรเจกต์"""
    # ตึกเตี้ยเคยมืดจนกลืนพื้น — ตอนนี้ฐานสีอุ่นขึ้น ยอดสว่างกว่าฐาน
    assert "0, '#3b2d24'" in CITY and "'fill-extrusion-vertical-gradient': true" in CITY
    # ในไทยชื่อไทยตาม OSM · ที่อื่นชื่อไทยถ้ามี ไม่มีก็อังกฤษ
    assert "var NAME_TH = ['coalesce', ['get', 'name:th'], ['get', 'name']" in CITY
    assert "var NAME_WORLD = ['coalesce', ['get', 'name:th'], ['get', 'name:en']" in CITY
    assert "map.on('moveend', syncNames)" in CITY and "TH_BOX" in CITY
    # ซอยจางเมื่อมองไกล
    assert "['interpolate', ['linear'], ['zoom'], 11, 0, 13, .18, 15, .45, 17, .65]" in CITY
    # เมืองเล็กขึ้นเมื่อซูมใกล้เท่านั้น
    assert "id: 'place-town'" in CITY and "minzoom: 9.5" in CITY and "'text-padding': 14" in CITY
    # เข็มทิศของโลกซ่อนเมื่ออยู่ในแผนที่ · มีเข็มทิศของแผนที่แทน
    assert "classList.toggle('kd-city', v)" in CITY and "html.kd-city .hud,html.kd-city .hud-deg{display:none}" in PAGE
    assert "NavigationControl({ showZoom: false, visualizePitch: true })" in CITY


def test_terrain_is_free_open_data_and_optional_on_weak_phones():
    assert "elevation-tiles-prod/terrarium" in CITY and "encoding: 'terrarium'" in CITY
    assert "registry.opendata.aws/terrain-tiles" in CITY                    # เครดิตแหล่งข้อมูล
    assert "type: 'hillshade'" in CITY and "source: 'demhs'" in CITY       # เงาภูเขาใช้แหล่งแยกจาก terrain
    assert "if (!lightDevice) st.terrain" in CITY                          # เครื่องแรมน้อย: เงาอย่างเดียว ไม่ยกพื้น


def test_round3_feedback_from_real_phone():
    """ภาพจริงรอบ 3: เขาสามมุขไม่มีป้าย · รูดำสี่เหลี่ยม · หลังคาส้มจ้า · เครดิตเปิดค้างบังแผนที่ · เน็ตช้าโดนเด้งกลับโลก"""
    assert "'source-layer': 'mountain_peak'" in CITY and "id: 'peak-name'" in CITY
    assert "['to-string', ['get', 'ele']], ' ม.'" in CITY                  # ชื่อเขา + ความสูง
    assert "map.setLayoutProperty('peak-name', 'text-field', peakText(name))" in CITY
    assert "exaggeration: 1.5" in CITY                                     # เขาเตี้ยริมทะเลยังเห็นเป็นเนิน
    assert "encoding: 'terrarium', tileSize: 256, maxzoom: 12" in CITY     # ไทล์ภูเขาน้อยลง โหลดทัน
    assert "350, '#ffe9bf'" not in CITY                                    # หลังคาไม่ส้มจ้าแล้ว
    assert "a.classList.remove('maplibregl-compact-show')" in CITY
    # มีไทล์เมืองมาแผ่นเดียวก็ถือว่าเน็ตใช้ได้ — ไม่ต้องรอภูเขาโหลดครบ
    assert "map.on('sourcedata', function (e) { if (e.sourceId === 'omt' && e.tile) loaded = true; });" in CITY


def test_ang_thong_great_buddha_landmark():
    """พระพุทธรูปองค์ใหญ่ วัดม่วง อ่างทอง — พิกัดจริง ทรงซ้อนชั้นสูงขึ้นเรื่อยๆ ยอดราว 92 ม."""
    import re
    m = re.search(r"lat: (\d+\.\d+), lon: (\d+\.\d+),\s*tiers: (\[\[.*?\]\]) }", CITY, re.S)
    assert m, "ไม่พบ LANDMARKS"
    lat, lon = float(m.group(1)), float(m.group(2))
    assert abs(lat - 14.5932) < 1e-3 and abs(lon - 100.3778) < 1e-3      # อ.วิเศษชัยชาญ จ.อ่างทอง
    tiers = [[int(x) for x in t.split(",")] for t in re.findall(r"\[(\d+, \d+, \d+, \d+)\]", m.group(3))]
    assert tiers[-1][3] == 92 and tiers[0][2] == 0
    for a, b in zip(tiers, tiers[1:]):
        assert a[3] == b[2] and b[0] <= a[0]                               # ชั้นต่อกันพอดี ยิ่งสูงยิ่งแคบ
    assert "id: 'landmark', type: 'fill-extrusion', source: 'lmshape'" in CITY
    assert "id: 'landmark-name'" in CITY and "'text-allow-overlap': true" in CITY


def test_day_and_night_modes():
    """กลางคืนอย่างเดียวน่าเบื่อ — มีปุ่มกลางวัน ใช้ทั้งโลกและแผนที่เมือง จำไว้ในเครื่อง"""
    assert 'id="ec-day"' in PAGE and "function KD_toggleDay()" in PAGE
    assert "localStorage.getItem('kd-day')==='1'" in PAGE                  # ตั้งก่อนวาด ไม่กระพริบ
    assert "localStorage.setItem('kd-day',on?'1':'0')" in PAGE and "new Event('kd-theme')" in PAGE
    assert "var C = isDay() ? DAY : NIGHT" in CITY
    for key in ("bg:", "water:", "park:", "bld:", "halo:", "gold:"):
        assert CITY.count(key) >= 2, key                                   # ทั้งสองชุดสีมีครบ
    assert "window.addEventListener('kd-theme'" in CITY and "map.setStyle(style())" in CITY
    assert "uniform1f(U.dayM, dayM)" in EARTH and "surf=mix(surf,dc,dayM)" in EARTH
    assert "window.addEventListener('kd-theme'" in EARTH
    assert "html.kd-day #city-map{background:#ece6da}" in PAGE
