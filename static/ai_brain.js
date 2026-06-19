/**
 * static/brain.js — KING DIADEM AI Core Bridge v2.0
 * Fetches /ai/brain + syncs state to window.KD
 * Triggers orbital + neural visual responses on state change
 */
(function () {
  'use strict';

  var POLL_MS  = 5000;
  var _polling = false;
  var _last    = {};

  /* ── FETCH ─────────────────────────────────────── */
  async function loadBrain() {
    try {
      var res  = await fetch('/ai/brain', { credentials: 'same-origin' });
      if (!res.ok) return;
      var data = await res.json();

      if (!window.KD) window.KD = {};
      if (!window.KD.state) window.KD.state = {};

      /* Merge brain data into KD state */
      if (data.risk)      window.KD.state.risk      = data.risk;
      if (data.consensus) window.KD.state.consensus  = data.consensus;
      if (data.entropy    != null) window.KD.state.entropy   = +data.entropy;
      if (data.stability  != null) window.KD.state.stability = +data.stability;
      if (data.resources  != null) window.KD.state.resources = +data.resources;
      if (data.waterline  != null) window.KD.state.waterline = +data.waterline;
      if (data.thinking   != null) window.KD.state.thinking  = !!data.thinking;

      /* Detect significant risk change → trigger visuals */
      var risk = +(data.risk && data.risk.risk_score) || 0;
      if (Math.abs(risk - (_last.risk || 0)) > 15) {
        triggerVisualResponse(risk);
      }
      _last.risk = risk;

      /* Detect thinking state transition */
      if (data.thinking && !_last.thinking) {
        if (typeof window.KD.orbitWarp === 'function')  window.KD.orbitWarp();
        if (typeof window.KD.brainPulse === 'function') window.KD.brainPulse();
      }
      _last.thinking = !!data.thinking;

      console.log('[KD Brain] state synced — risk:', Math.round(risk), '| WL:', Math.round(+(data.waterline || 0)));

    } catch (e) {
      console.warn('[KD Brain] fetch failed:', e.message);
    }
  }

  /* ── VISUAL RESPONSE ───────────────────────────── */
  function triggerVisualResponse(risk) {
    var x = window.innerWidth  * 0.50;
    var y = window.innerHeight * 0.50;

    if (risk > 75) {
      /* High risk — red burst */
      if (typeof window.KD.orbitBurst === 'function') window.KD.orbitBurst(x, y, 10);
      if (typeof window.KD.brainPulse === 'function') window.KD.brainPulse(x, y, '255,60,40');
    } else if (risk > 45) {
      /* Medium risk — amber */
      if (typeof window.KD.orbitBurst === 'function') window.KD.orbitBurst(x, y, 36);
      if (typeof window.KD.brainPulse === 'function') window.KD.brainPulse(x, y, '255,160,40');
    } else {
      /* Low risk — blue calm */
      if (typeof window.KD.brainFire  === 'function') window.KD.brainFire(Math.floor(Math.random() * 38));
      if (typeof window.KD.brainPulse === 'function') window.KD.brainPulse(x, y, '80,200,255');
    }

    /* Galaxy scene sync */
    if (typeof window.KD_setState === 'function') {
      if (window.KD.state.entropy   != null) window.KD_setState('entropy',   window.KD.state.entropy);
      if (window.KD.state.stability != null) window.KD_setState('stability', window.KD.state.stability);
      if (window.KD.state.resources != null) window.KD_setState('resources', window.KD.state.resources);
    }
  }

  /* ── POLL LOOP ─────────────────────────────────── */
  function startPolling() {
    if (_polling) return;
    _polling = true;
    loadBrain();
    setInterval(loadBrain, POLL_MS);
  }

  /* ── INIT ─────────────────────────────────────── */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startPolling);
  } else {
    setTimeout(startPolling, 500); /* small delay to let KD canvas init first */
  }

  /* ── PUBLIC ────────────────────────────────────── */
  if (!window.KD) window.KD = {};
  window.KD.loadBrain    = loadBrain;
  window.KD.brainPolling = function () { return _polling; };

})();
