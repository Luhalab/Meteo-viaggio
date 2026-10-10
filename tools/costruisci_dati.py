#!/usr/bin/env python3
"""Costruisce i dati di OpenStreetMap a pezzetti per l'app: monumenti (historic), opere d'arte pubbliche e luoghi di culto.

Per ogni regione di tools/dati_zone.json: scarica l'archivio da Geofabrik (con tentativi), tiene con osmium solo gli oggetti utili,
li divide in pezzi di 0,1 gradi e li scrive in dati/osm/<regione>/<riga>_<colonna>.json; poi aggiorna dati/index.json.
Ogni voce è [lat, lon, tipo, nome, descrizione, id] (+ un settimo campo, "it:Titolo" o "Q123", se ha un collegamento a Wikipedia/Wikidata; + un ottavo, il numero di edizioni di Wikipedia che ne parlano, se è maggiore di zero): tipo = valore di "historic", "@a" (opera d'arte) o "@w" (luogo di culto);
id = n123 / w456 / r789 (nodo, via, relazione di OpenStreetMap).

Uso:  python3 tools/costruisci_dati.py                   tutte le regioni accese (e toglie quelle spente)
      python3 tools/costruisci_dati.py --solo liguria    una sola regione (anche se spenta)
      python3 tools/costruisci_dati.py --imposta toscana accendi    accende o spegne una regione nel catalogo
      python3 tools/costruisci_dati.py --togli toscana   toglie i dati di una regione
      python3 tools/costruisci_dati.py --solo liguria --prova file.osm.pbf     prova locale, senza scaricare
Serve osmium-tool (sudo apt-get install osmium-tool). Dati © OpenStreetMap contributors (ODbL)."""
import argparse, datetime, json, math, os, re, shutil, subprocess, sys, tempfile, time, urllib.parse, urllib.request

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(RADICE, 'tools', 'dati_zone.json'), encoding='utf-8'))
PEZZO = CFG.get('pezzo', 0.1); K = round(1 / PEZZO)          # pezzi per grado
OUT = os.environ.get('DATI_OUT') or os.path.join(RADICE, 'dati')

# ---------- notorietà: quante edizioni di Wikipedia parlano di quell'opera (Wikidata) ----------
UA = 'MeteoViaggio-dati/1.0 (https://github.com/Luhalab/Meteo-viaggio)'
SPECIALI = {'commonswiki', 'wikidatawiki', 'specieswiki', 'metawiki', 'mediawikiwiki', 'incubatorwiki', 'outreachwiki'}      # collegamenti che non sono edizioni di Wikipedia
CACHE_WD = os.path.join(RADICE, 'tools', 'wikidata_cache.json')
VALIDITA_GIORNI = 120

def http_json(url, tentativi=5):
    for t in range(tentativi):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'}), timeout=60) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception as e:
            time.sleep(2 * (t + 1))
    return None

def qid_da_titoli(coppie):
    """[(lingua, titolo)] -> {(lingua, titolo): 'Q123'} con l'API di Wikipedia (50 titoli per richiesta; rinvii e maiuscole gestiti)"""
    out, per_lingua = {}, {}
    for lingua, titolo in coppie: per_lingua.setdefault(lingua, []).append(titolo)
    for lingua, titoli in per_lingua.items():
        for i in range(0, len(titoli), 50):
            blocco = titoli[i:i + 50]
            j = http_json('https://%s.wikipedia.org/w/api.php?action=query&prop=pageprops&ppprop=wikibase_item&redirects=1&format=json&titles=%s' % (lingua, urllib.parse.quote('|'.join(blocco))))
            if not j: continue
            q = j.get('query', {}); norm = {n['from']: n['to'] for n in q.get('normalized', [])}; red = {r['from']: r['to'] for r in q.get('redirects', [])}
            pagine = {p.get('title'): p for p in (q.get('pages') or {}).values()}
            for t in blocco:
                t2 = norm.get(t, t); t2 = red.get(t2, t2); p = pagine.get(t2)
                qid = p and (p.get('pageprops') or {}).get('wikibase_item')
                if qid: out[(lingua, t)] = qid
            time.sleep(0.3)
    return out

