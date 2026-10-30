/* พระพุทธรูปองค์ใหญ่ วัดม่วง อ่างทอง — ปั้นด้วยโค้ดล้วน ไม่มีไฟล์โมเดล ไม่มีรูปภาพ
 *
 * · รูปทรง = ระยะถึงผิว (signed distance) ของชิ้นส่วนหลายชิ้น หลอมรวมกันแบบนุ่มๆ (smooth union)
 *   หน้าตักขัดสมาธิ ลำตัว ไหล่ แขน พระหัตถ์ปางมารวิชัย (ขวาวางเข่า ซ้ายวางตัก) คอ พระเศียร ใบหู พระนาสิก พระเกตุมาลา พระรัศมีเปลว
 * · แปลงเป็นผิวสามเหลี่ยมด้วย surface nets แล้วใช้ความชันของระยะเป็นทิศผิว — ผิวโค้งเนียน ไม่เป็นขั้นบันได
 * · สร้างครั้งเดียวตอนซูมเข้าใกล้ ใน Web Worker (ไฟล์เดียวกันนี้) จอจึงไม่ค้าง — คนที่ไม่ได้ไปดูอ่างทองไม่เสียแรงเครื่องเลย
 * · วาดเป็น custom layer ของ MapLibre ใช้ความลึกร่วมกับตึก/ภูเขา · สีทองสะท้อนแสง · กลางคืนมีไฟส่องจากด้านล่าง
 * สัดส่วน: สูง ~92 ม. จากพื้น (ลาน 12 ม. + องค์พระ 80 ม.) หน้าตัก ~63 ม. — ตามข้อมูลที่เผยแพร่ ไม่ได้ลอกจากภาพใด
 */
