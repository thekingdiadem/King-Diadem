// static/ai_thinking.js — KING DIADEM
(function () {
  'use strict';

  var _timer = null;
  var _dots  = 0;
  var _FRAMES = ['', '.', '..', '...'];

  function _el() {
    return document.getElementById('thinking');
  }

  function start() {
    if (_timer) return;
    var node = _el();
    if (node) { node.style.display = 'block'; }
    _dots = 0;
    _timer = setInterval(function () {
      var n = _el();
      if (!n) return;
      _dots = (_dots + 1) % 4;
      n.textContent = 'Thinking' + _FRAMES[_dots];
    }, 450);
  }

  function stop() {
    clearInterval(_timer);
    _timer = null;
    _dots  = 0;
    var node = _el();
    if (node) { node.style.display = 'none'; node.textContent = ''; }
  }

  // Public API
  window.KDThinking = { start: start, stop: stop };

  // Hook KD:thinking / KD:response events
  window.addEventListener('KD:thinking', start);
  window.addEventListener('KD:response', stop);

  // Hook galaxy API ถ้ามี
  var _origThink = window.LYLA_thinking;
  window.LYLA_thinking = function () {
    start();
    if (typeof _origThink === 'function') _origThink.apply(this, arguments);
  };
  var _origAnswered = window.LYLA_answered;
  window.LYLA_answered = function () {
    stop();
    if (typeof _origAnswered === 'function') _origAnswered.apply(this, arguments);
  };

})();