def conta_collegamenti(qids, cache):
    """aggiorna cache {'Q123': [numero di edizioni di Wikipedia, 'AAAA-MM-GG']} per i Q-id mancanti o vecchi (50 per richiesta)"""
    oggi = datetime.date.today(); scaduti = lambda v: (oggi - datetime.date.fromisoformat(v[1])).days > VALIDITA_GIORNI
    da_fare = [q for q in sorted(set(qids)) if q not in cache or len(cache[q]) < 4 or scaduti(cache[q])]
    print('  notorietà: %d opere con Wikidata, %d da interrogare' % (len(set(qids)), len(da_fare)), flush=True)
    for i in range(0, len(da_fare), 50):
        blocco = da_fare[i:i + 50]
        j = http_json('https://www.wikidata.org/w/api.php?action=wbgetentities&props=sitelinks&format=json&maxlag=5&ids=' + '|'.join(blocco))
        if not j or 'entities' not in j: continue
        for q, e in j['entities'].items():
            sl = e.get('sitelinks') or {}
            wp = [k for k in sl if re.match(r'^[a-z_]+wiki$', k) and k not in SPECIALI]
            scelta = next((k for k in ('itwiki', 'enwiki') if k in sl), wp[0] if wp else None)        # pagina da cui controllare le coordinate
            cache[q] = [len(wp), oggi.isoformat(), scelta[:-4].replace('_', '-') if scelta else '', sl[scelta]['title'] if scelta else '']
        time.sleep(0.3)

def verifica_luoghi(qids, cache):
    """per le opere con almeno 2 edizioni controlla che la pagina di Wikipedia abbia le coordinate (quinto campo: 1 sì, 0 no): un collegamento a una persona o a un modello di aereo non è un luogo"""
    per_lingua = {}
    for q in sorted(set(qids)):
        v = cache.get(q)
        if v and v[0] >= 2 and len(v) == 4 and v[2] and v[3]: per_lingua.setdefault(v[2], []).append((q, v[3]))
    print('  luoghi da verificare: %d' % sum(len(x) for x in per_lingua.values()), flush=True)
    for lingua, lista in per_lingua.items():
        for i in range(0, len(lista), 50):
            blocco = lista[i:i + 50]
            j = http_json('https://%s.wikipedia.org/w/api.php?action=query&prop=coordinates&coprimary=primary&colimit=max&redirects=1&format=json&titles=%s' % (lingua, urllib.parse.quote('|'.join(t for _, t in blocco))))
            if not j: continue
            q_ = j.get('query', {}); norm = {n['from']: n['to'] for n in q_.get('normalized', [])}; red = {r['from']: r['to'] for r in q_.get('redirects', [])}
            pagine = {p.get('title'): p for p in (q_.get('pages') or {}).values()}
            for q, t in blocco:
                t2 = norm.get(t, t); t2 = red.get(t2, t2); p = pagine.get(t2)
                if p is not None: cache[q] = cache[q][:4] + [1 if p.get('coordinates') else 0]
            time.sleep(0.3)

def arricchisci(items):
    """aggiunge a ogni voce con Wikipedia/Wikidata il numero di edizioni di Wikipedia (ottavo campo); restituisce la copertura 0-1"""
    try: cache = json.load(open(CACHE_WD, encoding='utf-8'))
    except Exception: cache = {}
    coppie = {tuple(v[6].split(':', 1)) for v in items if len(v) > 6 and not re.match(r'^Q\d+$', v[6]) and ':' in v[6]}
    risolti = qid_da_titoli(coppie) if coppie else {}
    def qid(v):
        if len(v) < 7: return None
        return v[6] if re.match(r'^Q\d+$', v[6]) else risolti.get(tuple(v[6].split(':', 1))) if ':' in v[6] else None
    qs = {qid(v) for v in items if qid(v)}
    conta_collegamenti(qs, cache)
    verifica_luoghi(qs, cache)
    ok = con_q = 0
    for v in items:
        q = qid(v)
        if not q: continue
        con_q += 1
        if q in cache:
            ok += 1
            c = cache[q]
            if c[0] > 0 and not (len(c) > 4 and c[4] == 0 and c[0] >= 2): v.append(c[0])        # senza coordinate sulla pagina non è un luogo: niente notorietà
    open(CACHE_WD, 'w', encoding='utf-8').write(json.dumps(cache, separators=(',', ':'), sort_keys=True))
    return (ok / con_q) if con_q else 1.0           # quota delle opere con Wikidata di cui si è saputo il numero: sotto il 90% l'app non si fida

def run(cmd):
    print('+', ' '.join(cmd), flush=True); subprocess.run(cmd, check=True)

