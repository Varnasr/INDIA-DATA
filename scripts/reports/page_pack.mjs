// A PDF report and a slide deck for every analysis that has no hand-built
// one, made from the analysis's own pages, so neither can say anything the
// site does not.
//
//   PLAYWRIGHT_CORE=... CHROME=... NODE_PATH=<dir with pptxgenjs> \
//     node scripts/reports/page_pack.mjs http://localhost:8000 [id ...]
//
// The site must be served at the address given (python3 -m http.server from
// the repository root). For each place in PACKS:
//   - the PDF is its pages printed in order (overview, then the elections
//     page where there is one, then the method page), with the site's print
//     stylesheet, merged by scripts/reports/merge_pdf.py;
//   - the deck has a cover listing the overview's numbered findings, then one
//     slide per section that has a chart: the section's computed finding
//     sentence as the title, the chart as drawn on the page, and the rest of
//     the finding in the speaker notes; then the page's own limits line.
// Every sentence is read off the rendered page, where it is computed from
// the published JSON, so the report and deck change when the data does.
// Re-run after any data change, as with the other reports.
import fs from 'fs';
import path from 'path';
import os from 'os';
import { execFileSync } from 'child_process';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
const { chromium } = await import(process.env.PLAYWRIGHT_CORE || 'playwright-core');
const pptxgen = require('pptxgenjs');

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', '..');
const BASE = (process.argv[2] || 'http://localhost:8000').replace(/\/$/, '');
const ONLY = process.argv.slice(3);
const OTHER = ['chhattisgarh', 'madhyapradesh', 'andhrapradesh', 'odisha', 'jharkhand', 'haryana', 'punjab', 'goa', 'manipur',
  'meghalaya', 'mizoram', 'nagaland', 'sikkim', 'arunachal', 'tripura', 'puducherry', 'chandigarh', 'lakshadweep', 'andaman', 'dnhdd'];
export const PACKS = [
  { id: 'rj', name: 'Rajasthan 2026', file: 'rajasthan-sir-2026', pages: ['rajasthan/'], method: ['rajasthan/method/'] },
  { id: 'up', name: 'Uttar Pradesh 2026', file: 'uttar-pradesh-sir-2026', pages: ['uttarpradesh/'], method: ['uttarpradesh/method/'] },
  { id: 'dl', name: 'Delhi 2026', file: 'delhi-sir-2026', pages: ['delhi/'], method: ['delhi/method/'] },
  { id: 'mh', name: 'Maharashtra 2026', file: 'maharashtra-sir-2026', pages: ['maharashtra/'], method: ['maharashtra/method/'] },
  { id: 'gj', name: 'Gujarat 2026', file: 'gujarat-sir-2026', pages: ['gujarat/', 'gujarat/elections/'], method: ['gujarat/method/'] },
  { id: 'uk', name: 'Uttarakhand 2026', file: 'uttarakhand-sir-2026', pages: ['uttarakhand/'], method: ['uttarakhand/method/'] },
  { id: 'as', name: 'Assam 2025-26', file: 'assam-special-revision-2026', pages: ['assam/'], method: ['assam/method/'] },
  { id: 'other', name: 'Every other state and union territory', file: 'other-states-sir-2026', pages: OTHER.map((s) => s + '/'), method: [] },
];

const W = 13.333, H = 7.5, M = 0.6;
const HEAD = 'Cambria', BODY = 'Calibri', INK = '16130F', MUTED = '5A534A', RED = 'B3261E', PAPER = 'F6F2EA';

async function open(browser, url, media) {
  const p = await browser.newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 2, colorScheme: 'light' });
  await p.route('**supabase.co/**', (r) => r.fulfill({ body: '[]', contentType: 'application/json' }));
  await p.addInitScript(() => { try { localStorage.setItem('otr-tour', '1'); localStorage.setItem('theme', 'light'); } catch (e) {} });
  await p.goto(BASE + '/' + url, { waitUntil: 'networkidle', timeout: 60000 });
  await p.waitForTimeout(1200);
  if (media) await p.emulateMedia({ media });
  // the sticky header, tab row and floating buttons would sit over a tall
  // chart when it is captured, so the page chrome is hidden first
  else await p.addStyleTag({ content: 'header.top,.nav-tabs,.secbar,.fabs,.band,.tour,nav.toc{display:none!important}' });
  return p;
}

