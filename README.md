# Meteo e viaggio

App web per turisti, Italia e Svizzera, in due pagine.

## Pagine
- **Esplora**: una sola mappa. Da lontano mostra le città con il meteo (o mare e meduse);
  da zoom 14 in su diventa la mappa di Cicerone con chiese, monumenti, castelli e opere,
  la scheda di ogni punto e "Chiedi a Claude". Schermo intero, "Segna questo punto", "Fotografa un dettaglio".
  Sotto la mappa: foto della città e monumenti e curiosità.
- **Meteo**: l'app di sempre (mappa meteo, scheda città ora per ora e 15 giorni, mare, eventi).

## Struttura
- `index.html` — l'app (il "motore", uguale per tutte le regioni)
- `region-italia.json` — 7.894 comuni + 105 punti mare
- `region-svizzera.json` — 1.415 località, senza mare
- `custom-points.json` — punti e curiosità aggiunti a mano da Claude
- `sw.js`, `manifest.webmanifest`, `icon-*.png` — installazione come app

## Punti e curiosità aggiunti da Claude
`custom-points.json` è una lista. Ogni voce:
```json
{ "title": "Nome", "lat": 37.85, "lon": 15.28, "extract": "Descrizione breve", "url": null }
```
Con `"kind": "curiosita"` la voce compare tra le curiosità della città più vicina invece che come punto sulla mappa.
Sulla mappa i punti aggiunti da Claude sono rosso mattone, gli altri dorati.

## Fonti (nessuna API key)
Open-Meteo con modello ICON-2I di ItaliaMeteo-ARPAE · Open-Meteo Marine · iNaturalist ·
Wikipedia e Wikivoyage (CC BY-SA) · Wikimedia Commons · OpenStreetMap e Overpass ·
geo.admin.ch (beni culturali KGS) · patrimonioculturale-er.it · Regione Liguria ·
sfondo mappa Esri, con OpenStreetMap di riserva · comuni italiani ISTAT · località svizzere GeoNames

## Pubblicazione
Sito statico: su Vercel scegliere Framework Preset "Other", senza build.
