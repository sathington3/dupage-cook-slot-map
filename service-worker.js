const CACHE='slot-map-v13.3.3';
const SHELL=[
  './index.html','./manifest.webmanifest?v=13.3.3','./establishments.js?v=13.3.3',
  './buffalo-theme.png','./apple-touch-icon.png','./app-icon-512.png'
];
// Fixed-version library assets only. Map tiles remain uncached to avoid an unbounded cache.
const CDN_SHELL=[
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
  'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  'https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css',
  'https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css',
  'https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js'
];
const CDN_URLS=new Set(CDN_SHELL);

self.addEventListener('install', event => {
  event.waitUntil((async()=>{
    const cache=await caches.open(CACHE);
    await cache.addAll(SHELL);
    // Best effort: a temporary CDN problem must not block installation.
    await Promise.allSettled(CDN_SHELL.map(async url=>{
      const res=await fetch(url,{mode:'cors'});
      if(res.ok)await cache.put(url,res);
    }));
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const req=event.request;
  if(req.method!=='GET') return;
  const url=new URL(req.url);

  // Cache only the fixed CDN libraries required to boot the UI offline.
  if(url.origin!==self.location.origin){
    if(!CDN_URLS.has(url.href)) return;
    event.respondWith(caches.match(url.href).then(cached=>cached||fetch(req).then(res=>{
      if(res.ok)caches.open(CACHE).then(cache=>cache.put(url.href,res.clone()));
      return res;
    })));
    return;
  }

  // Network-first for pages so GitHub updates appear promptly; cached fallback offline.
  if(req.mode==='navigate'){
    event.respondWith(
      fetch(req).then(res=>{
        if(res.ok){const copy=res.clone();caches.open(CACHE).then(cache=>cache.put('./index.html',copy));}
        return res;
      }).catch(()=>caches.match('./index.html'))
    );
    return;
  }

  // Versioned/static assets are cache-first inside a versioned cache.
  event.respondWith(
    caches.match(req).then(cached => cached || fetch(req).then(res=>{
      if(res.ok){const copy=res.clone();caches.open(CACHE).then(cache=>cache.put(req,copy));}
      return res;
    }))
  );
});
