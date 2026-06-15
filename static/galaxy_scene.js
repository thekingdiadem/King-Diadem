/* ============================================================
   KING DIADEM — galaxy_scene.js v31
   OTHERWORLDLY — Living Decision Membrane (Safe-Zone Edition)
   Bioluminescent planets | Aurora filaments | FATE Doc layer
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
  }

  function buildFilaments() {
    FILAMENTS = [];
    var count = W < 500 ? 4 : 7;
    for (var i = 0; i < count; i++) {
      FILAMENTS.push({
        x: Math.random() * W,
        y: Math.random() * H,
        w: W * (0.18 + Math.random() * 0.35),
        h: H * (0.06 + Math.random() * 0.12),
        angle: -0.3 + Math.random() * 0.6,
        hue: (Math.random() < 0.45) ? 208 : (Math.random() < 0.78 ? 278 : 36),
        alpha: 0.03 + Math.random() * 0.055,
        speed: 0.000008 + Math.random() * 0.000012,
        phase: Math.random() * Math.PI * 2,
      });
    }
  }

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

    var bg = ctx.createLinearGradient(0, 0, W, H);
    bg.addColorStop(0,    '#05070f');
    bg.addColorStop(0.30, '#070b1e');
    bg.addColorStop(0.65, '#0a0a16');
    bg.addColorStop(1,    '#04050c');
    ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);

    ctx.globalCompositeOperation = 'screen';

    for (var i = 0; i < FILAMENTS.length; i++) {
      var f = FILAMENTS[i];
      var breathe = Math.sin(t * f.speed + f.phase);
      var al = f.alpha * (0.7 + 0.3 * breathe);
      var cx = f.x + Math.sin(t * f.speed * 0.7 + f.phase) * W * 0.04;
      var cy = f.y + Math.cos(t * f.speed * 0.5 + f.phase) * H * 0.03;
      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate(f.angle);
      var n = ctx.createRadialGradient(0, 0, 0, 0, 0, f.w * 0.5);
      var h = f.hue;
      n.addColorStop(0,   'hsla('+h+',100%,70%,'+al+')');
      n.addColorStop(0.5, 'hsla('+h+',80%,50%,'+(al*0.4)+')');
      n.addColorStop(1,   'hsla('+h+',60%,30%,0)');
      ctx.beginPath();
      ctx.ellipse(0, 0, f.w * 0.5, f.h * 0.5, 0, 0, Math.PI*2);
      ctx.fillStyle = n; ctx.fill();
      ctx.restore();
    }

    var sx = SX(), sy = SY();
    var sunHalo = ctx.createRadialGradient(sx, sy, SR()*0.5, sx, sy, Math.max(W,H)*0.55);
    sunHalo.addColorStop(0,   'rgba(255,140,20,0.30)');
    sunHalo.addColorStop(0.4, 'rgba(180,80,0,0.12)');
    sunHalo.addColorStop(1,   'rgba(0,0,0,0)');
    ctx.beginPath(); ctx.ellipse(sx, sy, Math.max(W,H)*0.55, Math.max(W,H)*0.55, 0, 0, Math.PI*2);
    ctx.fillStyle = sunHalo; ctx.fill();

    var farVoid = ctx.createRadialGradient(W*0.92, H*0.50, 0, W*0.92, H*0.50, W*0.40);
    farVoid.addColorStop(0,   'rgba(25,40,90,0.42)');
    farVoid.addColorStop(1,   'rgba(0,0,0,0)');
    ctx.beginPath(); ctx.ellipse(W*0.92, H*0.50, W*0.40, H*0.80, 0, 0, Math.PI*2);
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

    if (p.atm) {
      var atmA = isA ? 0.22 : 0.10;
      var atmR = sz * 2.6 + (isA ? 5 : 0);
      var atm = ctx.createRadialGradient(x, y, sz*0.5, x, y, atmR);
      atm.addColorStop(0, p.atm + atmA + ')');
      atm.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.beginPath(); ctx.arc(x, y, atmR, 0, Math.PI*2);
      ctx.fillStyle = atm; ctx.fill();
    }

    if (p.glow) {
      ctx.globalCompositeOperation = 'screen';
      var pulse = isA ? (1 + Math.sin(t*0.0012)*0.10) : 1;
      var glowR = sz * (isA ? 3.2 : 2.2) * pulse;
      var gr = ctx.createRadialGradient(x, y, sz*0.8, x, y, glowR);
      gr.addColorStop(0,   p.glow + (isA ? '0.45' : '0.18') + ')');
      gr.addColorStop(0.4, p.glow + (isA ? '0.12' : '0.05') + ')');
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
        ctx.shadowBlur = 6;
        ctx.fillStyle = p.c0;
      } else {
        ctx.fillStyle = 'rgba(120,200,160,0.40)';
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
    var gm = _S.thinking ? 1 + Math.sin(t*0.005)*0.20 : 1;

    ctx.globalCompositeOperation = 'lighter';

    for (var ring = 3; ring >= 1; ring--) {
      var rAl = (0.022 / ring) * gm;
      var rR = R * (4 + ring * 3.5);
      ctx.beginPath(); ctx.arc(sx, sy, rR, 0, Math.PI*2);
      ctx.strokeStyle = 'rgba(110,190,255,'+rAl+')';
      ctx.lineWidth = 0.40;
      ctx.stroke();
    }

    var fc = ctx.createRadialGradient(sx, sy, R*0.10, sx, sy, R*10);
    fc.addColorStop(0,    'rgba(255,200,60,'+(0.30*gm)+')');
    fc.addColorStop(0.15, 'rgba(255,140,20,'+(0.12*gm)+')');
    fc.addColorStop(0.40, 'rgba(90,170,255,'+(0.06*gm)+')');
    fc.addColorStop(0.70, 'rgba(40,70,150,'+(0.02*gm)+')');
    fc.addColorStop(1,    'rgba(0,0,0,0)');
    ctx.beginPath();
    ctx.ellipse(sx, sy, R*10, R*3.5, 0, 0, Math.PI*2);
    ctx.fillStyle = fc; ctx.fill();

    ctx.save(); ctx.translate(sx, sy); ctx.rotate(t*0.000018);
    for (var i = 0; i < 12; i++) {
      var a = (i/12)*Math.PI*2;
      var rl = R * (1.9 + 0.28*Math.sin(i*1.8 + t*0.00014)) * gm;
      var gr = ctx.createLinearGradient(
        Math.cos(a)*R*0.20, Math.sin(a)*R*0.20,
        Math.cos(a)*rl, Math.sin(a)*rl);
      gr.addColorStop(0,    'rgba(255,200,50,'+(0.28*gm)+')');
      gr.addColorStop(0.5,  'rgba(200,120,10,0.06)');
      gr.addColorStop(1,    'rgba(0,0,0,0)');
      ctx.strokeStyle = gr; ctx.lineWidth = 0.70;
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
    ctx.fillText('FATE  DETERMINISTIC DECISION INFRASTRUCTURE  v31', W-8, H - UI_BOTTOM() - 6);
    ctx.restore();
  }

  function loop(ts) {
    if (!lastTime) lastTime = ts;
    var dt = Math.min((ts - lastTime) / 1000, 0.05);
    lastTime = ts;
    try {
      drawBg(ts);
      drawStars(ts);
      drawFateTexts(dt, ts);
      drawComet(ts, dt);
      drawOrbits();
      drawDiademRing(ts);
      drawPlanets(dt, ts);
      drawSun(ts);
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
  window.KD_pulse       = function (r) { _S.thinking = false; if (r) activeRoute = r; };
  window.KD_setRoute    = function (r) { activeRoute = r; };
  window.KD_council     = function () { _S.thinking = true; };
  window.KD_councilEnd  = function () { _S.thinking = false; };
  window.KD.safeVal     = function (v, d) {
    var n = +v, dec = typeof d === 'number' ? d : 2;
    return (isFinite(n) && !isNaN(n)) ? n.toFixed(dec) : '0.00';
  };
})();
