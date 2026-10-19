const CACHE='sap-material-shell-v1';
const SHELL=['/','/manifest.webmanifest','/image_d6ce3f.png'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL))));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k))))));
self.addEventListener('fetch',e=>{if(e.request.method!=='GET'||new URL(e.request.url).pathname==='/search')return;e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)));});
