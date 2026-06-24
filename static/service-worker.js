/* ================================================================
   KING DIADEM — Service Worker v3.0
   Strategy: Network-first (ไม่ block updates)
   Static assets: stale-while-revalidate
   ================================================================ */
'use strict';

var CACHE = 'kd-v3';
/* เฉพาะ static ที่ไม่ค่อยเปลี่ยน */
var PRECACHE = [
  '/static/logo.png',
  '/static/manifest.json'
];

/* ── INSTALL: cache เฉพาะ essentials ── */
self.addEventListener('install', function(e){
  e.waitUntil(
    caches.open(CACHE).then(function(c){
      return c.addAll(PRECACHE);
    }).then(function(){
      return self.skipWaiting(); /* activate immediately */
    })
  );
});

/* ── ACTIVATE: ลบ cache เก่าทั้งหมด ── */
self.addEventListener('activate', function(e){
  e.waitUntil(
    caches.keys().then(function(keys){
      return Promise.all(
        keys.filter(function(k){ return k !== CACHE; })
            .map(function(k){ return caches.delete(k); })
      );
    }).then(function(){
      return self.clients.claim();
    })
  );
});

/* ── FETCH: Network-first strategy ── */
self.addEventListener('fetch', function(e){
  var req = e.request;
  var url = new URL(req.url);

  /* Skip non-GET, cross-origin, API calls */
  if(req.method !== 'GET') return;
  if(url.origin !== location.origin) return;
  if(url.pathname.startsWith('/run') ||
     url.pathname.startsWith('/api') ||
     url.pathname.startsWith('/me') ||
     url.pathname.startsWith('/health') ||
     url.pathname.startsWith('/simulate') ||
     url.pathname.startsWith('/login') ||
     url.pathname.startsWith('/logout') ||
     url.pathname.startsWith('/analyze-image') ||
     url.pathname.startsWith('/payment') ||
     url.pathname.startsWith('/create-') ||
     url.pathname.startsWith('/report')) return;

  /* Static JS/CSS/fonts: stale-while-revalidate
     ให้โหลดเร็ว แต่ update background */
  if(url.pathname.match(/\.(js|css|woff2?|ttf)$/)){
    e.respondWith(staleWhileRevalidate(req));
    return;
  }

  /* HTML + images: network-first, cache fallback */
  e.respondWith(networkFirst(req));
});

function networkFirst(req){
  return fetch(req).then(function(res){
    if(res && res.status === 200){
      var clone = res.clone();
      caches.open(CACHE).then(function(c){ c.put(req, clone); });
    }
    return res;
  }).catch(function(){
    return caches.match(req);
  });
}

function staleWhileRevalidate(req){
  return caches.open(CACHE).then(function(cache){
    return cache.match(req).then(function(cached){
      var fetchPromise = fetch(req).then(function(res){
        if(res && res.status === 200){
          cache.put(req, res.clone());
        }
        return res;
      }).catch(function(){ return cached; });
      return cached || fetchPromise;
    });
  });
}

/* ── Message: force update ── */
self.addEventListener('message', function(e){
  if(e.data && e.data.type === 'SKIP_WAITING'){
    self.skipWaiting();
  }
});
