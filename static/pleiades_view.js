/* ดาวลูกไก่ใกล้ๆ — แตะดาวลูกไก่บนฟ้าหน้าแรก แล้วบินเข้าไปเห็นทั้งกระจุก (ฟีลเดียวกับซูมโลกลงไปเห็นเมือง)
 *
 * · วาดสดด้วยการ์ดจอทั้งหมด ไม่ใช้ภาพถ่ายของใคร — ซูมลึกแค่ไหนก็คม
 * · ดาวสว่างทุกดวงอยู่ตำแหน่งจริง ความสว่างจริง สีจริง (แคตตาล็อก Hipparcos ชุดเดียวกับฟ้าหน้าแรก)
 *   ดาวจางกว่าโชติมาตร 7.5 เติมเพิ่มแบบสุ่มคงที่ให้แน่นเหมือนภาพถ่ายนานๆ (กระจุกจริงมีสมาชิกกว่า 1,000 ดวง)
 * · หมอกสะท้อนแสงสีฟ้าเป็นริ้ว หนาสุดรอบ Merope (NGC 1435) และ Maia (NGC 1432) ตามภาพถ่ายดาราศาสตร์
 * · ดาวสว่างมีแฉกแสง 4 แฉกแบบกล้องโทรทรรศน์สะท้อนแสง
 * · ถ่างนิ้ว/ล้อเมาส์ซูม · ลากเลื่อน · ซูมออกพ้นจุดเริ่ม หรือกด ✕ = กลับหน้าแรก
 */
