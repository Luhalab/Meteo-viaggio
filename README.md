# Meteo e viaggio

App web per turisti, Italia e Svizzera, in una pagina.

## Com'è fatta
Una sola pagina. In alto una mappa dettagliata (OpenStreetMap a ogni zoom): da lontano mostra le città con il meteo (o mare e meduse);
da zoom 14 in su mostra anche la mappa di Cicerone con chiese, monumenti, castelli e opere,
la scheda di ogni punto e "Chiedi a Claude". Schermo intero, "Segna questo punto", "Fotografa un dettaglio".
Scelta una città, sotto la mappa compaiono sezioni a scomparsa: meteo (adesso, 15 giorni, ora per ora),
mare e meduse, foto, monumenti, curiosità e leggende.

Senza città scelta, sotto la mappa c'è la tabella "La settimana a confronto" con tre modi:
- **Sulla mappa** (predefinito): le città visibili, che cambiano spostando o ingrandendo la mappa.
- **Cerca**: si aggiungono le città con la ricerca; la mappa mostra solo quelle e le inquadra.
- **Scegli**: tenendo premuto su una città della mappa la si aggiunge o toglie; la mappa resta libera.
Le città cercate e scelte restano salvate sul telefono.

Fuori dai centri abitati l'app non si aggancia per forza a una città: crea il luogo "Vicino a …"
con meteo, mare, foto e monumenti di quel punto preciso, e curiosità e consigli della città più vicina.
Con il GPS già consentito, all'apertura mostra subito il posto in cui ti trovi.

Sulla mappa c'è il tasto posizione: 1° tocco centra e segue, 2° tocco gira la mappa nella direzione in cui vai,
3° tocco torna con il nord in alto (la bussola in alto a sinistra fa lo stesso).
Tutti i tasti della mappa stanno in basso, a portata di pollice: a sinistra lo zoom a cursore (con + e − alle estremità e la bussola sopra),
a destra segna punto, foto, opzioni e posizione. A schermo intero il tasto opzioni
offre: rotazione seguendo la direzione, rotazione con due dita, nord in alto,
blocca la mappa, schermo sempre acceso. La rotazione usa il plugin leaflet-rotate (jsDelivr); se non si carica,
l'app funziona senza rotazione.

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
