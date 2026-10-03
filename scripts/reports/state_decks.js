// Four slide decks, Tamil Nadu, Karnataka, West Bengal and Kerala 2026, from
// the published JSON. Charts are native PowerPoint charts, so they stay
// editable.
//
//   NODE_PATH=<dir with pptxgenjs> node scripts/reports/state_decks.js [outdir]
//
// Every figure is computed here from data/<state>/*.json, the same files the
// pages and scripts/reports/state_report.py read. The slide kit, cover,
// contents and closing slides are copied from decks.js, which builds its own
// three decks as soon as it is loaded and so cannot be required from here.
const fs = require('fs');
const path = require('path');
const pptxgen = require('pptxgenjs');

const ROOT = path.resolve(__dirname, '..', '..');
const OUT = path.resolve(process.argv[2] || path.join(ROOT, 'reports'));
const J = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, 'data', p), 'utf8'));

// ------------------------------------------------------------ formatting
const indian = (x) => {
  const s = String(Math.round(x)); const neg = s[0] === '-'; let d = neg ? s.slice(1) : s;
  if (d.length > 3) { let head = d.slice(0, -3); const tail = d.slice(-3); const parts = []; while (head.length > 2) { parts.unshift(head.slice(-2)); head = head.slice(0, -2); } if (head) parts.unshift(head); d = parts.join(',') + ',' + tail; }
  return (neg ? '-' : '') + d;
};
const pct = (x, k = 1) => x.toFixed(k) + '%';
const lakh = (x) => (x / 1e5).toFixed(1) + ' lakh';
const crore = (x) => (x / 1e7).toFixed(2) + ' crore';
const size = (x) => x >= 1e7 ? crore(x) : lakh(x);
const sum = (a, f) => a.reduce((s, x) => s + (typeof f === 'function' ? f(x) : x[f]), 0);
const andj = (xs) => xs.length === 1 ? xs[0] : xs.slice(0, -1).join(', ') + ' and ' + xs[xs.length - 1];
const d1 = (v) => v.toFixed(1);
const sg = (v) => (v > 0 ? '+' : '') + v.toFixed(1);
const REASON = 'A reason on the list is what the officer wrote down, and nobody checked it.';

// ------------------------------------------------------------ slide kit
// Titles are plain sentences that state what the slide shows, computed from
// the data like everything else. A small label above each title names the
// part of the analysis it comes from, matching the pages on the site.
const W = 13.333, Hh = 7.5, M = 0.6, TOP = 2.1, BOT = 6.85, CH = BOT - TOP;
const HEAD = 'Cambria', BODY = 'Calibri', INK = '1C2833', MUTED = '4D5B69', PAPER = 'FFFFFF', TINT = 'F4F6F7', GREY = '95A5A6';

function kit(pres, P) {
  const K = { n: 1, sections: [] };
  K.band = (s) => {
    const n = 40, tw = W / n;
    for (let i = 0; i < n; i++) s.addShape(pres.shapes.RECTANGLE, { x: i * tw, y: Hh - 0.12, w: tw, h: 0.12, fill: { color: P.band[i % P.band.length] }, line: { type: 'none' } });
  };
  // A content slide: section label, title, optional subtitle, footer.
  K.slide = (section, title, sub) => {
    const s = pres.addSlide(); K.n++;
    const last = K.sections[K.sections.length - 1];
    if (!last || last.name !== section) K.sections.push({ name: section, from: K.n });
    s.addText(section.toUpperCase(), { x: M, y: 0.28, w: W - 2 * M, h: 0.3, fontFace: BODY, fontSize: 11, bold: true, color: P.accent, charSpacing: 2, margin: 0, isTextBox: true });
    s.addText(title, { x: M, y: 0.58, w: W - 2 * M, h: 1.0, fontFace: HEAD, fontSize: 27, bold: true, color: P.dark, margin: 0, isTextBox: true, valign: 'top', fit: 'shrink' });
    if (sub) s.addText(sub, { x: M, y: 1.6, w: W - 2 * M, h: 0.4, fontFace: BODY, fontSize: 14, color: MUTED, margin: 0, isTextBox: true, valign: 'top' });
    s.addText(P.foot, { x: M, y: Hh - 0.5, w: W - 2 * M - 1, h: 0.3, fontFace: BODY, fontSize: 9, color: MUTED, margin: 0, isTextBox: true, valign: 'middle' });
    s.addText(String(K.n), { x: W - M - 0.8, y: Hh - 0.5, w: 0.8, h: 0.3, fontFace: BODY, fontSize: 9, color: MUTED, align: 'right', margin: 0, isTextBox: true });
    K.band(s);
    return s;
  };
  K.stat = (s, x, y, w, h, value, label, opt = {}) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: opt.fill || TINT }, line: { type: 'none' } });
    s.addText(value, { x: x + 0.2, y: y + 0.12, w: w - 0.4, h: h * 0.48, fontFace: HEAD, fontSize: opt.size || 28, bold: true, color: opt.color || P.accent, margin: 0, isTextBox: true, valign: 'bottom', fit: 'shrink' });
    s.addText(label, { x: x + 0.2, y: y + 0.14 + h * 0.48, w: w - 0.4, h: h * 0.52 - 0.24, fontFace: BODY, fontSize: opt.lsize || 12, color: opt.lcolor || MUTED, margin: 0, isTextBox: true, valign: 'top', fit: 'shrink' });
  };
  // A row or grid of stat cards across the content area.
  K.stats = (s, items, y = TOP, h = 1.55, cols = items.length, x0 = M, w0 = W - 2 * M) => {
    const gap = 0.25, cw = (w0 - gap * (cols - 1)) / cols;
    items.forEach((it, i) => K.stat(s, x0 + (i % cols) * (cw + gap), y + Math.floor(i / cols) * (h + gap), cw, h, it[0], it[1], it[2] || {}));
  };
  K.body = (s, text, x, y, w, h, size = 15, color = INK) => s.addText(text, { x, y, w, h, fontFace: BODY, fontSize: size, color, margin: 0, isTextBox: true, valign: 'top', paraSpaceAfter: 8, fit: 'shrink' });
  K.bullets = (s, items, x, y, w, h, size = 14) => s.addText(items.filter(Boolean).map((t, i, a) => ({ text: t, options: { bullet: true, breakLine: i < a.length - 1 } })), { x, y, w, h, fontFace: BODY, fontSize: size, color: INK, margin: 0, isTextBox: true, valign: 'top', paraSpaceAfter: 8, fit: 'shrink' });
  K.numbered = (s, items, x, y, w, h, size = 15) => s.addText(items.map((t, i) => ({ text: t, options: { bullet: { type: 'number' }, breakLine: i < items.length - 1 } })), { x, y, w, h, fontFace: BODY, fontSize: size, color: INK, margin: 0, isTextBox: true, valign: 'top', paraSpaceAfter: 10, fit: 'shrink' });
  K.box = (s, text, x, y, w, h, size = 14) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1, fill: { color: P.soft }, line: { type: 'none' } });
    s.addText(text, { x: x + 0.25, y: y + 0.18, w: w - 0.5, h: h - 0.36, fontFace: BODY, fontSize: size, color: INK, margin: 0, isTextBox: true, valign: 'top', fit: 'shrink' });
  };
  // Question and answer, four to a slide.
  K.qa = (s, qs) => {
    const cw = (W - 2 * M - 0.3) / 2, ch = (CH - 0.25) / 2;
    qs.forEach(([q, a], i) => {
      const x = M + (i % 2) * (cw + 0.3), y = TOP - 0.35 + Math.floor(i / 2) * (ch + 0.25);
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: cw, h: ch + 0.1, rectRadius: 0.08, fill: { color: TINT }, line: { type: 'none' } });
      s.addText([{ text: q, options: { bold: true, color: P.dark, fontSize: 14, breakLine: true } }, { text: a, options: { color: INK, fontSize: 12 } }],
        { x: x + 0.22, y: y + 0.15, w: cw - 0.44, h: ch - 0.2, fontFace: BODY, margin: 0, isTextBox: true, valign: 'top', paraSpaceAfter: 5, fit: 'shrink' });
    });
  };
  K.table = (s, head, rows, x, y, w, colW, fs = 11, left = [0]) => {
    const al = (i) => left.includes(i) ? 'left' : 'right';
    const hdr = head.map((h, i) => ({ text: h, options: { bold: true, color: 'FFFFFF', fill: { color: P.dark }, align: al(i) } }));
    const body = rows.map((r, k) => r.map((v, i) => ({ text: String(v), options: { align: al(i), fill: { color: k % 2 ? TINT : PAPER } } })));
    s.addTable([hdr, ...body], { x, y, w, colW, fontFace: BODY, fontSize: fs, color: INK, border: { type: 'solid', pt: 0.5, color: 'D5D8DC' }, rowH: 0.28, margin: 0.05 });
  };
  K.chart = (o = {}) => Object.assign({
    catAxisLabelColor: MUTED, valAxisLabelColor: MUTED, catAxisLabelFontFace: BODY, valAxisLabelFontFace: BODY, catAxisLabelFontSize: 11, valAxisLabelFontSize: 10,
    valGridLine: { color: 'E1E5E8', size: 0.5 }, catGridLine: { style: 'none' }, showLegend: false, dataLabelFontFace: BODY, dataLabelFontSize: 10, dataLabelColor: INK,
    titleFontFace: BODY, titleColor: INK, titleFontSize: 12, legendFontFace: BODY, legendFontSize: 11, legendPos: 'b',
  }, o);
  // Chart on the left, notes on the right: the commonest layout.
  K.left = { x: M, y: TOP, w: 7.7, h: CH };
  K.right = (s, items, size = 14) => K.bullets(s, items, 8.65, TOP + 0.1, W - M - 8.65, CH - 0.1, size);
  K.contents = (s) => {
    const rows = K.sections.map((x, i) => { const to = K.sections[i + 1] ? K.sections[i + 1].from - 1 : K.n; return [x.name, to > x.from ? x.from + '–' + to : String(x.from)]; });
    const half = Math.ceil(rows.length / 2);
    [rows.slice(0, half), rows.slice(half)].forEach((col, c) => s.addText(col.map((r, i) => ({ text: r[0] + '   ' + r[1], options: { breakLine: i < col.length - 1 } })),
      { x: M + c * 6.2, y: 1.6, w: 5.9, h: 4.9, fontFace: BODY, fontSize: 17, color: INK, margin: 0, isTextBox: true, valign: 'top', paraSpaceAfter: 12 }));
  };
  return K;
}

