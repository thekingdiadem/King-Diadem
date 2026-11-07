/* วงโคจรของ "โหมดยานอวกาศ" (หน้า /universe) — คณิตศาสตร์ล้วน ไม่แตะหน้าเว็บ ทดสอบได้ใน tests/test_ship_mode.py
 *
 * ค่าอ้างอิงจากสถานีอวกาศนานาชาติ (ISS): สูงราว 408 กม. · เอียง 51.64° จากเส้นศูนย์สูตร · รอบละราว 92.9 นาที
 * ความเร็วราว 7.66 กม./วินาที · วนรอบโลกราว 15.5 รอบต่อวัน (เห็นพระอาทิตย์ขึ้นราว 16 ครั้ง)
 * วงกลม (ไม่คิดความรีของวงโคจร) — พอสำหรับภาพจากหน้าต่าง ไม่ใช่การนำทางจริง
 */
(function (root) {
  var RAD = Math.PI / 180;
  var O = {
    ALT_KM: 408,
    INC_DEG: 51.64,
    PERIOD_S: 92.9 * 60,
    SPEED_KMS: 7.66,
    EARTH_R_KM: 6371,
    SIDEREAL_DAY_S: 86164,
  };
  O.H = O.ALT_KM / O.EARTH_R_KM;                     // ความสูงยาน (หน่วยรัศมีโลก)
  O.HORIZON = Math.asin(1 / (1 + O.H));              // มุมจากแนวดิ่งใต้ยานถึงขอบฟ้า (408 กม. ≈ 70°)

  /* มุมกล้องในหน้าต่าง — กล้องของโลก (cockpit_earth.js) มองจุดบนพื้นจากระยะ D ด้วยมุมเอียง tilt จากแนวดิ่ง ณ จุดนั้น
   * หา D/tilt ที่ทำให้กล้องสูงเหนือพื้น ALT_KM จริง และขอบฟ้าอยู่สูงกว่ากลางจอ aboveDeg องศา
   * (สามเหลี่ยม ศูนย์กลางโลก–กล้อง–จุดที่มอง · กฎของไซน์) · ahead = จุดที่มองอยู่ทางเหนือของจุดใต้ยานกี่องศา */
  O.view = function (aboveDeg) {
    var eta = O.HORIZON - aboveDeg * RAD;                          // มุมจากแนวดิ่งใต้ยานถึงเส้นกลางจอ
    var tilt = Math.asin((1 + O.H) * Math.sin(eta));
    var ahead = tilt - eta;                                        // มุมที่ศูนย์กลางโลก ระหว่างจุดใต้ยานกับจุดที่มอง
    return { D: Math.sin(ahead) / Math.sin(eta), tilt: tilt, ahead: ahead / RAD };
  };
  O.VIEW = O.view(5);                                              // จอแนวนอน: ขอบฟ้าโค้งเหนือกลางจอราว 12% — โลกเต็มครึ่งล่างของหน้าต่าง
  O.VIEW_TALL = O.view(10);                                        // จอแนวตั้ง (มือถือ): หน้าต่างอยู่ค่อนบน ขอบฟ้าจึงต้องสูงขึ้นอีกหน่อย

  /* ตำแหน่งใต้ยาน (องศา) จากมุมในวงโคจร u (เรเดียน) และลองจิจูดของจุดตัดเส้นศูนย์สูตร node (องศา) */
  O.ground = function (u, node) {
    var i = O.INC_DEG * RAD;
    var lat = Math.asin(Math.sin(i) * Math.sin(u)) / RAD;
    var lon = node + Math.atan2(Math.cos(i) * Math.sin(u), Math.cos(u)) / RAD;
    lon = ((lon % 360) + 540) % 360 - 180;
    return { lat: lat, lon: lon };
  };

  /* เดินหน้า dt วินาที × ความเร่ง k (1 = เวลาจริง) — โลกหมุนใต้ยาน จุดตัดจึงเลื่อนไปทางตะวันตก */
  O.step = function (st, dt, k) {
    var s = dt * (k || 1);
    var u = st.u + 2 * Math.PI * s / O.PERIOD_S;
    var node = st.node - 360 * s / O.SIDEREAL_DAY_S;
    return { u: u % (2 * Math.PI), node: ((node % 360) + 360) % 360 };
  };

  /* จุดที่ดวงอาทิตย์อยู่ตรงศีรษะ (subsolar point) ณ เวลา ms (มิลลิวินาที UTC) — สูตรย่อแบบปฏิทินดาราศาสตร์ (คลาดราว 0.1°)
   * ใช้แบ่งกลางวัน/กลางคืนบนโลกในหน้าต่างยาน — ยานจึงผ่านพระอาทิตย์ขึ้นจริงราวทุก 93 นาที */
  O.sun = function (ms) {
    var d = ms / 86400000 - 10957.5;                               // วันนับจาก J2000.0 (1 ม.ค. 2000 12:00 UTC)
    var g = (357.529 + .98560028 * d) * RAD, q = 280.459 + .98564736 * d;
    var L = (q + 1.915 * Math.sin(g) + .020 * Math.sin(2 * g)) * RAD, e = (23.439 - .00000036 * d) * RAD;
    var ra = Math.atan2(Math.cos(e) * Math.sin(L), Math.cos(L)) / RAD;
    var dec = Math.asin(Math.sin(e) * Math.sin(L)) / RAD;
    var gmst = 280.46061837 + 360.98564736629 * d;                 // มุมเวลาดาวฤกษ์ที่กรีนิช (องศา)
    return { lat: dec, lon: ((ra - gmst) % 360 + 540) % 360 - 180 };
  };

  /* พิกัดองศา → เวกเตอร์หนึ่งหน่วยแบบเดียวกับ shader ของโลก (y = ขั้วเหนือ · z = ลองจิจูด 0°) */
  O.vec = function (lat, lon) {
    var a = lat * RAD, b = lon * RAD;
    return [Math.cos(a) * Math.sin(b), Math.sin(a), Math.cos(a) * Math.cos(b)];
  };

  root.KD_orbit = O;
})(typeof window !== 'undefined' ? window : this);
