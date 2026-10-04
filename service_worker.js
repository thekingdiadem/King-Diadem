// service_worker.js (root) — ไม่มี route ใน app.py เสิร์ฟไฟล์นี้ และไม่มีหน้าไหน register
// เดิม: cache-first ทุก request รวม POST (/run) และ API ที่ผูกกับบัญชี (/me, /wallet/balance)
//   → cache.put(POST) ล้ม แล้ว fallback คืน index.html แทนคำตอบ; ข้อมูลบัญชีค้างในแคชเครื่อง
// ตอนนี้: GET + /static/ เท่านั้น, network-first, แคชเป็น fallback ตอนออฟไลน์
const CACHE = "king-diadem-v4"
const STATIC_ASSETS = [
  "/static/logo.png",
  "/static/manifest.json"
]

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(cache => cache.addAll(STATIC_ASSETS)))
  self.skipWaiting()
})

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
  )
  self.clients.claim()
})

self.addEventListener("fetch", e => {
  const req = e.request
  const url = new URL(req.url)
  if (req.method !== "GET" || url.origin !== location.origin) return
  if (!url.pathname.startsWith("/static/") || url.search) return
  e.respondWith(
    fetch(req).then(net => {
      if (net && net.status === 200) {
        const copy = net.clone()
        caches.open(CACHE).then(cache => cache.put(req, copy))
      }
      return net
    }).catch(() => caches.match(req))
  )
})
