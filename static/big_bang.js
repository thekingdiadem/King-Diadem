/* KING DIADEM — ฉากกำเนิดจักรวาล (บิ๊กแบง) ก่อนเข้าหน้า The Universe
 *
 * จุดเดียว → ระเบิด → อวกาศขยาย → ซุปอนุภาคร้อน → หมอกจาง แสงแรก → ดาวดวงแรก → กาแล็กซีหมุนวน → วันนี้
 * เวลาและอุณหภูมิในแต่ละช่วงเป็นค่าโดยประมาณตามจักรวาลวิทยาปัจจุบัน
 *
 * ลูกเล่น:
 *  · แตะจุดกลางจอ (หรือรอสักครู่) = จุดประกายบิ๊กแบง
 *  · แตะระหว่างฉาก = คลื่นกระแทกผลักอนุภาคออกจากจุดนั้น
 *  · กดค้างแล้วลาก = หลุมแรงโน้มถ่วงดึงอนุภาคเข้าหานิ้ว
 *  · ปุ่ม "ข้าม" หรือ Esc = ข้ามทันที · ปุ่ม "บิ๊กแบง" ในหน้า = เล่นอีกครั้ง
 * เล่นเองครั้งแรกที่เปิดหน้าในแต่ละรอบเท่านั้น · ลดการเคลื่อนไหว = ไม่เล่นเอง และถ้ากดเล่นจะเป็นภาพนิ่งทีละช่วง
 * วาดด้วยการ์ดจอ (static/big_bang_gl.js) ได้หลักแสนอนุภาค · เครื่องที่ไม่มี WebGL ใช้ Canvas 2D ในไฟล์นี้
 * เสียงสร้างจากโค้ด (Web Audio) ปิดไว้ก่อน ผู้ใช้กดเปิดเอง · จำกัดความละเอียด · หยุดวาดเมื่อซ่อนแท็บ */
