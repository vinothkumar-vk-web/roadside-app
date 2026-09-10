// Service Worker for Standalone App - Live Sync Mode
const CACHE_NAME = 'roadside-app-v2';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(keys.map((k) => caches.delete(k)));
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  // Always fetch fresh from server to reflect latest updates immediately
  event.respondWith(
    fetch(event.request, { cache: 'no-store' })
      .catch(() => caches.match(event.request))
  );
});
