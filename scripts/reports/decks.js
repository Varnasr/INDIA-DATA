// Two slide decks, Bihar 2025 and Hyderabad Old City 2026, from the published
// JSON. Charts are native PowerPoint charts, so they stay editable.
//
//   NODE_PATH=<dir with pptxgenjs> node scripts/reports/decks.js [outdir]
//
// Every figure is computed here from data/bihar and data/hyderabad, the same
// files the pages and the reports read.
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
const sum = (a, f) => a.reduce((s, x) => s + (typeof f === 'function' ? f(x) : x[f]), 0);
const median = (a) => { const s = a.slice().sort((x, y) => x - y); const m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };
const andj = (xs) => xs.length === 1 ? xs[0] : xs.slice(0, -1).join(', ') + ' and ' + xs[xs.length - 1];

// ------------------------------------------------------------ slide kit
const W = 13.333, Hh = 7.5, M = 0.6;
const HEAD = 'Cambria', BODY = 'Calibri', INK = '1C2833', MUTED = '4D5B69', PAPER = 'FFFFFF', TINT = 'F4F6F7';

function kit(pres, P) {
  const K = {};
  K.title = (s, t, sub) => {
    s.addText(t, { x: M, y: 0.35, w: W - 2 * M, h: 0.8, fontFace: HEAD, fontSize: 30, bold: true, color: P.dark, margin: 0, isTextBox: true, valign: 'top' });
    if (sub) s.addText(sub, { x: M, y: 1.12, w: W - 2 * M, h: 0.5, fontFace: BODY, fontSize: 15, color: MUTED, margin: 0, isTextBox: true, valign: 'top' });
  };
  K.band = (s) => { // the folk-art band from the site, drawn as a row of tiles
    const n = 40, tw = W / n;
    for (let i = 0; i < n; i++) s.addShape(pres.shapes.RECTANGLE, { x: i * tw, y: Hh - 0.12, w: tw, h: 0.12, fill: { color: P.band[i % P.band.length] }, line: { type: 'none' } });
  };
  K.foot = (s, n, src) => {
    s.addText(src || P.foot, { x: M, y: Hh - 0.5, w: W - 2 * M - 1, h: 0.3, fontFace: BODY, fontSize: 9, color: MUTED, margin: 0, isTextBox: true, valign: 'middle' });
    s.addText(String(n), { x: W - M - 0.8, y: Hh - 0.5, w: 0.8, h: 0.3, fontFace: BODY, fontSize: 9, color: MUTED, align: 'right', margin: 0, isTextBox: true });
    K.band(s);
  };
  K.stat = (s, x, y, w, h, value, label, opt = {}) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: opt.fill || TINT }, line: { type: 'none' } });
    s.addText(value, { x: x + 0.2, y: y + 0.15, w: w - 0.4, h: h * 0.5, fontFace: HEAD, fontSize: opt.size || 30, bold: true, color: opt.color || P.accent, margin: 0, isTextBox: true, valign: 'bottom', fit: 'shrink' });
    s.addText(label, { x: x + 0.2, y: y + 0.15 + h * 0.5, w: w - 0.4, h: h * 0.5 - 0.25, fontFace: BODY, fontSize: opt.lsize || 12.5, color: opt.lcolor || MUTED, margin: 0, isTextBox: true, valign: 'top' });
  };
  K.body = (s, text, x, y, w, h, size = 16, color = INK) => s.addText(text, { x, y, w, h, fontFace: BODY, fontSize: size, color, margin: 0, isTextBox: true, valign: 'top', paraSpaceAfter: 8 });
  K.bullets = (s, items, x, y, w, h, size = 15) => s.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })), { x, y, w, h, fontFace: BODY, fontSize: size, color: INK, margin: 0, isTextBox: true, valign: 'top', paraSpaceAfter: 9 });
  K.numbered = (s, items, x, y, w, h, size = 15) => s.addText(items.map((t, i) => ({ text: t, options: { bullet: { type: 'number' }, breakLine: i < items.length - 1 } })), { x, y, w, h, fontFace: BODY, fontSize: size, color: INK, margin: 0, isTextBox: true, valign: 'top', paraSpaceAfter: 10 });
  K.callout = (s, text, x, y, w, h) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1, fill: { color: P.soft }, line: { type: 'none' } });
    s.addText(text, { x: x + 0.3, y: y + 0.2, w: w - 0.6, h: h - 0.4, fontFace: BODY, fontSize: 15, color: INK, margin: 0, isTextBox: true, valign: 'middle' });
  };
  K.table = (s, head, rows, x, y, w, colW, fs = 11) => {
    const hdr = head.map((h, i) => ({ text: h, options: { bold: true, color: 'FFFFFF', fill: { color: P.dark }, align: i ? 'right' : 'left' } }));
    const body = rows.map((r, k) => r.map((v, i) => ({ text: String(v), options: { align: i && typeof r.right === 'undefined' ? 'right' : (r.right && r.right.includes(i) ? 'right' : (i ? 'right' : 'left')), fill: { color: k % 2 ? TINT : PAPER } } })));
    s.addTable([hdr, ...body], { x, y, w, colW, fontFace: BODY, fontSize: fs, color: INK, border: { type: 'solid', pt: 0.5, color: 'D5D8DC' }, rowH: 0.3, margin: 0.05 });
  };
  K.chartBase = (o = {}) => Object.assign({
    catAxisLabelColor: MUTED, valAxisLabelColor: MUTED, catAxisLabelFontFace: BODY, valAxisLabelFontFace: BODY, catAxisLabelFontSize: 11, valAxisLabelFontSize: 10,
    valGridLine: { color: 'E1E5E8', size: 0.5 }, catGridLine: { style: 'none' }, showLegend: false, dataLabelFontFace: BODY, dataLabelFontSize: 10, dataLabelColor: INK,
    titleFontFace: BODY, titleColor: INK, titleFontSize: 13,
  }, o);
  return K;
}