(function () {
  'use strict';
  var root = document.getElementById('big-bang');
  if (!root) return;
  var cv = root.querySelector('canvas');
  // การ์ดจอก่อน — canvas ใบเดียวขอได้แค่บริบทเดียว จึงต้องลอง WebGL ก่อน 2D
  var GL = null;
  try { GL = window.KD_BigBangGL ? window.KD_BigBangGL(cv) : null; } catch (e) { GL = null; }
  var ctx = GL ? null : (cv.getContext && cv.getContext('2d'));
  if (!GL && !ctx) { root.remove(); return; }
  var capEl = document.getElementById('bb-cap'), timeEl = document.getElementById('bb-time'),
      tempEl = document.getElementById('bb-temp'), hintEl = document.getElementById('bb-hint'),
      skipEl = document.getElementById('bb-skip'), sndEl = document.getElementById('bb-snd'),
      tipEl = document.getElementById('bb-tip'), txtEl = document.getElementById('bb-txt');
  var MQ = matchMedia('(prefers-reduced-motion: reduce)');
  function CALM() { return MQ.matches || document.documentElement.classList.contains('kd-calm'); }

  // ยุคของจักรวาลตามเวลาในฉาก · ค่าเวลาและอุณหภูมิเป็นค่าโดยประมาณตามจักรวาลวิทยาปัจจุบัน
  var PHASES = [
    { t: 0,    time: '0 วินาที',          temp: '—',        cap: 'บิ๊กแบง — ทุกอย่างเริ่มจากจุดเดียว' },
    { t: 0.3,  time: '10⁻⁴³ วินาที',      temp: '10³² K',   cap: 'ยุคพลังค์ — แรงทั้งสี่ของธรรมชาติยังรวมเป็นหนึ่งเดียว' },
    { t: 0.6,  time: '10⁻³⁶ วินาที',      temp: '10²⁸ K',   cap: 'อวกาศขยายตัวพรวดเดียว ใหญ่ขึ้นหลายล้านล้านเท่า' },
    { t: 1.7,  time: '10⁻¹² วินาที',      temp: '10¹⁵ K',   cap: 'ซุปควาร์กและกลูออน — อนุภาคกับปฏิยานุภาคเกิดขึ้นแล้วดับไปไม่หยุด' },
    { t: 2.4,  time: '10⁻⁶ วินาที',       temp: '10¹² K',   cap: 'ควาร์กจับกลุ่มกันเป็นโปรตอนและนิวตรอน' },
    { t: 3.0,  time: '1 วินาที',          temp: '10¹⁰ K',   cap: 'สสารกับปฏิสสารชนกันหายไป เหลือสสารราว 1 ในพันล้าน — คือทุกสิ่งที่มีอยู่วันนี้' },
    { t: 3.8,  time: '3 นาที',            temp: '10⁹ K',    cap: 'นิวเคลียสของไฮโดรเจนและฮีเลียมก่อตัว' },
    { t: 4.8,  time: '380,000 ปี',        temp: '3,000 K',  cap: 'อะตอมแรกเกิดขึ้น หมอกจางลง แสงแรกเดินทางได้อิสระ' },
    { t: 5.8,  time: '10 ล้านปี',         temp: '400 K',    cap: 'ยุคมืด — ยังไม่มีดาวสักดวง มีแต่ก๊าซที่ค่อยๆ รวมตัว' },
    { t: 6.4,  time: '100 ล้านปี',        temp: '60 K',     cap: 'ดาวดวงแรกจุดประกาย' },
    { t: 7.2,  time: '500 ล้านปี',        temp: '30 K',     cap: 'แสงจากดาวรุ่นแรกทำให้ก๊าซทั่วจักรวาลแตกตัวอีกครั้ง ฟ้าเริ่มโปร่ง' },
    { t: 8.0,  time: '1,000 ล้านปี',      temp: '20 K',     cap: 'แรงโน้มถ่วงรวบดาวเป็นกาแล็กซีหมุนวน' },
    { t: 9.8,  time: '5,000 ล้านปี',      temp: '6 K',      cap: 'ทางช้างเผือกค่อยๆ เป็นจานเกลียวอย่างที่เห็นวันนี้' },
    { t: 11.2, time: '9,200 ล้านปี',      temp: '4 K',      cap: 'ดวงอาทิตย์และโลกถือกำเนิดในแขนหนึ่งของทางช้างเผือก' },
    // ดาวลูกไก่ (กระจุกดาวเปิด M45) เกิดราว 100 ล้านปีก่อน — ก่อนไดโนเสาร์สูญพันธุ์
    { t: 12.2, time: '100 ล้านปีก่อน',    temp: '—',        cap: 'เมฆก๊าซในทางช้างเผือกยุบตัว ดาวใหม่เกิดขึ้นพร้อมกันเป็นกระจุก' },
    { t: 13.0, time: '100 ล้านปีก่อน',    temp: '—',        cap: 'ดาวลูกไก่ — ดาวสีฟ้าร้อนจัด ห่างจากเราราว 440 ปีแสง' },
    // ยุคครีเทเชียส (145–66 ล้านปีก่อน) บนพื้นโลก
    { t: 14.0, time: '68 ล้านปีก่อน',     temp: '—',        cap: 'ยุคครีเทเชียส — โลกร้อนชื้น ลมร้อนพัดผ่านป่าสนและเฟิร์น' },
    { t: 15.4, time: '68 ล้านปีก่อน',     temp: '—',        cap: 'ไดโนเสาร์คอยาวเดินเป็นฝูง เทอโรซอร์ร่อนอยู่เหนือฟ้า และนกยุคแรกก็บินอยู่ร่วมกับพวกมัน' },
    { t: 16.8, time: '68 ล้านปีก่อน',     temp: '—',        cap: 'สัตว์เลี้ยงลูกด้วยนมตัวเล็กแอบอยู่ในโพรง — พวกมันมีมาแล้วกว่าร้อยล้านปี แต่ยังต้องหลบซ่อน' },
    { t: 17.8, time: '66 ล้านปีก่อน',     temp: '—',        cap: 'จุดแสงดวงใหม่บนฟ้า สว่างขึ้นทุกคืน' },
    // มองจากอวกาศ: ดาวเคราะห์น้อยชิกซูลุบ (กว้างราว 10 กม.) ชนคาบสมุทรยูคาทาน
    { t: 19.2, time: '66 ล้านปีก่อน',     temp: '—',        cap: 'ดาวเคราะห์น้อยกว้างราว 10 กิโลเมตร พุ่งเข้าหาโลก' },
    { t: 21.6, time: '66 ล้านปีก่อน',     temp: '—',        cap: 'ชนที่คาบสมุทรยูคาทาน คลื่นกระแทกแผ่ไปรอบโลก' },
    { t: 23.0, time: '66 ล้านปีก่อน',     temp: '—',        cap: 'ฝนลูกไฟตกทั่วโลก ฝุ่นและเขม่าบังแสงอาทิตย์อยู่นานหลายปี' },
    // หลังภัยพิบัติบนพื้นโลก
    { t: 25.0, time: '66 ล้านปีก่อน',     temp: '—',        cap: 'ไดโนเสาร์ที่บินไม่ได้สูญพันธุ์ พร้อมสิ่งมีชีวิตราว 3 ใน 4' },
    { t: 26.2, time: '66 ล้านปีก่อน',     temp: '—',        cap: 'แต่สัตว์ตัวเล็กที่ขุดโพรงและกินได้หลายอย่าง รอดมาได้' },
    { t: 27.4, time: '60 ล้านปีก่อน',     temp: '—',        cap: 'เฟิร์นงอกกลับก่อน ป่าค่อยๆ ฟื้น สัตว์เลี้ยงลูกด้วยนมแตกแขนงออกเป็นหลายร้อยชนิด' },
    { t: 28.8, time: '50 ล้านปีก่อน',     temp: '—',        cap: 'นกบางสายรอดมาได้ แล้วแตกแขนงเป็นนกเกือบทุกชนิดที่เห็นวันนี้ — พวกมันคือลูกหลานไดโนเสาร์' },
    { t: 30.0, time: '13,800 ล้านปี',     temp: '2.7 K',    cap: 'และวันนี้ — ดาวลูกไก่ยังส่องอยู่บนฟ้า และเราทุกคนเป็นส่วนหนึ่งของจักรวาลเดียวกัน' }
  ];
  // บทโลกจากอวกาศ: shader เขียนไว้ที่ชน 15.0 แล้วเลื่อนไป 6.6 (หลังบทดาวลูกไก่และยุคครีเทเชียส)
  var EARTH_SHIFT = 6.6, IMPACT = 15.0 + EARTH_SHIFT, END = 31.6, FADE = 1.4;
  // เวลาจริง (วินาที) → เวลาในฉาก: ยุคแรกๆ ที่เกิดเร็วมากได้เวลาดูนานขึ้น ทั้งฉากราว 93 วินาที
  // (เจ้าของโปรเจกต์อยากได้ละเอียด เล่าเป็นเรื่องราวตั้งแต่อนุภาคเกิดดับจนถึงวันนี้ — ใครไม่ดูกดข้ามได้)
  var CLOCK = [[0, 0], [1.5, .3], [3, .6], [6, 1.7], [10, 2.4], [14, 3], [18, 3.8], [22, 4.8], [25, 5.8], [28, 6.4],
               [31, 7.2], [35, 8], [39, 9.8], [42.5, 11.2], [45.5, 12.2], [48, 13], [50.5, 14], [54, 15.4], [57.5, 16.8],
               [60.5, 17.8], [63.5, 19.2], [68.5, 21.6], [72, 23], [75.5, 25], [79, 26.2], [82.5, 27.4], [86.5, 28.8],
               [90, 30], [93, 31.6]];
  function sceneTime(sec) {
    for (var i = 1; i < CLOCK.length; i++) {
      var A = CLOCK[i - 1], B = CLOCK[i];
      if (sec <= B[0]) return A[1] + (B[1] - A[1]) * (sec - A[0]) / (B[0] - A[0]);
    }
    var L = CLOCK[CLOCK.length - 1]; return L[1] + (sec - L[0]) * .6;
  }

  var W = 0, H = 0, DPR = 1, N = 0, P = [], GAL = [], glow = null;
  var state = 'idle', t0 = 0, last = 0, raf = 0, phase = -1, waitTimer = 0, calmTimer = 0, prevFocus = null;
  var ptr = { down: false, x: 0, y: 0, since: 0 }, waves = [], shake = 0, glWaves = [], wellAmt = 0;

  function resize() {
    W = window.innerWidth; H = window.innerHeight;
    if (GL) { DPR = Math.min(1.25, window.devicePixelRatio || 1); GL.resize(W, H, DPR); return; }
    DPR = Math.min(1.5, window.devicePixelRatio || 1);
    cv.width = Math.round(W * DPR); cv.height = Math.round(H * DPR);
    cv.style.width = W + 'px'; cv.style.height = H + 'px';
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
  }

  function sprite() {                         // จุดแสงฟุ้ง ใช้ซ้ำกับดาวสว่างและแกนกาแล็กซี
    var c = document.createElement('canvas'); c.width = c.height = 64;
    var g = c.getContext('2d'), r = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(.18, 'rgba(255,240,210,.75)');
    r.addColorStop(.5, 'rgba(255,200,140,.16)'); r.addColorStop(1, 'rgba(255,200,140,0)');
    g.fillStyle = r; g.fillRect(0, 0, 64, 64); return c;
  }

  function seed() {
    N = Math.round(Math.min(2600, Math.max(900, W * H / 420)));
    var R = Math.min(W, H), k = Math.max(3, Math.min(5, Math.round(W / 300)));
    GAL = [];
    for (var g = 0; g < k; g++) {
      var a = g / k * Math.PI * 2 + Math.random() * .6, d = (g === 0 ? 0 : (.22 + Math.random() * .2)) * R;
      GAL.push({ x: Math.cos(a) * d * (W / R), y: Math.sin(a) * d * .8, r: R * (g === 0 ? .3 : .11 + Math.random() * .07),
                 spin: (Math.random() < .5 ? -1 : 1) * (.25 + Math.random() * .35), tilt: .35 + Math.random() * .6,
                 rot: Math.random() * Math.PI * 2, arms: 2 + (Math.random() < .3 ? 1 : 0) });
    }
    P = [];
    for (var i = 0; i < N; i++) {
      var dir = Math.random() * Math.PI * 2, sp = Math.pow(Math.random(), .5) * R * (1.4 + Math.random() * 1.1);   // ระยะพุ่ง ≈ sp ÷ 2.6 — ยังอยู่ในจอ
      var gi = Math.random() < .45 ? 0 : 1 + Math.floor(Math.random() * (k - 1));
      var gr = Math.pow(Math.random(), 1.6), arm = Math.floor(Math.random() * GAL[gi].arms);
      P.push({ x: 0, y: 0, vx: Math.cos(dir) * sp, vy: Math.sin(dir) * sp, g: gi, gr: gr, arm: arm,
               off: (Math.random() - .5) * .28 * (1.2 - gr), s: .6 + Math.random() * 1.3,
               hue: Math.random(), star: Math.random() < .025, ign: Math.random() < .16 ? 6.4 + Math.random() * 1.6 : 99 });   // ดาวดวงแรกวาบแค่บางดวง
    }
  }

  function col(p, t, a) {                     // สีตามยุค: ขาวฟ้า → ส้มแดง → เหลืองนวล → ฟ้า/ทองของกาแล็กซี
    if (t < 2.8) { var w = Math.min(1, t / 2.8); return 'rgba(' + (255) + ',' + Math.round(255 - w * 60) + ',' + Math.round(255 - w * 150) + ',' + a + ')'; }
    if (t < 4.8) return 'rgba(255,' + Math.round(120 + p.hue * 70) + ',' + Math.round(40 + p.hue * 40) + ',' + a + ')';
    if (t < 8) return 'rgba(255,' + Math.round(200 + p.hue * 40) + ',' + Math.round(150 + p.hue * 60) + ',' + a * .8 + ')';
    return p.gr < .25 ? 'rgba(255,226,170,' + a + ')' : (p.hue < .55 ? 'rgba(170,200,255,' + a + ')' : 'rgba(255,214,160,' + a + ')');
  }

  function target(p, t) {                     // ตำแหน่งในแขนกาแล็กซี (หมุนตามเวลา)
    var G = GAL[p.g], r = p.gr * G.r, a = G.rot + p.arm / G.arms * Math.PI * 2 + p.gr * 4.2 + p.off + G.spin * (t - 8);
    return { x: G.x + Math.cos(a) * r, y: G.y + Math.sin(a) * r * G.tilt };
  }

  function setPhase(i) {
    if (i === phase) return; phase = i;
    var ph = PHASES[i];
    capEl.textContent = ph.cap; timeEl.textContent = ph.time; tempEl.textContent = ph.temp;
    capEl.classList.remove('on'); void capEl.offsetWidth; capEl.classList.add('on');
  }

  function step(now) {
    raf = 0;
    if (state !== 'idle' && state !== 'run' && state !== 'fade') return;
    var dt = Math.min(.05, (now - last) / 1000 || .016); last = now;
    var t = state === 'idle' ? -1 : sceneTime((now - t0) / 1000);
    var cx = W / 2, cy = H / 2;
    if (GL) {
      if (GL.lost()) { close(); return; }
      stepGL(now, t, dt);
    } else {
    ctx.globalCompositeOperation = 'source-over';
    // ทิ้งรอยแสงไว้นิดหน่อยตอนระเบิด แล้วค่อยๆ ใสขึ้น
    ctx.fillStyle = t < 0 ? '#000' : 'rgba(2,3,10,' + (t < 2.8 ? .22 : t < 8 ? .3 : .38) + ')';
    ctx.fillRect(0, 0, W, H);
    var sx = 0, sy = 0;
    if (shake > 0) { sx = (Math.random() - .5) * shake; sy = (Math.random() - .5) * shake; shake *= Math.exp(-dt * 6); if (shake < .3) shake = 0; }

    if (t < 0) {                              // จุดเดียวก่อนเวลาเริ่ม — เต้นเบาๆ รอให้แตะ
      var pul = 1 + Math.sin(now / 260) * .35, rr = 10 * pul;
      ctx.globalCompositeOperation = 'lighter';
      ctx.drawImage(glow, cx - rr * 3, cy - rr * 3, rr * 6, rr * 6);
      ctx.drawImage(glow, cx - rr, cy - rr, rr * 2, rr * 2);
    } else {
      ctx.globalCompositeOperation = 'lighter';
      // แสงวาบตอนระเบิด
      if (t < 1.2) {
        var f = Math.max(0, 1 - t / 1.2), fr = Math.max(W, H) * (.2 + t * 1.4);
        var gr = ctx.createRadialGradient(cx, cy, 0, cx, cy, fr);
        gr.addColorStop(0, 'rgba(255,255,255,' + f + ')'); gr.addColorStop(.4, 'rgba(255,230,190,' + f * .5 + ')'); gr.addColorStop(1, 'rgba(255,200,150,0)');
        ctx.fillStyle = gr; ctx.fillRect(0, 0, W, H);
      }
      // ซุปอนุภาค + หมอก (ฉากหลังอุ่นที่จางลงตอนแสงแรกหลุดออกไป)
      if (t > 1.6 && t < 6.6) {
        var fog = t < 4.8 ? Math.min(1, (t - 1.6) / 1.2) : Math.max(0, 1 - (t - 4.8) / 1.8);
        var fg = ctx.createRadialGradient(cx, cy, 0, cx, cy, Math.max(W, H) * .75);
        fg.addColorStop(0, 'rgba(255,120,50,' + .16 * fog + ')'); fg.addColorStop(1, 'rgba(120,30,20,' + .08 * fog + ')');
        ctx.fillStyle = fg; ctx.fillRect(0, 0, W, H);
      }
      var form = t > 8 ? Math.min(1, (t - 8) / 2.4) : 0;
      var fly = t > 11.4 ? (t - 11.4) : 0, zoom = 1 + fly * fly * .35;
      for (var i = 0; i < waves.length; i++) { waves[i].r += dt * 900; waves[i].a -= dt * 1.4; }
      waves = waves.filter(function (w) { return w.a > 0; });
      for (var j = 0; j < N; j++) {
        var p = P[j];
        if (form > 0) {
          var tg = target(p, t), k = 2.6 * form;
          p.vx += (tg.x - p.x) * k * dt; p.vy += (tg.y - p.y) * k * dt;
          p.vx *= Math.exp(-dt * 2.2); p.vy *= Math.exp(-dt * 2.2);
        } else {
          var damp = t < 2.8 ? 2.6 : 1.4;
          p.vx *= Math.exp(-dt * damp); p.vy *= Math.exp(-dt * damp);
          if (t > 2.8 && t < 4.8) { p.vx += (Math.random() - .5) * 120 * dt * 10; p.vy += (Math.random() - .5) * 120 * dt * 10; }
          if (t > 4.8) { p.vx -= p.x * .05 * dt; p.vy -= p.y * .05 * dt; }      // แรงโน้มถ่วงเริ่มรวบเบาๆ
        }
        if (ptr.down && now - ptr.since > 140) {          // กดค้าง = หลุมแรงโน้มถ่วง
          var dx = (ptr.x - cx) / zoom - p.x, dy = (ptr.y - cy) / zoom - p.y, d2 = dx * dx + dy * dy + 900;
          var pull = 5.2e6 / d2; p.vx += dx / Math.sqrt(d2) * pull * dt; p.vy += dy / Math.sqrt(d2) * pull * dt;
        }
        for (var q = 0; q < waves.length; q++) {          // แตะ = คลื่นกระแทก
          var w = waves[q], ex = p.x - w.x, ey = p.y - w.y, dd = Math.sqrt(ex * ex + ey * ey) + .1;
          if (Math.abs(dd - w.r) < 60) { var push = 1400 * w.a * dt * 4; p.vx += ex / dd * push; p.vy += ey / dd * push; }
        }
        p.x += p.vx * dt; p.y += p.vy * dt;
        var X = cx + p.x * zoom + sx, Y = cy + p.y * zoom + sy;
        if (X < -40 || X > W + 40 || Y < -40 || Y > H + 40) continue;
        var bright = t > p.ign && t < p.ign + .9 ? 1 + (1 - (t - p.ign) / .9) * 3 : 1;    // ดาวดวงแรกวาบขึ้น
        var a = t < 2.8 ? .95 : .7;
        if ((p.star && t > 6.4) || bright > 1.2) {
          var sz = p.s * 6 * bright;
          ctx.globalAlpha = Math.min(1, a * .9); ctx.drawImage(glow, X - sz / 2, Y - sz / 2, sz, sz); ctx.globalAlpha = 1;
        } else {
          ctx.fillStyle = col(p, t, a); var s = p.s * (t < 1 ? 1.8 : t > 8 ? 1.25 : 1);
          ctx.fillRect(X - s / 2, Y - s / 2, s, s);
        }
      }
      if (form > .2) {                                  // แกนกาแล็กซีเรืองแสง
        for (var g = 0; g < GAL.length; g++) {
          var G = GAL[g], gx = cx + G.x * zoom, gy = cy + G.y * zoom, gs = G.r * .55 * zoom * form;
          ctx.globalAlpha = .45 * form; ctx.drawImage(glow, gx - gs / 2, gy - gs * G.tilt / 2, gs, gs * G.tilt); ctx.globalAlpha = 1;
        }
      }
      for (var v = 0; v < waves.length; v++) {           // วงคลื่นกระแทก
        var wv = waves[v]; ctx.strokeStyle = 'rgba(255,230,190,' + wv.a * .5 + ')'; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.arc(cx + wv.x * zoom, cy + wv.y * zoom, wv.r * zoom, 0, Math.PI * 2); ctx.stroke();
      }
      if (t > 12.2 && t < 14.6) pleiades2D(t, cx, cy);
      if (t > 14 && t < 19) land2D(t - 14, 0, cx, cy);
      if (t > 18.4 && t < 25.3) earth2D(t - EARTH_SHIFT, cx, cy);
      if (t > 25) land2D(t - 25, 1, cx, cy);
      if (t > IMPACT && !hit) { hit = true; shake = 18; buzz([220, 60, 120, 60, 400]); }
      for (var pi = PHASES.length - 1; pi >= 0; pi--) if (t >= PHASES[pi].t) { setPhase(pi); break; }
      if (t > END && state === 'run') finish();
    }
    }
    if (state === 'fade') {
      var o = Math.max(0, 1 - (now - fadeAt) / (FADE * 1000));
      root.style.opacity = o;
      if (o <= 0) { close(); return; }
    }
    if (!document.hidden) raf = requestAnimationFrame(step);
  }
  var fadeAt = 0;

  // ดาวลูกไก่ 7 ดวงหลัก ตำแหน่งโดยประมาณบนฟ้า (หน่วยสัมพัทธ์ รอบดาวอัลไซโอนี)
  var M45 = [[0, 0], [-.62, .05], [-.62, .18], [.62, .12], [.36, -.22], [.42, .32], [.62, .45]];
  function pleiades2D(t, cx, cy) {
    var e = Math.min(1, (t - 12.2) / .6) * (1 - Math.max(0, Math.min(1, (t - 14) / .6))), S = Math.min(W, H) * .32;
    ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = e; ctx.fillStyle = '#02030a'; ctx.fillRect(0, 0, W, H);
    ctx.globalCompositeOperation = 'lighter';
    M45.forEach(function (m, i) {
      var on = Math.max(0, Math.min(1, (t - 12.9 - i * .07) / .25)), sz = S * (i === 0 ? .2 : .14) * on;
      ctx.globalAlpha = e * on; ctx.drawImage(glow, cx + m[0] * S - sz, cy - m[1] * S - sz, sz * 2, sz * 2);
    });
    ctx.globalAlpha = 1;
  }

  // บทพื้นโลกแบบ Canvas 2D: ฟ้า ดวงอาทิตย์ เนินเขา (ก่อนชน = แดดเย็นสีส้ม · หลังชน = มืดแล้วค่อยฟ้าใส)
  function land2D(lc, af, cx, cy) {
    var e = Math.min(1, lc / .7), gr = af ? Math.max(0, Math.min(1, (lc - 1.8) / 2.4)) : 0, gy = cy + Math.min(W, H) * .24;
    var g = ctx.createLinearGradient(0, 0, 0, gy);
    g.addColorStop(0, af ? (gr > .5 ? '#4d80d9' : '#140808') : '#3f2e73'); g.addColorStop(1, af ? (gr > .5 ? '#d9bf99' : '#381410') : '#f28c4d');
    ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = e; ctx.fillStyle = g; ctx.fillRect(0, 0, W, gy);
    ctx.fillStyle = af && gr < .5 ? '#1c1714' : '#140f12'; ctx.fillRect(0, gy, W, H - gy);
    ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = e * (af ? gr : 1);
    var sr = Math.min(W, H) * .12; ctx.drawImage(glow, cx - Math.min(W, H) * .35 - sr, gy - Math.min(W, H) * .2 - sr, sr * 2, sr * 2);
    ctx.globalAlpha = 1;
  }

  // บทโลกแบบ Canvas 2D (เครื่องที่ไม่มี WebGL): โลก · ดาวเคราะห์น้อย · แสงวาบ · คลื่นกระแทก · ฝุ่น
  function earth2D(t, cx, cy) {
    var e = Math.min(1, (t - 12) / .9), R = Math.min(W, H) * (.3 + .05 * Math.min(1, (t - 12.4) / 6.6));
    var ex = cx - R * .13, ey = cy - R * .12, ix = ex + R * .32, iy = ey - R * .22, ta = t - (IMPACT - EARTH_SHIFT);
    ctx.globalCompositeOperation = 'source-over';
    ctx.globalAlpha = e; ctx.fillStyle = '#02030a'; ctx.fillRect(0, 0, W, H);
    var g = ctx.createRadialGradient(ex - R * .35, ey - R * .35, R * .1, ex, ey, R);
    g.addColorStop(0, '#3f7fc0'); g.addColorStop(.55, '#1b4f86'); g.addColorStop(1, '#06142c');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(ex, ey, R, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = 'rgba(90,150,255,.5)'; ctx.lineWidth = 4; ctx.stroke();
    if (ta > 0) {
      var dust = Math.min(1, ta / 1.5) * (1 - Math.max(0, Math.min(1, (t - 18.6) / 1.4)));
      ctx.save(); ctx.beginPath(); ctx.arc(ex, ey, R, 0, Math.PI * 2); ctx.clip();
      ctx.fillStyle = 'rgba(46,30,20,' + .8 * dust + ')'; ctx.beginPath(); ctx.arc(ix, iy, R * Math.min(2, ta * .6 + .1), 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = 'rgba(255,170,90,' + Math.exp(-ta * .35) + ')'; ctx.lineWidth = 5;
      ctx.beginPath(); ctx.arc(ix, iy, R * ta * .55, 0, Math.PI * 2); ctx.stroke(); ctx.restore();
      ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = Math.exp(-ta * .5);
      var fs = R * (.2 + ta * .1); ctx.drawImage(glow, ix - fs, iy - fs, fs * 2, fs * 2);
      ctx.globalAlpha = Math.exp(-ta * 2.5) * e; ctx.fillStyle = '#fff3dc'; ctx.fillRect(0, 0, W, H);
    } else if (t > 12.6) {
      var k = Math.pow(Math.min(1, (t - 12.6) / (IMPACT - EARTH_SHIFT - 12.6)), 1.6), sx0 = cx + W * .55, sy0 = cy - H * .5;
      var ax = sx0 + (ix - sx0) * k, ay = sy0 + (iy - sy0) * k;
      ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = e;
      ctx.strokeStyle = 'rgba(255,200,140,.6)'; ctx.lineWidth = 2 + k * 3;
      ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(ax + (sx0 - ix) * .12, ay + (sy0 - iy) * .12); ctx.stroke();
      ctx.drawImage(glow, ax - 10 - k * 14, ay - 10 - k * 14, 20 + k * 28, 20 + k * 28);
    }
    ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'lighter';
  }

  // ── ตัววาดการ์ดจอ: คลื่นกระแทกและหลุมแรงโน้มถ่วงส่งเป็นพิกัดบนจอ (-1..1) ──
  var WV = new Float32Array(16), hit = false;
  function stepGL(now, t, dt) {
    var sh = [0, 0];
    if (shake > 0) { sh = [(Math.random() - .5) * shake, (Math.random() - .5) * shake]; shake *= Math.exp(-dt * 6); if (shake < .3) shake = 0; }
    for (var i = 0; i < glWaves.length; i++) { glWaves[i].r += dt * 1.25; glWaves[i].a -= dt * 1.1; }
    glWaves = glWaves.filter(function (w) { return w.a > 0; }).slice(-4);
    WV.fill(0);
    glWaves.forEach(function (w, k) { WV.set([w.x, w.y, w.r, w.a], k * 4); });
    var hold = ptr.down && now - ptr.since > 140;
    wellAmt = hold ? Math.min(1, wellAmt + dt * 1.6) : Math.max(0, wellAmt - dt * 2.2);
    GL.draw({ t: t, now: now, shake: sh, waves: WV, yaw: 0, pitch: 0,
              well: [ptr.x / W * 2 - 1, 1 - ptr.y / H * 2, wellAmt * .9] });
    if (t < 0) return;
    if (t > IMPACT && !hit) { hit = true; shake = 22; buzz([220, 60, 120, 60, 400]); }   // ชนโลก: จอสั่น มือถือสั่น
    for (var pi = PHASES.length - 1; pi >= 0; pi--) if (t >= PHASES[pi].t) { setPhase(pi); break; }
    if (tipEl) tipEl.hidden = !(t > 1.6 && t < 5.8);
    snd.update(t, hold);
    if (t > END && state === 'run') finish();
  }

  // ── เสียง (Web Audio): ระเบิดครืน · เสียงฮัมของอวกาศ · ดาวดวงแรกดังกริ๊ง · ลมตอนบินทะลุ ──
  // ปิดไว้ก่อนเสมอ เปิดได้ด้วยปุ่ม "เสียง" — จำค่าไว้ในเครื่อง
  var snd = (function () {
    var A = null, M = null, drone = null, on = false, done = {}, wellG = null;
    try { on = localStorage.getItem('kd-bang-sound') === '1'; } catch (e) {}
    function ctxOk() {
      if (A) { if (A.state === 'suspended') A.resume(); return true; }
      var C = window.AudioContext || window.webkitAudioContext; if (!C) return false;
      try { A = new C(); M = A.createGain(); M.gain.value = .8; M.connect(A.destination); } catch (e) { A = null; return false; }
      return true;
    }
    function noise(sec) {
      var b = A.createBuffer(1, Math.round(A.sampleRate * sec), A.sampleRate), d = b.getChannelData(0);
      for (var i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
      var s = A.createBufferSource(); s.buffer = b; return s;
    }
    function env(g, t, peak, a, r) { g.gain.setValueAtTime(.0001, t); g.gain.exponentialRampToValueAtTime(peak, t + a); g.gain.exponentialRampToValueAtTime(.0001, t + a + r); }
    function boom() {
      var t = A.currentTime, n = noise(3), f = A.createBiquadFilter(), g = A.createGain();
      f.type = 'lowpass'; f.frequency.setValueAtTime(9000, t); f.frequency.exponentialRampToValueAtTime(90, t + 2.4);
      env(g, t, .9, .01, 2.8); n.connect(f); f.connect(g); g.connect(M); n.start(t); n.stop(t + 3);
      var o = A.createOscillator(), og = A.createGain(); o.type = 'sine';
      o.frequency.setValueAtTime(70, t); o.frequency.exponentialRampToValueAtTime(26, t + 3);
      env(og, t, .9, .02, 3.2); o.connect(og); og.connect(M); o.start(t); o.stop(t + 3.4);
    }
    function startDrone() {
      if (drone) return;
      var t = A.currentTime, f = A.createBiquadFilter(), g = A.createGain(), o1 = A.createOscillator(), o2 = A.createOscillator();
      o1.type = o2.type = 'sawtooth'; o1.frequency.value = 55; o2.frequency.value = 55.6;
      f.type = 'lowpass'; f.frequency.value = 260; f.Q.value = 4;
      g.gain.setValueAtTime(.0001, t); g.gain.exponentialRampToValueAtTime(.07, t + 2.5);
      o1.connect(f); o2.connect(f); f.connect(g); g.connect(M); o1.start(t); o2.start(t);
      wellG = A.createGain(); wellG.gain.value = 0; var wo = A.createOscillator(); wo.type = 'sine'; wo.frequency.value = 38;
      wo.connect(wellG); wellG.connect(M); wo.start(t);
      drone = { f: f, g: g, o: [o1, o2, wo] };
    }
    function pings() {
      var t = A.currentTime;
      for (var i = 0; i < 9; i++) {
        var o = A.createOscillator(), g = A.createGain(), at = t + i * .17 + Math.random() * .12;
        o.type = 'sine'; o.frequency.value = [880, 1175, 1318, 1568, 1760][Math.floor(Math.random() * 5)];
        env(g, at, .05, .01, 1.4); o.connect(g); g.connect(M); o.start(at); o.stop(at + 1.6);
      }
    }
    function whoosh() {
      var t = A.currentTime, n = noise(3), f = A.createBiquadFilter(), g = A.createGain();
      f.type = 'bandpass'; f.Q.value = 1.4; f.frequency.setValueAtTime(250, t); f.frequency.exponentialRampToValueAtTime(3200, t + 2.6);
      env(g, t, .28, 1.6, 1.2); n.connect(f); f.connect(g); g.connect(M); n.start(t); n.stop(t + 3);
    }
    function wind() {                                  // ลมร้อนพัดผ่านป่า: เสียงซ่าที่ขึ้นลงช้าๆ ราว 8 วินาที
      var t = A.currentTime, n = noise(9), f = A.createBiquadFilter(), g = A.createGain();
      f.type = 'bandpass'; f.Q.value = .7; f.frequency.setValueAtTime(400, t);
      for (var i = 1; i < 9; i++) f.frequency.linearRampToValueAtTime(300 + Math.random() * 600, t + i);
      g.gain.setValueAtTime(.0001, t); g.gain.exponentialRampToValueAtTime(.12, t + 2); g.gain.setValueAtTime(.12, t + 6.5);
      g.gain.exponentialRampToValueAtTime(.0001, t + 8.8); n.connect(f); f.connect(g); g.connect(M); n.start(t); n.stop(t + 9);
    }
    function birds() {                                 // นกร้องสั้นๆ: เสียงหวีดที่ไล่ขึ้นเร็ว
      var t = A.currentTime;
      for (var i = 0; i < 7; i++) {
        var o = A.createOscillator(), g = A.createGain(), at = t + i * .32 + Math.random() * .2, f0 = 2200 + Math.random() * 1400;
        o.type = 'sine'; o.frequency.setValueAtTime(f0, at); o.frequency.exponentialRampToValueAtTime(f0 * 1.5, at + .09);
        env(g, at, .04, .01, .14); o.connect(g); g.connect(M); o.start(at); o.stop(at + .2);
      }
    }
    function stop() {
      if (!drone || !A) return; var t = A.currentTime, d = drone; drone = null;
      d.g.gain.cancelScheduledValues(t); d.g.gain.setValueAtTime(Math.max(.0001, d.g.gain.value), t); d.g.gain.exponentialRampToValueAtTime(.0001, t + 1.2);
      d.o.forEach(function (o) { try { o.stop(t + 1.3); } catch (e) {} });
    }
    return {
      on: function () { return on; },
      set: function (v) {
        on = v; try { localStorage.setItem('kd-bang-sound', v ? '1' : '0'); } catch (e) {}
        if (v && ctxOk() && state === 'run') { startDrone(); } else if (!v) { stop(); }
      },
      ignite: function () { done = {}; if (on && ctxOk()) { boom(); startDrone(); done.boom = 1; } },
      tap: function () {
        if (!on || !ctxOk()) return;
        var t = A.currentTime, o = A.createOscillator(), g = A.createGain(); o.type = 'sine';
        o.frequency.setValueAtTime(140, t); o.frequency.exponentialRampToValueAtTime(40, t + .4);
        env(g, t, .35, .005, .5); o.connect(g); g.connect(M); o.start(t); o.stop(t + .6);
      },
      update: function (t, hold) {
        if (!on || !A || !drone) return;
        var ft = t < 2.8 ? 700 : t < 4.8 ? 520 : t < 8 ? 170 : 300 + 80 * Math.sin(t * 1.3);
        drone.f.frequency.setTargetAtTime(ft, A.currentTime, .6);
        wellG.gain.setTargetAtTime(hold ? .18 : 0, A.currentTime, .25);
        if (t > 6.4 && !done.ping) { done.ping = 1; pings(); }
        if (t > 11.2 && !done.wh) { done.wh = 1; whoosh(); }
        if (t > 13 && !done.m45) { done.m45 = 1; pings(); }               // ดาวลูกไก่จุดประกาย
        if (t > 14 && !done.wind) { done.wind = 1; wind(); }              // ลมร้อนยุคครีเทเชียส
        if (t > 20.4 && !done.wh2) { done.wh2 = 1; whoosh(); }             // ดาวเคราะห์น้อยพุ่งเข้ามา
        if (t > 28.8 && !done.bird) { done.bird = 1; birds(); }           // นกร้อง
        if (t > IMPACT && !done.imp) { done.imp = 1; boom(); }            // ชนโลก
      },
      stop: stop
    };
  })();

  // สั่นมือถือตอนระเบิดและตอนชน (เหมือนเก้าอี้สั่นในโรงหนัง 4D) — เครื่องที่ไม่รองรับก็ข้ามไปเฉยๆ · ลดการเคลื่อนไหวไม่สั่น
  function buzz(pat) { if (CALM()) return; try { if (navigator.vibrate) navigator.vibrate(pat); } catch (e) {} }

  function ignite() {
    if (state !== 'idle') return;
    clearTimeout(waitTimer);
    state = 'run'; t0 = performance.now(); shake = 14; snd.ignite(); buzz([60, 40, 160]);
    hintEl.hidden = true; root.classList.add('lit');
  }

  function open(auto) {
    if (state !== 'off') return;
    prevFocus = document.activeElement;
    resize(); if (GL) GL.seed(GL.count(W, H)); else seed();
    phase = -1; waves = []; glWaves = []; wellAmt = 0; hit = false;
    root.hidden = false; root.style.opacity = 1; root.classList.remove('lit', 'still');
    document.documentElement.classList.add('bb-on');
    capEl.textContent = 'ก่อนเวลาจะเริ่ม ทุกอย่างอยู่ในจุดเดียว'; timeEl.textContent = '—'; tempEl.textContent = '—';
    try { skipEl.focus({ preventScroll: true }); } catch (e) { skipEl.focus(); }
    if (CALM()) { stillShow(); return; }
    hintEl.hidden = false; state = 'idle'; last = performance.now();
    waitTimer = setTimeout(ignite, auto ? 2600 : 1800);
    if (!raf) raf = requestAnimationFrame(step);
  }

  // ลดการเคลื่อนไหว: ไม่มีอนุภาคพุ่ง — ข้อความทีละช่วงบนพื้นนิ่ง
  function stillShow() {
    state = 'still'; root.classList.add('still', 'lit'); hintEl.hidden = true;
    if (GL) {                                          // ภาพนิ่งของกาแล็กซีที่ก่อตัวแล้ว วาดครั้งเดียว ไม่ขยับ
      GL.draw({ t: 10.4, now: 0, shake: [0, 0], waves: new Float32Array(16), well: [0, 0, 0], yaw: 0, pitch: 0 });
    } else {
    ctx.globalCompositeOperation = 'source-over'; ctx.fillStyle = '#02030a'; ctx.fillRect(0, 0, W, H);
    ctx.globalCompositeOperation = 'lighter';
    for (var i = 0; i < 260; i++) { var s = Math.random() * 1.6 + .4; ctx.fillStyle = 'rgba(220,230,255,' + (.25 + Math.random() * .6) + ')'; ctx.fillRect(Math.random() * W, Math.random() * H, s, s); }
    }
    var i2 = 0; (function next() {
      if (state !== 'still') return;
      if (i2 >= PHASES.length) { close(); return; }
      setPhase(i2++); calmTimer = setTimeout(next, 2600);
    })();
  }

  function finish() { if (state === 'run' || state === 'idle') { state = 'fade'; fadeAt = performance.now(); if (!raf) raf = requestAnimationFrame(step); } }
  function close() {
    clearTimeout(waitTimer); clearTimeout(calmTimer);
    if (raf) cancelAnimationFrame(raf); raf = 0;
    state = 'off'; root.hidden = true; ptr.down = false; snd.stop(); if (tipEl) tipEl.hidden = true;
    document.documentElement.classList.remove('bb-on');
    if (prevFocus && prevFocus.focus && prevFocus !== document.body) { try { prevFocus.focus({ preventScroll: true }); } catch (e) {} }
    window.dispatchEvent(new Event('kd-bang-done'));
  }
  function skip() { if (state === 'still') close(); else if (state !== 'off') finish(); }

  function local(e) { var cx = W / 2, cy = H / 2; return { x: e.clientX - cx, y: e.clientY - cy }; }
  cv.addEventListener('pointerdown', function (e) {
    if (state === 'idle') { ignite(); return; }
    if (state !== 'run') return;
    ptr.down = true; ptr.x = e.clientX; ptr.y = e.clientY; ptr.since = performance.now(); snd.tap();
    if (GL) { glWaves.push({ x: e.clientX / W * 2 - 1, y: 1 - e.clientY / H * 2, r: 0, a: 1 }); shake = Math.max(shake, 5); return; }
    var l = local(e), zoom = 1 + Math.pow(Math.max(0, sceneTime((performance.now() - t0) / 1000) - 11.4), 2) * .35;
    waves.push({ x: l.x / zoom, y: l.y / zoom, r: 0, a: 1 }); shake = Math.max(shake, 5);
  });
  cv.addEventListener('pointermove', function (e) { if (ptr.down) { ptr.x = e.clientX; ptr.y = e.clientY; } });
  ['pointerup', 'pointercancel', 'pointerleave'].forEach(function (n) { cv.addEventListener(n, function () { ptr.down = false; }); });
  skipEl.addEventListener('click', skip);
  function sndLabel() { sndEl.textContent = snd.on() ? 'เสียง: เปิด' : 'เสียง: ปิด'; sndEl.setAttribute('aria-pressed', snd.on() ? 'true' : 'false'); }
  if (sndEl) { sndLabel(); sndEl.addEventListener('click', function () { snd.set(!snd.on()); sndLabel(); }); }
  // ดูภาพล้วนๆ: ซ่อนคำบรรยาย เวลา และคำแนะนำ — จำค่าไว้ในเครื่อง
  var showText = true;
  try { showText = localStorage.getItem('kd-bang-text') !== '0'; } catch (e) {}
  function txtLabel() {
    root.classList.toggle('notext', !showText);
    txtEl.textContent = showText ? 'ข้อความ: เปิด' : 'ข้อความ: ปิด'; txtEl.setAttribute('aria-pressed', showText ? 'true' : 'false');
  }
  if (txtEl) {
    txtLabel();
    txtEl.addEventListener('click', function () { showText = !showText; try { localStorage.setItem('kd-bang-text', showText ? '1' : '0'); } catch (e) {} txtLabel(); });
  }
  root.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { e.preventDefault(); skip(); }
    else if ((e.key === 'Enter' || e.key === ' ') && state === 'idle' && document.activeElement !== skipEl) { e.preventDefault(); ignite(); }
    else if (e.key === 'Tab') {                                                // โฟกัสอยู่ในฉากจนกว่าจะปิด
      e.preventDefault();
      var btns = [skipEl, sndEl, txtEl].filter(Boolean), k = btns.indexOf(document.activeElement);
      btns[(k + (e.shiftKey ? btns.length - 1 : 1)) % btns.length].focus();
    }
  });
  window.addEventListener('resize', function () { if (state !== 'off') resize(); });
  document.addEventListener('visibilitychange', function () {
    if (!document.hidden && state !== 'off' && state !== 'still' && !raf) { last = performance.now(); raf = requestAnimationFrame(step); }
  });

  if (!GL) glow = sprite();
  state = 'off';
  window.KD_bigBang = function () { open(false); };
  // เล่นเองครั้งแรกในแต่ละรอบที่เปิดเว็บ · ลดการเคลื่อนไหวไม่เล่นเอง (กดปุ่ม "บิ๊กแบง" ได้)
  var seen = false;
  try { seen = sessionStorage.getItem('kd-bang') === '1'; sessionStorage.setItem('kd-bang', '1'); } catch (e) {}
  if (!seen && !CALM()) open(true);
})();
