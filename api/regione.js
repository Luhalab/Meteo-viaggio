// Funzione di Vercel (gratis nel piano Hobby): avvia il workflow "Dati OpenStreetMap" per accendere o spegnere una regione.
// Il token di GitHub e il PIN stanno solo nelle variabili d'ambiente del progetto su Vercel (GH_DISPATCH_TOKEN e APP_PIN), mai nel codice o nel repo.
// Il token deve avere solo il permesso "Actions: Read and write" su questo repo. Senza il PIN giusto non parte niente.
const crypto = require('crypto');
const cfg = require('../tools/dati_zone.json');
const REPO = 'Luhalab/Meteo-viaggio';

const uguali = (a, b) => { const x = Buffer.from(String(a)), y = Buffer.from(String(b)); return x.length === y.length && crypto.timingSafeEqual(x, y); };

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  const configurato = !!(process.env.GH_DISPATCH_TOKEN && process.env.APP_PIN);
  if (req.method === 'GET') return res.status(200).json({ configurato, token: !!process.env.GH_DISPATCH_TOKEN, pin: !!process.env.APP_PIN });   // dice solo se le variabili ci sono, mai i valori
  if (req.method !== 'POST') return res.status(405).json({ errore: 'metodo non ammesso' });
  if (!configurato) return res.status(503).json({ errore: 'non configurato' });
  let b = req.body;
  if (typeof b === 'string') { try { b = JSON.parse(b); } catch (e) { b = {}; } }
  b = b || {};
  if (!uguali(b.pin || '', process.env.APP_PIN)) {
    await new Promise(r => setTimeout(r, 600));                       // rallenta chi prova a indovinare il PIN
    return res.status(403).json({ errore: 'PIN errato' });
  }
  const reg = (cfg.regioni || []).find(r => r.id === b.id);
  if (!reg || !['accendi', 'spegni'].includes(b.azione)) return res.status(400).json({ errore: 'regione o azione non valide' });
  const r = await fetch('https://api.github.com/repos/' + REPO + '/actions/workflows/dati.yml/dispatches', {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + process.env.GH_DISPATCH_TOKEN, Accept: 'application/vnd.github+json', 'User-Agent': 'meteo-viaggio', 'X-GitHub-Api-Version': '2022-11-28' },
    body: JSON.stringify({ ref: 'main', inputs: { regione: reg.id, azione: b.azione } })
  });
  if (r.status === 204) return res.status(200).json({ ok: true });
  return res.status(502).json({ errore: 'GitHub ha risposto ' + r.status, github: r.status });
};