(function () {
  function len(x, y, z) { return Math.sqrt(x * x + y * y + z * z); }
  function ell(px, py, pz, cx, cy, cz, rx, ry, rz) {             // วงรีสามแกน (ประมาณระยะแบบที่ใช้กันทั่วไป)
    var x = (px - cx) / rx, y = (py - cy) / ry, z = (pz - cz) / rz, k0 = len(x, y, z);
    var k1 = len(x / rx, y / ry, z / rz);
    return k1 > 0 ? k0 * (k0 - 1) / k1 : -Math.min(rx, ry, rz);
  }
  function cap(px, py, pz, ax, ay, az, bx, by, bz, ra, rb) {     // แท่งปลายมน รัศมีค่อยๆ เปลี่ยนจาก ra ไป rb
    var bax = bx - ax, bay = by - ay, baz = bz - az, pax = px - ax, pay = py - ay, paz = pz - az;
    var h = (pax * bax + pay * bay + paz * baz) / (bax * bax + bay * bay + baz * baz);
    h = h < 0 ? 0 : h > 1 ? 1 : h;
    return len(pax - bax * h, pay - bay * h, paz - baz * h) - (ra + (rb - ra) * h);
  }
  function smin(a, b, k) { var h = Math.max(k - Math.abs(a - b), 0) / k; return Math.min(a, b) - h * h * k * .25; }

  // แกน: x = ซ้ายขวาขององค์พระ (+x = ด้านซ้ายพระองค์) · y = ขึ้น · z = ด้านหน้า (ทิศที่องค์พระหัน) · หน่วยเมตร · y=0 = พื้นลาน
  function sdf(x, y, z) {
    return smin(y < 62 ? body(x, y, z) : 1e3, y > 42 ? head(x, y, z) : 1e3, 2.5);   // ตัดชิ้นที่อยู่ไกลทิ้ง เร็วขึ้นราวครึ่ง
  }
  function body(x, y, z) {
    var d = ell(x, y, z, 0, 7, -1, 31, 8.5, 19);                                        // ฐานหน้าตัก
    d = smin(d, cap(x, y, z, -27, 6, 2, 17, 6.5, 13, 6.5, 7.5), 3);                     // หน้าแข้งขวาทับซ้าย
    d = smin(d, cap(x, y, z, 27, 5, 1, -14, 6, 12, 6.5, 6.5), 3);
    d = smin(d, ell(x, y, z, 0, 27, -7, 14.5, 18, 10), 6);                              // ลำตัว
    d = smin(d, ell(x, y, z, 0, 38, -7, 18, 10, 10), 5);                                // อก
    d = smin(d, cap(x, y, z, -15, 44, -7, 15, 44, -7, 6.5, 6.5), 5);                    // ไหล่
    d = smin(d, cap(x, y, z, -19, 43, -7, -22, 25, -2, 5.2, 4.6), 3);                   // ต้นแขนขวา
    d = smin(d, cap(x, y, z, 19, 43, -7, 21, 25, -3, 5.2, 4.6), 3);                     // ต้นแขนซ้าย
    d = smin(d, cap(x, y, z, -22, 25, -2, -23, 10, 14, 4.4, 3.6), 2.5);                 // แขนขวาทอดลงที่เข่า
    d = smin(d, ell(x, y, z, -23, 7, 16, 4, 5.5, 3), 1.5);                              // พระหัตถ์ขวาคว่ำบนเข่า
    if (z > 15 && y < 10 && x < -20) for (var f = 0; f < 4; f++)                         // นิ้วพระหัตถ์ชี้ลงแตะธรณี
      d = smin(d, cap(x, y, z, -25.6 + f * 1.7, 6, 18, -25.6 + f * 1.7, 1.5, 18.8, .75, .6), .5);
    d = smin(d, cap(x, y, z, 21, 25, -3, 7, 15, 4, 4.4, 3.6), 2.5);                     // แขนซ้ายวางตัก
    d = smin(d, ell(x, y, z, 3, 15, 5, 7.5, 2.4, 5), 1.5);                              // พระหัตถ์ซ้ายหงายบนตัก
    if (x > -2 && y > 27 && z > -4) for (var b = -1; b <= 1; b++) {                    // ผ้าสังฆาฏิพาดบ่าซ้าย เป็นแถบแบนกว้าง ~4 ม.
      d = smin(d, cap(x, y, z, 12 + b * 1.4, 47, -1.5, 7 + b * 1.4, 38, 2.1, .75, .75), .35);
      d = smin(d, cap(x, y, z, 7 + b * 1.4, 38, 2.1, 3 + b * 1.4, 29, 3.2, .75, .7), .35);
    }
    return smin(d, cap(x, y, z, 0, 46, -7, 0, 52, -5.5, 5.4, 5), 3);                  // พระศอ
  }
  function head(x, y, z) {
    var h = ell(x, y, z, 0, 58, -4.5, 8.2, 10, 8.8);                                    // พระเศียร
    h = smin(h, ell(x, y, z, 0, 55.5, 3.8, 1.3, 2.6, 1.6), 1.2);                        // พระนาสิก
    if (z > 0 && y > 51 && y < 63) {                                                    // พระพักตร์: คิ้วโก่ง เปลือกตาหลุบต่ำ ริมฝีปาก
      h = smin(h, cap(x, y, z, -5.5, 60.6, 1.9, -.8, 61, 3.9, .6, .6), .6);
      h = smin(h, cap(x, y, z, 5.5, 60.6, 1.9, .8, 61, 3.9, .6, .6), .6);
      h = smin(h, ell(x, y, z, -3, 58.3, 3.4, 2.2, .9, .9), .5);
      h = smin(h, ell(x, y, z, 3, 58.3, 3.4, 2.2, .9, .9), .5);
      h = smin(h, ell(x, y, z, 0, 52.8, 2.9, 2.2, .65, .8), .4);
    }
    h = smin(h, ell(x, y, z, -8.4, 55.5, -4.5, 1.4, 6.2, 2.8), 1.2);                    // พระกรรณยาว
    h = smin(h, ell(x, y, z, 8.4, 55.5, -4.5, 1.4, 6.2, 2.8), 1.2);
    h = smin(h, ell(x, y, z, 0, 66.5, -5, 5.6, 4.2, 5.6), 2);                           // พระเกตุมาลา
    h = smin(h, ell(x, y, z, 0, 69.3, -5, 3.4, 1.1, 3.4), .6);                          // ฐานพระรัศมี
    return smin(h, cap(x, y, z, 0, 69, -5, 0, 80, -5, 2.6, .12), .8);                 // พระรัศมีเปลว ปลายแหลม
  }

  // ── surface nets: ระยะบนตาราง → จุดกลางเซลล์ที่ผิวตัดผ่าน → สี่เหลี่ยมรอบขอบที่ผิวตัด ─────────────────────
  var BOX = [-36, -1.5, -22, 36, 82, 25];
  function build(step) {
    var nx = Math.ceil((BOX[3] - BOX[0]) / step), ny = Math.ceil((BOX[4] - BOX[1]) / step), nz = Math.ceil((BOX[5] - BOX[2]) / step);
    var sx = nx + 1, sy = ny + 1, F = new Float32Array(sx * sy * (nz + 1));
    // รอบแรกหยาบ (ทุก 3 ม.) — จุดละเอียดที่อยู่ห่างผิวชัดเจนใช้ค่าหยาบแทน คำนวณจริงเฉพาะแถบใกล้ผิว (เร็วขึ้นหลายเท่า)
    var G = 3, gx0 = Math.ceil((BOX[3] - BOX[0]) / G), gy0 = Math.ceil((BOX[4] - BOX[1]) / G), gz0 = Math.ceil((BOX[5] - BOX[2]) / G);
    var Q = new Float32Array((gx0 + 1) * (gy0 + 1) * (gz0 + 1));
    for (var k = 0; k <= gz0; k++) for (var j = 0; j <= gy0; j++) for (var i = 0; i <= gx0; i++)
      Q[i + (gx0 + 1) * (j + (gy0 + 1) * k)] = sdf(BOX[0] + i * G, BOX[1] + j * G, BOX[2] + k * G);
    for (k = 0; k <= nz; k++) for (j = 0; j <= ny; j++) for (i = 0; i <= nx; i++) {
      var x = BOX[0] + i * step, y = BOX[1] + j * step, z = BOX[2] + k * step;
      var qv = Q[Math.round((x - BOX[0]) / G) + (gx0 + 1) * (Math.round((y - BOX[1]) / G) + (gy0 + 1) * Math.round((z - BOX[2]) / G))];
      F[i + sx * (j + sy * k)] = y < 0 ? 1 : Math.abs(qv) > 4.5 ? qv : sdf(x, y, z);       // ตัดใต้พื้นลานทิ้ง
    }
    var vid = new Int32Array(nx * ny * nz).fill(-1), pos = [], nor = [], idx = [];
    var C = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0], [0, 0, 1], [1, 0, 1], [0, 1, 1], [1, 1, 1]];
    var E = [[0, 1], [2, 3], [4, 5], [6, 7], [0, 2], [1, 3], [4, 6], [5, 7], [0, 4], [1, 5], [2, 6], [3, 7]];
    var v = new Float32Array(8), e = 1e-3;
    for (k = 0; k < nz; k++) for (j = 0; j < ny; j++) for (i = 0; i < nx; i++) {
      var inside = 0;
      for (var c = 0; c < 8; c++) { v[c] = F[i + C[c][0] + sx * (j + C[c][1] + sy * (k + C[c][2]))]; if (v[c] < 0) inside++; }
      if (inside === 0 || inside === 8) continue;
      var ax = 0, ay = 0, az = 0, n = 0;
      for (var q = 0; q < 12; q++) {
        var a = E[q][0], b = E[q][1];
        if ((v[a] < 0) === (v[b] < 0)) continue;
        var t = v[a] / (v[a] - v[b]);
        ax += C[a][0] + (C[b][0] - C[a][0]) * t; ay += C[a][1] + (C[b][1] - C[a][1]) * t; az += C[a][2] + (C[b][2] - C[a][2]) * t; n++;
      }
      var px = BOX[0] + (i + ax / n) * step, py = BOX[1] + (j + ay / n) * step, pz = BOX[2] + (k + az / n) * step;
      var g1 = sdf(px + e, py - e, pz - e), g2 = sdf(px - e, py - e, pz + e), g3 = sdf(px - e, py + e, pz - e), g4 = sdf(px + e, py + e, pz + e);
      var gx = g1 - g2 - g3 + g4, gy = -g1 - g2 + g3 + g4, gz = -g1 + g2 - g3 + g4;          // ทิศผิวจาก 4 จุดรอบตัว
      var gl = len(gx, gy, gz) || 1;
      vid[i + nx * (j + ny * k)] = pos.length / 3;
      pos.push(px, py, pz); nor.push(gx / gl, gy / gl, gz / gl);
    }
    function V(i, j, k) { return vid[i + nx * (j + ny * k)]; }
    function quad(a, b, c, d, flip) {
      if (a < 0 || b < 0 || c < 0 || d < 0) return;
      if (flip) idx.push(a, c, b, a, d, c); else idx.push(a, b, c, a, c, d);
    }
    for (k = 1; k < nz; k++) for (j = 1; j < ny; j++) for (i = 1; i < nx; i++) {
      var f0 = F[i + sx * (j + sy * k)] < 0;
      if (f0 !== (F[i + 1 + sx * (j + sy * k)] < 0) && i < nx)
        quad(V(i, j - 1, k - 1), V(i, j, k - 1), V(i, j, k), V(i, j - 1, k), f0);
      if (f0 !== (F[i + sx * (j + 1 + sy * k)] < 0) && j < ny)
        quad(V(i - 1, j, k - 1), V(i - 1, j, k), V(i, j, k), V(i, j, k - 1), f0);
      if (f0 !== (F[i + sx * (j + sy * (k + 1))] < 0) && k < nz)
        quad(V(i - 1, j - 1, k), V(i, j - 1, k), V(i, j, k), V(i - 1, j, k), f0);
    }
    return { pos: new Float32Array(pos), nor: new Float32Array(nor), idx: new Uint32Array(idx) };
  }

  // ── ทำงานเป็น worker: รับขนาดตาราง → ส่งผิวกลับ (โอนหน่วยความจำ ไม่คัดลอก) ─────────────────────────────
  if (typeof window === 'undefined') {
    self.onmessage = function (e) {
      var m = build(e.data);
      self.postMessage(m, [m.pos.buffer, m.nor.buffer, m.idx.buffer]);
    };
    return;
  }
  var SRC = (document.currentScript && document.currentScript.src) || '/static/landmark_buddha.js';
  var meshCache = null, meshWait = [], meshBusy = false;
  function getMesh(cb) {
    if (meshCache) return cb(meshCache);
    meshWait.push(cb);
    if (meshBusy) return;
    meshBusy = true;
    function done(m) { meshCache = m; var w = meshWait; meshWait = []; w.forEach(function (f) { f(m); }); }
    try {
      var wk = new Worker(SRC);
      wk.onmessage = function (e) { done(e.data); wk.terminate(); };
      wk.onerror = function () { done(build(.8)); };                    // worker ใช้ไม่ได้ → สร้างบนหน้าเว็บแทน
      wk.postMessage(.5);
    } catch (err) { setTimeout(function () { done(build(.8)); }, 0); }
  }

  var VS = '#version 300 es\n' +
    'in vec3 p;in vec3 n;uniform mat4 M;out vec3 vn;out vec3 vp;' +
    'void main(){vn=n;vp=p;gl_Position=M*vec4(p,1.);}';
  var FS = '#version 300 es\nprecision highp float;' +
    'in vec3 vn;in vec3 vp;uniform float day;out vec4 o;' +
    'void main(){vec3 N=normalize(vn);' +
    // ขมวดพระเกศา: ลายเม็ดเล็กๆ บนพระเศียรเหนือหน้าผาก
    '  if(vp.y>61.6&&vp.y<69.){float c=sin(vp.x*2.2)*sin(vp.y*2.2)*sin(vp.z*2.2);N=normalize(N+vec3(cos(vp.x*2.2),cos(vp.y*2.2),cos(vp.z*2.2))*.15*sign(c));}' +
    '  vec3 V=normalize(vec3(0.,.35,1.));' +
    '  vec3 Ls=normalize(vec3(-.45,.8,.55)),Lf=normalize(vec3(.2,-.25,1.));' +
    '  vec3 gold=vec3(.93,.66,.17);' +
    '  float dS=max(dot(N,Ls),0.),dF=max(dot(N,Lf),0.);' +
    '  float sS=pow(max(dot(N,normalize(Ls+V)),0.),40.),sF=pow(max(dot(N,normalize(Lf+V)),0.),24.);' +
    '  float rim=pow(1.-max(dot(N,V),0.),3.);' +
    '  vec3 cD=gold*(.28+.85*dS)+vec3(1.,.93,.75)*sS*.9+gold*rim*.35;' +                  // กลางวัน: แดดส่อง
    '  vec3 cN=gold*(.10+.95*dF)+vec3(1.,.85,.55)*sF*.8+vec3(1.,.6,.2)*rim*.25;' +       // กลางคืน: ไฟส่องจากด้านล่างหน้าองค์
    '  o=vec4(mix(cN,cD,day),1.);}';

  // layer ของ MapLibre — lat/lon/facing/ฐาน(ม.) ตาม LANDMARKS ใน city_map.js
  window.KD_buddhaLayer = function (lib, at) {
    var map, prog, buf, count = 0, U = {}, mesh = null, asked = false;
    function setup(gl) {
      function sh(type, src) { var s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); return s; }
      prog = gl.createProgram();
      gl.attachShader(prog, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FS));
      gl.linkProgram(prog);
      if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) { prog = null; return; }
      U.M = gl.getUniformLocation(prog, 'M'); U.day = gl.getUniformLocation(prog, 'day');
      U.p = gl.getAttribLocation(prog, 'p'); U.n = gl.getAttribLocation(prog, 'n');
      buf = { p: gl.createBuffer(), n: gl.createBuffer(), i: gl.createBuffer() };
      gl.bindBuffer(gl.ARRAY_BUFFER, buf.p); gl.bufferData(gl.ARRAY_BUFFER, mesh.pos, gl.STATIC_DRAW);
      gl.bindBuffer(gl.ARRAY_BUFFER, buf.n); gl.bufferData(gl.ARRAY_BUFFER, mesh.nor, gl.STATIC_DRAW);
      gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, buf.i); gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, mesh.idx, gl.STATIC_DRAW);
      count = mesh.idx.length;
    }
    return {
      id: 'landmark-buddha', type: 'custom', renderingMode: '3d',
      onAdd: function (m) { map = m; },
      render: function (gl, args) {
        if (!map || map.getZoom() < 13) return;                            // ไกลกว่านี้องค์พระเล็กกว่าจุดเดียว
        if (!mesh) {                                                       // ผิวสร้างครั้งเดียวต่อการเปิดหน้า สลับกลางวัน/คืนใช้ของเดิม
          if (!asked) { asked = true; getMesh(function (m) { mesh = m; map.triggerRepaint(); }); }
          return;
        }
        if (!prog) {
          if (prog === null) return;
          setup(gl);
          if (!prog) return;
        }
        // เมทริกซ์รวมคำนวณด้วยเลขทศนิยมละเอียด (float64) ก่อนส่งให้การ์ดจอ — ไม่งั้นองค์พระสั่นทีละหลายเมตร
        var ground = (map.queryTerrainElevation && map.queryTerrainElevation([at.lon, at.lat])) || 0;
        var mc = lib.MercatorCoordinate.fromLngLat([at.lon, at.lat], ground + at.base);
        var s = mc.meterInMercatorCoordinateUnits(), a = at.facing * Math.PI / 180, ca = Math.cos(a), sa = Math.sin(a);
        // ท้องถิ่น (x ขวา, y ขึ้น, z หน้า) → เมอร์เคเตอร์ (x ตะวันออก, y ใต้, z ขึ้น) หมุนตามทิศที่องค์พระหัน
        var Mdl = [ -ca * s, -sa * s, 0, 0,   0, 0, s, 0,   sa * s, -ca * s, 0, 0,   mc.x, mc.y, mc.z, 1 ];
        var P = (args.defaultProjectionData && args.defaultProjectionData.mainMatrix) || args.modelViewProjectionMatrix, R = new Float32Array(16);
        for (var c = 0; c < 4; c++) for (var r = 0; r < 4; r++) {
          var v = 0;
          for (var k = 0; k < 4; k++) v += P[k * 4 + r] * Mdl[c * 4 + k];
          R[c * 4 + r] = v;
        }
        gl.useProgram(prog);
        gl.uniformMatrix4fv(U.M, false, R);
        gl.uniform1f(U.day, document.documentElement.classList.contains('kd-day') ? 1 : 0);
        gl.bindBuffer(gl.ARRAY_BUFFER, buf.p); gl.enableVertexAttribArray(U.p); gl.vertexAttribPointer(U.p, 3, gl.FLOAT, false, 0, 0);
        gl.bindBuffer(gl.ARRAY_BUFFER, buf.n); gl.enableVertexAttribArray(U.n); gl.vertexAttribPointer(U.n, 3, gl.FLOAT, false, 0, 0);
        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, buf.i);
        gl.enable(gl.DEPTH_TEST); gl.depthFunc(gl.LEQUAL); gl.depthMask(true);
        gl.disable(gl.BLEND);
        gl.drawElements(gl.TRIANGLES, count, gl.UNSIGNED_INT, 0);
        gl.disableVertexAttribArray(U.p); gl.disableVertexAttribArray(U.n);
      }
    };
  };
  window.KD_buddhaBuild = build;                                           // ให้เทสต์เรียกสร้างผิวได้โดยไม่ต้องมีจอ
})();
