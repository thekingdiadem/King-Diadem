/* แผนที่เมืองกลางคืน 3 มิติ — ต่อจากโลกใน cockpit_earth.js เมื่อซูมลงลึกกว่าที่ภาพ NASA ยังคม
 *
 * · ข้อมูล OpenStreetMap ผ่าน OpenFreeMap (ฟรี ไม่จำกัด ไม่ต้องมีคีย์ ใช้เชิงพาณิชย์ได้ · ต้องขึ้นเครดิต OSM)
 * · วาดด้วย MapLibre GL 5.24.0 (BSD-3) เก็บไว้ใน static/vendor/ — รุ่น CSP ไม่ใช้ eval ไม่ต้องเปิด CSP ให้สคริปต์ภายนอก
 * · โหลดเฉพาะตอนซูมใกล้จะถึง (ราว 450 KB บีบอัด) — คนที่ไม่ซูมลงไปไม่ต้องโหลดเลย
 * · โทนกลางคืน: พื้นมืด ถนนเรืองส้มตามขนาดถนน ตึกยกสูงตามความสูงจริง ยิ่งสูงยิ่งสว่าง ชื่อเมือง/ย่านจาก OSM
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

  // ชื่อภาษาอังกฤษก่อน — ตัวอักษรไทยในแผนที่แบบเวกเตอร์ยังวางสระ/วรรณยุกต์ไม่ถูกที่
  var NAME = ['coalesce', ['get', 'name:en'], ['get', 'name_en'], ['get', 'name']];
  function style() {
    function road(id, classes, color, w0, w1, op) {
      return { id: id, type: 'line', source: 'omt', 'source-layer': 'transportation',
               filter: ['in', ['get', 'class'], ['literal', classes]],
               layout: { 'line-cap': 'round', 'line-join': 'round' },
               paint: { 'line-color': color, 'line-opacity': op,
                        'line-width': ['interpolate', ['exponential', 1.6], ['zoom'], 7, w0, 18, w1] } };
    }
    return {
      version: 8,
      glyphs: TILES + '/fonts/{fontstack}/{range}.pbf',
      sources: { omt: { type: 'vector', url: TILES + '/planet' } },
      sky: { 'sky-color': '#03050c', 'horizon-color': '#16244a', 'fog-color': '#070c1c',
             'sky-horizon-blend': .6, 'horizon-fog-blend': .8, 'fog-ground-blend': .35, 'atmosphere-blend': 0 },
      light: { anchor: 'map', color: '#ffd9a8', intensity: .35, position: [1.2, 200, 35] },
      layers: [
        { id: 'bg', type: 'background', paint: { 'background-color': '#04060c' } },
        { id: 'urban', type: 'fill', source: 'omt', 'source-layer': 'landuse',
          filter: ['in', ['get', 'class'], ['literal', ['residential', 'commercial', 'retail', 'industrial']]],
          paint: { 'fill-color': ['match', ['get', 'class'], 'industrial', '#110d0b', '#0e0b0d'], 'fill-opacity': .95 } },
        { id: 'park', type: 'fill', source: 'omt', 'source-layer': 'park', paint: { 'fill-color': '#050d0a' } },
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
        road('road-minor', ['minor', 'service'], '#9a5a26', .2, 5, ['interpolate', ['linear'], ['zoom'], 11, 0, 13, .55]),
        road('road-mid', ['secondary', 'tertiary'], '#e08a35', .4, 9, .85),
        road('road-major', ['motorway', 'trunk', 'primary'], '#ffc46e', .7, 15, .95),
        { id: 'rail', type: 'line', source: 'omt', 'source-layer': 'transportation', minzoom: 11,
          filter: ['==', ['get', 'class'], 'rail'],
          paint: { 'line-color': '#4b5c88', 'line-width': 1.2, 'line-dasharray': [3, 2], 'line-opacity': .7 } },
        // ตึกยกสูงตามความสูงจริง — ยิ่งสูงยิ่งสว่าง (เหมือนไฟหน้าต่างตึกสูงกลางเมือง)
        { id: 'building', type: 'fill-extrusion', source: 'omt', 'source-layer': 'building', minzoom: 13,
          paint: {
            'fill-extrusion-color': ['interpolate', ['linear'], ['coalesce', ['get', 'render_height'], 6],
                                     0, '#17141d', 30, '#352a24', 100, '#9a6c36', 220, '#f0bd6a', 320, '#ffe0a3'],
            'fill-extrusion-height': ['interpolate', ['linear'], ['zoom'], 13, 0, 14.5, ['coalesce', ['get', 'render_height'], 6]],
            'fill-extrusion-base': ['coalesce', ['get', 'render_min_height'], 0],
            'fill-extrusion-opacity': .9, 'fill-extrusion-vertical-gradient': true } },
        { id: 'water-name', type: 'symbol', source: 'omt', 'source-layer': 'water_name',
          layout: { 'text-field': NAME, 'text-font': ['Noto Sans Italic'], 'text-size': 11 },
          paint: { 'text-color': '#7c9bd6', 'text-halo-color': 'rgba(0,0,0,.8)', 'text-halo-width': 1 } },
        { id: 'road-name', type: 'symbol', source: 'omt', 'source-layer': 'transportation_name', minzoom: 14,
          layout: { 'text-field': NAME, 'text-font': ['Noto Sans Regular'], 'text-size': 10.5, 'symbol-placement': 'line' },
          paint: { 'text-color': '#e7c493', 'text-halo-color': 'rgba(0,0,0,.85)', 'text-halo-width': 1.2 } },
        { id: 'place-small', type: 'symbol', source: 'omt', 'source-layer': 'place', minzoom: 10,
          filter: ['in', ['get', 'class'], ['literal', ['suburb', 'quarter', 'neighbourhood', 'village']]],
          layout: { 'text-field': NAME, 'text-font': ['Noto Sans Regular'], 'text-max-width': 8,
                    'text-size': ['interpolate', ['linear'], ['zoom'], 10, 10.5, 15, 13.5] },
          paint: { 'text-color': '#e6edf8', 'text-opacity': .88, 'text-halo-color': 'rgba(0,0,0,.85)', 'text-halo-width': 1.3 } },
        { id: 'place-city', type: 'symbol', source: 'omt', 'source-layer': 'place',
          filter: ['in', ['get', 'class'], ['literal', ['city', 'town']]],
          layout: { 'text-field': NAME, 'text-font': ['Noto Sans Bold'], 'text-max-width': 8,
                    'text-size': ['interpolate', ['linear'], ['zoom'], 6, 11.5, 12, 17] },
          paint: { 'text-color': '#f2d48a', 'text-halo-color': 'rgba(0,0,0,.85)', 'text-halo-width': 1.5 } }
      ]
    };
  }

  function show(v) {
    on = v;
    box.classList.toggle('on', v);
    box.setAttribute('aria-hidden', v ? 'false' : 'true');
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
        var loaded = false;
        map.on('load', function () { loaded = true; });
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