function cover(pres, K, P, kicker, title, sub, stats) {
  const s = pres.addSlide(); s.background = { color: P.dark };
  s.addText(kicker.toUpperCase(), { x: M, y: 0.7, w: 11, h: 0.4, fontFace: BODY, fontSize: 13, bold: true, color: P.light, charSpacing: 3, margin: 0, isTextBox: true });
  s.addText(title, { x: M, y: 1.15, w: W - 2 * M, h: 1.4, fontFace: HEAD, fontSize: 38, bold: true, color: 'FFFFFF', margin: 0, isTextBox: true, valign: 'top', fit: 'shrink' });
  s.addText(sub, { x: M, y: 2.6, w: W - 2 * M - 1, h: 0.8, fontFace: BODY, fontSize: 17, color: P.light, margin: 0, isTextBox: true, valign: 'top' });
  const cw = (W - 2 * M - 0.3 * (stats.length - 1)) / stats.length;
  stats.forEach((st, i) => K.stat(s, M + i * (cw + 0.3), 3.75, cw, 1.9, st[0], st[1], { fill: P.darker, color: 'FFFFFF', lcolor: P.light, size: 30, lsize: 12.5 }));
  s.addText('PinPoint Ventures', { x: M, y: 6.3, w: 8, h: 0.4, fontFace: BODY, fontSize: 13, color: P.light, margin: 0, isTextBox: true });
  K.band(s);
  return s;
}

function contentsSlide(pres, K, P) {
  const s = pres.addSlide(); K.n++;
  s.addText('Contents', { x: M, y: 0.5, w: W - 2 * M, h: 0.8, fontFace: HEAD, fontSize: 30, bold: true, color: P.dark, margin: 0, isTextBox: true });
  K.band(s);
  return s; // filled once every section exists
}

function closing(pres, K, P, head, lines) {
  const s = pres.addSlide(); K.n++; s.background = { color: P.dark };
  s.addText(head, { x: M, y: 1.4, w: W - 2 * M, h: 1.2, fontFace: HEAD, fontSize: 34, bold: true, color: 'FFFFFF', margin: 0, isTextBox: true, valign: 'top' });
  s.addText(lines.map((t, i) => ({ text: t, options: { breakLine: i < lines.length - 1 } })), { x: M, y: 3.0, w: W - 2 * M, h: 2.6, fontFace: BODY, fontSize: 17, color: P.light, margin: 0, isTextBox: true, valign: 'top', paraSpaceAfter: 10 });
  K.band(s);
}

// ------------------------------------------------------------ shared slides
// A waterfall drawn with shapes: totals in navy, falls in red, rises in teal.
// The bars start above zero, as on the pages, and each carries its count.
function waterfall(pres, s, steps, floor, box) {
  const top = Math.max(...steps.map((x) => x[1])) * 1.03, n = steps.length, bw = box.w / n, lab = 0.75;
  const H = box.h - lab - 0.3, y = (v) => box.y + 0.3 + H * (1 - (v - floor) / (top - floor));
  let run = 0;
  steps.forEach(([name, v, kind], i) => {
    let lo, hi, col;
    if (kind === 'total') { lo = floor; hi = v; col = '1F618D'; run = v; }
    else if (kind === 'down') { lo = run - v; hi = run; col = 'C0392B'; run -= v; }
    else { lo = Math.min(run, run + v); hi = Math.max(run, run + v); col = v >= 0 ? '17A589' : 'C0392B'; run += v; }
    const x = box.x + i * bw + bw * 0.15, w = bw * 0.7;
    s.addShape(pres.shapes.RECTANGLE, { x, y: y(hi), w, h: Math.max(y(lo) - y(hi), 0.02), fill: { color: col }, line: { type: 'none' } });
    const t = kind === 'total' ? indian(v) : (kind === 'up' && v >= 0 ? '+' : '−') + indian(Math.abs(v));
    s.addText(t, { x: box.x + i * bw, y: y(hi) - 0.3, w: bw, h: 0.28, fontFace: BODY, fontSize: 10, color: INK, align: 'center', margin: 0, isTextBox: true, fit: 'shrink' });
    s.addText(name, { x: box.x + i * bw, y: box.y + box.h - lab, w: bw, h: lab, fontFace: BODY, fontSize: 10, color: MUTED, align: 'center', valign: 'top', margin: 0, isTextBox: true, fit: 'shrink' });
  });
  s.addShape(pres.shapes.LINE, { x: box.x, y: box.y + box.h - lab - 0.02, w: box.w, h: 0, line: { color: GREY, width: 0.75 } });
}

// Seats by how many times the margin the count is.
const BINS = [[-1e9, 1, 'under 1×'], [1, 2, '1 to 2×'], [2, 5, '2 to 5×'], [5, 10, '5 to 10×'], [10, 1e9, '10× or more']];
function marginSlide(pres, K, P, rows, count, title, sub, what) {
  const s = K.slide('The 2026 election', title, sub);
  const vals = BINS.map(([a, b]) => rows.filter((r) => count(r) / r.margin >= a && count(r) / r.margin < b).length);
  s.addChart(pres.charts.BAR, [{ name: 'Seats', labels: BINS.map((b) => b[2]), values: vals }],
    K.chart(Object.assign({}, K.left, { barDir: 'col', chartColors: BINS.map((b) => b[0] >= 1 ? P.accent : GREY), showValue: true, dataLabelPosition: 'outEnd', valAxisHidden: true, catAxisTitle: what + ' as a multiple of the margin', showCatAxisTitle: true, catAxisTitleFontSize: 11, catAxisTitleColor: MUTED })));
  return [s, vals];
}

function partyTable(K, s, rows, key, head) {
  K.table(s, ['Party that won', 'Seats', head, 'Against own district', 'Over the margin'],
    rows.map((w) => [w.party, String(w.seats), d1(w[key]), sg(w.vs_district), String(w.over_margin)]), M, TOP - 0.1, 7.6, [2.0, 1.0, 1.6, 1.6, 1.4], 12);
}

function deck(title, P) {
  const pres = new pptxgen(); pres.layout = 'LAYOUT_WIDE'; pres.author = 'PinPoint Ventures'; pres.title = title;
  return [pres, kit(pres, P)];
}
const band = ['C0392B', 'E67E22', '27AE60', '1F618D', '8E44AD'];

