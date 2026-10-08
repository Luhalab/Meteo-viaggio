#!/usr/bin/env python3
"""Costruisce i dati di OpenStreetMap a pezzetti per l'app: monumenti (historic), opere d'arte pubbliche e luoghi di culto.

Per ogni regione di tools/dati_zone.json: scarica l'archivio da Geofabrik (con tentativi), tiene con osmium solo gli oggetti utili,
li divide in pezzi di 0,1 gradi e li scrive in dati/osm/<regione>/<riga>_<colonna>.json; poi aggiorna dati/index.json.
Ogni voce è [lat, lon, tipo, nome, descrizione, id] (+ un settimo campo, "it:Titolo" o "Q123", se ha un collegamento a Wikipedia/Wikidata): tipo = valore di "historic", "@a" (opera d'arte) o "@w" (luogo di culto);
id = n123 / w456 / r789 (nodo, via, relazione di OpenStreetMap).

Uso:  python3 tools/costruisci_dati.py                   tutte le regioni accese (e toglie quelle spente)
      python3 tools/costruisci_dati.py --solo liguria    una sola regione (anche se spenta)
      python3 tools/costruisci_dati.py --imposta toscana accendi    accende o spegne una regione nel catalogo
      python3 tools/costruisci_dati.py --togli toscana   toglie i dati di una regione
      python3 tools/costruisci_dati.py --solo liguria --prova file.osm.pbf     prova locale, senza scaricare
Serve osmium-tool (sudo apt-get install osmium-tool). Dati © OpenStreetMap contributors (ODbL)."""
import argparse, datetime, json, math, os, re, shutil, subprocess, sys, tempfile

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(RADICE, 'tools', 'dati_zone.json'), encoding='utf-8'))
PEZZO = CFG.get('pezzo', 0.1); K = round(1 / PEZZO)          # pezzi per grado
OUT = os.environ.get('DATI_OUT') or os.path.join(RADICE, 'dati')

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

def indice(reg, n, pezzi):
    p = os.path.join(OUT, 'index.json')
    idx = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {'regioni': []}
    voce = {'id': reg['id'], 'nome': reg['nome'], 'bbox': reg['bbox'], 'pezzo': PEZZO, 'n': n, 'pezzi': pezzi, 'data': datetime.date.today().isoformat()}
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
    ap = argparse.ArgumentParser(); ap.add_argument('--solo'); ap.add_argument('--prova'); ap.add_argument('--togli'); ap.add_argument('--imposta', nargs=2, metavar=('ID', 'accendi|spegni'))
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
        pezzi = scrivi(reg, items); indice(reg, len(items), pezzi)
        print('%s: %d voci in %d pezzi' % (reg['nome'], len(items), pezzi), flush=True)

if __name__ == '__main__':
    main()