(function () {
  var C0 = [56.75, 24.12];                                     // ศูนย์กลาง M45 (RA, Dec องศา)
  var NAMES = [['Alcyone', 56.871, 24.105], ['Atlas', 57.291, 24.054], ['Electra', 56.219, 24.113], ['Maia', 56.457, 24.368],
               ['Merope', 56.581, 23.948], ['Taygeta', 56.302, 24.467], ['Pleione', 57.297, 24.137], ['Celaeno', 56.201, 24.290],
               ['Asterope', 56.477, 24.555]];
  var el, cv, gl, lab, lctx, P = {}, view = null, raf = 0, stars = null, onClose = null;

  function gno(ra, dec) {                                      // องศาจากศูนย์กลาง (x ไปตะวันตก = ขวา, y ไปเหนือ = ขึ้น)
    var R = Math.PI / 180, d = dec * R, d0 = C0[1] * R, h = (ra - C0[0]) * R;
    var cc = Math.sin(d0) * Math.sin(d) + Math.cos(d0) * Math.cos(d) * Math.cos(h);
    return [-Math.cos(d) * Math.sin(h) / cc / R, (Math.cos(d0) * Math.sin(d) - Math.sin(d0) * Math.cos(d) * Math.cos(h)) / cc / R];
  }
  var BV = [[-.4, [155, 176, 255]], [-.1, [178, 198, 255]], [0, [205, 217, 255]], [.3, [238, 240, 255]], [.6, [255, 243, 230]],
            [.9, [255, 224, 186]], [1.2, [255, 204, 150]], [1.6, [255, 176, 110]], [2.1, [255, 148, 86]]];
  function bvRGB(b) {
    if (!(b > BV[0][0])) return BV[0][1];
    for (var i = 1; i < BV.length; i++) if (b <= BV[i][0]) {
      var t = (b - BV[i - 1][0]) / (BV[i][0] - BV[i - 1][0]), a = BV[i - 1][1], c = BV[i][1];
      return [a[0] + (c[0] - a[0]) * t, a[1] + (c[1] - a[1]) * t, a[2] + (c[2] - a[2]) * t];
    }
    return BV[BV.length - 1][1];
  }

  // ── ดาว: จริงจากแคตตาล็อก + สมาชิกจางๆ เติมแบบสุ่มคงที่ ─────────────────────────────────────────
  function buildStars(cat) {
    var out = [];
    (cat || []).forEach(function (s) {
      if (Math.abs(s[0] - C0[0]) > 6 || Math.abs(s[1] - C0[1]) > 5) return;
      var g = gno(s[0], s[1]), c = bvRGB(s[3]);
      out.push([g[0], g[1], s[2], c[0] / 255, c[1] / 255, c[2] / 255]);
    });
    var seed = 1337;
    function rnd() { seed = (seed * 16807) % 2147483647; return seed / 2147483647; }
    function gs() { return Math.sqrt(-2 * Math.log(rnd() + 1e-9)) * Math.cos(6.2831853 * rnd()); }
    for (var i = 0; i < 260; i++) {                            // สมาชิกกระจุก: กระจุกตัวรอบกลาง สีฟ้าอ่อน
      var m = 7.6 + rnd() * 4.4, c = bvRGB(-.05 + rnd() * .9);
      out.push([gs() * .55, gs() * .45, m, c[0] / 255, c[1] / 255, c[2] / 255]);
    }
    for (i = 0; i < 700; i++) {                                // ดาวพื้นหลังทั่วฟ้า สีคละ
      var m2 = 7.6 + rnd() * 5, c2 = bvRGB(-.2 + rnd() * 2);
      out.push([(rnd() - .5) * 12, (rnd() - .5) * 10, m2, c2[0] / 255, c2[1] / 255, c2[2] / 255]);
    }
    return out;
  }

  // ── shader ────────────────────────────────────────────────────────────────────────────
  var VS_Q = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}';
  var FS_NEB = [
    'precision highp float;',
    'uniform vec2 uRes,uC;uniform float uDpp,uT;',
    'float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
    'float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1.,0.)),f.x),mix(h(i+vec2(0.,1.)),h(i+1.),f.x),f.y);}',
    'float fbm(vec2 p){float v=0.,a=.5;for(int i=0;i<6;i++){v+=a*n(p);p=p*2.02+vec2(1.7,9.2);a*=.5;}return v;}',
    'float g(vec2 q,vec2 c,float s){vec2 d=q-c;return exp(-dot(d,d)/(2.*s*s));}',
    'void main(){',
    ' vec2 q=uC+(gl_FragCoord.xy-.5*uRes)*uDpp;',                       // องศาจากศูนย์กลาง
    // ริ้วหมอกเอียงตามทิศจริงของภาพถ่าย (แนวจากตะวันออกเฉียงใต้ไปตะวันตกเฉียงเหนือ)
    ' float a=-.55; vec2 r=vec2(q.x*cos(a)-q.y*sin(a),q.x*sin(a)+q.y*cos(a));',
    ' vec2 wq=q+.08*vec2(fbm(q*4.+2.),fbm(q*4.+8.));',                  // บิดลายให้เป็นเส้นใยแบบหมอกจริง ไม่ใช่รอยพู่กัน
    ' float streak=fbm(vec2(r.x*1.6,r.y*6.)+fbm(wq*3.)*1.5+3.);',
    ' float wisp=fbm(vec2(r.x*4.,r.y*14.)+fbm(wq*8.)*2.+7.);',
    // หมอกหนาตามดาวที่ส่องสว่าง: Merope (NGC 1435) หนาที่สุด · Maia · Electra · Alcyone · Taygeta
    ' float d=g(q,vec2(.15,-.17),.28)*1.1+g(q,vec2(.27,.25),.24)*.95+g(q,vec2(.48,-.01),.22)*.75+g(q,vec2(-.11,0.),.28)*.85+g(q,vec2(.41,.35),.18)*.5+g(q,vec2(.1,.05),.85)*.3;',
    ' float neb=d*pow(streak,1.6)*1.6*(.55+.7*wisp);',
    ' vec3 col=mix(vec3(.07,.12,.42),vec3(.45,.62,1.),smoothstep(.15,.9,neb))*neb*.42;',
    ' col+=vec3(.7,.82,1.)*pow(max(neb-.55,0.),2.)*.25;',               // แกนหมอกสว่างใกล้ Merope
    // ฝุ่นมืดของเมฆโมเลกุลกลุ่มดาววัวรอบนอก (สีน้ำตาลอมแดงจางๆ แบบภาพถ่ายนานๆ)
    ' float dust=smoothstep(.55,.8,fbm(q*.9+21.))*(1.-smoothstep(.0,1.6,length(q)));',
    ' col+=vec3(.035,.022,.02)*fbm(q*2.3+4.)*(1.-dust*.5);',
    ' col=col*(1.-dust*.35)+vec3(.006,.008,.018);',
    ' col+=(h(gl_FragCoord.xy+fract(uT))-.5)*.012;',
    ' gl_FragColor=vec4(col,1.);',
    '}'].join('\n');
  var VS_S = [
    'attribute vec2 aP;attribute float aM;attribute vec3 aC;',
    'uniform vec2 uRes,uC;uniform float uDpp,uDpr,uMaxPt;',
    'varying vec3 vC;varying float vF,vSz,vSp;',
    'void main(){',
    ' vec2 s=(aP-uC)/uDpp;',                                          // พิกเซลจากกลางจอ
    ' gl_Position=vec4(s/(.5*uRes),0.,1.);',
    ' float f=pow(10.,-.4*(aM-1.));',                                 // ความสว่างตามโชติมาตร
    ' float zoom=clamp(.012/uDpp,.7,2.2);',                           // ซูมใกล้ = ดาวใหญ่ขึ้นเล็กน้อย (ไม่ใหญ่ตามสเกลจริง)
    ' float core=max(1.2,5.6*pow(f,.3)*zoom)*uDpr;',                  // ดาวสว่างเป็นดวงกลมขาวแบบภาพถ่ายนานๆ
    ' float spk=aM<4.4?core*(2.2+2.6*pow(f,.3)):0.;',                 // แฉกแสงสั้นๆ เฉพาะดาวสว่าง
    ' float halo=core*(aM<6.?9.:3.);',
    ' vSz=min(uMaxPt,max(halo,spk)*2.+2.);gl_PointSize=vSz;',
    ' vC=aC;vF=min(1.6,.3+1.2*pow(f,.3));vSz=2.*core/vSz;vSp=2.*spk/max(1.,gl_PointSize);',
    '}'].join('\n');
  var FS_S = [
    'precision mediump float;',
    'varying vec3 vC;varying float vF,vSz,vSp;',
    'void main(){',
    ' vec2 d=(gl_PointCoord-.5)*2.;float r=length(d);',
    ' float core=exp(-pow(r/vSz,2.)*1.3);',
    ' float halo=(.24*vSz*vSz/(r*r+vSz*vSz*.5)+.13*exp(-r*r/(vSz*vSz*12.)))*smoothstep(1.,.2,r);',
    ' float sp=0.;',
    ' if(vSp>0.){float w=vSz*.12;sp=(exp(-abs(d.y)/w)*pow(max(0.,1.-abs(d.x)/(vSp*2.)),2.)+exp(-abs(d.x)/w)*pow(max(0.,1.-abs(d.y)/(vSp*2.)),2.))*.45;}',
    ' float a=(core+halo+sp)*vF;',
    ' vec3 hb=vec3(.55,.7,1.);',
    ' vec3 c=mix(mix(hb,vC,.5),vec3(1.),smoothstep(.35,1.,core));',                 // ฟุ้งอมฟ้าแบบภาพถ่ายดาวลูกไก่                // แกนกลางขาวจ้าแบบกล้องถ่ายภาพ
    ' gl_FragColor=vec4(c*a,a);',
    '}'].join('\n');

  function sh(t, src) { var o = gl.createShader(t); gl.shaderSource(o, src); gl.compileShader(o); return gl.getShaderParameter(o, gl.COMPILE_STATUS) ? o : null; }
  function prog(v, f) { var a = sh(gl.VERTEX_SHADER, v), b = sh(gl.FRAGMENT_SHADER, f); if (!a || !b) return null;
    var p = gl.createProgram(); gl.attachShader(p, a); gl.attachShader(p, b); gl.linkProgram(p); return gl.getProgramParameter(p, gl.LINK_STATUS) ? p : null; }

  function setup() {
    el = document.createElement('div'); el.id = 'm45'; el.setAttribute('role', 'dialog'); el.setAttribute('aria-label', 'ดาวลูกไก่');
    el.innerHTML = '<canvas class="m45-gl"></canvas><canvas class="m45-lab"></canvas>' +
      '<button type="button" class="m45-x" aria-label="กลับหน้าแรก">✕</button>' +
      '<div class="m45-info"><b>ดาวลูกไก่ <span>Pleiades · M45</span></b>' +
      '<p>กระจุกดาวเปิดห่างโลกราว 444 ปีแสง · อายุราว 100 ล้านปี · สมาชิกกว่า 1,000 ดวง · หมอกสีฟ้าคือฝุ่นที่สะท้อนแสงดาวร้อน</p>' +
      '<small>ถ่างนิ้วเพื่อซูม · ซูมออกเพื่อกลับ</small></div>';
    document.body.appendChild(el);
    cv = el.querySelector('.m45-gl'); lab = el.querySelector('.m45-lab'); lctx = lab.getContext('2d');
    gl = cv.getContext('webgl', { antialias: false, premultipliedAlpha: true, alpha: false });
    if (!gl) return false;
    P.neb = prog(VS_Q, FS_NEB); P.star = prog(VS_S, FS_S);
    if (!P.neb || !P.star) return false;
    P.quad = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, P.quad);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    P.maxPt = gl.getParameter(gl.ALIASED_POINT_SIZE_RANGE)[1] || 64;
    el.querySelector('.m45-x').addEventListener('click', close);
    gestures();
    addEventListener('resize', function () { if (view) { size(); draw(); } });
    return true;
  }
  function upload() {
    var a = new Float32Array(stars.length * 6);
    stars.forEach(function (s, i) { a.set(s, i * 6); });
    P.sbuf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, P.sbuf); gl.bufferData(gl.ARRAY_BUFFER, a, gl.STATIC_DRAW);
  }
  var DPR = 1;
  function size() {
    DPR = Math.min(window.devicePixelRatio || 1, 1.5);
    cv.width = Math.round(innerWidth * DPR); cv.height = Math.round(innerHeight * DPR);
    lab.width = Math.round(innerWidth * DPR); lab.height = Math.round(innerHeight * DPR);
  }

  // ── กล้อง: ศูนย์กลาง (องศา) + องศาต่อพิกเซลจริงบนจอ ─────────────────────────────────────────
  function frame(now) {
    raf = 0; if (!view) return;
    var k = view.anim ? Math.min(1, (now - view.t0) / view.dur) : 1, e = k < 1 ? 1 - Math.pow(1 - k, 3) : 1;
    if (view.anim) {
      view.dpp = Math.exp(Math.log(view.from.dpp) + (Math.log(view.to.dpp) - Math.log(view.from.dpp)) * e);
      view.c = [view.from.c[0] + (view.to.c[0] - view.from.c[0]) * e, view.from.c[1] + (view.to.c[1] - view.from.c[1]) * e];
      if (k >= 1) view.anim = false;
    }
    draw();
    if (view.anim) raf = requestAnimationFrame(frame);
  }
  function kick() { if (!raf) raf = requestAnimationFrame(frame); }
  function draw() {
    var W = cv.width, H = cv.height, dpp = view.dpp / DPR;
    gl.viewport(0, 0, W, H); gl.disable(gl.BLEND);
    gl.useProgram(P.neb); gl.bindBuffer(gl.ARRAY_BUFFER, P.quad);
    var lp = gl.getAttribLocation(P.neb, 'p'); gl.enableVertexAttribArray(lp); gl.vertexAttribPointer(lp, 2, gl.FLOAT, false, 0, 0);
    gl.uniform2f(gl.getUniformLocation(P.neb, 'uRes'), W, H); gl.uniform2f(gl.getUniformLocation(P.neb, 'uC'), view.c[0], view.c[1]);
    gl.uniform1f(gl.getUniformLocation(P.neb, 'uDpp'), dpp); gl.uniform1f(gl.getUniformLocation(P.neb, 'uT'), 0);
    gl.drawArrays(gl.TRIANGLES, 0, 3); gl.disableVertexAttribArray(lp);
    gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE);                 // แสงดาวบวกกัน
    gl.useProgram(P.star); gl.bindBuffer(gl.ARRAY_BUFFER, P.sbuf);
    var aP = gl.getAttribLocation(P.star, 'aP'), aM = gl.getAttribLocation(P.star, 'aM'), aC = gl.getAttribLocation(P.star, 'aC');
    gl.enableVertexAttribArray(aP); gl.vertexAttribPointer(aP, 2, gl.FLOAT, false, 24, 0);
    gl.enableVertexAttribArray(aM); gl.vertexAttribPointer(aM, 1, gl.FLOAT, false, 24, 8);
    gl.enableVertexAttribArray(aC); gl.vertexAttribPointer(aC, 3, gl.FLOAT, false, 24, 12);
    gl.uniform2f(gl.getUniformLocation(P.star, 'uRes'), W, H); gl.uniform2f(gl.getUniformLocation(P.star, 'uC'), view.c[0], view.c[1]);
    gl.uniform1f(gl.getUniformLocation(P.star, 'uDpp'), dpp); gl.uniform1f(gl.getUniformLocation(P.star, 'uDpr'), DPR);
    gl.uniform1f(gl.getUniformLocation(P.star, 'uMaxPt'), P.maxPt);
    gl.drawArrays(gl.POINTS, 0, stars.length);
    gl.disableVertexAttribArray(aP); gl.disableVertexAttribArray(aM); gl.disableVertexAttribArray(aC);
    labels();
  }
  function labels() {                                          // ชื่อดาว 9 ดวงหลัก — ขึ้นเมื่อซูมเห็นกระจุกเต็มจอ
    lctx.setTransform(DPR, 0, 0, DPR, 0, 0); lctx.clearRect(0, 0, innerWidth, innerHeight);
    var span = view.dpp * innerWidth, a = Math.max(0, Math.min(1, (3.2 - span) / 1.2)), boxes = [];
    if (a <= 0) return;
    lctx.font = '500 11px "Noto Sans Thai Looped", system-ui, sans-serif'; lctx.textAlign = 'left'; lctx.textBaseline = 'middle';
    lctx.fillStyle = 'rgba(205,220,255,' + (.75 * a) + ')'; lctx.shadowColor = 'rgba(0,0,0,.8)'; lctx.shadowBlur = 4;
    NAMES.forEach(function (nm) {
      var g = gno(nm[1], nm[2]), x = innerWidth / 2 + (g[0] - view.c[0]) / view.dpp, y = innerHeight / 2 - (g[1] - view.c[1]) / view.dpp;
      var w = lctx.measureText(nm[0]).width, bx = [x + 7, y - 16, x + 11 + w, y - 2];
      if (x < -40 || x > innerWidth || y < 10 || y > innerHeight - 10) return;
      if (boxes.some(function (o) { return bx[0] < o[2] && bx[2] > o[0] && bx[1] < o[3] && bx[3] > o[1]; })) return;   // ชนกัน = ข้าม (ดาวสว่างได้ก่อน)
      boxes.push(bx); lctx.fillText(nm[0], x + 9, y - 9);
    });
  }

  // ── นิ้ว/เมาส์ ─────────────────────────────────────────────────────────────────────────
  var ptr = {}, pinch = null;
  function gestures() {
    cv.style.touchAction = 'none';
    cv.addEventListener('pointerdown', function (e) { ptr[e.pointerId] = [e.clientX, e.clientY]; cv.setPointerCapture(e.pointerId);
      var ids = Object.keys(ptr); if (ids.length === 2) { var a = ptr[ids[0]], b = ptr[ids[1]]; pinch = { d: Math.hypot(a[0] - b[0], a[1] - b[1]), dpp: view.dpp }; } });
    cv.addEventListener('pointermove', function (e) {
      var p = ptr[e.pointerId]; if (!p || !view) return; view.anim = false;
      var ids = Object.keys(ptr);
      if (ids.length >= 2 && pinch) { ptr[e.pointerId] = [e.clientX, e.clientY]; var a = ptr[ids[0]], b = ptr[ids[1]];
        zoomTo(pinch.dpp * pinch.d / Math.max(10, Math.hypot(a[0] - b[0], a[1] - b[1]))); }
      else { view.c = [view.c[0] - (e.clientX - p[0]) * view.dpp, view.c[1] + (e.clientY - p[1]) * view.dpp]; ptr[e.pointerId] = [e.clientX, e.clientY]; clampC(); kick(); }
    });
    function up(e) { delete ptr[e.pointerId]; if (Object.keys(ptr).length < 2) pinch = null; }
    cv.addEventListener('pointerup', up); cv.addEventListener('pointercancel', up);
    cv.addEventListener('wheel', function (e) { e.preventDefault(); if (!view) return; view.anim = false; zoomTo(view.dpp * Math.exp(e.deltaY * .0015)); }, { passive: false });
    addEventListener('keydown', function (e) { if (view && e.key === 'Escape') close(); });
  }
  function clampC() { view.c[0] = Math.max(-4, Math.min(4, view.c[0])); view.c[1] = Math.max(-3.5, Math.min(3.5, view.c[1])); }
  function zoomTo(dpp) {
    if (dpp > view.exit) { close(); return; }                  // ซูมออกพ้นจุดเริ่ม = กลับหน้าแรก (แบบแผนที่เมือง)
    view.dpp = Math.max(.0006, dpp); kick();
  }

  function open(o) {
    // o = { x, y, k }: ตำแหน่งดาวลูกไก่บนจอหน้าแรก + พิกเซลต่อองศาของฟ้าหน้าแรก — เริ่มจากภาพเดียวกันแล้วบินเข้าไป
    if (!el && !setup()) { if (el) el.remove(); el = null; return false; }
    if (!stars) { stars = buildStars(o.stars); upload(); }
    onClose = o.onClose || null;
    size(); el.classList.add('on'); document.documentElement.classList.add('m45-open');
    var dpp0 = 1 / Math.max(4, o.k || 14);
    var c0 = [(innerWidth / 2 - (o.x || innerWidth / 2)) * dpp0, -(innerHeight / 2 - (o.y || innerHeight / 2)) * dpp0];
    var fit = 2.3 / Math.min(innerWidth, innerHeight * .8);           // ทั้งกระจุก (~2.3°) พอดีจอ
    var calm = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    view = { c: c0.slice(), dpp: dpp0, exit: dpp0 * 1.35, anim: !calm, t0: performance.now(), dur: 2200,
             from: { c: c0, dpp: dpp0 }, to: { c: [.12, .1], dpp: fit } };
    if (calm) { view.c = view.to.c.slice(); view.dpp = fit; }
    kick();
    setTimeout(function () { var x = el.querySelector('.m45-x'); if (x) x.focus(); }, 50);
    return true;
  }
  function close() {
    if (!view) return; view = null;
    el.classList.remove('on'); document.documentElement.classList.remove('m45-open');
    if (onClose) onClose();
  }
  window.KD_pleiades = { open: open, close: close, isOpen: function () { return !!view; }, _gno: gno };
})();
