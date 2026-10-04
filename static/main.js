/**
 * static/main.js — KING DIADEM Core Bridge v3.0
 * Full integration: galaxy_scene + ai_orbit + ai_brain + backend
 * FATE™ Deterministic Decision Infrastructure
 * "Fail less. Harm less. Restore more."
 */
(function () {
  'use strict';

  /* ══════════════════════════════════════════
     STATE — single source of truth
  ══════════════════════════════════════════ */
  var KD_STATE = {
    input:      '',
    energy:     50,
    food:       false,
    safe:       false,
    mode:       'general',
    thinking:   false,
    lastRisk:   0,
    sessionId:  null,
    msgCount:   0,
  };

  /* ══════════════════════════════════════════
     VISUAL SYNC — galaxy + orbit + brain
  ══════════════════════════════════════════ */
  function syncVisuals(data) {
    if (!data) return;

    /* Galaxy STATE sync */
    if (typeof window.KD_setState === 'function') {
      if (data.entropy   != null) window.KD_setState('entropy',   +data.entropy);
      if (data.stability != null) window.KD_setState('stability', +data.stability);
      if (data.resources != null) window.KD_setState('resources', +data.resources);
      if (data.waterline != null) window.KD_setState('waterline', +data.waterline);
    }

    /* Route sync */
    var route = data.route || data.active_route || KD_STATE.mode;
    if (route && typeof window.KD_setRoute === 'function') {
      window.KD_setRoute(route);
    }

    /* Orbit + Brain state */
    if (!window.KD) window.KD = {};
    if (!window.KD.state) window.KD.state = {};
    if (data.risk)      window.KD.state.risk      = data.risk;
    if (data.consensus) window.KD.state.consensus  = data.consensus;
    if (data.entropy    != null) window.KD.state.entropy   = +data.entropy;
    if (data.stability  != null) window.KD.state.stability = +data.stability;
    if (data.resources  != null) window.KD.state.resources = +data.resources;
    if (data.waterline  != null) window.KD.state.waterline = +data.waterline;

    /* Risk-based visual burst */
    var risk = +(data.risk && data.risk.risk_score) || 0;
    var cx = window.innerWidth  * 0.50;
    var cy = window.innerHeight * 0.50;

    if (Math.abs(risk - KD_STATE.lastRisk) > 12) {
      if (risk > 75) {
        if (typeof window.KD_shockwave === 'function') window.KD_shockwave(cx, cy, '255,60,40');
        if (typeof window.KD.orbitBurst === 'function') window.KD.orbitBurst(cx, cy, 10);
        if (typeof window.KD.brainPulse === 'function') window.KD.brainPulse(cx, cy, '255,60,40');
      } else if (risk > 45) {
        if (typeof window.KD_shockwave === 'function') window.KD_shockwave(cx, cy, '255,160,40');
        if (typeof window.KD.orbitBurst === 'function') window.KD.orbitBurst(cx, cy, 36);
        if (typeof window.KD.brainPulse === 'function') window.KD.brainPulse(cx, cy, '255,160,40');
      } else {
        if (typeof window.KD_pulse === 'function') window.KD_pulse(route);
        if (typeof window.KD.brainPulse === 'function') window.KD.brainPulse(cx, cy, '80,200,255');
      }
      KD_STATE.lastRisk = risk;
    }
  }

  function setThinkingMode(on) {
    KD_STATE.thinking = on;
    if (!window.KD) window.KD = {};
    if (!window.KD.state) window.KD.state = {};
    window.KD.state.thinking = on;

    if (on) {
      if (typeof window.LYLA_thinking === 'function')  window.LYLA_thinking();
      if (typeof window.KD_council === 'function')     window.KD_council();
      if (typeof window.KD.orbitWarp === 'function')   window.KD.orbitWarp();
      if (typeof window.KD.brainPulse === 'function')  window.KD.brainPulse();
    } else {
      if (typeof window.LYLA_answered === 'function')  window.LYLA_answered();
      if (typeof window.KD_councilEnd === 'function')  window.KD_councilEnd();
    }
  }

  /* ══════════════════════════════════════════
     WATERLINE DISPLAY
  ══════════════════════════════════════════ */
  function updateWaterlineUI(data) {
    var wl = data && data.waterline != null ? Math.round(+data.waterline) : null;
    if (wl === null) return;

    var wlEl  = document.getElementById('wl-entropy-val')   || document.getElementById('lyla-waterline');
    var driftEl = document.getElementById('lyla-drift');
    var choiceEl = document.getElementById('lyla-choices');

    var risk = +(data.risk && data.risk.risk_score) || 0;
    if (driftEl)  driftEl.textContent  = (risk / 100 * 0.15).toFixed(2) + '%';
    if (choiceEl) choiceEl.textContent = risk > 75 ? 'LOW' : '≥1';
    if (wlEl)     wlEl.textContent     = wl;

    /* Waterline bar meters */
    _meter('wl-entropy',   data.entropy,   true);
    _meter('wl-stability', data.stability, false);
    _meter('wl-resource',  data.resources, false);
    _txt('wl-entropy-val',   Math.round(+(data.entropy   || 40)));
    _txt('wl-stability-val', Math.round(+(data.stability || 60)));
    _txt('wl-resource-val',  Math.round(+(data.resources || 50)));
  }

  function _meter(id, val, inv) {
    var el = document.getElementById(id); if (!el) return;
    var p  = Math.max(0, Math.min(100, +(val || 0)));
    el.style.width = p + '%';
    var c  = inv ? (p > 72 ? 'crit' : p > 48 ? 'warn' : 'safe')
                 : (p < 28 ? 'crit' : p < 48 ? 'warn' : 'safe');
    el.className = 'wl-fill ' + c;
  }

  function _txt(id, val) {
    var el = document.getElementById(id); if (el) el.textContent = val;
  }

  /* ══════════════════════════════════════════
     MAIN RUN — called by chat send
  ══════════════════════════════════════════ */
  window.run = async function () {
    var inputEl  = document.getElementById('input') || document.getElementById('chat-input');
    var energyEl = document.getElementById('energy');
    var foodEl   = document.getElementById('food');
    var safeEl   = document.getElementById('safe');
    var modeEl   = document.getElementById('mode');
    var outputEl = document.getElementById('output');

    var input = inputEl ? inputEl.value.trim() : '';
    if (!input) return;

    KD_STATE.input   = input;
    KD_STATE.energy  = energyEl  ? +energyEl.value  : 50;
    KD_STATE.food    = foodEl    ? foodEl.checked    : false;
    KD_STATE.safe    = safeEl    ? safeEl.checked    : false;
    KD_STATE.mode    = modeEl    ? modeEl.value      : 'general';
    KD_STATE.msgCount++;

    /* Set route immediately */
    if (typeof window.KD_setRoute === 'function') window.KD_setRoute(KD_STATE.mode);
    if (typeof window.setRoute    === 'function') window.setRoute(KD_STATE.mode);

    /* Thinking ON */
    setThinkingMode(true);

    /* Clear output */
    if (outputEl) outputEl.textContent = '';

    try {
      var res = await fetch('/run', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({
          input:    KD_STATE.input,
          energy:   KD_STATE.energy,
          food:     KD_STATE.food,
          safe:     KD_STATE.safe,
          route:    KD_STATE.mode,      // /run อ่าน route (เดิมส่ง mode → ถูกเมิน ได้ general เสมอ)
        }),
      });

      if (!res.ok) throw new Error('HTTP ' + res.status);
      var data = await res.json();

      /* Sync visuals */
      syncVisuals(data);
      updateWaterlineUI(data);

      /* Output */
      if (outputEl) {
        var reply = data.ai_response || data.response;   // /run ตอบใน ai_response
        outputEl.textContent = typeof reply === 'string' ? reply : (data.error || '');
      }

      /* Session tracking */
      if (data.session_id) KD_STATE.sessionId = data.session_id;

      console.log('[KD Main] response — risk:', Math.round(+(data.risk && data.risk.risk_score) || 0), '| WL:', Math.round(+(data.waterline || 0)));

    } catch (e) {
      console.error('[KD Main] run failed:', e.message);
      if (outputEl) outputEl.textContent = '[SYSTEM ERROR] ' + e.message;
      if (typeof window.KD_setState === 'function') {
        window.KD_setState('entropy', 80);
      }
    } finally {
      setThinkingMode(false);
    }
  };

  /* ══════════════════════════════════════════
     CHAT SEND (index.html chat UI)
  ══════════════════════════════════════════ */
  window.sendMessage = async function (text, route) {
    var input = text || (document.getElementById('chat-input') || {}).value || '';
    input = input.trim();
    if (!input) return;

    var r = route || KD_STATE.mode;
    if (typeof window.KD_setRoute === 'function') window.KD_setRoute(r);
    if (typeof window.setRoute    === 'function') window.setRoute(r);

    setThinkingMode(true);
    KD_STATE.msgCount++;

    try {
      // เดิมยิง /chat ซึ่งไม่มีใน app.py (404 ทุกครั้ง) → ใช้ /run ตัวเดียวกับหน้าแชท
      var res = await fetch('/run', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({
          input:    input,
          route:    r,
        }),
      });

      if (!res.ok) throw new Error('HTTP ' + res.status);
      var data = await res.json();

      syncVisuals(data);
      updateWaterlineUI(data);

      if (data.session_id) KD_STATE.sessionId = data.session_id;

      return data;

    } catch (e) {
      console.error('[KD Main] sendMessage failed:', e.message);
      return { error: e.message };
    } finally {
      setThinkingMode(false);
    }
  };

  /* ══════════════════════════════════════════
     SIMULATE — /simulate endpoint
  ══════════════════════════════════════════ */
  window.simulate = async function (scenario) {
    setThinkingMode(true);
    if (typeof window.KD_setRoute === 'function') window.KD_setRoute('collapse');

    try {
      var res = await fetch('/simulate', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({ scenario: scenario || KD_STATE.input }),
      });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      var data = await res.json();
      syncVisuals(data);
      return data;
    } catch (e) {
      console.error('[KD Simulate]', e.message);
      return { error: e.message };
    } finally {
      setThinkingMode(false);
    }
  };

  /* ══════════════════════════════════════════
     KEYBOARD — Enter to send
  ══════════════════════════════════════════ */
  document.addEventListener('DOMContentLoaded', function () {
    var inputs = ['input', 'chat-input'];
    inputs.forEach(function (id) {
      var el = document.getElementById(id);
      if (!el) return;
      el.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          if (typeof window.run === 'function') window.run();
        }
      });
    });

    /* Mode select sync → galaxy route */
    var modeEl = document.getElementById('mode');
    if (modeEl) {
      modeEl.addEventListener('change', function () {
        KD_STATE.mode = modeEl.value;
        if (typeof window.KD_setRoute === 'function') window.KD_setRoute(KD_STATE.mode);
        if (typeof window.setRoute    === 'function') window.setRoute(KD_STATE.mode);
      });
    }
  });

  /* ══════════════════════════════════════════
     PUBLIC API
  ══════════════════════════════════════════ */
  if (!window.KD) window.KD = {};
  window.KD.getState   = function () { return Object.assign({}, KD_STATE); };
  window.KD.setState   = function (k, v) { if (k in KD_STATE) KD_STATE[k] = v; };
  window.KD.syncVisual = syncVisuals;
  window.KD.thinking   = function (on) { setThinkingMode(on); };
  window.KD.loadBrain  = window.KD.loadBrain || function () {};

  console.log('[KD Main v3.0] loaded — FATE™ DETERMINISTIC · Fail less · Harm less · Restore more');

})();