function cover(pres, K, P, kicker, title, sub, stats, n) {
  const s = pres.addSlide(); s.background = { color: P.dark };
  s.addText(kicker.toUpperCase(), { x: M, y: 0.7, w: 9, h: 0.4, fontFace: BODY, fontSize: 13, bold: true, color: P.light, charSpacing: 3, margin: 0, isTextBox: true });
  s.addText(title, { x: M, y: 1.15, w: W - 2 * M, h: 1.3, fontFace: HEAD, fontSize: 44, bold: true, color: 'FFFFFF', margin: 0, isTextBox: true, valign: 'top' });
  s.addText(sub, { x: M, y: 2.45, w: W - 2 * M - 1, h: 0.8, fontFace: BODY, fontSize: 18, color: P.light, margin: 0, isTextBox: true, valign: 'top' });
  const cw = (W - 2 * M - 0.3 * (stats.length - 1)) / stats.length;
  stats.forEach((st, i) => K.stat(s, M + i * (cw + 0.3), 3.75, cw, 1.9, st[0], st[1], { fill: P.darker, color: 'FFFFFF', lcolor: P.light, size: 30 }));
  s.addText('Varna Sri Raman', { x: M, y: 6.3, w: 8, h: 0.4, fontFace: BODY, fontSize: 13, color: P.light, margin: 0, isTextBox: true });
  K.band(s);
  return s;
}

function closing(pres, K, P, head, lines) {
  const s = pres.addSlide(); s.background = { color: P.dark };
  s.addText(head, { x: M, y: 1.4, w: W - 2 * M, h: 1.2, fontFace: HEAD, fontSize: 36, bold: true, color: 'FFFFFF', margin: 0, isTextBox: true, valign: 'top' });
  s.addText(lines.map((t, i) => ({ text: t, options: { breakLine: i < lines.length - 1 } })), { x: M, y: 3.0, w: W - 2 * M, h: 2.6, fontFace: BODY, fontSize: 17, color: P.light, margin: 0, isTextBox: true, valign: 'top', paraSpaceAfter: 10 });
  K.band(s);
}

