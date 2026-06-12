// Service Worker — Mini-Serra Living Soil PWA
const CACHE = 'serra-v56';
const ASSETS = ['./manuale_mini_serra_completo.html'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS))); self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))); self.clients.claim(); });
self.addEventListener('fetch', e => { e.respondWith(caches.match(e.request).then(cached => cached || fetch(e.request)).catch(() => caches.match('./manuale_mini_serra_completo.html'))); });
