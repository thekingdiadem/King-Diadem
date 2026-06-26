// static/system.js
// KING DIADEM™ — System Kernel v2.1
// Patched: resize throttle · RAF scheduling · safe canvas DPR

window.KD = window.KD || {};
window.KD.apiUrl = "/run";   // was /ENGINE — align with actual backend
window.KD.state  = {};

// ─── DOM HELPERS ──────────────────────────────────────────────────────────────
window.KD.byId = function(id){ return document.getElementById(id); };

window.KD.getValue = function(id, fallback){
  fallback = fallback === undefined ? "" : fallback;
  var el = window.KD.byId(id);
  if(!el) return fallback;
  return el.value !== undefined ? el.value : fallback;
};

window.KD.setText = function(id, value){
  var el = window.KD.byId(id);
  if(!el) return;
  el.textContent = value == null ? "" : String(value);
};

window.KD.setValue = function(id, value){
  var el = window.KD.byId(id);
  if(!el) return;
  el.value = value == null ? "" : String(value);
};

window.KD.clamp = function(value, low, high){
  low  = low  === undefined ? 0   : low;
  high = high === undefined ? 100 : high;
  var n = Number(value);
  if(!Number.isFinite(n)) return low;
  return Math.max(low, Math.min(high, n));
};

window.KD.readInputs = function(){
  return {
    input:      window.KD.getValue("input", ""),
    entropy:    Number(window.KD.getValue("entropy",    40))  || 40,
    resource:   Number(window.KD.getValue("resource",   50))  || 50,
    stability:  Number(window.KD.getValue("stability",  60))  || 60,
    choices:    Number(window.KD.getValue("choices",     1))  || 1,
    confidence: Number(window.KD.getValue("confidence", 0.5)) || 0.5,
  };
};

window.KD.writeJSON = function(id, value){
  window.KD.setText(id, JSON.stringify(value, null, 2));
};

window.KD.setState = function(nextState){
  window.KD.state = nextState || {};
  window.dispatchEvent(new CustomEvent("KD:response", { detail: window.KD.state }));
};

// ─── CANVAS RESIZE — throttled, RAF-scheduled ─────────────────────────────────
// FIX: raw resize on every event caused galaxy re-init every frame → lag spike
var _kdResizeTimer = null;

window.KD.resizeCanvas = function(canvas){
  if(!canvas) return null;
  var dpr = Math.min(window.devicePixelRatio || 1, 2); // cap at 2× — no need for 3×
  var cssW = window.innerWidth;
  var cssH = window.innerHeight;
  var w = Math.floor(cssW * dpr);
  var h = Math.floor(cssH * dpr);

  // avoid redundant resize — only resize if dimensions actually changed
  if(canvas.width === w && canvas.height === h) {
    var ctx = canvas.getContext("2d");
    return ctx;
  }

  canvas.width  = w;
  canvas.height = h;
  canvas.style.width  = "100%";
  canvas.style.height = "100%";

  var ctx = canvas.getContext("2d");
  if(ctx) ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return ctx;
};

// Throttled global resize dispatcher — fires at most once per 200ms
// galaxy_scene.js should listen to "KD:resize" instead of raw "resize"
(function(){
  var _raf = null;
  function onResize(){
    if(_raf) return;
    _raf = requestAnimationFrame(function(){
      _raf = null;
      window.dispatchEvent(new CustomEvent("KD:resize", {
        detail: { w: window.innerWidth, h: window.innerHeight }
      }));
    });
  }
  window.addEventListener("resize", onResize, { passive: true });
})();

// ─── EVENT BUS ────────────────────────────────────────────────────────────────
window.KD.bind = function(id, event, handler){
  var el = window.KD.byId(id);
  if(!el) return;
  el.addEventListener(event, handler);
};

// ─── FETCH UTILS ──────────────────────────────────────────────────────────────
// Centralized fetch with timeout — avoids Render cold-start hanging forever
window.KD.fetchJSON = async function(url, opts, timeoutMs){
  timeoutMs = timeoutMs || 15000;
  var controller = new AbortController();
  var timer = setTimeout(function(){ controller.abort(); }, timeoutMs);
  opts = opts || {};
  opts.signal = controller.signal;
  try {
    var res = await fetch(url, opts);
    clearTimeout(timer);
    return res;
  } catch(e) {
    clearTimeout(timer);
    if(e.name === "AbortError") throw new Error("Request timeout — backend ไม่ตอบสนอง");
    throw e;
  }
};

// ─── VISIBILITY API — pause RAF when tab hidden ────────────────────────────────
// galaxy_scene.js should check window.KD.visible before animating
window.KD.visible = true;
document.addEventListener("visibilitychange", function(){
  window.KD.visible = !document.hidden;
  window.dispatchEvent(new CustomEvent("KD:visibility", { detail: { visible: window.KD.visible } }));
}, { passive: true });

// ─── USER EMAIL ───────────────────────────────────────────────────────────────
Object.defineProperty(window.KD, "userEmail", {
  get: function(){ return window.__kdUserEmail || null; },
  enumerable: true,
});