// ============================================================ TAMIL NADU
function tamilnadu() {
  const S = J('tamilnadu/summary.json'), D = J('tamilnadu/districts.json'), A = J('tamilnadu/constituencies.json');
  const C = S.chennai, WN = Object.fromEntries(S.winners.map((w) => [w.party, w])), low = D[D.length - 1];
  const P = { dark: '6E3420', darker: '552818', accent: '8E442B', light: 'F2DCCB', soft: 'FBEFE8', band, foot: 'Tamil Nadu SIR 2026 · PinPoint Ventures · totals only, never names or EPIC numbers' };
  const [pres, K] = deck('Tamil Nadu SIR 2026', P);
  const CHN = A.filter((a) => a.district === 'Chennai').sort((a, b) => b.per_100 - a.per_100);

  cover(pres, K, P, 'Special Intensive Revision · Tamil Nadu 2026', 'The revision left ' + lakh(S.removed) + ' names off Tamil Nadu\'s draft roll',
    'Where the names were removed, on what recorded reason, what the final roll put back, and how the removals compare with the 2026 result',
    [[indian(S.removed), 'names left off the draft roll of 19 December 2025'], [d1(S.per_100), 'of every 100 electors on the roll before'], [S.over_margin + ' of ' + S.acs, 'seats where more names were left off than the 2026 margin'], [d1(C.per_100), 'removed per 100 electors in Chennai']])
    .addNotes('Every figure in this deck is computed from the Chief Electoral Officer\'s tables and the 2026 results, the same data the website and the full report use. No name or EPIC number is published.');
  const toc = contentsSlide(pres, K, P);

  let s = K.slide('In short', 'The revision removed ' + d1(S.per_100) + ' of every 100 electors, and more than the winning margin in ' + S.over_margin + ' of ' + S.acs + ' seats', 'Five findings, each computed from the published tables');
  K.numbered(s, [
    lakh(S.removed) + ' names were left off Tamil Nadu\'s draft roll, ' + d1(S.per_100) + ' of every 100 electors on the roll before the revision.',
    'In ' + S.over_margin + ' of the ' + S.acs + ' constituencies, more names were left off than the 2026 winning margin, large enough to decide the seat. Counting only the living removed at each seat\'s turnout, ' + S.could_change + '.',
    pct(S.shares.shifted_absent) + ' were entered as shifted or absent, ' + pct(S.shares.dead) + ' as dead and ' + pct(S.shares.multiple) + ' as enrolled in more than one place.',
    'Chennai lost ' + d1(C.per_100) + ' of every 100 electors. It holds ' + pct(S.chennai_share_of_roll) + ' of the roll and ' + pct(S.chennai_share_of_removed) + ' of the names removed.',
    'The final roll was ' + lakh(S.added_net) + ' larger than the draft, at most ' + pct(S.made_up_pct) + ' of the names removed, and it includes new voters.',
  ], M, TOP - 0.2, W - 2 * M, CH - 0.6, 16);
  K.body(s, 'No split of the removals by sex or age has been published. ' + REASON, M, TOP + CH - 0.5, W - 2 * M, 0.5, 12, MUTED);

  s = K.slide('The roll', 'The roll fell from ' + crore(S.before) + ' to ' + crore(S.draft) + ' at the draft, and the final roll held ' + crore(S.final), 'The state\'s roll, step by step, to the final roll of 23 February 2026');
  waterfall(pres, s, [['Roll before the revision', S.before, 'total'], ['Dead', S.dead, 'down'], ['Shifted or absent', S.shifted_absent, 'down'], ['Enrolled in more than one place', S.multiple, 'down'], ['Draft roll', S.draft, 'total'], ['Net change after the draft', S.added_net, 'up'], ['Final roll', S.final, 'total']],
    Math.floor(S.draft * 0.8 / 1e5) * 1e5, { x: M, y: TOP, w: W - 2 * M, h: CH });
  s.addNotes('The bars start above zero so that the changes can be seen. The roll before the revision is the draft plus the names left off, because no constituency table of that roll was published. ' + REASON);

  s = K.slide('By district', 'Chennai lost ' + d1(D[0].per_100) + ' of every 100 electors, against ' + d1(S.per_100) + ' for the state', 'Names left off the draft roll per 100 electors on the roll before the revision, by district');
  s.addChart(pres.charts.BAR, [{ name: 'Per 100', labels: D.map((d) => d.district), values: D.map((d) => d.per_100) }],
    K.chart(Object.assign({}, K.left, { y: TOP - 0.3, h: CH + 0.3, barDir: 'bar', chartColors: D.map((d) => d.district === 'Chennai' ? 'C0392B' : '1F618D'), showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0', dataLabelFontSize: 7, valAxisHidden: true, catAxisLabelFontSize: 7, catAxisOrientation: 'maxMin' })));
  K.right(s, ['The next four are ' + andj(D.slice(1, 5).map((d) => d.district + ' (' + d1(d.per_100) + ')')) + '.', low.district + ' lost the fewest, ' + d1(low.per_100) + '.', 'By constituency the rate runs from ' + d1(S.rate_min_v) + ' in ' + S.rate_min + ' to ' + d1(S.rate_max_v) + ' in ' + S.rate_max + '.']);

  const byDead = D.slice().sort((a, b) => b.dead_share - a.dead_share)[0], top12 = D.slice(0, 12);
  s = K.slide('The reasons', pct(S.shares.shifted_absent, 0) + ' of the names were entered as shifted or absent and ' + pct(S.shares.dead, 0) + ' as dead', 'Share of each district\'s removals by the reason entered, the twelve districts with the highest rates');
  s.addChart(pres.charts.BAR, [['dead', 'Dead'], ['shifted_absent', 'Shifted or absent'], ['multiple', 'In more than one place']].map(([k, n]) => ({ name: n, labels: top12.map((d) => d.district), values: top12.map((d) => +(100 * d[k] / d.removed).toFixed(1)) })),
    K.chart(Object.assign({}, K.left, { barDir: 'bar', barGrouping: 'percentStacked', chartColors: [GREY, '1F618D', 'D4AC0D'], showLegend: true, valAxisHidden: true, catAxisOrientation: 'maxMin', catAxisLabelFontSize: 10 })));
  K.right(s, ['Where more names were removed, more were marked shifted or absent (rank correlation ' + S.rho_rate_shifted.toFixed(2) + ' across constituencies).', 'In Chennai ' + pct(C.shifted_share) + ' were entered as shifted or absent.', 'The share entered as dead is highest in ' + byDead.district + ', ' + pct(byDead.dead_share) + '.', REASON], 13);

  s = K.slide('Chennai', 'Every one of Chennai\'s ' + CHN.length + ' constituencies lost more than ' + Math.floor(CHN[CHN.length - 1].per_100) + ' of every 100 electors', 'Removed per 100 electors, by reason');
  s.addChart(pres.charts.BAR, [['dead', 'Dead'], ['shifted_absent', 'Shifted or absent'], ['multiple', 'In more than one place']].map(([k, n]) => ({ name: n, labels: CHN.map((a) => a.name), values: CHN.map((a) => +(100 * a[k] / a.before).toFixed(1)) })),
    K.chart(Object.assign({}, K.left, { barDir: 'bar', barGrouping: 'stacked', chartColors: [GREY, '1F618D', 'D4AC0D'], showLegend: true, catAxisOrientation: 'maxMin', catAxisLabelFontSize: 9, valAxisLabelFontSize: 9 })));
  K.right(s, [CHN[0].name + ' lost ' + d1(CHN[0].per_100) + ', the most of any seat in the state.', 'Chennai holds ' + pct(S.chennai_share_of_roll) + ' of the roll and ' + pct(S.chennai_share_of_removed) + ' of the names removed, ' + indian(C.removed) + ' in all.', 'At the final roll Chennai was still ' + d1(C.net_per_100) + ' per 100 smaller than before.']);

  const tw = A.reduce((t, a) => [t[0] + a.draft_women, t[1] + a.final_women, t[2] + a.draft, t[3] + a.final], [0, 0, 0, 0]);
  s = K.slide('Women', 'Women\'s share of the removals cannot be counted, because no split by sex has been published', 'What can be counted is the change after the draft');
  K.stats(s, [[pct(100 * tw[0] / tw[2]), 'women\'s share of the draft roll'], [pct(100 * (tw[1] - tw[0]) / (tw[3] - tw[2])), 'women\'s share of the net rise to the final roll'], [pct(S.women_final_pct), 'women\'s share of the final roll']], TOP, 1.8);
  K.body(s, 'The Chief Electoral Officer has published no split of the names left off by sex, and no roll by sex from before the revision. The rise after the draft counts new voters as well as names put back, so it does not say how many women\'s names were restored.', M, TOP + 2.2, W - 2 * M, 2, 16);

  const t12 = D.slice(0, 12);
  s = K.slide('After the draft', 'The final roll put back at most ' + pct(S.made_up_pct) + ' of the names removed, and the roll is still ' + lakh(S.net_fall) + ' smaller', 'Per 100 electors, removed at the draft and the fall that remains at the final roll, the twelve districts with the highest rates');
  s.addChart(pres.charts.BAR, [{ name: 'At the draft', labels: t12.map((d) => d.district), values: t12.map((d) => d.per_100) }, { name: 'At the final roll', labels: t12.map((d) => d.district), values: t12.map((d) => d.net_per_100) }],
    K.chart(Object.assign({}, K.left, { barDir: 'bar', barGrouping: 'clustered', chartColors: ['AEB6BF', P.accent], showLegend: true, showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0', dataLabelFontSize: 8, valAxisHidden: true, catAxisOrientation: 'maxMin', catAxisLabelFontSize: 10 })));
  K.right(s, ['The final roll is ' + lakh(S.added_net) + ' larger than the draft.', 'For the state the fall is ' + d1(S.net_per_100) + ' of every 100 electors at the final roll, from ' + d1(S.per_100) + ' at the draft.', 'The rise includes new voters, so it is the most that can have been restored.']);

  const [s1] = marginSlide(pres, K, P, A, (a) => a.removed, 'In ' + S.over_margin + ' of ' + S.acs + ' constituencies, more names were left off than the 2026 winning margin', 'Seats by the names left off the draft as a multiple of the 2026 margin', 'Names left off');
  K.right(s1, ['In those seats the removals were large enough to decide the result.', 'Whether they did depends on how those people would have voted, and the lists cannot show that.', 'The removal rate and the margin as a share of votes rise together a little (rank correlation ' + S.rho_rate_margin.toFixed(2) + '), so the seats that lost most were not the closest contests.'], 13.5);
  s1.addNotes('No list of removals can show intent. Over the margin means large enough to decide a seat, and says nothing about whether the removals did.');

  s = K.slide('The 2026 election', 'Counting only the living removed at each seat\'s turnout, they outnumber the margin in ' + S.could_change + ' seats', 'Three ways of setting the removals against the margin, from the widest to the narrowest');
  K.stats(s, [[S.over_margin + ' of ' + S.acs, 'every name left off the draft'], [S.net_over_margin + ' of ' + S.acs, 'the net fall at the final roll'], [S.could_change + ' of ' + S.acs, 'the names not marked dead, at the seat\'s 2026 turnout']], TOP, 1.9);
  K.body(s, 'In the other ' + (S.acs - S.could_change) + ' seats, the runner-up could not have won even if every living person removed had voted for the runner-up at the seat\'s turnout. Even the narrowest count assumes all of them would have, which nobody can know.', M, TOP + 2.3, W - 2 * M, 2, 16);

  s = K.slide('The 2026 election', 'Seats won by TVK lost ' + d1(WN.TVK.per_100) + ' per 100 and DMK seats ' + d1(WN.DMK.per_100) + ', and against their own districts they differ by ' + Math.abs(WN.TVK.vs_district - WN.DMK.vs_district).toFixed(1) + ' points', 'Names removed per 100 electors in the seats each party won, and against the rate of each seat\'s own district');
  partyTable(K, s, S.winners, 'per_100', 'Removed per 100');
  K.right(s, ['TVK won most of the city seats, and the city seats lost the most names.', 'Against their own districts, TVK seats come out at ' + sg(WN.TVK.vs_district) + ', DMK seats at ' + sg(WN.DMK.vs_district) + ' and AIADMK seats at ' + sg(WN.AIADMK.vs_district) + '.', S.changed_hands + ' of the ' + S.acs + ' seats changed hands from 2021.'], 13);
  s.addNotes('Against own district is each seat\'s rate less its district\'s, averaged over the party\'s seats. A minus means fewer removals than the district as a whole.');

  s = K.slide('Limits', 'What the tables show, and what they cannot show');
  K.box(s, 'How many names were left off the draft in every constituency, on what recorded reason, what the final roll put back, and how those numbers compare with the 2026 margins.', M, TOP - 0.4, 5.95, 2.3, 15);
  K.box(s, 'Whether women, the old or the young were removed more often, because no split by sex or age has been published. Whether each removal was right, or how anyone removed would have voted.', 6.78, TOP - 0.4, 5.95, 2.3, 15);
  K.body(s, REASON + ' No list of removals can show intent.', M, TOP + 2.2, W - 2 * M, 1.5, 16);

  s = K.slide('What the Election Commission should do', 'Publish who was removed, and on what basis');
  K.numbered(s, [
    'Publish the names removed by sex and age for every constituency, with the roll before the revision by sex.',
    'Publish the basis for the ' + lakh(S.shifted_absent) + ' entries marked shifted or absent, including the visits made and the notice given.',
    'Publish how many of those added for the final roll had been left off the draft.',
    'Explain why Chennai lost ' + d1(C.per_100) + ' of every 100 electors, more than twice the state\'s rate.',
    'Publish the roll the election was held on, constituency by constituency.',
  ], M, TOP - 0.3, W - 2 * M, CH + 0.3, 17);

  s = K.slide('Method', 'Where the figures come from');
  K.bullets(s, [
    'The names left off the draft roll, by constituency and reason, and the draft and final rolls by constituency and sex, are the Chief Electoral Officer\'s tables. They add up to the state totals published with them.',
    'The roll before the revision is the draft plus the names left off, ' + indian(S.before) + ' in all, because no constituency table of it was published.',
    'The 2026 result is from the Election Commission\'s result pages, and turnout is votes over the final roll. The 2021 result is from the Commission\'s statistical report, through a published compilation of it.',
    'Each seat\'s rate is also set against its own district\'s, because Chennai and the districts around it removed far more names than the rest of the state.',
    'Only counts are published, never a name, EPIC number or address.',
  ], M, TOP - 0.3, W - 2 * M, CH + 0.3, 15);

  closing(pres, K, P, 'The full analysis', ['The constituency map, every district and constituency, and the full report are published online alongside this deck.', 'PinPoint Ventures']);
  K.contents(toc);
  return pres.writeFile({ fileName: path.join(OUT, 'tamil-nadu-sir-2026-deck.pptx') });
}

// ============================================================ KARNATAKA
function karnataka() {
  const S = J('karnataka/summary.json'), D = J('karnataka/districts.json'), B = S.bengaluru, R = S.rest;
  const P = { dark: '17533F', darker: '103D2E', accent: '1E6B52', light: 'CFE8DE', soft: 'EAF5F0', band, foot: 'Karnataka SIR 2026 · PinPoint Ventures · totals only, never names or EPIC numbers' };
  const [pres, K] = deck('Karnataka SIR 2026', P);
  const BL = D.filter((d) => d.bengaluru), nxt = D.filter((d) => !d.bengaluru), low = D[D.length - 1];
  const RK = [['shifted', 'Shifted', '1F618D'], ['absent', 'Absent', 'C0392B'], ['dead', 'Dead', GREY], ['duplicate', 'Already enrolled', 'D4AC0D'], ['other', 'Other', '8E7CC3']];

  cover(pres, K, P, 'Special Intensive Revision · Karnataka 2026', 'The revision left ' + crore(S.removed) + ' names off Karnataka\'s draft roll',
    'District by district, on what recorded reason, and how the roll stood while notices were still being heard',
    [[indian(S.removed), 'names left off the draft roll of 24 August 2026'], [d1(S.per_100), 'of every 100 electors on the roll of 16 June'], [pct(B.share_of_removed), 'of the names removed were in Bengaluru'], [pct(S.made_up_pct), 'of the names removed back by 25 September']])
    .addNotes('Every figure is computed from the Chief Electoral Officer\'s district tables. Nothing has been published by assembly constituency, so there is no comparison with election margins. The final roll is due on 27 October 2026.');
  const toc = contentsSlide(pres, K, P);

  let s = K.slide('In short', 'The revision removed ' + d1(S.per_100) + ' of every 100 electors, and ' + d1(B.per_100) + ' in Bengaluru', 'Four findings, each computed from the published tables');
  K.numbered(s, [
    crore(S.removed) + ' names were left off Karnataka\'s draft roll, ' + d1(S.per_100) + ' of every 100 electors on the roll before the revision.',
    'Bengaluru\'s four districts lost ' + d1(B.per_100) + ' of every 100 electors. They hold ' + pct(B.share_of_roll) + ' of the roll and ' + pct(B.share_of_removed) + ' of the names removed.',
    pct(S.shares.shifted) + ' were entered as shifted, ' + pct(S.shares.absent) + ' as absent, ' + pct(S.shares.dead) + ' as dead and ' + pct(S.shares.duplicate) + ' as already enrolled elsewhere.',
    'By 25 September the roll had risen by ' + indian(S.added_sep) + ' since the draft, ' + pct(S.made_up_pct) + ' of the names removed. In Bengaluru it rose by ' + indian(B.added_sep) + '.',
  ], M, TOP - 0.2, W - 2 * M, CH - 0.6, 17);
  K.body(s, 'Published by district only, with no split by sex. ' + REASON, M, TOP + CH - 0.5, W - 2 * M, 0.5, 12, MUTED);

  s = K.slide('The roll', 'The roll fell from ' + crore(S.before) + ' on 16 June to ' + crore(S.draft) + ' at the draft', 'The state\'s roll, step by step, to 25 September 2026, while notices were still being heard');
  waterfall(pres, s, [['Roll of 16 June', S.before, 'total'], ['Shifted', S.reasons.shifted, 'down'], ['Dead', S.reasons.dead, 'down'], ['Absent', S.reasons.absent, 'down'], ['Already enrolled', S.reasons.duplicate, 'down'], ['Other', S.reasons.other, 'down'], ['Draft roll', S.draft, 'total'], ['Net change after the draft', S.added_sep, 'up'], ['Roll of 25 September', S.sep, 'total']],
    Math.floor(S.draft * 0.8 / 1e6) * 1e6, { x: M, y: TOP, w: W - 2 * M, h: CH });
  s.addNotes('The bars start above zero so that the changes can be seen. The final roll is due on 27 October 2026. ' + REASON);

  s = K.slide('By district', 'Bengaluru\'s four districts lost between ' + d1(Math.min(...BL.map((d) => d.per_100))) + ' and ' + d1(D[0].per_100) + ' of every 100 electors', 'Names left off the draft roll per 100 electors on the roll of 16 June, by election district');
  s.addChart(pres.charts.BAR, [{ name: 'Per 100', labels: D.map((d) => d.district), values: D.map((d) => d.per_100) }],
    K.chart(Object.assign({}, K.left, { y: TOP - 0.3, h: CH + 0.3, barDir: 'bar', chartColors: D.map((d) => d.bengaluru ? 'C0392B' : '1F618D'), showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0', dataLabelFontSize: 7, valAxisHidden: true, catAxisLabelFontSize: 7.5, catAxisOrientation: 'maxMin' })));
  K.right(s, ['The state lost ' + d1(S.per_100) + ' per 100.', 'Outside Bengaluru the highest is ' + nxt[0].district + ' at ' + d1(nxt[0].per_100) + '.', low.district + ' lost the fewest, ' + d1(low.per_100) + '.', 'Bangalore Rural is outside Bengaluru\'s four districts.']);

  const t12 = D.slice(0, 12);
  s = K.slide('The reasons', pct(S.shares.shifted, 0) + ' of the names were entered as shifted and ' + pct(S.shares.absent, 0) + ' as absent', 'Share of each district\'s removals by the reason entered, the twelve districts with the highest rates');
  s.addChart(pres.charts.BAR, RK.map(([k, n]) => ({ name: n, labels: t12.map((d) => d.district), values: t12.map((d) => d.shares[k]) })),
    K.chart(Object.assign({}, K.left, { barDir: 'bar', barGrouping: 'percentStacked', chartColors: RK.map((r) => r[2]), showLegend: true, valAxisHidden: true, catAxisOrientation: 'maxMin', catAxisLabelFontSize: 10 })));
  K.right(s, [pct(S.shares.dead) + ' were entered as dead and ' + pct(S.shares.duplicate) + ' as already enrolled.', 'The more names a district removed, the larger the share marked shifted or absent (rank correlation ' + S.rho_rate_shifted.toFixed(2) + ').', 'The share entered as dead is highest in ' + S.dead_max.district + ', ' + pct(S.dead_max.share) + '.', REASON], 13);

  s = K.slide('Bengaluru', 'Bengaluru holds ' + pct(B.share_of_roll) + ' of Karnataka\'s roll and ' + pct(B.share_of_removed) + ' of the names removed', 'Bangalore Urban and the North, Central and South districts of the city corporation');
  K.stats(s, [[lakh(B.removed), 'names removed in Bengaluru'], [d1(B.per_100), 'per 100 electors, against ' + d1(R.per_100) + ' elsewhere'], [pct(B.shifted_absent_share), 'entered as shifted or absent, against ' + pct(R.shifted_absent_share) + ' elsewhere'], [pct(B.dead_share), 'entered as dead, against ' + pct(R.dead_share) + ' elsewhere']], TOP, 1.9, 4);
  K.body(s, 'By 25 September Bengaluru\'s roll had risen by ' + indian(B.added_sep) + ' since the draft, against ' + lakh(B.removed) + ' names removed. In the rest of the state the rise came to ' + pct(R.made_up_pct) + ' of the names removed.', M, TOP + 2.3, W - 2 * M, 1.8, 16);

  s = K.slide('Women', 'Women\'s share of the removals cannot be counted, because the roll of 16 June has no count by sex', 'What can be counted is women\'s share of each later roll');
  K.stats(s, [[pct(S.women_draft_pct), 'women\'s share of the draft roll'], [pct(S.women_sep_pct), 'women\'s share of the roll of 25 September']], TOP, 1.8);
  K.body(s, 'The names left off are not split by sex. These two figures cannot show whether women were left off more often than men.', M, TOP + 2.2, W - 2 * M, 1.6, 16);

  s = K.slide('After the draft', 'By 25 September only ' + pct(S.made_up_pct) + ' of the names removed had come back, and ' + pct(B.made_up_pct, 2) + ' in Bengaluru', 'Removed at the draft and the fall left on 25 September, per 100 electors, the twelve districts with the highest rates');
  s.addChart(pres.charts.BAR, [{ name: 'At the draft', labels: t12.map((d) => d.district), values: t12.map((d) => d.per_100) }, { name: 'On 25 September', labels: t12.map((d) => d.district), values: t12.map((d) => d.net_per_100) }],
    K.chart(Object.assign({}, K.left, { barDir: 'bar', barGrouping: 'clustered', chartColors: ['AEB6BF', P.accent], showLegend: true, showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0', dataLabelFontSize: 8, valAxisHidden: true, catAxisOrientation: 'maxMin', catAxisLabelFontSize: 10 })));
  K.right(s, ['The roll rose by ' + indian(S.added_sep) + ' after the draft, against ' + crore(S.removed) + ' names removed.', 'The rise includes new voters, so it is the most that could have been restored.', 'The final roll is due on 27 October 2026 and may change this.']);

  s = K.slide('Limits', 'What the tables show, and what they cannot show');
  K.box(s, 'How many names were left off the draft in each of the 34 election districts, on what recorded reason, and how the roll stood on 25 September.', M, TOP - 0.4, 5.95, 2.3, 15);
  K.box(s, 'Which constituencies lost the most names, or how the removals compare with the 2023 margins, because nothing was published by constituency. Whether women, the old or the young were removed more often.', 6.78, TOP - 0.4, 5.95, 2.3, 15);
  K.body(s, REASON + ' The tables show where names were removed and cannot show why.', M, TOP + 2.2, W - 2 * M, 1.5, 16);

  s = K.slide('What the Election Commission should do', 'Publish the revision by constituency and by sex before the final roll');
  K.numbered(s, [
    'Publish the names removed by assembly constituency and polling station, with the reason.',
    'Publish the names removed by sex and age, with the roll of 16 June by sex.',
    'Publish the basis for the ' + lakh(S.reasons.shifted + S.reasons.absent) + ' entries marked shifted or absent.',
    'Explain why Bengaluru lost ' + d1(B.per_100) + ' of every 100 electors, against ' + d1(R.per_100) + ' in the rest of the state.',
    'Publish with the final roll how many of those added had been left off the draft.',
  ], M, TOP - 0.3, W - 2 * M, CH + 0.3, 17);

  s = K.slide('Method', 'Where the figures come from');
  K.bullets(s, [
    'The names left off the draft roll of 24 August 2026, by election district and under five reasons, are the Chief Electoral Officer\'s table. The ' + S.districts + ' district rows add up to the state row, ' + indian(S.removed) + ' out of ' + indian(S.before) + '.',
    'The roll of 25 September 2026, by district and sex, is from the press note of that date. The final roll is due on 27 October.',
    'Bengaluru is four election districts, Bangalore Urban and the B.B.M.P. North, Central and South districts.',
    'Only counts are published, never a name, EPIC number or address.',
  ], M, TOP - 0.3, W - 2 * M, CH + 0.3, 16);

  closing(pres, K, P, 'The full analysis', ['The district map, every district, and the full report are published online alongside this deck.', 'PinPoint Ventures']);
  K.contents(toc);
  return pres.writeFile({ fileName: path.join(OUT, 'karnataka-sir-2026-deck.pptx') });
}

// ============================================================ WEST BENGAL
function westbengal() {
  const S = J('westbengal/summary.json'), D = J('westbengal/districts.json'), A = J('westbengal/constituencies.json'), Pn = S.pn05, AD = S.adj;
  const WN = Object.fromEntries(S.winners.map((w) => [w.party, w])), kol = (n) => /^Kolkata/.test(n), low = D[D.length - 1];
  const P = { dark: '1F4E79', darker: '163A5C', accent: '1F618D', light: 'D6E4F0', soft: 'EAF1F8', band, foot: 'West Bengal SIR 2026 · PinPoint Ventures · totals only, never names or EPIC numbers' };
  const [pres, K] = deck('West Bengal SIR 2026', P);

  cover(pres, K, P, 'Special Intensive Revision · West Bengal 2026', 'The revision left ' + lakh(Pn.removed) + ' names off West Bengal\'s draft roll and held back ' + lakh(Pn.adjudication) + ' more',
    'The names left off by reason, the names held back for adjudication, and how much smaller each roll was at the 2026 election than in 2024',
    [[indian(Pn.removed), 'names left off the draft roll'], [indian(Pn.adjudication), 'held back for adjudication'], [S.over_margin + ' of ' + S.acs, 'seats where the roll fell by more than the 2026 margin'], [pct(Pn.women_removed_pct), 'of the names left off were women']])
    .addNotes('The removals and their reasons are published for the state only. Below the state the deck measures the fall in the roll from 2024, which takes in ordinary changes as well as the revision and is a different count from the names struck off.');
  const toc = contentsSlide(pres, K, P);

  let s = K.slide('In short', 'The revision left ' + d1(Pn.removed_per_100) + ' of every 100 electors off the draft, and held back ' + lakh(Pn.adjudication) + ' more', 'Six findings, each computed from the published tables');
  K.numbered(s, [
    lakh(Pn.removed) + ' names were left off the draft roll, ' + d1(Pn.removed_per_100) + ' of every 100 electors, and another ' + lakh(Pn.adjudication) + ' were held back from the final roll for adjudication.',
    'In ' + S.over_margin + ' of the ' + S.acs + ' constituencies, the roll fell by more than the 2026 winning margin, large enough to decide the seat. At each seat\'s turnout, ' + S.could_change + '.',
    'Women were ' + pct(Pn.women_removed_pct) + ' of the names left off the draft, against ' + pct(Pn.women_before_pct) + ' of the roll before it.',
    'Of the names held back, ' + lakh(AD.found_not_eligible) + ' were found not eligible, as reported, and ' + indian(AD.restored_before_poll) + ' were restored by appeal in time to vote.',
    'The roll the election was held on was ' + lakh(S.fall) + ' smaller than in 2024. Kolkata North\'s fell by ' + d1(D[0].per_100) + ' per 100.',
    pct(Pn.shares.dead) + ' of the names left off were entered as dead, ' + pct(Pn.shares.shifted) + ' as shifted and ' + pct(Pn.shares.absent) + ' as absent.',
  ], M, TOP - 0.25, W - 2 * M, CH - 0.5, 15);
  K.body(s, 'The fall in the roll from 2024 includes ordinary changes as well as the revision. ' + REASON, M, TOP + CH - 0.45, W - 2 * M, 0.45, 12, MUTED);

  s = K.slide('The roll', 'The roll fell from ' + crore(Pn.before) + ' to ' + crore(Pn.final) + ' at the final roll, and stood at ' + crore(S.election) + ' for the election', 'The state\'s roll, step by step, as the Chief Electoral Officer reported it');
  waterfall(pres, s, [['Roll of Oct 2025', Pn.before, 'total'], ['Dead', Pn.dead, 'down'], ['Shifted', Pn.shifted, 'down'], ['Absent', Pn.absent, 'down'], ['Enrolled elsewhere and other', Pn.duplicate + Pn.other, 'down'], ['Draft roll', Pn.draft, 'total'], ['Added on claims', Pn.added, 'up'], ['Removed on objections', Pn.form7, 'down'], ['Held back', Pn.adjudication, 'down'], ['Final roll', Pn.final, 'total'], ['Net change after', S.after_final, 'up'], ['Roll at the nominations', S.election, 'total']],
    Math.floor(Pn.final * 0.85 / 1e6) * 1e6, { x: M, y: TOP, w: W - 2 * M, h: CH });
  s.addNotes('From press note PN-05-2026 and the roll at the 2026 nominations. The bars start above zero so that the changes can be seen. ' + REASON);

  s = K.slide('Adjudication', 'Of the ' + lakh(AD.under_adjudication) + ' names held back, ' + lakh(AD.found_not_eligible) + ' were found not eligible, as reported', 'The Election Commission\'s figures as reported, for the state as a whole');
  s.addChart(pres.charts.BAR, [{ name: 'Names', labels: ['Found eligible', 'Not eligible, appealed', 'Not eligible, no appeal', 'Not accounted for'], values: [AD.found_eligible, AD.appeals_by_excluded, AD.not_eligible_no_appeal, AD.not_accounted] }],
    K.chart(Object.assign({}, K.left, { barDir: 'bar', chartColors: ['17A589', 'D4AC0D', 'C0392B', GREY], showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '#,##0', valAxisHidden: true, catAxisOrientation: 'maxMin', catAxisLabelFontSize: 12 })));
  K.stats(s, [[indian(AD.restored_before_poll), 'restored by the tribunals in time to vote'], [lakh(AD.appeals_against_inclusion), 'appeals against names the judicial officers kept'], [pct(AD.pending_pct), 'of all appeals undecided on 16 September']], TOP, 1.4, 1, 8.65, W - M - 8.65);
  s.addNotes('Judicial officers appointed on the Supreme Court\'s direction decided the cases, and their orders could be appealed to tribunals. These outcomes are as reported, and they are not published by district.');

  s = K.slide('By district', 'The roll fell by ' + d1(S.per_100) + ' per 100 from 2024 to the election, and by ' + d1(D[0].per_100) + ' in Kolkata North', 'Fall in the roll from the 2024 Lok Sabha nominations to the 2026 nominations, per 100 electors on the 2024 roll');
  s.addChart(pres.charts.BAR, [{ name: 'Fall per 100', labels: D.map((d) => d.district), values: D.map((d) => d.per_100) }],
    K.chart(Object.assign({}, K.left, { y: TOP - 0.3, h: CH + 0.3, barDir: 'bar', chartColors: D.map((d) => kol(d.district) ? 'C0392B' : '1F618D'), showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0', dataLabelFontSize: 8, valAxisHidden: true, catAxisLabelFontSize: 9, catAxisOrientation: 'maxMin' })));
  K.right(s, ['No count of the names removed is published below the state, so this is the fall in the roll.', 'It takes in eighteen months of ordinary changes, and the 2024 roll was ' + lakh(S.growth_2024_to_oct2025) + ' smaller than the roll the revision started from.', low.district + ' fell the least, ' + d1(low.per_100) + '.'], 13);

  const RK = [['dead', 'Dead', GREY], ['shifted', 'Shifted', '1F618D'], ['absent', 'Absent', 'C0392B'], ['duplicate', 'Already enrolled', 'D4AC0D'], ['other', 'Other', '8E7CC3']];
  s = K.slide('The reasons', pct(Pn.shares.dead, 0) + ' of the names left off were entered as dead, ' + pct(Pn.shares.shifted, 0) + ' as shifted and ' + pct(Pn.shares.absent, 0) + ' as absent', 'Names left off the draft roll by the reason entered, for the state');
  s.addChart(pres.charts.BAR, [{ name: 'Names', labels: RK.map((r) => r[1]), values: RK.map((r) => Pn[r[0]]) }],
    K.chart(Object.assign({}, K.left, { barDir: 'bar', chartColors: RK.map((r) => r[2]), showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '#,##0', valAxisHidden: true, catAxisOrientation: 'maxMin', catAxisLabelFontSize: 12 })));
  K.right(s, ['The reasons are published for the state only, so no district or constituency figure can be split by reason.', REASON]);

  const DW = D.slice().sort((a, b) => (b.women_fall_pct - b.women_2024_pct) - (a.women_fall_pct - a.women_2024_pct));
  s = K.slide('Women', 'Women were ' + pct(Pn.women_removed_pct) + ' of the names left off the draft, against ' + pct(Pn.women_before_pct) + ' of the roll', 'Women\'s share of the 2024 roll and of the fall in the roll, by district');
  s.addChart(pres.charts.BAR, [{ name: 'Share of the 2024 roll', labels: DW.map((d) => d.district), values: DW.map((d) => d.women_2024_pct) }, { name: 'Share of the fall', labels: DW.map((d) => d.district), values: DW.map((d) => d.women_fall_pct) }],
    K.chart(Object.assign({}, K.left, { y: TOP - 0.3, h: CH + 0.3, barDir: 'bar', barGrouping: 'clustered', chartColors: ['AEB6BF', 'AF3B6E'], showLegend: true, valAxisMinVal: 30, valAxisMaxVal: 70, catAxisLabelFontSize: 8, catAxisOrientation: 'maxMin' })));
  K.right(s, ['From 2024 to the election women were ' + pct(S.women_fall_pct) + ' of the fall in the roll and ' + pct(S.women_2024_pct) + ' of the 2024 roll.', 'They were more than their share in ' + S.districts_women_over + ' of the ' + S.districts + ' districts.', 'In Kolkata North and Kolkata South men were the larger part of the fall.']);

  const DD = D.slice().sort((a, b) => (b.per_100 - b.draft_per_100) - (a.per_100 - a.draft_per_100)), d12 = DD.slice(0, 12);
  s = K.slide('After the draft', 'Most of the fall in ' + andj(DD.slice(0, 3).map((d) => d.district)) + ' came after the draft', 'Fall per 100 electors on the 2024 roll, at the draft and at the election, the twelve districts where it grew most');
  s.addChart(pres.charts.BAR, [{ name: 'At the draft', labels: d12.map((d) => d.district), values: d12.map((d) => d.draft_per_100) }, { name: 'At the election', labels: d12.map((d) => d.district), values: d12.map((d) => d.per_100) }],
    K.chart(Object.assign({}, K.left, { barDir: 'bar', barGrouping: 'clustered', chartColors: ['AEB6BF', P.accent], showLegend: true, showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0', dataLabelFontSize: 8, valAxisHidden: true, catAxisOrientation: 'maxMin', catAxisLabelFontSize: 10 })));
  K.right(s, ['The ' + lakh(Pn.adjudication) + ' names held back are counted for the state only.', 'This gap is the nearest the published tables come to showing where they fell, and it is not a count of them.', 'In Kolkata almost all of the fall was already in the draft.']);

  const [s1] = marginSlide(pres, K, P, A, (a) => a.fall, 'In ' + S.over_margin + ' of ' + S.acs + ' constituencies, the roll fell by more than the 2026 winning margin', 'Seats by the fall in the roll from 2024 to the election as a multiple of the 2026 margin', 'Fall in the roll');
  K.right(s1, ['In those seats the fall was large enough to decide the result.', 'The fall and the margin as a share of votes are close to unrelated (rank correlation ' + S.rho_rate_margin.toFixed(2) + ').', 'The fall counts the dead and ordinary changes too.'], 13.5);
  s1.addNotes('Over the margin means large enough to decide a seat, and says nothing about whether the fall did. Nobody can know how anyone missing from the roll would have voted.');

  s = K.slide('The 2026 election', 'Counted at each seat\'s own turnout, the fall still exceeds the margin in ' + S.could_change + ' seats', 'Three ways of setting the fall in the roll against the margin');
  K.stats(s, [[S.draft_over_margin + ' of ' + S.acs, 'fall to the draft roll'], [S.over_margin + ' of ' + S.acs, 'fall to the roll the election was held on'], [S.could_change + ' of ' + S.acs, 'the same, at the seat\'s 2026 turnout']], TOP, 1.9);
  K.body(s, 'None of the three separates the names entered as dead, because the reasons are published for the state only. In the other ' + (S.acs - S.could_change) + ' seats, the runner-up could not have won even if every elector missing from the roll had voted for the runner-up at the seat\'s turnout.', M, TOP + 2.3, W - 2 * M, 2, 16);

  s = K.slide('The 2026 election', 'The roll fell by ' + d1(WN.BJP.per_100) + ' per 100 in BJP seats and ' + d1(WN.AITC.per_100) + ' in AITC seats, and against their own districts they differ by ' + Math.abs(WN.BJP.vs_district - WN.AITC.vs_district).toFixed(1) + ' points', 'Fall per 100 in the seats each party won, and against the fall of each seat\'s own district');
  partyTable(K, s, S.winners, 'per_100', 'Fall per 100');
  K.right(s, ['The BJP won ' + WN.BJP.seats + ' seats and the AITC ' + WN.AITC.seats + '.', 'Against their own districts the two come out at ' + sg(WN.BJP.vs_district) + ' and ' + sg(WN.AITC.vs_district) + ', so the difference is about where the seats are.', 'The fall exceeded the margin in ' + WN.BJP.over_margin + ' BJP seats and ' + WN.AITC.over_margin + ' AITC seats.'], 13);

  s = K.slide('Limits', 'What the tables show, and what they cannot show');
  K.box(s, 'The names left off and held back for the state as a whole, by reason and by sex, and how much smaller every constituency\'s roll was at the 2026 election than in 2024.', M, TOP - 0.4, 5.95, 2.3, 15);
  K.box(s, 'How many names were removed in each district or constituency, or why. Where the names held back were. Whether each removal was right, or how anyone missing from the roll would have voted.', 6.78, TOP - 0.4, 5.95, 2.3, 15);
  K.body(s, 'The adjudication outcomes are the Election Commission\'s figures as reported. ' + REASON, M, TOP + 2.2, W - 2 * M, 1.5, 16);

  s = K.slide('What the Election Commission should do', 'Publish the removals and adjudication where they happened');
  K.numbered(s, [
    'Publish the names removed by constituency and polling station, with the reason and the sex of each.',
    'Publish the outcome of adjudication by district and constituency, in full.',
    'Decide the ' + lakh(AD.appeals_pending) + ' appeals still pending, and publish what each decision restored or removed.',
    'Account for the ' + indian(AD.not_accounted) + ' cases missing from the reported outcome.',
    'Publish how many of those added after the draft had been left off it.',
  ], M, TOP - 0.3, W - 2 * M, CH + 0.3, 17);

  s = K.slide('Method', 'Where the figures come from');
  K.bullets(s, [
    'The state\'s revision is from the Chief Electoral Officer\'s press note PN-05-2026, whose figures add up step by step.',
    'The rolls at the 2024 Lok Sabha nominations, the draft of 16 December 2025 and the 2026 nominations are the Chief Electoral Officer\'s tables by constituency and sex. The fall between them is never called the removals.',
    'The adjudication outcomes and appeals are the Election Commission\'s figures as the press reported them.',
    'The 2026 result is from the Election Commission\'s result pages, with Falta\'s from its re-poll. Each seat\'s fall is also set against its own district\'s.',
    'Only counts are published, never a name, EPIC number or address.',
  ], M, TOP - 0.3, W - 2 * M, CH + 0.3, 15);

  closing(pres, K, P, 'The full analysis', ['The constituency map, every district and constituency, and the full report are published online alongside this deck.', 'PinPoint Ventures']);
  K.contents(toc);
  return pres.writeFile({ fileName: path.join(OUT, 'west-bengal-sir-2026-deck.pptx') });
}

// ============================================================ KERALA
function kerala() {
  const S = J('kerala/summary.json'), D = J('kerala/districts.json'), A = J('kerala/constituencies.json');
  const WN = Object.fromEntries(S.winners.map((w) => [w.party, w])), low = D[D.length - 1], grew = D.filter((d) => d.per_100 < 0).map((d) => d.district);
  const P = { dark: '0B4A57', darker: '083843', accent: '0E5E6F', light: 'CDE6EB', soft: 'E8F3F5', band, foot: 'Kerala SIR 2026 · PinPoint Ventures · totals only, never names or EPIC numbers' };
  const [pres, K] = deck('Kerala SIR 2026', P);

  cover(pres, K, P, 'Special Intensive Revision · Kerala 2026', 'Kerala\'s draft roll was ' + lakh(S.fall_draft) + ' smaller than in January 2025',
    'How much smaller each roll was at the draft, who was missing, how much came back before the 2026 election, and how that compares with the result',
    [[indian(S.fall_draft), 'fewer electors on the draft roll'], [d1(S.draft_per_100), 'of every 100 electors on the January 2025 roll'], [pct(S.women_fall_pct), 'of the fall were women, against ' + pct(S.women_2025_pct) + ' of the roll'], [S.draft_over_margin + ' of ' + S.acs, 'seats where the fall exceeded the 2026 margin']])
    .addNotes('No table of the names left off has been published. The deck measures the fall in the roll from January 2025, which takes in ordinary changes as well as the revision and is a different count from the names struck off.');
  const toc = contentsSlide(pres, K, P);

  let s = K.slide('In short', 'The draft roll was ' + d1(S.draft_per_100) + ' per 100 smaller, and women were ' + pct(S.women_fall_pct) + ' of the fall', 'Five findings, each computed from the published rolls');
  K.numbered(s, [
    'Kerala\'s draft roll was ' + lakh(S.fall_draft) + ' smaller than its roll of January 2025, ' + d1(S.draft_per_100) + ' of every 100 electors.',
    'In ' + S.draft_over_margin + ' of the ' + S.acs + ' constituencies the roll fell by more at the draft than the 2026 margin. On the roll the election was held on, it was still more than the margin in ' + S.over_margin + ', large enough to decide them.',
    'Women were ' + pct(S.women_fall_pct) + ' of the fall, against ' + pct(S.women_2025_pct) + ' of the roll, and more than their share in all ' + S.districts + ' districts.',
    D[0].district + ' fell most, by ' + d1(D[0].draft_per_100) + ' per 100, and ' + low.district + ' least, by ' + d1(low.draft_per_100) + '.',
    'By the election the roll had risen ' + lakh(S.election - S.draft) + ' from the draft, counting new voters too, and it was ' + lakh(S.fall) + ' smaller than in January 2025.',
  ], M, TOP - 0.2, W - 2 * M, CH - 0.6, 16);
  K.body(s, 'No count of the names removed has been published, so these are falls in the roll, which take in ordinary changes too.', M, TOP + CH - 0.5, W - 2 * M, 0.5, 12, MUTED);

  s = K.slide('The roll', 'The roll fell from ' + crore(S.roll_2025) + ' to ' + crore(S.draft) + ' at the draft, and stood at ' + crore(S.election) + ' for the election', 'The state\'s roll from January 2025 to the roll of 23 March 2026');
  waterfall(pres, s, [['Roll of January 2025', S.roll_2025, 'total'], ['Fall to the draft', S.fall_draft, 'down'], ['Draft roll', S.draft, 'total'], ['Net change to the final roll', S.added_final, 'up'], ['Final roll', S.final, 'total'], ['Net change to March 2026', S.added_election, 'up'], ['Roll of 23 March 2026', S.election, 'total']],
    Math.floor(S.draft * 0.85 / 1e6) * 1e6, { x: M, y: TOP, w: W - 2 * M, h: CH });
  s.addNotes('For the state the fall to the draft, ' + indian(S.fall_draft) + ', is close to the ' + indian(S.press_removed) + ' names reported left off with the draft. For one constituency the two may differ more. The rise after the draft counts new voters and electors registered abroad.');

  s = K.slide('By district', D[0].district + '\'s roll was ' + d1(D[0].draft_per_100) + ' per 100 smaller at the draft, against ' + d1(S.draft_per_100) + ' for the state', 'Fall in the roll from January 2025 to the draft, per 100 electors, by district');
  s.addChart(pres.charts.BAR, [{ name: 'Fall per 100', labels: D.map((d) => d.district), values: D.map((d) => d.draft_per_100) }],
    K.chart(Object.assign({}, K.left, { barDir: 'bar', chartColors: D.map((d, i) => i === 0 ? 'C0392B' : '1F618D'), showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0', valAxisHidden: true, catAxisLabelFontSize: 11, catAxisOrientation: 'maxMin' })));
  K.right(s, [D[1].district + ' and ' + D[2].district + ' come next.', 'By constituency the fall runs from ' + d1(S.rate_min_v) + ' in ' + S.rate_min + ' to ' + d1(S.rate_max_v) + ' in ' + S.rate_max + '.', 'No reasons have been published, by constituency or for the state, so none of these can be split by reason.']);

  s = K.slide('Women', 'Women were more than their share of the fall in all ' + S.districts + ' districts and ' + S.acs_women_over + ' of ' + S.acs + ' constituencies', 'Women\'s share of the January 2025 roll and of the fall at the draft, by district');
  s.addChart(pres.charts.BAR, [{ name: 'Share of the roll', labels: D.map((d) => d.district), values: D.map((d) => d.women_2025_pct) }, { name: 'Share of the fall', labels: D.map((d) => d.district), values: D.map((d) => d.women_fall_pct) }],
    K.chart(Object.assign({}, K.left, { barDir: 'bar', barGrouping: 'clustered', chartColors: ['AEB6BF', 'AF3B6E'], showLegend: true, valAxisMinVal: 40, valAxisMaxVal: 65, catAxisLabelFontSize: 10, catAxisOrientation: 'maxMin' })));
  K.right(s, ['For the state women were ' + pct(S.women_fall_pct) + ' of the fall, against ' + pct(S.women_2025_pct) + ' of the roll.', 'Of the rise after the draft, women were ' + pct(S.women_added_pct) + '.']);

  s = K.slide('After the draft', 'By the election the roll was still ' + lakh(S.fall) + ' smaller than in January 2025, and ' + grew.length + ' districts had grown past it', 'Per 100 electors on the January 2025 roll, the fall at the draft, at the final roll and on the roll of March 2026');
  s.addChart(pres.charts.BAR, [['At the draft', (d) => d.draft_per_100], ['At the final roll', (d) => 100 * (d.roll_2025 - d.final) / d.roll_2025], ['March 2026', (d) => d.per_100]].map(([n, f]) => ({ name: n, labels: D.map((d) => d.district), values: D.map((d) => +f(d).toFixed(1)) })),
    K.chart(Object.assign({}, K.left, { barDir: 'bar', barGrouping: 'clustered', chartColors: ['AEB6BF', '5D8AA8', P.accent], showLegend: true, catAxisLabelFontSize: 10, catAxisOrientation: 'maxMin', valAxisLabelFontSize: 9 })));
  K.right(s, ['A negative figure means the roll was larger than in January 2025.', andj(grew) + ' ended above their January roll.', 'The rise counts new voters, including those who turned eighteen and those registered abroad, so it cannot show how many of those left off were restored.'], 13);

  const [s1] = marginSlide(pres, K, P, A, (a) => a.fall_draft, 'In ' + S.draft_over_margin + ' of ' + S.acs + ' constituencies, the roll fell by more at the draft than the 2026 winning margin', 'Seats by the fall in the roll at the draft as a multiple of the 2026 margin', 'Fall at the draft');
  K.right(s1, ['The fall and the margin as a share of votes are close to unrelated (rank correlation ' + S.rho_rate_margin.toFixed(2) + ').', 'By the election most of the fall had been made up, so the count on the roll the election was held on is smaller.'], 13.5);
  s1.addNotes('Over the margin means large enough to decide a seat, and says nothing about whether the fall did. Nobody can know how anyone missing from the roll would have voted.');

  s = K.slide('The 2026 election', 'On the roll the election was held on, the fall still exceeded the margin in ' + S.over_margin + ' seats', 'Three ways of setting the fall in the roll against the margin');
  K.stats(s, [[S.draft_over_margin + ' of ' + S.acs, 'fall to the draft roll'], [S.over_margin + ' of ' + S.acs, 'fall to the roll the election was held on'], [S.could_change + ' of ' + S.acs, 'the same, at the seat\'s 2026 turnout']], TOP, 1.9);
  K.body(s, 'In those seats the fall was large enough to decide the result. The rise after the draft counts new voters too, and nobody can know how anyone missing from the roll would have voted.', M, TOP + 2.3, W - 2 * M, 2, 16);

  s = K.slide('The 2026 election', 'INC seats lost ' + d1(WN.INC.draft_per_100) + ' per 100 at the draft and CPI(M) seats ' + d1(WN['CPI(M)'].draft_per_100) + ', and against their own districts they differ by ' + Math.abs(WN.INC.vs_district - WN['CPI(M)'].vs_district).toFixed(1) + ' points', 'Fall at the draft per 100 in the seats each party won, and against the fall of each seat\'s own district');
  partyTable(K, s, S.winners, 'draft_per_100', 'Fall per 100 at the draft');
  K.right(s, ['The INC won ' + WN.INC.seats + ' seats, the CPI(M) ' + WN['CPI(M)'].seats + ' and the IUML ' + WN.IUML.seats + '.', 'Against their own districts they come out at ' + sg(WN.INC.vs_district) + ', ' + sg(WN['CPI(M)'].vs_district) + ' and ' + sg(WN.IUML.vs_district) + ', so most of the difference is about where the seats are.', 'Comparisons are by party, because the fronts of the independents are not in the data.'], 13);

  s = K.slide('Limits', 'What the rolls show, and what they cannot show');
  K.box(s, 'How much smaller every constituency\'s roll was at the draft and at the election than in January 2025, by sex, and how that compares with the 2026 margins.', M, TOP - 0.4, 5.95, 2.3, 15);
  K.box(s, 'How many names were removed in each place, or on what reason, because no table of the names left off has been published. How many of those left off were put back. How anyone missing from the roll would have voted.', 6.78, TOP - 0.4, 5.95, 2.3, 15);
  K.body(s, 'No list of removals can show intent, and the fall in the roll is a different count from the names struck off.', M, TOP + 2.2, W - 2 * M, 1.5, 16);

  s = K.slide('What the Election Commission should do', 'Publish the names left off, where and why');
  K.numbered(s, [
    'Publish the names left off the draft by constituency and polling station, with the reason and the sex of each.',
    'Explain why women were ' + pct(S.women_fall_pct) + ' of the fall at the draft, against ' + pct(S.women_2025_pct) + ' of the roll.',
    'Publish how many of those added for the final roll had been left off the draft.',
    'Explain why ' + D[0].district + ' lost ' + d1(D[0].draft_per_100) + ' of every 100 electors at the draft, ' + (D[0].draft_per_100 / low.draft_per_100).toFixed(1) + ' times the rate of ' + low.district + '.',
  ], M, TOP - 0.3, W - 2 * M, CH + 0.3, 17);

  s = K.slide('Method', 'Where the figures come from');
  K.bullets(s, [
    'Four rolls by constituency and sex, all the Chief Electoral Officer\'s, are the final roll of the 2025 summary revision (6 January 2025), the draft (23 December 2025), the final roll (21 February 2026) and the roll of 23 March 2026, on which the election was held.',
    'No table of the names left off has been published, so the figures measure the fall in the roll. For the state it is ' + indian(S.fall_draft) + ', against ' + indian(S.press_removed) + ' names reported left off with the draft.',
    'The 2026 result is from the Election Commission\'s result pages. Each seat\'s fall is also set against its own district\'s.',
    'Only counts are published, never a name, EPIC number or address.',
  ], M, TOP - 0.3, W - 2 * M, CH + 0.3, 16);

  closing(pres, K, P, 'The full analysis', ['The constituency map, every district and constituency, and the full report are published online alongside this deck.', 'PinPoint Ventures']);
  K.contents(toc);
  return pres.writeFile({ fileName: path.join(OUT, 'kerala-sir-2026-deck.pptx') });
}

fs.mkdirSync(OUT, { recursive: true });
Promise.all([tamilnadu(), karnataka(), westbengal(), kerala()]).then((f) => console.log('wrote', f.join(', ')));
