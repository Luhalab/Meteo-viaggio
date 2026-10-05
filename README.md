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

Due modi secondo lo zoom: da lontano (sotto zoom 14) meteo, tabella settimanale e livello mare e meduse;
da vicino (zoom 14+) monumenti, foto, percorsi e le schede curiosità / cose da fare. Il tasto sotto il nome
della città ("Esplora …" / "Torna al meteo") passa dall'uno all'altro; anche "Vai alla città" nel fumetto.

Foto: non più sulla mappa. Nel modo meteo, scelta una città, sotto il nome compare una striscia con le immagini
della voce di Wikipedia della città (prima la foto principale; solo jpg grandi, senza stemmi e mappe); toccandole
si apre il visore a tutto schermo. Nei filtri compaiono solo i percorsi con almeno 2 tappe con coordinate.

Pagina personalizzabile (tasto "Personalizza la pagina" in fondo): ordine e visibilità dei blocchi Esplora,
Chiedi a Claude, Mappa, Meteo/Mare, Foto, schede Curiosità/Cosa fare, Meteo, Settimana (salvati sul telefono).
L'ordine predefinito tiene sopra la mappa solo blocchi che non cambiano con lo zoom, così la mappa non salta.
Tolto il riquadro di giudizio della giornata ("Tempo incerto…") dalla sezione meteo.

Zoom: due tasti in basso a destra, "Città" (zoom 16) e "Meteo" (zoom 9), centrati sulla città scelta o sulla posizione.
Curiosità e consigli chiusi di default, con le fonti (campo "fonti": [{"t","url"}] o "url"; altrimenti "cerca su Wikipedia").
"Cosa vedere e fare": foto della guida Wikivoyage, sentieri segnati da OpenStreetMap (relazioni route=hiking/foot,
con tracciato vero, anche nei filtri dei percorsi), testi Wikivoyage e consigli di Claude, con fonti.
A schermo intero e da vicino, curiosità e cose da fare diventano un pannello in basso: chiuso mostra le linguette,
aperto occupa metà schermo.
A schermo intero e da lontano, con una città scelta, il pannello in basso ha "Meteo" e "Foto".
Nei pannelli: toccare la linguetta già scelta chiude, un'altra linguetta apre; si possono anche trascinare su e giù.
Meteo essenziale: solo la fila ora per ora di oggi (con "adesso" al centro) e la tabella settimanale, con la città
scelta sempre presente ed evidenziata e la stella sulla settimana migliore; tolti condizioni attuali, 15 giorni e testi.
Nel pannello a schermo intero la linguetta Meteo contiene entrambe.

Interfaccia tipo Google Maps (ottobre 2026): la mappa occupa tutto lo schermo; in alto ricerca (con tasto tema) e chip
delle nazioni (REGIONI: per aggiungerne una basta un nuovo elemento); a destra in alto livelli (mappa con / senza icone)
e filtri; a destra in basso posizione e zoom Città / Meteo; in basso il pannello con testata del luogo (nome, meteo,
Esplora, Chiedi a Claude) e linguette Meteo/Foto da lontano, Curiosità/Cosa fare da vicino. "Mare e meduse" è una scelta nel pannello Livelli (solo da lontano, solo dove c'è il mare).
Foto: nel visore "Mostra sulla mappa" usa le coordinate del file su Commons; se mancano e la foto ritrae un luogo noto,
lo cerca tra i luoghi noti e poi su OpenStreetMap ("stimata"); le foto di cibo senza coordinate non vanno sulla mappa.
Pannello a tre posizioni (chiuso, metà, tutto lo schermo) che segue il dito come su Google Maps: al rilascio va sulla posizione più vicina, con un gesto veloce sulla successiva; dal contenuto in cima si trascina giù, le righe orizzontali scorrono normalmente.
Tabella: 7 o 15 giorni (la stella della città migliore usa la media sul periodo scelto); toccando una città la si sceglie
(mappa e ora per ora seguono), toccando un giorno (cella o intestazione) l'ora per ora mostra quel giorno.
Ora per ora: solo le ore 6, 8, 10 … 22, più l'ora attuale ("adesso"). Pannello animato (anche all'apertura da chiuso), trascinamento aggiornato una volta per fotogramma.

