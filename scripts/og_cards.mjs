// Writes assets/og/<place>.png: the 1200x630 card a link preview shows when a
// page is shared on WhatsApp or elsewhere. One card per place, carrying the
// place's headline figure, read from the published JSON.
//
//   node scripts/og_cards.mjs
//
// Needs playwright-core and a Chromium (PLAYWRIGHT_CORE and CHROME, as for
// i18n_collect.mjs). Re-run after any data change: nothing checks that the
// figure on a card is current.
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const { chromium } = await import(process.env.PLAYWRIGHT_CORE || 'playwright-core');
const J = (f) => JSON.parse(fs.readFileSync(path.join(ROOT, 'data', f), 'utf8'));
const n = (x) => Math.round(x).toLocaleString('en-IN');
const p = (x) => (Math.round(x * 10) / 10).toFixed(1);
const CFG = JSON.parse(fs.readFileSync(path.join(ROOT, 'site/places.json'), 'utf8'));
const place = Object.fromEntries(CFG.places.map((x) => [x.id, x]));

const india = J('india/states.json').total;
const bh = J('bihar/summary.json').totals;
const hy = J('hyderabad/summary.json').totals;
const tn = J('tamilnadu/summary.json');
const ka = J('karnataka/summary.json');
const wb = J('westbengal/summary.json');
const kl = J('kerala/summary.json');
const rj = J('rajasthan/summary.json');
const up = J('uttarpradesh/summary.json');
const dl = J('delhi/summary.json');
const mh = J('maharashtra/summary.json');
const gj = J('gujarat/summary.json');
const uk = J('uttarakhand/summary.json');
const as = J('assam/summary.json').state;

// [place id, place name, big figure, the line under it, a second line]
const CARDS = [
  ['home', 'All India', n(india.removed), `names left off the draft electoral rolls in ${india.states} states and union territories`,
    `${p(india.per_100)} of every 100 electors on the rolls before the revision`],
  ['india', 'All India', n(india.removed), `names left off the draft electoral rolls in ${india.states} states and union territories`,
    `${p(india.per_100)} of every 100 electors on the rolls before the revision`],
  ['bihar', 'Bihar 2025', n(bh.total), `names removed from Bihar's electoral roll in ${n(bh.acs)} constituencies`,
    `Women were ${p(100 * bh.female / (bh.female + bh.male))}% of those removed`],
  ['hyd', 'Hyderabad Old City 2026', n(hy.deleted), `names removed from the rolls of five Old City constituencies`,
    `${p(hy.rate)} of every 100 electors, across ${n(hy.parts)} polling parts`],
  ['tn', 'Tamil Nadu 2026', n(tn.removed), `names left off Tamil Nadu's draft roll`,
    `More than the 2026 winning margin in ${tn.over_margin} of ${tn.acs} constituencies`],
  ['ka', 'Karnataka 2026', n(ka.removed), `names left off Karnataka's draft roll`,
    `${p(ka.per_100)} of every 100 electors, in ${ka.districts} districts`],
  ['wb', 'West Bengal 2026', n(wb.fall), `fewer names on the roll the 2026 election was held on than on the 2024 roll`,
    `Larger than the winning margin in ${wb.over_margin} of ${wb.acs} constituencies`],
  ['kl', 'Kerala 2026', n(kl.fall_draft), `fewer names on Kerala's draft roll than in January 2025`,
    `${p(kl.draft_per_100)} of every 100 electors on the January 2025 roll`],
  ['rj', 'Rajasthan 2026', n(rj.left_off), `names left off Rajasthan's draft roll`,
    `${p(rj.left_per_100)} of every 100 electors on the roll before the revision`],
  ['up', 'Uttar Pradesh 2026', n(up.left_off), `names left off Uttar Pradesh's draft roll`,
    `${p(up.per_100)} of every 100 electors, in ${up.districts} districts`],
  ['dl', 'Delhi 2026', n(dl.left_off), `names left off Delhi's draft roll`,
    `More than the 2025 winning margin in ${dl.over_margin} of ${dl.acs} constituencies`],
  ['mh', 'Maharashtra 2026', n(mh.left_off), `names left off Maharashtra's draft roll`,
    `${p(mh.per_100)} of every 100 electors, in ${mh.districts} districts`],
  ['gj', 'Gujarat 2026', n(gj.removed), `names left off Gujarat's draft roll`,
    `More than the 2022 winning margin in ${gj.over_margin} of ${gj.acs} constituencies`],
  ['uk', 'Uttarakhand 2026', n(uk.left_off), `names left off Uttarakhand's draft roll`,
    `Women were ${p(uk.women_objections_pct)}% of those removed after it`],
  ['as', 'Assam 2026', n(as.flagged), `names flagged for deletion in Assam's special revision`,
    `${n(as.d_voters_draft)} D-voters carried onto the draft unchanged`],
];

