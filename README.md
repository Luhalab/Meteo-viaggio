# Meteo e viaggio

App web per turisti: meteo ora per ora e a 15 giorni, stato del mare, meduse,
guida delle città con foto, eventi. Italia e Svizzera.

## Struttura
- `index.html` — l'app (il "motore", uguale per tutte le regioni)
- `region-italia.json` — 7.894 comuni + 105 punti mare
- `region-svizzera.json` — 1.415 località, senza mare
- `sw.js`, `manifest.webmanifest`, `icon-*.png` — installazione come app

Per aggiungere una regione: nuovo file in la cartella principale e una riga nell'elenco
`REGIONI` dentro `index.html`.

## Fonti (nessuna API key)
Open-Meteo con modello ICON-2I di ItaliaMeteo-ARPAE · Open-Meteo Marine ·
iNaturalist · Wikipedia e Wikivoyage (CC BY-SA) · Wikimedia Commons ·
sfondo mappa Esri, con OpenStreetMap di riserva · comuni italiani ISTAT ·
località svizzere GeoNames

## Pubblicazione
Sito statico: su Vercel scegliere Framework Preset "Other", senza build.
