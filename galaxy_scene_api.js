/**
 * galaxy_scene_api.js — KING DIADEM v4.5
 * เชื่อม galaxy_scene.js กับ backend /api/galaxy/*
 * include หลัง galaxy_scene.js ใน index.html
 *
 * FIX v4.5: intercept setRoute/KD_pulse ใน DOMContentLoaded
 *           หลีกเลี่ยง race condition กับ inline script ใน index.html
 */
(function () {
  'use strict';
  var POLL_MS = 5000;

  /* ── poll state จาก backend ── */
  function poll() {
    fetch('/api/galaxy/nodes', { credentials: 'same-origin' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) {
        if (!d) return;
        // sync active route → planet glow
        if (d.active_route) {
          var cur = (document.querySelector('.ctx-tag.active') || {}).dataset || {};
          if (d.active_route !== cur.r) {
            var orig = window._origSetRoute || window.setRoute;
            if (orig) orig(d.active_route);
          }
        }
        // sync lyla mode
        if (d.lyla_mode === 'thinking' && window.LYLA_thinking) window.LYLA_thinking();
        else if (d.lyla_mode === 'burst' && window.LYLA_answered) window.LYLA_answered();
        // sync waterline meters
        var w = d.waterline || {};
        _meter('wl-entropy',   w.entropy,   true);
        _meter('wl-stability', w.stability, false);
        _meter('wl-resource',  w.resource,  false);
        _txt('wl-entropy-val',   Math.round(w.entropy   || 40));
        _txt('wl-stability-val', Math.round(w.stability || 60));
        _txt('wl-resource-val',  Math.round(w.resource  || 50));
        // risk indicators
        if (d.risk_score != null) {
          var rs = Math.round(d.risk_score);
          _txt('lyla-drift',     (rs / 100 * 0.15).toFixed(2) + '%');
          _txt('lyla-choices',   rs > 75 ? 'LOW' : '\u22651');
          _txt('lyla-waterline', rs > 60 ? 'BELOW' : 'ABOVE');
          var wlEl = document.getElementById('lyla-waterline');
          if (wlEl) wlEl.className = 'lyla-val ' + (rs > 60 ? 'warn' : 'safe');
        }
      })
      .catch(function () {});
  }

  function _signal(route, mode) {
    fetch('/api/galaxy/signal', {
      method: 'POST', credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ route: route, lyla_mode: mode }),
    }).catch(function () {});
  }

  function _meter(id, val, inv) {
    var el = document.getElementById(id);
    if (!el) return;
    var p = Math.max(0, Math.min(100, val || 0));
    el.style.width = p + '%';
    var c = inv ? (p > 72 ? 'crit' : p > 48 ? 'warn' : 'safe')
                : (p < 28 ? 'crit' : p < 48 ? 'warn' : 'safe');
    el.className = 'wl-fill ' + c;
  }

  function _txt(id, val) {
    var el = document.getElementById(id);
    if (el) el.textContent = val;
  }

  /* ── intercept ใน DOMContentLoaded เพื่อให้ inline script โหลดก่อน ── */
  function wireIntercepts() {
    // setRoute — wire เฉพาะครั้งแรก
    if (window.setRoute && !window._origSetRoute) {
      window._origSetRoute = window.setRoute;
      window.setRoute = function (r) {
        _signal(r, 'idle');
        if (window._origSetRoute) window._origSetRoute.apply(this, arguments);
      };
    }

    // KD_pulse (galaxy_scene.js) — wire เฉพาะครั้งแรก
    if (window.KD_pulse && !window._origKDPulse) {
      window._origKDPulse = window.KD_pulse;
      window.KD_pulse = function (r) {
        if (r) _signal(r, 'burst');
        if (window._origKDPulse) window._origKDPulse.apply(this, arguments);
      };
    }

    // LYLA_thinking
    var _origThink = window.LYLA_thinking;
    window.LYLA_thinking = function () {
      var r = (document.querySelector('.ctx-tag.active') || {}).dataset || {};
      _signal(r.r || 'general', 'thinking');
      if (_origThink) _origThink.apply(this, arguments);
    };

    // LYLA_answered
    var _origAnswer = window.LYLA_answered;
    window.LYLA_answered = function () {
      var r = (document.querySelector('.ctx-tag.active') || {}).dataset || {};
      _signal(r.r || 'general', 'burst');
      if (_origAnswer) _origAnswer.apply(this, arguments);
    };
  }

  /* ── start ── */
  function start() {
    wireIntercepts();
    poll();
    setInterval(poll, POLL_MS);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    // defer ไป microtask เพื่อให้ inline scripts execute ครบก่อน
    Promise.resolve().then(start);
  }

})();