// The states and territories drawn by assets/statepage.js, each read from its
// own summary (scripts/build_states.py). Their places carry the CSV download.
const MON = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const day = (iso) => { const [y, m, d] = iso.split('-').map(Number); return `${d} ${MON[m - 1]} ${y}`; };
for (const pl of CFG.places) {
  const csv = (pl.downloads || []).map((d) => d[0]).find((f) => /^data\/[a-z]+\/tables\.csv$/.test(f));
  if (!csv) continue;
  const d = J(csv.slice(5).replace('tables.csv', 'summary.json')), F = d.figures, R = d.rates, st = d.state;
  if (d.revision === 'no_draft') {
    CARDS.push([pl.id, pl.label, 'No draft yet', `${st}'s draft roll had not been published when these pages were built`,
      d.dates.draft ? `The draft is due on ${day(d.dates.draft)}` : 'No date has been set for the draft']);
  } else {
    CARDS.push([pl.id, pl.label, n(F.removed.v), st.length > 30 ? 'names left off the draft roll' : `names left off ${st}'s draft roll`,
      `${p(R.per_100)} of every 100 electors on the roll before the revision`]);
  }
}

const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
const html = (c) => `<!DOCTYPE html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="/assets/sir.css"><style>
html,body{margin:0;width:1200px;height:630px;overflow:hidden}
body{background:var(--bg);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.band{height:28px;background-size:auto 28px!important;animation:none!important}
.c{padding:56px 72px 0}
.k{font-size:30px;font-weight:700;color:var(--muted);letter-spacing:.01em}
.pl{font-size:64px;font-weight:800;margin:6px 0 34px;color:var(--ink)}
.big{font-size:112px;font-weight:800;line-height:1;color:var(--fill-red)}
.l1{font-size:38px;line-height:1.25;margin-top:16px;max-width:1040px}
.l2{font-size:30px;color:var(--muted);margin-top:18px}
</style></head><body data-theme="light"><div class="band ${place[c[0]].band}"></div><div class="c">
<div class="k">SIR analysis for India</div><div class="pl"${c[1].length > 30 ? ' style="font-size:44px;margin-bottom:26px"' : ''}>${esc(c[1])}</div>
<div class="big">${esc(c[2])}</div><div class="l1">${esc(c[3])}</div><div class="l2">${esc(c[4])}</div></div></body></html>`;

const port = 8700 + Math.floor(Math.random() * 200);
const srv = spawn('python3', ['-m', 'http.server', String(port)], { cwd: ROOT, stdio: 'ignore' });
await new Promise((r) => setTimeout(r, 800));
const browser = await chromium.launch(process.env.CHROME ? { executablePath: process.env.CHROME } : {});
fs.mkdirSync(path.join(ROOT, 'assets/og'), { recursive: true });
try {
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
  await page.route('**fonts.googleapis.com/**', (r) => r.abort());
  for (const c of CARDS) {
    await page.route(`http://localhost:${port}/og`, (r) => r.fulfill({ body: html(c), contentType: 'text/html' }));
    await page.goto(`http://localhost:${port}/og`, { waitUntil: 'load' });
    await page.screenshot({ path: path.join(ROOT, 'assets/og', c[0] + '.png') });
    await page.unroute(`http://localhost:${port}/og`);
    console.log(c[0], c[2]);
  }
} finally {
  await browser.close();
  srv.kill();
}
