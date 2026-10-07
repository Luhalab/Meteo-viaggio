# Meteo e viaggio — riassunto per ripartire in una chat nuova

Repo `Luhalab/Meteo-viaggio` (branch `main`, deploy automatico su Vercel). App web a pagina unica, in italiano, pensata per il telefono Android di Luca.
Il dettaglio funzione per funzione è nel `README.md` (lungo: leggilo solo se serve). Prima di pubblicare: `git pull --rebase` (l'altra chat
"Guida D'Arte" fa commit su `custom-points.json`/`custom-inbox.json`), alza `V` in `sw.js`, aggiungi una riga al README.

## File
- `index.html` (~3000 righe di JS in un solo `<script>`), `sw.js` (cache: pagina dalla rete entro 2,5 s, librerie e tile salvate), `manifest.webmanifest`.
- `custom-points.json` (116 KB, ~190 voci: luoghi, curiosità, consigli "da-fare", eventi): NON leggerlo né stamparlo intero.
- `custom-inbox.json` (piccolo): dove l'altra chat aggiunge le voci nuove; l'app legge i due file insieme. Quando supera ~30 voci, unirlo al file grande con uno script.
- `region-italia.json`, `region-svizzera.json`: comuni.

- `tools/doppioni.py`: segnala voci simili (stesso tipo, titolo simile, vicine) in custom-points + inbox; non modifica nulla. Lancialo ogni tanto: `python3 tools/doppioni.py`.

## Come funziona
- Due modalità: **meteo** (zoom < 14: etichette meteo, ★ luoghi imperdibili, tabella settimanale) e **città** (zoom ≥ 14: monumenti, curiosità, consigli, percorsi, eventi). Tasto Esplora/Torna al meteo e zoom Città/Meteo.
- Interfaccia tipo Google Maps: ricerca + chip (Italia/Svizzera, Ristoranti, Bar e gelaterie) in alto, Livelli e Filtri a destra, pannello in basso con 3 posizioni (chiuso/metà/tutto), trascinabile.
- Filtri: due serie separate (meteo: monumenti/luoghi/curiosità spenti di default; città: tutto acceso). Percorsi: elenco nei Filtri solo in modalità città; i percorsi accesi restano sulla mappa anche se cambi zona e si spengono dal pannello.
- "Chiedi a Claude": apre la chat del progetto con un messaggio già scritto. In meteo con una città scelta, o senza città ("Cosa fare in questa zona"), chiede consigli in base al meteo e alle preferenze; i consigli nuovi compaiono nella linguetta "Consigli (N)" accanto a Meteo e Foto.
- Messaggi pensati per consumare pochi token: modalità Veloce (default)/Approfondito, limiti di ricerca, elenco dei titoli già presenti, salvataggio in `custom-inbox.json`.
- GPS stabile (filtro di Kalman, puntino morbido, riavvio automatico), apertura veloce (IndexedDB + service worker + ultima vista salvata), volo verso la città fluido (lavoro pesante a volo finito), linee ridisegnate a ogni fotogramma durante lo zoom con due dita.

## Da fare / da ricordare
- Luca deve aggiornare le istruzioni del progetto "Guida D'Arte": scrivere le voci in `custom-inbox.json`, non leggere mai il file grande, rispettare i LIMITI scritti nel messaggio.
- Token GitHub fine-grained da rinnovare alla scadenza; non incollarlo mai nella chat.
- I consigli non scadono: restano finché Luca non li toglie dall'app (✕); l'eliminazione vale solo su quel telefono.
