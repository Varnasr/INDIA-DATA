// Writes i18n/catalogue.json: every string a reader can see on the site, as
// the key the translations are stored under.
//
//   node scripts/i18n_collect.mjs
//
// Needs playwright-core and a Chromium (set PLAYWRIGHT_CORE to the module's
// index.mjs and CHROME to the executable if they are not found). It serves
// the repository itself on a spare port.
//
// Fixed text in the markup is read from a browser, because the key is the
// element's inner HTML as the browser serialises it, and a hand-written
// parser would disagree about entities and attribute quoting. Sentences
// built by scripts are read from the source: the first argument of every
// L('...') call. check_i18n.py reads the same source and fails if the two
// drift apart.
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const PW = process.env.PLAYWRIGHT_CORE || 'playwright-core';
const { chromium } = await import(PW);
// Every page on disk under the two analyses, plus the home page, so a page
// added later is collected without anyone remembering to list it here.
const walk = (d) => fs.readdirSync(path.join(ROOT, d), { withFileTypes: true }).flatMap((e) =>
  e.isDirectory() ? walk(path.join(d, e.name)) : e.name === 'index.html' ? [d ? d + '/' : ''] : []);
// The analyses are the first folder of every page each place lists.
const SECTIONS = [...new Set(JSON.parse(fs.readFileSync(path.join(ROOT, 'site/places.json'), 'utf8')).places
  .flatMap((p) => p.pages.map((x) => x[0].split('/')[0])))];
// plus any top-level page of the front page's own (terms/), from site/pages
const OWN = fs.readdirSync(path.join(ROOT, 'site/pages'), { withFileTypes: true })
  .filter((e) => e.isDirectory() && !SECTIONS.includes(e.name)).map((e) => e.name);
const PAGES = ['', ...SECTIONS.flatMap((d) => walk(d)), ...OWN.flatMap((d) => walk(d))].sort();
const SOURCES = ['index.html', 'assets/sir.js', 'assets/dash.js', 'assets/i18n.js', ...fs.readdirSync(path.join(ROOT, 'assets/faq')).filter(f => f.endsWith('.js')).sort().map(f => 'assets/faq/' + f), ...PAGES.filter(Boolean).map(p => p + 'index.html')];

const cat = {};
const add = (k, page, kind) => { const e = cat[k] || (cat[k] = { kind, pages: [] }); if (!e.pages.includes(page)) e.pages.push(page); if (kind === 'script') e.kind = 'script'; };

// Sentences built by scripts.
const LIT = /(?<![\w.$])L\(\s*'((?:[^'\\]|\\.)*)'/g;
for (const f of SOURCES) {
  const text = fs.readFileSync(path.join(ROOT, f), 'utf8');
  for (const m of text.matchAll(LIT)) add(m[1].replace(/\\(.)/g, (x, c) => ({ n: '\n', t: '\t' })[c] || c), '/' + f.replace(/index\.html$/, ''), 'script');
}

// Fixed text in the markup.
const port = 8700 + Math.floor(Math.random() * 200);
const srv = spawn('python3', ['-m', 'http.server', String(port)], { cwd: ROOT, stdio: 'ignore' });
await new Promise(r => setTimeout(r, 800));
const browser = await chromium.launch(process.env.CHROME ? { executablePath: process.env.CHROME } : {});
try {
  for (const p of PAGES) {
    const page = await browser.newPage();
    // The page scripts are not needed: fixed text is collected before they run.
    await page.route('**cdnjs.cloudflare.com/**', r => r.fulfill({ body: '', contentType: 'application/javascript' }));
    await page.goto(`http://localhost:${port}/${p}?i18n-collect=1&lang=en`, { waitUntil: 'load' });
    const got = await page.evaluate(() => window.L && L.collected ? L.collected().statics : null);
    if (!got) throw new Error('no collector on /' + p);
    got.forEach(k => add(k, '/' + p, 'markup'));
    await page.close();
  }
} finally {
  await browser.close();
  srv.kill();
}
const sorted = Object.fromEntries(Object.keys(cat).sort().map(k => [k, cat[k]]));
fs.mkdirSync(path.join(ROOT, 'i18n'), { recursive: true });
fs.writeFileSync(path.join(ROOT, 'i18n', 'catalogue.json'), JSON.stringify(sorted, null, 1) + '\n');
const n = Object.keys(sorted).length, s = Object.values(sorted).filter(e => e.kind === 'script').length;
console.log(`${n} strings: ${s} built by scripts, ${n - s} in the markup`);