def scarica(url, dest):
    # curl con tanti tentativi e pause lunghe: a questa ora il server può essere occupato
    run(['curl', '-L', '--fail', '--silent', '--show-error', '--retry', '8', '--retry-delay', '60', '--retry-all-errors', '-o', dest, url])

def centro(g):
    t, c = g.get('type'), g.get('coordinates')
    if t == 'Point': return c[1], c[0]
    pts = []
    def raccogli(x):
        if x and isinstance(x[0], (int, float)): pts.append(x)
        else: [raccogli(y) for y in x]
    raccogli(c)
    if not pts: return None
    if t == 'LineString': m = pts[len(pts) // 2]; return m[1], m[0]
    lo = [p[0] for p in pts]; la = [p[1] for p in pts]                    # poligoni: centro del rettangolo che li contiene
    return (min(la) + max(la)) / 2, (min(lo) + max(lo)) / 2

def tipo(t):
    if t.get('historic'): return str(t['historic']).lower()
    if t.get('tourism') == 'artwork': return '@a'
    if t.get('amenity') == 'place_of_worship': return '@w'
    return None

def idnorm(i):
    # osmium numera le aree: a(2*id) = via, a(2*id+1) = relazione
    if i[0] == 'a':
        n = int(i[1:]); return ('w%d' % (n // 2)) if n % 2 == 0 else ('r%d' % (n // 2))
    return i

def voci(pbf, bbox, tmp):
    filt, seq = os.path.join(tmp, 'filtrato.osm.pbf'), os.path.join(tmp, 'oggetti.geojsonseq')
    run(['osmium', 'tags-filter', pbf, 'nwr/historic', 'nwr/tourism=artwork', 'nwr/amenity=place_of_worship', '-o', filt, '--overwrite'])
    run(['osmium', 'export', filt, '-f', 'geojsonseq', '--add-unique-id=type_id', '-o', seq, '--overwrite'])
    trovati = {}      # id normalizzato -> voce (una via chiusa esce due volte, come linea e come area: tengo l'area)
    for riga in open(seq, encoding='utf-8'):
        riga = riga.strip('\x1e\n ')
        if not riga: continue
        try: f = json.loads(riga)
        except ValueError: continue
        t = f.get('properties') or {}; h = tipo(t); c = centro(f.get('geometry') or {})
        if not h or not c: continue
        la, lo = round(c[0], 5), round(c[1], 5)
        if not (bbox[0] <= la <= bbox[2] and bbox[1] <= lo <= bbox[3]): continue
        oid = str(f.get('id') or '')
        if not oid: continue
        chiave = idnorm(oid)
        if chiave in trovati and not oid.startswith('a'): continue
        nome = (t.get('name') or t.get('name:it') or '').strip()
        desc = (t.get('description:it') or t.get('description') or '').strip()[:300]
        wp = (t.get('wikipedia') or '').strip()            # "it:Titolo"
        if not wp and re.match(r'^Q\d+$', (t.get('wikidata') or '').strip()): wp = t['wikidata'].strip()
        voce = [la, lo, h, nome, desc, chiave]
        if wp: voce.append(wp)                              # solo se c'è: l'app ne prende la descrizione da Wikipedia quando tocchi il punto
        trovati[chiave] = voce
    return list(trovati.values())

def scrivi(reg, items):
    cartella = os.path.join(OUT, 'osm', reg['id']); os.makedirs(cartella, exist_ok=True)
    pezzi = {}
    for v in items: pezzi.setdefault((math.floor(v[0] * K), math.floor(v[1] * K)), []).append(v)   # stessa formula dell'app: floor(lat * 10)
    nuovi = set()
    for (ty, tx), lista in pezzi.items():
        lista.sort(key=lambda v: (v[0], v[1], v[5]))
        nome = '%d_%d.json' % (ty, tx); nuovi.add(nome)
        testo = json.dumps({'v': 1, 'i': lista}, ensure_ascii=False, separators=(',', ':'))
        p = os.path.join(cartella, nome)
        if not (os.path.exists(p) and open(p, encoding='utf-8').read() == testo):        # non riscrivo i pezzi uguali: niente differenze inutili nel repo
            open(p, 'w', encoding='utf-8').write(testo)
    for nome in os.listdir(cartella):                      # pezzi di questa regione che non esistono più
        if nome.endswith('.json') and nome not in nuovi: os.remove(os.path.join(cartella, nome))
    return len(pezzi)

def indice(reg, n, pezzi, copertura=None):
    p = os.path.join(OUT, 'index.json')
    idx = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {'regioni': []}
    voce = {'id': reg['id'], 'nome': reg['nome'], 'bbox': reg['bbox'], 'pezzo': PEZZO, 'n': n, 'pezzi': pezzi, 'data': datetime.date.today().isoformat(), 'v': int(time.time())}      # v: versione precisa, per non tenere pezzi vecchi dopo una ricostruzione nello stesso giorno
    if copertura is not None and copertura >= 0.9: voce['s'] = True            # le voci portano il numero di edizioni di Wikipedia: l'app può giudicare la notorietà
    idx['regioni'] = [r for r in idx['regioni'] if r['id'] != reg['id']] + [voce]
    idx['regioni'].sort(key=lambda r: r['id'])
    open(p, 'w', encoding='utf-8').write(json.dumps(idx, ensure_ascii=False, indent=1) + '\n')

def togli(reg):
    # una regione spenta: tolgo la sua cartella e la sua riga dall'indice
    cartella = os.path.join(OUT, 'osm', reg['id']); n = 0
    if os.path.isdir(cartella):
        n = len(os.listdir(cartella)); shutil.rmtree(cartella)
    p = os.path.join(OUT, 'index.json')
    if os.path.exists(p):
        idx = json.load(open(p, encoding='utf-8')); idx['regioni'] = [r for r in idx['regioni'] if r['id'] != reg['id']]
        open(p, 'w', encoding='utf-8').write(json.dumps(idx, ensure_ascii=False, indent=1) + '\n')
    print('%s: spenta, tolti %d pezzi' % (reg['nome'], n), flush=True)

def salva_config():
    def riga(r): return '    { "id": "%s", "nome": %s, "attiva": %s, "bbox": %s,\n      "url": "%s" }' % (r['id'], json.dumps(r['nome'], ensure_ascii=False), 'true' if r.get('attiva', True) else 'false', json.dumps(r['bbox']), r['url'])
    t = '{\n  "pezzo": %s,\n  "regioni": [\n' % PEZZO + ',\n'.join(riga(r) for r in CFG['regioni']) + '\n  ]\n}\n'
    open(os.path.join(RADICE, 'tools', 'dati_zone.json'), 'w', encoding='utf-8').write(t)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--solo'); ap.add_argument('--prova'); ap.add_argument('--togli'); ap.add_argument('--imposta', nargs=2, metavar=('ID', 'accendi|spegni')); ap.add_argument('--senza-wikidata', action='store_true')
    a = ap.parse_args()
    tutte = CFG['regioni']; per_id = {r['id']: r for r in tutte}
    if a.imposta:                  # accende o spegne una regione nel catalogo
        i, az = a.imposta
        if i not in per_id or az not in ('accendi', 'spegni'): sys.exit('regione o azione non valide')
        per_id[i]['attiva'] = (az == 'accendi'); salva_config(); print('%s: %s' % (per_id[i]['nome'], 'accesa' if az == 'accendi' else 'spenta')); return
    if a.togli:
        if a.togli not in per_id: sys.exit('regione non trovata')
        togli(per_id[a.togli]); return
    if a.solo:                     # una o più regioni (anche spente), separate da virgola
        regioni = [per_id[i] for i in a.solo.split(',') if i in per_id]
    else: regioni = [r for r in tutte if r.get('attiva', True)]
    if not regioni: sys.exit('regione non trovata')
    os.makedirs(OUT, exist_ok=True)
    vecchi = os.path.join(OUT, 'osm')                         # vecchio formato (un solo elenco di pezzi): lo tolgo
    if os.path.isdir(vecchi):
        for f in os.listdir(vecchi):
            if f.endswith('.json'): os.remove(os.path.join(vecchi, f))
    if not a.solo and not a.prova:
        for r in tutte:
            if not r.get('attiva', True): togli(r)
    for reg in regioni:
        with tempfile.TemporaryDirectory() as tmp:
            pbf = a.prova
            if not pbf: pbf = os.path.join(tmp, reg['id']+'.osm.pbf'); scarica(reg['url'], pbf)
            items = voci(pbf, reg['bbox'], tmp)
        if not items: sys.exit('%s: nessuna voce trovata (indirizzo o riquadro sbagliati?)' % reg['nome'])
        cop = None if a.senza_wikidata else arricchisci(items)
        pezzi = scrivi(reg, items); indice(reg, len(items), pezzi, cop)
        print('%s: %d voci in %d pezzi' % (reg['nome'], len(items), pezzi), flush=True)

if __name__ == '__main__':
    main()
