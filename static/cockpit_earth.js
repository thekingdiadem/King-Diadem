/* ฉากเปิดของหน้า Universe — ภาพจากกล้องดาวเทียม เห็นโลกตอนกลางคืนทั้งใบ แสงไฟทุกเมือง ทะเลสะท้อนแสงจันทร์ ขั้วโลกเหนือ-ใต้
 *
 * · โหมดวงโคจร (เริ่มต้น): มองขอบฟ้าจากความสูง 408 km เริ่มที่อเมริกาเหนือ แล้วเคลื่อนไปทางตะวันออกช้าๆ
 * · โหมดทั้งโลก: เห็นโลกทั้งใบ ลากเพื่อหมุนไปดูประเทศไหนก็ได้ · ปุ่มพาไปขั้วโลกเหนือ/ใต้
 * · ไม่เติมอะไรลงบนโลก (ไม่มีเส้นพรมแดน ไม่มีดวงจันทร์ปลอม ไม่มีตัวหนังสือ) — เจ้าของอยากให้สวยแบบของจริง
 * · ภาพ NASA 2K โหลดก่อน แล้วสลับเป็น 4K เมื่อเครื่องรองรับ (ไม่โหลด 4K ถ้าเปิดโหมดประหยัดเน็ต) — scripts/build_earth_textures.py
 * · ทะเล: แยกน้ำจากแผนที่น้ำจริง · ประกายแสงจันทร์บนผิวน้ำ · ระลอกคลื่น · ขอบทะเลสว่างขึ้นเมื่อมองเฉียง (Fresnel)
 * · ลดการเคลื่อนไหว (ตั้งในเครื่อง หรือปุ่มในหน้า → html.kd-calm): โลกหยุด ดาวไม่กะพริบ กล้องไม่เลื่อนเอง เปลี่ยนมุมทันทีไม่มีแพน
 * วาดด้วย WebGL ไม่มีไลบรารีเพิ่ม · ไม่มี WebGL = พื้นหลังไล่สีแทน
 */
