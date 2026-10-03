# Meteo e viaggio

App web per turisti, Italia e Svizzera, in una pagina.

## Com'è fatta
Una sola pagina. In alto una mappa dettagliata (OpenStreetMap; nei filtri si può scegliere lo sfondo Esri World Street Map, senza icone dei locali): da lontano mostra le città con il meteo (o mare e meduse);
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

Filtri della mappa (tasto imbuto): monumenti e punti di Claude, e la scelta dello sfondo:
- Vettoriale (predefinita): OpenFreeMap disegnata da MapLibre (caricata solo se scelta), in un livello sotto Leaflet
  allineato a ogni spostamento, zoom e rotazione. Icone dello sfondo accendibili per categoria, scritte grandi nitide.
  Se il telefono non regge la grafica vettoriale, l'app torna da sola alla mappa classica.
- OpenStreetMap classica, con tutte le icone dei locali.
- Senza icone dei locali (Esri World Street Map).
Le scelte restano salvate.

Percorsi: nei consigli di Wikivoyage, i paragrafi con "da X a Y" o con un elenco di tappe (giro, percorso, itinerario)
hanno il tasto "Mostra il percorso sulla mappa": le tappe vengono cercate con Nominatim vicino alla città
(una richiesta al secondo, risultati salvati) e unite con il percorso a piedi di routing.openstreetmap.de.

Sulla mappa c'è il tasto posizione: 1° tocco centra e segue, 2° tocco gira la mappa nella direzione in cui vai,
3° tocco torna con il nord in alto (la bussola in alto a sinistra fa lo stesso).
Tutti i tasti della mappa stanno in basso, a portata di pollice: a destra lo zoom a cursore (da zoom 9 al massimo, movimento continuo, un livello ogni 26 px di dito, + e − alle estremità),
in fila a sinistra posizione, opzioni, segna punto e foto; la bussola in alto a sinistra. A schermo intero il tasto opzioni
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

Curiosità e consigli di Claude sulla mappa (punti viola, filtro proprio): compaiono solo se hanno le coordinate del luogo
preciso (non quelle del centro città, condivise da più voci). Toccando un luogo si vedono anche le curiosità entro 80 m; i luoghi con curiosità hanno un anello viola. Nella sezione Curiosità, "Mostra sulla mappa" porta al luogo.
Un consiglio "da-fare" può avere il campo "stops": tappe in ordine, ognuna {"n": nome, "lat", "lon"} (coordinate facoltative:
senza, l'app cerca il nome tra i luoghi noti e poi su OpenStreetMap). Senza "stops", l'app prova a leggere "da X a Y" nel titolo.

Pagina (ottobre 2026): sotto la mappa le schede "Curiosità e leggende" / "Cosa vedere e fare" (altezza limitata,
la mappa resta in vista), poi meteo (aperto) e tabella settimanale. Mare e meduse resta come livello della mappa;
foto e monumenti stanno solo sulla mappa (foto di Wikimedia Commons come miniature tonde, da zoom 12).
Tasti: "Filtri" (monumenti, luoghi di Claude, curiosità, foto, partenze dei percorsi + elenco dei percorsi in zona,
ognuno accendibile, anche più insieme e con colori diversi) e "Sfondo" (tipo di mappa, icone dello sfondo, scritte grandi).
