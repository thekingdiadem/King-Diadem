/**
 * static/ai_orbit.js — KING DIADEM Orbital Engine v2.0
 * Multi-ring orbital system — syncs with KD STATE
 * Features: elliptical orbits, trail decay, council rings, warp mode, entropy speed
 */
(function () {
  'use strict';

  var canvas = document.getElementById('orbit');
  if (!canvas) return;

  var ctx = canvas.getContext('2d');
  var W = 0, H = 0;

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
    buildOrbits();
  }
  window.addEventListener('resize', function () { clearTimeout(_rt); _rt = setTimeout(resize, 80); }, { passive: true });
  var _rt;

  /* ── STATE ────────────────────────────────────── */
  function getConf()      { return Math.min(100, Math.max(0, +(window.KD && window.KD.state && window.KD.state.consensus && window.KD.state.consensus.confidence) || 50)); }
  function getRisk()      { return Math.min(100, Math.max(0, +(window.KD && window.KD.state && window.KD.state.risk && window.KD.state.risk.risk_score) || 0)); }
  function getEntropy()   { return Math.min(100, Math.max(0, +(window.KD && window.KD.state && window.KD.state.entropy) || 45)); }
  function getThinking()  { return !!(window.KD && window.KD.state && window.KD.state.thinking); }
  function getWaterline() { return Math.min(100, Math.max(0, +(window.KD && window.KD.state && window.KD.state.waterline) || 89)); }

  /* ── ORBIT DEFINITIONS ────────────────────────── */
  /* Each ring represents a council member / decision axis */
  var ORBIT_DEFS = [
    { name: 'LYLA',    hue: 48,  sat: 90, count: 12, rx: 0.08, ry: 0.06, tilt: 0.00, spd: 0.0012, trailLen: 28, sz: 2.8, pulsing: true  },
    { name: 'VEGA',    hue: 265, sat: 85, count: 8,  rx: 0.14, ry: 0.10, tilt: 0.40, spd: 0.0008, trailLen: 22, sz: 2.4, pulsing: true  },
    { name: 'TITAN',   hue: 210, sat: 80, count: 10, rx: 0.20, ry: 0.14, tilt: 0.90, spd: 0.0006, trailLen: 18, sz: 2.0, pulsing: false },
    { name: 'PATICCA', hue: 168, sat: 75, count: 7,  rx: 0.27, ry: 0.18, tilt: 1.55, spd: 0.0004, trailLen: 14, sz: 1.8, pulsing: false },
    { name: 'COSMOS',  hue: 350, sat: 80, count: 5,  rx: 0.34, ry: 0.22, tilt: 2.20, spd: 0.0003, trailLen: 10, sz: 2.2, pulsing: true  },
    /* Outer debris */
    { name: null,      hue: 200, sat: 30, count: 28, rx: 0.42, ry: 0.28, tilt: 0.60, spd: 0.0001, trailLen: 5,  sz: 0.8, pulsing: false },
  ];

  var RINGS = [];

  function buildOrbits() {
    RINGS = [];
    var cx = W * 0.50, cy = H * 0.50;
    var base = Math.min(W, H);

    ORBIT_DEFS.forEach(function (def) {
      var particles = [];
      for (var i = 0; i < def.count; i++) {
        var startAng = (i / def.count) * Math.PI * 2;
        particles.push({
          ang:   startAng,
          trail: [],
          burst: false,
          burstAge: 0,
        });
      }
      RINGS.push({
        def:       def,
        particles: particles,
        rx:        base * def.rx,
        ry:        base * def.ry,
        cx:        cx,
        cy:        cy,
        tilt:      def.tilt,
        warpMode:  false,
      });
    });
  }

  /* ── PARTICLES ────────────────────────────────── */
  var BURST_PARTICLES = [];

  function spawnBurst(x, y, hue, n) {
    n = n || 20;
    for (var i = 0; i < n; i++) {
      var ang = Math.random() * Math.PI * 2;
      var spd = 0.5 + Math.random() * 2.5;
      BURST_PARTICLES.push({
        x: x, y: y,
        vx: Math.cos(ang) * spd,
        vy: Math.sin(ang) * spd,
        r: 0.5 + Math.random() * 1.8,
        alpha: 0.8 + Math.random() * 0.2,
        decay: 0.018 + Math.random() * 0.025,
        hue: hue,
      });
    }
  }

  /* ── WARP RINGS ───────────────────────────────── */
  var WARP_RINGS = [];

  function addWarpRing(cx, cy) {
    WARP_RINGS.push({ x: cx, y: cy, r: 0, maxR: Math.min(W, H) * 0.55, alpha: 0.60, hue: 210 });
  }

  /* ── MAIN LOOP ────────────────────────────────── */
  var _last = 0;
  function loop(ts) {
    var dt = Math.min((ts - _last) / 1000, 0.05);
    _last  = ts;

    var conf      = getConf();
    var risk      = getRisk();
    var entropy   = getEntropy();
    var thinking  = getThinking();
    var waterline = getWaterline();
    var danger    = risk / 100;

    /* Speed driven by confidence + entropy */
    var speedMult = (0.4 + (conf / 100) * 0.8) * (0.5 + (entropy / 100) * 1.5);
    if (thinking) speedMult *= 1.6;
    if (waterline < 30) speedMult *= 0.5; /* Collapse slow-down */

    ctx.clearRect(0, 0, W, H);
    var cx = W * 0.50, cy = H * 0.50;

    /* ── Central core ── */
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    var coreHue = danger > 0.7 ? 10 : danger > 0.4 ? 36 : 48;
    var corePulse = thinking ? 1 + Math.sin(ts * 0.005) * 0.3 : 1;
    var cg = ctx.createRadialGradient(cx, cy, 0, cx, cy, Math.min(W, H) * 0.07 * corePulse);
    cg.addColorStop(0, 'hsla(' + coreHue + ',100%,85%,0.90)');
    cg.addColorStop(0.3, 'hsla(' + coreHue + ',90%,60%,0.40)');
    cg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.beginPath();
    ctx.arc(cx, cy, Math.min(W, H) * 0.07 * corePulse, 0, Math.PI * 2);
    ctx.fillStyle = cg;
    ctx.fill();

    /* Core dot */
    ctx.beginPath();
    ctx.arc(cx, cy, Math.min(W, H) * 0.012 * corePulse, 0, Math.PI * 2);
    ctx.fillStyle = 'hsla(' + coreHue + ',100%,92%,0.96)';
    ctx.fill();
    ctx.restore();

    /* ── Orbit ellipses (faint structural) ── */
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    RINGS.forEach(function (ring) {
      var def = ring.def;
      if (!def.name) return; /* skip debris ring guide */
      ctx.save();
      ctx.translate(ring.cx, ring.cy);
      ctx.rotate(ring.tilt);
      ctx.beginPath();
      ctx.ellipse(0, 0, ring.rx, ring.ry, 0, 0, Math.PI * 2);
      ctx.strokeStyle = 'hsla(' + def.hue + ',60%,55%,0.06)';
      ctx.lineWidth   = 0.5;
      ctx.setLineDash([3, 14]);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.restore();

      /* Label */
      if (def.name) {
        var labelAng  = ts * def.spd * 0.15;
        var labelX    = ring.cx + Math.cos(labelAng + ring.tilt) * ring.rx;
        var labelY    = ring.cy + Math.sin(labelAng + ring.tilt) * ring.ry;
        ctx.save();
        ctx.font      = '300 7px "DM Mono",monospace';
        ctx.fillStyle = 'hsla(' + def.hue + ',70%,65%,0.22)';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(def.name, labelX, labelY);
        ctx.restore();
      }
    });
    ctx.restore();

    /* ── Update + draw particles ── */
    ctx.save();
    ctx.globalCompositeOperation = 'screen';

    RINGS.forEach(function (ring) {
      var def = ring.def;
      ring.particles.forEach(function (p) {
        /* Advance angle */
        p.ang += def.spd * dt * 60 * speedMult;

        /* Ellipse position with tilt */
        var cosT = Math.cos(ring.tilt), sinT = Math.sin(ring.tilt);
        var lx   = Math.cos(p.ang) * ring.rx;
        var ly   = Math.sin(p.ang) * ring.ry;
        var px   = ring.cx + lx * cosT - ly * sinT;
        var py   = ring.cy + lx * sinT + ly * cosT;

        /* Trail */
        p.trail.push({ x: px, y: py });
        if (p.trail.length > def.trailLen) p.trail.shift();

        /* Draw trail */
        for (var ti = 1; ti < p.trail.length; ti++) {
          var prog  = ti / p.trail.length;
          var talpha = prog * prog * 0.45;
          ctx.beginPath();
          ctx.moveTo(p.trail[ti - 1].x, p.trail[ti - 1].y);
          ctx.lineTo(p.trail[ti].x, p.trail[ti].y);
          ctx.strokeStyle = 'hsla(' + def.hue + ',80%,65%,' + talpha.toFixed(3) + ')';
          ctx.lineWidth   = prog * def.sz * 0.55;
          ctx.stroke();
        }

        /* Glow when pulsing */
        var pulseFactor = def.pulsing ? (0.6 + 0.4 * Math.sin(ts * 0.003 + p.ang * 3)) : 0.8;
        if (pulseFactor > 0.9 || p.burst) {
          var gg = ctx.createRadialGradient(px, py, 0, px, py, def.sz * 4);
          gg.addColorStop(0, 'hsla(' + def.hue + ',100%,80%,' + (pulseFactor * 0.35) + ')');
          gg.addColorStop(1, 'rgba(0,0,0,0)');
          ctx.beginPath();
          ctx.arc(px, py, def.sz * 4, 0, Math.PI * 2);
          ctx.fillStyle = gg;
          ctx.fill();
        }

        /* Core dot */
        ctx.beginPath();
        ctx.arc(px, py, def.sz * pulseFactor, 0, Math.PI * 2);
        ctx.fillStyle = 'hsla(' + def.hue + ',90%,' + (60 + pulseFactor * 20) + '%,' + (0.7 + pulseFactor * 0.3) + ')';
        ctx.fill();

        /* Random burst when thinking */
        if (thinking && Math.random() < 0.004 * speedMult) {
          spawnBurst(px, py, def.hue, 10);
        }

        /* Burst age */
        if (p.burst) { p.burstAge += dt * 1000; if (p.burstAge > 400) { p.burst = false; p.burstAge = 0; } }
      });
    });

    /* ── Burst particles ── */
    for (var bi = BURST_PARTICLES.length - 1; bi >= 0; bi--) {
      var bp = BURST_PARTICLES[bi];
      bp.x    += bp.vx * dt * 60 * 0.016;
      bp.y    += bp.vy * dt * 60 * 0.016;
      bp.alpha -= bp.decay;
      if (bp.alpha <= 0) { BURST_PARTICLES.splice(bi, 1); continue; }
      ctx.beginPath();
      ctx.arc(bp.x, bp.y, bp.r, 0, Math.PI * 2);
      ctx.fillStyle = 'hsla(' + bp.hue + ',90%,75%,' + bp.alpha.toFixed(3) + ')';
      ctx.fill();
    }
    ctx.restore();

    /* ── Warp rings ── */
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    for (var wi = WARP_RINGS.length - 1; wi >= 0; wi--) {
      var wr = WARP_RINGS[wi];
      wr.r     += dt * 220;
      wr.alpha *= 0.95;
      if (wr.r >= wr.maxR || wr.alpha < 0.005) { WARP_RINGS.splice(wi, 1); continue; }
      var prog2 = wr.r / wr.maxR;
      ctx.beginPath();
      ctx.arc(wr.x, wr.y, wr.r, 0, Math.PI * 2);
      ctx.strokeStyle = 'hsla(' + wr.hue + ',80%,70%,' + wr.alpha.toFixed(3) + ')';
      ctx.lineWidth   = (1 - prog2) * 2.5 + 0.3;
      ctx.stroke();
    }
    ctx.restore();

    /* ── Waterline collapse visual ── */
    if (waterline < 30) {
      ctx.save();
      ctx.globalCompositeOperation = 'screen';
      var collapseAlpha = (30 - waterline) / 30 * 0.25;
      var vignette = ctx.createRadialGradient(cx, cy, Math.min(W, H) * 0.15, cx, cy, Math.min(W, H) * 0.70);
      vignette.addColorStop(0, 'rgba(0,0,0,0)');
      vignette.addColorStop(1, 'rgba(180,20,5,' + collapseAlpha + ')');
      ctx.fillStyle = vignette;
      ctx.fillRect(0, 0, W, H);
      ctx.restore();
    }

    /* ── HUD ── */
    ctx.save();
    ctx.font = '300 8px "DM Mono",monospace';
    ctx.fillStyle = 'rgba(80,220,200,0.18)';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'bottom';
    ctx.fillText(
      'ORBITAL ENGINE  |  CONF ' + Math.round(conf) +
      '  RISK ' + Math.round(risk) +
      '  SPEED ×' + speedMult.toFixed(2) +
      (thinking ? '  [COUNCIL ACTIVE]' : ''),
      W - 14, H - 14
    );
    ctx.restore();

    requestAnimationFrame(loop);
  }

  /* ── INIT ──────────────────────────────────────── */
  resize();
  requestAnimationFrame(loop);

  /* ── PUBLIC API ────────────────────────────────── */
  if (!window.KD) window.KD = {};

  window.KD.orbitWarp = function () {
    var cx = W * 0.50, cy = H * 0.50;
    addWarpRing(cx, cy);
    RINGS.forEach(function (ring) {
      ring.particles.forEach(function (p) { p.burst = true; p.burstAge = 0; });
    });
  };

  window.KD.orbitBurst = function (x, y, hue) {
    spawnBurst(x || W / 2, y || H / 2, hue || 200, 30);
  };

  window.KD.orbitSetSpeed = function (mult) {
    ORBIT_DEFS.forEach(function (d) { d.spd = d.spd * mult; });
    buildOrbits();
  };

})();

