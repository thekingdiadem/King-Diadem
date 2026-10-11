/* cinema_sky.js — ฟ้าดาวบางๆ ที่ใช้ร่วมกันในหน้ารอง (Wallet · เข้าสู่ระบบ · สมัคร)
   ต้องมี <canvas id="sky"> · ดาวสุ่มกระจายทั่วจอ ไม่มีดวงไหนเป็นศูนย์กลาง · เราเป็นฝ่ายลอยผ่านช้าๆ
   จำกัด ~30 เฟรม/วินาที · หยุดเมื่อแท็บถูกซ่อน · ลดการเคลื่อนไหว = วาดภาพนิ่งครั้งเดียว
   data-density บน canvas = พื้นที่ (px²) ต่อดาวหนึ่งดวง (ค่าเริ่ม 2600 · มากขึ้น = ดาวน้อยลง) */
(function () {
  var cv = document.getElementById('sky'), cx = cv && cv.getContext && cv.getContext('2d');
  if (!cx) return;
  var REDUCED = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var AREA = Number(cv.getAttribute('data-density')) || 2600;
  var S = [], W0 = 0, H0 = 0, last = 0, raf = 0;
  var COL = ['214,224,255', '200,182,240', '255,198,161', '255,217,143', '242,246,255'];
  function size() {
    var dpr = Math.min(2, window.devicePixelRatio || 1); W0 = innerWidth; H0 = innerHeight;
    cv.width = W0 * dpr; cv.height = H0 * dpr; cx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var n = Math.min(420, Math.round(W0 * H0 / AREA)); S = [];
    for (var i = 0; i < n; i++) S.push({ x: Math.random() * W0, y: Math.random() * H0, z: .25 + Math.random() * .75,
      c: COL[i % COL.length], p: Math.random() * 6.28, w: .6 + Math.random() * 1.6 });
  }
  function draw(t) {
    cx.clearRect(0, 0, W0, H0);
    for (var i = 0; i < S.length; i++) {
      var s = S[i], x = (s.x - t * .006 * s.z) % W0, y = (s.y + t * .0016 * s.z) % H0;
      if (x < 0) x += W0;
      var a = (.25 + .55 * s.z) * (.72 + .28 * Math.sin(t * .001 * s.w + s.p)), r = .35 + s.z * .9;
      if (s.z > .93) { cx.fillStyle = 'rgba(' + s.c + ',' + (a * .12).toFixed(3) + ')'; cx.beginPath(); cx.arc(x, y, r * 4, 0, 6.283); cx.fill(); }
      cx.fillStyle = 'rgba(' + s.c + ',' + a.toFixed(3) + ')';
      cx.beginPath(); cx.arc(x, y, r, 0, 6.283); cx.fill();
    }
  }
  function loop(t) { raf = requestAnimationFrame(loop); if (t - last < 33) return; last = t; draw(t); }
  size(); addEventListener('resize', function () { size(); if (REDUCED) draw(0); });
  if (REDUCED) { draw(0); return; }
  raf = requestAnimationFrame(loop);
  document.addEventListener('visibilitychange', function () { cancelAnimationFrame(raf); if (!document.hidden) raf = requestAnimationFrame(loop); });
})();
