// service-worker.js
const CACHE_NAME = "hospital-cache-v1";

// Archivos que queremos guardar en caché
const urlsToCache = [
  "/"
];

// Instalar el service worker
self.addEventListener("install", event => {
  console.log("[SW] Instalando service worker...");
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log("[SW] Cacheando archivos...");
      return cache.addAll(urlsToCache);
    })
  );
});

// Activar el service worker
self.addEventListener("activate", event => {
  console.log("[SW] Activado");
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(name => {
          if (name !== CACHE_NAME) {
            console.log("[SW] Eliminando caché viejo:", name);
            return caches.delete(name);
          }
        })
      );
    })
  );
});

// Interceptar solicitudes
self.addEventListener("fetch", event => {
  event.respondWith(
    fetch(event.request).catch(() => {
      console.log("[SW] Modo offline para", event.request.url);
      return caches.match(event.request);
    })
  );
});
