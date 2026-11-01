/* ================================================================
   KING DIADEM — Service Worker v4
   เสิร์ฟที่ /service-worker.js (app.py ใส่ Service-Worker-Allowed: /) → ดูแลทั้งแอป ไม่ใช่แค่ /static/
   ลงทะเบียนจาก static/index.html

   หลัก: เครือข่ายมาก่อนเสมอ (network-first) — ทุกครั้งที่ออนไลน์ได้ไฟล์ใหม่ล่าสุด ไม่ค้างของเก่าหลัง deploy
         แคชใช้เฉพาะตอนออฟไลน์: เปิดแอปได้ แชทที่เคยคุยยังอยู่ในเครื่อง (ข้อมูลแชทอยู่ใน localStorage)
   แคชเฉพาะ: หน้าแรก "/" + ไฟล์ใน /static/ ที่ไม่มี query
   ไม่แคชเด็ดขาด: API / บัญชี / เครดิต / รายงาน / ทุกอย่างที่ไม่ใช่ GET — ข้อมูลส่วนตัวไม่ค้างในเครื่องที่ใช้ร่วมกัน
   ================================================================ */
'use strict';

var CACHE = 'kd-v7';   // v7: โลโก้ใหม่ (ดาวในวงแหวน) — เครื่องที่ติดตั้งแอปไว้จะได้ไอคอนใหม่
//   // v6: หน้าแรกแยกเป็น index.html + app.css + app.js   // v5: โลโก้มงกุฎใหม่ — เครื่องที่ติดตั้งแอปไว้จะได้ไอคอนใหม่
var OFFLINE = '/static/offline.html';
var PRECACHE = ['/', OFFLINE, '/static/manifest.json', '/static/icons/icon-192.png', '/static/icons/favicon-48.png', '/static/i18n.js', '/static/app.css', '/static/app.js'];

self.addEventListener('install', function (e) {
  e.waitUntil(
    caches.open(CACHE)
      .then(function (c) { return Promise.all(PRECACHE.map(function (u) { return c.add(u).catch(function () {}); })); })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys()
      .then(function (keys) { return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); })); })
      .then(function () { return self.clients.claim(); })
  );
});

function cacheable(url) {
  if (url.origin !== self.location.origin || url.search) return false;
  return url.pathname === '/' || url.pathname.indexOf('/static/') === 0;
}

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;
  var url = new URL(req.url);
  var nav = req.mode === 'navigate';
  if (!nav && !cacheable(url)) return;            // API/บัญชี/ข้ามโดเมน → ให้เบราว์เซอร์จัดการเอง ไม่แตะ

  e.respondWith(
    fetch(req).then(function (res) {
      if (res && res.status === 200 && res.type === 'basic' && cacheable(url)) {
        var copy = res.clone();
        caches.open(CACHE).then(function (c) { c.put(req, copy); });
      }
      return res;
    }).catch(function () {
      return caches.match(req).then(function (hit) {
        if (hit) return hit;
        if (nav) return caches.match(url.pathname === '/' ? '/' : OFFLINE).then(function (r) { return r || caches.match(OFFLINE); });
        return Response.error();
      });
    })
  );
});
