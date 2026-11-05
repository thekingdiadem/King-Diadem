/* ฟ้าจริง ณ ตำแหน่งและเวลาของคุณ — หน้าดูดาวของ KING DIADEM (static/sky.html)
 *
 * · ดาว 5,044 ดวงถึงโชติมาตร 6 (Hipparcos/HYG ผ่าน d3-celestial — scripts/build_sky_catalog.py) แก้การหมุนควงของแกนโลกถึงวันนี้
 * · ดาวเคราะห์จากธาตุวงโคจรของ JPL (แม่นราว 1 ลิปดาในช่วง ค.ศ. 1800–2050) · ดวงจันทร์สูตรย่อ + แก้พารัลแลกซ์ (~0.3°) · ดวงอาทิตย์
 * · ฉายแบบ stereographic (กลุ่มดาวไม่บิดตอนมองกว้าง) · แสงหักเหใกล้ขอบฟ้า · ฟ้าสว่างตามมุมดวงอาทิตย์
 * · ลากหมุนรอบตัว · ถ่าง/ล้อเมาส์ซูม · แตะดาวดูรายละเอียด · ปุ่มชั้นข้อมูลมุมซ้ายล่าง · ชี้มือถือขึ้นฟ้าให้ภาพหมุนตาม (เข็มทิศเครื่อง)
 * · ตำแหน่งเริ่มต้นกรุงเทพฯ — ใช้ตำแหน่งจริงเมื่อผู้ใช้กดเองเท่านั้น (จำไว้ในเครื่อง ไม่ส่งออกไปไหน)
 * วาดเมื่อมีอะไรเปลี่ยนเท่านั้น (และทุก 10 วินาทีตามเวลาจริง) — ประหยัดแบต
 */