// sections of a page that carry a chart: [{h2, finding, shot}]
async function sections(p, dir, tag) {
  const items = await p.evaluate(() => {
    const out = [];
    const art = document.querySelector('main') || document.body;
    const hs = [...art.querySelectorAll('h2')].filter((h) => !h.closest('.page-faq'));
    hs.forEach((h, i) => {
      const end = hs[i + 1];
      let n = h.nextElementSibling, box = null, finding = null;
      while (n && n !== end && !(end && n.contains(end))) {
        if (!box) box = n.querySelector && (n.querySelector('.vizbox svg') ? n.querySelector('.vizbox') : (n.querySelector('canvas') ? n.querySelector('canvas').closest('.panel') : null));
        if (!finding && n.matches && n.matches('p.finding') && n.textContent.trim()) finding = n;
        n = n.nextElementSibling;
      }
      if (box && box.getBoundingClientRect().height > 40 && !/^Find /.test(h.textContent.trim())) {
        box.setAttribute('data-pack', String(i));
        const b = finding && finding.querySelector('b');
        out.push({ i, h2: h.textContent.replace(/\s+/g, ' ').trim(), lead: b ? b.textContent.trim() : '',
          finding: finding ? finding.textContent.replace(/\s+/g, ' ').trim() : '' });
      }
    });
    return out;
  });
  for (const it of items) {
    it.shot = path.join(dir, tag + '-' + it.i + '.png');
    await p.locator('[data-pack="' + it.i + '"]').screenshot({ path: it.shot });
  }
  return items;
}

async function head(p) {
  return p.evaluate(() => ({
    title: (document.querySelector('.page-head h1') || {}).textContent || document.title,
    kicker: ((document.querySelector('.kicker') || {}).textContent || '').trim(),
    asof: ((document.querySelector('p.asof') || {}).textContent || '').trim(),
    findings: [...document.querySelectorAll('ol.summary > li')].map((li) => li.textContent.replace(/\s+/g, ' ').trim()).filter(Boolean),
    limits: ((document.querySelector('#shortNote') || {}).textContent || '').trim(),
  }));
}

function cover(pptx, title, sub, lines) {
  const s = pptx.addSlide();
  s.background = { color: PAPER };
  s.addText('SPECIAL INTENSIVE REVISION', { x: M, y: 0.5, w: W - 2 * M, h: 0.4, fontFace: BODY, fontSize: 12, color: RED, bold: true, charSpacing: 2 });
  s.addText(title, { x: M, y: 0.95, w: W - 2 * M, h: 1.0, fontFace: HEAD, fontSize: 40, color: INK, bold: true });
  if (sub) s.addText(sub, { x: M, y: 1.95, w: W - 2 * M, h: 0.5, fontFace: BODY, fontSize: 14, color: MUTED });
  if (lines.length) s.addText(lines.slice(0, 6).map((t, i) => ({ text: t, options: { bullet: { type: 'number' }, breakLine: i < Math.min(lines.length, 6) - 1 } })),
    { x: M, y: 2.6, w: W - 2 * M, h: 4.4, fontFace: BODY, fontSize: lines.join(' ').length > 900 ? 13 : 15, color: INK, valign: 'top', paraSpaceAfter: 8 });
}

function chartSlide(pptx, label, it) {
  const s = pptx.addSlide();
  s.background = { color: 'FFFFFF' };
  const title = it.lead || it.h2;
  s.addText(label.toUpperCase() + '  ·  ' + it.h2, { x: M, y: 0.3, w: W - 2 * M, h: 0.3, fontFace: BODY, fontSize: 10, color: RED, bold: true });
  s.addText(title, { x: M, y: 0.6, w: W - 2 * M, h: 1.15, fontFace: HEAD, fontSize: title.length > 160 ? 16 : title.length > 100 ? 19 : 22, color: INK, bold: true, valign: 'top' });
  const { width, height } = imageSize(it.shot);
  if (height / width > 0.75) {
    // a tall chart: the finding on the left, the chart at full height on the right
    const bw = 7.4, bh = H - 1.85 - 0.5;
    const k = Math.min(bw / width, bh / height);
    s.addImage({ path: it.shot, x: W - M - width * k, y: 1.85, w: width * k, h: height * k });
    if (it.finding && it.finding !== title) s.addText(it.finding.replace(title, '').trim(), { x: M, y: 1.85, w: W - 2 * M - width * k - 0.4, h: bh, fontFace: BODY, fontSize: 13, color: INK, valign: 'top' });
  } else {
    const bw = W - 2 * M, bh = H - 2.0 - 0.45;
    const k = Math.min(bw / width, bh / height);
    s.addImage({ path: it.shot, x: M + (bw - width * k) / 2, y: 1.85, w: width * k, h: height * k });
  }
  s.addText('Figures as published by the Chief Electoral Officer or the Election Commission; the method section of the report gives each source.',
    { x: M, y: H - 0.45, w: W - 2 * M, h: 0.3, fontFace: BODY, fontSize: 9, color: MUTED });
  if (it.finding) s.addNotes(it.finding);
}

