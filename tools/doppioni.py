#!/usr/bin/env python3
"""Segnala le voci simili (stesso tipo, titolo simile, vicine) in custom-points.json + custom-inbox.json.
Uso: python3 tools/doppioni.py [km=1.5] [soglia=0.55]   -> stampa solo le coppie sospette; non modifica nulla."""
import json, sys, re, math, unicodedata
from difflib import SequenceMatcher
KM = float(sys.argv[1]) if len(sys.argv) > 1 else 1.5
TH = float(sys.argv[2]) if len(sys.argv) > 2 else 0.6
STOP = set('''il lo la i gli le un una di del dello della dei degli delle a al allo alla ai alle da dal dalla in nel nella su sul sulla e ed o con per tra fra che poi
chiesa chiese san santa santo sant sante castello palazzo tempio museo piazza porto borgo parco torre via cattedrale duomo basilica convento teatro spiaggia
ad ss maria madonna mattino pomeriggio sera giornata mezza giorno cielo coperto sole oggi vento'''.split())   # parole generiche o legate al meteo/momento: non distinguono una voce dall'altra
def load(f):
    try: return json.load(open(f, encoding='utf-8'))
    except Exception: return []
def norm(t):
    t = unicodedata.normalize('NFD', t.lower()); t = ''.join(c for c in t if not unicodedata.combining(c))
    return [w for w in re.sub(r'[^a-z0-9 ]', ' ', t).split() if w not in STOP and len(w) > 1]
def km(a, b):
    p = math.pi/180; x = math.sin((b['lat']-a['lat'])*p/2)**2 + math.cos(a['lat']*p)*math.cos(b['lat']*p)*math.sin((b['lon']-a['lon'])*p/2)**2
    return 12742*math.asin(math.sqrt(x))
def sim(a, b):
    A, B = set(a), set(b)
    return len(A & B), (len(A & B)/min(len(A), len(B)) if A and B else 0)
src = [(x, 'points') for x in load('custom-points.json')] + [(x, 'inbox') for x in load('custom-inbox.json')]
V = [(p, s, norm(p.get('title', ''))) for p, s in src if p.get('lat') is not None and p.get('kind') != 'evento']
out = []
for i in range(len(V)):
    for j in range(i+1, len(V)):
        (a, sa, na), (b, sb, nb) = V[i], V[j]
        if (a.get('kind') or 'luogo') != (b.get('kind') or 'luogo'): continue
        d = km(a, b)
        if d > KM: continue
        n, s = sim(na, nb)
        if n >= 2 and s >= TH: out.append((s, d, a['title'], sa, b['title'], sb, a.get('kind') or 'luogo'))
out.sort(reverse=True)
print(f'{len(V)} voci controllate; {len(out)} coppie sospette (entro {KM} km, somiglianza >= {TH})')
for s, d, ta, sa, tb, sb, k in out[:30]:
    print(f'[{k}] {s:.2f} · {d*1000:.0f} m\n   A ({sa}): {ta[:80]}\n   B ({sb}): {tb[:80]}')
if len(out) > 30: print(f'... altre {len(out)-30}')
