/* แผนที่เมืองกลางคืน 3 มิติ — ต่อจากโลกใน cockpit_earth.js เมื่อซูมลงลึกกว่าที่ภาพ NASA ยังคม
 *
 * · ข้อมูล OpenStreetMap ผ่าน OpenFreeMap (ฟรี ไม่จำกัด ไม่ต้องมีคีย์ ใช้เชิงพาณิชย์ได้ · ต้องขึ้นเครดิต OSM)
 * · วาดด้วย MapLibre GL 5.24.0 (BSD-3) เก็บไว้ใน static/vendor/ — รุ่น CSP ไม่ใช้ eval ไม่ต้องเปิด CSP ให้สคริปต์ภายนอก
 * · โหลดเฉพาะตอนซูมใกล้จะถึง (ราว 450 KB บีบอัด) — คนที่ไม่ซูมลงไปไม่ต้องโหลดเลย
 * · โทนกลางคืน: พื้นมืด ถนนเรืองส้มตามขนาดถนน ตึกยกสูงตามความสูงจริง มีแสงหน้าต่าง ยิ่งสูงยิ่งสว่าง ชื่อเมือง/ย่านจาก OSM
 * · ภูเขา 3 มิติ + เงาภูเขาแสงจันทร์จาก AWS Terrain Tiles (ข้อมูลเปิด ฟรี) — เครื่องแรมน้อยมีแค่เงา ไม่ยกพื้น
 * · ซูมออกพ้นระดับที่เข้ามา = กลับไปโลกทั้งใบที่จุดเดิม · ไม่มี WebGL2 หรือโหลดไม่ขึ้น = อยู่กับโลกต่อไปตามเดิม
 * · โหมดกลางวัน (ปุ่ม "กลางวัน" → html.kd-day จำไว้ในเครื่อง): พื้นสว่าง น้ำฟ้า สวนเขียว ตึกสีปูน — ข้อมูลชุดเดียวกัน
 * · ยอดเขามีชื่อ+ความสูงจาก OSM (เช่น เขาสามมุข) · สถานที่สำคัญที่ใส่เองอยู่ใน LANDMARKS
 */
