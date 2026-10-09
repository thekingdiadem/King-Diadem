/* ============================================================
   KING DIADEM — warp_intro.js
   ★ Dark warp intro — gold + teal streaks from center
   ★ Hook KD_thinking / KD_answer into run()
   ============================================================ */

/* ── DARK WARP INTRO ── */
(function () {
  var cv = document.getElementById('warp-canvas');
  if (!cv) return;
  var ctx = cv.getContext('2d');
  var W, H, stars = [];

  function resize() { W = cv.width = window.innerWidth; H = cv.height = window.innerHeight; }
  resize();

  /* generate streaks — ทอง · ฟ้า · กุหลาบ (ร้อนสลับเย็น เหมือนแท็บจักรวาล) */
  for (var i = 0; i < 320; i++) {
    var a = Math.random() * Math.PI * 2;
    var d = Math.random() * Math.max(W, H) * 0.58 + 20;
    var r0 = Math.random(), gold = r0 > 0.5, rose = !gold && r0 > 0.32;
    stars.push({
      a: a, d: 0, maxD: d,
      vd: d * 0.018 + 2,
      done: false,
      gold: gold, rose: rose,
    });
  }

  var t = 0;
  function frame() {
    if (t > 3200) return;
    t += 16;

    /* dark fade trail */
    ctx.fillStyle = 'rgba(2,1,10,0.20)';
    ctx.fillRect(0, 0, W, H);

    var cx = W * 0.5, cy = H * 0.5;
    stars.forEach(function (s) {
      if (s.done) return;
      s.d = Math.min(s.d + s.vd * (1 + t / 800), s.maxD);
      if (s.d >= s.maxD) { s.done = true; }

      var x  = cx + Math.cos(s.a) * s.d;
      var y  = cy + Math.sin(s.a) * s.d * 0.52;
      var len = s.vd * (1 + t / 380);
      var tx = cx + Math.cos(s.a) * (s.d - len);
      var ty = cy + Math.sin(s.a) * (s.d - len) * 0.52;

      var progress = s.d / s.maxD;
      var alpha    = 0.35 + progress * 0.55;

      var g = ctx.createLinearGradient(tx, ty, x, y);
      g.addColorStop(0, 'rgba(0,0,0,0)');
      if (s.gold) {
        g.addColorStop(1, 'rgba(255,205,130,' + alpha + ')');
      } else if (s.rose) {
        g.addColorStop(1, 'rgba(255,150,195,' + alpha * 0.85 + ')');
      } else {
        g.addColorStop(1, 'rgba(130,180,255,' + alpha + ')');
      }
      ctx.strokeStyle = g;
      ctx.lineWidth   = 0.7 + progress * 1.4;
      ctx.beginPath();
      ctx.moveTo(tx, ty);
      ctx.lineTo(x, y);
      ctx.stroke();
    });

    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);

  /* remove intro screen after animation */
  setTimeout(function () {
    var el = document.getElementById('intro-screen');
    if (el) {
      el.style.transition = 'opacity 0.6s ease';
      el.style.opacity    = '0';
      setTimeout(function () { el.style.display = 'none'; }, 650);
    }
  }, 3600);
})();

/* ── Hook KD_thinking + KD_answer into run() ── */
(function () {
  /* Wait for run() to be defined */
  var _hookTimer = setInterval(function () {
    if (typeof window.run !== 'function') return;
    clearInterval(_hookTimer);

    var _origRun = window.run;
    window.run = function () {
      /* trigger thinking mode on galaxy */
      if (typeof window.KD_thinking === 'function') {
        window.KD_thinking();
      }
      return _origRun.apply(this, arguments);
    };

    /* patch addMsg to detect when AI response arrives */
    var _origAddMsg = window.addMsg;
    if (typeof _origAddMsg === 'function') {
      window.addMsg = function (type, text, meta, persona) {
        if (type !== 'user' && type !== 'thinking' && typeof window.KD_answer === 'function') {
          window.KD_answer();
        }
        return _origAddMsg.apply(this, arguments);
      };
    }
  }, 50);
})();
