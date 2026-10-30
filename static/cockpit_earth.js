/* ฉากเปิดของหน้า Universe — โลกตอนกลางคืนจากอวกาศ แสงไฟทุกเมือง ทะเลสะท้อนแสงจันทร์ ซูมจากทั้งใบลงไปจนเห็นเมือง
 *
 * · กล้องจริงแบบมีมุมมอง (perspective): ยิ่งซูมลง กล้องยิ่งต่ำและเอียงเห็นขอบฟ้าโค้ง — ไม่ใช่ภาพแบนขยาย
 * · ระดับซูมต่อเนื่องค่าเดียว L: 0 = ทั้งโลก · 1 = วงโคจร · 2–4.4 = ลงใกล้ขึ้นทีละ 2 เท่า
 *   ซูมเลย 4.4 → แผนที่เมืองกลางคืน 3 มิติ (static/city_map.js) รับช่วงต่อที่ตำแหน่งเดิม · ซูมออกกลับมาเป็นโลก
 * · นิ้ว: ลากเลื่อน (ปล่อยแล้วไหลต่อ) · ถ่าง/บีบซูมเข้าหาจุดที่นิ้วอยู่ · แตะสองครั้งบินไปจุดนั้น
 *   เมาส์: ลาก · ล้อเลื่อนซูมเมื่อซูมเข้าไปแล้ว (หรือกด Ctrl / ถ่างบนทัชแพด) · ดับเบิลคลิก · คีย์บอร์ด: ลูกศร + −
 * · ชื่อเมืองเป็นชั้นตามความสำคัญ: เมืองหลวง → ศูนย์กลางจังหวัด/รัฐ → เมืองใหญ่ไปเล็ก · จังหวัดไทยแสดงชื่อไทย
 * · ภาพ NASA 2K โหลดก่อน แล้วสลับเป็น 4K เมื่อเครื่องรองรับ (ไม่โหลด 4K ถ้าเปิดโหมดประหยัดเน็ต) — scripts/build_earth_textures.py
 * · ลื่นบนมือถือ: ปรับความละเอียดการวาดตามความเร็วเครื่อง · คลื่นทะเลคำนวณเฉพาะจุดที่เป็นน้ำ · ชื่อเมืองวาดใหม่เมื่อกล้องขยับเท่านั้น
 * · ลดการเคลื่อนไหว (ตั้งในเครื่อง หรือปุ่มในหน้า → html.kd-calm): โลกหยุด ดาวไม่กะพริบ ไม่ไหลต่อ เปลี่ยนมุมทันที
 * · โหมดกลางวัน (ปุ่ม "กลางวัน" → html.kd-day): ภาพดาวเทียม NASA สีจริง เมฆขาว แดดสะท้อนทะเล — ค่อยๆ เปลี่ยนจากกลางคืน
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

  var PI = Math.PI, RAD = PI / 180, LMAX = 4.4;   // ลึกกว่านี้ภาพ NASA (~10 กม./พิกเซล) เบลอเป็นก้อน
  // lon/lat = จุดกลางจอบนผิวโลก · L = ระดับซูม · ค่า t* คือเป้าหมายที่ค่อยๆ เลื่อนไปหา · v* = ความเร็วที่ไหลต่อหลังปล่อยนิ้ว
  // zoom/mag เก็บไว้ให้โค้ดเดิมอ่านได้: zoom 0–1 (ทั้งโลก → วงโคจร) · mag = 2^(L−1)
  var S = { lon: -95, lat: 40, L: 1, tlon: -95, tlat: 40, tL: 1, vlon: 0, vlat: 0, zoom: 1, mag: 1, tzoom: 1, tmag: 1 };
  var DRIFT = 0.5;                                  // องศาต่อวินาที — รอบโลกราว 12 นาที
  window.KD_satLon = function () { return ((S.lon % 360) + 540) % 360 - 180; };
  function clamp(x, a, b) { return x < a ? a : x > b ? b : x; }
  function smooth(x) { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); }
  function sync() {
    S.zoom = Math.min(1, S.L); S.mag = Math.pow(2, Math.max(0, S.L - 1));
    S.tzoom = Math.min(1, S.tL); S.tmag = Math.pow(2, Math.max(0, S.tL - 1));
  }

  // ── กล้อง: ระยะเหนือผิวโลก D (หน่วยรัศมีโลก) และมุมเอียงจากแนวดิ่ง ─────────────────────────────
  var FOV = 40 * RAD, F = .5 / Math.tan(FOV / 2);
  function camera(L, aspect) {
    // ทั้งโลก: ถอยจนลูกโลกพอดีจอ (จอแนวตั้งต้องถอยไกลกว่า)
    var half = Math.min(FOV / 2, Math.atan(Math.tan(FOV / 2) * aspect)) * .86;
    var Dg = 1 / Math.sin(half) - 1, Do = .62;
    var D, tilt;
    if (L <= 1) { var z = smooth(L); D = Math.exp(Math.log(Dg) + (Math.log(Do) - Math.log(Dg)) * z); tilt = 1.02 * z; }
    else { D = Do / Math.pow(2, L - 1); tilt = 1.02 - .30 * smooth((L - 1) / 4); }   // ลงใกล้ = เอียงน้อยลง เห็นพื้นชัดขึ้น
    return { D: D, tilt: tilt, st: Math.sin(tilt), ct: Math.cos(tilt) };
  }

  var VS = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}';
  var FS = [
    'precision highp float;',
    'uniform vec2 res;uniform float t,ready,lon,lat,D,tilt,F,hasW,dayM;uniform sampler2D lights,day,clouds,water;',
    'const float PI=3.14159265;',
    'float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
    'float vn(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1.,0.)),f.x),mix(h(i+vec2(0.,1.)),h(i+1.),f.x),f.y);}',
    'float fbm(vec2 p){float v=0.,a=.5;for(int i=0;i<4;i++){v+=a*vn(p);p*=2.03;a*=.5;}return v;}',
    'mat3 rx(float a){float c=cos(a),s=sin(a);return mat3(1.,0.,0.,0.,c,s,0.,-s,c);}',
    'mat3 ry(float a){float c=cos(a),s=sin(a);return mat3(c,0.,-s,0.,1.,0.,s,0.,c);}',
    'void main(){',
    '  vec2 uv=(gl_FragCoord.xy-.5*res)/res.y;',
    '  float st=sin(tilt),ct=cos(tilt);',
    '  vec3 fw=vec3(0.,st,-ct),up=vec3(0.,ct,st),rt=vec3(1.,0.,0.);',
    '  vec3 P=vec3(0.,0.,1.)+D*vec3(0.,-st,ct);',                 // กล้องอยู่เหนือจุดกลางจอ ถอยไปทางใต้ตามมุมเอียง
    '  vec3 rd=normalize(fw*F+uv.x*rt+uv.y*up);',
    '  float b=dot(P,rd),c2=dot(P,P)-1.,disc=b*b-c2,pix=1./(F*res.y);',
    // ดาว — เลื่อนตามกล้องนิดหน่อยให้มีมิติ
    '  vec3 col=vec3(.004,.005,.012);',
    '  vec2 g=floor((gl_FragCoord.xy+vec2(lon,-lat)*res.y*.003)/2.);float s=h(g);',
    '  if(s>.9975){float tw=.6+.4*sin(t*2.+s*90.);col+=vec3(.75,.8,1.)*tw*(s-.9975)*90.;}',
    '  float dmin=sqrt(max(dot(P,P)-b*b,0.));',
    '  if(b<0.){float o=max(dmin-1.,0.);',                          // บรรยากาศเหนือขอบฟ้า + airglow สีเขียวแบบภาพจาก ISS
    '    col+=vec3(.15,.35,1.)*exp(-o*26.)*(.45+.5*dayM)+vec3(.35,.6,1.)*exp(-o*150.)*.55+vec3(.20,.85,.42)*exp(-abs(o-.007)*480.)*.5;}',
    '  if(disc>0.&&-b-sqrt(disc)>0.){',
    '    vec3 nl=P+rd*(-b-sqrt(disc));',
    '    vec3 n=ry(radians(lon))*rx(-radians(lat))*nl;',
    '    float la=asin(clamp(n.y,-1.,1.)),lo=atan(n.x,n.z);',
    '    vec2 tc=vec2(lo/(2.*PI)+.5,.5-la/PI);',
    '    float zz=max(dot(nl,-rd),0.);',
    '    vec2 px=vec2(1./4096.,1./2048.);',
    '    float L=texture2D(lights,tc).r;',
    '    float B=(texture2D(lights,tc+px*vec2(5.,0.)).r+texture2D(lights,tc-px*vec2(5.,0.)).r+texture2D(lights,tc+px*vec2(0.,4.)).r+texture2D(lights,tc-px*vec2(0.,4.)).r)*.25;',
    '    float cl=texture2D(clouds,tc+vec2(t*.0004,0.)).r;',
    '    vec3 land=texture2D(day,tc).rgb;',
    '    float wm=hasW>.5?texture2D(water,tc).r:0.;',
    '    vec3 baseC=land*vec3(.018,.026,.05)+vec3(.002,.005,.014);',
    '    float glint=0.;',
    '    baseC+=vec3(.10,.12,.17)*smoothstep(.55,.8,dot(land,vec3(.33)))*(1.-wm);',   // น้ำแข็งขั้วโลก/ภูเขาหิมะต้องแสงจันทร์
    '    if(wm>.01){',                                                                  // ทะเล — คำนวณเฉพาะจุดที่เป็นน้ำ
    '      vec2 wv=vec2(fbm(tc*vec2(900.,450.)+t*.05),fbm(tc*vec2(900.,450.)+17.-t*.04))-.5;',
    '      vec3 wn=normalize(nl+(rt*wv.x+up*wv.y)*.10);',
    '      vec3 Ld=normalize(.38*rt+.55*up-.74*fw);',
    '      vec3 rf=reflect(rd,wn);',
    '      glint=pow(max(dot(rf,Ld),0.),90.)*1.4+pow(max(dot(rf,Ld),0.),12.)*.10;',
    '      float fres=.02+.98*pow(1.-max(dot(wn,-rd),0.),5.);',
    '      vec3 sea=vec3(.004,.014,.034)+vec3(.30,.38,.55)*fres*.22+vec3(.75,.82,1.)*glint*(1.-cl);',
    '      baseC=mix(baseC,sea,wm);',
    '    }',
    '    vec3 city=vec3(1.,.48,.10)*pow(L,1.35)*2.4+vec3(1.,.78,.42)*pow(L,4.)*1.4+vec3(1.,.42,.1)*pow(B,1.5)*.45;',
    '    city*=(1.-.55*cl)*(1.-.85*wm);',                                              // ไฟเรือ/แท่นเจาะยังเห็นจางๆ
    '    vec3 surf=baseC+city*ready+vec3(.55,.62,.85)*pow(cl,1.4)*.16;',
    '    surf+=vec3(.18,.35,1.)*pow(1.-zz,2.6)*.35+vec3(.35,.55,1.)*pow(1.-zz,9.)*.6;', // ฟ้าหลัวตามความหนาของบรรยากาศที่มองผ่าน
    '    if(dayM>0.){',                                                                // กลางวัน: สีจริงจากดาวเทียม เมฆขาว แดดสะท้อนทะเล
    '      vec3 dc=pow(land,vec3(1.15))*1.25+vec3(.55,.65,.8)*glint*wm*.6*(1.-cl);',
    '      dc=mix(dc,vec3(.95,.97,1.),smoothstep(.15,.85,cl)*.85);',
    '      dc+=vec3(.25,.45,1.)*pow(1.-zz,2.2)*.55+vec3(.5,.7,1.)*pow(1.-zz,8.)*.5;',
    '      surf=mix(surf,dc,dayM);',
    '    }',
    '    col=mix(col,surf,smoothstep(0.,3.*sqrt(c2)*pix,disc));',
    '  }',
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
  ['res', 't', 'ready', 'lon', 'lat', 'D', 'tilt', 'F', 'hasW', 'dayM', 'lights', 'day', 'clouds', 'water']
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
      // ภาพทุกภาพกว้างยาวเป็นกำลังของ 2 — ใช้ mipmap ได้ ภาพทั้งโลกจึงไม่ระยิบเวลาหมุน · วนรอบเส้นแบ่งวันได้ไม่มีรอยต่อ
      gl.generateMipmap(gl.TEXTURE_2D);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      if (done) done();
      kick();
    };
    img.src = base + 'earth/' + file;
  }
  var conn = navigator.connection || {};
  var can4k = gl.getParameter(gl.MAX_TEXTURE_SIZE) >= 4096 && !conn.saveData;
  // มือถือ/เครื่องแรมน้อย/เน็ตช้า: ภาพ 4K (ราว 2.6 MB) ยังไม่โหลดจนกว่าจะซูมเข้าไปดูจริง — ทั้งโลกภาพ 2K ก็คมพอบนจอเล็ก
  var light = Math.min(screen.width, screen.height) < 700 || (navigator.deviceMemory || 8) <= 4 || /2g|3g/.test(conn.effectiveType || '');
  var got4k = false, firstIn = false;
  function maybe4k() {
    if (got4k || !firstIn || !can4k || (light && S.tL < 2)) return;
    got4k = true;
    load(0, 'lights_4k.jpg'); load(1, 'day_4k.jpg'); load(2, 'clouds_4k.jpg');      // 4K หลังภาพแรกขึ้นแล้ว — เน็ตช้าไม่ต้องรอ
  }
  function firstDone() {
    if (--pending > 0) return;
    wrap.classList.add('lit');
    load(3, 'water.png', function () { hasW = 1; });
    firstIn = true;
    maybe4k();
  }
  load(0, 'lights.jpg', firstDone); load(1, 'day.jpg', firstDone); load(2, 'clouds.jpg', firstDone);

  // ── ความละเอียดการวาดปรับตามเครื่อง: เฟรมช้า → ลดลงทีละขั้น · เร็วพอ → เพิ่มกลับ ─────────────────────
  var DPR_MAX = Math.min(window.devicePixelRatio || 1, light ? 1.25 : 1.5), scale = DPR_MAX, ftAvg = 16, ftCheck = 0;
  function size() {
    canvas.width = Math.max(1, Math.round(canvas.clientWidth * scale));
    canvas.height = Math.max(1, Math.round(canvas.clientHeight * scale));
    gl.viewport(0, 0, canvas.width, canvas.height);
    labelsDirty = true;
    kick();
  }
  window.addEventListener('resize', size);

  // ── ฉายจุดบนโลกมาที่จอ และกลับกัน — สมการเดียวกับ shader ───────────────────────────────────────
  // world n = ry(lon)·rx(−lat)·l  →  l = rx(lat)·ry(−lon)·n
  function rxv(a, v) { var c = Math.cos(a), s = Math.sin(a); return [v[0], c * v[1] - s * v[2], s * v[1] + c * v[2]]; }
  function ryv(a, v) { var c = Math.cos(a), s = Math.sin(a); return [c * v[0] + s * v[2], v[1], -s * v[0] + c * v[2]]; }
  function view() {
    var W = canvas.clientWidth, H = canvas.clientHeight, cam = camera(S.L, W / Math.max(1, H));
    var P = [0, -cam.D * cam.st, 1 + cam.D * cam.ct];
    return { W: W, H: H, cam: cam, P: P, C: ryv(S.lon * RAD, rxv(-S.lat * RAD, P)) };   // C = ตำแหน่งกล้องในพิกัดโลก
  }
  function toScreen(V, w) {
    if (w[0] * V.C[0] + w[1] * V.C[1] + w[2] * V.C[2] <= 1.002) return null;          // อยู่หลังขอบฟ้า
    var l = rxv(S.lat * RAD, ryv(-S.lon * RAD, w)), c = V.cam;
    var vx = l[0] - V.P[0], vy = l[1] - V.P[1], vz = l[2] - V.P[2];
    var x = vx, y = vy * c.ct + vz * c.st, z = vy * c.st - vz * c.ct;
    if (z <= 1e-4) return null;
    return [V.W / 2 + x / z * F * V.H, V.H / 2 - y / z * F * V.H, z];
  }
  function pick(V, sx, sy) {                                           // จุดบนจอ → lat/lon (null = ไม่โดนโลก)
    var c = V.cam, ux = (sx - V.W / 2) / V.H, uy = (V.H / 2 - sy) / V.H;
    var d = [ux, F * c.st + uy * c.ct, -F * c.ct + uy * c.st], dl = Math.hypot(d[0], d[1], d[2]);
    d = [d[0] / dl, d[1] / dl, d[2] / dl];
    var b = V.P[0] * d[0] + V.P[1] * d[1] + V.P[2] * d[2];
    var disc = b * b - (V.P[0] * V.P[0] + V.P[1] * V.P[1] + V.P[2] * V.P[2] - 1);
    if (disc <= 0) return null;
    var tt = -b - Math.sqrt(disc);
    if (tt <= 0) return null;
    var n = ryv(S.lon * RAD, rxv(-S.lat * RAD, [V.P[0] + d[0] * tt, V.P[1] + d[1] * tt, V.P[2] + d[2] * tt]));
    var lo = Math.atan2(n[0], n[2]) / RAD;
    return { lat: Math.asin(clamp(n[1], -1, 1)) / RAD, lon: lo + 360 * Math.round((S.tlon - lo) / 360) };
  }

  // ── การควบคุม ─────────────────────────────────────────────────────────────────────────────
  var idleUntil = 0, pointers = {}, gest = null, lastTap = 0, hist = [];
  function setL(L) {
    if (L > LMAX + .02 && toCity()) return;                          // ลึกกว่าภาพ NASA → แผนที่เมืองรับช่วงต่อ
    S.tL = clamp(L, 0, LMAX); sync(); maybe4k();
  }
  // ── ส่งต่อให้แผนที่เมืองกลางคืน (static/city_map.js) ด้วยตำแหน่งและระยะเดียวกับกล้องตอนนี้ ──────────────
  function toCity() {
    var CM = window.KD_cityMap;
    if (!CM || !CM.can() || S.city) return false;
    var V = view(), cam = camera(LMAX, V.W / Math.max(1, V.H));
    var mpp = cam.D * 6371000 / (F * V.H);                             // เมตรต่อพิกเซลกลางจอ
    var lon = ((S.tlon % 360) + 540) % 360 - 180;
    if (!CM.enter({ lon: lon, lat: S.tlat, zoom: Math.log(78271.517 * Math.cos(S.tlat * RAD) / mpp) / Math.LN2,
                    pitch: cam.tilt / RAD })) return false;
    S.city = true; pointers = {}; gest = null; S.vlon = S.vlat = 0;
    S.tL = LMAX; sync();
    if (lab) lab.style.opacity = '0';
    if (hero) { hero.style.setProperty('--hero-a', '0'); hero.classList.add('zoomed'); }   // โลกหยุดวาดแล้ว — ต้องซ่อนหัวเรื่องเอง
    return true;
  }
  function settle() { if (calm()) { S.lon = S.tlon; S.lat = S.tlat; S.L = S.tL; sync(); } }
  function hold(ms) { idleUntil = performance.now() + ms; kick(); }
  function degPerPx(V) {                                             // ระยะบนพื้นต่อ 1 พิกเซล (องศา) ตรงกลางจอ
    return V.cam.D / (F * V.H) / RAD;
  }
  function zoomAt(newL, sx, sy) {
    // ซูมเข้าหาจุดที่ชี้: เป้าหมายเลื่อนเข้าหาจุดนั้นตามสัดส่วนระยะที่หดลง (ทำเฉพาะตอนลงใกล้กว่าวงโคจร)
    var V = view(), at = sx != null && S.tL >= 1 && newL >= 1 ? pick(V, sx, sy) : null;
    var k = Math.pow(2, S.tL - clamp(newL, 0, LMAX));
    if (at) { S.tlon = at.lon + (S.tlon - at.lon) * k; S.tlat = clamp(at.lat + (S.tlat - at.lat) * k, -85, 85); }
    setL(newL);
  }
  function panBy(dx, dy, V) {
    var g = degPerPx(V);
    S.tlon -= dx * g / Math.max(.25, Math.cos(S.tlat * RAD));
    S.tlat = clamp(S.tlat + dy * g / Math.max(.5, V.cam.ct * 1.6 + .2), -85, 85);
  }
  function setTouchMode() { canvas.style.touchAction = S.tL > 1.02 ? 'none' : 'pan-y'; }   // ซูมเข้าไปแล้ว = แอปแผนที่เต็มตัว
  canvas.addEventListener('pointerdown', function (e) {
    pointers[e.pointerId] = { x: e.clientX, y: e.clientY };
    S.vlon = S.vlat = 0; hist = [];
    var ids = Object.keys(pointers);
    if (ids.length === 2) {
      var a = pointers[ids[0]], b = pointers[ids[1]];
      gest = { pinch: true, d0: Math.hypot(a.x - b.x, a.y - b.y) || 1, L0: S.tL, mx: (a.x + b.x) / 2, my: (a.y + b.y) / 2 };
    } else {
      gest = { pinch: false, x: e.clientX, y: e.clientY, touch: e.pointerType === 'touch', moved: 0 };
    }
    hold(6000);
  });
  window.addEventListener('pointermove', function (e) {
    var p = pointers[e.pointerId];
    if (!p || !gest) return;
    var V = view(), r = canvas.getBoundingClientRect(), dx = e.clientX - p.x, dy = e.clientY - p.y;
    p.x = e.clientX; p.y = e.clientY;
    if (gest.pinch) {
      var ids = Object.keys(pointers);
      if (ids.length < 2) return;
      var a = pointers[ids[0]], b = pointers[ids[1]], mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
      panBy(mx - gest.mx, my - gest.my, V); gest.mx = mx; gest.my = my;
      zoomAt(gest.L0 + Math.log(Math.hypot(a.x - b.x, a.y - b.y) / gest.d0) / Math.LN2, mx - r.left, my - r.top);
    } else {
      // นิ้วเดียวตอนมองทั้งโลก/วงโคจร: หมุนแนวนอนเท่านั้น (ลากแนวตั้งยังเลื่อนหน้าได้) · ซูมเข้าไปแล้วเลื่อนได้ทุกทิศ
      gest.moved += Math.abs(dx) + Math.abs(dy);
      var free = !gest.touch || S.tL > 1.02;
      panBy(dx * (S.tL <= 1 ? 1.4 : 1), free ? dy : 0, V);
      hist.push([performance.now(), S.tlon, S.tlat]);
      if (hist.length > 6) hist.shift();
    }
    settle();
    hold(6000);
  });
  function up(e) {
    var p = pointers[e.pointerId];
    delete pointers[e.pointerId];
    if (!gest) return;
    if (!gest.pinch && p) {
      var now = performance.now();
      if (gest.moved < 8) {                                             // แตะ (ไม่ใช่ลาก) — แตะสองครั้ง = บินไปจุดนั้น
        if (now - lastTap < 320) { var r = canvas.getBoundingClientRect(); flyTo(e.clientX - r.left, e.clientY - r.top); lastTap = 0; }
        else lastTap = now;
      } else if (!calm() && hist.length > 1) {                          // ปล่อยนิ้ว = โลกไหลต่ออีกนิดแล้วหยุดเอง
        var h0 = hist[0], h1 = hist[hist.length - 1], dt = (h1[0] - h0[0]) / 1000;
        if (dt > 0 && now - h1[0] < 80) { S.vlon = (h1[1] - h0[1]) / dt; S.vlat = (h1[2] - h0[2]) / dt; }
      }
    }
    gest = null;                                                        // ยกนิ้วใดนิ้วหนึ่ง = จบท่านั้น
    setTouchMode();
    hold(6000);
  }
  window.addEventListener('pointerup', up);
  window.addEventListener('pointercancel', up);
  canvas.addEventListener('wheel', function (e) {
    // ล้อเมาส์ซูมเมื่อซูมเข้าไปแล้ว หรือกด Ctrl/ถ่างทัชแพด — ที่ระดับวงโคจรปล่อยให้เลื่อนหน้าได้ตามปกติ
    if (!e.ctrlKey && S.tL <= 1.02 && e.deltaY > 0) return;
    if (!e.ctrlKey && S.tL <= 1.02 && e.deltaY < 0 && window.scrollY > 40) return;
    e.preventDefault();
    var r = canvas.getBoundingClientRect(), dy = e.deltaMode === 1 ? e.deltaY * 16 : e.deltaY;
    zoomAt(S.tL - clamp(dy, -120, 120) * (e.ctrlKey ? .012 : .0045), e.clientX - r.left, e.clientY - r.top);
    S.vlon = S.vlat = 0;
    settle(); setTouchMode(); hold(8000);
  }, { passive: false });
  canvas.tabIndex = 0;
  canvas.addEventListener('keydown', function (e) {
    var V = view(), step = 60, k = e.key;
    if (k === 'ArrowLeft') panBy(-step, 0, V); else if (k === 'ArrowRight') panBy(step, 0, V);
    else if (k === 'ArrowUp') panBy(0, -step, V); else if (k === 'ArrowDown') panBy(0, step, V);
    else if (k === '+' || k === '=') setL(S.tL < 1 ? 1 : S.tL + 1);
    else if (k === '-' || k === '_') setL(S.tL - 1);
    else return;
    e.preventDefault(); settle(); setTouchMode(); hold(8000);
  });
  function flyTo(sx, sy) {
    var at = pick(view(), sx, sy);
    if (!at) return;
    go({ lat: at.lat, lon: at.lon, L: Math.max(2, Math.min(LMAX, S.tL + 1)) });
  }
  canvas.addEventListener('dblclick', function (e) {
    if (e.pointerType === 'touch') return;                            // นิ้วจัดการเองใน pointerup แล้ว
    var r = canvas.getBoundingClientRect();
    flyTo(e.clientX - r.left, e.clientY - r.top);
  });

  function leaveCity() { if (S.city && window.KD_cityMap) window.KD_cityMap.exit(); }
  function go(o) {
    if (o.L > LMAX + .02 && toCity()) return;
    for (var k in o) S['t' + k] = o[k];
    S.tL = clamp(S.tL, 0, LMAX); S.vlon = S.vlat = 0;
    sync(); settle(); setTouchMode(); maybe4k();
    hold(8000);
  }
  window.KD_earth = {
    globe: function (on) { leaveCity(); go({ L: on ? 0 : 1, lat: on ? 20 : 40 }); },
    pole: function (north) { leaveCity(); go({ L: 0, lat: north ? 80 : -80 }); },
    zoomIn: function () { if (S.city) window.KD_cityMap.zoom(1); else go({ L: S.tL < 1 ? 1 : S.tL + 1 }); },
    zoomOut: function () {
      if (S.city) { window.KD_cityMap.zoom(-1); return; }
      go({ L: S.tL > 1 ? S.tL - 1 : 0, lat: S.tL > 1 ? S.tlat : clamp(S.tlat, -60, 60) });
    },
    // แผนที่เมืองเรียกตอนซูมออกพ้นระดับที่เข้ามา — กลับมาเป็นโลกที่จุดเดิม
    fromCity: function (c) {
      S.city = false;
      S.lon = S.tlon = c.lon; S.lat = S.tlat = clamp(c.lat, -85, 85);
      S.L = LMAX; S.tL = LMAX - .5; sync(); setTouchMode();
      if (lab) lab.style.opacity = '';
      labelsDirty = true; last = 0; hold(6000);
    },
    state: S
  };

  var hudPos = document.getElementById('sat-pos'), hudUtc = document.getElementById('sat-utc'), hudAlt = document.getElementById('sat-alt'), lastHud = 0;
  var hero = document.getElementById('hero');
  var visible = true, raf = 0, last = 0, tsec = 0, labelsDirty = true, lastKey = '';
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) { visible = es[0].isIntersecting; if (visible) kick(); }).observe(canvas);
  }
  function kick() { if (!raf) raf = requestAnimationFrame(frame); }
  window.addEventListener('kd-calm', kick);
  // กลางวัน/กลางคืน: dayM ไหลจาก 0 ↔ 1 ราว 1 วินาที (โหมดลดการเคลื่อนไหว = เปลี่ยนทันที)
  function dayOn() { return document.documentElement.classList.contains('kd-day') ? 1 : 0; }
  var dayM = dayOn();
  window.addEventListener('kd-theme', function () { labelsDirty = true; kick(); });
  document.addEventListener('visibilitychange', kick);

  function frame(now) {
    raf = 0;
    if (document.hidden || !visible || S.city) { last = 0; return; }   // แผนที่เมืองเต็มจอ — โลกไม่ต้องวาด
    var busy = !!gest || Math.abs(S.vlon) + Math.abs(S.vlat) > .01;
    // เครื่องเบา: ตอนลอยเองไม่มีใครแตะ วาด ~30 ภาพ/วินาทีพอ — ประหยัดแบตและไม่ร้อน
    if (light && !busy && last && now - last < 30) { kick(); return; }
    var dt = last ? Math.min(.05, (now - last) / 1000) : .016;
    if (last && busy) {                                                 // วัดความลื่นเฉพาะตอนมีคนเล่นอยู่
      ftAvg = ftAvg * .9 + (now - last) * .1;
      if (now - ftCheck > 900) {
        ftCheck = now;
        if (ftAvg > 26 && scale > .55) { scale = Math.max(.55, scale * .82); size(); }
        else if (ftAvg < 17 && scale < DPR_MAX) { scale = Math.min(DPR_MAX, scale * 1.12); size(); }
      }
    }
    last = now;
    var still = calm();
    if (!still) tsec += dt;
    if (!still && !gest && now > idleUntil && S.tL > .5 && S.tL <= 1.02) S.tlon += DRIFT * dt;   // ดาวเทียมเคลื่อนไปทางตะวันออก
    if (!gest && (S.vlon || S.vlat)) {                                 // ไหลต่อหลังปล่อยนิ้ว แล้วค่อยๆ หยุด
      S.tlon += S.vlon * dt; S.tlat = clamp(S.tlat + S.vlat * dt, -85, 85);
      var f = Math.exp(-dt * 3.2); S.vlon *= f; S.vlat *= f;
      if (Math.abs(S.vlon) + Math.abs(S.vlat) < .01) S.vlon = S.vlat = 0;
    }
    var k = still ? 1 : 1 - Math.exp(-dt * (gest ? 18 : 5));
    S.lon += (S.tlon - S.lon) * k; S.lat += (S.tlat - S.lat) * k;
    S.L += (S.tL - S.L) * (still ? 1 : 1 - Math.exp(-dt * (gest ? 16 : 4)));
    sync();
    if (S.tL > LMAX - 1 && window.KD_cityMap) window.KD_cityMap.prefetch();   // ใกล้ถึงระดับเมือง — โหลดแผนที่รอไว้
    var dayT = dayOn();
    if (dayM !== dayT) dayM = still ? dayT : dayT > dayM ? Math.min(1, dayM + dt * 1.1) : Math.max(0, dayM - dt * 1.1);
    if (ready < 1 && pending === 0) ready = still ? 1 : Math.min(1, ready + dt * 1.2);
    var cam = camera(S.L, canvas.width / Math.max(1, canvas.height));
    gl.uniform2f(U.res, canvas.width, canvas.height);
    gl.uniform1f(U.t, tsec); gl.uniform1f(U.ready, ready);
    gl.uniform1f(U.lon, S.lon); gl.uniform1f(U.lat, S.lat);
    gl.uniform1f(U.D, cam.D); gl.uniform1f(U.tilt, cam.tilt); gl.uniform1f(U.F, F);
    gl.uniform1f(U.hasW, hasW); gl.uniform1f(U.dayM, dayM);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
    if (hudPos && now - lastHud > 250) {
      lastHud = now;
      var lo = window.KD_satLon(), la = S.lat, V = view(), alt = (Math.hypot(V.C[0], V.C[1], V.C[2]) - 1) * 6371;
      hudPos.textContent = 'LAT ' + Math.abs(la).toFixed(1) + '°' + (la < 0 ? 'S' : 'N') + ' · LON ' + Math.abs(lo).toFixed(1) + '°' + (lo < 0 ? 'W' : 'E');
      if (hudUtc) hudUtc.textContent = 'UTC ' + new Date().toISOString().slice(11, 19);
      if (hudAlt) hudAlt.textContent = S.L < .3 ? 'FULL DISK' : 'ALT ' + Math.round(alt).toLocaleString('en-US') + ' km';
    }
    labels();
    if (!still || ready < 1 || dayM !== dayT) kick();                                    // คลื่น/ดาว/เมฆขยับตลอด — โหมดลดการเคลื่อนไหวหยุดวาดเมื่อนิ่ง
  }

  // ── ชื่อเมือง — ชั้นตามความสำคัญ โหลดเมื่อซูมถึง (มองทั้งโลกไม่โหลดอะไรเลย) ───────────────────────
  // GeoNames ผ่าน static/earth/ — scripts/build_earth_cities.py · แถว [ชื่อ, lat, lon, ชื่อไทย?]
  var lab = document.getElementById('earth-labels'), lctx = lab && lab.getContext('2d');
  var THAI = /^th/i.test(document.documentElement.lang || '');
  var FONT = '"Noto Sans Thai Looped",system-ui,sans-serif';
  var TIERS = [
    { f: 'capitals.json', at: 1.55, cap: 1, font: '600 12.5px ', color: '#edcc62', a: .96, dot: 2.4 },
    { f: 'admin1.json', at: 2.25, font: '500 11.5px ', color: '#f2e2b4', a: .9, dot: 1.9 },
    { f: 'cities_t2.json', at: 1.75, font: '500 11px ', color: '#e6f0ff', a: .86, dot: 1.6 },
    { f: 'cities_t3.json', at: 2.85, font: '500 10.5px ', color: '#e6f0ff', a: .76, dot: 1.4 },
    { f: 'cities_t4.json', at: 3.45, font: '400 10px ', color: '#dfe8fa', a: .68, dot: 1.2 },
    { f: 'cities_t5.json', at: 4.0, font: '400 10px ', color: '#d6e0f2', a: .6, dot: 1.1 }
  ];
  TIERS.forEach(function (T) { T.data = null; T.busy = false; });
  function fetchTier(T) {
    T.busy = true;
    fetch(base + 'earth/' + T.f).then(function (r) { return r.json(); }).then(function (d) {
      T.data = (d.capitals || d).map(function (c) {            // [ชื่อ, lat, lon, ไทย?] หรือ [ชื่อ, ประเทศ, lat, lon, ประชากร, ไทย?]
        var la = (T.cap ? c[2] : c[1]) * RAD, lo = (T.cap ? c[3] : c[2]) * RAD, th = T.cap ? c[5] : c[3];
        return [THAI && th ? th : c[0], Math.cos(la) * Math.sin(lo), Math.sin(la), Math.cos(la) * Math.cos(lo)];
      });
      labelsDirty = true; kick();
    }).catch(function () { T.busy = false; });
  }
  function labels() {
    // หัวเว็บค่อยๆ จางเมื่อซูมลง จนหายไปเมื่อเลยวงโคจร — แผนที่จะได้โล่ง
    var heroA = 1 - smooth((S.L - 1.08) / .55);
    if (hero) { hero.style.setProperty('--hero-a', heroA.toFixed(3)); hero.classList.toggle('zoomed', heroA < .99); }
    if (!lctx) return;
    var key = [S.lon.toFixed(3), S.lat.toFixed(3), S.L.toFixed(3), canvas.clientWidth, canvas.clientHeight].join();
    if (key === lastKey && !labelsDirty) return;                       // กล้องไม่ขยับ = ไม่ต้องวาดชื่อใหม่
    lastKey = key; labelsDirty = false;
    var dpr = Math.min(window.devicePixelRatio || 1, 2), Wc = canvas.clientWidth, Hc = canvas.clientHeight;
    if (lab.width !== Math.round(Wc * dpr)) { lab.width = Math.round(Wc * dpr); lab.height = Math.round(Hc * dpr); }
    lctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    lctx.clearRect(0, 0, Wc, Hc);
    var show = smooth((S.L - 1.5) / .4);
    if (show <= 0) return;
    var V = view(), limit = Math.min(Math.round(26 + 14 * S.mag), Math.round(Wc * Hc / 6500)), boxes = [], drawn = 0;
    lctx.textBaseline = 'middle';
    lctx.shadowColor = 'rgba(0,0,0,.9)';
    for (var ti = 0; ti < TIERS.length && drawn < limit; ti++) {
      var T = TIERS[ti], ta = smooth((S.L - T.at) / .35);
      if (S.tL < T.at - .3 && ta <= 0) continue;
      if (!T.data) { if (!T.busy) fetchTier(T); continue; }
      if (ta < .35) continue;                                          // ยังจางเกินอ่าน — ไม่ต้องขึ้นให้รกจอ
      lctx.font = T.font + FONT;
      for (var i = 0; i < T.data.length && drawn < limit; i++) {
        var c = T.data[i], w = [c[1], c[2], c[3]], p = toScreen(V, w);
        if (!p || p[0] < -20 || p[0] > Wc + 20 || p[1] < 8 || p[1] > Hc - 8) continue;
        var far = clamp(2.4 - p[2] / (V.cam.D * 1.7), 0, 1);           // ชื่อที่อยู่ไกลไปทางขอบฟ้าจางลง
        if (far <= .05) continue;
        var tw = lctx.measureText(c[0]).width + 10, bx = [p[0] - 12, p[1] - 11, p[0] + tw + 10, p[1] + 11], hit = false;
        for (var j = 0; j < boxes.length; j++) {
          var o = boxes[j];
          if (bx[0] < o[2] && bx[2] > o[0] && bx[1] < o[3] && bx[3] > o[1]) { hit = true; break; }
        }
        if (hit) continue;                                              // ชนกับชื่อที่สำคัญกว่า — ข้าม (ชั้นสำคัญวาดก่อน)
        boxes.push(bx); drawn++;
        lctx.globalAlpha = show * ta * far * T.a;
        lctx.fillStyle = T.color;
        lctx.shadowBlur = 0;
        lctx.beginPath(); lctx.arc(p[0], p[1], T.dot, 0, 6.283); lctx.fill();
        lctx.shadowBlur = 4;
        lctx.fillText(c[0], p[0] + 6, p[1]);
      }
    }
    lctx.shadowBlur = 0;
    lctx.globalAlpha = 1;
  }
  sync(); setTouchMode(); size();
})();
