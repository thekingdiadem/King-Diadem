/* ============================================================
   KING DIADEM — galaxy_scene.js v32
   TRANSCENDENT — Living Decision Membrane · God-Tier Edition
   Deep nebula layers | Gravitational lensing | Particle storm
   Planetary rings | Black hole vortex | Aurora curtains
   Meteor showers | Ion trails | Quantum filaments
   Fixed-pixel sizing - never overlaps sidebar / topbar / input dock
   ============================================================ */
(function () {
  'use strict';
  var cv = document.getElementById('galaxy');
  if (!cv) return;
  if (!window.KD) window.KD = {};

  var ctx = cv.getContext('2d', { alpha: true });
  var W = 0, H = 0, lastTime = 0;
  var activeRoute = 'general';
  var STARS = [];
  var FILAMENTS = [];
  var FATE_TEXTS = [];

  cv.style.cssText = 'display:block;position:absolute;inset:0;width:100%;height:100%;';

  var _rT;
  function doResize() {
    W = cv.width  = window.innerWidth;
    H = cv.height = window.innerHeight;
    buildStars();
    buildFilaments();
  }
  window.addEventListener('resize', function () {
    clearTimeout(_rT); _rT = setTimeout(doResize, 60);
  }, { passive: true });
  window.addEventListener('orientationchange', function () {
    clearTimeout(_rT); _rT = setTimeout(doResize, 160);
  }, { passive: true });
  doResize();

  /* SAFE ZONE - exclude sidebar / topbar / input dock */
  function isDesktop() { return W >= 900; }
  function UI_LEFT()   { return isDesktop() ? 252 : 0; }
  function UI_TOP()    { return 56; }
  function UI_BOTTOM() { return isDesktop() ? 92 : 132; }

  function usableW() { return Math.max(160, W - UI_LEFT()); }
  function usableH() { return Math.max(160, H - UI_TOP() - UI_BOTTOM()); }

  function SX() { return UI_LEFT() + Math.min(usableW() * 0.10, 64) + 16; }
  function SY() { return UI_TOP() + usableH() * 0.50; }
  function SR() { return Math.max(9, Math.min(usableH() * 0.045, 16)); }

  var TILT = 0.16;

  var CANON = [
    'Logic over Persona.',
    'Rule over Authority.',
    'Downside before Upside.',
    'If it cannot be explained,\nit cannot be used.',
    'Human retains final authority.',
    'Fail less, not win more.',
    'Power without trace is risk.',
    'Structure before action.',
    'Know the 99. Respect the 1.',
    'Auditability over convenience.',
    'Deferred is better than reckless.',
    'Evidence before opinion.',
    'Choice(t) >= 1 -> collapse = False',
    'ไม่ได้สร้างมาเพื่อชนะทุกครั้ง\nสร้างมาเพื่อไม่พังแบบเดิมอีกครั้ง',
    'กฎมีไว้จำกัดอำนาจ\nไม่ใช่ขยายอำนาจ',
  ];

  function spawnFateText(t) {
    var text = CANON[Math.floor(Math.random() * CANON.length)];
    var lines = text.split('\n');
    var left = UI_LEFT();
    return {
      lines: lines,
      x: left + (W - left) * (0.18 + Math.random() * 0.64),
      y: UI_TOP() + usableH() * (0.10 + Math.random() * 0.78),
      alpha: 0,
      maxAlpha: 0.05 + Math.random() * 0.05,
      state: 'in',
      lifeIn: 2200 + Math.random() * 1800,
      lifeHold: 4000 + Math.random() * 5000,
      lifeOut: 2500 + Math.random() * 1500,
      age: 0,
      size: W < 500 ? (7 + Math.random() * 3) : (9 + Math.random() * 4),
    };
  }

  function initFateTexts() {
    FATE_TEXTS = [];
    var count = W < 500 ? 3 : 5;
    for (var i = 0; i < count; i++) {
      var ft = spawnFateText(0);
      ft.age = Math.random() * (ft.lifeIn + ft.lifeHold);
      if (ft.age > ft.lifeIn) ft.state = 'hold';
      FATE_TEXTS.push(ft);
    }
  }

  var PDEFS = [
    { id:'general',  label:'GENERAL',  ang:0.60, spd:0.00022, orb:0.34, sz:8,
      c0:'#a8d4ff', c1:'#3a7ddb', c2:'#0b1f42',
      glow:'rgba(80,160,255,', atm:'rgba(70,150,250,' },
    { id:'risk',     label:'RISK',     ang:2.30, spd:0.00015, orb:0.50, sz:7,
      c0:'#ff6eb0', c1:'#cc0060', c2:'#300015',
      glow:'rgba(255,60,120,', atm:'rgba(200,30,80,' },
    { id:'survival', label:'SURVIVAL', ang:3.80, spd:0.00010, orb:0.66, sz:9,
      c0:'#baff6e', c1:'#5ecc00', c2:'#153000',
      glow:'rgba(130,255,40,', atm:'rgba(90,200,10,' },
    { id:'collapse', label:'COLLAPSE', ang:5.10, spd:0.00007, orb:0.80, sz:7.5,
      c0:'#ffaa44', c1:'#cc5500', c2:'#301000',
      glow:'rgba(255,140,20,', atm:'rgba(200,80,10,' },
    { id:'civil',    label:'CIVIL',    ang:1.20, spd:0.00004, orb:0.92, sz:9.5,
      c0:'#44ddff', c1:'#0088cc', c2:'#001830',
      glow:'rgba(0,200,255,', atm:'rgba(0,150,220,' },
    { id:'vega',     label:'VEGA',     ang:4.20, spd:0.00002, orb:0.99, sz:12,
      c0:'#eebbff', c1:'#9933dd', c2:'#1a0030',
      glow:'rgba(180,80,255,', atm:'rgba(140,40,220,' },
    { id:'a1', ang:1.60, spd:0.00032, orb:0.24, sz:2.2,
      c0:'#9ecfff', c1:'#2a6fcc', c2:'#06182e', glow:'rgba(70,150,255,' },
    { id:'a2', ang:3.20, spd:0.00019, orb:0.42, sz:1.9,
      c0:'#ff88aa', c1:'#880033', c2:'#1a0008', glow:'rgba(200,40,80,' },
    { id:'a3', ang:5.60, spd:0.00009, orb:0.58, sz:2.0,
      c0:'#ffd9a0', c1:'#cc8a30', c2:'#2a1500', glow:'rgba(255,190,90,' },
    { id:'a4', ang:2.80, spd:0.00003, orb:0.74, sz:2.3,
      c0:'#99aaff', c1:'#334499', c2:'#080d1e', glow:'rgba(80,100,255,' },
  ];
  var PLANETS = PDEFS.map(function (d) { return Object.assign({}, d); });

  function buildStars() {
    STARS = [];
    for (var i = 0; i < 1800; i++)
      STARS.push({ x:Math.random()*W, y:Math.random()*H,
        r: 0.05+Math.random()*0.18, a: 0.08+Math.random()*0.22,
        col: Math.random()>0.5 ? '170,205,255' : '205,185,255', tw:false });
    for (var j = 0; j < 280; j++)
      STARS.push({ x:Math.random()*W, y:Math.random()*H,
        r: 0.15+Math.random()*0.32, a: 0.18+Math.random()*0.28,
        col: Math.random()>0.5 ? '150,205,255' : '195,155,255',
        tw:true, tS:0.00008+Math.random()*0.00015, tO:Math.random()*Math.PI*2, tA:0.14 });
    for (var k = 0; k < 60; k++) {
      var rr = Math.random();
      STARS.push({ x:Math.random()*W, y:Math.random()*H,
        r: 0.40+Math.random()*0.65, a: 0.40+Math.random()*0.38,
        col: rr<0.42 ? '130,195,255' : (rr<0.80 ? '200,150,255' : '255,205,130'),
        tw:true, tS:0.00004+Math.random()*0.00009, tO:Math.random()*Math.PI*2, tA:0.20, bloom:true });
    }
    initFateTexts();
    buildAurora();
    buildDustMotes();
    initIonTrails();
  }

  function buildFilaments() {
    FILAMENTS = [];
    var count = W < 500 ? 6 : 12;   /* v32: doubled */
    for (var i = 0; i < count; i++) {
      FILAMENTS.push({
        x: Math.random() * W,
        y: Math.random() * H,
        w: W * (0.14 + Math.random() * 0.42),
        h: H * (0.04 + Math.random() * 0.16),
        angle: -0.5 + Math.random() * 1.0,
        hue: (Math.random() < 0.38) ? 208 : (Math.random() < 0.65 ? 278 : (Math.random() < .80 ? 36 : 168)),
        alpha: 0.022 + Math.random() * 0.060,
        speed: 0.000005 + Math.random() * 0.000014,
        phase: Math.random() * Math.PI * 2,
        /* v32: breathing layers */
        layer: i < count/2 ? 'deep' : 'mid',
      });
    }
  }

  /* ── v32: AURORA CURTAINS ──────────────────────────── */
  function buildAurora() {
    AURORA = [];
    var n = W < 600 ? 3 : 5;
    for (var i = 0; i < n; i++) {
      var segs = 18 + Math.floor(Math.random()*14);
      var pts  = [];
      var baseY = H * (0.05 + Math.random() * 0.30);
      for (var j = 0; j <= segs; j++) {
        pts.push({ x: (j/segs)*W, dy: 0, dv: (Math.random()-0.5)*0.08 });
      }
      AURORA.push({
        pts: pts,
        baseY: baseY,
        height: H * (0.06 + Math.random() * 0.12),
        hue: Math.random() < .5 ? 165 + Math.random()*30 : 210 + Math.random()*40,
        alpha: 0.012 + Math.random() * 0.022,
        speed: 0.000004 + Math.random() * 0.000008,
        phase: Math.random() * Math.PI * 2,
        waveSpeed: 0.00006 + Math.random() * 0.00008,
      });
    }
  }

  /* ── v32: DUST MOTES ───────────────────────────────── */
  function buildDustMotes() {
    DUST_MOTES = [];
    var n = W < 600 ? 60 : 140;
    for (var i = 0; i < n; i++) {
      DUST_MOTES.push({
        x: Math.random()*W, y: Math.random()*H,
        vx: (Math.random()-0.5)*0.010,
        vy: (Math.random()-0.5)*0.006,
        r: 0.3 + Math.random()*1.0,
        a: 0.04 + Math.random()*0.10,
        col: Math.random()<.6 ? '130,190,255' : '180,140,255',
        tw: true, tS: 0.00010+Math.random()*0.00020, tO: Math.random()*Math.PI*2,
      });
    }
  }

  /* ── v32: ION TRAIL per named planet ───────────────── */
  function initIonTrails() {
    ION_TRAILS = {};
    PLANETS.forEach(function(p){ if(p.label) ION_TRAILS[p.id] = []; });
  }

  /* ── NEW v32 SYSTEMS ─────────────────────────────────── */
  var METEORS   = [];          // meteor shower particles
  var ION_TRAILS= [];          // ion particle trails per planet
  var AURORA    = [];          // aurora curtain bands
  var VORTEX    = { angle:0 }; // black-hole-style vortex rings
  var DUST_MOTES= [];          // micro dust particles drifting
  var SHOCKWAVE = { active:false, x:0, y:0, r:0, maxR:0, alpha:0, col:'' };
  var nextMeteorShower = 8000;
  var meteorShowerActive = false;
  var meteorShowerEnd    = 0;

  /* ── CANON UPGRADE — more lines ─────────────────────── */
  CANON.push(
    'Fail less.\nHarm less.\nRestore more.',
    'Silence is success\nwhen choice still exists.',
    'Stay simple long enough\nto outlive the impossible.',
    'The crown belongs to no one.\nChoice itself is the crown.',
    'ปฏิจสมุปบาท —\nทุกอย่างเกิดจากเหตุปัจจัย',
    'สุญยตา —\nความว่างคือพื้นที่ของทางเลือก'
  );

  var COMET = { x:0, y:0, vx:0, vy:0, active:false, life:0, maxLife:0 };
  var nextComet = 12000;
  function spawnComet(t) {
    COMET.x = W*0.20 + Math.random()*W*0.55;
    COMET.y = -4;
    COMET.vx = 0.5 + Math.random()*0.7;
    COMET.vy = 0.4 + Math.random()*0.5;
    COMET.life = 0;
    COMET.maxLife = 1.5 + Math.random()*1.4;
    COMET.active = true;
    nextComet = t + 20000 + Math.random()*35000;
  }
  function drawComet(t, dt) {
    if (t > nextComet && !COMET.active) spawnComet(t);
    if (!COMET.active) return;
    COMET.life += dt;
    if (COMET.life > COMET.maxLife || COMET.y > H+20) { COMET.active = false; return; }
    COMET.x += COMET.vx * dt * 60 * 0.013;
    COMET.y += COMET.vy * dt * 60 * 0.013;
    var prog = COMET.life / COMET.maxLife;
    var al = prog < 0.15 ? prog/0.15 : Math.max(0, 1-(prog-0.15)/0.85);
    var tl = 80, tx = COMET.x - COMET.vx*tl*0.013, ty = COMET.y - COMET.vy*tl*0.013;
    var g = ctx.createLinearGradient(tx, ty, COMET.x, COMET.y);
    g.addColorStop(0, 'rgba(150,205,255,0)');
    g.addColorStop(0.5, 'rgba(170,215,255,'+(al*0.20)+')');
    g.addColorStop(1, 'rgba(210,235,255,'+(al*0.72)+')');
    ctx.beginPath(); ctx.moveTo(tx, ty); ctx.lineTo(COMET.x, COMET.y);
    ctx.strokeStyle = g; ctx.lineWidth = 0.8; ctx.stroke();
    ctx.beginPath(); ctx.arc(COMET.x, COMET.y, 1.3, 0, Math.PI*2);
    ctx.fillStyle = 'rgba(195,225,255,'+(al*0.90)+')'; ctx.fill();
  }

  function drawBg(t) {
    ctx.clearRect(0, 0, W, H);

    /* ── deep space gradient ── */
    var bg = ctx.createLinearGradient(0, 0, W, H);
    bg.addColorStop(0,    '#03040e');
    bg.addColorStop(0.25, '#060918');
    bg.addColorStop(0.55, '#080816');
    bg.addColorStop(0.80, '#060612');
    bg.addColorStop(1,    '#02030a');
    ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);

    ctx.globalCompositeOperation = 'screen';

    /* ── deep filaments (layer=deep first, more opaque) ── */
    for (var i = 0; i < FILAMENTS.length; i++) {
      var f = FILAMENTS[i];
      var breathe = Math.sin(t * f.speed + f.phase);
      var al = f.alpha * (f.layer==='deep' ? (0.80+0.20*breathe) : (0.55+0.45*breathe));
      var cx = f.x + Math.sin(t * f.speed * 0.7 + f.phase) * W * 0.035;
      var cy = f.y + Math.cos(t * f.speed * 0.5 + f.phase) * H * 0.025;
      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate(f.angle);
      var n = ctx.createRadialGradient(0, 0, 0, 0, 0, f.w * 0.5);
      var h = f.hue;
      n.addColorStop(0,   'hsla('+h+',100%,72%,'+al+')');
      n.addColorStop(0.4, 'hsla('+h+',85%,55%,'+(al*0.45)+')');
      n.addColorStop(0.75,'hsla('+h+',65%,35%,'+(al*0.15)+')');
      n.addColorStop(1,   'hsla('+h+',50%,20%,0)');
      ctx.beginPath();
      ctx.ellipse(0, 0, f.w * 0.5, f.h * 0.5, 0, 0, Math.PI*2);
      ctx.fillStyle = n; ctx.fill();
      ctx.restore();
    }

    /* ── AURORA CURTAINS ── */
    for (var ai = 0; ai < AURORA.length; ai++) {
      var au = AURORA[ai];
      /* animate points */
      for (var pi = 0; pi < au.pts.length; pi++) {
        var pt = au.pts[pi];
        pt.dv += (Math.random()-0.5)*0.002;
        pt.dv *= 0.98;
        pt.dy += pt.dv;
        pt.dy *= 0.995;
      }
      var aBreath = Math.sin(t * au.speed + au.phase);
      var aAl = au.alpha * (0.6 + 0.4 * aBreath);
      ctx.save();
      ctx.globalAlpha = 1;
      /* curtain: gradient from top to bottom */
      var topY = au.baseY + Math.sin(t * au.waveSpeed) * H * 0.02;
      var grad = ctx.createLinearGradient(0, topY, 0, topY + au.height);
      grad.addColorStop(0,   'hsla('+au.hue+',100%,70%,0)');
      grad.addColorStop(0.2, 'hsla('+au.hue+',100%,70%,'+(aAl*0.8)+')');
      grad.addColorStop(0.5, 'hsla('+au.hue+',90%,60%,'+aAl+')');
      grad.addColorStop(0.8, 'hsla('+au.hue+',80%,50%,'+(aAl*0.5)+')');
      grad.addColorStop(1,   'hsla('+au.hue+',70%,40%,0)');
      ctx.beginPath();
      ctx.moveTo(au.pts[0].x, topY + au.pts[0].dy);
      for (var ci = 1; ci < au.pts.length; ci++) {
        var prev = au.pts[ci-1], cur = au.pts[ci];
        var mx = (prev.x + cur.x) * 0.5;
        ctx.quadraticCurveTo(prev.x, topY+prev.dy, mx, topY+(prev.dy+cur.dy)*0.5);
      }
      ctx.lineTo(W, topY + au.height);
      ctx.lineTo(0, topY + au.height);
      ctx.closePath();
      ctx.fillStyle = grad; ctx.fill();
      ctx.restore();
    }

    var sx = SX(), sy = SY();

    /* ── VORTEX RINGS around sun (gravitational lens effect) ── */
    VORTEX.angle += 0.00015;
    ctx.save();
    ctx.translate(sx, sy);
    for (var vi = 0; vi < 4; vi++) {
      var vr = SR() * (6 + vi * 4.5);
      var va = 0.008 - vi * 0.0015;
      var vtwist = VORTEX.angle * (vi % 2 === 0 ? 1 : -1) * (1 + vi * 0.3);
      ctx.save();
      ctx.rotate(vtwist);
      ctx.beginPath();
      ctx.ellipse(0, 0, vr, vr * 0.18, 0, 0, Math.PI*2);
      var vg = ctx.createLinearGradient(-vr, 0, vr, 0);
      vg.addColorStop(0,   'rgba(80,160,255,'+(va*0.4)+')');
      vg.addColorStop(0.3, 'rgba(140,100,255,'+(va)+')');
      vg.addColorStop(0.5, 'rgba(255,180,80,'+(va*1.2)+')');
      vg.addColorStop(0.7, 'rgba(140,100,255,'+(va)+')');
      vg.addColorStop(1,   'rgba(80,160,255,'+(va*0.4)+')');
      ctx.strokeStyle = vg;
      ctx.lineWidth = 0.50 + vi * 0.10;
      ctx.stroke();
      ctx.restore();
    }
    ctx.restore();

    /* ── sun ambient halo ── */
    var sunHalo = ctx.createRadialGradient(sx, sy, SR()*0.5, sx, sy, Math.max(W,H)*0.60);
    sunHalo.addColorStop(0,   'rgba(255,140,20,0.28)');
    sunHalo.addColorStop(0.3, 'rgba(180,80,0,0.10)');
    sunHalo.addColorStop(0.6, 'rgba(60,80,200,0.04)');
    sunHalo.addColorStop(1,   'rgba(0,0,0,0)');
    ctx.beginPath(); ctx.ellipse(sx, sy, Math.max(W,H)*0.60, Math.max(W,H)*0.60, 0, 0, Math.PI*2);
    ctx.fillStyle = sunHalo; ctx.fill();

    /* ── far void (right side deep space) ── */
    var farVoid = ctx.createRadialGradient(W*0.90, H*0.50, 0, W*0.90, H*0.50, W*0.45);
    farVoid.addColorStop(0,   'rgba(20,35,80,0.38)');
    farVoid.addColorStop(0.5, 'rgba(10,15,40,0.12)');
    farVoid.addColorStop(1,   'rgba(0,0,0,0)');
    ctx.beginPath(); ctx.ellipse(W*0.90, H*0.50, W*0.45, H*0.85, 0, 0, Math.PI*2);
    ctx.fillStyle = farVoid; ctx.fill();

    ctx.globalCompositeOperation = 'source-over';
  }

  function drawStars(t) {
    for (var i = 0; i < STARS.length; i++) {
      var s = STARS[i], al = s.a;
      if (s.tw) al = s.a * (1 + Math.sin(t*s.tS + s.tO) * s.tA);
      al = Math.max(0.02, Math.min(1, al));
      ctx.beginPath(); ctx.arc(s.x, s.y, s.r, 0, Math.PI*2);
      ctx.fillStyle = 'rgba('+s.col+','+al.toFixed(3)+')'; ctx.fill();
      if (s.bloom && al > 0.45) {
        var sp = s.r * 3.5;
        ctx.strokeStyle = 'rgba('+s.col+','+(al*0.06).toFixed(3)+')';
        ctx.lineWidth = 0.20;
        ctx.beginPath();
        ctx.moveTo(s.x-sp, s.y); ctx.lineTo(s.x+sp, s.y);
        ctx.moveTo(s.x, s.y-sp); ctx.lineTo(s.x, s.y+sp);
        ctx.stroke();
      }
    }
  }

  function drawFateTexts(dt, t) {
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    for (var i = 0; i < FATE_TEXTS.length; i++) {
      var ft = FATE_TEXTS[i];
      ft.age += dt * 1000;
      if (ft.state === 'in') {
        ft.alpha = ft.maxAlpha * Math.min(1, ft.age / ft.lifeIn);
        if (ft.age >= ft.lifeIn) { ft.state = 'hold'; ft.age = 0; }
      } else if (ft.state === 'hold') {
        ft.alpha = ft.maxAlpha;
        if (ft.age >= ft.lifeHold) { ft.state = 'out'; ft.age = 0; }
      } else if (ft.state === 'out') {
        ft.alpha = ft.maxAlpha * Math.max(0, 1 - ft.age / ft.lifeOut);
        if (ft.age >= ft.lifeOut) {
          var nft = spawnFateText(t);
          FATE_TEXTS[i] = nft;
          continue;
        }
      }
      if (ft.alpha < 0.002) continue;
      var fs = ft.size;
      ctx.font = '300 ' + fs + 'px "DM Mono", monospace';
      ctx.fillStyle = 'rgba(175,210,255,' + ft.alpha.toFixed(4) + ')';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      for (var li = 0; li < ft.lines.length; li++) {
        var ly = ft.y + (li - (ft.lines.length - 1) * 0.5) * (fs * 1.5);
        ctx.fillText(ft.lines[li], ft.x, ly);
      }
    }
    ctx.restore();
  }

  /* ── v32: DUST MOTES ───────────────────────────────── */
  function drawDustMotes(t) {
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    for (var i = 0; i < DUST_MOTES.length; i++) {
      var d = DUST_MOTES[i];
      d.x = (d.x + d.vx + W) % W;
      d.y = (d.y + d.vy + H) % H;
      var al = d.a * (0.5 + 0.5 * Math.sin(t * d.tS + d.tO));
      ctx.beginPath(); ctx.arc(d.x, d.y, d.r, 0, Math.PI*2);
      ctx.fillStyle = 'rgba('+d.col+','+al.toFixed(3)+')';
      ctx.fill();
    }
    ctx.restore();
  }

  /* ── v32: METEOR SHOWER ─────────────────────────────── */
  function spawnMeteorShower(t) {
    METEORS = [];
    var n = 18 + Math.floor(Math.random()*22);
    for (var i = 0; i < n; i++) {
      var delay = Math.random() * 3000;
      METEORS.push({
        x: Math.random()*W*0.8 + W*0.05,
        y: -10 - Math.random()*60,
        vx: 0.6 + Math.random()*0.8,
        vy: 0.5 + Math.random()*0.7,
        length: 40 + Math.random()*80,
        alpha: 0.55 + Math.random()*0.35,
        life: 0, maxLife: 1.2 + Math.random()*1.0,
        delay: delay,
        col: Math.random()<.7?'195,220,255':'255,220,180',
        active: false,
      });
    }
    meteorShowerActive = true;
    meteorShowerEnd = t + 7000;
    nextMeteorShower = t + 45000 + Math.random()*60000;
  }

  function drawMeteors(t, dt) {
    if (t > nextMeteorShower && !meteorShowerActive) spawnMeteorShower(t);
    if (!meteorShowerActive) return;
    if (t > meteorShowerEnd) {
      var allDone = METEORS.every(function(m){ return m.life >= m.maxLife; });
      if (allDone) { meteorShowerActive = false; METEORS = []; return; }
    }
    var elapsed = t - (meteorShowerEnd - 7000);
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    for (var i = 0; i < METEORS.length; i++) {
      var m = METEORS[i];
      if (elapsed < m.delay) continue;
      if (!m.active) m.active = true;
      m.life += dt;
      if (m.life >= m.maxLife || m.y > H+20) continue;
      m.x += m.vx * dt * 60 * 0.014;
      m.y += m.vy * dt * 60 * 0.014;
      var prog = m.life / m.maxLife;
      var al = prog < 0.10 ? (prog/0.10)*m.alpha : Math.max(0, m.alpha*(1-(prog-0.10)/0.90));
      var tx = m.x - m.vx * m.length * 0.013;
      var ty = m.y - m.vy * m.length * 0.013;
      var mg = ctx.createLinearGradient(tx, ty, m.x, m.y);
      mg.addColorStop(0, 'rgba('+m.col+',0)');
      mg.addColorStop(0.5,'rgba('+m.col+','+(al*0.25)+')');
      mg.addColorStop(1, 'rgba('+m.col+','+al+')');
      ctx.beginPath(); ctx.moveTo(tx, ty); ctx.lineTo(m.x, m.y);
      ctx.strokeStyle = mg; ctx.lineWidth = 0.9; ctx.stroke();
      ctx.beginPath(); ctx.arc(m.x, m.y, 1.1, 0, Math.PI*2);
      ctx.fillStyle = 'rgba('+m.col+','+al+')'; ctx.fill();
    }
    ctx.restore();
  }

  /* ── v32: ION TRAILS ────────────────────────────────── */
  function updateIonTrail(pid, x, y) {
    if (!ION_TRAILS[pid]) return;
    ION_TRAILS[pid].push({ x:x, y:y, a:0.45, t:0 });
    if (ION_TRAILS[pid].length > 28) ION_TRAILS[pid].shift();
  }

  function drawIonTrails() {
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    PLANETS.forEach(function(p) {
      if (!p.label || !ION_TRAILS[p.id]) return;
      var trail = ION_TRAILS[p.id];
      if (trail.length < 2) return;
      for (var i = 1; i < trail.length; i++) {
        var prev = trail[i-1], cur = trail[i];
        var prog = i / trail.length;
        var al = prog * 0.18;
        ctx.beginPath();
        ctx.moveTo(prev.x, prev.y);
        ctx.lineTo(cur.x, cur.y);
        ctx.strokeStyle = p.glow ? p.glow + al + ')' : 'rgba(150,200,255,'+al+')';
        ctx.lineWidth = prog * 1.5;
        ctx.stroke();
      }
    });
    ctx.restore();
  }

  /* ── v32: SHOCKWAVE (triggered on route change) ──── */
  function triggerShockwave(x, y, col) {
    SHOCKWAVE.active = true;
    SHOCKWAVE.x = x; SHOCKWAVE.y = y;
    SHOCKWAVE.r = 0; SHOCKWAVE.maxR = Math.min(W,H) * 0.35;
    SHOCKWAVE.alpha = 0.55; SHOCKWAVE.col = col || '120,200,255';
  }

  function drawShockwave(dt) {
    if (!SHOCKWAVE.active) return;
    SHOCKWAVE.r  += dt * 260;
    SHOCKWAVE.alpha *= 0.96;
    if (SHOCKWAVE.r >= SHOCKWAVE.maxR || SHOCKWAVE.alpha < 0.005) {
      SHOCKWAVE.active = false; return;
    }
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    var prog = SHOCKWAVE.r / SHOCKWAVE.maxR;
    ctx.beginPath();
    ctx.arc(SHOCKWAVE.x, SHOCKWAVE.y, SHOCKWAVE.r, 0, Math.PI*2);
    ctx.strokeStyle = 'rgba('+SHOCKWAVE.col+','+SHOCKWAVE.alpha.toFixed(3)+')';
    ctx.lineWidth = (1 - prog) * 3 + 0.5;
    ctx.stroke();
    ctx.restore();
  }

  function drawOrbits() {
    var sx = SX(), sy = SY();
    var maxOrbR = Math.min(W - SX() - 16, usableH() / (TILT * 2) - 16);
    var seen = {};
    ctx.setLineDash([2, 12]);
    PLANETS.forEach(function (p) {
      var key = Math.round(p.orb * 1000);
      if (seen[key]) return; seen[key] = true;
      var isA = p.id === activeRoute;
      var orbR = p.orb * maxOrbR;
      ctx.beginPath();
      ctx.ellipse(sx, sy, orbR, orbR * TILT, 0, 0, Math.PI*2);
      ctx.strokeStyle = isA ? 'rgba(120,200,255,0.24)' : 'rgba(90,150,230,0.07)';
      ctx.lineWidth   = isA ? 0.65 : 0.30;
      ctx.stroke();
    });
    ctx.setLineDash([]);
  }

  function drawPlanet(x, y, p, isA, t) {
    var scale = Math.max(0.75, Math.min(usableH() / 560, 1.25));
    var sz = p.sz * scale;

    /* update ion trail */
    if (p.label) updateIonTrail(p.id, x, y);

    /* ── PLANETARY RING (for vega + civil only) ── */
    if (p.id === 'vega' || p.id === 'civil') {
      var rx = sz * (p.id==='vega' ? 3.2 : 2.6);
      var ry = rx * 0.22;
      ctx.save();
      ctx.globalCompositeOperation = 'screen';
      ctx.translate(x, y); ctx.rotate(-0.12);
      var rg = ctx.createLinearGradient(-rx, 0, rx, 0);
      rg.addColorStop(0,   'rgba(0,0,0,0)');
      rg.addColorStop(0.25, p.glow+(isA?'0.25':'0.12')+')');
      rg.addColorStop(0.5, p.glow+(isA?'0.40':'0.20')+')');
      rg.addColorStop(0.75,p.glow+(isA?'0.25':'0.12')+')');
      rg.addColorStop(1,   'rgba(0,0,0,0)');
      ctx.beginPath(); ctx.ellipse(0, 0, rx, ry, 0, 0, Math.PI*2);
      ctx.strokeStyle = rg;
      ctx.lineWidth = isA ? 1.4 : 0.70;
      ctx.stroke();
      /* inner ring */
      ctx.beginPath(); ctx.ellipse(0, 0, rx*0.80, ry*0.80, 0, 0, Math.PI*2);
      ctx.strokeStyle = p.glow+(isA?'0.15':'0.06')+')';
      ctx.lineWidth = 0.40; ctx.stroke();
      ctx.restore();
    }

    if (p.atm) {
      var atmA = isA ? 0.24 : 0.10;
      var atmR = sz * 2.8 + (isA ? 6 : 0);
      var atm = ctx.createRadialGradient(x, y, sz*0.5, x, y, atmR);
      atm.addColorStop(0, p.atm + atmA + ')');
      atm.addColorStop(0.6, p.atm+(atmA*0.3)+')');
      atm.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.beginPath(); ctx.arc(x, y, atmR, 0, Math.PI*2);
      ctx.fillStyle = atm; ctx.fill();
    }

    if (p.glow) {
      ctx.globalCompositeOperation = 'screen';
      var pulse = isA ? (1 + Math.sin(t*0.0012)*0.12) : 1;
      /* outer soft glow */
      var glowR2 = sz * (isA ? 5.0 : 3.2) * pulse;
      var gr2 = ctx.createRadialGradient(x, y, sz*1.2, x, y, glowR2);
      gr2.addColorStop(0, p.glow + (isA ? '0.18' : '0.06') + ')');
      gr2.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.beginPath(); ctx.arc(x, y, glowR2, 0, Math.PI*2);
      ctx.fillStyle = gr2; ctx.fill();
      /* inner tight glow */
      var glowR = sz * (isA ? 3.4 : 2.2) * pulse;
      var gr = ctx.createRadialGradient(x, y, sz*0.8, x, y, glowR);
      gr.addColorStop(0,   p.glow + (isA ? '0.50' : '0.20') + ')');
      gr.addColorStop(0.4, p.glow + (isA ? '0.14' : '0.06') + ')');
      gr.addColorStop(1,   'rgba(0,0,0,0)');
      ctx.beginPath(); ctx.arc(x, y, glowR, 0, Math.PI*2);
      ctx.fillStyle = gr; ctx.fill();
      ctx.globalCompositeOperation = 'source-over';
    }

    var body = ctx.createRadialGradient(x - sz*0.28, y - sz*0.26, 0, x + sz*0.08, y + sz*0.08, sz*1.06);
    body.addColorStop(0,    p.c0);
    body.addColorStop(0.45, p.c1);
    body.addColorStop(1,    p.c2);
    ctx.beginPath(); ctx.arc(x, y, sz, 0, Math.PI*2);
    ctx.fillStyle = body; ctx.fill();

    ctx.globalCompositeOperation = 'screen';
    var vein = ctx.createRadialGradient(x - sz*0.20, y - sz*0.20, 0, x - sz*0.05, y - sz*0.05, sz*0.65);
    vein.addColorStop(0, p.glow ? p.glow + '0.35)' : 'rgba(255,255,255,0.20)');
    vein.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.beginPath(); ctx.arc(x, y, sz, 0, Math.PI*2);
    ctx.fillStyle = vein; ctx.fill();
    ctx.globalCompositeOperation = 'source-over';

    var limb = ctx.createRadialGradient(x, y, sz*0.10, x, y, sz*1.05);
    limb.addColorStop(0,   'rgba(0,0,0,0)');
    limb.addColorStop(0.5, 'rgba(0,0,0,0.18)');
    limb.addColorStop(1,   'rgba(0,0,0,0.80)');
    ctx.beginPath(); ctx.arc(x, y, sz, 0, Math.PI*2);
    ctx.fillStyle = limb; ctx.fill();

    if (p.label) {
      var fs = Math.max(7, Math.round(sz * 0.85));
      ctx.save();
      if (isA) {
        ctx.globalCompositeOperation = 'screen';
        ctx.shadowColor = p.glow ? p.glow + '0.80)' : 'rgba(0,255,160,0.80)';
        ctx.shadowBlur = 8;
        ctx.fillStyle = p.c0;
      } else {
        ctx.fillStyle = 'rgba(120,190,160,0.35)';
      }
      ctx.font = '500 '+fs+'px "DM Mono",monospace';
      ctx.textAlign = 'center'; ctx.textBaseline = 'top';
      ctx.fillText(p.label, x, y + sz + 3);
      ctx.restore();
    }
  }

  function drawDiademRing(t) {
    var sx = SX(), sy = SY(), R = SR();
    var rx = R * 5.4, ry = R * 1.55;
    var pulse = 1 + Math.sin(t * 0.0006) * 0.05;
    ctx.save();
    ctx.translate(sx, sy);
    ctx.rotate(-0.16);
    ctx.globalCompositeOperation = 'lighter';
    ctx.lineWidth = 1.1;
    ctx.beginPath();
    ctx.ellipse(0, 0, rx * pulse, ry * pulse, 0, Math.PI * 0.5, Math.PI * 1.5);
    ctx.strokeStyle = 'rgba(120,190,255,0.20)';
    ctx.stroke();
    ctx.beginPath();
    ctx.ellipse(0, 0, rx * pulse, ry * pulse, 0, -Math.PI * 0.5, Math.PI * 0.5);
    ctx.strokeStyle = 'rgba(255,190,110,0.20)';
    ctx.stroke();
    ctx.globalCompositeOperation = 'source-over';
    ctx.restore();
  }

  function drawPlanets(dt, t) {
    var sx = SX(), sy = SY();
    var maxOrbR = Math.min(W - SX() - 16, usableH() / (TILT * 2) - 16);
    var left = UI_LEFT(), top = UI_TOP(), bottom = H - UI_BOTTOM();
    var items = PLANETS.map(function (p) {
      p.ang += p.spd * dt * 60;
      var orb = p.orb * maxOrbR;
      return { p:p, x: sx + Math.cos(p.ang)*orb, y: sy + Math.sin(p.ang)*orb*TILT };
    }).sort(function (a, b) { return a.y - b.y; });
    items.forEach(function (item) {
      if (item.x < left - 30 || item.x > W+30) return;
      if (item.y < top - 30 || item.y > bottom + 30) return;
      drawPlanet(item.x, item.y, item.p, item.p.id === activeRoute, t);
    });
  }

  var _S = { thinking: false };

  function drawSun(t) {
    var sx = SX(), sy = SY(), R = SR();
    var gm = _S.thinking ? 1 + Math.sin(t*0.005)*0.28 : 1;

    ctx.globalCompositeOperation = 'lighter';

    /* ── 5 corona rings (v32: more) ── */
    for (var ring = 5; ring >= 1; ring--) {
      var rAl = (0.018 / ring) * gm;
      var rR = R * (3.5 + ring * 3.8);
      ctx.beginPath(); ctx.arc(sx, sy, rR, 0, Math.PI*2);
      ctx.strokeStyle = 'rgba(110,190,255,'+rAl+')';
      ctx.lineWidth = 0.38;
      ctx.stroke();
    }

    /* ── thinking burst rings ── */
    if (_S.thinking) {
      for (var b = 0; b < 3; b++) {
        var bPhase = (t * 0.003 + b * 1.0) % (Math.PI * 2);
        var bR = R * (2 + b * 4 + Math.sin(bPhase) * 2);
        var bAl = Math.max(0, Math.sin(bPhase) * 0.25);
        ctx.beginPath(); ctx.arc(sx, sy, bR, 0, Math.PI*2);
        ctx.strokeStyle = 'rgba(255,220,80,'+bAl+')';
        ctx.lineWidth = 0.6; ctx.stroke();
      }
    }

    var fc = ctx.createRadialGradient(sx, sy, R*0.10, sx, sy, R*11);
    fc.addColorStop(0,    'rgba(255,200,60,'+(0.32*gm)+')');
    fc.addColorStop(0.15, 'rgba(255,140,20,'+(0.13*gm)+')');
    fc.addColorStop(0.40, 'rgba(90,170,255,'+(0.06*gm)+')');
    fc.addColorStop(0.70, 'rgba(40,70,150,'+(0.02*gm)+')');
    fc.addColorStop(1,    'rgba(0,0,0,0)');
    ctx.beginPath();
    ctx.ellipse(sx, sy, R*11, R*3.8, 0, 0, Math.PI*2);
    ctx.fillStyle = fc; ctx.fill();

    /* ── 16 rays (v32: more) ── */
    ctx.save(); ctx.translate(sx, sy); ctx.rotate(t*0.000018);
    for (var i = 0; i < 16; i++) {
      var a = (i/16)*Math.PI*2;
      var rl = R * (1.9 + 0.30*Math.sin(i*1.8 + t*0.00014)) * gm;
      var gr = ctx.createLinearGradient(
        Math.cos(a)*R*0.20, Math.sin(a)*R*0.20,
        Math.cos(a)*rl, Math.sin(a)*rl);
      gr.addColorStop(0,    'rgba(255,200,50,'+(0.30*gm)+')');
      gr.addColorStop(0.5,  'rgba(200,120,10,0.06)');
      gr.addColorStop(1,    'rgba(0,0,0,0)');
      ctx.strokeStyle = gr; ctx.lineWidth = 0.65;
      ctx.beginPath();
      ctx.moveTo(Math.cos(a)*R*0.20, Math.sin(a)*R*0.20);
      ctx.lineTo(Math.cos(a)*rl, Math.sin(a)*rl);
      ctx.stroke();
    }
    ctx.restore();

    var ih = ctx.createRadialGradient(sx, sy, R*0.25, sx, sy, R*2.5);
    ih.addColorStop(0,    'rgba(255,240,150,0.95)');
    ih.addColorStop(0.25, 'rgba(255,190,50,0.65)');
    ih.addColorStop(0.60, 'rgba(200,90,10,0.22)');
    ih.addColorStop(1,    'rgba(0,0,0,0)');
    ctx.beginPath(); ctx.arc(sx, sy, R*2.5, 0, Math.PI*2);
    ctx.fillStyle = ih; ctx.fill();

    ctx.globalCompositeOperation = 'source-over';

    var body = ctx.createRadialGradient(sx - R*0.22, sy - R*0.22, 0, sx, sy, R);
    body.addColorStop(0,    '#fffad0');
    body.addColorStop(0.25, '#ffdd40');
    body.addColorStop(0.65, '#e06800');
    body.addColorStop(1,    '#5c1e00');
    ctx.beginPath(); ctx.arc(sx, sy, R, 0, Math.PI*2);
    ctx.fillStyle = body; ctx.fill();

    var spec = ctx.createRadialGradient(sx - R*0.34, sy - R*0.34, 0, sx - R*0.16, sy - R*0.16, R*0.54);
    spec.addColorStop(0, 'rgba(255,252,230,0.55)');
    spec.addColorStop(1, 'rgba(255,252,230,0)');
    ctx.beginPath(); ctx.arc(sx, sy, R, 0, Math.PI*2);
    ctx.fillStyle = spec; ctx.fill();

    var limb = ctx.createRadialGradient(sx, sy, R*0.15, sx, sy, R*1.05);
    limb.addColorStop(0,   'rgba(0,0,0,0)');
    limb.addColorStop(0.5, 'rgba(0,0,0,0.15)');
    limb.addColorStop(1,   'rgba(0,0,0,0.75)');
    ctx.beginPath(); ctx.arc(sx, sy, R, 0, Math.PI*2);
    ctx.fillStyle = limb; ctx.fill();

    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    ctx.shadowColor = 'rgba(255,200,60,0.90)'; ctx.shadowBlur = 10;
    ctx.fillStyle = 'rgba(255,240,140,0.95)';
    var lfs = Math.max(8, Math.round(R*0.62));
    ctx.font = '600 '+lfs+'px "DM Mono",monospace';
    ctx.textAlign = 'center'; ctx.textBaseline = 'bottom';
    ctx.fillText('LYLA \u25c6', sx, sy - R - 3);
    ctx.restore();
  }

  function drawAxiom() {
    ctx.save();
    ctx.font = '300 7px "DM Mono",monospace';
    ctx.fillStyle = 'rgba(150,205,255,0.16)';
    ctx.textAlign = 'left'; ctx.textBaseline = 'bottom';
    ctx.fillText('Choice(t) >= 1  ->  collapse = False', UI_LEFT()+12, H - UI_BOTTOM() - 6);
    ctx.restore();
  }
  function drawBadge() {
    ctx.save();
    ctx.font = '400 5px "DM Mono",monospace';
    ctx.fillStyle = 'rgba(150,205,255,0.10)';
    ctx.textAlign = 'right'; ctx.textBaseline = 'bottom';
    ctx.fillText('FATE  DETERMINISTIC DECISION INFRASTRUCTURE  v32', W-8, H - UI_BOTTOM() - 6);
    ctx.restore();
  }

  function loop(ts) {
    if (!lastTime) lastTime = ts;
    var dt = Math.min((ts - lastTime) / 1000, 0.05);
    lastTime = ts;
    try {
      drawBg(ts);
      drawStars(ts);
      drawDustMotes(ts);
      drawFateTexts(dt, ts);
      drawMeteors(ts, dt);
      drawComet(ts, dt);
      drawIonTrails();
      drawOrbits();
      drawDiademRing(ts);
      drawPlanets(dt, ts);
      drawSun(ts);
      drawShockwave(dt);
      drawAxiom();
      drawBadge();
    } catch (e) {
      console.error('[galaxy_scene] frame error:', e);
    }
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);

  window.LYLA_thinking  = function () { _S.thinking = true; };
  window.LYLA_answered  = function () { _S.thinking = false; };
  window.KD_pulse       = function (r) {
    _S.thinking = false;
    if (r && r !== activeRoute) {
      /* shockwave on route change */
      var p = PLANETS.find(function(pl){ return pl.id === r; });
      if (p) {
        var sx=SX(), sy=SY(), mR=Math.min(W-SX()-16, usableH()/(TILT*2)-16);
        var orb=p.orb*mR;
        triggerShockwave(
          sx + Math.cos(p.ang)*orb,
          sy + Math.sin(p.ang)*orb*TILT,
          p.glow ? p.glow.replace('rgba(','').replace(',','').split(',').slice(0,3).join(',') : '120,200,255'
        );
      }
      activeRoute = r;
    }
  };
  window.KD_setRoute    = function (r) { activeRoute = r; };
  window.KD_council     = function () { _S.thinking = true; };
  window.KD_councilEnd  = function () { _S.thinking = false; };
  window.KD_shockwave   = function (x, y, col) { triggerShockwave(x, y, col); };
  window.KD.safeVal     = function (v, d) {
    var n = +v, dec = typeof d === 'number' ? d : 2;
    return (isFinite(n) && !isNaN(n)) ? n.toFixed(dec) : '0.00';
  };
})();
