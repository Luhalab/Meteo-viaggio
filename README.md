# Meteo e viaggio

Repo `Luhalab/Meteo-viaggio` (branch `main`, deploy automatico su Vercel). Questo README è anche il riassunto per ripartire in una chat nuova: vedi "Per riprendere il lavoro" in fondo.

App web per turisti (Italia e Svizzera) in una pagina, pensata per il telefono. Sito statico: nessuna build, nessuna API key, nessuna API a pagamento. Su Vercel: Framework Preset "Other".

## File
- `index.html`: tutta l'app (HTML, CSS e un solo `<script>` di JS, ~3.700 righe). `sw.js`: cache offline (alzare `V` a ogni modifica). `manifest.webmanifest`, `icon-*.png`: installazione come app.
- `region-italia.json` (7.894 comuni + 105 punti mare), `region-svizzera.json` (1.415 località): elenco città per regione.
- `custom-points.json` (grande, ~190 voci) e `custom-inbox.json` (piccolo): voci aggiunte da Claude. Quando l'inbox supera ~30 voci, unirla al file grande con uno script.
- `tools/doppioni.py`: segnala voci simili (stesso tipo, titolo simile, entro 1,5 km); non modifica nulla.

## Schermata
- Mappa a schermo intero. In alto: ricerca (con tasto tema) e chip Italia/Svizzera, Ristoranti, Bar e gelaterie. A destra: Livelli e Filtri. In basso a destra: posizione e zoom Città/Meteo. In basso: pannello a 3 posizioni (chiuso, metà, tutto), che segue il dito.
- Due modalità secondo lo zoom. **Meteo** (sotto 14): città con il meteo, luoghi imperdibili ★ (da zoom 8,5, da Wikidata), livello Mare e meduse (solo dove c'è il mare); pannello con linguette Meteo, Foto, Consigli. **Città** (da 14): monumenti, curiosità, consigli, percorsi, eventi; pannello con Curiosità, Cosa fare, Eventi. "Esplora"/"Torna al meteo" passa dall'una all'altra.
- Fuori dai centri abitati crea il luogo "Vicino a …" con i dati di quel punto e le curiosità della città più vicina.
- Tasto posizione: 1° tocco segue, 2° ruota la mappa, 3° nord in alto. GPS con filtro di Kalman, riavvio automatico se non arrivano fix.
- Personalizza la pagina: ordine e visibilità dei blocchi (salvati sul telefono).

## Meteo
Open-Meteo (modello ICON-2I) e Open-Meteo Marine. Ora per ora (6, 8 … 22 e "adesso") e tabella "La settimana a confronto" (7 o 15 giorni, stella sulla città migliore; modi Sulla mappa, Cerca, Scegli). Vento in km/h con freccia. Le città cercate e scelte restano salvate.

## Mappa e luoghi
- Sfondi (Filtri): vettoriale OpenFreeMap con MapLibre (predefinito, torna alla classica se il telefono non regge), OpenStreetMap classica, Esri senza icone dei locali. Con il vettoriale l'animazione di zoom di Leaflet è spenta (`_zoomAnimated = false`): in quel caso il plugin di rotazione non ruota i riquadri, quindi a ogni apertura li forziamo a `_zoomAnimated = true` e li rimisuriamo (`popFix`), altrimenti con la mappa ruotata si staccano dalla città.
- Monumenti da più fonti (OSM/Overpass, Wikipedia, geo.admin.ch, patrimonioculturale-er.it, Regione Liguria), ognuna con un tempo massimo. Punti entro 30 m (o stesso nome entro 150 m) uniti in uno.
- Foto: striscia con le immagini Wikipedia della città; il visore ha "Mostra sulla mappa" (coordinate di Commons, altrimenti stimate).
- Locali (chip): dalla mappa vettoriale, Overpass solo se manca; al massimo 40; orari e telefono da OSM solo al tocco.
- Filtri separati per modalità (meteo: monumenti, luoghi di Claude e curiosità spenti; città: tutto acceso), salvati in `mapFilters2`.
- Eventi (15 giorni, 15 km): voci `"kind": "evento"` (campi `inizio`, `fine`, `luogo`), Wikidata, feste di Wikivoyage. "Cerca eventi con Claude" manda `[Meteo e viaggio: eventi]`.

## Indicazioni e percorsi
- Pressione lunga sulla mappa: indicazioni (auto e piedi con routing.openstreetmap.de, nomi da Nominatim, "Apri in Google Maps"), con tappe intermedie. "Salva percorso" → `myRoutes` sul telefono; "Gestisci i miei percorsi" nei Filtri. Il percorso attivo resta 24 h (`navActive`).
- Percorsi dei consigli: campo `stops` (tappe in ordine, nome + lat/lon facoltativi; senza coordinate cerca il nome tra i luoghi noti e poi su Nominatim, 1 richiesta al secondo). Anche paragrafi Wikivoyage "da X a Y" e sentieri OSM (route=hiking/foot).
- Elenco percorsi (Filtri, solo modalità città): consigli entro 12 km dal centro, al massimo 8. I percorsi accesi restano sulla mappa cambiando zona finché non li spegni.

## Voci di Claude (custom-points.json e custom-inbox.json)
Ogni voce: `title`, `lat`, `lon`, `extract`, `url` (null); facoltativi `fonti` (`[{"t","url"}]`), `stops`, `kind`.
- senza `kind`: luogo (punto sulla mappa, rosso mattone); `"curiosita"`: leggenda o aneddoto; `"da-fare"`: consiglio; `"evento"`.
- Curiosità e consigli legati a un luogo usano le coordinate di quel luogo (non il centro città) e compaiono sulla mappa con un anello viola; più voci sullo stesso luogo hanno le stesse coordinate. Solo quelle generiche usano il centro città.
- L'app legge i due file insieme (no-cache, ogni 3 minuti, al ritorno nell'app) e toglie i doppioni (stesso titolo e coordinate).

