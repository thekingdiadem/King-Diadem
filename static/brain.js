/**
 * static/ai_brain.js — KING DIADEM Neural Core v2.0
 * Full cosmic neural network — syncs with KD STATE
 * Features: pulse waves, synaptic fire, risk heatmap, signal cascades
 */
(function () {
  'use strict';

  var canvas = document.getElementById('brain');
  if (!canvas) return;

  var ctx = canvas.getContext('2d');
  var W = 0, H = 0;

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
    buildGraph();
  }

  window.addEventListener('resize', function () { clearTimeout(_rt); _rt = setTimeout(resize, 80); }, { passive: true });
  var _rt;

  /* ── STATE BRIDGE ─────────────────────────────── */
  function getRisk()       { return Math.min(100, Math.max(0, +(window.KD && window.KD.state && window.KD.state.risk && window.KD.state.risk.risk_score) || 0)); }
  function getConfidence() { return Math.min(100, Math.max(0, +(window.KD && window.KD.state && window.KD.state.consensus && window.KD.state.consensus.confidence) || 50)); }
  function getThinking()   { return !!(window.KD && window.KD.state && window.KD.state.thinking); }
  function getWaterline()  { return Math.min(100, Math.max(0, +(window.KD && window.KD.state && window.KD.state.waterline) || 89)); }
  function getEntropy()    { return Math.min(100, Math.max(0, +(window.KD && window.KD.state && window.KD.state.entropy) || 45)); }

  /* ── NODE GRAPH ───────────────────────────────── */
  var NODES = [], EDGES = [], SIGNALS = [], PULSES = [];
  var NODE_COUNT = 38;

  /* Layer clusters for structured layout */
  var LAYERS = [
    { count: 5,  ring: 0.08, label: 'INPUT'  },
    { count: 10, ring: 0.18, label: 'ENCODE' },
    { count: 10, ring: 0.30, label: 'REASON' },
    { count: 8,  ring: 0.42, label: 'DECIDE' },
    { count: 5,  ring: 0.54, label: 'OUTPUT' },
  ];

  function buildGraph() {
    NODES = []; EDGES = [];
    var cx = W * 0.50, cy = H * 0.50;
    var base = Math.min(W, H) * 0.46;

    LAYERS.forEach(function (layer, li) {
      for (var i = 0; i < layer.count; i++) {
        var baseAng = (i / layer.count) * Math.PI * 2;
        var jitter  = (Math.random() - 0.5) * (Math.PI / layer.count) * 0.6;
        var ang     = baseAng + jitter + li * 0.22;
        var r       = base * layer.ring * (0.88 + Math.random() * 0.24);
        NODES.push({
          x:       cx + Math.cos(ang) * r,
          y:       cy + Math.sin(ang) * r,
          vx:      (Math.random() - 0.5) * 0.18,
          vy:      (Math.random() - 0.5) * 0.12,
          r:       1.6 + Math.random() * 2.8,
          layer:   li,
          charge:  Math.random(),
          phase:   Math.random() * Math.PI * 2,
          firing:  false,
          fireAge: 0,
          label:   layer.label,
        });
      }
    });

    /* Edges — connect within layer + bridge to next */
    NODES.forEach(function (a, i) {
      NODES.forEach(function (b, j) {
        if (j <= i) return;
        var dl = Math.abs(a.layer - b.layer);
        if (dl > 1) return;
        var dx = a.x - b.x, dy = a.y - b.y;
        var dist = Math.sqrt(dx * dx + dy * dy);
        var maxDist = Math.min(W, H) * (dl === 0 ? 0.13 : 0.22);
        if (dist < maxDist) {
          EDGES.push({ a: i, b: j, w: 1 - dist / maxDist, active: false, activeAge: 0 });
        }
      });
    });
  }

  /* ── SIGNAL CASCADE ───────────────────────────── */
  function fireSignal(fromNode) {
    var node = NODES[fromNode];
    if (!node) return;
    node.firing  = true;
    node.fireAge = 0;

    /* Propagate along edges */
    EDGES.forEach(function (e) {
      var target = -1;
      if (e.a === fromNode) target = e.b;
      if (e.b === fromNode) target = e.a;
      if (target < 0) return;
      var delay = e.w * 300 + Math.random() * 200;
      e.active    = true;
      e.activeAge = 0;
      setTimeout(function () {
        if (NODES[target] && NODES[target].layer > node.layer) {
          NODES[target].firing  = true;
          NODES[target].fireAge = 0;
        }
      }, delay);
    });
  }

  function spawnPulseWave(x, y, col) {
    PULSES.push({ x: x, y: y, r: 0, maxR: Math.min(W, H) * 0.28, alpha: 0.55, col: col || '80,200,255' });
  }

  /* ── MAIN LOOP ────────────────────────────────── */
  var _last = 0;
  function loop(ts) {
    var dt  = Math.min((ts - _last) / 1000, 0.05);
    _last   = ts;

    var risk       = getRisk();
    var conf       = getConfidence();
    var thinking   = getThinking();
    var waterline  = getWaterline();
    var entropy    = getEntropy();
    var danger     = risk / 100;
    var speedMult  = 0.5 + (entropy / 100) * 1.5;
    var cx = W * 0.50, cy = H * 0.50;

    ctx.clearRect(0, 0, W, H);

    /* ── Background nebula haze ── */
    if (!window._bhMode || waterline > 20) {
      var bhue = danger > 0.7 ? 10 : danger > 0.4 ? 30 : 210;
      var bg = ctx.createRadialGradient(cx, cy, 0, cx, cy, Math.min(W, H) * 0.55);
      bg.addColorStop(0,   'hsla(' + bhue + ',60%,12%,0.22)');
      bg.addColorStop(0.5, 'hsla(' + bhue + ',40%,8%,0.10)');
      bg.addColorStop(1,   'rgba(0,0,0,0)');
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, W, H);
    }

    /* ── Auto-fire when thinking ── */
    if (thinking && Math.random() < 0.08 * speedMult) {
      var src = Math.floor(Math.random() * NODES.length);
      fireSignal(src);
    }

    /* ── Spontaneous firing ── */
    if (Math.random() < 0.012 * speedMult) {
      var n = Math.floor(Math.random() * NODES.length);
      fireSignal(n);
      if (Math.random() < 0.3) spawnPulseWave(NODES[n].x, NODES[n].y, riskColor(danger));
    }

    /* ── Update node drift ── */
    NODES.forEach(function (n) {
      n.x  += n.vx * dt * 60 * speedMult * 0.10;
      n.y  += n.vy * dt * 60 * speedMult * 0.10;
      var dx = n.x - cx, dy = n.y - cy;
      var dist = Math.sqrt(dx * dx + dy * dy);
      var maxR = Math.min(W, H) * 0.58;
      if (dist > maxR) { n.vx -= dx * 0.0006; n.vy -= dy * 0.0006; }
      n.vx *= 0.998; n.vy *= 0.998;
      n.charge = 0.5 + 0.5 * Math.sin(ts * 0.0006 + n.phase);
      if (n.firing) { n.fireAge += dt * 1000; if (n.fireAge > 600) n.firing = false; }
    });

    /* ── Draw edges ── */
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    EDGES.forEach(function (e) {
      var na = NODES[e.a], nb = NODES[e.b];
      if (!na || !nb) return;
      if (e.active) { e.activeAge += dt * 1000; if (e.activeAge > 500) { e.active = false; e.activeAge = 0; } }
      var base  = e.active ? 0.55 : (e.w * 0.08 + 0.02);
      var pulse = thinking ? (0.5 + 0.5 * Math.sin(ts * 0.004 + e.a)) * 0.15 : 0;
      var alpha = Math.min(0.85, base + pulse);
      var hue   = e.active ? (danger > 0.6 ? 10 : 185) : 200;
      var sat   = e.active ? 90 : 50;
      ctx.beginPath();
      ctx.moveTo(na.x, na.y);
      ctx.lineTo(nb.x, nb.y);
      ctx.strokeStyle = 'hsla(' + hue + ',' + sat + '%,65%,' + alpha.toFixed(3) + ')';
      ctx.lineWidth   = e.active ? 1.4 : 0.4;
      ctx.stroke();

      /* Signal pulse dot moving along edge when active */
      if (e.active) {
        var t   = Math.min(1, e.activeAge / 400);
        var px2 = na.x + (nb.x - na.x) * t;
        var py2 = na.y + (nb.y - na.y) * t;
        ctx.beginPath();
        ctx.arc(px2, py2, 2.8, 0, Math.PI * 2);
        ctx.fillStyle = 'hsla(' + hue + ',100%,85%,0.90)';
        ctx.fill();
      }
    });
    ctx.restore();

    /* ── Draw nodes ── */
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    NODES.forEach(function (n) {
      var fireP  = n.firing ? Math.max(0, 1 - n.fireAge / 600) : 0;
      var sz     = n.r * (1 + fireP * 2.2);
      var hue    = n.layer === 0 ? 200 : n.layer === 4 ? (danger > 0.6 ? 10 : 120) : 210 - n.layer * 18;
      var alpha  = 0.35 + n.charge * 0.40 + fireP * 0.50;

      /* Glow */
      if (fireP > 0.1 || n.charge > 0.7) {
        var glow = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, sz * 4.5);
        glow.addColorStop(0,   'hsla(' + hue + ',100%,72%,' + (alpha * 0.55 * fireP || 0.04) + ')');
        glow.addColorStop(1,   'rgba(0,0,0,0)');
        ctx.beginPath();
        ctx.arc(n.x, n.y, sz * 4.5, 0, Math.PI * 2);
        ctx.fillStyle = glow;
        ctx.fill();
      }

      /* Core */
      ctx.beginPath();
      ctx.arc(n.x, n.y, sz, 0, Math.PI * 2);
      ctx.fillStyle = 'hsla(' + hue + ',80%,' + (55 + fireP * 30) + '%,' + alpha + ')';
      ctx.fill();
    });
    ctx.restore();

    /* ── Layer rings (faint structural guides) ── */
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    LAYERS.forEach(function (layer, li) {
      var r   = Math.min(W, H) * 0.46 * layer.ring;
      var al  = 0.025 + (thinking ? 0.01 * Math.sin(ts * 0.002 + li) : 0);
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(80,160,255,' + al + ')';
      ctx.lineWidth   = 0.5;
      ctx.setLineDash([4, 18]);
      ctx.stroke();
      ctx.setLineDash([]);
    });
    ctx.restore();

    /* ── Pulse waves ── */
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    for (var pi = PULSES.length - 1; pi >= 0; pi--) {
      var p = PULSES[pi];
      p.r     += dt * 160;
      p.alpha *= 0.94;
      if (p.r >= p.maxR || p.alpha < 0.005) { PULSES.splice(pi, 1); continue; }
      var prog = p.r / p.maxR;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(' + p.col + ',' + p.alpha.toFixed(3) + ')';
      ctx.lineWidth   = (1 - prog) * 2.5 + 0.4;
      ctx.stroke();
    }
    ctx.restore();

    /* ── HUD overlay ── */
    ctx.save();
    ctx.font      = '300 8px "DM Mono",monospace';
    ctx.fillStyle = 'rgba(80,160,255,0.18)';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'bottom';
    ctx.fillText(
      'NEURAL CORE  |  RISK ' + Math.round(risk) +
      '  CONF ' + Math.round(conf) +
      '  WL ' + Math.round(waterline) +
      '  NODES ' + NODES.length +
      '  EDGES ' + EDGES.length +
      (thinking ? '  [THINKING]' : ''),
      14, H - 14
    );
    ctx.restore();

    requestAnimationFrame(loop);
  }

  /* ── UTILS ─────────────────────────────────────── */
  function riskColor(danger) {
    if (danger > 0.7) return '255,60,40';
    if (danger > 0.4) return '255,160,40';
    return '80,200,255';
  }

  /* ── INIT ─────────────────────────────────────── */
  resize();
  requestAnimationFrame(loop);

  /* ── PUBLIC ────────────────────────────────────── */
  if (!window.KD) window.KD = {};
  window.KD.brainFire = function (nodeIndex) { fireSignal(nodeIndex || 0); };
  window.KD.brainPulse = function (x, y, col) { spawnPulseWave(x || W / 2, y || H / 2, col); };
  window.KD.brainNodes = function () { return NODES.length; };

})();