Linguetta "Eventi" (accanto a Curiosità e Cosa fare): eventi nei prossimi 15 giorni entro 15 km, da custom-points.json
("kind": "evento", con "inizio", "fine" AAAA-MM-GG, "luogo", coordinate, "extract", "fonti") e da Wikidata (eventi con data
e coordinate); poi le feste tradizionali dalla guida Wikivoyage (date indicative). Il tasto "Cerca eventi con Claude" manda
il messaggio "[Meteo e viaggio: eventi]" all'altra chat, che li cerca su comune, pro loco, regione e siti di eventi.
Gli eventi non compaiono come punti fissi sulla mappa (solo con "Mostra sulla mappa").

Indicazioni: tenendo premuto sulla mappa. Da vicino si aprono subito; da lontano compare un piccolo menu
("Confronta il meteo di …" / "Indicazioni fin qui"). Partenza = posizione GPS (modificabile toccando A e poi la mappa),
arrivo = punto premuto (modificabile allo stesso modo). Auto e a piedi calcolati insieme (routing.openstreetmap.de),
nomi dei punti da Nominatim, "Apri in Google Maps" per la navigazione.
Indicazioni: la mappa non si sposta da sola (tasto "Mostra tutto"); tappe intermedie ("+ Aggiungi tappa", poi tocco sulla
mappa; mentre scegli la scheda si nasconde); "Salva percorso" li salva sul telefono (localStorage "myRoutes") e li mostra
nei filtri della zona ("Il mio percorso", eliminabili). Ricerca: oltre ai comuni, "Cerca … come via o luogo" (Nominatim
vicino alla città o alla zona); dal risultato: indicazioni fin lì, o partenza/tappa/arrivo se le indicazioni sono aperte.
Locali a richiesta: chip Ristoranti, Bar, Gelaterie, Hotel accanto alle nazioni (Overpass, al massimo 40 nella zona,
si aggiornano spostando la mappa, spariscono toccando di nuovo il chip); scheda con orari, telefono, link a Google
(foto e recensioni), TripAdvisor e "Indicazioni fin qui".
Locali: prima dalle tile vettoriali già scaricate (nessuna richiesta), altrimenti Overpass con server di riserva (kumi.systems, private.coffee); orari e telefono chiesti a OpenStreetMap solo toccando il locale. Con un chip acceso monumenti e punti di Claude si nascondono.
Chip dei locali ridotti a Ristoranti e Bar e gelaterie, presi solo dalla mappa vettoriale (online solo se la vettoriale manca). Spegnendo il chip i monumenti tornano (ricaricati se mancano); se una fonte dei monumenti non risponde e non c'è nulla, l'app riprova da sola una volta.
Monumenti: ogni fonte ha un tempo massimo e i punti compaiono man mano che arrivano (una fonte lenta non blocca più tutto). Gli eventi non contano nel decidere se una curiosità è legata a un luogo preciso.
Percorso attivo: chiudendo la scheda delle indicazioni il percorso resta sulla mappa, con un riquadro in basso
(tempo · km, tocca per riaprire, ✕ per togliere); resta anche riaprendo l'app per 24 ore (localStorage "navActive").
I miei percorsi: salvati nel browser del telefono finché non li elimini; Filtri → "Gestisci i miei percorsi" per vederli
tutti, mostrarli, eliminarne alcuni o tutti.

Avvio veloce: service worker con pagina dalla rete se risponde entro 2,5 s (altrimenti copia salvata), librerie salvate
una volta, tile della mappa salvate (fino a ~4000) e aggiornate in background. L'app salva in IndexedDB previsioni
(riusate per 30 minuti, offline fino a un giorno), monumenti per zona (3 giorni senza richiedere, poi aggiornati),
testi di Wikipedia/Wikivoyage, foto e sentieri (7 giorni); pulizia automatica dopo 14 giorni. Riaprendo entro 12 ore
riparte dall'ultima zona e città.
Riapertura come Google Maps: la mappa nasce già nell'ultima zona e zoom (salvati a ogni spostamento e quando esci dall'app), poi torna la città scelta; senza limite di tempo. Il salto automatico sulla posizione GPS avviene solo la prima volta.