## Chiedi a Claude e consigli di zona
- Il tasto apre la chat del progetto con un messaggio `[Meteo e viaggio: città | posizione | foto | luogo | zona | città e meteo | eventi]`. In modalità meteo ("Cosa fare in questa zona" o città scelta) chiede consigli in base al meteo e alle preferenze (quando, interessi, testo libero).
- Segna quali consigli esistono già (`zoneAsk`, 14 giorni); i consigli nuovi nella zona chiesta diventano "consigli della tua richiesta" (`zoneFound`): linguetta "Consigli (N)", 💡 sulla mappa, interruttore del percorso, ✕ per toglierli (solo su quel telefono).
- Valgono solo il giorno in cui arrivano: spariscono a mezzanotte (controllo all'apertura, al ritorno nell'app e ogni 10 minuti). Restano come consigli della modalità città, dove le frasi sul meteo del giorno ("Oggi vento minimo, 12 km/h") sono tolte dal testo.

## Risparmio di token
Messaggi compatti con LIMITI di ricerca: Veloce (3 ricerche, 3 consigli, 150 parole) o Approfondito (8, 5, 300). Includono l'elenco dei titoli già presenti vicino al punto (i più vicini per primi, al massimo 25) così Claude non rilegge il file; le voci nuove vanno in `custom-inbox.json`. Stessa richiesta entro 30 minuti: chiede conferma. I token si consumano solo nelle chat di Claude.

## Velocità e cache
Service worker: pagina dalla rete entro 2,5 s (altrimenti copia salvata), librerie e tile (~4000) salvate. IndexedDB: previsioni 30 minuti (offline fino a un giorno), monumenti 3 giorni, testi, foto e sentieri 7 giorni; pulizia dopo 14 giorni. Riapre nell'ultima zona e zoom. Rotazione mappa: plugin leaflet-rotate (jsDelivr), opzionale.

## Fonti
Open-Meteo · iNaturalist · Wikipedia, Wikivoyage, Wikidata, Wikimedia Commons · OpenStreetMap, Overpass, Nominatim · geo.admin.ch · patrimonioculturale-er.it · Regione Liguria · OpenFreeMap · Esri · ISTAT · GeoNames.

## Per riprendere il lavoro
- Modo di lavorare: modifiche piccole e testate (controllo sintassi con `node --check` sul `<script>`), poi `git pull --rebase` (l'altra chat "Guida D'Arte" committa su `custom-points.json` e `custom-inbox.json`), alza `V` in `sw.js`, aggiorna qui solo la sezione che cambia (niente cronologia: c'è `git log`) e `git push`. Rispondere in italiano, in modo conciso.
- Token: NON leggere né stampare `custom-points.json` (116 KB); per cercare una voce usare uno script che stampa solo quella. Il README è breve e si può leggere intero.
- Da ricordare: il progetto "Guida D'Arte" deve scrivere solo in `custom-inbox.json`, non leggere mai il file grande e rispettare i LIMITI del messaggio. Il token GitHub fine-grained va rinnovato alla scadenza e non incollato in chat. I consigli di zona li toglie l'utente con ✕ (vale solo su quel telefono).