(function () {
  var canvas = document.getElementById('cockpit-earth');
  if (!canvas) return;
  var wrap = canvas.parentNode;
  var gl = canvas.getContext('webgl', { antialias: false, alpha: false, premultipliedAlpha: false });
  if (!gl) { wrap.classList.add('no-webgl'); return; }

  var MQ = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  function calm() { return MQ.matches || document.documentElement.classList.contains('kd-calm'); }

  // มุมกล้อง: lon/lat ของจุดกลางจอ · zoom 0 = ทั้งโลก, 1 = วงโคจร · ค่า t* คือเป้าหมายที่ค่อยๆ เลื่อนไปหา
  var S = { lon: -95, lat: 40, zoom: 1, mag: 1, tlon: -95, tlat: 40, tzoom: 1, tmag: 1 };
  var MAG_MAX = 16;
  var DRIFT = 0.5;                                  // องศาต่อวินาที — รอบโลกราว 12 นาที
  window.KD_satLon = function () { return ((S.lon % 360) + 540) % 360 - 180; };

  var VS = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}';
  var FS = [
    'precision highp float;',
    'uniform vec2 res;uniform float t,ready,zoom,mag,lon,lat,hasW;uniform sampler2D lights,day,clouds,water;',
    'const float PI=3.14159265;',
    'float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
    'float vn(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1.,0.)),f.x),mix(h(i+vec2(0.,1.)),h(i+1.),f.x),f.y);}',
    'float fbm(vec2 p){float v=0.,a=.5;for(int i=0;i<5;i++){v+=a*vn(p);p*=2.03;a*=.5;}return v;}',
    'mat3 rx(float a){float c=cos(a),s=sin(a);return mat3(1.,0.,0.,0.,c,s,0.,-s,c);}',
    'mat3 ry(float a){float c=cos(a),s=sin(a);return mat3(c,0.,-s,0.,1.,0.,s,0.,c);}',
    'void main(){',
    '  vec2 uv=(gl_FragCoord.xy-.5*res)/res.y;float aspect=res.x/res.y;',
    '  float Ro=max(.82,aspect*.95);vec2 co=vec2(0.,-Ro-.02+.30);',            // วงโคจร: ขอบฟ้าราวหนึ่งในสามจากบน
    '  float Rg=min(.40,aspect*.44);vec2 cg=vec2(0.,.05);',                      // ทั้งโลก: ลูกโลกอยู่กลางจอ
    '  float z=smoothstep(0.,1.,zoom);float R=mix(Rg,Ro,z)*mag;vec2 c=mix(cg,co,z)*mag;',   // mag > 1 = ซูมใกล้กว่าวงโคจร
    '  vec2 q=(uv-c)/R;float d=length(q);',
    '  vec3 col=vec3(.004,.005,.012);',
    '  vec2 g=floor(gl_FragCoord.xy/2.);float s=h(g);',
    '  if(s>.9975){float tw=.6+.4*sin(t*2.+s*90.);col+=vec3(.75,.8,1.)*tw*(s-.9975)*90.;}',
    '  if(d<1.){',
    '    float zz=sqrt(1.-d*d);vec3 nv=vec3(q.x,q.y,zz);',
    '    float base=asin(clamp(-c.y/R,-1.,1.))*z;',          // วงโคจร: กลางจอไม่ใช่กลางลูกโลก — ชดเชยให้กลางจอ = lat ที่ตั้งไว้
    '    vec3 n=ry(radians(lon))*rx(base-radians(lat))*nv;',
    '    float la=asin(clamp(n.y,-1.,1.)),lo=atan(n.x,n.z);',
    '    vec2 tc=vec2(lo/(2.*PI)+.5,.5-la/PI);',
    '    vec2 px=vec2(1./4096.,1./2048.);',
    '    float L=texture2D(lights,tc).r;',
    '    float B=(texture2D(lights,tc+px*vec2(5.,0.)).r+texture2D(lights,tc-px*vec2(5.,0.)).r+texture2D(lights,tc+px*vec2(0.,4.)).r+texture2D(lights,tc-px*vec2(0.,4.)).r)*.25;',
    '    float cl=texture2D(clouds,tc+vec2(t*.0004,0.)).r;',
    '    vec3 land=texture2D(day,tc).rgb;',
    '    float wm=hasW>.5?texture2D(water,tc).r:step(land.b,land.g*.9+.02)*0.;',
    '    vec3 baseC=land*vec3(.018,.026,.05)+vec3(.002,.005,.014);',
    '    baseC+=vec3(.10,.12,.17)*smoothstep(.55,.8,dot(land,vec3(.33)))*(1.-wm);',   // น้ำแข็งขั้วโลก/ภูเขาหิมะต้องแสงจันทร์
    // ทะเล — สีน้ำลึก · ระลอกคลื่น · ประกายแสงจันทร์ · ขอบสว่างเมื่อมองเฉียง
    '    vec2 wv=vec2(fbm(tc*vec2(900.,450.)+t*.05),fbm(tc*vec2(900.,450.)+17.-t*.04))-.5;',
    '    vec3 wn=normalize(nv+vec3(wv*.10,0.));',
    '    vec3 Ld=normalize(vec3(.38,.55,.74));',
    '    vec3 rf=reflect(vec3(0.,0.,-1.),wn);',
    '    float glint=pow(max(dot(rf,Ld),0.),90.)*1.4+pow(max(dot(rf,Ld),0.),12.)*.10;',
    '    float fres=.02+.98*pow(1.-max(wn.z,0.),5.);',
    '    vec3 sea=vec3(.004,.014,.034)+vec3(.30,.38,.55)*fres*.22+vec3(.75,.82,1.)*glint*(1.-cl);',
    '    baseC=mix(baseC,sea,wm);',
    '    vec3 city=vec3(1.,.48,.10)*pow(L,1.35)*2.4+vec3(1.,.78,.42)*pow(L,4.)*1.4+vec3(1.,.42,.1)*pow(B,1.5)*.45;',
    '    city*=(1.-.55*cl)*(1.-.85*wm);',                                              // ไฟเรือ/แท่นเจาะยังเห็นจางๆ
    '    vec3 surf=baseC+city*ready+vec3(.55,.62,.85)*pow(cl,1.4)*.16;',
    '    surf+=vec3(.18,.35,1.)*pow(1.-zz,2.6)*.35+vec3(.35,.55,1.)*pow(1.-zz,9.)*.6;',
    '    col=mix(col,surf,smoothstep(1.,1.-.006/R,d));',
    '  }',
    '  float o=max(d-1.,0.)*R;',
    '  col+=step(1.,d)*(vec3(.15,.35,1.)*exp(-o*31.)*.45+vec3(.35,.6,1.)*exp(-o*178.)*.55);',
    '  col+=vec3(.20,.85,.42)*exp(-abs(o-.006)*555.)*.5;',                                // airglow สีเขียวเหนือขอบฟ้า แบบภาพจาก ISS
    '  col*=1.-.35*pow(length(uv*vec2(.9,1.1)),2.2);',
    '  col+=(h(gl_FragCoord.xy+fract(t)*91.)-.5)*.018;',
    '  col=1.-exp(-col*1.35);',
    '  gl_FragColor=vec4(pow(col,vec3(.92)),1.);',
    '}'
  ].join('\n');

  function sh(type, src) {
    var o = gl.createShader(type); gl.shaderSource(o, src); gl.compileShader(o);
    if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o));
    return o;
  }
  var prog;
  try {
    prog = gl.createProgram();
    gl.attachShader(prog, sh(gl.VERTEX_SHADER, VS));
    gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FS));
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(prog));
  } catch (e) { wrap.classList.add('no-webgl'); return; }
  gl.useProgram(prog);

  gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  var loc = gl.getAttribLocation(prog, 'p');
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

  var U = {};
  ['res', 't', 'ready', 'zoom', 'mag', 'lon', 'lat', 'hasW', 'lights', 'day', 'clouds', 'water']
    .forEach(function (k) { U[k] = gl.getUniformLocation(prog, k); });

  var base = (document.currentScript && document.currentScript.src || '/static/cockpit_earth.js').replace(/cockpit_earth\.js.*$/, '');
  var texs = [], pending = 3, ready = 0, hasW = 0;
  ['lights', 'day', 'clouds', 'water'].forEach(function (name, unit) {
    var tx = gl.createTexture();
    gl.activeTexture(gl.TEXTURE0 + unit);
    gl.bindTexture(gl.TEXTURE_2D, tx);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array([0, 0, 0, 255]));
    gl.uniform1i(U[name], unit);
    texs[unit] = tx;
  });
  function load(unit, file, done) {
    var img = new Image();
    img.onload = function () {
      gl.activeTexture(gl.TEXTURE0 + unit);
      gl.bindTexture(gl.TEXTURE_2D, texs[unit]);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      if (done) done();
      kick();
    };
    img.src = base + 'earth/' + file;
  }
  var can4k = gl.getParameter(gl.MAX_TEXTURE_SIZE) >= 4096 && !(navigator.connection && navigator.connection.saveData);
  function firstDone() {
    if (--pending > 0) return;
    wrap.classList.add('lit');
    load(3, 'water.png', function () { hasW = 1; });
    if (!can4k) return;
    load(0, 'lights_4k.jpg'); load(1, 'day_4k.jpg'); load(2, 'clouds_4k.jpg');      // 4K หลังภาพแรกขึ้นแล้ว — เน็ตช้าไม่ต้องรอ
  }
  load(0, 'lights.jpg', firstDone); load(1, 'day.jpg', firstDone); load(2, 'clouds.jpg', firstDone);

  function size() {
    var dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    canvas.width = Math.max(1, Math.round(canvas.clientWidth * dpr));
    canvas.height = Math.max(1, Math.round(canvas.clientHeight * dpr));
    gl.viewport(0, 0, canvas.width, canvas.height);
    kick();
  }
  window.addEventListener('resize', size);

  // ── ลากเพื่อหมุน — เมาส์ได้ทุกทิศ · นิ้วหมุนแนวนอน (ลากแนวตั้งยังเลื่อนหน้าได้ตามปกติ) ─────────────
  var drag = null, idleUntil = 0;
  canvas.addEventListener('pointerdown', function (e) {
    drag = { x: e.clientX, y: e.clientY, lon: S.tlon, lat: S.tlat, touch: e.pointerType === 'touch' };
  });
  window.addEventListener('pointermove', function (e) {
    if (!drag) return;
    var k = (S.zoom > .5 ? 25 : 110) / S.mag / Math.max(1, canvas.clientHeight / 2);   // องศาต่อพิกเซล — มองใกล้ = หมุนช้าลง
    S.tlon = drag.lon - (e.clientX - drag.x) * k * 1.4;
    if (!drag.touch) S.tlat = Math.max(-89, Math.min(89, drag.lat + (e.clientY - drag.y) * k));
    if (calm()) { S.lon = S.tlon; S.lat = S.tlat; }
    idleUntil = performance.now() + 6000;            // หยุดเลื่อนเองสักพักหลังผู้ใช้หมุนเอง
    kick();
  });
  ['pointerup', 'pointercancel'].forEach(function (ev) { window.addEventListener(ev, function () { drag = null; }); });

  function go(o) {
    for (var k in o) S['t' + k] = o[k];
    if (calm()) { S.lon = S.tlon; S.lat = S.tlat; S.zoom = S.tzoom; S.mag = S.tmag; }
    idleUntil = performance.now() + 8000;
    kick();
  }
  window.KD_earth = {
    globe: function (on) { go({ zoom: on ? 0 : 1, mag: 1, lat: on ? 20 : 40 }); },
    pole: function (north) { go({ zoom: 0, mag: 1, lat: north ? 80 : -80 }); },
    zoomIn: function () { if (S.tzoom < .5) go({ zoom: 1 }); else go({ mag: Math.min(MAG_MAX, S.tmag * 2) }); },
    zoomOut: function () { if (S.tmag > 1) go({ mag: Math.max(1, S.tmag / 2) }); else go({ zoom: 0, lat: Math.max(-60, Math.min(60, S.tlat)) }); },
    state: S
  };

  var hudPos = document.getElementById('sat-pos'), hudUtc = document.getElementById('sat-utc'), hudAlt = document.getElementById('sat-alt'), lastHud = 0;
  var visible = true, raf = 0, last = 0, tsec = 0;
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) { visible = es[0].isIntersecting; if (visible) kick(); }).observe(canvas);
  }
  function kick() { if (!raf) raf = requestAnimationFrame(frame); }
  window.addEventListener('kd-calm', kick);
  document.addEventListener('visibilitychange', kick);

  function frame(now) {
    raf = 0;
    if (document.hidden || !visible) { last = 0; return; }
    var dt = last ? Math.min(.05, (now - last) / 1000) : .016; last = now;
    var still = calm();
    if (!still) tsec += dt;
    if (!still && !drag && now > idleUntil && S.tzoom > .5 && S.tmag <= 1) S.tlon += DRIFT * dt;   // ดาวเทียมเคลื่อนไปทางตะวันออก
    var k = still ? 1 : Math.min(1, dt * 2.2);
    S.lon += (S.tlon - S.lon) * k; S.lat += (S.tlat - S.lat) * k;
    S.zoom += (S.tzoom - S.zoom) * (still ? 1 : Math.min(1, dt * 1.6));
    S.mag *= Math.pow(S.tmag / S.mag, still ? 1 : Math.min(1, dt * 1.8));   // ซูมแบบลอการิทึม — ความเร็วเท่ากันทุกระดับ
    if (ready < 1 && pending === 0) ready = still ? 1 : Math.min(1, ready + dt * 1.2);
    gl.uniform2f(U.res, canvas.width, canvas.height);
    gl.uniform1f(U.t, tsec); gl.uniform1f(U.ready, ready);
    gl.uniform1f(U.zoom, S.zoom); gl.uniform1f(U.mag, S.mag); gl.uniform1f(U.lon, S.lon); gl.uniform1f(U.lat, S.lat);
    gl.uniform1f(U.hasW, hasW);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
    if (hudPos && now - lastHud > 250) {
      lastHud = now;
      var lo = window.KD_satLon(), la = S.lat;
      hudPos.textContent = 'LAT ' + Math.abs(la).toFixed(1) + '°' + (la < 0 ? 'S' : 'N') + ' · LON ' + Math.abs(lo).toFixed(1) + '°' + (lo < 0 ? 'W' : 'E');
      if (hudUtc) hudUtc.textContent = 'UTC ' + new Date().toISOString().slice(11, 19);
      if (hudAlt) hudAlt.textContent = S.zoom > .5 ? 'ALT 408 km · 7.66 km/s' : 'FULL DISK';
    }
    labels();
    var moving = !still || Math.abs(S.tlon - S.lon) > .01 || Math.abs(S.tlat - S.lat) > .01 ||
                 Math.abs(S.tzoom - S.zoom) > .001 || Math.abs(S.tmag / S.mag - 1) > .002 || ready < 1;
    if (moving) kick();
  }
  // ── ชื่อเมือง — โผล่เฉพาะตอนซูมใกล้ · โหลดเป็นชั้นตามระยะซูม (มองทั้งโลกไม่โหลดอะไรเลย) ─────────────
  // ชั้น: เมืองหลวง 241 + เมือง 200k+ (ซูม 2×) · 50k+ (4×) · 15k+ (8×) · 5k+ (16×) — GeoNames ผ่าน static/earth/
  var lab = document.getElementById('earth-labels'), lctx = lab && lab.getContext('2d'), hero = document.getElementById('hero');
  var TIERS = [{ f: 'capitals.json', at: 2, cap: 1 }, { f: 'cities_t2.json', at: 2 }, { f: 'cities_t3.json', at: 4 },
               { f: 'cities_t4.json', at: 8 }, { f: 'cities_t5.json', at: 16 }];
  TIERS.forEach(function (T) { T.data = null; T.busy = false; });
  function fetchTier(T) {
    T.busy = true;
    fetch(base + 'earth/' + T.f).then(function (r) { return r.json(); }).then(function (d) {
      T.data = (d.capitals || d).map(function (c) {             // [ชื่อ, lat, lon] หรือ [ชื่อ, ประเทศ, lat, lon, ประชากร]
        var la = (T.cap ? c[2] : c[1]) * Math.PI / 180, lo = (T.cap ? c[3] : c[2]) * Math.PI / 180;
        return [c[0], Math.cos(la) * Math.sin(lo), Math.sin(la), Math.cos(la) * Math.cos(lo)];
      });
      kick();
    }).catch(function () { T.busy = false; });
  }
  function proj() {                                              // สมการเดียวกับ shader — กลับด้านจากลูกโลกมาหาจอ
    var Wc = canvas.clientWidth, Hc = canvas.clientHeight, aspect = Wc / Hc;
    var Ro = Math.max(.82, aspect * .95), coy = -Ro - .02 + .30, Rg = Math.min(.40, aspect * .44);
    var zr = Math.max(0, Math.min(1, S.zoom)), z = zr * zr * (3 - 2 * zr);
    var R = (Rg + (Ro - Rg) * z) * S.mag, cy = (.05 + (coy - .05) * z) * S.mag;
    var base = Math.asin(Math.max(-1, Math.min(1, -cy / R))) * z;
    var b = base - S.lat * Math.PI / 180, a = S.lon * Math.PI / 180;
    return { W: Wc, H: Hc, R: R, cy: cy, ca: Math.cos(a), sa: Math.sin(a), cb: Math.cos(b), sb: Math.sin(b) };
  }
  function toScreen(P, x, y, zw) {
    // nv = rx(-b) · ry(-a) · n   (ย้อนกลับ n = ry(a)·rx(b)·nv ของ shader)
    var x1 = P.ca * x - P.sa * zw, z1 = P.sa * x + P.ca * zw;
    var y2 = P.cb * y + P.sb * z1, z2 = -P.sb * y + P.cb * z1;
    if (z2 < .08) return null;                                   // หลังโลก หรือชิดขอบเกินไป
    return [P.W / 2 + x1 * P.R * P.H, P.H / 2 - (P.cy + y2 * P.R) * P.H];
  }
  function labels() {
    if (!lctx) return;
    var dpr = Math.min(window.devicePixelRatio || 1, 2), Wc = canvas.clientWidth, Hc = canvas.clientHeight;
    if (lab.width !== Math.round(Wc * dpr)) { lab.width = Math.round(Wc * dpr); lab.height = Math.round(Hc * dpr); }
    lctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    lctx.clearRect(0, 0, Wc, Hc);
    var show = S.zoom > .9 ? Math.max(0, Math.min(1, (S.mag - 1.5) / .8)) : 0;
    if (hero) hero.classList.toggle('zoomed', show > 0);           // ซูมใกล้ = หัวเว็บจางลง ให้เห็นแผนที่
    if (show <= 0) return;
    var limit = Math.round(30 + 12 * S.mag);                      // ไม่ให้ชื่อแน่นจนอ่านไม่ออก
    var P = proj(), boxes = [], drawn = 0;
    lctx.font = '500 11px "Noto Sans Thai Looped",system-ui,sans-serif';
    lctx.textBaseline = 'middle';
    TIERS.forEach(function (T) {
      if (S.mag < T.at * .75) return;
      if (!T.data) { if (!T.busy) fetchTier(T); return; }
      for (var i = 0; i < T.data.length && drawn < limit; i++) {
        var c = T.data[i], p = toScreen(P, c[1], c[2], c[3]);
        if (!p || p[0] < -20 || p[0] > Wc + 20 || p[1] < 0 || p[1] > Hc) continue;
        var w = lctx.measureText(c[0]).width + 10, bx = [p[0] - 14, p[1] - 13, p[0] + w + 14, p[1] + 13], hit = false;
        for (var j = 0; j < boxes.length; j++) {
          var o = boxes[j];
          if (bx[0] < o[2] && bx[2] > o[0] && bx[1] < o[3] && bx[3] > o[1]) { hit = true; break; }
        }
        if (hit) continue;                                       // ชนกับชื่อที่ใหญ่กว่า — ข้าม (เมืองใหญ่วาดก่อน)
        boxes.push(bx); drawn++;
        lctx.globalAlpha = show * (T.cap ? .95 : .72);
        lctx.fillStyle = T.cap ? '#edcc62' : 'rgba(230,240,255,.9)';
        lctx.beginPath(); lctx.arc(p[0], p[1], T.cap ? 2.2 : 1.5, 0, 6.283); lctx.fill();
        lctx.shadowColor = 'rgba(0,0,0,.9)'; lctx.shadowBlur = 4;
        lctx.fillText(c[0], p[0] + 6, p[1]);
        lctx.shadowBlur = 0;
      }
    });
    lctx.globalAlpha = 1;
  }
  // ดับเบิลคลิก/แตะสองครั้ง = บินไปจุดนั้นแล้วซูมเข้า
  canvas.addEventListener('dblclick', function (e) {
    var r = canvas.getBoundingClientRect(), P = proj();
    var ux = ((e.clientX - r.left) - P.W / 2) / P.H, uy = (P.H / 2 - (e.clientY - r.top)) / P.H;
    var qx = ux / P.R, qy = (uy - P.cy) / P.R, dd = qx * qx + qy * qy;
    if (dd >= 1) return;
    var qz = Math.sqrt(1 - dd);
    var y1 = P.cb * qy - P.sb * qz, z1 = P.sb * qy + P.cb * qz;           // n = ry(a)·rx(b)·nv
    var x = P.ca * qx + P.sa * z1, zw = -P.sa * qx + P.ca * z1;
    var lon = Math.atan2(x, zw) * 180 / Math.PI;
    lon += 360 * Math.round((S.tlon - lon) / 360);                   // หมุนทางสั้น ไม่วนรอบโลก
    go({ lat: Math.asin(Math.max(-1, Math.min(1, y1))) * 180 / Math.PI, lon: lon,
         zoom: 1, mag: Math.min(MAG_MAX, Math.max(2, S.tmag * 2)) });
  });
  size();
})();
