/* ============================================================
   KING DIADEM — galaxy_scene.js v35
   FULL COSMIC ENGINE
   - Live STATE sync (entropy/stability/resources → visual)
   - Planet speed scales with entropy
   - Gravitational lensing on active planet
   - Black hole mode (waterline < 20)
   - Click planet → shockwave + route change
   - Particle explosion on route change
   - Performance: skip heavy fx on low-end devices
   - Solar flare eruptions
   - Wormhole pulse between Sun and active planet
   - Nebula color shifts with route
   - Comet + meteor shower (preserved)
   - Fate texts (preserved)
   - Full public API
   ============================================================ */
(function () {
  'use strict';

  var cv = document.getElementById('galaxy');
  if (!cv) return;
  if (!window.KD) window.KD = {};

  var ctx = cv.getContext('2d', { alpha: true });
  var W = 0, H = 0, lastTime = 0;
  var activeRoute = 'general';
  var FPS_LOW = false; // auto-detected low-end device flag

  cv.style.cssText = 'display:block;position:absolute;inset:0;width:100%;height:100%;cursor:pointer;';

  /* ── SAFE ZONE ─────────────────────────────────── */
  function isDesktop() { return W >= 900; }
  function UI_LEFT()   { return isDesktop() ? 252 : 0; }
  function UI_TOP()    { return 52; }
  function UI_BOTTOM() { return isDesktop() ? 92 : 132; }
  function usableW()   { return Math.max(160, W - UI_LEFT()); }
  function usableH()   { return Math.max(160, H - UI_TOP() - UI_BOTTOM()); }
  function SX() { return UI_LEFT() + usableW() * 0.42; }
  function SY() { return UI_TOP()  + usableH() * 0.50; }
  function sunR() { return Math.max(10, Math.min(usableH() * 0.048, 20)); }
  function maxOrb() { return Math.min(usableW() * 0.46, usableH() * 0.46); }

  /* ── LIVE STATE ────────────────────────────────── */
  var STATE = {
    entropy:     45,
    stability:   62,
    resources:   78,
    waterline:   89,
    choice_count: 4,
    thinking:    false,
    activeRoute: 'general',
    blackHole:   false,
    flareCharge: 0,
  };

  function updateWaterline() {
    var danger = (STATE.entropy * 0.33)
               + (100 - STATE.stability) * 0.33
               + (100 - STATE.resources) * 0.34;
    STATE.waterline  = Math.max(0, Math.min(100, 100 - danger));
    STATE.blackHole  = STATE.waterline < 20;
  }

  function syncStateFromHTML() {
    var eE = document.querySelector('[data-state="entropy"]');
    var sE = document.querySelector('[data-state="stability"]');
    var rE = document.querySelector('[data-state="resources"]');
    var cE = document.querySelector('[data-state="choice_count"]');
    if (eE) STATE.entropy      = parseFloat(eE.textContent)  || STATE.entropy;
    if (sE) STATE.stability    = parseFloat(sE.textContent)  || STATE.stability;
    if (rE) STATE.resources    = parseFloat(rE.textContent)  || STATE.resources;
    if (cE) STATE.choice_count = parseInt(cE.textContent)    || STATE.choice_count;
    updateWaterline();
  }

  function updateHTMLDisplay() {
    var wlFloat = document.getElementById('wl-float');
    if (wlFloat) {
      var st = STATE.waterline > 60 ? 'SAFE' : STATE.waterline > 30 ? 'WARN' : 'CRIT';
      wlFloat.innerHTML =
        '<span class="wl-dot">WATERLINE ' + Math.round(STATE.waterline) + '</span>' +
        '<span class="wl-dot">' + st + '</span>';
    }
  }

  /* ── FPS MONITOR ────────────────────────────────── */
  var _fpsFrames = 0, _fpsLast = 0;
  function monitorFPS(ts) {
    _fpsFrames++;
    if (ts - _fpsLast > 2000) {
      var fps = _fpsFrames / ((ts - _fpsLast) / 1000);
      FPS_LOW = fps < 28;
      _fpsFrames = 0; _fpsLast = ts;
    }
  }

  /* ── RESIZE ────────────────────────────────────── */
  var _rT;
  function doResize() {
    W = cv.width  = window.innerWidth;
    H = cv.height = window.innerHeight;
    buildStars(); buildFilaments(); buildAurora(); buildDustMotes();
  }
  window.addEventListener('resize', function(){ clearTimeout(_rT); _rT = setTimeout(doResize, 60); }, { passive:true });
  window.addEventListener('orientationchange', function(){ clearTimeout(_rT); _rT = setTimeout(doResize, 160); }, { passive:true });
  doResize();

  /* ── ROUTE COLOR MAP ────────────────────────────── */
  var ROUTE_NEBULA_HUE = {
    general:  208,
    risk:     10,
    survival: 36,
    collapse: 28,
    civil:    168,
    vega:     258,
  };
  var _currentNebulaHue = 208, _targetNebulaHue = 208;

  /* ── PLANET DEFINITIONS ─────────────────────────── */
  var PDEFS = [
    { id:'a1',       label:null,       orb:0.13, spd:0.00028, ang:0.80,
      sz:2.0, c0:'#c8c0b8', c1:'#706860', c2:'#1e1a18', glow:'rgba(200,190,175,', atm:null },
    { id:'a2',       label:null,       orb:0.20, spd:0.00022, ang:2.10,
      sz:3.2, c0:'#f0d890', c1:'#b89030', c2:'#2a1e04', glow:'rgba(230,200,100,', atm:'rgba(220,180,80,' },
    { id:'general',  label:'GENERAL',  orb:0.28, spd:0.00016, ang:3.60,
      sz:4.8, c0:'#78c8f8', c1:'#1a6eca', c2:'#05152e', glow:'rgba(80,160,255,', atm:'rgba(60,140,240,' },
    { id:'risk',     label:'RISK',     orb:0.37, spd:0.00011, ang:5.20,
      sz:3.8, c0:'#e87848', c1:'#a03818', c2:'#220a02', glow:'rgba(230,100,60,', atm:'rgba(200,70,30,' },
    { id:'survival', label:'SURVIVAL', orb:0.50, spd:0.00006,  ang:1.40,
      sz:7.5, c0:'#e8c880', c1:'#b87820', c2:'#1e0e00', glow:'rgba(200,160,60,', atm:'rgba(180,130,40,', bands:true },
    { id:'collapse', label:'COLLAPSE', orb:0.62, spd:0.00004,  ang:4.00,
      sz:6.2, c0:'#d8c090', c1:'#987040', c2:'#1a1004', glow:'rgba(200,170,90,', atm:'rgba(170,140,60,', rings:true },
    { id:'civil',    label:'CIVIL',    orb:0.76, spd:0.000025, ang:0.50,
      sz:5.0, c0:'#80e8e0', c1:'#289898', c2:'#021e1e', glow:'rgba(80,220,210,', atm:'rgba(60,200,190,' },
    { id:'vega',     label:'VEGA',     orb:0.91, spd:0.000016, ang:2.80,
      sz:4.8, c0:'#6898e8', c1:'#2838b8', c2:'#020416', glow:'rgba(100,140,240,', atm:'rgba(80,110,220,', storm:true },
  ];
  var PLANETS = PDEFS.map(function(d){ return Object.assign({ang:0}, d); });

  /* ── ION TRAILS ───────────────────────────────── */
  var ION_TRAILS = {};
  PLANETS.forEach(function(p){ if(p.label) ION_TRAILS[p.id] = []; });
  function updateIonTrail(pid, x, y) {
    if (!ION_TRAILS[pid]) return;
    ION_TRAILS[pid].push({ x:x, y:y });
    if (ION_TRAILS[pid].length > 40) ION_TRAILS[pid].shift();
  }

  /* ── PARTICLE EXPLOSIONS ─────────────────────── */
  var PARTICLES = [];
  function spawnExplosion(x, y, col, n) {
    n = n || 40;
    for (var i = 0; i < n; i++) {
      var angle = Math.random() * Math.PI * 2;
      var speed = 0.4 + Math.random() * 2.8;
      PARTICLES.push({
        x:x, y:y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        r: 0.4 + Math.random() * 2.2,
        alpha: 0.7 + Math.random() * 0.3,
        decay: 0.012 + Math.random() * 0.022,
        col: col || '120,200,255',
        grav: 0.008 + Math.random() * 0.012,
      });
    }
  }

  /* ── SOLAR FLARES ─────────────────────────────── */
  var FLARES = [];
  var nextFlare = 8000;
  function spawnFlare(sx, sy, R) {
    var angle = Math.random() * Math.PI * 2;
    var len   = R * (2.2 + Math.random() * 3.5);
    FLARES.push({
      angle: angle, len: len,
      sx: sx, sy: sy, R: R,
      life: 0, maxLife: 0.8 + Math.random() * 1.4,
      width: 0.5 + Math.random() * 1.2,
      col: Math.random() < 0.6 ? '255,160,40' : '255,220,80',
    });
  }

  /* ── WORMHOLE ─────────────────────────────────── */
  var WORMHOLE = { active: false, progress: 0, fromX:0, fromY:0, toX:0, toY:0, alpha:0 };
  var nextWormhole = 20000;

  /* ── GRAVITATIONAL LENSING ───────────────────── */
  // Rendered as distortion rings around active planet
  var LENS_RINGS = 3;

  /* ── STARS ────────────────────────────────────── */
  var STARS = [];
  function buildStars() {
    STARS = [];
    for (var i = 0; i < 2200; i++)
      STARS.push({ x:Math.random()*W, y:Math.random()*H,
        r:0.05+Math.random()*0.20, a:0.06+Math.random()*0.22,
        col:Math.random()>0.5?'170,205,255':'205,185,255', tw:false });
    for (var j = 0; j < 300; j++)
      STARS.push({ x:Math.random()*W, y:Math.random()*H,
        r:0.14+Math.random()*0.30, a:0.18+Math.random()*0.28,
        col:Math.random()>0.5?'145,205,255':'195,155,255',
        tw:true, tS:0.00008+Math.random()*0.00015, tO:Math.random()*Math.PI*2 });
    for (var k = 0; k < 55; k++) {
      var rr = Math.random();
      STARS.push({ x:Math.random()*W, y:Math.random()*H,
        r:0.38+Math.random()*0.60, a:0.38+Math.random()*0.40,
        col:rr<0.42?'130,195,255':(rr<0.80?'200,150,255':'255,205,130'),
        tw:true, tS:0.00004+Math.random()*0.00009, tO:Math.random()*Math.PI*2, bloom:true });
    }
  }

  /* ── NEBULA FILAMENTS ─────────────────────────── */
  var FILAMENTS = [];
  function buildFilaments() {
    FILAMENTS = [];
    var n = W < 500 ? 5 : 10;
    for (var i = 0; i < n; i++) {
      FILAMENTS.push({
        x:Math.random()*W, y:Math.random()*H,
        w:W*(0.14+Math.random()*0.42), h:H*(0.04+Math.random()*0.16),
        angle:-0.5+Math.random()*1.0,
        hue:_currentNebulaHue + (Math.random()-0.5)*40,
        alpha:0.018+Math.random()*0.048,
        speed:0.000004+Math.random()*0.000012,
        phase:Math.random()*Math.PI*2,
      });
    }
  }

  /* ── AURORA ───────────────────────────────────── */
  var AURORA = [];
  function buildAurora() {
    AURORA = [];
    var n = W < 600 ? 2 : 4;
    for (var i = 0; i < n; i++) {
      var segs = 16+Math.floor(Math.random()*12), pts = [];
      for (var j = 0; j <= segs; j++)
        pts.push({ x:(j/segs)*W, dy:0, dv:(Math.random()-0.5)*0.08 });
      AURORA.push({
        pts:pts, baseY:H*(0.05+Math.random()*0.28), height:H*(0.05+Math.random()*0.10),
        hue:Math.random()<0.5?165+Math.random()*30:210+Math.random()*40,
        alpha:0.010+Math.random()*0.018, speed:0.000004+Math.random()*0.000008,
        phase:Math.random()*Math.PI*2,
      });
    }
  }

  /* ── DUST MOTES ───────────────────────────────── */
  var DUST_MOTES = [];
  function buildDustMotes() {
    DUST_MOTES = [];
    var n = W < 600 ? 50 : 120;
    for (var i = 0; i < n; i++) {
      DUST_MOTES.push({
        x:Math.random()*W, y:Math.random()*H,
        vx:(Math.random()-0.5)*0.009, vy:(Math.random()-0.5)*0.005,
        r:0.3+Math.random()*0.9, a:0.03+Math.random()*0.08,
        col:Math.random()<0.6?'130,190,255':'180,140,255',
        tS:0.00010+Math.random()*0.00020, tO:Math.random()*Math.PI*2,
      });
    }
  }

  /* ── SHOCKWAVE ────────────────────────────────── */
  var SHOCKWAVES = [];
  function triggerShockwave(x, y, col, big) {
    SHOCKWAVES.push({
      x:x, y:y, r:0,
      maxR: Math.min(W,H) * (big ? 0.55 : 0.32),
      alpha: big ? 0.80 : 0.55,
      col: col || '120,200,255',
    });
    if (SHOCKWAVES.length > 6) SHOCKWAVES.shift();
  }

  /* ── COMET ────────────────────────────────────── */
  var COMET = { active:false, x:0, y:0, vx:0, vy:0, life:0, maxLife:0 };
  var nextComet = 14000;

  /* ── METEORS ──────────────────────────────────── */
  var METEORS = [], meteorActive = false, meteorEnd = 0, nextMeteor = 10000;

  /* ── ASTEROID BELT ───────────────────────────── */
  var ASTEROIDS = (function() {
    var belt = [];
    for (var i = 0; i < 180; i++) {
      belt.push({
        frac:0.42+Math.random()*0.06, ang:Math.random()*Math.PI*2,
        spd:0.000008+Math.random()*0.000005, r:0.3+Math.random()*0.9,
        a:0.06+Math.random()*0.18, scatter:(Math.random()-0.5)*0.025
      });
    }
    return belt;
  })();

  /* ── FATE TEXTS ───────────────────────────────── */
  var CANON = [
    'Logic over Persona.',
    'Rule over Authority.',
    'Downside before Upside.',
    'Human retains\nfinal authority.',
    'Fail less.\nHarm less.\nRestore more.',
    'Choice(t) >= 1\ncollapse = False',
    'ไม่ได้สร้างมาเพื่อชนะทุกครั้ง\nสร้างมาเพื่อไม่พังแบบเดิมอีกครั้ง',
    'Stay simple long enough\nto outlive the impossible.',
    'The crown belongs to no one.\nChoice itself is the crown.',
    'ปฏิจสมุปบาท —\nทุกอย่างเกิดจากเหตุปัจจัย',
    'Structure before action.',
    'กฎมีไว้จำกัดอำนาจ\nไม่ใช่ขยายอำนาจ',
  ];
  var FATE_TEXTS = [];
  function spawnFateText() {
    var text = CANON[Math.floor(Math.random()*CANON.length)];
    var lines = text.split('\n'), left = UI_LEFT();
    return {
      lines:lines,
      x:left+(W-left)*(0.18+Math.random()*0.64),
      y:UI_TOP()+usableH()*(0.12+Math.random()*0.74),
      alpha:0, maxAlpha:0.040+Math.random()*0.038,
      state:'in', lifeIn:2400+Math.random()*1600,
      lifeHold:4200+Math.random()*5000, lifeOut:2200+Math.random()*1400,
      age:0, size:W<500?7+Math.random()*2.5:8.5+Math.random()*3.5,
    };
  }
  function initFateTexts() {
    FATE_TEXTS = [];
    for (var i = 0; i < (W<500?3:5); i++) {
      var ft = spawnFateText();
      ft.age = Math.random()*(ft.lifeIn+ft.lifeHold);
      if (ft.age > ft.lifeIn) ft.state = 'hold';
      FATE_TEXTS.push(ft);
    }
  }
  initFateTexts();

  /* ══════════════════════════════════════════════
     CLICK INTERACTION
  ══════════════════════════════════════════════ */
  cv.addEventListener('click', function(e) {
    var rect = cv.getBoundingClientRect();
    var mx = e.clientX - rect.left, my = e.clientY - rect.top;
    var sx = SX(), sy = SY(), mr = maxOrb();
    // Check planet click
    for (var i = 0; i < PLANETS.length; i++) {
      var p = PLANETS[i];
      if (!p.label) continue;
      var r = p.orb * mr;
      var px = sx + Math.cos(p.ang) * r;
      var py = sy + Math.sin(p.ang) * r;
      var dist = Math.sqrt((mx-px)*(mx-px)+(my-py)*(my-py));
      var scale = Math.max(0.70, Math.min(usableH()/560, 1.30));
      var hitR = p.sz * scale * 3;
      if (dist < hitR) {
        // Route change via click
        var col = p.glow.replace('rgba(','').split(',').slice(0,3).join(',');
        triggerShockwave(px, py, col, false);
        spawnExplosion(px, py, col, 55);
        if (p.id !== activeRoute) {
          activeRoute = p.id;
          STATE.activeRoute = p.id;
          _targetNebulaHue = ROUTE_NEBULA_HUE[p.id] || 208;
          if (window.setRoute) window.setRoute(p.id);
          if (window.KD_setRoute) window.KD_setRoute(p.id);
        }
        return;
      }
    }
    // Click empty space — small sparkle
    spawnExplosion(mx, my, '120,190,255', 12);
  }, { passive: true });

  /* ══════════════════════════════════════════════
     DRAW FUNCTIONS
  ══════════════════════════════════════════════ */

  function drawBg(t) {
    ctx.clearRect(0, 0, W, H);
    // Black hole: near-total darkness with red fringe
    if (STATE.blackHole) {
      var bhProg = Math.max(0, (20 - STATE.waterline) / 20);
      var bg = ctx.createRadialGradient(SX(), SY(), 0, W*0.5, H*0.5, Math.max(W,H)*0.82);
      bg.addColorStop(0,    'rgba(10,0,0,'+(0.95*bhProg)+')');
      bg.addColorStop(0.40, 'rgba(4,0,0,'+(0.98*bhProg)+')');
      bg.addColorStop(1,    '#020409');
      ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);
      return;
    }
    var bg = ctx.createRadialGradient(SX()*0.6, SY(), 0, W*0.5, H*0.5, Math.max(W,H)*0.82);
    bg.addColorStop(0,    '#050814');
    bg.addColorStop(0.30, '#040711');
    bg.addColorStop(0.65, '#03060e');
    bg.addColorStop(1,    '#020409');
    ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);
    ctx.save(); ctx.globalCompositeOperation = 'screen';
    var band = ctx.createLinearGradient(0, H*0.20, W, H*0.80);
    band.addColorStop(0,    'rgba(0,0,0,0)');
    band.addColorStop(0.25, 'rgba(60,80,140,0.038)');
    band.addColorStop(0.50, 'rgba(80,100,180,0.055)');
    band.addColorStop(0.75, 'rgba(60,80,140,0.038)');
    band.addColorStop(1,    'rgba(0,0,0,0)');
    ctx.fillStyle = band; ctx.fillRect(0, 0, W, H);
    ctx.restore();
  }

  function drawFilaments(t) {
    if (STATE.blackHole) return;
    // Lerp nebula hue toward target
    _currentNebulaHue += (_targetNebulaHue - _currentNebulaHue) * 0.008;
    ctx.save(); ctx.globalCompositeOperation = 'screen';
    for (var i = 0; i < FILAMENTS.length; i++) {
      var f = FILAMENTS[i];
      // Blend filament hue toward current
      f.hue += (_currentNebulaHue - f.hue) * 0.004;
      var breathe = Math.sin(t*f.speed+f.phase);
      var al = f.alpha*(0.6+0.4*breathe);
      var fx = f.x+Math.sin(t*f.speed*0.7+f.phase)*W*0.030;
      var fy = f.y+Math.cos(t*f.speed*0.5+f.phase)*H*0.020;
      ctx.save(); ctx.translate(fx, fy); ctx.rotate(f.angle);
      var ng = ctx.createRadialGradient(0,0,0,0,0,f.w*0.5);
      ng.addColorStop(0,   'hsla('+f.hue+',60%,55%,'+al+')');
      ng.addColorStop(0.5, 'hsla('+f.hue+',50%,45%,'+(al*0.4)+')');
      ng.addColorStop(1,   'hsla('+f.hue+',40%,35%,0)');
      ctx.beginPath(); ctx.ellipse(0,0,f.w*0.5,f.h*0.5,0,0,Math.PI*2);
      ctx.fillStyle=ng; ctx.fill(); ctx.restore();
    }
    ctx.restore();
  }

  function drawAurora(t) {
    if (STATE.blackHole || FPS_LOW) return;
    ctx.save(); ctx.globalCompositeOperation='screen';
    for (var i = 0; i < AURORA.length; i++) {
      var au = AURORA[i];
      for (var j = 0; j < au.pts.length; j++) {
        au.pts[j].dv += (Math.random()-0.5)*0.004;
        au.pts[j].dv *= 0.96; au.pts[j].dy += au.pts[j].dv; au.pts[j].dy *= 0.97;
      }
      var aal=au.alpha*(0.6+0.4*Math.sin(t*au.speed+au.phase));
      var ag=ctx.createLinearGradient(0,au.baseY,0,au.baseY+au.height);
      ag.addColorStop(0,'hsla('+au.hue+',80%,60%,0)');
      ag.addColorStop(0.3,'hsla('+au.hue+',80%,60%,'+aal+')');
      ag.addColorStop(0.7,'hsla('+au.hue+',70%,50%,'+(aal*0.5)+')');
      ag.addColorStop(1,'hsla('+au.hue+',70%,50%,0)');
      ctx.beginPath();
      ctx.moveTo(au.pts[0].x, au.baseY+au.pts[0].dy);
      for (var k=1; k<au.pts.length; k++) {
        var p0=au.pts[k-1],p1=au.pts[k];
        ctx.quadraticCurveTo(p0.x,au.baseY+p0.dy,(p0.x+p1.x)*0.5,(au.baseY+p0.dy+au.baseY+p1.dy)*0.5);
      }
      ctx.lineTo(W,au.baseY+au.height); ctx.lineTo(0,au.baseY+au.height); ctx.closePath();
      ctx.fillStyle=ag; ctx.fill();
    }
    ctx.restore();
  }

  function drawStars(t) {
    ctx.save(); ctx.globalCompositeOperation='screen';
    var bhProg = STATE.blackHole ? Math.max(0,(20-STATE.waterline)/20) : 0;
    for (var i = 0; i < STARS.length; i++) {
      var s = STARS[i];
      var al = s.a * (1 - bhProg * 0.85);
      if (s.tw) al *= (0.5+0.5*Math.sin(t*s.tS+s.tO));
      al = Math.max(0.01, Math.min(1, al));
      ctx.beginPath(); ctx.arc(s.x,s.y,s.r,0,Math.PI*2);
      ctx.fillStyle='rgba('+s.col+','+al.toFixed(3)+')'; ctx.fill();
      if (!FPS_LOW && s.bloom && al>0.44) {
        var sp=s.r*3.5;
        ctx.strokeStyle='rgba('+s.col+','+(al*0.06).toFixed(3)+')';
        ctx.lineWidth=0.18;
        ctx.beginPath(); ctx.moveTo(s.x-sp,s.y); ctx.lineTo(s.x+sp,s.y);
        ctx.moveTo(s.x,s.y-sp); ctx.lineTo(s.x,s.y+sp); ctx.stroke();
      }
    }
    ctx.restore();
  }

  function drawDustMotes(t) {
    if (FPS_LOW) return;
    ctx.save(); ctx.globalCompositeOperation='screen';
    for (var i=0;i<DUST_MOTES.length;i++) {
      var d=DUST_MOTES[i];
      d.x=(d.x+d.vx+W)%W; d.y=(d.y+d.vy+H)%H;
      var al=d.a*(0.5+0.5*Math.sin(t*d.tS+d.tO));
      ctx.beginPath(); ctx.arc(d.x,d.y,d.r,0,Math.PI*2);
      ctx.fillStyle='rgba('+d.col+','+al.toFixed(3)+')'; ctx.fill();
    }
    ctx.restore();
  }

  function drawFateTexts(dt) {
    if (STATE.blackHole) return;
    ctx.save(); ctx.globalCompositeOperation='screen';
    for (var i=0;i<FATE_TEXTS.length;i++) {
      var ft=FATE_TEXTS[i];
      ft.age+=dt*1000;
      if (ft.state==='in') { ft.alpha=ft.maxAlpha*Math.min(1,ft.age/ft.lifeIn); if(ft.age>=ft.lifeIn){ft.state='hold';ft.age=0;} }
      else if (ft.state==='hold') { ft.alpha=ft.maxAlpha; if(ft.age>=ft.lifeHold){ft.state='out';ft.age=0;} }
      else if (ft.state==='out') { ft.alpha=ft.maxAlpha*Math.max(0,1-ft.age/ft.lifeOut); if(ft.age>=ft.lifeOut){FATE_TEXTS[i]=spawnFateText();continue;} }
      if (ft.alpha<0.002) continue;
      ctx.font='300 '+ft.size+'px "DM Mono",monospace';
      ctx.fillStyle='rgba(175,210,255,'+ft.alpha.toFixed(4)+')';
      ctx.textAlign='center'; ctx.textBaseline='middle';
      for (var li=0;li<ft.lines.length;li++) {
        ctx.fillText(ft.lines[li], ft.x, ft.y+(li-(ft.lines.length-1)*0.5)*(ft.size*1.5));
      }
    }
    ctx.restore();
  }

  function drawOrbits() {
    var sx=SX(),sy=SY(),mr=maxOrb();
    ctx.save(); ctx.setLineDash([2,14]);
    PLANETS.forEach(function(p) {
      var r=p.orb*mr, isA=p.id===activeRoute;
      ctx.beginPath(); ctx.arc(sx,sy,r,0,Math.PI*2);
      if (STATE.blackHole) {
        ctx.strokeStyle=isA?'rgba(180,20,20,0.28)':'rgba(80,10,10,0.06)';
      } else {
        ctx.strokeStyle=isA?'rgba(140,200,255,0.22)':'rgba(80,130,220,0.06)';
      }
      ctx.lineWidth=isA?0.70:0.28; ctx.stroke();
    });
    ctx.setLineDash([]); ctx.restore();
  }

  function drawAsteroidBelt(dt) {
    var sx=SX(),sy=SY(),mr=maxOrb();
    // Speed scales with entropy
    var entropyMult = 0.5 + (STATE.entropy / 100) * 1.5;
    ctx.save(); ctx.globalCompositeOperation='screen';
    for (var i=0;i<ASTEROIDS.length;i++) {
      var a=ASTEROIDS[i];
      a.ang+=a.spd*dt*60*entropyMult;
      var r=(a.frac+a.scatter)*mr;
      ctx.beginPath(); ctx.arc(sx+Math.cos(a.ang)*r, sy+Math.sin(a.ang)*r, a.r, 0, Math.PI*2);
      ctx.fillStyle='rgba(160,150,140,'+a.a+')'; ctx.fill();
    }
    ctx.restore();
  }

  function drawIonTrails() {
    ctx.save(); ctx.globalCompositeOperation='screen';
    PLANETS.forEach(function(p) {
      if (!p.label||!ION_TRAILS[p.id]) return;
      var trail=ION_TRAILS[p.id];
      if (trail.length<3) return;
      for (var i=1;i<trail.length;i++) {
        var prog=i/trail.length, al=prog*0.15;
        ctx.beginPath(); ctx.moveTo(trail[i-1].x,trail[i-1].y); ctx.lineTo(trail[i].x,trail[i].y);
        ctx.strokeStyle=p.glow?p.glow+al+')':'rgba(150,200,255,'+al+')';
        ctx.lineWidth=prog*1.8; ctx.stroke();
      }
    });
    ctx.restore();
  }

  function drawGravLens(x, y, sz, t) {
    // Gravitational lensing rings around active planet
    ctx.save(); ctx.globalCompositeOperation='screen';
    for (var ri=1;ri<=LENS_RINGS;ri++) {
      var lR=sz*(2.2+ri*1.4);
      var al=0.055/ri*(0.7+0.3*Math.sin(t*0.0008+ri*1.1));
      ctx.beginPath(); ctx.arc(x,y,lR,0,Math.PI*2);
      ctx.strokeStyle='rgba(180,220,255,'+al+')';
      ctx.lineWidth=0.5; ctx.stroke();
      // Distorted segment
      ctx.save(); ctx.translate(x,y); ctx.rotate(t*0.0002*ri);
      ctx.beginPath();
      ctx.arc(0,0,lR,-0.4,0.4);
      ctx.strokeStyle='rgba(200,230,255,'+(al*2.5)+')';
      ctx.lineWidth=0.8; ctx.stroke();
      ctx.restore();
    }
    ctx.restore();
  }

  function drawWormhole(t, dt) {
    var sx=SX(),sy=SY(),mr=maxOrb();
    // Find active planet position
    var ap = PLANETS.find(function(p){return p.id===activeRoute;});
    if (!ap) return;
    var r=ap.orb*mr;
    var apx=sx+Math.cos(ap.ang)*r, apy=sy+Math.sin(ap.ang)*r;

    if (t>nextWormhole&&!WORMHOLE.active) {
      WORMHOLE.active=true; WORMHOLE.progress=0;
      WORMHOLE.fromX=sx; WORMHOLE.fromY=sy;
      WORMHOLE.toX=apx; WORMHOLE.toY=apy; WORMHOLE.alpha=0;
      nextWormhole=t+35000+Math.random()*40000;
    }
    if (!WORMHOLE.active) return;

    WORMHOLE.progress+=dt*0.35;
    WORMHOLE.toX=apx; WORMHOLE.toY=apy;
    if (WORMHOLE.progress<0.3) WORMHOLE.alpha=WORMHOLE.progress/0.3;
    else if (WORMHOLE.progress>0.7) WORMHOLE.alpha=Math.max(0,(1-WORMHOLE.progress)/0.3);
    else WORMHOLE.alpha=1;
    if (WORMHOLE.progress>=1) { WORMHOLE.active=false; return; }

    ctx.save(); ctx.globalCompositeOperation='screen';
    var al=WORMHOLE.alpha*0.35;
    var dx=WORMHOLE.toX-WORMHOLE.fromX, dy=WORMHOLE.toY-WORMHOLE.fromY;
    var wg=ctx.createLinearGradient(WORMHOLE.fromX,WORMHOLE.fromY,WORMHOLE.toX,WORMHOLE.toY);
    wg.addColorStop(0,'rgba(255,200,60,'+al+')');
    wg.addColorStop(0.5,'rgba(120,180,255,'+(al*0.6)+')');
    wg.addColorStop(1,'rgba(200,150,255,'+al+')');
    // Dashed wormhole path
    ctx.setLineDash([4,8]);
    ctx.beginPath(); ctx.moveTo(WORMHOLE.fromX,WORMHOLE.fromY);
    ctx.lineTo(WORMHOLE.toX,WORMHOLE.toY);
    ctx.strokeStyle=wg; ctx.lineWidth=0.8+WORMHOLE.alpha; ctx.stroke();
    ctx.setLineDash([]);
    // Energy pulse along path
    var pulseT=(WORMHOLE.progress%1);
    var px2=WORMHOLE.fromX+dx*pulseT, py2=WORMHOLE.fromY+dy*pulseT;
    var pg=ctx.createRadialGradient(px2,py2,0,px2,py2,8);
    pg.addColorStop(0,'rgba(255,240,200,'+al*2+')');
    pg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.beginPath(); ctx.arc(px2,py2,8,0,Math.PI*2); ctx.fillStyle=pg; ctx.fill();
    ctx.restore();
  }

  function drawSolarFlares(t, dt) {
    var sx=SX(),sy=SY(),R=sunR();
    if (t>nextFlare&&!FPS_LOW) {
      spawnFlare(sx,sy,R);
      nextFlare=t+3000+Math.random()*8000;
      STATE.flareCharge=Math.min(1,STATE.flareCharge+0.15);
    }
    ctx.save(); ctx.globalCompositeOperation='screen';
    for (var i=FLARES.length-1;i>=0;i--) {
      var f=FLARES[i];
      f.life+=dt;
      if (f.life>=f.maxLife) { FLARES.splice(i,1); continue; }
      var prog=f.life/f.maxLife;
      var al=(prog<0.2?prog/0.2:Math.max(0,1-(prog-0.2)/0.8))*0.65;
      var curve=Math.sin(prog*Math.PI)*f.len;
      var perpA=f.angle+Math.PI*0.5;
      var midX=f.sx+Math.cos(f.angle)*curve*0.5+Math.cos(perpA)*f.len*0.22;
      var midY=f.sy+Math.sin(f.angle)*curve*0.5+Math.sin(perpA)*f.len*0.22;
      var endX=f.sx+Math.cos(f.angle)*curve;
      var endY=f.sy+Math.sin(f.angle)*curve;
      var fg=ctx.createLinearGradient(f.sx,f.sy,endX,endY);
      fg.addColorStop(0,'rgba('+f.col+','+al+')');
      fg.addColorStop(0.5,'rgba('+f.col+','+(al*0.6)+')');
      fg.addColorStop(1,'rgba('+f.col+',0)');
      ctx.beginPath();
      ctx.moveTo(f.sx+Math.cos(f.angle)*f.R,f.sy+Math.sin(f.angle)*f.R);
      ctx.quadraticCurveTo(midX,midY,endX,endY);
      ctx.strokeStyle=fg; ctx.lineWidth=f.width*(1-prog*0.6); ctx.stroke();
    }
    ctx.restore();
  }

  function drawBlackHole(t) {
    if (!STATE.blackHole) return;
    var sx=SX(),sy=SY(),R=sunR();
    var bhProg=Math.max(0,(20-STATE.waterline)/20);
    ctx.save();
    // Accretion disk
    ctx.globalCompositeOperation='screen';
    for (var ri=8;ri>=1;ri--) {
      var rAl=(0.04/ri)*bhProg;
      var rR=R*(1.5+ri*2.8);
      ctx.beginPath(); ctx.arc(sx,sy,rR,0,Math.PI*2);
      ctx.strokeStyle='rgba(200,40,10,'+rAl+')';
      ctx.lineWidth=0.6; ctx.stroke();
    }
    // Event horizon
    ctx.globalCompositeOperation='source-over';
    var ehg=ctx.createRadialGradient(sx,sy,0,sx,sy,R*2.5);
    ehg.addColorStop(0,'rgba(0,0,0,1)');
    ehg.addColorStop(0.5,'rgba(5,0,0,0.92)');
    ehg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.beginPath(); ctx.arc(sx,sy,R*2.5,0,Math.PI*2);
    ctx.fillStyle=ehg; ctx.fill();
    // Hawking radiation glow
    ctx.globalCompositeOperation='screen';
    var hg=ctx.createRadialGradient(sx,sy,R*0.5,sx,sy,R*3.5);
    hg.addColorStop(0,'rgba(220,60,20,'+(0.55*bhProg)+')');
    hg.addColorStop(0.4,'rgba(120,10,5,'+(0.18*bhProg)+')');
    hg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.beginPath(); ctx.arc(sx,sy,R*3.5,0,Math.PI*2);
    ctx.fillStyle=hg; ctx.fill();
    // Label
    ctx.save();
    ctx.font='600 '+(Math.max(8,Math.round(R*0.55)))+'px "DM Mono",monospace';
    ctx.fillStyle='rgba(220,60,20,'+(0.80*bhProg)+')';
    ctx.textAlign='center'; ctx.textBaseline='bottom';
    ctx.fillText('COLLAPSE', sx, sy-R*2.8-4);
    ctx.restore();
    ctx.restore();
  }

  function drawPlanet(x, y, p, isA, t) {
    var scale=Math.max(0.70,Math.min(usableH()/560,1.30));
    var sz=p.sz*scale;

    ctx.save(); ctx.globalCompositeOperation='screen';
    if (p.atm) {
      var atmA=isA?0.22:0.08, atmR=sz*2.8+(isA?7:0);
      var atm=ctx.createRadialGradient(x,y,sz*0.5,x,y,atmR);
      atm.addColorStop(0,p.atm+atmA+')'); atm.addColorStop(0.6,p.atm+(atmA*0.3)+')'); atm.addColorStop(1,'rgba(0,0,0,0)');
      ctx.beginPath(); ctx.arc(x,y,atmR,0,Math.PI*2); ctx.fillStyle=atm; ctx.fill();
    }
    if (p.glow) {
      var pulse=isA?(1+Math.sin(t*0.0011)*0.14):1;
      var gR2=sz*(isA?5.2:3.0)*pulse;
      var gr2=ctx.createRadialGradient(x,y,sz*1.0,x,y,gR2);
      gr2.addColorStop(0,p.glow+(isA?'0.22':'0.07')+')'); gr2.addColorStop(1,'rgba(0,0,0,0)');
      ctx.beginPath(); ctx.arc(x,y,gR2,0,Math.PI*2); ctx.fillStyle=gr2; ctx.fill();
      var gR=sz*(isA?3.2:2.0)*pulse;
      var gr=ctx.createRadialGradient(x,y,sz*0.7,x,y,gR);
      gr.addColorStop(0,p.glow+(isA?'0.55':'0.22')+')'); gr.addColorStop(0.4,p.glow+(isA?'0.16':'0.07')+')'); gr.addColorStop(1,'rgba(0,0,0,0)');
      ctx.beginPath(); ctx.arc(x,y,gR,0,Math.PI*2); ctx.fillStyle=gr; ctx.fill();
    }
    ctx.restore();

    if (p.rings) {
      var rx=sz*3.4,ry=sz*0.36;
      ctx.save(); ctx.translate(x,y); ctx.rotate(-0.22); ctx.globalCompositeOperation='screen';
      for (var ri=0;ri<3;ri++) {
        var rf=0.78+ri*0.12;
        var rg=ctx.createLinearGradient(-rx*rf,0,rx*rf,0);
        rg.addColorStop(0,'rgba(0,0,0,0)'); rg.addColorStop(0.25,p.glow+(isA?'0.28':'0.14')+')');
        rg.addColorStop(0.5,p.glow+(isA?'0.42':'0.20')+')'); rg.addColorStop(0.75,p.glow+(isA?'0.28':'0.14')+')'); rg.addColorStop(1,'rgba(0,0,0,0)');
        ctx.beginPath(); ctx.ellipse(0,0,rx*rf,ry*rf,0,Math.PI,Math.PI*2);
        ctx.strokeStyle=rg; ctx.lineWidth=isA?1.6:0.8; ctx.stroke();
      }
      ctx.restore();
    }

    ctx.save();
    var body=ctx.createRadialGradient(x-sz*0.28,y-sz*0.26,0,x+sz*0.08,y+sz*0.08,sz*1.06);
    body.addColorStop(0,p.c0); body.addColorStop(0.45,p.c1); body.addColorStop(1,p.c2);
    ctx.beginPath(); ctx.arc(x,y,sz,0,Math.PI*2); ctx.fillStyle=body; ctx.fill();

    if (p.bands) {
      ctx.globalCompositeOperation='overlay';
      for (var bi=0;bi<4;bi++) {
        var by=y-sz*0.65+bi*(sz*0.36),bh=sz*0.14;
        var bg2=ctx.createLinearGradient(x-sz,by,x+sz,by);
        bg2.addColorStop(0,'rgba(0,0,0,0)'); bg2.addColorStop(0.3,'rgba(100,60,20,0.28)');
        bg2.addColorStop(0.7,'rgba(100,60,20,0.28)'); bg2.addColorStop(1,'rgba(0,0,0,0)');
        ctx.save(); ctx.beginPath(); ctx.ellipse(x,by+bh*0.5,sz*0.92,bh,0,0,Math.PI*2);
        ctx.fillStyle=bg2; ctx.fill(); ctx.restore();
      }
    }
    if (p.storm) {
      ctx.globalCompositeOperation='screen';
      var stx=x+sz*0.28,sty=y-sz*0.20;
      var stg=ctx.createRadialGradient(stx,sty,0,stx,sty,sz*0.32);
      stg.addColorStop(0,'rgba(180,200,255,0.35)'); stg.addColorStop(1,'rgba(0,0,0,0)');
      ctx.beginPath(); ctx.arc(stx,sty,sz*0.32,0,Math.PI*2); ctx.fillStyle=stg; ctx.fill();
    }

    ctx.globalCompositeOperation='screen';
    var vein=ctx.createRadialGradient(x-sz*0.20,y-sz*0.20,0,x-sz*0.06,y-sz*0.06,sz*0.62);
    vein.addColorStop(0,p.glow?p.glow+'0.32)':'rgba(255,255,255,0.18)'); vein.addColorStop(1,'rgba(0,0,0,0)');
    ctx.beginPath(); ctx.arc(x,y,sz,0,Math.PI*2); ctx.fillStyle=vein; ctx.fill();
    ctx.globalCompositeOperation='source-over';
    var limb=ctx.createRadialGradient(x,y,sz*0.12,x,y,sz*1.05);
    limb.addColorStop(0,'rgba(0,0,0,0)'); limb.addColorStop(0.5,'rgba(0,0,0,0.16)'); limb.addColorStop(1,'rgba(0,0,0,0.78)');
    ctx.beginPath(); ctx.arc(x,y,sz,0,Math.PI*2); ctx.fillStyle=limb; ctx.fill();
    ctx.restore();

    if (p.rings) {
      var rx2=sz*3.4,ry2=sz*0.36;
      ctx.save(); ctx.translate(x,y); ctx.rotate(-0.22); ctx.globalCompositeOperation='screen';
      for (var ri2=0;ri2<3;ri2++) {
        var rf2=0.78+ri2*0.12;
        var rg2=ctx.createLinearGradient(-rx2*rf2,0,rx2*rf2,0);
        rg2.addColorStop(0,'rgba(0,0,0,0)'); rg2.addColorStop(0.25,p.glow+(isA?'0.28':'0.14')+')');
        rg2.addColorStop(0.5,p.glow+(isA?'0.42':'0.20')+')'); rg2.addColorStop(0.75,p.glow+(isA?'0.28':'0.14')+')'); rg2.addColorStop(1,'rgba(0,0,0,0)');
        ctx.beginPath(); ctx.ellipse(0,0,rx2*rf2,ry2*rf2,0,0,Math.PI);
        ctx.strokeStyle=rg2; ctx.lineWidth=isA?1.6:0.8; ctx.stroke();
      }
      ctx.restore();
    }

    if (isA && !FPS_LOW) drawGravLens(x, y, sz, t);

    if (p.label) {
      ctx.save();
      var fs=Math.max(7,Math.round(sz*0.82));
      if (isA) { ctx.globalCompositeOperation='screen'; ctx.shadowColor=p.glow?p.glow+'0.85)':'rgba(120,200,255,0.85)'; ctx.shadowBlur=10; ctx.fillStyle=p.c0; }
      else { ctx.fillStyle='rgba(120,185,160,0.30)'; }
      ctx.font='500 '+fs+'px "DM Mono",monospace';
      ctx.textAlign='center'; ctx.textBaseline='top';
      ctx.fillText(p.label, x, y+sz+4);
      ctx.restore();
    }
    if (p.label) updateIonTrail(p.id, x, y);
  }

  function drawPlanets(dt, t) {
    var sx=SX(),sy=SY(),mr=maxOrb();
    // Planet speed scales with entropy
    var entropyMult = 0.4 + (STATE.entropy/100)*1.6;
    var items=PLANETS.map(function(p) {
      p.ang+=p.spd*dt*60*entropyMult;
      var r=p.orb*mr;
      return { p:p, x:sx+Math.cos(p.ang)*r, y:sy+Math.sin(p.ang)*r };
    });
    items.sort(function(a,b){return a.y-b.y;});
    var left=UI_LEFT(),top=UI_TOP(),bot=H-UI_BOTTOM();
    items.forEach(function(item) {
      if (item.x<left-40||item.x>W+40||item.y<top-40||item.y>bot+40) return;
      drawPlanet(item.x,item.y,item.p,item.p.id===activeRoute,t);
    });
  }

  function drawSun(t) {
    if (STATE.blackHole) { drawBlackHole(t); return; }
    var sx=SX(),sy=SY(),R=sunR();
    var gm = STATE.waterline<40?0.60:STATE.waterline<70?1.00:1.30;
    if (STATE.thinking) gm*=(1+Math.sin(t*0.005)*0.32);

    ctx.save(); ctx.globalCompositeOperation='lighter';

    for (var ring=6;ring>=1;ring--) {
      var rAl=(0.016/ring)*gm, rR=R*(3.2+ring*3.6);
      ctx.beginPath(); ctx.arc(sx,sy,rR,0,Math.PI*2);
      ctx.strokeStyle='rgba(255,200,80,'+rAl+')'; ctx.lineWidth=0.32; ctx.stroke();
    }
    if (STATE.thinking) {
      for (var b=0;b<3;b++) {
        var bPhase=(t*0.003+b*1.0)%(Math.PI*2);
        var bR=R*(2+b*4+Math.sin(bPhase)*2), bAl=Math.max(0,Math.sin(bPhase)*0.28);
        ctx.beginPath(); ctx.arc(sx,sy,bR,0,Math.PI*2);
        ctx.strokeStyle='rgba(255,220,80,'+bAl+')'; ctx.lineWidth=0.65; ctx.stroke();
      }
    }

    var fc=ctx.createRadialGradient(sx,sy,R*0.12,sx,sy,R*13);
    fc.addColorStop(0,'rgba(255,200,60,'+(0.34*gm)+')');
    fc.addColorStop(0.15,'rgba(255,140,20,'+(0.12*gm)+')');
    fc.addColorStop(0.40,'rgba(90,170,255,'+(0.05*gm)+')');
    fc.addColorStop(0.70,'rgba(40,70,150,'+(0.018*gm)+')');
    fc.addColorStop(1,'rgba(0,0,0,0)');
    ctx.beginPath(); ctx.arc(sx,sy,R*13,0,Math.PI*2); ctx.fillStyle=fc; ctx.fill();

    ctx.save(); ctx.translate(sx,sy); ctx.rotate(t*0.000015);
    for (var i=0;i<18;i++) {
      var a=(i/18)*Math.PI*2, rl=R*(1.8+0.28*Math.sin(i*1.7+t*0.00012))*gm;
      var gr=ctx.createLinearGradient(Math.cos(a)*R*0.18,Math.sin(a)*R*0.18,Math.cos(a)*rl,Math.sin(a)*rl);
      gr.addColorStop(0,'rgba(255,200,50,'+(0.32*gm)+')'); gr.addColorStop(0.5,'rgba(200,120,10,0.05)'); gr.addColorStop(1,'rgba(0,0,0,0)');
      ctx.strokeStyle=gr; ctx.lineWidth=0.6;
      ctx.beginPath(); ctx.moveTo(Math.cos(a)*R*0.18,Math.sin(a)*R*0.18); ctx.lineTo(Math.cos(a)*rl,Math.sin(a)*rl); ctx.stroke();
    }
    ctx.restore();
    ctx.globalCompositeOperation='source-over';

    var ih=ctx.createRadialGradient(sx,sy,R*0.22,sx,sy,R*2.6);
    ih.addColorStop(0,'rgba(255,240,150,0.96)'); ih.addColorStop(0.25,'rgba(255,190,50,0.65)');
    ih.addColorStop(0.60,'rgba(200,90,10,0.20)'); ih.addColorStop(1,'rgba(0,0,0,0)');
    ctx.beginPath(); ctx.arc(sx,sy,R*2.6,0,Math.PI*2); ctx.fillStyle=ih; ctx.fill();

    var sbody=ctx.createRadialGradient(sx-R*0.22,sy-R*0.22,0,sx,sy,R);
    sbody.addColorStop(0,'#fffad0'); sbody.addColorStop(0.25,'#ffdd40'); sbody.addColorStop(0.65,'#e06800'); sbody.addColorStop(1,'#5c1e00');
    ctx.beginPath(); ctx.arc(sx,sy,R,0,Math.PI*2); ctx.fillStyle=sbody; ctx.fill();

    var spec=ctx.createRadialGradient(sx-R*0.34,sy-R*0.34,0,sx-R*0.16,sy-R*0.16,R*0.52);
    spec.addColorStop(0,'rgba(255,252,230,0.52)'); spec.addColorStop(1,'rgba(255,252,230,0)');
    ctx.beginPath(); ctx.arc(sx,sy,R,0,Math.PI*2); ctx.fillStyle=spec; ctx.fill();

    var slim=ctx.createRadialGradient(sx,sy,R*0.14,sx,sy,R*1.05);
    slim.addColorStop(0,'rgba(0,0,0,0)'); slim.addColorStop(0.5,'rgba(0,0,0,0.14)'); slim.addColorStop(1,'rgba(0,0,0,0.72)');
    ctx.beginPath(); ctx.arc(sx,sy,R,0,Math.PI*2); ctx.fillStyle=slim; ctx.fill();

    ctx.save(); ctx.globalCompositeOperation='screen';
    ctx.shadowColor='rgba(255,200,60,0.90)'; ctx.shadowBlur=10; ctx.fillStyle='rgba(255,240,140,0.95)';
    var lfs=Math.max(8,Math.round(R*0.60));
    ctx.font='600 '+lfs+'px "DM Mono",monospace'; ctx.textAlign='center'; ctx.textBaseline='bottom';
    ctx.fillText('LYLA', sx, sy-R-4);
    ctx.restore(); ctx.restore();
  }

  function drawParticles(dt) {
    if (!PARTICLES.length) return;
    ctx.save(); ctx.globalCompositeOperation='screen';
    for (var i=PARTICLES.length-1;i>=0;i--) {
      var p=PARTICLES[i];
      p.x+=p.vx*dt*60*0.016; p.y+=p.vy*dt*60*0.016; p.vy+=p.grav;
      p.alpha-=p.decay;
      if (p.alpha<=0) { PARTICLES.splice(i,1); continue; }
      ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
      ctx.fillStyle='rgba('+p.col+','+Math.max(0,p.alpha).toFixed(3)+')'; ctx.fill();
    }
    ctx.restore();
  }

  function drawShockwaves(dt) {
    if (!SHOCKWAVES.length) return;
    ctx.save(); ctx.globalCompositeOperation='screen';
    for (var i=SHOCKWAVES.length-1;i>=0;i--) {
      var sw=SHOCKWAVES[i];
      sw.r+=dt*280; sw.alpha*=0.96;
      if (sw.r>=sw.maxR||sw.alpha<0.005) { SHOCKWAVES.splice(i,1); continue; }
      var prog=sw.r/sw.maxR;
      ctx.beginPath(); ctx.arc(sw.x,sw.y,sw.r,0,Math.PI*2);
      ctx.strokeStyle='rgba('+sw.col+','+sw.alpha.toFixed(3)+')';
      ctx.lineWidth=(1-prog)*3+0.5; ctx.stroke();
    }
    ctx.restore();
  }

  function drawComet(t, dt) {
    if (t>nextComet&&!COMET.active) {
      COMET.x=W*0.20+Math.random()*W*0.55; COMET.y=-4;
      COMET.vx=0.5+Math.random()*0.7; COMET.vy=0.4+Math.random()*0.5;
      COMET.life=0; COMET.maxLife=1.5+Math.random()*1.4; COMET.active=true;
      nextComet=t+22000+Math.random()*38000;
    }
    if (!COMET.active) return;
    COMET.life+=dt; if(COMET.life>COMET.maxLife||COMET.y>H+20){COMET.active=false;return;}
    COMET.x+=COMET.vx*dt*60*0.013; COMET.y+=COMET.vy*dt*60*0.013;
    var prog=COMET.life/COMET.maxLife;
    var al=prog<0.15?prog/0.15:Math.max(0,1-(prog-0.15)/0.85);
    var tl=80,tx=COMET.x-COMET.vx*tl*0.013,ty=COMET.y-COMET.vy*tl*0.013;
    var cg=ctx.createLinearGradient(tx,ty,COMET.x,COMET.y);
    cg.addColorStop(0,'rgba(150,205,255,0)'); cg.addColorStop(0.5,'rgba(170,215,255,'+(al*0.20)+')'); cg.addColorStop(1,'rgba(210,235,255,'+(al*0.72)+')');
    ctx.save(); ctx.globalCompositeOperation='screen';
    ctx.beginPath(); ctx.moveTo(tx,ty); ctx.lineTo(COMET.x,COMET.y); ctx.strokeStyle=cg; ctx.lineWidth=0.8; ctx.stroke();
    ctx.beginPath(); ctx.arc(COMET.x,COMET.y,1.3,0,Math.PI*2); ctx.fillStyle='rgba(195,225,255,'+(al*0.90)+')'; ctx.fill();
    ctx.restore();
  }

  function drawMeteors(t, dt) {
    if (t>nextMeteor&&!meteorActive) {
      METEORS=[]; var n=16+Math.floor(Math.random()*20);
      for (var i=0;i<n;i++) {
        METEORS.push({x:Math.random()*W*0.8+W*0.05,y:-10-Math.random()*60,
          vx:0.5+Math.random()*0.8,vy:0.4+Math.random()*0.7,
          length:40+Math.random()*80,alpha:0.55+Math.random()*0.35,
          life:0,maxLife:1.2+Math.random()*1.0,delay:Math.random()*3000,
          col:Math.random()<0.7?'195,220,255':'255,220,180',active:false});
      }
      meteorActive=true; meteorEnd=t+7000; nextMeteor=t+50000+Math.random()*60000;
    }
    if (!meteorActive) return;
    if (t>meteorEnd&&METEORS.every(function(m){return m.life>=m.maxLife;})) { meteorActive=false; METEORS=[]; return; }
    var elapsed=t-(meteorEnd-7000);
    ctx.save(); ctx.globalCompositeOperation='screen';
    for (var i=0;i<METEORS.length;i++) {
      var m=METEORS[i];
      if (elapsed<m.delay) continue;
      if (!m.active) m.active=true;
      m.life+=dt; if(m.life>=m.maxLife||m.y>H+20) continue;
      m.x+=m.vx*dt*60*0.014; m.y+=m.vy*dt*60*0.014;
      var prog2=m.life/m.maxLife;
      var al2=prog2<0.10?(prog2/0.10)*m.alpha:Math.max(0,m.alpha*(1-(prog2-0.10)/0.90));
      var tx2=m.x-m.vx*m.length*0.013,ty2=m.y-m.vy*m.length*0.013;
      var mg=ctx.createLinearGradient(tx2,ty2,m.x,m.y);
      mg.addColorStop(0,'rgba('+m.col+',0)'); mg.addColorStop(0.5,'rgba('+m.col+','+(al2*0.25)+')'); mg.addColorStop(1,'rgba('+m.col+','+al2+')');
      ctx.beginPath(); ctx.moveTo(tx2,ty2); ctx.lineTo(m.x,m.y); ctx.strokeStyle=mg; ctx.lineWidth=0.9; ctx.stroke();
      ctx.beginPath(); ctx.arc(m.x,m.y,1.1,0,Math.PI*2); ctx.fillStyle='rgba('+m.col+','+al2+')'; ctx.fill();
    }
    ctx.restore();
  }

  function drawHUD() {
    ctx.save();
    ctx.font='300 7px "DM Mono",monospace'; ctx.textBaseline='bottom';
    ctx.fillStyle='rgba(150,205,255,0.14)';
    ctx.textAlign='left';
    ctx.fillText(
      'Choice(t)='+STATE.choice_count+
      '  ENT='+Math.round(STATE.entropy)+
      '  STB='+Math.round(STATE.stability)+
      '  RSC='+Math.round(STATE.resources)+
      '  WL='+Math.round(STATE.waterline)+
      (STATE.blackHole?' ⚠ COLLAPSE':''),
      UI_LEFT()+14, H-UI_BOTTOM()-7
    );
    ctx.fillStyle='rgba(150,205,255,0.09)';
    ctx.textAlign='right';
    ctx.fillText('FATE DETERMINISTIC DECISION INFRASTRUCTURE v35 | '+activeRoute.toUpperCase(), W-9, H-UI_BOTTOM()-7);
    ctx.restore();
  }

  /* ── MAIN LOOP ────────────────────────────────── */
  function loop(ts) {
    if (!lastTime) lastTime = ts;
    var dt = Math.min((ts-lastTime)/1000, 0.05);
    lastTime = ts;
    monitorFPS(ts);
    syncStateFromHTML();
    updateHTMLDisplay();
    try {
      drawBg(ts);
      drawFilaments(ts);
      drawAurora(ts);
      drawStars(ts);
      drawDustMotes(ts);
      drawFateTexts(dt);
      drawMeteors(ts, dt);
      drawComet(ts, dt);
      drawIonTrails();
      drawOrbits();
      drawAsteroidBelt(dt);
      drawPlanets(dt, ts);
      drawWormhole(ts, dt);
      drawSolarFlares(ts, dt);
      drawSun(ts);
      drawParticles(dt);
      drawShockwaves(dt);
      drawHUD();
    } catch(e) { console.error('[v35]', e); }
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);

  /* ── PUBLIC API ───────────────────────────────── */
  window.LYLA_thinking  = function()   { STATE.thinking=true; };
  window.LYLA_answered  = function()   { STATE.thinking=false; };
  window.KD_pulse = function(r) {
    STATE.thinking=false;
    if (r&&r!==activeRoute) {
      var p=PLANETS.find(function(pl){return pl.id===r;});
      if (p) {
        var sx=SX(),sy=SY(),mr=maxOrb(),orb=p.orb*mr;
        var px2=sx+Math.cos(p.ang)*orb, py2=sy+Math.sin(p.ang)*orb;
        var col=p.glow.replace('rgba(','').split(',').slice(0,3).join(',');
        triggerShockwave(px2,py2,col,false);
        spawnExplosion(px2,py2,col,50);
      }
      activeRoute=r; STATE.activeRoute=r;
      _targetNebulaHue=ROUTE_NEBULA_HUE[r]||208;
    }
  };
  window.KD_setRoute   = function(r)       { activeRoute=r; STATE.activeRoute=r; _targetNebulaHue=ROUTE_NEBULA_HUE[r]||208; };
  window.KD_council    = function()         { STATE.thinking=true; };
  window.KD_councilEnd = function()         { STATE.thinking=false; };
  window.KD_shockwave  = function(x,y,col) { triggerShockwave(x,y,col,false); };
  window.KD_explosion  = function(x,y,col,n){ spawnExplosion(x,y,col,n); };
  window.KD_setState   = function(key,val) { if(key in STATE){STATE[key]=val;} updateWaterline(); };
  window.KD_getState   = function()        { return Object.assign({},STATE); };
  window.KD.safeVal    = function(v,d) {
    var n=+v, dec=typeof d==='number'?d:2;
    return (isFinite(n)&&!isNaN(n))?n.toFixed(dec):'0.00';
  };
})();
