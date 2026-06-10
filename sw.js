// Service Worker — Mini-Serra Living Soil PWA
const CACHE = 'serra-v32';
const ASSETS = ['./manuale_mini_serra_completo.html'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ));
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  e.respondWith(
    fetch(e.request).catch(() => caches.match(e.request))
  );
});

// Notifiche push pianificate via postMessage
self.addEventListener('message', e => {
  if (e.data && e.data.type === 'SCHEDULE_NOTIF') {
    const { title, body, delay } = e.data;
    setTimeout(() => {
      self.registration.showNotification(title, {
        body,
        icon: './icon-192.png',
        badge: './icon-192.png',
        vibrate: [200, 100, 200],
        tag: 'serra-reminder',
        renotify: true
      });
    }, delay);
  }
});