(function () {
  'use strict';
  var cv = document.getElementById('sky'), cx = cv && cv.getContext('2d');
  if (!cx) return;
  var D2R = Math.PI / 180, R2D = 180 / Math.PI;
  var THAI = !/^en/i.test((new URLSearchParams(location.search)).get('lang') || document.documentElement.lang || 'th');
  function T(th, en) { return THAI ? th : en; }
  function clamp(x, a, b) { return x < a ? a : x > b ? b : x; }
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }

  // ── สถานะ ──────────────────────────────────────────────────────────────────────────────
  var loc = { lat: 13.7563, lon: 100.5018, name: T('กรุงเทพฯ', 'Bangkok') };
  try { var sv = JSON.parse(store('kd-sky-loc') || 'null'); if (sv && isFinite(sv.lat) && isFinite(sv.lon)) loc = sv; } catch (e) {}
  // มาจากลูกโลก (กด "ดูดาว" ตอนดูอเมริกาอยู่) = ฟ้าเหนือจุดนั้น · ใช้รอบนี้รอบเดียว ไม่จำทับตำแหน่งของผู้ใช้
  (function () {
    var q = new URLSearchParams(location.search), la = parseFloat(q.get('lat')), lo = parseFloat(q.get('lon'));
    if (isFinite(la) && isFinite(lo) && Math.abs(la) <= 90) {
      loc = { lat: clamp(la, -89.9, 89.9), lon: ((lo % 360) + 540) % 360 - 180, name: (q.get('name') || '').replace(/[<>]/g, '').slice(0, 40), away: true };
    }
  })();
  var V = { az: 90, alt: 35, fov: 70 };                      // หันทิศตะวันออก มองขึ้น 35° · มุมมองกว้าง 70°
  var tgt = null;                                           // บินไปหาเป้าหมาย {az, alt, fov}
  var LAY = { lines: true, names: true, grid: false, milky: true, ground: true, red: false, mine: true };
  try { var sl = JSON.parse(store('kd-sky-layers') || 'null'); if (sl) for (var k in LAY) if (k in sl) LAY[k] = !!sl[k]; } catch (e) {}
  var offsetMin = 0;                                        // เลื่อนเวลา (นาที) — 0 = ตอนนี้
  var CAT = null, STARS = null, MW = null, sensor = null, dirty = true, raf = 0, lastDraw = 0;
  function now() { return new Date(Date.now() + offsetMin * 60000); }

  // ── ดาราศาสตร์ ─────────────────────────────────────────────────────────────────────────
  function jd(d) { return d.getTime() / 86400000 + 2440587.5; }
  function gmst(J) { var d = J - 2451545, t = d / 36525; return (280.46061837 + 360.98564736629 * d + .000387933 * t * t - t * t * t / 38710000) % 360; }
  function precess(t) {                                      // J2000 → วันนี้ (IAU 1976) · คืนเมทริกซ์ 3×3 แบบแถว
    var as = D2R / 3600, ze = (2306.2181 * t + .30188 * t * t + .017998 * t * t * t) * as,
        z = (2306.2181 * t + 1.09468 * t * t + .018203 * t * t * t) * as, th = (2004.3109 * t - .42665 * t * t - .041833 * t * t * t) * as;
    var cz = Math.cos(ze), sz = Math.sin(ze), cZ = Math.cos(z), sZ = Math.sin(z), ct = Math.cos(th), st = Math.sin(th);
    return [[cz * ct * cZ - sz * sZ, -sz * ct * cZ - cz * sZ, -st * cZ],
            [cz * ct * sZ + sz * cZ, -sz * ct * sZ + cz * cZ, -st * sZ],
            [cz * st, -sz * st, ct]];
  }
  function mul(P, v) { return [P[0][0] * v[0] + P[0][1] * v[1] + P[0][2] * v[2], P[1][0] * v[0] + P[1][1] * v[1] + P[1][2] * v[2], P[2][0] * v[0] + P[2][1] * v[1] + P[2][2] * v[2]]; }
  function eqv(ra, dec) { var a = ra * D2R, d = dec * D2R; return [Math.cos(d) * Math.cos(a), Math.cos(d) * Math.sin(a), Math.sin(d)]; }
  var OBL = 23.43928 * D2R;
  function ecl2eq(x, y, z, e) { e = e || OBL; return [x, y * Math.cos(e) - z * Math.sin(e), y * Math.sin(e) + z * Math.cos(e)]; }
  function kepler(el, t) {                                    // ธาตุวงโคจรประมาณของ JPL → ตำแหน่งรอบดวงอาทิตย์ (สุริยวิถี J2000, AU)
    var a = el.a + el.da * t, e = el.e + el.de * t, i = (el.i + el.di * t) * D2R, L = el.L + el.dL * t,
        W = el.W + el.dW * t, N = (el.N + el.dN * t) * D2R, w = W * D2R - N, M = ((L - W) % 360 + 540) % 360 - 180;
    M *= D2R; var E = M + e * Math.sin(M);
    for (var k = 0; k < 8; k++) E -= (E - e * Math.sin(E) - M) / (1 - e * Math.cos(E));
    var xp = a * (Math.cos(E) - e), yp = a * Math.sqrt(1 - e * e) * Math.sin(E);
    var cw = Math.cos(w), sw = Math.sin(w), cN = Math.cos(N), sN = Math.sin(N), ci = Math.cos(i), si = Math.sin(i);
    return [(cw * cN - sw * sN * ci) * xp + (-sw * cN - cw * sN * ci) * yp,
            (cw * sN + sw * cN * ci) * xp + (-sw * sN + cw * cN * ci) * yp,
            (sw * si) * xp + (cw * si) * yp];
  }
  function moon(t) {                                          // สูตรย่อ (Astronomical Almanac) — ลองจิจูด/ละติจูดสุริยวิถีของวันนั้น
    function s(a, b) { return Math.sin((a + b * t) * D2R); }
    function c(a, b) { return Math.cos((a + b * t) * D2R); }
    var L = 218.32 + 481267.881 * t + 6.29 * s(134.9, 477198.85) - 1.27 * s(259.2, -413335.38) + .66 * s(235.7, 890534.23)
          + .21 * s(269.9, 954397.70) - .19 * s(357.5, 35999.05) - .11 * s(186.6, 966404.05);
    var B = 5.13 * s(93.3, 483202.03) + .28 * s(228.2, 960400.87) - .28 * s(318.3, 6003.18) - .17 * s(217.6, -407332.20);
    var P = .9508 + .0518 * c(134.9, 477198.85) + .0095 * c(259.2, -413335.38) + .0078 * c(235.7, 890534.23) + .0028 * c(269.9, 954397.70);
    var l = L * D2R, b = B * D2R, eps = (23.439 - .0130 * t) * D2R;
    return { v: ecl2eq(Math.cos(b) * Math.cos(l), Math.cos(b) * Math.sin(l), Math.sin(b), eps), par: P };
  }

  // ── เตรียมข้อมูล (ครั้งเดียวต่อวัน — การหมุนควงช้ามาก) ─────────────────────────────────────────
  var prepDay = -1, PM = null;
  function prepare(J) {
    var day = Math.floor(J);
    if (day === prepDay && STARS) return;
    prepDay = day; PM = precess((J - 2451545) / 36525);
    STARS = CAT.stars.map(function (s) { var v = mul(PM, eqv(s[0], s[1])); return { v: v, mag: s[2], col: bvColor(s[3]), bv: s[3] }; });
    CAT.named.forEach(function (n) { STARS[n[0]].name = THAI && n[2] ? n[2] : n[1]; STARS[n[0]].en = n[1]; });
    LINES = Object.keys(CAT.lines).map(function (id) {
      return CAT.lines[id].map(function (seg) { return seg.map(function (p) { return mul(PM, eqv(p[0], p[1])); }); });
    });
    CONS = CAT.cons.map(function (c) { return { v: mul(PM, eqv(c.at[0], c.at[1])), name: THAI && c.th ? c.th : c.en, en: c.en, rank: c.rank }; });
    [DEEP, DEEP2].forEach(function (DD) {                       // ดาวจาง 6–8 แล้ว 8–10 ต่อท้าย (ไฟล์เรียงตามความสว่างอยู่แล้ว)
      if (!DD || (DD === DEEP2 && !DEEP)) return;
      var D = DD.stars, k = DD.scale;
      for (var i = 0; i < D.length; i += 4) STARS.push({ v: mul(PM, eqv(D[i] / k[0], D[i + 1] / k[1])), mag: D[i + 2] / k[2], col: bvColor(D[i + 3] / k[3]), bv: D[i + 3] / k[3], deep: true });
    });
    MWL = MWRAW ? MWRAW.levels.map(function (lv) { return lv.map(function (ring) { return ring.map(function (p) { return mul(PM, eqv(p[0], p[1])); }); }); }) : null;
  }
  var DEEP = null, DEEP2 = null, deep2Asked = false, MWRAW = null, MWL = null, mwc = null, mwx = null;
  var LINES = [], CONS = [];
  // ภาพดาวสำเร็จรูป 9 สี (ร้อนฟ้า → เย็นแดง) — วาดครั้งเดียว แล้วประทับซ้ำ เร็วกว่าไล่สีทุกดวงหลายเท่า
  var SPR = {};
  function starSprite(bv) {
    var k = Math.round(clamp((bv + .4) / 2.4, 0, 1) * 8);
    if (SPR[k]) return SPR[k];
    var n = 64, c = document.createElement('canvas'); c.width = c.height = n;
    var g = c.getContext('2d'), col = bvColor(-.4 + k * .3).replace('rgb(', '').replace(')', ''), h = n / 2;
    var gr = g.createRadialGradient(h, h, 0, h, h, h);
    gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(.08, 'rgba(255,255,255,.95)');
    gr.addColorStop(.18, 'rgba(' + col + ',.8)'); gr.addColorStop(.4, 'rgba(' + col + ',.22)');
    gr.addColorStop(.7, 'rgba(' + col + ',.05)'); gr.addColorStop(1, 'rgba(' + col + ',0)');
    g.fillStyle = gr; g.fillRect(0, 0, n, n);
    return (SPR[k] = c);
  }
  function bvColor(bv) {                                      // สีดาวตามอุณหภูมิ (B−V) แบบประมาณ — ฟ้าอมขาว → ขาว → เหลือง → ส้ม
    bv = clamp(bv, -.4, 2);
    var r = bv < .4 ? 175 + 80 * (bv + .4) / .8 : 255, g = bv < 0 ? 200 + 40 * (bv + .4) / .4 : bv < .6 ? 240 - 10 * bv : 234 - 60 * (bv - .6),
        b = bv < 0 ? 255 : bv < .4 ? 255 - 50 * bv / .4 : 205 - 90 * (bv - .4) / 1.6;
    return 'rgb(' + Math.round(r) + ',' + Math.round(clamp(g, 120, 255)) + ',' + Math.round(clamp(b, 70, 255)) + ')';
  }


  // ── จากศูนย์สูตร (ของวันนี้) → ขอบฟ้าของผู้ดู → จอ ─────────────────────────────────────────────
  var F = null;   // ค่าของเฟรมนี้
  function frameSetup() {
    var d = now(), J = jd(d), t = (J - 2451545) / 36525;
    prepare(J);
    var lst = (gmst(J) + loc.lon) * D2R, ph = loc.lat * D2R;
    var W = cv.clientWidth, H = cv.clientHeight, a0 = V.az * D2R, h0 = (Math.abs(V.alt) < .05 ? .05 : V.alt) * D2R;
    var f = [Math.sin(a0) * Math.cos(h0), Math.cos(a0) * Math.cos(h0), Math.sin(h0)], r = [Math.cos(a0), -Math.sin(a0), 0];
    var u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]];
    F = { d: d, J: J, t: t, cL: Math.cos(lst), sL: Math.sin(lst), cP: Math.cos(ph), sP: Math.sin(ph), W: W, H: H, f: f, r: r, u: u,
          s: (H / 2) / (2 * Math.tan(V.fov * D2R / 4)) };              // FOV = มุมมองแนวตั้ง
    F.bodies = bodies(t);
  }
  function local(v) {                                         // [ตะวันออก, เหนือ, ขึ้น]
    var xH = F.cL * v[0] + F.sL * v[1], yH = F.sL * v[0] - F.cL * v[1];
    return [-yH, v[2] * F.cP - xH * F.sP, v[2] * F.sP + xH * F.cP];
  }
  function refract(l) {                                       // แสงหักเหใกล้ขอบฟ้า (Bennett) — ยกภาพขึ้นราวครึ่งองศาที่ขอบฟ้า
    var h = Math.asin(clamp(l[2], -1, 1)) * R2D;
    if (h < -1.5 || h > 80) return l;
    var R = 1.02 / Math.tan((h + 10.3 / (h + 5.11)) * D2R) / 60, nh = (h + R) * D2R, k = Math.cos(nh) / Math.max(1e-9, Math.hypot(l[0], l[1]));
    return [l[0] * k, l[1] * k, Math.sin(nh)];
  }
  function proj(l) {                                          // stereographic — null = อยู่ข้างหลังเกินไป
    var x = l[0] * F.r[0] + l[1] * F.r[1] + l[2] * F.r[2], y = l[0] * F.u[0] + l[1] * F.u[1] + l[2] * F.u[2], z = l[0] * F.f[0] + l[1] * F.f[1] + l[2] * F.f[2];
    if (z < -.6) return null;
    var k = 2 / (1 + z) * F.s;
    return [F.W / 2 + x * k, F.H / 2 - y * k, z];
  }
  function altaz(l) { return [((Math.atan2(l[0], l[1]) * R2D) + 360) % 360, Math.asin(clamp(l[2], -1, 1)) * R2D]; }
  function fromAltAz(az, alt) { var a = az * D2R, h = alt * D2R; return [Math.sin(a) * Math.cos(h), Math.cos(a) * Math.cos(h), Math.sin(h)]; }
  function onScreen(p, m) { return p && p[0] > -m && p[0] < F.W + m && p[1] > -m && p[1] < F.H + m; }

  function bodies(t) {
    var P = CAT.planets, E = kepler(P.ter.el, t), out = [];
    var sunV = mul(PM, ecl2eq(-E[0], -E[1], -E[2]));
    var sl = Math.hypot(sunV[0], sunV[1], sunV[2]);
    out.push({ id: 'sun', name: T('ดวงอาทิตย์', 'Sun'), v: [sunV[0] / sl, sunV[1] / sl, sunV[2] / sl], mag: -26.7, au: sl });
    var m = moon(t);
    out.push({ id: 'moon', name: T('ดวงจันทร์', 'Moon'), v: m.v, mag: -11, par: m.par * D2R });
    ['mer', 'ven', 'mar', 'jup', 'sat', 'ura', 'nep'].forEach(function (k) {
      var p = kepler(P[k].el, t), g = ecl2eq(p[0] - E[0], p[1] - E[1], p[2] - E[2]), dl = Math.hypot(g[0], g[1], g[2]);
      var rh = Math.hypot(p[0], p[1], p[2]), cosA = clamp((rh * rh + dl * dl - sl * sl) / (2 * rh * dl), -1, 1), A = Math.acos(cosA) * R2D;
      var mag = P[k].H != null ? P[k].H + 5 * Math.log10(rh * dl) + (k === 'ven' ? .0009 * A + 2.4e-4 * A * A / 10 : .02 * A) : 6;
      out.push({ id: k, name: THAI ? P[k].th : P[k].en, v: mul(PM, [g[0] / dl, g[1] / dl, g[2] / dl]), mag: clamp(mag, -4.9, 8), au: dl });
    });
    return out;
  }
  function bodyLocal(b) {
    var l = local(b.v);
    if (b.par) {                                              // ดวงจันทร์: มองจากผิวโลกต่ำกว่ามองจากศูนย์กลางโลก ~1°
      var h = Math.asin(clamp(l[2], -1, 1)), nh = h - b.par * Math.cos(h), k = Math.cos(nh) / Math.max(1e-9, Math.hypot(l[0], l[1]));
      l = [l[0] * k, l[1] * k, Math.sin(nh)];
    }
    return refract(l);
  }

  // ── วาด ─────────────────────────────────────────────────────────────────────────────────
  var hits = [];
  function size() {
    var dpr = Math.min(3, window.devicePixelRatio || 1);
    cv.width = Math.round(cv.clientWidth * dpr); cv.height = Math.round(cv.clientHeight * dpr);
    cx.setTransform(dpr, 0, 0, dpr, 0, 0); dirty = true; kick();
  }
  function skyColor(sunAlt) {                                 // ฟ้ามืด → ฟ้าสาง → กลางวัน ตามมุมดวงอาทิตย์จริง
    var k = clamp((sunAlt + 18) / 24, 0, 1);
    var top = [Math.round(4 + 40 * k), Math.round(6 + 90 * k), Math.round(14 + 160 * k)];
    var low = [Math.round(14 + 150 * k), Math.round(18 + 140 * k), Math.round(34 + 160 * k)];
    return { top: top, low: low, starA: 1 - clamp((sunAlt + 12) / 10, 0, 1) * .97, k: k };
  }
  function draw() {
    dirty = false; lastDraw = Date.now();
    frameSetup();
    var W = F.W, H = F.H, sun = F.bodies[0], sunL = bodyLocal(sun), sunAlt = altaz(sunL)[1], sc = skyColor(sunAlt);
    hits = [];
    // ฟ้า
    var hp = proj(fromAltAz(V.az, 0)), hy = hp ? hp[1] : H * 1.5;
    var g = cx.createLinearGradient(0, Math.min(hy, H) - H * .9, 0, hy);
    g.addColorStop(0, 'rgb(' + sc.top + ')'); g.addColorStop(1, 'rgb(' + sc.low + ')');
    cx.fillStyle = g; cx.fillRect(0, 0, W, H);
    var zoomK = clamp(70 / V.fov, .6, 6);
    // ทางช้างเผือก: ขอบจริง 5 ระดับความสว่าง (d3-celestial) วาดบนผืนผ้าใบเล็ก 1/4 แล้วขยาย = ฟุ้งนุ่ม เบาเครื่อง
    if (LAY.milky && MWL && sc.starA > .2) drawMilky(sc);
    // เส้นกริด (มุมเงย/ทิศ)
    if (LAY.grid) {
      cx.strokeStyle = 'rgba(120,170,220,.22)'; cx.lineWidth = 1;
      for (var al = -30; al <= 75; al += 15) path(function (i) { return fromAltAz(i * 3, al); }, 121);
      for (var az = 0; az < 360; az += 15) path(function (i) { return fromAltAz(az, -30 + i * 1.5); }, 81);
    }
    // เส้นกลุ่มดาว
    if (LAY.lines && sc.starA > .15) {
      cx.strokeStyle = 'rgba(126,196,214,' + (.42 * sc.starA).toFixed(2) + ')'; cx.lineWidth = 1;
      LINES.forEach(function (c) {
        c.forEach(function (seg) {
          cx.beginPath(); var pen = false;
          seg.forEach(function (v) { var p = proj(refract(local(v))); if (!p) { pen = false; return; } if (pen) cx.lineTo(p[0], p[1]); else cx.moveTo(p[0], p[1]); pen = true; });
          cx.stroke();
        });
      });
    }
    // ดาว
    cx.save(); cx.globalCompositeOperation = 'lighter';
    // ตาเปล่าที่ฟ้ามืดเห็นถึงโชติมาตร ~6 · ซูมเข้า = เหมือนส่องกล้อง เห็นจางลงได้ถึง 8 (ดาวจางโหลดตามหลัง)
    var zoomS = 70 / V.fov, limit = Math.min(DEEP2 && DEEP ? 10 : DEEP ? 8 : 6.05, 5.6 + Math.log(Math.max(1, zoomS)) / Math.LN2 * .85) - (1 - sc.starA) * 3;
    if (V.fov < 25 && DEEP && !deep2Asked) { deep2Asked = true; loadLater('deep2.json', function (x) { DEEP2 = x; }); }   // ซูมลึกครั้งแรก = โหลดชั้นที่ 3
    var half = Math.atan(Math.hypot(W, H) / H * Math.tan(V.fov * D2R / 2)), zmin = Math.cos(Math.min(2.6, half * 1.08 + .02));
    var labels = [];
    for (var i = 0; i < STARS.length; i++) {
      var st = STARS[i];
      if (st.mag > limit) break;                              // เรียงจากสว่างไปจาง
      var l0 = local(st.v);
      if (l0[0] * F.f[0] + l0[1] * F.f[1] + l0[2] * F.f[2] < zmin) continue;      // นอกมุมมอง — ไม่ต้องคำนวณต่อ
      var l = l0[2] > .5 ? l0 : refract(l0); if (behindHill(l)) continue;
      var p = proj(l); if (!onScreen(p, 4)) continue;
      // ดาวแบบแสงจริง (PSF): แกนขาวคม ฟุ้งเป็นสีของดาว · ขนาดตามแสงจริง 10^(−0.4m) · วาดแบบแสงบวกกัน
      // ใกล้ขอบฟ้าแสงผ่านอากาศหนากว่า (airmass) → จางลงและอมแดง แบบที่ตาเห็นจริง
      var sh = Math.max(.02, l[2]), X = 1 / (sh + .025 * Math.exp(-11 * sh)), ext = LAY.ground ? .22 * (X - 1) : 0;
      var m = st.mag + ext, rel = Math.pow(10, -.15 * (m - limit)), core = clamp(.55 * rel, .5, 7) * Math.pow(Math.min(zoomK, 6), .22);
      var a = clamp((limit + 1.2 - m) / 2.4, .3, 1) * sc.starA;
      if (a < .03 || m > limit + .4) continue;
      var R = core * (m < 2.2 ? 5.5 : 3.2), spr = starSprite(st.bv + Math.min(.9, (X - 1) * .05));
      cx.globalAlpha = a; cx.drawImage(spr, p[0] - R, p[1] - R, R * 2, R * 2);
      var rad = core;
      hits.push({ x: p[0], y: p[1], o: st, l: l, kind: 'star' });
      if (st.name && LAY.names && st.mag < Math.min(limit, 6.05) - 3.3) labels.push({ x: p[0] + rad + 5, y: p[1], t: st.name, c: 'rgba(214,226,255,.86)', f: '500 12px ', pri: st.mag });
    }
    cx.restore(); cx.globalAlpha = 1;
    if (LAY.mine) drawMine(labels);
    // ดาวเคราะห์ ดวงจันทร์ ดวงอาทิตย์
    F.bodies.forEach(function (b) {
      var l = bodyLocal(b); if (b.id !== 'sun' && behindHill(l)) return;
      var p = proj(l); if (!onScreen(p, 30)) return;
      if (b.id === 'sun') { if (l[2] < -.02) return; drawSun(p); }
      else if (b.id === 'moon') drawMoon(p, l, sunL);
      else {
        var rad = clamp(3.4 - b.mag * .55, 1.6, 5.5) * Math.sqrt(zoomK) * .8;
        cx.fillStyle = { mer: '#d8cfc4', ven: '#fff6dc', mar: '#ff9a6a', jup: '#f3dcb4', sat: '#ead9a6', ura: '#bfe9f0', nep: '#8fb2ff' }[b.id];
        cx.globalAlpha = Math.max(.35, sc.starA);
        cx.beginPath(); cx.arc(p[0], p[1], rad, 0, 6.283); cx.fill(); cx.globalAlpha = 1;
        if (b.id === 'sat' && zoomK > 1.6) { cx.strokeStyle = 'rgba(234,217,166,.7)'; cx.beginPath(); cx.ellipse(p[0], p[1], rad * 2.3, rad * .8, -.35, 0, 6.283); cx.stroke(); }
      }
      hits.push({ x: p[0], y: p[1], o: b, l: l, kind: 'body', pri: -1 });
      if (LAY.names) labels.push({ x: p[0] + 10, y: p[1] - 12, t: b.name, c: '#ffffff', f: '600 13.5px ', pri: -30 });
    });
    // ชื่อกลุ่มดาว
    if (LAY.lines && LAY.names && sc.starA > .3) CONS.forEach(function (c) {
      if (c.rank > (zoomK > 1.4 ? 3 : 2) && !/[ก-๙]/.test(c.name)) return;
      var l = refract(local(c.v)); if (behindHill(l)) return;
      var p = proj(l); if (!onScreen(p, 0)) return;
      labels.push({ x: p[0], y: p[1], t: c.name, c: 'rgba(126,206,214,.78)', f: '400 13px ', pri: 10, center: true, spaced: true });
    });
    // พื้นดิน + ทิศ
    if (LAY.ground) ground(sc);
    cardinals();
    drawLabels(labels);
    if (LAY.red) { cx.save(); cx.globalCompositeOperation = 'multiply'; cx.fillStyle = '#ff2a1a'; cx.fillRect(0, 0, W, H); cx.restore(); }
    hud();
  }
  function projMW(l) {                                        // เหมือน proj แต่ยอมจุดค่อนไปข้างหลังมากกว่า (รูปหลายเหลี่ยมไม่ขาด)
    var x = l[0] * F.r[0] + l[1] * F.r[1] + l[2] * F.r[2], y = l[0] * F.u[0] + l[1] * F.u[1] + l[2] * F.u[2], z = l[0] * F.f[0] + l[1] * F.f[1] + l[2] * F.f[2];
    if (z < -.96) return null;
    var k = 2 / (1 + z) * F.s;
    return [F.W / 2 + x * k, F.H / 2 - y * k];
  }
  var MW_TINT = ['168,182,228', '182,192,232', '204,206,230', '226,214,214', '246,224,200'];   // ขอบนอกอมฟ้า → ใจกลางอุ่น
  function drawMilky(sc) {
    var q = .25, w = Math.max(1, Math.ceil(F.W * q)), h = Math.max(1, Math.ceil(F.H * q));
    if (!mwc) { mwc = document.createElement('canvas'); mwx = mwc.getContext('2d'); }
    if (mwc.width !== w || mwc.height !== h) { mwc.width = w; mwc.height = h; }
    mwx.setTransform(q, 0, 0, q, 0, 0); mwx.clearRect(0, 0, F.W, F.H);
    if ('filter' in mwx) mwx.filter = 'blur(1.6px)';
    mwx.globalCompositeOperation = 'lighter';
    MWL.forEach(function (level, li) {
      mwx.fillStyle = 'rgba(' + MW_TINT[li] + ',' + ((.055 + li * .012) * sc.starA).toFixed(3) + ')';
      level.forEach(function (ring) {
        mwx.beginPath(); var n = 0;
        for (var i = 0; i < ring.length; i++) { var p = projMW(local(ring[i])); if (!p) continue; if (n++) mwx.lineTo(p[0], p[1]); else mwx.moveTo(p[0], p[1]); }
        if (n > 2) { mwx.closePath(); mwx.fill(); }
      });
    });
    if ('filter' in mwx) mwx.filter = 'none';
    cx.save(); cx.globalCompositeOperation = 'lighter'; cx.imageSmoothingEnabled = true; cx.imageSmoothingQuality = 'high';
    cx.drawImage(mwc, 0, 0, F.W, F.H); cx.restore();
  }
  // ── กลุ่มดาวการตัดสินใจของฉัน: ทุกครั้งที่คุยกับ LYLA แล้วได้คำตอบ = ดาวหนึ่งดวง ณ จุดเหนือศีรษะตอนนั้น ─────────
  // ตำแหน่งบนฟ้าคงที่ตลอดไป (เหมือนดาวจริง) จึงขึ้นตก หมุนไปกับฟ้า · ต่อเส้นตามลำดับเวลา = กลุ่มดาวที่ไม่มีใครเหมือน
  // ข้อมูลอยู่ในเครื่องนี้เท่านั้น (static/app.js เขียน kd-my-stars: เวลา เส้นทาง ความเสี่ยง ตำแหน่งคร่าวๆ — ไม่มีข้อความ)
  var WL = 0, MINE = null, ROUTE_TH = { general: 'ชีวิตทั่วไป', risk: 'ประเมินความเสี่ยง', civil: 'สังคม/งาน', survival: 'ความอยู่รอด', collapse: 'ช่วงวิกฤต', crisis: 'ช่วงวิกฤต', vega: 'วิเคราะห์ระยะยาว' };
  function loadMine() {
    try { var L = JSON.parse(store('kd-my-stars') || '[]'); if (!Array.isArray(L)) L = []; } catch (e) { L = []; }
    MINE = L.filter(function (m) { return m && isFinite(m.t) && isFinite(m.la) && isFinite(m.lo); }).sort(function (a, b) { return a.t - b.t; }).map(function (m) {
      var ra = (gmst(jd(new Date(m.t))) + m.lo + 360) % 360;              // จุดเหนือศีรษะ = RA เท่ากับเวลาดาราคติท้องถิ่น · Dec = ละติจูด
      return { v: eqv(ra, m.la), t: m.t, r: m.r, k: m.k };
    });
    WL = waterline();
    var w = $('sky-wl'); if (w) w.textContent = WL > .5 ? T('ขอบฟ้าตอนนี้สูงขึ้น ' + WL.toFixed(1) + '° ตามความหนักของเรื่องล่าสุด — จะค่อยๆ ลดลงเอง และลดทันทีเมื่อเจอทางไปต่อ', 'Horizon raised ' + WL.toFixed(1) + '° by your latest heavy topic — it lowers as you find a way forward') : '';
    var n = $('sky-mine-n'); if (n) n.textContent = MINE.length ? T('ดาวของฉัน ' + MINE.length + ' ดวง — เกิดจากทุกครั้งที่ปรึกษา LYLA แล้วได้ทางไปต่อ', 'My stars: ' + MINE.length) : T('ยังไม่มีดาวของฉัน — ปรึกษา LYLA สักเรื่อง แล้วดาวดวงแรกจะเกิดบนฟ้าตรงเหนือหัวคุณ', 'No stars yet — talk to LYLA and your first star appears overhead');
  }
  function drawMine(labels) {
    if (!MINE || !MINE.length) return;
    var pts = MINE.map(function (m) { var l = refract(local(m.v)); return { m: m, l: l, p: proj(l) }; });
    cx.save();
    cx.strokeStyle = 'rgba(237,204,98,.5)'; cx.lineWidth = 1.2; cx.setLineDash([4, 5]);
    cx.beginPath(); var pen = false;
    pts.forEach(function (q) { if (!q.p || (LAY.ground && q.l[2] < -.01)) { pen = false; return; } if (pen) cx.lineTo(q.p[0], q.p[1]); else cx.moveTo(q.p[0], q.p[1]); pen = true; });
    cx.stroke(); cx.setLineDash([]);
    pts.forEach(function (q, i) {
      if (!onScreen(q.p, 10) || behindHill(q.l)) return;
      var x = q.p[0], y = q.p[1], last = i === pts.length - 1, r = last ? 7 : 5;
      var g = cx.createRadialGradient(x, y, 0, x, y, r * 3.2);
      g.addColorStop(0, 'rgba(255,226,150,.85)'); g.addColorStop(1, 'rgba(255,210,120,0)');
      cx.fillStyle = g; cx.fillRect(x - r * 3.2, y - r * 3.2, r * 6.4, r * 6.4);
      cx.fillStyle = '#ffe7a6'; cx.beginPath();                   // ดาวสี่แฉกสีทอง — แยกออกจากดาวจริงได้ทันที
      cx.moveTo(x, y - r); cx.quadraticCurveTo(x, y, x + r, y); cx.quadraticCurveTo(x, y, x, y + r); cx.quadraticCurveTo(x, y, x - r, y); cx.quadraticCurveTo(x, y, x, y - r); cx.fill();
      hits.push({ x: x, y: y, o: { mine: q.m, mag: -30 }, l: q.l, kind: 'body' });
      if (last && LAY.names) labels.push({ x: x + 10, y: y - 10, t: T('ดาวล่าสุดของฉัน', 'My latest star'), c: '#ffe7a6', f: '600 12.5px ', pri: -40 });
    });
    cx.restore();
  }
  function path(fn, n) {
    cx.beginPath(); var pen = false;
    for (var i = 0; i < n; i++) { var p = proj(fn(i)); if (!p || p[2] < -.3) { pen = false; continue; } if (pen) cx.lineTo(p[0], p[1]); else cx.moveTo(p[0], p[1]); pen = true; }
    cx.stroke();
  }
  function drawSun(p) {
    var r = Math.max(10, .27 * F.s * D2R * 2), g = cx.createRadialGradient(p[0], p[1], 0, p[0], p[1], r * 6);
    g.addColorStop(0, 'rgba(255,250,230,1)'); g.addColorStop(.18, 'rgba(255,236,190,.9)'); g.addColorStop(1, 'rgba(255,220,160,0)');
    cx.fillStyle = g; cx.fillRect(p[0] - r * 6, p[1] - r * 6, r * 12, r * 12);
  }
  function drawMoon(p, l, sunL) {                              // เฟสจริง: ด้านสว่างหันไปทางดวงอาทิตย์
    var r = Math.max(6, .26 * D2R * F.s * 2 / (1 + p[2]) * 1.0);
    var cosE = clamp(l[0] * sunL[0] + l[1] * sunL[1] + l[2] * sunL[2], -1, 1), k = (1 - cosE) / 2;
    var ahead = [l[0] + (sunL[0] - l[0]) * .01, l[1] + (sunL[1] - l[1]) * .01, l[2] + (sunL[2] - l[2]) * .01], q = proj(ahead);
    var ang = q ? Math.atan2(q[1] - p[1], q[0] - p[0]) : 0;
    cx.save(); cx.translate(p[0], p[1]); cx.rotate(ang);
    var glow = cx.createRadialGradient(0, 0, r * .8, 0, 0, r * 4); glow.addColorStop(0, 'rgba(230,235,255,' + (.25 * k).toFixed(3) + ')'); glow.addColorStop(1, 'rgba(230,235,255,0)');
    cx.fillStyle = glow; cx.fillRect(-r * 4, -r * 4, r * 8, r * 8);
    cx.fillStyle = 'rgba(40,44,58,.9)'; cx.beginPath(); cx.arc(0, 0, r, 0, 6.283); cx.fill();
    cx.fillStyle = '#f4f1e6'; cx.beginPath();
    cx.arc(0, 0, r, -Math.PI / 2, Math.PI / 2, false);
    cx.ellipse(0, 0, Math.abs(r * (1 - 2 * k)), r, 0, Math.PI / 2, -Math.PI / 2, k < .5);
    cx.fill(); cx.restore();
  }
  // ขอบฟ้า = เส้น Waterline: เรื่องล่าสุดที่ปรึกษายิ่งหนัก (ความเสี่ยงสูง ทางเลือกน้อย) ขอบฟ้ายิ่งสูง ดาวถูกบังมากขึ้น
  // ค่อยๆ ลดกลับเองใน ~3 วัน · ปรึกษาเรื่องใหม่แล้วเบาลง = ขอบฟ้าลดทันที ดาวกลับมาเต็มฟ้า (Choice(t) ≥ 1 ที่มองเห็นได้)
  function waterline() {
    if (!MINE || !MINE.length) return 0;
    var m = MINE[MINE.length - 1], age = (Date.now() - m.t) / 86400000;
    return clamp((m.k - 30) / 70, 0, 1) * 9 * Math.exp(-Math.max(0, age) / 3);
  }
  function behindHill(l) {                                    // อยู่หลังแนวเขา/ขอบฟ้าที่ยกขึ้นไหม (เช็กเฉพาะใกล้ขอบฟ้า — เร็ว)
    if (!LAY.ground) return false;
    if (l[2] < -.01) return true;
    if (l[2] > .2 + WL * .018) return false;
    var aa = altaz(l); return aa[1] < hill(aa[0]) - .2;
  }
  function hill(az) {                                         // แนวเขาไกลๆ แบบตายตัว (องศา) — ไม่ใช่ภาพจริงของที่ไหน
    var a = az * D2R;
    return WL + Math.max(0, .9 + .55 * Math.sin(a * 3 + 1.3) + .35 * Math.sin(a * 7 + .4) + .25 * Math.sin(a * 13 + 2.2) + .12 * Math.sin(a * 29));
  }
  function ground(sc) {
    // พื้นทั้งแผ่น = วงกลมขอบฟ้าบนจอ (stereographic ส่งวงกลมเป็นวงกลม) · จุดกลางจอคือฟ้าเสมอเมื่อมองเหนือขอบฟ้า
    // → ระบายฝั่งที่ไม่มีจุดกลางจอ · ใช้ 3 จุดบนขอบฟ้าที่อยู่ด้านหน้าเสมอ (ทิศที่มอง ±60°)
    var A = proj(fromAltAz(V.az - 60, 0)), B = proj(fromAltAz(V.az, 0)), C = proj(fromAltAz(V.az + 60, 0));
    var col = 'rgb(' + Math.round(6 + 30 * sc.k) + ',' + Math.round(8 + 32 * sc.k) + ',' + Math.round(12 + 26 * sc.k) + ')';
    cx.fillStyle = col;
    var circ = A && B && C ? circle(A, B, C) : null, skyUp = V.alt >= 0;
    if (circ && circ[2] < 1e6) {
      var centerIn = Math.hypot(F.W / 2 - circ[0], F.H / 2 - circ[1]) < circ[2];
      cx.beginPath();
      // 2π พอดี = วงเต็ม (6.283 แบบทวนเข็มจะได้แค่เสี้ยวเดียว แล้วพื้นทับทั้งจอ)
      if (centerIn === skyUp) { cx.rect(-10, -10, F.W + 20, F.H + 20); cx.arc(circ[0], circ[1], circ[2], 0, Math.PI * 2, true); cx.fill('evenodd'); }
      else { cx.arc(circ[0], circ[1], circ[2], 0, Math.PI * 2); cx.fill(); }
    } else if (B) {                                            // วงกลมใหญ่มากจนเป็นเส้นตรง
      cx.fillRect(0, B[1], F.W, F.H);
    }
    // แนวเขาไกลๆ: แถบระหว่างเส้นเขากับขอบฟ้า เฉพาะช่วงที่อยู่ด้านหน้า (ไม่ลากข้ามจอ)
    var run = [];
    function flush() {
      if (run.length > 1) {
        cx.beginPath();
        run.forEach(function (q, n) { if (n) cx.lineTo(q[0][0], q[0][1]); else cx.moveTo(q[0][0], q[0][1]); });
        for (var n = run.length - 1; n >= 0; n--) cx.lineTo(run[n][1][0], run[n][1][1]);
        cx.closePath(); cx.fill();
      }
      run = [];
    }
    for (var az = 0; az <= 360; az += 1.5) {
      var top = proj(refract(fromAltAz(az, hill(az)))), base = proj(fromAltAz(az, -.5));
      if (!top || !base || top[2] < .05 || base[2] < .05) { flush(); continue; }
      run.push([top, base]);
    }
    flush();
  }
  function circle(a, b, c) {
    var d = 2 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]));
    if (Math.abs(d) < 1e-6) return null;
    var a2 = a[0] * a[0] + a[1] * a[1], b2 = b[0] * b[0] + b[1] * b[1], c2 = c[0] * c[0] + c[1] * c[1];
    var ux = (a2 * (b[1] - c[1]) + b2 * (c[1] - a[1]) + c2 * (a[1] - b[1])) / d, uy = (a2 * (c[0] - b[0]) + b2 * (a[0] - c[0]) + c2 * (b[0] - a[0])) / d;
    return [ux, uy, Math.hypot(a[0] - ux, a[1] - uy)];
  }
  var CARD = THAI ? ['เหนือ', 'ตะวันออกเฉียงเหนือ', 'ตะวันออก', 'ตะวันออกเฉียงใต้', 'ใต้', 'ตะวันตกเฉียงใต้', 'ตะวันตก', 'ตะวันตกเฉียงเหนือ']
                  : ['North', 'NE', 'East', 'SE', 'South', 'SW', 'West', 'NW'];
  function cardinals() {
    for (var i = 0; i < 8; i++) {
      var p = proj(fromAltAz(i * 45, -2.2)); if (!onScreen(p, 0) || p[2] < 0) continue;
      p = [p[0], Math.min(p[1], F.H - 132)];                     // ไม่ทับแถบปุ่มด้านล่าง (จอเตี้ยก็อ่านได้)
      var big = i % 2 === 0;
      cx.fillStyle = big ? '#e0645c' : 'rgba(224,100,92,.7)'; cx.textAlign = 'center'; cx.textBaseline = 'top';
      cx.font = (big ? '700 22px ' : '500 13px ') + FONT;
      cx.beginPath(); cx.arc(p[0], p[1] - 8, big ? 3.5 : 2.5, 0, 6.283); cx.fill();
      cx.fillText(CARD[i], p[0], p[1]);
    }
    cx.textAlign = 'left';
  }
  var FONT = '"Noto Sans Thai Looped","Noto Sans Thai",system-ui,sans-serif';
  function drawLabels(L) {
    L.sort(function (a, b) { return a.pri - b.pri; });
    var boxes = [];
    cx.textBaseline = 'middle'; cx.shadowColor = 'rgba(0,0,0,.9)'; cx.shadowBlur = 4;
    L.forEach(function (o) {
      cx.font = o.f + FONT;
      var t = o.spaced && /[A-Za-z]/.test(o.t) ? o.t.toUpperCase() : o.t;
      if (o.spaced && 'letterSpacing' in cx) cx.letterSpacing = '3px';
      var w = cx.measureText(t).width, x = o.center ? o.x - w / 2 : o.x, bx = [x - 4, o.y - 9, x + w + 4, o.y + 9];
      for (var j = 0; j < boxes.length; j++) { var b = boxes[j]; if (bx[0] < b[2] && bx[2] > b[0] && bx[1] < b[3] && bx[3] > b[1]) { if ('letterSpacing' in cx) cx.letterSpacing = '0px'; return; } }
      boxes.push(bx); cx.fillStyle = o.c; cx.fillText(t, x, o.y);
      if ('letterSpacing' in cx) cx.letterSpacing = '0px';
    });
    cx.shadowBlur = 0;
  }

  // ── แถบข้อมูล ────────────────────────────────────────────────────────────────────────────
  var $ = function (id) { return document.getElementById(id); };
  function hud() {
    var d = F.d, hh = ('0' + d.getHours()).slice(-2), mm = ('0' + d.getMinutes()).slice(-2);
    $('sky-time').textContent = hh + ':' + mm;
    $('sky-time').classList.toggle('shifted', offsetMin !== 0);
    $('sky-fov').textContent = 'FOV ' + V.fov.toFixed(1) + '°';
    $('sky-rose').style.transform = 'rotate(' + (-V.az).toFixed(1) + 'deg)';
    var place = loc.name || (Math.abs(loc.lat).toFixed(1) + '°' + (loc.lat < 0 ? 'S' : 'N') + ' ' + Math.abs(loc.lon).toFixed(1) + '°' + (loc.lon < 0 ? 'W' : 'E'));
    var offH = loc.lon / 15 + d.getTimezoneOffset() / 60;                   // ต่างจากเวลาเครื่องกี่ชั่วโมง (ประมาณจากลองจิจูด)
    if (Math.abs(offH) >= 1.5) {
      var t2 = new Date(d.getTime() + Math.round(offH) * 3600000);
      place += T(' · เวลาที่นั่น ≈ ', ' · local ≈ ') + ('0' + t2.getHours()).slice(-2) + ':' + ('0' + t2.getMinutes()).slice(-2);
    }
    $('sky-loc').textContent = place;
  }

  // ── วงจรวาด ─────────────────────────────────────────────────────────────────────────────
  function kick() { if (!raf) raf = requestAnimationFrame(frame); }
  function frame() {
    raf = 0;
    if (document.hidden || !CAT) return;
    if (tgt) {
      var da = ((tgt.az - V.az + 540) % 360) - 180, k = .16;
      V.az = (V.az + da * k + 360) % 360; V.alt += (tgt.alt - V.alt) * k; V.fov += (tgt.fov - V.fov) * k;
      if (Math.abs(da) < .05 && Math.abs(tgt.alt - V.alt) < .05 && Math.abs(tgt.fov - V.fov) < .05) tgt = null;
      dirty = true;
    }
    if (sensor && sensor.v) {
      var s = sensor.v, d2 = ((s[0] - V.az + 540) % 360) - 180;
      V.az = (V.az + d2 * .25 + 360) % 360; V.alt += (s[1] - V.alt) * .25; dirty = true;
    }
    if (dirty || Date.now() - lastDraw > 10000) draw();
    if (tgt || sensor) kick();
  }
  setInterval(kick, 10000);
  document.addEventListener('visibilitychange', function () { dirty = true; kick(); });
  window.addEventListener('resize', size);

  // ── นิ้ว/เมาส์ ───────────────────────────────────────────────────────────────────────────
  var ptr = {}, gest = null;
  function degPx() { return V.fov / Math.max(1, cv.clientHeight); }
  cv.addEventListener('pointerdown', function (e) {
    cv.setPointerCapture(e.pointerId); ptr[e.pointerId] = [e.clientX, e.clientY]; tgt = null;
    var ids = Object.keys(ptr);
    gest = ids.length === 2 ? { pinch: Math.hypot(ptr[ids[0]][0] - ptr[ids[1]][0], ptr[ids[0]][1] - ptr[ids[1]][1]), fov: V.fov }
                            : { x: e.clientX, y: e.clientY, moved: 0 };
  });
  cv.addEventListener('pointermove', function (e) {
    if (!ptr[e.pointerId] || !gest) return;
    var dx = e.clientX - ptr[e.pointerId][0], dy = e.clientY - ptr[e.pointerId][1]; ptr[e.pointerId] = [e.clientX, e.clientY];
    var ids = Object.keys(ptr);
    if (gest.pinch && ids.length === 2) {
      var dd = Math.hypot(ptr[ids[0]][0] - ptr[ids[1]][0], ptr[ids[0]][1] - ptr[ids[1]][1]);
      V.fov = clamp(gest.fov * gest.pinch / Math.max(1, dd), 1, 120);
    } else if (!gest.pinch) {
      if (sensor) stopSensor();
      gest.moved += Math.abs(dx) + Math.abs(dy);
      var g = degPx();
      V.az = (V.az - dx * g / Math.max(.3, Math.cos(V.alt * D2R)) * .9 + 360) % 360; V.alt = clamp(V.alt + dy * g, -20, 90);
    }
    dirty = true; kick();
  });
  function up(e) {
    var was = gest; delete ptr[e.pointerId]; gest = Object.keys(ptr).length ? gest : null;
    if (was && !was.pinch && was.moved < 6) tap(e.clientX, e.clientY);
  }
  cv.addEventListener('pointerup', up); cv.addEventListener('pointercancel', up);
  cv.addEventListener('wheel', function (e) { e.preventDefault(); V.fov = clamp(V.fov * Math.exp(e.deltaY * .0012), 1, 120); tgt = null; dirty = true; kick(); }, { passive: false });
  window.addEventListener('keydown', function (e) {
    if (/INPUT|TEXTAREA/.test((e.target || {}).tagName || '')) return;
    var k = e.key, s = V.fov / 10;
    if (k === 'ArrowLeft') V.az = (V.az - s + 360) % 360; else if (k === 'ArrowRight') V.az = (V.az + s) % 360;
    else if (k === 'ArrowUp') V.alt = clamp(V.alt + s, -20, 90); else if (k === 'ArrowDown') V.alt = clamp(V.alt - s, -20, 90);
    else if (k === '+' || k === '=') V.fov = clamp(V.fov / 1.25, 1, 120); else if (k === '-') V.fov = clamp(V.fov * 1.25, 1, 120);
    else if (k === 'Escape') { closeAll(); return; } else return;
    dirty = true; kick();
  });

  // ── แตะดาว = รายละเอียด ─────────────────────────────────────────────────────────────────
  function tap(x, y) {
    var r = cv.getBoundingClientRect(); x -= r.left; y -= r.top;
    var best = null, bd = 1e9;
    hits.forEach(function (h) { var d = Math.hypot(h.x - x, h.y - y) + (h.kind === 'body' ? -8 : h.o.mag * 1.5); if (Math.hypot(h.x - x, h.y - y) < 26 && d < bd) { bd = d; best = h; } });
    if (best) info(best); else $('sky-info').classList.add('hide');
  }
  function info(h) {
    var aa = altaz(h.l), o = h.o, box = $('sky-info'), lines = [];
    if (o.mine) {
      var dt = new Date(o.mine.t);
      box.textContent = '';
      [['b', T('ดาวของฉัน', 'My star')], ['span', dt.toLocaleDateString(THAI ? 'th-TH' : 'en-GB', { day: 'numeric', month: 'long', year: 'numeric' }) + ' · ' + ('0' + dt.getHours()).slice(-2) + ':' + ('0' + dt.getMinutes()).slice(-2)],
       ['span', T('เรื่อง: ', 'Topic: ') + (ROUTE_TH[o.mine.r] || o.mine.r)], ['i', T('คืนนั้นดาวดวงนี้อยู่ตรงเหนือหัวคุณพอดี — คุณผ่านมันมาแล้ว', 'That night this point was right above you — and you came through it')]]
        .forEach(function (ln) { var e = document.createElement(ln[0]); e.textContent = ln[1]; box.appendChild(e); });
      box.classList.remove('hide'); return;
    }
    var nm = o.name || T('ดาวไม่มีชื่อเรียก', 'Unnamed star');
    lines.push(['b', nm]);
    if (o.en && o.en !== nm) lines.push(['i', o.en]);
    if (o.mag != null && o.id !== 'sun' && o.id !== 'moon') lines.push(['s', T('ความสว่าง (โชติมาตร) ', 'Magnitude ') + o.mag.toFixed(1)]);
    if (o.au) lines.push(['s', T('ระยะ ', 'Distance ') + (o.au < 2 ? o.au.toFixed(3) : o.au.toFixed(2)) + ' AU' + T(' (ราว ', ' (~') + Math.round(o.au * 8.317) + T(' นาทีแสง)', ' light-min)')]);
    lines.push(['s', T('ทิศ ', 'Azimuth ') + aa[0].toFixed(1) + '° · ' + T('มุมเงย ', 'Altitude ') + aa[1].toFixed(1) + '°' + (aa[1] < 0 ? T(' (อยู่ใต้ขอบฟ้า)', ' (below horizon)') : '')]);
    box.textContent = '';
    lines.forEach(function (ln) { var e = document.createElement(ln[0] === 's' ? 'span' : ln[0]); e.textContent = ln[1]; box.appendChild(e); });
    box.classList.remove('hide');
  }

  // ── ค้นหา ───────────────────────────────────────────────────────────────────────────────
  function lookAt(l, fov) { var aa = altaz(l); tgt = { az: aa[0], alt: clamp(aa[1], -20, 90), fov: fov || Math.min(V.fov, 50) }; kick(); }
  function search(q) {
    q = q.trim().toLowerCase(); var out = [];
    if (!q || !F) return out;
    F.bodies.forEach(function (b) { if ((b.name + ' ' + b.id).toLowerCase().indexOf(q) >= 0) out.push({ t: b.name, go: function () { lookAt(bodyLocal(b), 30); info({ o: b, l: bodyLocal(b) }); } }); });
    STARS.forEach(function (s) { if (s.name && (s.name + ' ' + s.en).toLowerCase().indexOf(q) >= 0) out.push({ t: s.name, go: function () { var l = refract(local(s.v)); lookAt(l, 30); info({ o: s, l: l }); } }); });
    CONS.forEach(function (c) { if ((c.name + ' ' + c.en).toLowerCase().indexOf(q) >= 0) out.push({ t: c.name + ' · ' + T('กลุ่มดาว', 'constellation'), go: function () { lookAt(refract(local(c.v)), 45); } }); });
    if (MINE && MINE.length && /ของฉัน|ของผม|mine|my/i.test(q)) out.unshift({ t: T('ดาวของฉัน (ล่าสุด)', 'My latest star'), go: function () { lookAt(refract(local(MINE[MINE.length - 1].v)), 60); } });
    return out.slice(0, 8);
  }
  $('sky-search-in').addEventListener('input', function () {
    var ul = $('sky-results'); ul.textContent = '';
    search(this.value).forEach(function (r) {
      var b = document.createElement('button'); b.type = 'button'; b.textContent = r.t;
      b.addEventListener('click', function () { r.go(); closeAll(); }); ul.appendChild(b);
    });
  });

  // ── แผงเครื่องมือ (ปุ่มซ้ายล่าง) ─────────────────────────────────────────────────────────────
  function closeAll() { $('sky-sheet').classList.add('hide'); $('sky-search').classList.add('hide'); $('sky-info').classList.add('hide'); }
  function toggle(id) { var el = $(id), was = el.classList.contains('hide'); closeAll(); if (was) el.classList.remove('hide'); }
  $('sky-layers').addEventListener('click', function () { toggle('sky-sheet'); });
  $('sky-find').addEventListener('click', function () { toggle('sky-search'); if (!$('sky-search').classList.contains('hide')) $('sky-search-in').focus(); });
  $('sky-rose-btn').addEventListener('click', function () { tgt = { az: 0, alt: V.alt, fov: V.fov }; kick(); });
  function syncLayers() {
    document.querySelectorAll('[data-layer]').forEach(function (b) { b.setAttribute('aria-pressed', LAY[b.getAttribute('data-layer')] ? 'true' : 'false'); });
    document.documentElement.classList.toggle('sky-red', LAY.red);
    store('kd-sky-layers', JSON.stringify(LAY));
  }
  document.querySelectorAll('[data-layer]').forEach(function (b) {
    b.addEventListener('click', function () { var k = b.getAttribute('data-layer'); LAY[k] = !LAY[k]; syncLayers(); dirty = true; kick(); });
  });
  document.querySelectorAll('[data-time]').forEach(function (b) {
    b.addEventListener('click', function () { var v = b.getAttribute('data-time'); offsetMin = v === 'now' ? 0 : offsetMin + Number(v); prepDay = -1; dirty = true; kick(); });
  });
  $('sky-here').addEventListener('click', function () {
    if (!navigator.geolocation) return;
    var btn = this; btn.setAttribute('aria-busy', 'true');
    navigator.geolocation.getCurrentPosition(function (p) {
      loc = { lat: +p.coords.latitude.toFixed(3), lon: +p.coords.longitude.toFixed(3), name: T('ตำแหน่งของฉัน', 'My location') };
      store('kd-sky-loc', JSON.stringify(loc)); btn.removeAttribute('aria-busy'); dirty = true; kick();
    }, function () { btn.removeAttribute('aria-busy'); }, { maximumAge: 6e5, timeout: 15000 });
  });

  // ── ชี้มือถือขึ้นฟ้า: ภาพหมุนตามทิศจริงของเครื่อง ───────────────────────────────────────────────
  function onOrient(e) {
    var al = e.webkitCompassHeading != null ? 360 - e.webkitCompassHeading : e.alpha;
    if (al == null || e.beta == null) return;
    if (!e.absolute && e.webkitCompassHeading == null && e.type !== 'deviceorientationabsolute') return;   // ไม่รู้ทิศเหนือจริง = ไม่เดา
    var a = al * D2R, b = e.beta * D2R, g = (e.gamma || 0) * D2R;
    var vx = -Math.cos(a) * Math.sin(g) - Math.sin(a) * Math.sin(b) * Math.cos(g),
        vy = -Math.sin(a) * Math.sin(g) + Math.cos(a) * Math.sin(b) * Math.cos(g), vz = -Math.cos(b) * Math.cos(g);
    sensor.v = [((Math.atan2(vx, vy) * R2D) + 360) % 360, clamp(Math.asin(clamp(vz, -1, 1)) * R2D, -20, 90)];
    kick();
  }
  function stopSensor() {
    window.removeEventListener('deviceorientationabsolute', onOrient); window.removeEventListener('deviceorientation', onOrient);
    sensor = null; $('sky-aim').setAttribute('aria-pressed', 'false');
  }
  $('sky-aim').addEventListener('click', function () {
    if (sensor) { stopSensor(); return; }
    function start() {
      sensor = { v: null }; $('sky-aim').setAttribute('aria-pressed', 'true');
      if ('ondeviceorientationabsolute' in window) window.addEventListener('deviceorientationabsolute', onOrient);
      else window.addEventListener('deviceorientation', onOrient);
      closeAll();
    }
    var DOE = window.DeviceOrientationEvent;
    if (DOE && typeof DOE.requestPermission === 'function') DOE.requestPermission().then(function (s) { if (s === 'granted') start(); }).catch(function () {});
    else if (DOE) start();
  });

  // ── เริ่ม ────────────────────────────────────────────────────────────────────────────────
  syncLayers(); size(); loadMine();
  window.addEventListener('storage', function (e) { if (e.key === 'kd-my-stars') { loadMine(); dirty = true; kick(); } });
  fetch('/static/sky/catalog.json').then(function (r) { return r.ok ? r.json() : null; }).then(function (d) {
    if (!d || !d.stars) return;
    CAT = d; dirty = true; document.documentElement.classList.add('sky-ready'); kick();
    var later = loadLater;
    later('milkyway.json', function (x) { MWRAW = x; });
    (window.requestIdleCallback || function (f) { setTimeout(f, 1500); })(function () { later('deep.json', function (x) { DEEP = x; }); });
  }).catch(function () {});
  function loadLater(f, set) {
    fetch('/static/sky/' + f).then(function (r) { return r.ok ? r.json() : null; }).then(function (x) { if (x) { set(x); prepDay = -1; dirty = true; kick(); } }).catch(function () {});
  }
  window.KD_sky = { stars: function () { return STARS ? STARS.length : 0; }, drawn: function () { return hits.length; }, view: V, loc: function () { return loc; }, setTime: function (m) { offsetMin = m; prepDay = -1; dirty = true; kick(); },
                    _test: { jd: jd, gmst: gmst, kepler: kepler, moon: moon, precess: precess, bodies: function () { frameSetup(); return F.bodies.map(function (b) { return { id: b.id, altaz: altaz(bodyLocal(b)) }; }); },
                             load: function (d) { CAT = d; prepDay = -1; }, at: function (ms) { offsetMin = (ms - Date.now()) / 60000; prepDay = -1; },
                             starAltAz: function (i) { frameSetup(); return altaz(refract(local(STARS[i].v))); }, setLoc: function (l) { loc = l; dirty = true; } } };
})();
