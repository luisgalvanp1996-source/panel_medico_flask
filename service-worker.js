// service-worker.js
const CACHE_NAME = "hospital-cache-v2";
const urlsToCache = [
  "/",
  "/rondas",
  "/static/css/style.css",
  "/static/js/app.js",
  "/static/js/idb-wrapper.js",
  "/static/js/offline-sync.js",
  "/static/logo.png",
  "/static/manifest.json"
];

self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache)));
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.map(k => { if (k!==CACHE_NAME) return caches.delete(k); })))
  );
});

self.addEventListener("fetch", event => {
  if (event.request.mode === 'navigate') {
    event.respondWith(fetch(event.request).catch(()=>caches.match('/')));
    return;
  }
  event.respondWith(caches.match(event.request).then(resp => resp || fetch(event.request).catch(()=>caches.match('/'))));
});