function textSlide(pptx, label, title, lines) {
  const s = pptx.addSlide();
  s.background = { color: PAPER };
  s.addText(label.toUpperCase(), { x: M, y: 0.3, w: W - 2 * M, h: 0.3, fontFace: BODY, fontSize: 10, color: RED, bold: true });
  s.addText(title, { x: M, y: 0.6, w: W - 2 * M, h: 0.8, fontFace: HEAD, fontSize: 24, color: INK, bold: true });
  s.addText(lines.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < lines.length - 1 } })),
    { x: M, y: 1.6, w: W - 2 * M, h: H - 2.2, fontFace: BODY, fontSize: lines.join(' ').length > 1200 ? 12 : 15, color: INK, valign: 'top', paraSpaceAfter: 8 });
}

function imageSize(f) {
  const b = fs.readFileSync(f);
  return { width: b.readUInt32BE(16), height: b.readUInt32BE(20) };
}

const browser = await chromium.launch({ executablePath: process.env.CHROME });
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'pack-'));
for (const pk of PACKS.filter((x) => !ONLY.length || ONLY.includes(x.id))) {
  // the PDF
  const parts = [];
  for (const u of pk.pages.concat(pk.method)) {
    const p = await open(browser, u, 'print');
    const f = path.join(tmp, pk.id + '-' + parts.length + '.pdf');
    await p.pdf({ path: f, format: 'A4', printBackground: true, margin: { top: '14mm', bottom: '16mm', left: '12mm', right: '12mm' },
      displayHeaderFooter: true, headerTemplate: '<span></span>',
      footerTemplate: '<div style="font:8px system-ui,sans-serif;color:#5a534a;width:100%;padding:0 12mm;display:flex;justify-content:space-between"><span>' +
        pk.name + ', Special Intensive Revision</span><span class="pageNumber"></span></div>' });
    parts.push(f);
    await p.close();
  }
  const pdf = path.join(ROOT, 'reports', pk.file + '-report.pdf');
  execFileSync('python3', [path.join(ROOT, 'scripts', 'reports', 'merge_pdf.py'), pdf, pk.name + ', Special Intensive Revision'].concat(parts));

  // the deck
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_WIDE';
  pptx.title = pk.name + ', Special Intensive Revision';
  if (pk.id === 'other') {
    cover(pptx, pk.name, 'Twenty states and union territories, each from its Chief Electoral Officer\'s published figures', []);
    for (const u of pk.pages) {
      const p = await open(browser, u);
      const h = await head(p);
      const secs = await sections(p, tmp, pk.id + '-' + u.replace(/\W/g, ''));
      const place = h.kicker || u.replace('/', '');
      if (secs.length) chartSlide(pptx, place, Object.assign({}, secs[0], { lead: h.findings[0] || secs[0].lead, finding: h.findings.join(' ') }));
      else textSlide(pptx, place, h.title, h.findings.length ? h.findings : [h.asof || 'No figures published yet.']);
      await p.close();
    }
  } else {
    let first = true;
    for (const u of pk.pages) {
      const p = await open(browser, u);
      const h = await head(p);
      if (first) cover(pptx, pk.name, h.asof, h.findings);
      first = false;
      for (const it of await sections(p, tmp, pk.id + '-' + u.replace(/\W/g, ''))) chartSlide(pptx, pk.name + (u.includes('elections') ? ', elections' : ''), it);
      if (h.limits && u === pk.pages[pk.pages.length - 1]) textSlide(pptx, pk.name, 'What these figures cannot show', [h.limits]);
      await p.close();
    }
  }
  await pptx.writeFile({ fileName: path.join(ROOT, 'reports', pk.file + '-deck.pptx') });
  console.log('wrote reports/' + pk.file + '-report.pdf and -deck.pptx');
}
await browser.close();
fs.rmSync(tmp, { recursive: true, force: true });
