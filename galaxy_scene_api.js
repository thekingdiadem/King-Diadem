/**
 * galaxy_scene_api.js — KING DIADEM v4.6 STABLE
 * เชื่อม galaxy_scene.js กับ backend /api/galaxy/*
 */
(function () {
  'use strict';
  var POLL_MS = 6000;
  var _wired = false;

  function poll() {
    fetch('/api/galaxy/nodes', { credentials: 'same-origin' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) {
        if (!d) return;
        if (d.active_route) {
          var cur = (document.querySelector('.ctx-tag.active') || {}).dataset || {};
          if (d.active_route !== cur.r) {
            var orig = window._origSetRoute || window.setRoute;
            if (typeof orig === 'function') orig(d.active_route);
          }
        }
        if (d.lyla_mode === 'thinking' && typeof window.LYLA_thinking === 'function') window.LYLA_thinking();
        else if (d.lyla_mode === 'burst' && typeof window.LYLA_answered === 'function') window.LYLA_answered();
        var w = d.waterline || {};
        _meter('wl-entropy',   w.entropy,   true);
        _meter('wl-stability', w.stability, false);
        _meter('wl-resource',  w.resource,  false);
        _txt('wl-entropy-val',   Math.round(w.entropy   || 40));
        _txt('wl-stability-val', Math.round(w.stability || 60));
        _txt('wl-resource-val',  Math.round(w.resource  || 50));
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

  function wireIntercepts() {
    if (_wired) return;
    _wired = true;

    if (typeof window.setRoute === 'function' && !window._origSetRoute) {
      window._origSetRoute = window.setRoute;
      window.setRoute = function (r) {
        _signal(r, 'idle');
        window._origSetRoute.apply(this, arguments);
      };
    }

    if (typeof window.KD_pulse === 'function' && !window._origKDPulse) {
      window._origKDPulse = window.KD_pulse;
      window.KD_pulse = function (r) {
        if (r) _signal(r, 'burst');
        window._origKDPulse.apply(this, arguments);
      };
    }

    var _origThink = window.LYLA_thinking;
    window.LYLA_thinking = function () {
      var r = (document.querySelector('.ctx-tag.active') || {}).dataset || {};
      _signal(r.r || 'general', 'thinking');
      if (typeof _origThink === 'function') _origThink.apply(this, arguments);
    };

    var _origAnswer = window.LYLA_answered;
    window.LYLA_answered = function () {
      var r = (document.querySelector('.ctx-tag.active') || {}).dataset || {};
      _signal(r.r || 'general', 'burst');
      if (typeof _origAnswer === 'function') _origAnswer.apply(this, arguments);
    };
  }

  function start() {
    wireIntercepts();
    poll();
    setInterval(poll, POLL_MS);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    Promise.resolve().then(start);
  }

})();