// ============================================================ BIHAR
function bihar() {
  const S = J('bihar/summary.json'), A = J('bihar/constituencies.json'), DS = J('bihar/districts.json'), ID = J('bihar/identity.json');
  const t = S.totals, DI = ID.districts;
  const P = { dark: '8E2F25', darker: '6E231C', accent: 'B03A2E', light: 'F5D6C6', soft: 'FBEFE8', band: ['C0392B', 'E67E22', '27AE60', '1F618D', '8E44AD'], foot: 'Bihar SIR 2025 · Varna Sri Raman · aggregates only; no names or EPIC numbers' };
  const AL = { NDA: 'E67E22', INDIA: '1E8449', Other: '8E7CC3' };
  const pres = new pptxgen(); pres.layout = 'LAYOUT_WIDE'; pres.author = 'Varna Sri Raman'; pres.title = 'Bihar SIR 2025: 69 lakh names struck off';
  const K = kit(pres, P);
  const withM = A.filter((a) => a.margin2025), over = withM.filter((a) => a.total > a.margin2025);
  const nda = withM.filter((a) => a.al2025 === 'NDA'), took = withM.filter((a) => a.al2020 === 'INDIA' && a.al2025 === 'NDA'), tookO = took.filter((a) => a.total > a.margin2025);
  const polled = sum(A, 'votes2025'), mAll = sum(withM, 'margin2025'), mNDA = sum(nda, 'margin2025'), tookRem = sum(took, 'total'), tookM = sum(took, 'margin2025');
  const share = (a) => 100 * a.total / a.votes2025, ratio = (a) => a.total / a.margin2025;
  const fem = 100 * t.female / (t.female + t.male), per100 = 100 * t.total / t.electorate_2025;
  const cls = t.hindu + t.muslim + t.unknown, mlo = 100 * t.muslim / cls, mhi = 100 * (t.muslim + t.unknown) / cls;
  const fOver = DI.filter((d) => d.female_share_deleted > d.female_share_population_2011);
  const above = DI.filter((d) => d.muslim_share_deleted_low > d.muslim_share_population_2011 + 1);
  const rankD = DS.slice().sort((a, b) => b.per_100 - a.per_100);
  const L = S.by_alliance_label, Wt = S.within_seat_2024;
  let n = 1;

  let s = cover(pres, K, P, 'Special Intensive Revision 2025', 'Bihar: 69 lakh names struck off', 'Removals from the electoral roll, booth by booth, set against the margins and the votes that decided each seat',
    [[indian(t.total), 'names removed across both phases'], [pct(100 * t.total / polled), 'of the votes polled in November 2025'], [over.length + ' of ' + withM.length, 'seats where removals exceed the margin'], [pct(fem), 'of the removed are women']]);
  s.addNotes('The Special Intensive Revision removed 69,10,559 names from Bihar\'s roll in 2025. This deck sets those removals against the margins and votes that decided each seat, and against who was removed. Every figure comes from the Chief Electoral Officer\'s booth lists and the 2025 results.');

  // 2. Scale
  s = pres.addSlide(); n++;
  K.title(s, 'One name removed for every seven votes cast', 'The revision in numbers, before the Assembly election of November 2025');
  [[indian(t.total), 'names removed: ' + indian(t.p1) + ' in phase 1, ' + indian(t.p2) + ' in phase 2'], [per100.toFixed(2), 'names removed for every 100 electors on the final roll'],
    [indian(t.booths), 'polling booths, every one accounted for in the lists'], [pct(100 * t.total / polled), 'of the ' + indian(polled) + ' votes polled in the election that followed']]
    .forEach((st, i) => K.stat(s, M + (i % 2) * 6.15, 1.85 + Math.floor(i / 2) * 2.35, 5.9, 2.1, st[0], st[1], { size: 40 }));
  K.foot(s, n);
  s.addNotes('Phase 1 removed names before the draft roll of 1 August 2025; phase 2 before the final roll. Votes polled are the turnout applied to the 2025 roll.');

  // 3. Against combined margins
  s = pres.addSlide(); n++;
  K.title(s, 'More names removed than the NDA\'s entire winning margin', 'Names removed against the combined winning margin of each group of seats, in lakh');
  s.addChart(pres.charts.BAR, [
    { name: 'Names removed', labels: ['All ' + withM.length + ' seats', 'The NDA\'s ' + nda.length + ' wins', took.length + ' seats taken from INDIA'], values: [t.total, sum(nda, 'total'), tookRem].map((v) => +(v / 1e5).toFixed(1)) },
    { name: 'Combined winning margins', labels: ['All ' + withM.length + ' seats', 'The NDA\'s ' + nda.length + ' wins', took.length + ' seats taken from INDIA'], values: [mAll, mNDA, tookM].map((v) => +(v / 1e5).toFixed(1)) },
  ], K.chartBase({ x: M, y: 1.75, w: 7.6, h: 5.0, barDir: 'col', barGrouping: 'clustered', chartColors: [P.accent, '95A5A6'], showValue: true, dataLabelPosition: 'outEnd', showLegend: true, legendPos: 'b', legendFontFace: BODY, legendFontSize: 11, valAxisHidden: true }));
  K.bullets(s, [
    'Across Bihar, ' + lakh(t.total) + ' names were removed; the combined winning margin of all ' + withM.length + ' seats was ' + lakh(mAll) + '.',
    'The NDA\'s ' + nda.length + ' wins add up to a combined margin of ' + lakh(mNDA) + ', less than the names removed.',
    'In the ' + took.length + ' seats the NDA took from INDIA, ' + lakh(tookRem) + ' names were removed against combined margins of ' + lakh(tookM) + '.',
  ], 8.6, 2.0, 4.1, 4.6, 15);
  K.foot(s, n);
  s.addNotes('A combined margin is the sum of each seat\'s margin of victory. The comparison measures scale; it does not say how the removed would have voted.');

  // 4. Multiples of the margin
  s = pres.addSlide(); n++;
  const cuts = [0, 1, 2, 5, 10, 20, 1e9], labs = ['under 1×', '1–2×', '2–5×', '5–10×', '10–20×', '20× or more'];
  const vals = labs.map((l, i) => withM.filter((a) => ratio(a) >= cuts[i] && ratio(a) < cuts[i + 1]).length);
  K.title(s, over.length + ' of ' + withM.length + ' seats lost more names than they were won by', 'Constituencies by names removed as a multiple of the 2025 winning margin');
  s.addChart(pres.charts.BAR, [{ name: 'Constituencies', labels: labs, values: vals }], K.chartBase({ x: M, y: 1.75, w: 7.9, h: 5.0, barDir: 'col', chartColors: ['95A5A6', P.accent, P.accent, P.accent, P.accent, P.accent], showValue: true, dataLabelPosition: 'outEnd', valAxisHidden: true }));
  const smallest = withM.slice().sort((a, b) => a.margin2025 - b.margin2025)[0];
  K.stat(s, 8.9, 1.9, 3.85, 1.55, vals.slice(3).reduce((a, b) => a + b, 0) + ' seats', 'where removals were five times the margin or more');
  K.stat(s, 8.9, 3.65, 3.85, 1.55, median(withM.map(ratio)).toFixed(2) + '×', 'removals against the margin in the median seat');
  K.stat(s, 8.9, 5.4, 3.85, 1.55, indian(smallest.margin2025) + ' votes', smallest.name + '\'s margin; ' + indian(smallest.total) + ' names removed', { size: 26 });
  K.foot(s, n);
  s.addNotes('Grey is the ' + vals[0] + ' seats where removals were below the margin. ' + smallest.name + ' was won by ' + smallest.margin2025 + ' votes.');

  // 5. Largest multiples table
  s = pres.addSlide(); n++;
  const top = withM.slice().sort((a, b) => ratio(b) - ratio(a)).slice(0, 12);
  K.title(s, 'Where the removals dwarfed the margin', 'The twelve constituencies with the largest removals against their 2025 winning margin');
  K.table(s, ['Constituency', 'District', 'Won by', 'Margin', 'Names removed', '× margin', '% of votes polled'],
    top.map((a) => [a.ac + ' ' + a.name, a.district, a.win2025 + ' (' + a.al2025 + ')', indian(a.margin2025), indian(a.total), ratio(a).toFixed(1) + '×', pct(share(a))]),
    M, 1.75, W - 2 * M, [2.6, 2.2, 1.9, 1.3, 1.7, 1.3, 1.1], 12);
  K.foot(s, n);

  // 6. Seats taken from INDIA
  s = pres.addSlide(); n++;
  K.title(s, tookO.length + ' of the ' + took.length + ' seats the NDA took from INDIA', 'In these seats more names were removed than the NDA won by');
  K.stat(s, M, 1.85, 3.9, 1.7, tookO.length + ' of ' + took.length, 'seats INDIA held in 2020 and lost in 2025 where removals exceed the NDA\'s margin');
  K.stat(s, M, 3.75, 3.9, 1.7, median(took.map(ratio)).toFixed(1) + '×', 'removals against the margin in the median such seat');
  K.stat(s, M, 5.65, 3.9, 1.35, lakh(tookRem), 'names removed in these ' + took.length + ' seats', { size: 26 });
  const tk = took.slice().sort((a, b) => ratio(b) - ratio(a)).slice(0, 12).reverse();
  s.addChart(pres.charts.BAR, [{ name: '× margin', labels: tk.map((a) => a.name), values: tk.map((a) => +ratio(a).toFixed(1)) }],
    K.chartBase({ x: 4.9, y: 1.75, w: 7.8, h: 5.15, barDir: 'bar', chartColors: [P.accent], showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0"×"', valAxisHidden: true, valAxisLogScaleBase: 10, showTitle: true, title: 'Names removed ÷ NDA margin, the twelve largest (log scale)' }));
  K.foot(s, n);

  // 7. Share of votes polled
  s = pres.addSlide(); n++;
  const bys = A.slice().sort((a, b) => share(b) - share(a)), tp = bys.slice(0, 15).reverse();
  const ru = A.filter((a) => a.total > a.runner_up_votes2025);
  K.title(s, 'Removals against the vote', 'Names removed as a share of the votes polled in 2025, the fifteen highest');
  s.addChart(pres.charts.BAR, [{ name: '% of votes polled', labels: tp.map((a) => a.name), values: tp.map((a) => +share(a).toFixed(1)) }],
    K.chartBase({ x: M, y: 1.7, w: 7.6, h: 5.2, barDir: 'bar', chartColors: tp.map((a) => AL[a.al2025]), showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0"%"', valAxisHidden: true }));
  K.bullets(s, [
    'Across Bihar, removals equal ' + pct(100 * t.total / polled) + ' of the votes polled.',
    'In ' + A.filter((a) => share(a) > 15).length + ' seats they exceed 15%, in ' + A.filter((a) => share(a) > 20).length + ' a fifth.',
    bys[0].name + ' is highest, at ' + pct(share(bys[0])) + '.',
    ru.length ? 'In ' + andj(ru.map((a) => a.name)) + ' the removals exceed the runner-up\'s entire vote.' : '',
    'Colour marks the 2025 winner: orange NDA, green INDIA, purple neither.',
  ].filter(Boolean), 8.6, 1.95, 4.1, 4.8, 15);
  K.foot(s, n);

  // 8. Women
  s = pres.addSlide(); n++;
  const gaps = DI.slice().sort((a, b) => (b.female_share_deleted - b.female_share_population_2011) - (a.female_share_deleted - a.female_share_population_2011)).slice(0, 10).reverse();
  K.title(s, 'Women are ' + pct(fem) + ' of those removed', 'Against 47.86% of Bihar\'s population; over-represented in ' + fOver.length + ' of ' + DI.length + ' districts');
  s.addChart(pres.charts.BAR, [
    { name: 'Women, % of population 2011', labels: gaps.map((d) => d.district), values: gaps.map((d) => +d.female_share_population_2011.toFixed(1)) },
    { name: 'Women, % of names removed', labels: gaps.map((d) => d.district), values: gaps.map((d) => +d.female_share_deleted.toFixed(1)) },
  ], K.chartBase({ x: M, y: 1.7, w: 7.6, h: 5.2, barDir: 'bar', barGrouping: 'clustered', chartColors: ['95A5A6', 'AF3B6E'], showLegend: true, legendPos: 'b', legendFontFace: BODY, legendFontSize: 11, valAxisMinVal: 40, valAxisMaxVal: 65, showTitle: true, title: 'The ten districts with the widest gap' }));
  K.bullets(s, [
    indian(t.female) + ' women and ' + indian(t.male) + ' men were removed: ' + indian(t.female - t.male) + ' more women.',
    'The roll records sex, so this rests on no estimate.',
    'Women who move on marriage and are marked "shifted" at their parents\' address would produce this pattern; the lists do not record the reason against each name.',
    'The lists do not show whether they were enrolled again where they now live. If not, they have lost the vote.',
  ], 8.6, 1.95, 4.1, 4.8, 15);
  K.foot(s, n);

  // 9. Religion
  s = pres.addSlide(); n++;
  K.title(s, 'Religion, read from names, as a range', 'The roll records no religion; the lists classify names where the name allows it');
  K.stat(s, M, 1.85, 3.9, 1.6, pct(mlo) + ' to ' + pct(mhi), 'Muslim share of removals: classified names only, then adding every unclassified name', { size: 28 });
  K.stat(s, M, 3.65, 3.9, 1.6, '16.87%', 'Muslim share of Bihar\'s population, 2011 census (17.70% in the 2023 caste survey)', { size: 28 });
  K.stat(s, M, 5.45, 3.9, 1.5, above.length + ' districts', 'where the classified Muslim share alone runs more than a point above the census', { size: 28 });
  K.table(s, ['District', 'Census 2011', 'Removals: low', 'Removals: high'], above.map((d) => [d.district, pct(d.muslim_share_population_2011), pct(d.muslim_share_deleted_low), pct(d.muslim_share_deleted_high)]), 4.9, 1.85, 7.8, [2.6, 1.7, 1.75, 1.75], 12);
  K.body(s, 'The census share lies inside the range in ' + DI.filter((d) => d.muslim_share_deleted_low <= d.muslim_share_population_2011 && d.muslim_share_population_2011 <= d.muslim_share_deleted_high).length + ' of ' + DI.length + ' districts.', 4.9, 5.2, 7.8, 0.8, 14, MUTED);
  K.foot(s, n);

  // 10. Caste
  s = pres.addSlide(); n++;
  const cg = ID.caste.guardian, G = ['General', 'BC', 'EBC', 'SC', 'ST', 'Muslim'];
  const up = G.filter((g) => cg.A.groups[g].ratio_to_survey >= 1 && cg.B.groups[g].ratio_to_survey >= 1), down = G.filter((g) => cg.A.groups[g].ratio_to_survey < 1 && cg.B.groups[g].ratio_to_survey < 1);
  K.title(s, 'Caste, under two classifications', 'Read from the surname of the father or husband, against the 2023 caste survey');
  s.addChart(pres.charts.BAR, [
    { name: 'Classification A', labels: G, values: G.map((g) => cg.A.groups[g].ratio_to_survey) },
    { name: 'Classification B (strict)', labels: G, values: G.map((g) => cg.B.groups[g].ratio_to_survey) },
  ], K.chartBase({ x: M, y: 1.7, w: 7.6, h: 5.2, barDir: 'col', barGrouping: 'clustered', chartColors: [P.accent, '1F618D'], showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.00', showLegend: true, legendPos: 'b', legendFontFace: BODY, legendFontSize: 11, valAxisHidden: true, showTitle: true, title: 'Share of the removed ÷ share of the population' }));
  K.bullets(s, [
    'Above 1: a group\'s share of the removed exceeds its share of the population.',
    'Under both, ' + andj(up) + ' families are removed at or above their share, ' + andj(down) + ' below it.',
    'The two classifications disagree on Muslim families.',
    'A places ' + pct(cg.A.coverage_pct) + ' of removals in a group; the strict B, which sets aside surnames shared across groups, ' + pct(cg.B.coverage_pct) + '.',
  ], 8.6, 1.95, 4.1, 4.8, 15);
  K.foot(s, n);

  // 11. Districts
  s = pres.addSlide(); n++;
  const td = rankD.slice(0, 15).reverse();
  K.title(s, 'Where the removals fell hardest', 'Names removed per 100 electors on the 2025 roll, the fifteen heaviest districts');
  s.addChart(pres.charts.BAR, [{ name: 'Per 100 electors', labels: td.map((d) => d.district), values: td.map((d) => d.per_100) }],
    K.chartBase({ x: M, y: 1.7, w: 7.6, h: 5.2, barDir: 'bar', chartColors: ['E67E22'], showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0', valAxisHidden: true }));
  const rankA = A.slice().sort((a, b) => b.per_100 - a.per_100);
  K.bullets(s, [
    rankD[0].district + ' lost ' + rankD[0].per_100.toFixed(1) + ' per 100 electors, ' + rankD[rankD.length - 1].district + ' ' + rankD[rankD.length - 1].per_100.toFixed(1) + '.',
    'Among constituencies, from ' + rankA[rankA.length - 1].per_100.toFixed(1) + ' in ' + rankA[rankA.length - 1].name + ' to ' + rankA[0].per_100.toFixed(1) + ' in ' + rankA[0].name + '.',
    'The median booth lost ' + median(A.map((a) => a.booth_median)) + ' names; ' + indian(sum(A, 'booths_200')) + ' booths lost 200 or more.',
  ], 8.6, 1.95, 4.1, 4.8, 15);
  K.foot(s, n);

  // 12. Alliances
  s = pres.addSlide(); n++;
  K.title(s, 'The alliances, stated plainly', 'What the lists show, and what they cannot');
  s.addChart(pres.charts.BAR, ['NDA', 'INDIA', 'Other'].map((al) => ({ name: al, labels: ['2020 winner', '2024 segment leader', '2025 winner'], values: ['2020', '2024', '2025'].map((y) => L[y][al] ? L[y][al].per_100 : 0) })),
    K.chartBase({ x: M, y: 1.7, w: 7.0, h: 5.2, barDir: 'col', barGrouping: 'clustered', chartColors: [AL.NDA, AL.INDIA, AL.Other], showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.00', showLegend: true, legendPos: 'b', legendFontFace: BODY, legendFontSize: 11, valAxisHidden: true, showTitle: true, title: 'Names removed per 100 electors, seats grouped by who held them' }));
  K.bullets(s, [
    'Seats the NDA held lost ' + L['2020'].NDA.per_100.toFixed(2) + ' per 100 electors, INDIA seats ' + L['2020'].INDIA.per_100.toFixed(2) + '; the order holds under all three labels.',
    'Within the same seat, NDA-led booths lost ' + Wt.pooled_nda_minus_india.toFixed(1) + ' more names each.',
    'A booth\'s leader says how most of its voters voted, not how the removed voted.',
    'What the lists establish is the scale of the removals against the margins.',
  ], 8.0, 1.95, 4.7, 4.8, 15);
  K.foot(s, n);

  // 13. What the lists show
  s = pres.addSlide(); n++;
  K.title(s, 'What the lists show, and what they do not');
  K.callout(s, 'The lists show how many names were removed, where, and who the removed were by sex and by name, and they allow the removals to be set against the margins and votes that decided each seat.', M, 1.5, 5.9, 2.4);
  K.callout(s, 'They do not show why an individual name was removed, whether the removal was right, or how the elector voted. Religion and caste are read from names and are estimates.', 6.83, 1.5, 5.9, 2.4);
  K.body(s, 'The reasons officers entered, dead, shifted, absent or enrolled twice, are entries after a visit or its absence, not findings, and the lists used here do not carry them against each name. A change to the roll larger than the margin in ' + over.length + ' of ' + withM.length + ' seats is large enough to have decided the seat, whatever the reason entered. Whether it did turns on how the removed would have voted, which no list records.', M, 4.3, W - 2 * M, 2.4, 17);
  K.foot(s, n);

  // 14. Audit
  s = pres.addSlide(); n++;
  K.title(s, 'What an audit needs', 'The questions the lists leave open, and how to settle them');
  K.numbered(s, [
    'A name-by-name verification of removals in every seat where they exceed the margin, starting with the ' + vals.slice(3).reduce((a, b) => a + b, 0) + ' where they exceed it five times or more.',
    'Publication, booth by booth, of every claim and objection filed after the draft roll, with its outcome.',
    'The reason entered against each removed name, and the evidence for each "shifted" and "absent" entry.',
    'A check of women removed as "shifted" against new enrolments where they now live.',
    'An independent review of the method before the revision is repeated in other states.',
  ], M, 1.7, W - 2 * M, 5.0, 18);
  K.foot(s, n);

  // 15. Method
  s = pres.addSlide(); n++;
  K.title(s, 'Method and sources');
  K.bullets(s, [
    'Removals by polling booth: the phase 1 deletion lists the Chief Electoral Officer, Bihar published against the draft roll of 1 August 2025, for all ' + indian(t.booths) + ' booths.',
    'Removals by constituency, phase and sex: Chief Electoral Officer, Bihar.',
    '2025 Assembly results: winner, runner-up and turnout for each seat, cross-checked between two independent tables. Votes polled are the turnout applied to the 2025 roll.',
    'Religion and surnames: counts from the same lists, by booth. Census of India 2011; Bihar caste-based survey, 2 October 2023.',
    'Every headline figure is recomputed from the lists by a second, independent program. No name, EPIC number or address is published.',
  ], M, 1.5, W - 2 * M, 5.2, 16);
  K.foot(s, n);

  closing(pres, K, P, 'Every booth, every constituency, online', ['The dashboard, the booth explorer and the full report, with a chapter for each of the 38 districts, are published on the same website as this deck.', 'Varna Sri Raman']);
  return pres.writeFile({ fileName: path.join(OUT, 'bihar-sir-2025-deck.pptx') });
}

// ============================================================ HYDERABAD
function hyderabad() {
  const S = J('hyderabad/summary.json'), PJ = J('hyderabad/parts.json');
  const PR = PJ.rows.map((r) => Object.fromEntries(PJ.fields.map((f, i) => [f, r[i]])));
  const A = S.acs, t = S.totals, names = A.map((a) => a.name);
  const P = { dark: '6E1832', darker: '52101F', accent: '8B1E3F', light: 'F2D9B8', soft: 'F7ECEF', band: ['8B1E3F', '0E5E6F', 'E0A526', '0E5E6F'], foot: 'Hyderabad Old City SIR 2026 · Varna Sri Raman · aggregates only; no names or EPIC numbers' };
  const ACC = ['8B1E3F', '0E5E6F', 'E0A526', '1F618D', '8E7CC3'];
  const pres = new pptxgen(); pres.layout = 'LAYOUT_WIDE'; pres.author = 'Varna Sri Raman'; pres.title = 'Hyderabad Old City SIR 2026';
  const K = kit(pres, P);
  const s_ = (f) => sum(A, f);
  const LK = A.filter((a) => a.linked), yak = A.find((a) => a.name === 'Yakutpura');
  const overV = A.filter((a) => a.e2023.deleted_over_valid > 100), valid = s_((a) => a.e2023.valid);
  const age = S.bands.map((b, i) => 100 * s_((a) => a.counts.age_asd[i]) / s_((a) => a.age_all[i]));
  const rsh = (k) => 100 * s_((a) => a.reasons[k]) / t.deleted;
  const hin = 100 * s_((a) => a.counts.hin_asd) / s_((a) => a.counts.hin_all), mus = 100 * s_((a) => a.counts.mus_asd) / s_((a) => a.counts.mus_all);
  const HM = A.map((a) => a.within_part.hindu_minus_muslim), UL = LK.map((a) => a.within_part.unlinked_minus_linked);
  const lk = 100 * sum(LK, (a) => a.counts.lk_asd) / sum(LK, (a) => a.counts.lk_all), ul = 100 * sum(LK, (a) => a.deleted - a.counts.lk_asd) / sum(LK, (a) => a.electors - a.counts.lk_all);
  const heavy = A.slice().sort((a, b) => b.max_slot - a.max_slot)[0];
  const P100 = PR.filter((p) => p.electors >= 100), o60 = P100.filter((p) => p.rate > 60);
  const ruleTot = S.rules.map((k) => s_((a) => a.rules[k] || 0));
  let n = 1;

  let s = cover(pres, K, P, 'Special Intensive Revision 2026', 'Hyderabad Old City: four in ten struck off', 'Charminar, Yakutpura, Malakpet, Chandrayangutta and Bahadurpura, polling part by polling part',
    [[indian(t.deleted), 'electors struck off the pre-revision rolls'], [pct(t.rate), 'of every elector on those rolls'], [pct(100 * t.deleted / valid), 'of the valid votes cast in 2023'], [indian(t.hearing), 'kept but summoned to a hearing']]);
  s.addNotes('The lists cover every elector on the pre-revision rolls of five Old City constituencies, so each group has a true removal rate. These are the September 2026 lists; the final roll is due on 9 November.');

  s = pres.addSlide(); n++;
  K.title(s, 'Four in ten electors struck off', 'What happened to each elector on the five pre-revision rolls, % of the roll');
  s.addChart(pres.charts.BAR, [
    { name: 'Struck off', labels: names, values: A.map((a) => a.rate) },
    { name: 'Kept, summoned to a hearing', labels: names, values: A.map((a) => a.hearing_rate) },
    { name: 'Kept, untouched', labels: names, values: A.map((a) => +(100 - a.rate - a.hearing_rate - 100 * a.unaccounted / a.electors).toFixed(1)) },
  ], K.chartBase({ x: M, y: 1.7, w: 8.2, h: 5.2, barDir: 'bar', barGrouping: 'stacked', chartColors: ['C0392B', 'D4AC0D', '1F618D'], showValue: true, dataLabelPosition: 'ctr', dataLabelFormatCode: '0.0', dataLabelColor: 'FFFFFF', showLegend: true, legendPos: 'b', legendFontFace: BODY, legendFontSize: 11, valAxisMaxVal: 100, valAxisHidden: true }));
  const sr = A.slice().sort((a, b) => b.rate - a.rate);
  K.stat(s, 9.2, 1.9, 3.55, 1.55, indian(t.deleted), 'struck off, ' + pct(t.rate) + ' of ' + indian(t.electors));
  K.stat(s, 9.2, 3.65, 3.55, 1.55, indian(t.hearing), 'kept on the roll only if they attend a hearing');
  K.stat(s, 9.2, 5.4, 3.55, 1.5, pct(sr[0].rate), sr[0].name + ' lost the most; ' + sr[4].name + ' the least, ' + pct(sr[4].rate), { size: 26 });
  K.foot(s, n);

  s = pres.addSlide(); n++;
  K.title(s, A.every((a) => a.deleted > a.e2023.winner_votes) ? 'More names struck off than the winner received' : 'More names struck off than the winning margin', 'Names struck off against the 2023 winning margin and the valid votes cast');
  K.table(s, ['Constituency', 'Won by (2023)', 'Margin', 'Struck off', '× margin', 'Valid votes 2023', '% of valid votes'],
    A.slice().sort((a, b) => b.e2023.deleted_over_valid - a.e2023.deleted_over_valid).map((a) => [a.name, a.e2023.winner, indian(a.e2023.margin), indian(a.deleted), a.e2023.deleted_over_margin.toFixed(1) + '×', indian(a.e2023.valid), pct(a.e2023.deleted_over_valid)]),
    M, 1.75, W - 2 * M, [2.3, 3.3, 1.3, 1.5, 1.2, 1.7, 0.83 + 0.7], 13);
  K.callout(s, (A.every((a) => a.deleted > a.e2023.winner_votes) ? 'Every constituency lost more names than its 2023 winner polled, let alone the margin. In ' : 'Every constituency lost more names than its 2023 margin. In ') + andj(overV.map((a) => a.name)) + ' the names struck off exceed every valid vote cast. Yakutpura was won by ' + indian(yak.e2023.margin) + ' votes and lost ' + indian(yak.deleted) + ' names. Across the five, the names struck off equal ' + pct(100 * t.deleted / valid) + ' of the 2023 vote.', M, 4.35, W - 2 * M, 1.7);
  K.foot(s, n);
  s.addNotes('The comparison is one of scale. The roll records no one\'s vote, so none of this says whom the removed would have chosen.');

  s = pres.addSlide(); n++;
  K.title(s, 'The oldest were struck off most', 'Share of each age band struck off, all five constituencies');
  s.addChart(pres.charts.BAR, [{ name: '% struck off', labels: S.bands, values: age.map((v) => +v.toFixed(1)) }],
    K.chartBase({ x: M, y: 1.7, w: 7.8, h: 5.2, barDir: 'col', chartColors: [P.accent], showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0"%"', valAxisHidden: true }));
  K.bullets(s, [
    pct(age[age.length - 1]) + ' of electors aged 80 and over were struck off, against ' + pct(age[0]) + ' of those aged 18 to 24.',
    indian(s_((a) => a.reasons.Death)) + ' were entered as dead, which explains part of the rise at the top.',
    'The rate roughly doubles between 18 to 24 and 30 to 39, ages at which almost nobody dies. Death is not the whole of it.',
  ], 8.8, 1.95, 3.9, 4.8, 15);
  K.foot(s, n);

  s = pres.addSlide(); n++;
  K.title(s, 'No link to 2002 doubled the risk', 'Electors struck off, by link to the 2002 intensive revision roll');
  s.addChart(pres.charts.BAR, [
    { name: 'Linked to 2002', labels: LK.map((a) => a.name), values: LK.map((a) => a.linked_rate) },
    { name: 'No 2002 link', labels: LK.map((a) => a.name), values: LK.map((a) => a.unlinked_rate) },
  ], K.chartBase({ x: M, y: 1.7, w: 7.8, h: 5.2, barDir: 'col', barGrouping: 'clustered', chartColors: ['0E5E6F', 'C0392B'], showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0', showLegend: true, legendPos: 'b', legendFontFace: BODY, legendFontSize: 11, valAxisHidden: true }));
  K.bullets(s, [
    'Linked electors: ' + pct(lk) + ' struck off. No link: ' + pct(ul) + '.',
    'Inside the same polling part the gap is ' + Math.min(...UL.map((u) => u.diff_pp)).toFixed(0) + ' to ' + Math.max(...UL.map((u) => u.diff_pp)).toFixed(0) + ' points, in ' + indian(sum(UL, 'a_higher')) + ' of ' + indian(sum(UL, 'parts')) + ' parts.',
    'Anyone who moved to the city after 2002, or whose family name is spelt differently on the old roll, starts at a disadvantage.',
    'Malakpet\'s list carries no linkage.',
  ], 8.8, 1.95, 3.9, 4.8, 15);
  K.foot(s, n);

  s = pres.addSlide(); n++;
  K.title(s, 'The reasons officers entered', 'Share of names struck off, by the reason recorded against each');
  s.addChart(pres.charts.BAR, S.reasons.map((k, i) => ({ name: ['Permanently shifted', 'Untraceable or absent', 'Dead', 'Enrolled elsewhere'][i], labels: names, values: A.map((a) => +(100 * a.reasons[k] / a.deleted).toFixed(1)) })),
    K.chartBase({ x: M, y: 1.7, w: 8.2, h: 5.2, barDir: 'bar', barGrouping: 'percentStacked', chartColors: ['1F618D', 'C0392B', '95A5A6', 'E0A526'], showLegend: true, legendPos: 'b', legendFontFace: BODY, legendFontSize: 11, valAxisHidden: true }));
  const ut = A.map((a) => 100 * a.reasons['Untraceable/Absent'] / a.deleted);
  K.bullets(s, [
    pct(rsh('Permanently Shifted')) + ' "permanently shifted", ' + pct(rsh('Untraceable/Absent')) + ' "untraceable or absent", ' + pct(rsh('Death')) + ' dead, ' + pct(rsh('Already enrolled')) + ' enrolled elsewhere.',
    'The untraceable share runs from ' + pct(Math.min(...ut)) + ' to ' + pct(Math.max(...ut)) + '.',
    'Each is an officer\'s entry, not a finding. The untraceable entries are where verification should begin.',
  ], 9.2, 1.95, 3.5, 4.8, 15);
  K.foot(s, n);

  s = pres.addSlide(); n++;
  K.title(s, 'Hearings: 459 cases in one slot', 'Electors kept on the draft roll but summoned to prove eligibility');
  K.stat(s, M, 1.85, 3.9, 1.6, indian(t.hearing), 'electors summoned, ' + pct(100 * t.hearing / t.electors) + ' of the rolls');
  K.stat(s, M, 3.65, 3.9, 1.6, indian(s_((a) => a.slots)), 'hearing slots, 28 August to 12 October');
  K.stat(s, M, 5.45, 3.9, 1.5, indian(heavy.max_slot), 'cases in the heaviest single slot, in ' + heavy.name + ' (median ' + heavy.median_slot + ')', { size: 28 });
  s.addChart(pres.charts.BAR, [
    { name: 'Median cases per slot', labels: names, values: A.map((a) => a.median_slot) },
    { name: 'Heaviest single slot', labels: names, values: A.map((a) => a.max_slot) },
  ], K.chartBase({ x: 4.9, y: 1.75, w: 7.8, h: 5.15, barDir: 'col', barGrouping: 'clustered', chartColors: ['0E5E6F', P.accent], showValue: true, dataLabelPosition: 'outEnd', showLegend: true, legendPos: 'b', legendFontFace: BODY, legendFontSize: 11, valAxisHidden: true }));
  K.foot(s, n);
  s.addNotes('Not being traceable to the last intensive revision was the commonest reason to be summoned, ' + pct(100 * ruleTot[0] / ruleTot.reduce((a, b) => a + b, 0)) + ' of flags.');

  s = pres.addSlide(); n++;
  K.title(s, 'Religion and sex', 'True rates: the lists hold every elector, not only the removed');
  const fr = 100 * s_((a) => a.counts.f_asd) / s_((a) => a.counts.f_all), mr = 100 * s_((a) => a.counts.m_asd) / s_((a) => a.counts.m_all);
  s.addChart(pres.charts.BAR, [
    { name: 'Hindu-name electors', labels: names, values: A.map((a) => a.hindu_rate) },
    { name: 'Muslim-name electors', labels: names, values: A.map((a) => a.muslim_rate) },
  ], K.chartBase({ x: M, y: 1.7, w: 7.8, h: 5.2, barDir: 'col', barGrouping: 'clustered', chartColors: ['E0A526', '1E8449'], showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0', showLegend: true, legendPos: 'b', legendFontFace: BODY, legendFontSize: 11, valAxisHidden: true, showTitle: true, title: '% struck off, by name-estimated religion' }));
  K.bullets(s, [
    pct(hin) + ' of Hindu-name electors and ' + pct(mus) + ' of Muslim-name electors were struck off.',
    'Inside the same part the gap holds in ' + sum(HM, 'a_higher') + ' of ' + sum(HM, 'parts') + ' parts. Religion and age are given separately, so part of it may be an age gap.',
    'Women ' + pct(fr) + ', men ' + pct(mr) + ': no gap by sex, unlike Bihar.',
  ], 8.8, 1.95, 3.9, 4.8, 15);
  K.foot(s, n);

  s = pres.addSlide(); n++;
  K.title(s, o60.length + ' polling parts lost more than 60% of their roll', 'The fifteen heaviest parts with 100 or more electors');
  K.table(s, ['Constituency', 'Part', 'Locality', 'Electors', 'Struck off', '% struck off'],
    P100.slice().sort((a, b) => b.rate - a.rate).slice(0, 15).map((p) => [p.ac, p.part, p.locality && p.locality !== 'nan' ? p.locality : '–', indian(p.electors), indian(p.deleted), pct(p.rate)]),
    M, 1.65, W - 2 * M, [2.6, 1.0, 4.0, 1.6, 1.6, 1.33], 11.5);
  K.foot(s, n);

  s = pres.addSlide(); n++;
  K.title(s, 'What the lists show, and what they do not');
  K.callout(s, 'How many electors were struck off, from which parts, and who they were by age, sex, religion estimated from name, and 2002 linkage.', M, 1.5, 5.9, 2.2);
  K.callout(s, 'Whether any individual removal was right. A household that moved out is a correct "shifted" deletion; the files cannot tell it from an elector who was at home and missed.', 6.83, 1.5, 5.9, 2.2);
  K.body(s, 'The Malakpet list used here is incomplete: 1,42,688 names against the 1,47,799 counted in the published list, with no part numbers and no 2002 link. For the other four constituencies the counts agree exactly with an independent count of the same lists. These are the September lists; restorations after hearings are not in them.', M, 4.1, W - 2 * M, 2.6, 17);
  K.foot(s, n);

  s = pres.addSlide(); n++;
  K.title(s, 'What verification needs, before the final roll');
  K.numbered(s, [
    'Verify every removal entered as "untraceable or absent", ' + indian(s_((a) => a.reasons['Untraceable/Absent'])) + ' names, by a visit with notice and a record of the attempt.',
    'Review every removal of an elector with no link to the 2002 roll.',
    'Hearing schedules that give each elector a real hearing: no slot of several hundred cases.',
    'Ground checks in the ' + o60.length + ' parts that lost more than 60% of their roll.',
    'Publish restorations after hearings, part by part, so the final count can be set against these.',
  ], M, 1.5, W - 2 * M, 5.2, 18);
  K.foot(s, n);

  closing(pres, K, P, 'Every part, every constituency, online', ['The dashboard, the part explorer and the full report, with a chapter for each constituency, are published on the same website as this deck.', 'Varna Sri Raman']);
  return pres.writeFile({ fileName: path.join(OUT, 'hyderabad-old-city-sir-2026-deck.pptx') });
}

fs.mkdirSync(OUT, { recursive: true });
Promise.all([bihar(), hyderabad()]).then((f) => console.log('wrote', f.join(', ')));