(function () {
  var BASE = '/static/vendor/maplibre-gl-5.24.0/';
  var TILES = 'https://tiles.openfreemap.org';
  var box = document.getElementById('city-map');
  if (!box) return;
  var hasGL2 = !!document.createElement('canvas').getContext('webgl2');
  var lib = null, loading = false, failed = !hasGL2, map = null, on = false, entering = false, exitZ = 0, waiters = [];

  function calm() { return document.documentElement.classList.contains('kd-calm') ||
                    (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches); }

  function prefetch(cb) {
    if (cb) waiters.push(cb);
    if (lib || failed) { flush(); return; }
    if (loading) return;
    loading = true;
    var css = document.createElement('link');
    css.rel = 'stylesheet'; css.href = BASE + 'maplibre-gl.css';
    document.head.appendChild(css);
    var s = document.createElement('script');
    s.src = BASE + 'maplibre-gl-csp.js';
    s.onload = function () {
      lib = window.maplibregl;
      if (lib) lib.setWorkerUrl(BASE + 'maplibre-gl-csp-worker.js'); else failed = true;
      flush();
    };
    s.onerror = function () { failed = true; flush(); };
    document.head.appendChild(s);
  }
  function flush() { var w = waiters; waiters = []; w.forEach(function (f) { f(); }); }

  // ชื่อ: ในไทยใช้ชื่อในแผนที่ตรงๆ (OSM เก็บเป็นภาษาไทย) · นอกไทยใช้ชื่อไทยถ้ามี (โตเกียว ซีอาน) ไม่มีก็อังกฤษ/อักษรโรมัน
  // ภาพจริงจากมือถือ: ตัวอักษรไทยแสดงได้ดี — เดิมใช้อังกฤษก่อนเพราะกลัวสระ/วรรณยุกต์วางผิดที่
  var NAME_TH = ['coalesce', ['get', 'name:th'], ['get', 'name'], ['get', 'name:en']];
  var NAME_WORLD = ['coalesce', ['get', 'name:th'], ['get', 'name:en'], ['get', 'name_en'], ['get', 'name:latin'], ['get', 'name']];
  var TH_BOX = [97.3, 5.6, 105.7, 20.5];                                // กรอบประเทศไทยคร่าวๆ (lon/lat)
  var LABEL_LAYERS = ['water-name', 'road-name', 'place-small', 'place-town', 'place-city'];
  // ยอดเขา: ชื่อ + ความสูง (เมตร) ถ้า OSM มี — เดิมไม่มีชั้นนี้ เขาเตี้ยริมทะเลอย่างเขาสามมุขเลยไม่มีป้ายเลย
  function peakText(name) {
    return ['case', ['has', 'ele'], ['concat', name, '\n', ['to-string', ['get', 'ele']], ' ม.'], name];
  }

  // ── สถานที่สำคัญที่ใส่เอง: OSM มีแค่จุด/รั้ววัด ไม่มีรูปทรงองค์พระ — วาดเป็นทรงองค์พระแบบเรียบง่ายสีทอง ──────
  // พระพุทธมหานวมินทร์ศากยมุนีศรีวิเศษชัยชาญ วัดม่วง อ.วิเศษชัยชาญ จ.อ่างทอง — พระพุทธรูปองค์ใหญ่ที่สุดในไทย
  // พิกัด 14.5932, 100.3778 · สูงราว 92 ม. · หน้าตัก ~63 ม. (Wikipedia: Great Buddha of Thailand)
  // ชั้น = [กว้าง ม., ลึก ม., ฐาน ม., ยอด ม.] ซ้อนจากฐานบัวขึ้นไปถึงพระเกศ
  var LANDMARKS = [
    { name: 'หลวงพ่อใหญ่ วัดม่วง', sub: 'พระพุทธรูปองค์ใหญ่ที่สุดในไทย · สูง ~92 ม.', lat: 14.5932, lon: 100.3778,
      tiers: [[70, 50, 0, 12], [63, 42, 12, 32], [40, 28, 32, 62], [22, 20, 62, 78], [14, 14, 78, 86], [6, 6, 86, 92]] }
  ];
  function landmarkData() {
    var shapes = [], points = [];
    LANDMARKS.forEach(function (m) {
      var dy = 1 / 111320, dx = dy / Math.cos(m.lat * Math.PI / 180);
      m.tiers.forEach(function (t) {
        var w = t[0] / 2 * dx, d = t[1] / 2 * dy;
        shapes.push({ type: 'Feature', properties: { base: t[2], top: t[3] },
          geometry: { type: 'Polygon', coordinates: [[[m.lon - w, m.lat - d], [m.lon + w, m.lat - d], [m.lon + w, m.lat + d],
                                                       [m.lon - w, m.lat + d], [m.lon - w, m.lat - d]]] } });
      });
      points.push({ type: 'Feature', properties: { name: m.name, sub: m.sub },
                    geometry: { type: 'Point', coordinates: [m.lon, m.lat] } });
    });
    return { shapes: { type: 'FeatureCollection', features: shapes }, points: { type: 'FeatureCollection', features: points } };
  }

  // ── สีสองชุด: กลางคืน (เดิม) · กลางวัน — ชั้นข้อมูลเหมือนกันทุกอย่าง เปลี่ยนแค่สี ─────────────────────────
  function isDay() { return document.documentElement.classList.contains('kd-day'); }
  var NIGHT = {
    bg: '#04060c', sky: ['#03050c', '#16244a', '#070c1c'], light: ['#ffd9a8', .45],
    hsShadow: '#000000', hsHi: 'rgba(150,175,255,.22)', hsAccent: '#05070e', hsEx: .45,
    urban: '#110d0e', industrial: '#140f0c', park: '#06110c', water: '#06132b', waterway: '#0a1c40',
    glow: ['#ff8a1f', .32], minor: '#9a5a26', mid: '#e08a35', major: '#ffc46e', rail: '#4b5c88',
    // ตึก: ภาพจริงจากมือถือ หลังคาสีส้มสดเกินไปตอนมองจากข้างบน — ลดความสดลง ยังสว่างตามความสูงเหมือนเดิม
    bld: [0, '#3b2d24', 10, '#56412f', 40, '#7a5c3c', 120, '#a8834f', 250, '#d8b47a', 350, '#ecd3a6'],
    gold: '#f0b941', goldGlow: 'rgba(255,190,80,.35)',
    halo: 'rgba(0,0,0,.85)', water_t: '#7c9bd6', road_t: '#e7c493', small_t: '#e6edf8', town_t: '#ecd4a0', city_t: '#f2d48a',
    peak_t: '#c9d6ee', peak_dot: '#8fa6d8'
  };
  var DAY = {
    bg: '#ece6da', sky: ['#7fb2e8', '#cfe3f6', '#dfe8f0'], light: ['#ffffff', .35],
    hsShadow: '#5b5a50', hsHi: 'rgba(255,255,255,.55)', hsAccent: '#6d6a5c', hsEx: .5,
    urban: '#e2dbcf', industrial: '#ddd5ca', park: '#c6dfb1', water: '#8fc1ea', waterway: '#7ab2e0',
    glow: ['#ffffff', 0], minor: '#ffffff', mid: '#fff3c4', major: '#ffd27a', rail: '#9a9aa6',
    bld: [0, '#d9d2c6', 40, '#cfc6b8', 120, '#c4bcb0', 350, '#b8b4ad'],
    gold: '#e2a92e', goldGlow: 'rgba(226,169,46,.25)',
    halo: 'rgba(255,255,255,.92)', water_t: '#2d5d93', road_t: '#5b4a33', small_t: '#3b4252', town_t: '#3a3020', city_t: '#22201c',
    peak_t: '#4a3b26', peak_dot: '#8a6a3a'
  };
  function inThai(c) { return c.lng > TH_BOX[0] && c.lng < TH_BOX[2] && c.lat > TH_BOX[1] && c.lat < TH_BOX[3]; }
  // ภูมิประเทศ: AWS Terrain Tiles (ข้อมูลเปิด ฟรี ใช้เชิงพาณิชย์ได้ · ต้องให้เครดิตแหล่งข้อมูล)
  // maxzoom 12 (~30 ม./พิกเซล — ละเอียดเท่าข้อมูล SRTM จริงอยู่แล้ว): ไทล์น้อยลงมาก โหลดทัน ไม่เป็นรูดำสี่เหลี่ยมตอนเลื่อนเร็ว
  var DEM = { type: 'raster-dem', tiles: ['https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png'],
              encoding: 'terrarium', tileSize: 256, maxzoom: 12,
              attribution: '<a href="https://registry.opendata.aws/terrain-tiles/" target="_blank" rel="noopener">Terrain Tiles</a> (Mapzen · SRTM · ETOPO1 ฯลฯ)' };
  // เครื่องแรมน้อย/จอเล็ก: เงาภูเขาอย่างเดียว ไม่ยกพื้นเป็น 3 มิติ (ประหยัดแรงเครื่องและเน็ต)
  var lightDevice = (navigator.deviceMemory || 8) <= 3 || (navigator.connection || {}).saveData;
  function style() {
    var st = buildStyle();
    // ภูเขานูนจริงเมื่อเอียงกล้อง · 1.5 เท่า ให้เขาเตี้ยๆ ริมทะเล (เขาสามมุข ~100 ม.) ยังเห็นเป็นเนิน
    if (!lightDevice) st.terrain = { source: 'dem', exaggeration: 1.5 };
    return st;
  }
  function buildStyle() {
    var C = isDay() ? DAY : NIGHT, LM = landmarkData();
    function road(id, classes, color, w0, w1, op) {
      return { id: id, type: 'line', source: 'omt', 'source-layer': 'transportation',
               filter: ['in', ['get', 'class'], ['literal', classes]],
               layout: { 'line-cap': 'round', 'line-join': 'round' },
               paint: { 'line-color': color, 'line-opacity': op,
                        'line-width': ['interpolate', ['exponential', 1.6], ['zoom'], 7, w0, 18, w1] } };
    }
    var halo = { 'text-halo-color': C.halo, 'text-halo-width': 1.4 };
    function paint(o) { for (var k in halo) o[k] = halo[k]; return o; }
    return {
      version: 8,
      glyphs: TILES + '/fonts/{fontstack}/{range}.pbf',
      sources: { omt: { type: 'vector', url: TILES + '/planet' }, dem: DEM, demhs: DEM,
                 lmshape: { type: 'geojson', data: LM.shapes }, lmpoint: { type: 'geojson', data: LM.points } },
      sky: { 'sky-color': C.sky[0], 'horizon-color': C.sky[1], 'fog-color': C.sky[2],
             'sky-horizon-blend': .6, 'horizon-fog-blend': .8, 'fog-ground-blend': .35, 'atmosphere-blend': 0 },
      light: { anchor: 'map', color: C.light[0], intensity: C.light[1], position: [1.2, 200, 35] },
      layers: [
        { id: 'bg', type: 'background', paint: { 'background-color': C.bg } },
        // เงาภูเขาใต้แสงจันทร์ — สันเขาสว่างอมฟ้าจางๆ หุบเขามืด
        { id: 'hillshade', type: 'hillshade', source: 'demhs',
          paint: { 'hillshade-shadow-color': C.hsShadow, 'hillshade-highlight-color': C.hsHi,
                   'hillshade-accent-color': C.hsAccent, 'hillshade-exaggeration': C.hsEx, 'hillshade-illumination-direction': 315 } },
        { id: 'urban', type: 'fill', source: 'omt', 'source-layer': 'landuse',
          filter: ['in', ['get', 'class'], ['literal', ['residential', 'commercial', 'retail', 'industrial']]],
          paint: { 'fill-color': ['match', ['get', 'class'], 'industrial', C.industrial, C.urban], 'fill-opacity': .8 } },
        { id: 'park', type: 'fill', source: 'omt', 'source-layer': 'park', paint: { 'fill-color': C.park, 'fill-opacity': .8 } },
        { id: 'water', type: 'fill', source: 'omt', 'source-layer': 'water', paint: { 'fill-color': C.water } },
        { id: 'waterway', type: 'line', source: 'omt', 'source-layer': 'waterway',
          paint: { 'line-color': C.waterway, 'line-width': ['interpolate', ['linear'], ['zoom'], 8, .5, 15, 3] } },
        // ถนนใหญ่มีแสงฟุ้งรอบเส้น เหมือนภาพถ่ายกลางคืนจากอวกาศ
        { id: 'road-glow', type: 'line', source: 'omt', 'source-layer': 'transportation',
          filter: ['in', ['get', 'class'], ['literal', ['motorway', 'trunk', 'primary']]],
          layout: { 'line-cap': 'round', 'line-join': 'round' },
          paint: { 'line-color': C.glow[0], 'line-opacity': C.glow[1],
                   'line-blur': ['interpolate', ['exponential', 1.6], ['zoom'], 7, 2, 18, 18],
                   'line-width': ['interpolate', ['exponential', 1.6], ['zoom'], 7, 3, 18, 40] } },
        // ซอยจางเมื่อมองไกล แล้วค่อยสว่างเมื่อซูมใกล้ — ถนนใหญ่เด่นเหมือนเส้นเลือดของเมือง
        road('road-minor', ['minor', 'service'], C.minor, .15, 4.5,
             ['interpolate', ['linear'], ['zoom'], 11, 0, 13, .18, 15, .45, 17, .65]),
        road('road-mid', ['secondary', 'tertiary'], C.mid, .35, 9,
             ['interpolate', ['linear'], ['zoom'], 7, .35, 11, .7, 14, .9]),
        road('road-major', ['motorway', 'trunk', 'primary'], C.major, .7, 15, .95),
        { id: 'rail', type: 'line', source: 'omt', 'source-layer': 'transportation', minzoom: 11,
          filter: ['==', ['get', 'class'], 'rail'],
          paint: { 'line-color': C.rail, 'line-width': 1.2, 'line-dasharray': [3, 2], 'line-opacity': .7 } },
        // ตึกมีแสงอุ่นจากหน้าต่าง — ยอดตึกสว่างกว่าฐาน (vertical gradient) ตึกสูงสว่างกว่าตึกเตี้ย
        // ตึกส่วนใหญ่ในไทยไม่มีข้อมูลความสูง (ได้ ~3–6 ม.) — เดิมสีมืดจนกลืนพื้น
        { id: 'building', type: 'fill-extrusion', source: 'omt', 'source-layer': 'building', minzoom: 13,
          paint: {
            'fill-extrusion-color': ['interpolate', ['linear'], ['coalesce', ['get', 'render_height'], 6]].concat(C.bld),
            'fill-extrusion-height': ['interpolate', ['linear'], ['zoom'], 13, 0, 14.5, ['coalesce', ['get', 'render_height'], 6]],
            'fill-extrusion-base': ['coalesce', ['get', 'render_min_height'], 0],
            'fill-extrusion-opacity': .93, 'fill-extrusion-vertical-gradient': true } },
        // สถานที่สำคัญ: แสงทองรอบฐาน + องค์พระสีทอง — เห็นได้ตั้งแต่ซูมระดับอำเภอ
        { id: 'landmark-glow', type: 'circle', source: 'lmpoint', minzoom: 11,
          paint: { 'circle-color': C.goldGlow, 'circle-blur': 1, 'circle-pitch-alignment': 'map',
                   'circle-radius': ['interpolate', ['exponential', 2], ['zoom'], 11, 6, 18, 520] } },
        { id: 'landmark', type: 'fill-extrusion', source: 'lmshape', minzoom: 12,
          paint: { 'fill-extrusion-color': C.gold, 'fill-extrusion-opacity': .97, 'fill-extrusion-vertical-gradient': true,
                   'fill-extrusion-base': ['get', 'base'],
                   'fill-extrusion-height': ['interpolate', ['linear'], ['zoom'], 12, ['get', 'base'], 13.5, ['get', 'top']] } },
        { id: 'peak-dot', type: 'circle', source: 'omt', 'source-layer': 'mountain_peak', minzoom: 10,
          filter: ['has', 'name'],
          paint: { 'circle-radius': 2.6, 'circle-color': C.peak_dot, 'circle-stroke-color': C.halo, 'circle-stroke-width': 1 } },
        { id: 'peak-name', type: 'symbol', source: 'omt', 'source-layer': 'mountain_peak', minzoom: 10,
          filter: ['has', 'name'],
          layout: { 'text-field': peakText(NAME_WORLD), 'text-font': ['Noto Sans Italic'], 'text-size': 11,
                    'text-anchor': 'top', 'text-offset': [0, .5], 'text-max-width': 8, 'text-padding': 6 },
          paint: paint({ 'text-color': C.peak_t }) },
        { id: 'water-name', type: 'symbol', source: 'omt', 'source-layer': 'water_name',
          layout: { 'text-field': NAME_WORLD, 'text-font': ['Noto Sans Italic'], 'text-size': 11 },
          paint: paint({ 'text-color': C.water_t }) },
        { id: 'road-name', type: 'symbol', source: 'omt', 'source-layer': 'transportation_name', minzoom: 14,
          layout: { 'text-field': NAME_WORLD, 'text-font': ['Noto Sans Regular'], 'text-size': 10.5, 'symbol-placement': 'line' },
          paint: paint({ 'text-color': C.road_t }) },
        { id: 'place-small', type: 'symbol', source: 'omt', 'source-layer': 'place', minzoom: 11.5,
          filter: ['in', ['get', 'class'], ['literal', ['suburb', 'quarter', 'neighbourhood', 'village']]],
          layout: { 'text-field': NAME_WORLD, 'text-font': ['Noto Sans Regular'], 'text-max-width': 8, 'text-padding': 6,
                    'text-size': ['interpolate', ['linear'], ['zoom'], 11.5, 10, 16, 13] },
          paint: paint({ 'text-color': C.small_t, 'text-opacity': .85 }) },
        // ตอนมองไกลขึ้นเฉพาะเมืองใหญ่ เมืองเล็กค่อยขึ้นเมื่อซูมใกล้ — เดิมชื่อแน่นจนบังถนนที่เรืองแสง
        { id: 'place-town', type: 'symbol', source: 'omt', 'source-layer': 'place', minzoom: 9.5,
          filter: ['==', ['get', 'class'], 'town'],
          layout: { 'text-field': NAME_WORLD, 'text-font': ['Noto Sans Bold'], 'text-max-width': 8, 'text-padding': 10,
                    'text-size': ['interpolate', ['linear'], ['zoom'], 9.5, 10.5, 14, 14] },
          paint: paint({ 'text-color': C.town_t, 'text-opacity': .9 }) },
        { id: 'place-city', type: 'symbol', source: 'omt', 'source-layer': 'place',
          filter: ['==', ['get', 'class'], 'city'],
          layout: { 'text-field': NAME_WORLD, 'text-font': ['Noto Sans Bold'], 'text-max-width': 8, 'text-padding': 14,
                    'text-size': ['interpolate', ['linear'], ['zoom'], 5, 10.5, 12, 15.5] },
          paint: paint({ 'text-color': C.city_t }) },
        { id: 'landmark-name', type: 'symbol', source: 'lmpoint', minzoom: 10,
          layout: { 'text-field': ['format', ['get', 'name'], { 'font-scale': 1.1 }, '\n', {}, ['get', 'sub'], { 'font-scale': .8 }],
                    'text-font': ['Noto Sans Bold'], 'text-size': 13, 'text-anchor': 'top', 'text-offset': [0, 1.4],   // ใต้ฐาน ไม่บังองค์พระ
                    'text-max-width': 14, 'text-allow-overlap': true, 'symbol-z-order': 'source' },
          paint: paint({ 'text-color': C.gold }) }
      ]
    };
  }
  // ชื่อเปลี่ยนตามที่กำลังดู: ในไทยใช้ชื่อไทยตาม OSM · ที่อื่นใช้ชื่อไทยถ้ามี ไม่มีก็อังกฤษ
  var nameMode = '';
  function syncNames() {
    if (!map || !map.isStyleLoaded()) return;
    var mode = inThai(map.getCenter()) ? 'th' : 'world';
    if (mode === nameMode) return;
    nameMode = mode;
    var name = mode === 'th' ? NAME_TH : NAME_WORLD;
    LABEL_LAYERS.forEach(function (id) { if (map.getLayer(id)) map.setLayoutProperty(id, 'text-field', name); });
    if (map.getLayer('peak-name')) map.setLayoutProperty('peak-name', 'text-field', peakText(name));
  }
  // สลับกลางวัน/กลางคืน: เปลี่ยนทั้งสไตล์ (ไทล์ที่โหลดแล้วใช้ต่อ ไม่ต้องโหลดใหม่) แล้วตั้งชื่อตามที่กำลังดูอีกรอบ
  window.addEventListener('kd-theme', function () {
    if (!map) return;
    map.setStyle(style());
    nameMode = '';
    map.once('idle', syncNames);
  });
  function closeAttrib() {
    // เครดิตแบบย่อเปิดค้างตอนเข้า บังแผนที่ที่ยังโหลดอยู่ — เก็บเป็นปุ่ม (i) ไว้ แตะเพื่อเปิดอ่านได้
    var a = box.querySelector('.maplibregl-ctrl-attrib');
    if (a) { a.classList.remove('maplibregl-compact-show'); a.removeAttribute('open'); }
  }

  function show(v) {
    on = v;
    box.classList.toggle('on', v);
    box.setAttribute('aria-hidden', v ? 'false' : 'true');
    document.documentElement.classList.toggle('kd-city', v);          // ซ่อนเข็มทิศของหน้าโลกตอนอยู่ในแผนที่
  }
  function enter(at) {
    // at = {lon, lat, zoom, pitch} — ตำแหน่ง/ระยะเดียวกับกล้องโลกตอนนี้ แผนที่จึงต่อจากภาพเดิมไม่สะดุด
    if (failed) return false;
    prefetch(function () {
      if (failed || !lib) { back(at); return; }
      var opts = { center: [at.lon, at.lat], zoom: at.zoom, pitch: at.pitch, bearing: 0 };
      exitZ = at.zoom - .8;
      if (!map) {
        map = new lib.Map({ container: box, style: style(), center: opts.center, zoom: opts.zoom, pitch: opts.pitch,
                            maxPitch: 75, minZoom: 3, maxZoom: 18.5, attributionControl: false,
                            fadeDuration: calm() ? 0 : 300 });
        map.addControl(new lib.AttributionControl({ compact: true,
          customAttribution: '<a href="https://openfreemap.org" target="_blank" rel="noopener">OpenFreeMap</a> · © OpenStreetMap contributors' }),
          'top-right');                                                   // มุมล่างมีปุ่มควบคุมโลกอยู่แล้ว
        // เข็มทิศของแผนที่เอง: แตะเพื่อหันทิศเหนือขึ้นบน และเห็นมุมเอียงของกล้อง
        map.addControl(new lib.NavigationControl({ showZoom: false, visualizePitch: true }), 'top-right');
        var loaded = false;
        map.on('load', function () { loaded = true; syncNames(); closeAttrib(); });
        // ไทล์เมืองมาถึงสักแผ่น = เน็ตใช้ได้ — เดิมรอ 'load' ซึ่งต้องโหลดทุกแผ่น (รวมภูเขา) ให้ครบก่อน
        // เน็ตมือถือช้าๆ เกิน 12 วิ เลยโดนเด้งกลับไปโลก และซูมเข้าเมืองไม่ได้อีกจนกว่าจะเปิดหน้าใหม่
        map.on('sourcedata', function (e) { if (e.sourceId === 'omt' && e.tile) loaded = true; });
        closeAttrib();
        map.on('moveend', syncNames);
        setTimeout(function () { if (!loaded) { failed = true; exit(); } }, 15000);   // เน็ตล่ม/โดนบล็อก — กลับไปโลก
        map.on('zoom', function () { if (on && !entering && map.getZoom() < exitZ) exit(); });
      } else {
        map.jumpTo(opts);
        map.resize();
      }
      show(true);
      // ดำดิ่งลงไปอีกนิดตอนเข้า ให้รู้สึกว่าบินลงเมือง
      entering = true;
      var dive = { zoom: at.zoom + 1.6, pitch: Math.min(60, at.pitch + 8) };
      if (calm()) { map.jumpTo(dive); entering = false; }
      else { map.easeTo(Object.assign(dive, { duration: 1400 })); map.once('moveend', function () { entering = false; }); }
    });
    return true;
  }
  function back(at) { if (window.KD_earth && KD_earth.fromCity) KD_earth.fromCity({ lon: at.lon, lat: at.lat }); }
  function exit() {
    if (!on) return;
    var c = map ? map.getCenter() : { lng: 0, lat: 0 };
    show(false);
    back({ lon: c.lng, lat: c.lat });
  }
  window.KD_cityMap = {
    can: function () { return !failed; },
    active: function () { return on; },
    prefetch: function () { prefetch(); },
    enter: enter,
    exit: exit,
    zoom: function (d) { if (map && on) { if (map.getZoom() + d < exitZ) exit(); else map.zoomTo(map.getZoom() + d, { duration: calm() ? 0 : 500 }); } }
  };
})();
