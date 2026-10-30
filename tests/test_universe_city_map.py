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


BUDDHA = (ROOT / "static" / "landmark_buddha.js").read_text(encoding="utf-8")


def test_ang_thong_great_buddha_landmark():
    """พระพุทธรูปองค์ใหญ่ วัดม่วง อ่างทอง — พิกัดจริง ลาน 12 ม. + องค์พระปั้นด้วยโค้ด (ไม่มีไฟล์โมเดล ไม่มีรูปภาพ)"""
    import re
    m = re.search(r"lat: (\d+\.\d+), lon: (\d+\.\d+),", CITY)
    assert m, "ไม่พบ LANDMARKS"
    assert abs(float(m.group(1)) - 14.5932) < 1e-3 and abs(float(m.group(2)) - 100.3778) < 1e-3
    assert "facing: 90, base: 12," in CITY
    parts = re.findall(r"\['([er])', ([\d.]+), ([\d.]+), (-?[\d.]+), (-?[\d.]+), ([\d.]+), ([\d.]+), '(\w+)'\]", CITY)
    stone = [p for p in parts if p[7] == "stone"]
    assert stone and float(stone[0][6]) == 12                                # ลานสูงเท่าฐานองค์พระ ไม่ลอย ไม่จม
    assert all(float(p[5]) < float(p[6]) for p in parts)
    assert "map.addLayer(window.KD_buddhaLayer(lib, m), 'water-name')" in CITY  # ใต้ชั้นชื่อ
    assert "map.on('style.load', addModels)" in CITY                         # สลับกลางวัน/คืนแล้วองค์พระยังอยู่
    assert '<script src="/static/landmark_buddha.js" defer></script>' in PAGE
    assert "id: 'landmark-name'" in CITY and "'text-allow-overlap': true" in CITY


def test_buddha_model_is_sculpted_in_code_and_light_on_phones():
    """ผิวโค้งจาก signed distance + surface nets — สร้างใน worker ครั้งเดียว ใช้ซ้ำตอนสลับโหมด"""
    for part in ("หน้าตัก", "พระหัตถ์ขวาคว่ำบนเข่า", "นิ้วพระหัตถ์ชี้ลงแตะธรณี", "พระหัตถ์ซ้ายหงายบนตัก", "ผ้าสังฆาฏิ",
                 "พระเศียร", "พระกรรณ", "พระนาสิก", "คิ้วโก่ง เปลือกตาหลุบต่ำ ริมฝีปาก", "พระเกตุมาลา", "พระรัศมีเปลว ปลายแหลม"):
        assert part in BUDDHA, part
    assert "function smin(" in BUDDHA and "surface nets" in BUDDHA
    assert "cap(x, y, z, 0, 69, -5, 0, 80, -5," in BUDDHA                    # ยอดพระรัศมี 80 ม. เหนือลาน 12 ม. = ~92 ม.
    assert "ell(x, y, z, 0, 7, -1, 31," in BUDDHA                            # หน้าตักกว้าง ~62–63 ม.
    assert "new Worker(SRC)" in BUDDHA and "self.postMessage(m, [m.pos.buffer" in BUDDHA
    assert "wk.postMessage(.5);" in BUDDHA                                   # ตารางละเอียด 0.5 ม. ใน worker — ผิวคม
    assert "done(build(.8))" in BUDDHA                                       # worker ใช้ไม่ได้ก็ยังมีองค์พระ (หยาบลง ไม่ค้าง)
    assert "if (meshCache) return cb(meshCache);" in BUDDHA
    assert "if (z < 13 || !mesh) return;" in BUDDHA                          # ไกลๆ ไม่วาด
    # เมทริกซ์รวมคิดด้วย float64 ก่อนส่งการ์ดจอ · ใช้พิกัดเมอร์เคเตอร์ 0–1 ของ MapLibre 5
    assert "args.defaultProjectionData.mainMatrix" in BUDDHA and "meterInMercatorCoordinateUnits()" in BUDDHA
    assert "queryTerrainElevation" in BUDDHA                                 # วางบนพื้นจริงเมื่อมีภูเขา 3 มิติ
    assert "uniform float day" in BUDDHA and "kd-day" in BUDDHA


def test_day_and_night_modes():
    """กลางคืนอย่างเดียวน่าเบื่อ — มีปุ่มกลางวัน ใช้ทั้งโลกและแผนที่เมือง จำไว้ในเครื่อง"""
    assert 'id="ec-day"' in PAGE and "function KD_toggleDay()" in PAGE
    assert "localStorage.getItem('kd-day')==='1'" in PAGE                  # ตั้งก่อนวาด ไม่กระพริบ
    assert "localStorage.setItem('kd-day',on?'1':'0')" in PAGE and "new Event('kd-theme')" in PAGE
    assert "var C = isDay() ? DAY : NIGHT" in CITY
    for key in ("bg:", "water:", "park:", "bld:", "halo:", "gold:", "stone:"):
        assert CITY.count(key) >= 2, key                                   # ทั้งสองชุดสีมีครบ
    assert "window.addEventListener('kd-theme'" in CITY and "map.setStyle(style())" in CITY
    assert "uniform1f(U.dayM, dayM)" in EARTH and "surf=mix(surf,dc,dayM)" in EARTH
    assert "window.addEventListener('kd-theme'" in EARTH
    assert "html.kd-day #city-map{background:#ece6da}" in PAGE


def test_round4_feedback_day_mode_on_real_phone():
    """ภาพจริงรอบ 4 (โหมดกลางวัน): เส้นจุดพาดลูกโลกที่เส้นแบ่งวัน · แดดสะท้อนทะเลเป็นเม็ด
    · ลานขึ้นก่อนองค์พระ · ไม่เห็นป้ายยอดเขาตอนดูทั้งจังหวัด"""
    # รอยต่อ 180°: มีพิกัดชุดที่สองที่รอยต่ออยู่ที่ 0° แล้วเลือกชุดที่เปลี่ยนช้ากว่า (ต้องเปิด OES_standard_derivatives)
    assert "float tx2=fract(tc.x+.5)-.5;" in EARTH and "if(fwidth(tx2)<fwidth(tc.x))tc.x=tx2;" in EARTH
    assert "gl.getExtension('OES_standard_derivatives')" in EARTH
    assert "'#extension GL_OES_standard_derivatives : enable\\n#define DERIV 1\\n'" in EARTH
    # แดดกลางวันใช้ผิวน้ำเรียบ ไม่ใช้คลื่นของกลางคืน
    assert "float sg=pow(max(dot(reflect(rd,nl)," in EARTH and "glint*wm*.6" not in EARTH
    # ป้ายยอดเขาขึ้นตั้งแต่ซูม 8 ยอดสำคัญได้ที่ก่อน
    assert "id: 'peak-name', type: 'symbol', source: 'omt', 'source-layer': 'mountain_peak', minzoom: 8," in CITY
    assert "'symbol-sort-key': ['coalesce', ['get', 'rank'], 99]" in CITY
    # องค์พระเริ่มสร้างตั้งแต่ซูม 10 เมื่ออยู่ใกล้ แสดงที่ซูม 13
    assert "if (!asked && z >= 10 && Math.abs(c.lat - at.lat) < .45 && Math.abs(c.lng - at.lon) < .45)" in BUDDHA
    assert "if (z < 13 || !mesh) return;" in BUDDHA
