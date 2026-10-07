#!/usr/bin/env python3
"""Alza la versione dell'app in un colpo solo: V in sw.js e APP_V in index.html (devono restare uguali).
Uso: python3 tools/versione.py        (alza di 1)   |   python3 tools/versione.py 120   (imposta v120)"""
import re, sys
sw = open('sw.js', encoding='utf-8').read(); ix = open('index.html', encoding='utf-8').read()
a = re.search(r"const V = 'v(\d+)'", sw); b = re.search(r"const APP_V = 'v(\d+)'", ix)
if not a or not b: sys.exit('non trovo V in sw.js o APP_V in index.html')
n = int(sys.argv[1]) if len(sys.argv) > 1 else max(int(a.group(1)), int(b.group(1))) + 1
open('sw.js', 'w', encoding='utf-8').write(sw.replace(a.group(0), "const V = 'v%d'" % n))
open('index.html', 'w', encoding='utf-8').write(ix.replace(b.group(0), "const APP_V = 'v%d'" % n))
print('versione: v%d (sw.js e index.html)' % n)
