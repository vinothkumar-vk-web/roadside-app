// Standalone Service Worker - Zero Cache Lag, Live Network Always
const CACHE_NAME = 'roadside-app-v5-live';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  // Purge ALL caches from all previous versions!
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((k) => caches.delete(k))
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  // HTML navigation & API calls: ALWAYS bypass cache and fetch live from server
  if (event.request.mode === 'navigate' || event.request.url.includes('/api/') || event.request.url.includes('/ws/')) {
    event.respondWith(
      fetch(event.request, { cache: 'no-store' }).catch(() => {
        return new Response('Network offline. Please check your internet.', {
          headers: { 'Content-Type': 'text/plain' }
        });
      })
    );
    return;
  }

  // All other assets: Network first
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
