/* แผนที่เมืองกลางคืน 3 มิติ — ต่อจากโลกใน cockpit_earth.js เมื่อซูมลงลึกกว่าที่ภาพ NASA ยังคม
 *
 * · ข้อมูล OpenStreetMap ผ่าน OpenFreeMap (ฟรี ไม่จำกัด ไม่ต้องมีคีย์ ใช้เชิงพาณิชย์ได้ · ต้องขึ้นเครดิต OSM)
 * · วาดด้วย MapLibre GL 5.24.0 (BSD-3) เก็บไว้ใน static/vendor/ — รุ่น CSP ไม่ใช้ eval ไม่ต้องเปิด CSP ให้สคริปต์ภายนอก
 * · โหลดเฉพาะตอนซูมใกล้จะถึง (ราว 450 KB บีบอัด) — คนที่ไม่ซูมลงไปไม่ต้องโหลดเลย
 * · โทนกลางคืน: พื้นมืด ถนนเรืองส้มตามขนาดถนน ตึกยกสูงตามความสูงจริง มีแสงหน้าต่าง ยิ่งสูงยิ่งสว่าง ชื่อเมือง/ย่านจาก OSM
 * · ภูเขา 3 มิติ + เงาภูเขาแสงจันทร์จาก AWS Terrain Tiles (ข้อมูลเปิด ฟรี) — เครื่องแรมน้อยมีแค่เงา ไม่ยกพื้น
 * · ซูมออกพ้นระดับที่เข้ามา = กลับไปโลกทั้งใบที่จุดเดิม · ไม่มี WebGL2 หรือโหลดไม่ขึ้น = อยู่กับโลกต่อไปตามเดิม
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
  function inThai(c) { return c.lng > TH_BOX[0] && c.lng < TH_BOX[2] && c.lat > TH_BOX[1] && c.lat < TH_BOX[3]; }
  // ภูมิประเทศ: AWS Terrain Tiles (ข้อมูลเปิด ฟรี ใช้เชิงพาณิชย์ได้ · ต้องให้เครดิตแหล่งข้อมูล)
  var DEM = { type: 'raster-dem', tiles: ['https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png'],
              encoding: 'terrarium', tileSize: 256, maxzoom: 14,
              attribution: '<a href="https://registry.opendata.aws/terrain-tiles/" target="_blank" rel="noopener">Terrain Tiles</a> (Mapzen · SRTM · ETOPO1 ฯลฯ)' };
  // เครื่องแรมน้อย/จอเล็ก: เงาภูเขาอย่างเดียว ไม่ยกพื้นเป็น 3 มิติ (ประหยัดแรงเครื่องและเน็ต)
  var lightDevice = (navigator.deviceMemory || 8) <= 3 || (navigator.connection || {}).saveData;
  function style() {
    var st = buildStyle();
    if (!lightDevice) st.terrain = { source: 'dem', exaggeration: 1.25 };   // ภูเขานูนจริงเมื่อเอียงกล้อง
    return st;
  }
  function buildStyle() {
    function road(id, classes, color, w0, w1, op) {
      return { id: id, type: 'line', source: 'omt', 'source-layer': 'transportation',
               filter: ['in', ['get', 'class'], ['literal', classes]],
               layout: { 'line-cap': 'round', 'line-join': 'round' },
               paint: { 'line-color': color, 'line-opacity': op,
                        'line-width': ['interpolate', ['exponential', 1.6], ['zoom'], 7, w0, 18, w1] } };
    }
    var halo = { 'text-halo-color': 'rgba(0,0,0,.85)', 'text-halo-width': 1.4 };
    function paint(o) { for (var k in halo) o[k] = halo[k]; return o; }
    return {
      version: 8,
      glyphs: TILES + '/fonts/{fontstack}/{range}.pbf',
      sources: { omt: { type: 'vector', url: TILES + '/planet' }, dem: DEM, demhs: DEM },
      sky: { 'sky-color': '#03050c', 'horizon-color': '#16244a', 'fog-color': '#070c1c',
             'sky-horizon-blend': .6, 'horizon-fog-blend': .8, 'fog-ground-blend': .35, 'atmosphere-blend': 0 },
      light: { anchor: 'map', color: '#ffd9a8', intensity: .45, position: [1.2, 200, 35] },
      layers: [
        { id: 'bg', type: 'background', paint: { 'background-color': '#04060c' } },
        // เงาภูเขาใต้แสงจันทร์ — สันเขาสว่างอมฟ้าจางๆ หุบเขามืด
        { id: 'hillshade', type: 'hillshade', source: 'demhs',
          paint: { 'hillshade-shadow-color': '#000000', 'hillshade-highlight-color': 'rgba(150,175,255,.22)',
                   'hillshade-accent-color': '#05070e', 'hillshade-exaggeration': .45, 'hillshade-illumination-direction': 315 } },
        { id: 'urban', type: 'fill', source: 'omt', 'source-layer': 'landuse',
          filter: ['in', ['get', 'class'], ['literal', ['residential', 'commercial', 'retail', 'industrial']]],
          paint: { 'fill-color': ['match', ['get', 'class'], 'industrial', '#140f0c', '#110d0e'], 'fill-opacity': .8 } },
        { id: 'park', type: 'fill', source: 'omt', 'source-layer': 'park', paint: { 'fill-color': '#06110c', 'fill-opacity': .8 } },
        { id: 'water', type: 'fill', source: 'omt', 'source-layer': 'water', paint: { 'fill-color': '#06132b' } },
        { id: 'waterway', type: 'line', source: 'omt', 'source-layer': 'waterway',
          paint: { 'line-color': '#0a1c40', 'line-width': ['interpolate', ['linear'], ['zoom'], 8, .5, 15, 3] } },
        // ถนนใหญ่มีแสงฟุ้งรอบเส้น เหมือนภาพถ่ายกลางคืนจากอวกาศ
        { id: 'road-glow', type: 'line', source: 'omt', 'source-layer': 'transportation',
          filter: ['in', ['get', 'class'], ['literal', ['motorway', 'trunk', 'primary']]],
          layout: { 'line-cap': 'round', 'line-join': 'round' },
          paint: { 'line-color': '#ff8a1f', 'line-opacity': .32,
                   'line-blur': ['interpolate', ['exponential', 1.6], ['zoom'], 7, 2, 18, 18],
                   'line-width': ['interpolate', ['exponential', 1.6], ['zoom'], 7, 3, 18, 40] } },
        // ซอยจางเมื่อมองไกล แล้วค่อยสว่างเมื่อซูมใกล้ — ถนนใหญ่เด่นเหมือนเส้นเลือดของเมือง
        road('road-minor', ['minor', 'service'], '#9a5a26', .15, 4.5,
             ['interpolate', ['linear'], ['zoom'], 11, 0, 13, .18, 15, .45, 17, .65]),
        road('road-mid', ['secondary', 'tertiary'], '#e08a35', .35, 9,
             ['interpolate', ['linear'], ['zoom'], 7, .35, 11, .7, 14, .9]),
        road('road-major', ['motorway', 'trunk', 'primary'], '#ffc46e', .7, 15, .95),
        { id: 'rail', type: 'line', source: 'omt', 'source-layer': 'transportation', minzoom: 11,
          filter: ['==', ['get', 'class'], 'rail'],
          paint: { 'line-color': '#4b5c88', 'line-width': 1.2, 'line-dasharray': [3, 2], 'line-opacity': .7 } },
        // ตึกมีแสงอุ่นจากหน้าต่าง — ยอดตึกสว่างกว่าฐาน (vertical gradient) ตึกสูงสว่างกว่าตึกเตี้ย
        // ตึกส่วนใหญ่ในไทยไม่มีข้อมูลความสูง (ได้ ~3–6 ม.) — เดิมสีมืดจนกลืนพื้น
        { id: 'building', type: 'fill-extrusion', source: 'omt', 'source-layer': 'building', minzoom: 13,
          paint: {
            'fill-extrusion-color': ['interpolate', ['linear'], ['coalesce', ['get', 'render_height'], 6],
                                     0, '#4a3424', 10, '#6b4a2c', 40, '#9a6a34', 120, '#d29a4c', 250, '#ffd28a', 350, '#ffe9bf'],
            'fill-extrusion-height': ['interpolate', ['linear'], ['zoom'], 13, 0, 14.5, ['coalesce', ['get', 'render_height'], 6]],
            'fill-extrusion-base': ['coalesce', ['get', 'render_min_height'], 0],
            'fill-extrusion-opacity': .93, 'fill-extrusion-vertical-gradient': true } },
        { id: 'water-name', type: 'symbol', source: 'omt', 'source-layer': 'water_name',
          layout: { 'text-field': NAME_WORLD, 'text-font': ['Noto Sans Italic'], 'text-size': 11 },
          paint: paint({ 'text-color': '#7c9bd6' }) },
        { id: 'road-name', type: 'symbol', source: 'omt', 'source-layer': 'transportation_name', minzoom: 14,
          layout: { 'text-field': NAME_WORLD, 'text-font': ['Noto Sans Regular'], 'text-size': 10.5, 'symbol-placement': 'line' },
          paint: paint({ 'text-color': '#e7c493' }) },
        { id: 'place-small', type: 'symbol', source: 'omt', 'source-layer': 'place', minzoom: 11.5,
          filter: ['in', ['get', 'class'], ['literal', ['suburb', 'quarter', 'neighbourhood', 'village']]],
          layout: { 'text-field': NAME_WORLD, 'text-font': ['Noto Sans Regular'], 'text-max-width': 8, 'text-padding': 6,
                    'text-size': ['interpolate', ['linear'], ['zoom'], 11.5, 10, 16, 13] },
          paint: paint({ 'text-color': '#e6edf8', 'text-opacity': .85 }) },
        // ตอนมองไกลขึ้นเฉพาะเมืองใหญ่ เมืองเล็กค่อยขึ้นเมื่อซูมใกล้ — เดิมชื่อแน่นจนบังถนนที่เรืองแสง
        { id: 'place-town', type: 'symbol', source: 'omt', 'source-layer': 'place', minzoom: 9.5,
          filter: ['==', ['get', 'class'], 'town'],
          layout: { 'text-field': NAME_WORLD, 'text-font': ['Noto Sans Bold'], 'text-max-width': 8, 'text-padding': 10,
                    'text-size': ['interpolate', ['linear'], ['zoom'], 9.5, 10.5, 14, 14] },
          paint: paint({ 'text-color': '#ecd4a0', 'text-opacity': .9 }) },
        { id: 'place-city', type: 'symbol', source: 'omt', 'source-layer': 'place',
          filter: ['==', ['get', 'class'], 'city'],
          layout: { 'text-field': NAME_WORLD, 'text-font': ['Noto Sans Bold'], 'text-max-width': 8, 'text-padding': 14,
                    'text-size': ['interpolate', ['linear'], ['zoom'], 5, 10.5, 12, 15.5] },
          paint: paint({ 'text-color': '#f2d48a' }) }
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
    LABEL_LAYERS.forEach(function (id) { if (map.getLayer(id)) map.setLayoutProperty(id, 'text-field', mode === 'th' ? NAME_TH : NAME_WORLD); });
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
        map.on('load', function () { loaded = true; syncNames(); });
        map.on('moveend', syncNames);
        setTimeout(function () { if (!loaded) { failed = true; exit(); } }, 12000);   // เน็ตล่ม/โดนบล็อก — กลับไปโลก
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
