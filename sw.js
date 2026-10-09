/* Service worker: fa aprire l'app subito anche con rete lenta.
   - pagina dell'app: dalla rete se risponde in fretta, altrimenti la copia salvata;
   - altri file dell'app (comuni, icone): copia salvata subito, aggiornata in background;
   - librerie (cdnjs, jsDelivr, font): salvate una volta, hanno la versione nell'indirizzo;
   - mappa (tile e stile): copia salvata subito, aggiornata in background; al massimo ~4000 tile, poi si tolgono le più vecchie;
   - mappe salvate dall'utente (cache OFFLINE): tessere, simboli e caratteri si leggono da lì per primi; lo stile e l'elenco delle tessere (che cambiano) dalla rete, e da lì solo se sei offline;
   - custom-points.json: sempre dalla rete (i punti di Claude devono essere aggiornati), copia salvata solo se sei offline.
   Previsioni, monumenti e testi li salva l'app stessa (IndexedDB) con le loro scadenze. */
const V = 'v109';
const SHELL = 'viaggio-shell-'+V, LIBS = 'viaggio-libs', TILES = 'viaggio-tiles', OFFLINE = 'viaggio-offline';   /* OFFLINE: mappe salvate dall'utente ("Salva visuale offline"), mai tolte da sole */
const FILES = ['./', './index.html', './icon-192.png', './icon-512.png', './manifest.webmanifest', './region-italia.json', './region-svizzera.json'];
const LIB_HOSTS = ['cdnjs.cloudflare.com', 'cdn.jsdelivr.net', 'fonts.googleapis.com', 'fonts.gstatic.com'];
const TILE_HOSTS = ['tiles.openfreemap.org', 'tile.openstreetmap.org', 'server.arcgisonline.com'];
const MAX_TILES = 4000;

self.addEventListener('install', e => {
  e.waitUntil(caches.open(SHELL).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('viaggio-') && ![SHELL, LIBS, TILES, OFFLINE].includes(k)).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

async function staleWhileRevalidate(cacheName, req, e){
  const c = await caches.open(cacheName), hit = await c.match(req, { ignoreVary: true });
  /* solo risposte leggibili: quelle "opache" occupano moltissimo spazio nella memoria del telefono */
  const net = fetch(req).then(res => { if (res && res.ok) c.put(req, res.clone()); return res; }).catch(() => null);
  if (hit){ e.waitUntil(net); return hit; }
  return (await net) || new Response('', { status: 504 });
}
/* la pagina dell'app: dalla rete se risponde entro 2,5 secondi (così vedi subito le novità), altrimenti la copia salvata */
async function pageFirst(req, e){
  const c = await caches.open(SHELL);
  const net = fetch(req).then(res => { if (res.ok) c.put(req, res.clone()); return res; });
  e.waitUntil(net.catch(() => {}));
  try { return await Promise.race([net, new Promise((_, ko) => setTimeout(() => ko(0), 2500))]); }
  catch(x){ return (await c.match(req)) || (await c.match('./index.html')) || net; }
}
async function cacheFirst(cacheName, req){
  const c = await caches.open(cacheName), hit = await c.match(req);
  if (hit) return hit;
  const res = await fetch(req); if (res && (res.ok || res.type === 'opaque')) c.put(req, res.clone()); return res;
}
async function networkFirst(cacheName, req){
  const c = await caches.open(cacheName);
  try { const res = await fetch(req); if (res.ok) c.put(req, res.clone()); return res; }
  catch(e){ return (await c.match(req, { ignoreSearch: true })) || new Response('[]', { headers: { 'Content-Type': 'application/json' } }); }
}
/* mappa vettoriale: tessere, caratteri e simboli hanno la versione nell'indirizzo, quindi se sono nelle mappe salvate si usano subito;
   lo stile e l'elenco delle tessere (/styles/..., /planet) cambiano: prima la rete (3,5 secondi), se manca o è lenta la copia salvata */
const isMutableTile = url => url.hostname === 'tiles.openfreemap.org' && (url.pathname === '/planet' || url.pathname.startsWith('/styles/'));
async function tileFetch(req, url, e){
  const off = await caches.open(OFFLINE), saved = await off.match(req, { ignoreVary: true });
  if (!isMutableTile(url)){
    if (saved) return saved;
    return staleWhileRevalidate(TILES, req, e);
  }
  const t = await caches.open(TILES);
  try {
    const res = await Promise.race([fetch(req), new Promise((_, ko) => setTimeout(() => ko(0), 3500))]);
    if (res && res.ok){ t.put(req, res.clone()); return res; }
  } catch(x){}
  return saved || (await t.match(req, { ignoreVary: true })) || new Response('', { status: 504 });
}
let trimming = false;
async function trimTiles(){
  if (trimming) return; trimming = true;
  try { const c = await caches.open(TILES), ks = await c.keys(); if (ks.length > MAX_TILES) for (const k of ks.slice(0, ks.length - MAX_TILES)) await c.delete(k); }
  finally { trimming = false; }
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin === self.location.origin){
    if (url.pathname.endsWith('/sw.js')) return;      /* controllo versione dell'app: sempre dalla rete, mai dalla cache */
    if ((url.pathname.endsWith('custom-points.json') || url.pathname.endsWith('custom-inbox.json') || url.pathname.endsWith('dati/index.json') || url.pathname.endsWith('tools/dati_zone.json'))) { e.respondWith(networkFirst(SHELL, req)); return; }
    if (url.pathname.startsWith('/api/')) return;
    if (req.mode === 'navigate' || url.pathname.endsWith('/') || url.pathname.endsWith('index.html')) { e.respondWith(pageFirst(req, e)); return; }
    e.respondWith(staleWhileRevalidate(SHELL, req, e)); return;
  }
  if (LIB_HOSTS.includes(url.hostname)){ e.respondWith(cacheFirst(LIBS, req)); return; }
  if (TILE_HOSTS.includes(url.hostname)){ e.respondWith(tileFetch(req, url, e)); if (Math.random() < 0.02) e.waitUntil(trimTiles()); return; }
});
