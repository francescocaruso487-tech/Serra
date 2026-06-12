const CACHE='serra-v64';
const HTML='./manuale_mini_serra_completo.html';
// Network-first per HTML (sempre versione aggiornata), cache-first per il resto
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll([HTML])));self.skipWaiting();});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==CACHE).map(x=>caches.delete(x)))));self.clients.claim();});
self.addEventListener('fetch',e=>{
  var url=new URL(e.request.url);
  var isHTML=url.pathname.endsWith('.html')||url.pathname.endsWith('/')||url.pathname==='/Serra'||url.pathname==='/Serra/';
  if(isHTML){
    e.respondWith(fetch(e.request).then(function(r){var cl=r.clone();caches.open(CACHE).then(function(c){c.put(e.request,cl);});return r;}).catch(function(){return caches.match(e.request);}));
  } else {
    e.respondWith(caches.match(e.request).then(function(c){return c||fetch(e.request);}).catch(function(){return caches.match(HTML);}));
  }
});
