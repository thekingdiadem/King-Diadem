/* ตำแหน่งดาวเคราะห์จริงจากธาตุวงโคจรประมาณของ JPL (แม่นราว 1 ลิปดา ช่วง ค.ศ. 1800–2050)
 * ใช้กับหน้าจักรวาล (universe_sky.js) — window.KD_astro.planets(date, catalog.planets)
 * คืนทิศของดาวเคราะห์เมื่อมองจากโลก เป็นเวกเตอร์ศูนย์สูตร J2000 พร้อมระยะ (AU)
 * สูตรเดียวกับ static/sky_view.js (หน้าดูดาว) ซึ่งเทียบกับ astropy ไว้ใน tests/test_sky_view.py */
(function () {
  'use strict';
  var D2R = Math.PI / 180, OBL = 23.43928 * D2R;
  function kepler(el, t) {
    var a = el.a + el.da * t, e = el.e + el.de * t, i = (el.i + el.di * t) * D2R, L = el.L + el.dL * t,
        W = el.W + el.dW * t, N = (el.N + el.dN * t) * D2R, w = W * D2R - N, M = (((L - W) % 360 + 540) % 360 - 180) * D2R;
    var E = M + e * Math.sin(M);
    for (var k = 0; k < 8; k++) E -= (E - e * Math.sin(E) - M) / (1 - e * Math.cos(E));
    var xp = a * (Math.cos(E) - e), yp = a * Math.sqrt(1 - e * e) * Math.sin(E);
    var cw = Math.cos(w), sw = Math.sin(w), cN = Math.cos(N), sN = Math.sin(N), ci = Math.cos(i), si = Math.sin(i);
    return [(cw * cN - sw * sN * ci) * xp + (-sw * cN - cw * sN * ci) * yp,
            (cw * sN + sw * cN * ci) * xp + (-sw * sN + cw * cN * ci) * yp,
            (sw * si) * xp + (cw * si) * yp];
  }
  function ecl2eq(v) { return [v[0], v[1] * Math.cos(OBL) - v[2] * Math.sin(OBL), v[1] * Math.sin(OBL) + v[2] * Math.cos(OBL)]; }
  function planets(date, P) {
    var t = (date.getTime() / 86400000 + 2440587.5 - 2451545) / 36525, E = kepler(P.ter.el, t);
    return ['mer', 'ven', 'mar', 'jup', 'sat', 'ura', 'nep'].map(function (k) {
      var p = kepler(P[k].el, t), g = ecl2eq([p[0] - E[0], p[1] - E[1], p[2] - E[2]]), d = Math.hypot(g[0], g[1], g[2]);
      return { id: k, v: [g[0] / d, g[1] / d, g[2] / d], au: d, th: P[k].th, en: P[k].en, kind: P[k].kind, kind_en: P[k].kind_en };
    });
  }
  window.KD_astro = { kepler: kepler, planets: planets };
})();
