/* Service worker minimo: tiene in cache solo l'app (pagina e icone).
   I dati di meteo, mare, meduse e luoghi NON vengono mai messi in cache:
   passano sempre dalla rete, così non vedi mai previsioni vecchie. */
const CACHE = 'viaggio-v2';
const SHELL = ['./', './index.html', './icon-192.png', './icon-512.png', './manifest.webmanifest', './regions/italia.json', './regions/svizzera.json'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;           // API e mappe: sempre dalla rete
  e.respondWith(
    fetch(req).then(res => {                                  // prima la rete, così l'app è sempre aggiornata
      const copy = res.clone();
      caches.open(CACHE).then(c => c.put(req, copy)).catch(() => {});
      return res;
    }).catch(() => caches.match(req).then(r => r || caches.match('./index.html')))  // offline: versione salvata
  );
});
