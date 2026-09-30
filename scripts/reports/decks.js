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
const orj = (xs) => xs.length === 1 ? xs[0] : xs.slice(0, -1).join(', ') + ' or ' + xs[xs.length - 1];
const andj = (xs) => xs.length === 1 ? xs[0] : xs.slice(0, -1).join(', ') + ' and ' + xs[xs.length - 1];

const pearson = (x, y) => { const n = x.length, mx = sum(x, (v) => v) / n, my = sum(y, (v) => v) / n; let a = 0, b = 0, c = 0; for (let i = 0; i < n; i++) { a += (x[i] - mx) * (y[i] - my); b += (x[i] - mx) ** 2; c += (y[i] - my) ** 2; } return a / Math.sqrt(b * c); };
const ranks = (x) => { const o = x.map((v, i) => [v, i]).sort((p, q) => p[0] - q[0]), r = new Array(x.length); for (let i = 0; i < o.length;) { let j = i; while (j + 1 < o.length && o[j + 1][0] === o[i][0]) j++; for (let k = i; k <= j; k++) r[o[k][1]] = (i + j) / 2 + 1; i = j + 1; } return r; };
const spearman = (x, y) => pearson(ranks(x), ranks(y));
const per100 = (rows) => 100 * sum(rows, 'total') / sum(rows, 'electorate_2025');

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
    const rows = K.sections.map((x, i) => [x.name, String(x.from) + (K.sections[i + 1] ? '–' + (K.sections[i + 1].from - 1) : '–' + K.n)]);
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
  s.addText('Varna Sri Raman', { x: M, y: 6.3, w: 8, h: 0.4, fontFace: BODY, fontSize: 13, color: P.light, margin: 0, isTextBox: true });
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

// ============================================================ BIHAR
function bihar() {
  const S = J('bihar/summary.json'), A = J('bihar/constituencies.json'), DS = J('bihar/districts.json'), ID = J('bihar/identity.json'), RS = J('bihar/reasons.json');
  const t = S.totals, DI = ID.districts;
  const P = { dark: '8E2F25', darker: '6E231C', accent: 'B03A2E', light: 'F5D6C6', soft: 'FBEFE8', band: ['C0392B', 'E67E22', '27AE60', '1F618D', '8E44AD'], foot: 'Bihar SIR 2025 · Varna Sri Raman · aggregates only; no names or EPIC numbers' };
  const AL = { NDA: 'E67E22', INDIA: '1E8449', Other: '8E7CC3' };
  const pres = new pptxgen(); pres.layout = 'LAYOUT_WIDE'; pres.author = 'Varna Sri Raman'; pres.title = 'Bihar SIR 2025';
  const K = kit(pres, P);
  const withM = A.filter((a) => a.margin2025), over = withM.filter((a) => a.total > a.margin2025);
  const nda = withM.filter((a) => a.al2025 === 'NDA'), ndaO = nda.filter((a) => a.total > a.margin2025);
  const took = withM.filter((a) => a.al2020 === 'INDIA' && a.al2025 === 'NDA'), tookO = took.filter((a) => a.total > a.margin2025);
  const polled = sum(A, 'votes2025'), mAll = sum(withM, 'margin2025'), mNDA = sum(nda, 'margin2025'), tookRem = sum(took, 'total'), tookM = sum(took, 'margin2025');
  const share = (a) => 100 * a.total / a.votes2025, ratio = (a) => a.total / a.margin2025;
  const fem = 100 * t.female / (t.female + t.male), p100 = 100 * t.total / t.electorate_2025;
  const cls = t.hindu + t.muslim + t.unknown, mlo = 100 * t.muslim / cls, mhi = 100 * (t.muslim + t.unknown) / cls;
  const fOver = DI.filter((d) => d.female_share_deleted > d.female_share_population_2011);
  const above = DI.filter((d) => d.muslim_share_deleted_low > d.muslim_share_population_2011 + 1).sort((a, b) => (b.muslim_share_deleted_low / b.muslim_share_population_2011) - (a.muslim_share_deleted_low / a.muslim_share_population_2011));
  const inside = DI.filter((d) => d.muslim_share_deleted_low <= d.muslim_share_population_2011 && d.muslim_share_population_2011 <= d.muslim_share_deleted_high);
  const rankD = DS.slice().sort((a, b) => b.per_100 - a.per_100), rankA = A.slice().sort((a, b) => b.per_100 - a.per_100);
  const LB = S.by_alliance_label, Wt = S.within_seat_2024, F5 = S.intensity.within_seat_fifths, BH = S.booth_histogram;
  const cuts = [0, 1, 2, 5, 10, 20, 1e9], labs = ['under 1×', '1–2×', '2–5×', '5–10×', '10–20×', '20× or more'];
  const vals = labs.map((l, i) => withM.filter((a) => ratio(a) >= cuts[i] && ratio(a) < cuts[i + 1]).length), five = sum(vals.slice(3), (v) => v);
  const smallest = withM.slice().sort((a, b) => a.margin2025 - b.margin2025)[0];
  const RK = ['shifted', 'dead', 'absent', 'already_enrolled'], RNm = { shifted: 'Shifted', dead: 'Dead', absent: 'Absent', already_enrolled: 'Already enrolled' }, RCol = { shifted: '1F618D', dead: GREY, absent: 'C0392B', already_enrolled: 'D4AC0D' };
  const RT = RS.totals, rsh = (k) => 100 * RT[k] / RS.total;
  const xsF = sum(RK, (k) => RS.by_sex[k].F - RS.by_sex[k].M), xsS = RS.by_sex.shifted.F - RS.by_sex.shifted.M;
  const yS = RS.by_age.shifted[0] + RS.by_age.shifted[1], yW = RS.by_age_women.shifted[0] + RS.by_age_women.shifted[1];
  const rOver = (k) => withM.filter((a) => a[k] > a.margin2025).length;
  const dsum = (d) => sum(RK, (k) => d[k]), RD = RS.districts.slice().sort((a, b) => b.absent / dsum(b) - a.absent / dsum(a));
  const ageTot = RS.bands.map((b, i) => sum(RK, (k) => RS.by_age[k][i]));
  const b200 = sum(Object.keys(BH).filter((k) => parseInt(k, 10) >= 200), (k) => BH[k]);

  cover(pres, K, P, 'Special Intensive Revision · Bihar 2025', 'The 2025 revision removed ' + lakh(t.total) + ' names from Bihar\'s electoral roll',
    'What the deletion lists show, booth by booth, set against the Assembly election that followed',
    [[indian(t.total), 'names removed across both phases'], [pct(100 * t.total / polled), 'of the votes polled in November 2025'], [over.length + ' of ' + withM.length, 'seats where removals exceed the winning margin'], [pct(fem), 'of the removed are women']])
    .addNotes('Every figure in this deck is computed from the Chief Electoral Officer\'s deletion lists and the 2025 results, the same data the website and the full report use. No name or EPIC number is published.');
  const toc = contentsSlide(pres, K, P);

  // ---- Scale
  let s = K.slide('The scale', lakh(t.total) + ' names removed, ' + p100.toFixed(2) + ' for every 100 electors', 'Phase 1 before the draft roll of 1 August 2025, phase 2 before the final roll');
  K.stats(s, [[indian(t.total), 'names removed in all'], [indian(t.p1), 'in phase 1, before the draft roll'], [indian(t.p2), 'in phase 2, before the final roll'],
    [p100.toFixed(2), 'removed per 100 electors on the 2025 roll'], [indian(t.booths), 'polling booths, every one in the lists'], [indian(t.electorate_2025), 'electors on the 2025 roll']], TOP, 2.05, 3);
  s.addNotes('Per 100 electors divides by the 2025 electorate. Votes polled, used later, are the 2025 turnout applied to the same roll.');

  s = K.slide('The scale', 'Most booths lost fewer than 100 names; ' + indian(b200) + ' lost 200 or more', 'Booths by the number of names removed in phase 1, the phase listed booth by booth');
  s.addChart(pres.charts.BAR, [{ name: 'Booths', labels: Object.keys(BH), values: Object.values(BH) }], K.chart(Object.assign({}, K.left, { barDir: 'col', chartColors: Object.keys(BH).map((k) => parseInt(k, 10) >= 200 ? P.accent : GREY), showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '#,##0', valAxisHidden: true, catAxisTitle: 'Names removed per booth', showCatAxisTitle: true })));
  K.right(s, [
    'The median booth lost ' + median(A.map((a) => a.booth_median)) + ' names.',
    indian(BH['400+']) + ' booths lost 400 or more.',
    'By constituency, removals ran from ' + rankA[rankA.length - 1].per_100.toFixed(1) + ' per 100 electors in ' + rankA[rankA.length - 1].name + ' to ' + rankA[0].per_100.toFixed(1) + ' in ' + rankA[0].name + '.',
  ]);

  // ---- Elections
  // ---- Reasons
  s = K.slide('Reasons', pct(rsh('shifted'), 0) + ' of phase 1 removals were entered as shifted and ' + pct(rsh('dead'), 0) + ' as dead', 'The reason the officer entered against each of the ' + indian(RS.total) + ' names removed in phase 1, by sex');
  s.addChart(pres.charts.BAR, [
    { name: 'Women', labels: RK.map((k) => RNm[k]), values: RK.map((k) => RS.by_sex[k].F) },
    { name: 'Men', labels: RK.map((k) => RNm[k]), values: RK.map((k) => RS.by_sex[k].M) },
  ], K.chart(Object.assign({}, K.left, { barDir: 'col', barGrouping: 'clustered', chartColors: ['AF3B6E', '1F618D'], showLegend: true, valAxisLabelFormatCode: '#,##0' })));
  K.right(s, [
    'Shifted ' + indian(RT.shifted) + ', dead ' + indian(RT.dead) + ', absent ' + indian(RT.absent) + ', already enrolled ' + indian(RT.already_enrolled) + '.',
    indian(xsS) + ' of the ' + indian(xsF) + ' more women than men removed in phase 1 were entered as shifted.',
    'A reason is an officer\'s entry after a visit or its absence, not a finding. The ' + indian(t.p2) + ' phase 2 removals carry no reason in the lists.',
  ], 13.5);
  s.addNotes('Counted from the row-level phase 1 list as entered. The counts agree with the booth list in all ' + indian(t.booths) + ' booths, and the women and men with the Chief Electoral Officer\'s phase 1 figures in every constituency.');

  s = K.slide('Reasons', 'Among those marked shifted aged 18 to 29, ' + pct(100 * yW / yS) + ' are women', 'The reason entered, as a share of the removed in each age band');
  s.addChart(pres.charts.BAR, ['dead', 'shifted', 'absent', 'already_enrolled'].map((k) => ({ name: RNm[k], labels: RS.bands, values: RS.bands.map((b, i) => +(100 * RS.by_age[k][i] / ageTot[i]).toFixed(1)) })),
    K.chart(Object.assign({}, K.left, { barDir: 'col', barGrouping: 'percentStacked', chartColors: ['dead', 'shifted', 'absent', 'already_enrolled'].map((k) => RCol[k]), showLegend: true, valAxisHidden: true })));
  K.right(s, [
    'Dead is ' + pct(100 * RS.by_age.dead[RS.bands.length - 1] / ageTot[RS.bands.length - 1]) + ' of the removed aged 80 and over, and ' + pct(100 * RS.by_age.dead[0] / ageTot[0]) + ' of those aged 18 to 24.',
    'Women are ' + pct(100 * yW / yS) + ' of those aged 18 to 29 marked shifted, and about half of those aged 50 and over: the pattern women who move on marriage would produce.',
    'The lists do not show whether any of them were enrolled again where they now live.',
  ], 13.5);

  s = K.slide('Reasons', 'Names marked absent alone exceed the 2025 margin in ' + rOver('r_absent') + ' of ' + withM.length + ' seats', 'Seats where the names removed for one reason exceed the winning margin; districts with the highest absent share');
  s.addChart(pres.charts.BAR, ['NDA', 'INDIA', 'Other'].map((al) => ({ name: al, labels: ['Dead', 'Shifted', 'Absent', 'Already enrolled'], values: ['r_dead', 'r_shifted', 'r_absent', 'r_enrolled'].map((k) => withM.filter((a) => a[k] > a.margin2025 && a.al2025 === al).length) })),
    K.chart(Object.assign({}, K.left, { w: 6.2, barDir: 'col', barGrouping: 'stacked', chartColors: [AL.NDA, AL.INDIA, AL.Other], showLegend: true, showTitle: true, title: 'Seats, by the alliance that won in 2025' })));
  K.table(s, ['District', 'Absent', 'Shifted', 'Dead'], RD.slice(0, 8).map((d) => [d.district, pct(100 * d.absent / dsum(d)), pct(100 * d.shifted / dsum(d)), pct(100 * d.dead / dsum(d))]), 7.1, TOP, W - M - 7.1, [2.2, 1.1, 1.1, 1.23], 12);
  s.addNotes('Absent rests on the least of the four reasons: it records only that the elector was not found. Already enrolled is a removal only if the other entry is the same person. Shifted exceeds the margin in ' + rOver('r_shifted') + ' seats, dead in ' + rOver('r_dead') + ', already enrolled in ' + rOver('r_enrolled') + '.');

  s = K.slide('Elections', 'In ' + over.length + ' of ' + withM.length + ' seats, more names were removed than the 2025 winning margin', 'Constituencies by names removed as a multiple of the margin');
  s.addChart(pres.charts.BAR, [{ name: 'Constituencies', labels: labs, values: vals }], K.chart(Object.assign({}, K.left, { barDir: 'col', chartColors: [GREY, P.accent, P.accent, P.accent, P.accent, P.accent], showValue: true, dataLabelPosition: 'outEnd', valAxisHidden: true })));
  K.stats(s, [[five + ' seats', 'where removals were five times the margin or more'], [median(withM.map(ratio)).toFixed(2) + '×', 'removals against the margin in the median seat'], [indian(smallest.margin2025) + ' votes', smallest.name + '\'s margin, with ' + indian(smallest.total) + ' names removed']], TOP, 1.45, 1, 8.65, W - M - 8.65);
  s.addNotes('Grey: the ' + vals[0] + ' seats where removals were below the margin. Of the ' + over.length + ' seats above it, the NDA won ' + over.filter((a) => a.al2025 === 'NDA').length + ', INDIA ' + over.filter((a) => a.al2025 === 'INDIA').length + ' and others ' + over.filter((a) => a.al2025 === 'Other').length + '.');

  s = K.slide('Elections', lakh(t.total) + ' names removed, against a combined NDA winning margin of ' + lakh(mNDA), 'Names removed set against the sum of the winning margins in each group of seats, in lakh');
  const grp = ['All ' + withM.length + ' seats', 'The NDA\'s ' + nda.length + ' wins', 'The ' + took.length + ' seats the NDA took from INDIA'];
  s.addChart(pres.charts.BAR, [
    { name: 'Names removed', labels: grp, values: [t.total, sum(nda, 'total'), tookRem].map((v) => +(v / 1e5).toFixed(1)) },
    { name: 'Combined winning margins', labels: grp, values: [mAll, mNDA, tookM].map((v) => +(v / 1e5).toFixed(1)) },
  ], K.chart(Object.assign({}, K.left, { barDir: 'col', barGrouping: 'clustered', chartColors: [P.accent, GREY], showValue: true, dataLabelPosition: 'outEnd', showLegend: true, valAxisHidden: true })));
  K.right(s, [
    'Across all ' + withM.length + ' seats, ' + lakh(t.total) + ' names were removed; the margins add up to ' + lakh(mAll) + '.',
    'The NDA won ' + nda.length + ' seats with a combined margin of ' + lakh(mNDA) + '. In ' + ndaO.length + ' of them the removals exceeded the margin.',
    'In the ' + took.length + ' seats the NDA took from INDIA, ' + lakh(tookRem) + ' names were removed against combined margins of ' + lakh(tookM) + '.',
  ]);
  s.addNotes('A combined margin is the sum of each seat\'s margin of victory. The comparison measures size only; the lists do not say how the removed would have voted.');

  s = K.slide('Elections', 'The twelve seats where removals were largest relative to the margin', 'Names removed against the 2025 winning margin');
  K.table(s, ['Constituency', 'District', 'Won by', 'Margin', 'Names removed', '× margin', '% of votes polled'],
    withM.slice().sort((a, b) => ratio(b) - ratio(a)).slice(0, 12).map((a) => [a.ac + ' ' + a.name, a.district, a.win2025 + ' (' + a.al2025 + ')', indian(a.margin2025), indian(a.total), ratio(a).toFixed(1) + '×', pct(share(a))]),
    M, TOP - 0.2, W - 2 * M, [2.6, 2.2, 1.9, 1.3, 1.7, 1.3, 1.13], 12, [0, 1, 2]);

  s = K.slide('Elections', 'In ' + tookO.length + ' of the ' + took.length + ' seats the NDA took from INDIA, removals exceeded the NDA\'s margin', 'Seats INDIA won in 2020 and the NDA won in 2025');
  K.stats(s, [[tookO.length + ' of ' + took.length, 'seats where removals exceed the NDA\'s 2025 margin'], [median(took.map(ratio)).toFixed(1) + '×', 'removals against the margin in the median such seat'], [lakh(tookRem), 'names removed in these ' + took.length + ' seats']], TOP, 1.45, 1, M, 3.9);
  const tk = took.slice().sort((a, b) => ratio(b) - ratio(a)).slice(0, 12).reverse();
  s.addChart(pres.charts.BAR, [{ name: '× margin', labels: tk.map((a) => a.name), values: tk.map((a) => +ratio(a).toFixed(1)) }],
    K.chart({ x: 4.8, y: TOP - 0.1, w: 7.9, h: CH + 0.1, barDir: 'bar', chartColors: [P.accent], showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0"×"', valAxisHidden: true, valAxisLogScaleBase: 10, showTitle: true, title: 'Names removed ÷ NDA margin, the twelve largest (log scale)' }));

  s = K.slide('Elections', 'Removals equal ' + pct(100 * t.total / polled) + ' of the votes polled in 2025, and more than 15% in ' + A.filter((a) => share(a) > 15).length + ' seats', 'Names removed as a share of the votes polled, the fifteen highest seats');
  const bys = A.slice().sort((a, b) => share(b) - share(a)), tp = bys.slice(0, 15).reverse(), ru = A.filter((a) => a.total > a.runner_up_votes2025);
  s.addChart(pres.charts.BAR, [{ name: '% of votes polled', labels: tp.map((a) => a.name), values: tp.map((a) => +share(a).toFixed(1)) }],
    K.chart(Object.assign({}, K.left, { barDir: 'bar', chartColors: tp.map((a) => AL[a.al2025]), showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0"%"', valAxisHidden: true })));
  K.right(s, [
    'Across Bihar: ' + indian(t.total) + ' removed, ' + indian(polled) + ' votes polled, one removal for every ' + (polled / t.total).toFixed(1) + ' votes.',
    'Above 20% in ' + A.filter((a) => share(a) > 20).length + ' seats; highest in ' + bys[0].name + ', at ' + pct(share(bys[0])) + '.',
    ru.length ? 'In ' + andj(ru.map((a) => a.name)) + ', more names were removed than the runner-up polled.' : '',
    'Bar colour is the 2025 winner: orange NDA, green INDIA, purple neither.',
  ]);

  s = K.slide('Elections', 'Seats held by the NDA lost more names per elector than INDIA seats', 'Names removed per 100 electors, seats grouped three ways by who held them');
  s.addChart(pres.charts.BAR, ['NDA', 'INDIA', 'Other'].map((al) => ({ name: al, labels: ['2020 Assembly winner', '2024 Lok Sabha segment leader', '2025 Assembly winner'], values: ['2020', '2024', '2025'].map((y) => LB[y][al] ? LB[y][al].per_100 : 0) })),
    K.chart(Object.assign({}, K.left, { barDir: 'col', barGrouping: 'clustered', chartColors: [AL.NDA, AL.INDIA, AL.Other], showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.00', showLegend: true, valAxisHidden: true })));
  const gapsA = ['2020', '2024', '2025'].map((y) => LB[y].NDA.per_100 - LB[y].INDIA.per_100);
  K.right(s, [
    'Under each of the three groupings, NDA seats lost ' + Math.min(...gapsA).toFixed(2) + ' to ' + Math.max(...gapsA).toFixed(2) + ' more names per 100 electors than INDIA seats.',
    'Seats held by neither alliance, most of them in Seemanchal, lost the most: ' + LB['2020'].Other.per_100.toFixed(2) + ' per 100 by the 2020 winner.',
    'A seat\'s winner says how most of its voters voted, not how the removed voted.',
  ]);

  s = K.slide('Elections', 'Inside the same seat, booths the NDA led in 2024 lost ' + Wt.pooled_nda_minus_india.toFixed(1) + ' more names each', 'Booths compared with other booths in their own constituency, where the officer, the villages and the migration are the same');
  K.stats(s, [['+' + Wt.pooled_nda_minus_india.toFixed(1), 'more names per NDA-led booth than INDIA-led, same seat'], [Wt.seats_nda_higher + ' of ' + Wt.seats_compared, 'seats where NDA-led booths lost more'], [Wt.seats_india_higher + ' of ' + Wt.seats_compared, 'seats where INDIA-led booths lost more'], [indian(Wt.booths), 'booths compared']], TOP, 1.5, 4);
  s.addChart(pres.charts.BAR, [{ name: 'NDA-led share of booths', labels: F5.map((f) => ['Lightest', 'Second', 'Middle', 'Fourth', 'Heaviest'][f.fifth - 1] + ' fifth'), values: F5.map((f) => f.nda_pct) }],
    K.chart({ x: M, y: TOP + 1.75, w: 7.7, h: CH - 1.75, barDir: 'col', chartColors: [AL.NDA], showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0"%"', valAxisHidden: true, valAxisMinVal: 50, showTitle: true, title: 'Share of booths the NDA led, by fifth of removals within each seat' }));
  K.bullets(s, ['Rank each seat\'s booths into fifths by names removed. The NDA led ' + pct(F5[0].nda_pct) + ' of the lightest fifth and ' + pct(F5[4].nda_pct) + ' of the heaviest.', 'Every booth holds voters of both sides, so this is where removals fell, not whose votes they were.'], 8.65, TOP + 1.9, W - M - 8.65, CH - 1.9, 13);

  const byParty = {}; A.forEach((a) => { (byParty[a.win2025] = byParty[a.win2025] || []).push(a); });
  const parties = Object.keys(byParty).filter((p) => byParty[p].length >= 4).sort((a, b) => per100(byParty[b]) - per100(byParty[a]));
  const res = ['GEN', 'SC', 'ST'].map((r) => [r, A.filter((a) => a.reserved === r)]);
  s = K.slide('Elections', parties[0] + '\'s seats lost the most names per elector, ' + per100(byParty[parties[0]]).toFixed(1) + ' per 100', 'Seats grouped by the party that won in 2025 (parties with four or more seats), and by reservation');
  s.addChart(pres.charts.BAR, [{ name: 'Per 100 electors', labels: parties.map((p) => p + ' (' + byParty[p].length + ')'), values: parties.map((p) => +per100(byParty[p]).toFixed(2)) }],
    K.chart(Object.assign({}, K.left, { barDir: 'bar', chartColors: parties.map((p) => AL[byParty[p][0].al2025]), showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.00', valAxisHidden: true })));
  K.right(s, [
    ...res.map(([r, xs]) => ({ GEN: 'General', SC: 'Scheduled Caste', ST: 'Scheduled Tribe' }[r]) + ' seats (' + xs.length + '): ' + per100(xs).toFixed(2) + ' per 100 electors.'),
    'Number of seats in brackets. Bar colour is the party\'s alliance.',
  ]);

  const ch = withM.filter((a) => a.al2020 !== a.al2025), gained = A.filter((a) => a.al2020 !== 'NDA' && a.al2025 === 'NDA'), held = A.filter((a) => a.al2020 === 'NDA' && a.al2025 === 'NDA');
  s = K.slide('Elections', ch.length + ' of ' + withM.length + ' seats changed alliance between 2020 and 2025', 'Seats by the alliance that won in 2020 and in 2025, with names removed per 100 electors in each group');
  const ALS = ['NDA', 'INDIA', 'Other'];
  K.table(s, ['2020 winner → 2025 winner', ...ALS.map((a) => a + ' in 2025')], ALS.map((a20) => [a20 + ' in 2020', ...ALS.map((a25) => { const xs = A.filter((a) => a.al2020 === a20 && a.al2025 === a25); return xs.length ? xs.length + ' seats · ' + per100(xs).toFixed(2) : '–'; })]),
    M, TOP, 7.6, [2.8, 1.6, 1.6, 1.6], 13);
  K.right(s, ['Seats the NDA gained lost ' + per100(gained).toFixed(2) + ' per 100 electors; seats it held lost ' + per100(held).toFixed(2) + '.', 'Each cell: number of seats, then names removed per 100 electors.']);

  // ---- Women, religion, caste
  const gaps = DI.slice().sort((a, b) => (b.female_share_deleted - b.female_share_population_2011) - (a.female_share_deleted - a.female_share_population_2011));
  s = K.slide('Women, religion, caste', 'Women are ' + pct(fem) + ' of those removed and 47.86% of the population', 'Over-represented in ' + fOver.length + ' of ' + DI.length + ' districts; the ten with the widest gap');
  const g10 = gaps.slice(0, 10).reverse();
  s.addChart(pres.charts.BAR, [
    { name: 'Women, % of population 2011', labels: g10.map((d) => d.district), values: g10.map((d) => +d.female_share_population_2011.toFixed(1)) },
    { name: 'Women, % of names removed', labels: g10.map((d) => d.district), values: g10.map((d) => +d.female_share_deleted.toFixed(1)) },
  ], K.chart(Object.assign({}, K.left, { barDir: 'bar', barGrouping: 'clustered', chartColors: [GREY, 'AF3B6E'], showLegend: true, valAxisMinVal: 40, valAxisMaxVal: 65 })));
  const gv = DI.map((d) => d.female_share_deleted - d.female_share_population_2011);
  K.right(s, [
    indian(t.female) + ' women and ' + indian(t.male) + ' men were removed, ' + indian(t.female - t.male) + ' more women.',
    'The gap runs from ' + Math.min(...gv).toFixed(1) + ' to ' + Math.max(...gv).toFixed(1) + ' points by district.',
    'The roll records sex, so this needs no inference from names.',
    indian(xsS) + ' of the ' + indian(xsF) + ' more women than men removed in phase 1 were entered as shifted. The lists do not show whether any were enrolled again elsewhere.',
  ], 13);

  s = K.slide('Women, religion, caste', 'Muslim-name electors are ' + pct(mlo) + ' to ' + pct(mhi) + ' of the removed, against 16.87% of the population', 'The roll records no religion. The lists classify names as Hindu, Muslim or unclassified, so the share is a range');
  K.stats(s, [[pct(mlo) + ' to ' + pct(mhi), 'Muslim-name share of removals: classified names only, then adding every unclassified name', { size: 24 }], ['16.87%', 'Muslim share of the population, 2011 census'], ['17.70%', 'Muslim share in the 2023 Bihar caste survey'], [pct(100 * t.unknown / cls), 'of removed names unclassified']], TOP, 1.9, 2, M, 6.2);
  K.right(s, ['Statewide, the range contains the population share.', 'District by district it does not: the census share lies inside the range in ' + inside.length + ' of ' + DI.length + ' districts.', 'In the rest, the classified share alone is above the census share. Most of those gaps are within the 0.83-point rise in the Muslim share since 2011.'], 13.5);

  s = K.slide('Women, religion, caste', 'In ' + above.length + ' districts the Muslim-name share of removals is more than a point above the census share', 'Counting only names classified Muslim, the low end of the range');
  K.table(s, ['District', 'Census 2011', 'Removals, low', 'Removals, high', 'Low ÷ census'], above.map((d) => [d.district, pct(d.muslim_share_population_2011), pct(d.muslim_share_deleted_low), pct(d.muslim_share_deleted_high), (d.muslim_share_deleted_low / d.muslim_share_population_2011).toFixed(2)]), M, TOP, 7.4, [2.2, 1.3, 1.3, 1.3, 1.3], 13);
  K.right(s, ['All ' + above.length + ' lie in south and central Bihar, where Muslims are a small minority.', 'Muslims in Bihar are younger than average, so their share of electors is below their share of population. That would widen these gaps, not close them.', 'Migration into Patna and errors in classifying names could narrow them.'], 13.5);

  const cg = ID.caste.guardian, G = ['General', 'BC', 'EBC', 'SC', 'ST', 'Muslim'];
  const up = G.filter((g) => g !== 'Muslim' && cg.A.groups[g].ratio_to_survey >= 1 && cg.B.groups[g].ratio_to_survey >= 1), down = G.filter((g) => g !== 'Muslim' && cg.A.groups[g].ratio_to_survey < 1 && cg.B.groups[g].ratio_to_survey < 1);
  s = K.slide('Women, religion, caste', 'Under both surname readings, ' + andj(up) + ' families are removed at or above their population share', 'Caste read from the surname of the father or husband, against the 2023 Bihar caste survey');
  s.addChart(pres.charts.BAR, [
    { name: 'Classification A', labels: G, values: G.map((g) => cg.A.groups[g].ratio_to_survey) },
    { name: 'Classification B (strict)', labels: G, values: G.map((g) => cg.B.groups[g].ratio_to_survey) },
  ], K.chart(Object.assign({}, K.left, { barDir: 'col', barGrouping: 'clustered', chartColors: [P.accent, '1F618D'], showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.00', showLegend: true, valAxisHidden: true, showTitle: true, title: 'Share of the removed ÷ share of the population' })));
  K.right(s, [
    'Above 1: a group\'s share of the removed exceeds its share of the population.',
    andj(down) + ' families are removed below their share under both.',
    'The two readings disagree on Muslim families (' + cg.A.groups.Muslim.ratio_to_survey.toFixed(2) + ' and ' + cg.B.groups.Muslim.ratio_to_survey.toFixed(2) + '), so no reading is offered for them.',
    'A places ' + pct(cg.A.coverage_pct, 0) + ' of removals in a group. B, which sets aside surnames shared across groups such as Singh, Prasad and Mandal, places ' + pct(cg.B.coverage_pct, 0) + '.',
  ], 13);

  // ---- Border
  const BG = [['Nepal', (a) => a.border === 'Nepal'], ['Uttar Pradesh', (a) => a.border === 'Uttar Pradesh'], ['Jharkhand', (a) => a.border === 'Jharkhand'], ['West Bengal', (a) => a.border === 'West Bengal'], ['Two borders', (a) => a.border.includes(';')], ['Interior', (a) => a.border === 'Interior']];
  const bord = A.filter((a) => a.border !== 'Interior'), intr = A.filter((a) => a.border === 'Interior');
  s = K.slide('Border', 'Border seats lost ' + per100(bord).toFixed(2) + ' names per 100 electors, interior seats ' + per100(intr).toFixed(2), bord.length + ' constituencies lie in a district on the Nepal, West Bengal, Jharkhand or Uttar Pradesh border');
  s.addChart(pres.charts.BAR, [{ name: 'Per 100 electors', labels: BG.map(([n, f]) => n + ' (' + A.filter(f).length + ')'), values: BG.map(([, f]) => +per100(A.filter(f)).toFixed(2)) }],
    K.chart(Object.assign({}, K.left, { barDir: 'col', chartColors: BG.map(([n]) => n === 'Interior' ? GREY : P.accent), showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.00', valAxisHidden: true })));
  K.right(s, [
    pct(100 * sum(bord, 'total') / t.total) + ' of all removals were in border seats, which hold ' + pct(100 * sum(bord, 'electorate_2025') / t.electorate_2025) + ' of the electorate.',
    'The Nepal and Bengal belts, and Seemanchal within them, are also where out-migration is heaviest, and a migrant who has moved is a legitimate "shifted" deletion.',
    'Border seats: ' + pct(100 * sum(bord, 'r_shifted') / sum(bord, (a) => a.r_dead + a.r_shifted + a.r_absent + a.r_enrolled)) + ' of phase 1 removals entered as shifted; interior seats: ' + pct(100 * sum(intr, 'r_shifted') / sum(intr, (a) => a.r_dead + a.r_shifted + a.r_absent + a.r_enrolled)) + '.',
  ], 13.5);

  // ---- Districts
  s = K.slide('Districts', rankD[0].district + ' lost ' + rankD[0].per_100.toFixed(1) + ' names per 100 electors, the most of any district', 'Names removed per 100 electors on the 2025 roll, the fifteen heaviest districts');
  const td = rankD.slice(0, 15).reverse();
  s.addChart(pres.charts.BAR, [{ name: 'Per 100 electors', labels: td.map((d) => d.district), values: td.map((d) => d.per_100) }],
    K.chart(Object.assign({}, K.left, { barDir: 'bar', chartColors: td.map((d) => d.border && d.border !== 'Interior' ? P.accent : GREY), showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0', valAxisHidden: true })));
  K.right(s, [rankD[rankD.length - 1].district + ' lost the fewest, ' + rankD[rankD.length - 1].per_100.toFixed(1) + ' per 100.', 'Red bars are border districts, grey the interior.', 'The full report has a chapter for each of the 38 districts.']);

  const FAC = [['Income per head', 'gddp_pc'], ['Urban share', 'urban_pct'], ['Literacy', 'literacy'], ['Women\'s literacy', 'female_literacy'], ['Density', 'density'], ['Electors per booth', 'electors_per_booth']];
  const y = DS.map((d) => d.per_100);
  const cor = FAC.map(([n, k]) => { const x = DS.map((d) => d[k]); return { n, r: pearson(x, y), rho: spearman(x, y) }; });
  const word = (c) => Math.abs(c.rho) < 0.2 ? 'no clear relationship' : c.rho < 0 ? 'fewer removals where higher' : 'more removals where higher';
  const flat = cor.filter((c) => Math.abs(c.rho) < 0.2).map((c) => c.n.toLowerCase()), strong = cor.slice().sort((a, b) => Math.abs(b.rho) - Math.abs(a.rho))[0];
  s = K.slide('Districts', 'District removal rates move most with ' + strong.n.toLowerCase() + ', and not with ' + orj(flat), 'Each district\'s removal rate against one characteristic: r is the linear correlation, ρ the rank correlation');
  K.table(s, ['Characteristic', 'r', 'ρ', 'Reading'], cor.map((c) => [c.n, c.r.toFixed(2), c.rho.toFixed(2), word(c)]), M, TOP, 7.6, [2.3, 0.9, 0.9, 3.5], 14, [0, 3]);
  K.right(s, ['A rank correlation under 0.2 either way is read as no relationship.', 'Thirty-eight districts cannot separate these factors: the poorest districts are also the least urban and least literate, and in the north-east the most exposed to migration.', 'Census 2011; income per head from the Bihar Economic Survey 2021-22.'], 13);

  // ---- Questions
  const fq = [
    ['Were most of the removed not simply dead, or moved away?', 'Not most. Of the ' + indian(RS.total) + ' phase 1 removals, ' + pct(rsh('shifted')) + ' were entered as shifted, ' + pct(rsh('dead')) + ' dead, ' + pct(rsh('absent')) + ' absent and ' + pct(rsh('already_enrolled')) + ' already enrolled. Each is an officer\'s entry, not a finding; the ' + indian(RT.absent) + ' marked absent rest on the least: the entry records only that the elector was not found.'],
    ['Did the removals exceed the margins?', 'Yes, in ' + over.length + ' of ' + withM.length + ' constituencies, and in ' + tookO.length + ' of the ' + took.length + ' seats the NDA took from INDIA. That does not mean each result would have been different; it means the change to the roll was larger than the decision at the ballot box.'],
    ['Did NDA seats not lose more names than INDIA seats?', 'They did: ' + LB['2020'].NDA.per_100.toFixed(2) + ' per 100 electors against ' + LB['2020'].INDIA.per_100.toFixed(2) + ' by the 2020 winner, and NDA-led booths lost ' + Wt.pooled_nda_minus_india.toFixed(1) + ' more names each than INDIA-led booths in the same seat. A booth\'s leader says how most voters voted, not how the removed voted.'],
    ['Why are women over-represented?', 'Women are ' + pct(fem) + ' of those removed and 47.86% of the population, over-represented in ' + fOver.length + ' of ' + DI.length + ' districts. ' + indian(xsS) + ' of the ' + indian(xsF) + ' more women than men removed in phase 1 were entered as shifted, and ' + pct(100 * yW / yS) + ' of those marked shifted aged 18 to 29 are women.'],
  ];
  const fq2 = [
    ['Were Muslims removed out of proportion?', 'Muslim-name electors are ' + pct(mlo) + ' to ' + pct(mhi) + ' of removals, against 16.87% of the population in 2011. The census share lies inside that range in ' + inside.length + ' of ' + DI.length + ' districts; in ' + above.length + ' the classified share alone is more than a point above it.'],
    ['How can caste be read from surnames?', 'Only partly, which is why two classifications are used and only what holds under both is reported. Read from the father\'s or husband\'s surname, ' + andj(up) + ' families are removed at or above their share of the 2023 survey under both.'],
    ['How reliable are the lists?', 'The booth list accounts for all ' + indian(t.booths) + ' polling booths, and constituency totals for both phases match the Chief Electoral Officer\'s table. Vote counts summed from the booths give the declared winner and runner-up in all 40 Lok Sabha seats. Every headline figure is recomputed by a second, independent program.'],
    ['Does this show the removals were meant to change results?', 'No list of removals can show intent. It shows where the removals fell, who was removed, and how their number compares with the margins. Whose votes they were, and whether they were rightly removed, the lists cannot show.'],
  ];
  K.qa(K.slide('Questions put to this analysis', 'What the lists say about deaths, moves, margins and alliances'), fq);
  K.qa(K.slide('Questions put to this analysis', 'What the lists say about religion, caste, reliability and intent'), fq2);

  // ---- Limits
  s = K.slide('Limits', 'What the lists show, and what they cannot show');
  K.box(s, 'The lists show how many names were removed and where, who the removed were by sex, and by religion and caste as read from names, and they allow the removals to be set against the margins and votes that decided each seat.', M, TOP - 0.4, 5.95, 2.3, 15);
  K.box(s, 'They record the reason an officer entered against each phase 1 removal, but not whether it was true, whether the removal was right, or how the elector voted. Religion and caste are estimates from names. No list can show intent.', 6.78, TOP - 0.4, 5.95, 2.3, 15);
  K.body(s, 'The reasons officers entered (dead, shifted, absent, enrolled twice) are entries made after a visit or its absence, not findings. Names marked absent alone exceed the margin in ' + rOver('r_absent') + ' seats. A change to the roll larger than the margin in ' + over.length + ' of ' + withM.length + ' seats is large enough to have decided those seats. Whether it did depends on how the removed would have voted, which no list records.', M, TOP + 2.2, W - 2 * M, 2.3, 16);

  s = K.slide('What the Election Commission should do', 'Publish what the lists leave out');
  K.numbered(s, [
    'Publish the reason for each of the ' + indian(t.p2) + ' phase 2 removals, which the lists do not carry.',
    'Publish the basis for each entry marked absent (' + indian(RT.absent) + ') or already enrolled (' + indian(RT.already_enrolled) + ') in phase 1.',
    'Publish every claim and objection filed after the draft roll, booth by booth, with its outcome.',
    'Publish new enrolments by constituency after the revision, so that women removed as shifted can be matched against enrolments where they now live.',
  ], M, TOP - 0.3, W - 2 * M, CH + 0.3, 17);

  // ---- Method
  s = K.slide('Method', 'Where the figures come from');
  K.bullets(s, [
    'Removals by booth: the Chief Electoral Officer\'s phase 1 deletion lists against the draft roll of 1 August 2025, for all ' + indian(t.booths) + ' booths. Removals by constituency, phase and sex: the Chief Electoral Officer\'s table. Reason, sex and age of each phase 1 removal: counts from the row-level list.',
    '2025 results: winner, runner-up and turnout for each seat, from the declared results; votes polled are turnout applied to the 2025 roll. 2024 booth leaders from Form 20, the booth-level count.',
    'Population: Census 2011 for sex, religion, literacy, density and urban share; the Bihar caste-based survey of 2 October 2023 for caste; income per head from the Bihar Economic Survey 2021-22.',
    'Alliances: NDA is BJP, JD(U), LJP(RV), HAM(S) and RLM; INDIA is RJD, INC, the Left parties, VIP and IIP; everything else is Other.',
  ], M, TOP - 0.3, W - 2 * M, CH + 0.3, 15);

  s = K.slide('Method', 'How the lists were prepared');
  K.bullets(s, [
    'One count per booth. The booth file lists each booth once for each of its three leading 2024 parties; each booth is counted once.',
    'Party names matched to the declared result. In nine Lok Sabha seats a party name in the booth file differed from the declared result and was matched to it, with evidence. After matching, the top two in all 40 seats are the declared winner and runner-up.',
    'Titles are not surnames. Devi, Kumari and Khatun say nothing about caste and are set aside; caste is read from the father\'s or husband\'s surname.',
    'Seats are joined by number: Bihar has two Kalyanpurs and two Pipras.',
    'A second, independent program recomputes every headline figure from the raw files before publication. Only counts are published: no name, EPIC number or address.',
  ], M, TOP - 0.3, W - 2 * M, CH + 0.3, 15);

  closing(pres, K, P, 'The full analysis', ['The dashboard, the booth explorer for every constituency and booth, and the full report with a chapter for each of the 38 districts, are published online alongside this deck.', 'Varna Sri Raman']);
  K.contents(toc);
  return pres.writeFile({ fileName: path.join(OUT, 'bihar-sir-2025-deck.pptx') });
}

// ============================================================ HYDERABAD
function hyderabad() {
  const S = J('hyderabad/summary.json'), PJ = J('hyderabad/parts.json');
  const PR = PJ.rows.map((r) => Object.fromEntries(PJ.fields.map((f, i) => [f, r[i]])));
  const A = S.acs, t = S.totals, names = A.map((a) => a.name);
  const P = { dark: '6E1832', darker: '52101F', accent: '8B1E3F', light: 'F2D9B8', soft: 'F7ECEF', band: ['8B1E3F', '0E5E6F', 'E0A526', '0E5E6F'], foot: 'Hyderabad Old City SIR 2026 · Varna Sri Raman · aggregates only; no names or EPIC numbers' };
  const pres = new pptxgen(); pres.layout = 'LAYOUT_WIDE'; pres.author = 'Varna Sri Raman'; pres.title = 'Hyderabad Old City SIR 2026';
  const K = kit(pres, P);
  const s_ = (f) => sum(A, f);
  const LK = A.filter((a) => a.linked), yak = A.find((a) => a.name === 'Yakutpura'), mal = A.find((a) => a.name === 'Malakpet');
  const overV = A.filter((a) => a.e2023.deleted_over_valid > 100), valid = s_((a) => a.e2023.valid), allWin = A.every((a) => a.deleted > a.e2023.winner_votes);
  const age = S.bands.map((b, i) => 100 * s_((a) => a.counts.age_asd[i]) / s_((a) => a.age_all[i]));
  const rsh = (k) => 100 * s_((a) => a.reasons[k]) / t.deleted;
  const hin = 100 * s_((a) => a.counts.hin_asd) / s_((a) => a.counts.hin_all), mus = 100 * s_((a) => a.counts.mus_asd) / s_((a) => a.counts.mus_all);
  const fr = 100 * s_((a) => a.counts.f_asd) / s_((a) => a.counts.f_all), mr = 100 * s_((a) => a.counts.m_asd) / s_((a) => a.counts.m_all);
  const HM = A.map((a) => a.within_part.hindu_minus_muslim), UL = LK.map((a) => a.within_part.unlinked_minus_linked), FM = A.map((a) => a.within_part.female_minus_male);
  const lk = 100 * sum(LK, (a) => a.counts.lk_asd) / sum(LK, (a) => a.counts.lk_all), ul = 100 * sum(LK, (a) => a.deleted - a.counts.lk_asd) / sum(LK, (a) => a.electors - a.counts.lk_all);
  const heavy = A.slice().sort((a, b) => b.max_slot - a.max_slot)[0];
  const P100 = PR.filter((p) => p.electors >= 100), o60 = P100.filter((p) => p.rate > 60);
  const ruleTot = S.rules.map((k) => s_((a) => a.rules[k] || 0)), ruleAll = sum(ruleTot, (v) => v);
  const byAge = A.map((a) => a.age_rate), a80 = byAge.map((r) => r[r.length - 1]), a18 = byAge.map((r) => r[0]);
  const RN = { 'Permanently Shifted': 'Permanently shifted', 'Untraceable/Absent': 'Untraceable or absent', 'Death': 'Dead', 'Already enrolled': 'Enrolled elsewhere' };

  cover(pres, K, P, 'Special Intensive Revision · Hyderabad Old City 2026', 'The 2026 revision struck ' + lakh(t.deleted) + ' electors off five Old City rolls',
    'Charminar, Yakutpura, Malakpet, Chandrayangutta and Bahadurpura, polling part by polling part',
    [[indian(t.deleted), 'electors struck off the pre-revision rolls'], [pct(t.rate), 'of every elector on those rolls'], [pct(100 * t.deleted / valid), 'of the valid votes cast in 2023'], [indian(t.hearing), 'kept but summoned to a hearing']])
    .addNotes('The lists cover every elector on the pre-revision rolls of the five constituencies, so each group has a true removal rate. These are the September 2026 lists; the final roll is due on 9 November, so restorations after hearings are not in them.');
  const toc = contentsSlide(pres, K, P);

  // ---- Overview
  let s = K.slide('Overview', pct(t.rate) + ' of electors were struck off, and ' + pct(100 * t.hearing / t.electors) + ' more summoned to hearings', 'What happened to each elector on the five pre-revision rolls, % of the roll');
  s.addChart(pres.charts.BAR, [
    { name: 'Struck off', labels: names, values: A.map((a) => a.rate) },
    { name: 'Kept, summoned to a hearing', labels: names, values: A.map((a) => a.hearing_rate) },
    { name: 'Kept, not summoned', labels: names, values: A.map((a) => +(100 - a.rate - a.hearing_rate - 100 * a.unaccounted / a.electors).toFixed(1)) },
  ], K.chart(Object.assign({}, K.left, { w: 8.2, barDir: 'bar', barGrouping: 'stacked', chartColors: ['C0392B', 'D4AC0D', '1F618D'], showValue: true, dataLabelPosition: 'ctr', dataLabelFormatCode: '0.0', dataLabelColor: 'FFFFFF', showLegend: true, valAxisMaxVal: 100, valAxisHidden: true })));
  const sr = A.slice().sort((a, b) => b.rate - a.rate);
  K.stats(s, [[indian(t.deleted), 'struck off, out of ' + indian(t.electors)], [indian(t.hearing), 'kept on the roll only if they attend a hearing'], [pct(sr[0].rate), sr[0].name + ' lost the most, ' + sr[4].name + ' the least (' + pct(sr[4].rate) + ')']], TOP, 1.45, 1, 9.15, W - M - 9.15);

  s = K.slide('Overview', allWin ? 'In all five seats, more names were struck off than the 2023 winner received' : 'In all five seats, more names were struck off than the 2023 winning margin', 'Names struck off against the 2023 result');
  K.table(s, ['Constituency', 'Won by (2023)', 'Winner\'s votes', 'Margin', 'Struck off', '× margin', '% of valid votes'],
    A.slice().sort((a, b) => b.e2023.deleted_over_valid - a.e2023.deleted_over_valid).map((a) => [a.name, a.e2023.winner, indian(a.e2023.winner_votes), indian(a.e2023.margin), indian(a.deleted), a.e2023.deleted_over_margin.toFixed(1) + '×', pct(a.e2023.deleted_over_valid)]),
    M, TOP - 0.2, W - 2 * M, [2.2, 3.0, 1.45, 1.2, 1.4, 1.1, 1.78], 13, [0, 1]);
  K.box(s, 'In ' + andj(overV.map((a) => a.name)) + ' the names struck off exceed every valid vote cast in 2023. Yakutpura was won by ' + indian(yak.e2023.margin) + ' votes and lost ' + indian(yak.deleted) + ' names. Across the five, the names struck off equal ' + pct(100 * t.deleted / valid) + ' of the 2023 vote.', M, TOP + 2.3, W - 2 * M, 1.5, 15);
  s.addNotes('No election has been held on the revised roll. The comparison is one of size; the roll records no one\'s vote.');

  s = K.slide('Overview', pct(rsh('Permanently Shifted'), 0) + ' of removals were entered as "permanently shifted" and ' + pct(rsh('Untraceable/Absent'), 0) + ' as untraceable', 'Share of names struck off, by the reason the officer recorded');
  s.addChart(pres.charts.BAR, S.reasons.map((k) => ({ name: RN[k] || k, labels: names, values: A.map((a) => +(100 * a.reasons[k] / a.deleted).toFixed(1)) })),
    K.chart(Object.assign({}, K.left, { w: 8.2, barDir: 'bar', barGrouping: 'percentStacked', chartColors: ['1F618D', 'C0392B', GREY, 'E0A526'], showLegend: true, valAxisHidden: true })));
  const ut = A.map((a) => 100 * a.reasons['Untraceable/Absent'] / a.deleted);
  K.bullets(s, [
    pct(rsh('Death')) + ' were entered as dead and ' + pct(rsh('Already enrolled')) + ' as enrolled elsewhere.',
    'The untraceable share runs from ' + pct(Math.min(...ut)) + ' to ' + pct(Math.max(...ut)) + ' by constituency.',
    'Each reason is an officer\'s entry, not a finding. An untraceable entry records only that someone was not found.',
  ], 9.15, TOP + 0.1, W - M - 9.15, CH - 0.1, 13.5);

  // ---- Age, sex, religion, 2002
  s = K.slide('Age, sex, religion, 2002', pct(age[age.length - 1], 0) + ' of electors aged 80 and over were struck off, against ' + pct(age[0], 0) + ' of those aged 18 to 24', 'Share of each age band struck off, all five constituencies');
  s.addChart(pres.charts.BAR, [{ name: '% struck off', labels: S.bands, values: age.map((v) => +v.toFixed(1)) }],
    K.chart(Object.assign({}, K.left, { barDir: 'col', chartColors: [P.accent], showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0"%"', valAxisHidden: true })));
  K.right(s, [
    'The pattern holds in every constituency: ' + pct(Math.min(...a80)) + ' to ' + pct(Math.max(...a80)) + ' of those aged 80 and over, ' + pct(Math.min(...a18)) + ' to ' + pct(Math.max(...a18)) + ' of those aged 18 to 24.',
    indian(s_((a) => a.reasons.Death)) + ' were entered as dead, which explains part of the top of the range.',
    'The rate roughly doubles between 18 to 24 and 30 to 39, ages at which few people die.',
  ]);

  s = K.slide('Age, sex, religion, 2002', 'Electors with no link to the 2002 roll were struck off ' + (ul / lk).toFixed(1) + ' times as often', 'Share struck off, by whether the elector maps to the 2002 intensive revision roll. Malakpet\'s list carries no link.');
  s.addChart(pres.charts.BAR, [
    { name: 'Linked to 2002', labels: LK.map((a) => a.name), values: LK.map((a) => a.linked_rate) },
    { name: 'No 2002 link', labels: LK.map((a) => a.name), values: LK.map((a) => a.unlinked_rate) },
  ], K.chart(Object.assign({}, K.left, { barDir: 'col', barGrouping: 'clustered', chartColors: ['0E5E6F', 'C0392B'], showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0', showLegend: true, valAxisHidden: true })));
  K.right(s, [
    'Linked electors: ' + pct(lk) + ' struck off. No link: ' + pct(ul) + '.',
    'Inside the same polling part the gap is ' + Math.min(...UL.map((u) => u.diff_pp)).toFixed(0) + ' to ' + Math.max(...UL.map((u) => u.diff_pp)).toFixed(0) + ' points, and runs the same way in ' + indian(sum(UL, 'a_higher')) + ' of ' + indian(sum(UL, 'parts')) + ' parts.',
    'The 2002 link is the revision\'s own test. Anyone who moved to the city after 2002, or whose family name is spelt differently on the old roll, starts behind.',
  ]);

  s = K.slide('Age, sex, religion, 2002', pct(hin) + ' of Hindu-name electors were struck off, and ' + pct(mus) + ' of Muslim-name electors', 'Share struck off by religion estimated from names, constituency by constituency');
  s.addChart(pres.charts.BAR, [
    { name: 'Hindu-name electors', labels: names, values: A.map((a) => a.hindu_rate) },
    { name: 'Muslim-name electors', labels: names, values: A.map((a) => a.muslim_rate) },
  ], K.chart(Object.assign({}, K.left, { barDir: 'col', barGrouping: 'clustered', chartColors: ['E0A526', '1E8449'], showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0', showLegend: true, valAxisHidden: true })));
  K.right(s, [
    'Inside the same polling part, Hindu-name electors were struck off ' + Math.min(...HM.map((h) => h.diff_pp)).toFixed(1) + ' to ' + Math.max(...HM.map((h) => h.diff_pp)).toFixed(1) + ' points more often, in ' + sum(HM, 'a_higher') + ' of ' + sum(HM, 'parts') + ' parts large enough to compare.',
    'The lists give religion and age separately, so part of this gap may be an age gap.',
    'Religion is estimated from names; the roll records none.',
  ]);

  s = K.slide('Age, sex, religion, 2002', 'Women and men were struck off at similar rates, ' + pct(fr) + ' and ' + pct(mr), 'Share struck off by sex, constituency by constituency');
  s.addChart(pres.charts.BAR, [
    { name: 'Women', labels: names, values: A.map((a) => a.female_rate) },
    { name: 'Men', labels: names, values: A.map((a) => a.male_rate) },
  ], K.chart(Object.assign({}, K.left, { barDir: 'col', barGrouping: 'clustered', chartColors: ['AF3B6E', '1F618D'], showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0', showLegend: true, valAxisHidden: true })));
  K.right(s, ['Inside the same part the gaps are under ' + Math.ceil(Math.max(...FM.map((f) => Math.abs(f.diff_pp))) * 2) / 2 + ' points either way.', 'In Bihar, women were 55.5% of the removed. The Old City shows no such gap.']);

  // ---- Polling parts
  const bins = [[10, 20], [20, 30], [30, 40], [40, 50], [50, 60], [60, 70], [70, 81]];
  s = K.slide('Polling parts', 'Part removal rates ran from ' + Math.floor(Math.min(...P100.map((p) => p.rate))) + '% to ' + Math.round(Math.max(...P100.map((p) => p.rate))) + '%', 'Polling parts with at least 100 electors, by the share struck off; Malakpet has no part numbers');
  s.addChart(pres.charts.BAR, [{ name: 'Parts', labels: bins.map(([a, b]) => a + '–' + Math.min(b, 80) + '%'), values: bins.map(([a, b]) => P100.filter((p) => p.rate >= a && p.rate < b).length) }],
    K.chart(Object.assign({}, K.left, { w: 6.4, barDir: 'col', chartColors: bins.map(([a]) => a >= 60 ? P.accent : GREY), showValue: true, dataLabelPosition: 'outEnd', valAxisHidden: true })));
  K.table(s, ['Constituency', 'Lowest', 'Median', 'Highest'], LK.map((a) => [a.name, pct(a.part_rate_quartiles[0]), pct(a.part_rate_quartiles[2]), pct(a.part_rate_quartiles[4])]), 7.3, TOP, W - M - 7.3, [2.2, 1.1, 1.1, 1.03], 13);

  s = K.slide('Polling parts', 'Parts with more Muslim-name electors lost fewer names, in every constituency', 'Rank correlation across parts within each constituency, with the part\'s removal rate');
  K.table(s, ['Constituency', 'Muslim-name share', 'Share aged 80+', 'Share untraceable'], LK.map((a) => [a.name, a.part_correlations.muslim_share_vs_rate.toFixed(2), a.part_correlations.aged80_share_vs_rate.toFixed(2), a.part_correlations.untraceable_share_vs_rate.toFixed(2)]), M, TOP, 7.6, [2.35, 1.75, 1.75, 1.75], 14);
  K.right(s, ['Negative: parts with more of that group lost fewer names.', 'The share of elderly electors and the share entered as untraceable barely move with a part\'s rate.', 'Parts with at least 100 electors; the untraceable share uses parts with at least 20 removals.'], 13.5);

  s = K.slide('Polling parts', o60.length + ' polling parts lost more than 60% of their roll', 'The fifteen heaviest parts with 100 or more electors');
  K.table(s, ['Constituency', 'Part', 'Locality', 'Electors', 'Struck off', '% struck off'],
    P100.slice().sort((a, b) => b.rate - a.rate).slice(0, 15).map((p) => [p.ac, p.part, p.locality && p.locality !== 'nan' ? p.locality : '–', indian(p.electors), indian(p.deleted), pct(p.rate)]),
    M, TOP - 0.25, W - 2 * M, [2.4, 0.9, 4.2, 1.5, 1.5, 1.63], 11.5, [0, 2]);

  // ---- Hearings
  const RL = { 'Unmapped with Last SIR': 'Not traced to the 2002 roll', 'Parent Name Mismatch': 'Parent\'s name does not match', 'Self Name Mismatch': 'Own name does not match', 'Progeny >= 6': 'Six or more children recorded', 'Parent Age Difference <15': 'Parent less than 15 years older', 'Progeny Age Gap <9 Month': 'Children born under 9 months apart', 'Grandparent Age difference <40': 'Grandparent less than 40 years older' };
  const ro = S.rules.map((k, i) => [RL[k] || k, ruleTot[i]]).sort((a, b) => a[1] - b[1]);
  s = K.slide('Hearings', indian(t.hearing) + ' electors kept on the draft roll were summoned to hearings', 'Electors summoned under each of the Commission\'s seven rules, all five constituencies');
  s.addChart(pres.charts.BAR, [{ name: 'Flags', labels: ro.map((r) => r[0]), values: ro.map((r) => r[1]) }],
    K.chart(Object.assign({}, K.left, { barDir: 'bar', chartColors: [P.accent], showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '#,##0', valAxisHidden: true })));
  K.right(s, [pct(100 * ro[ro.length - 1][1] / ruleAll) + ' of flags were for not being traced to the last intensive revision, in 2002; mismatched names came next.', 'One elector can carry more than one rule, so the flags add up to more than the people summoned.', pct(100 * t.hearing / t.electors) + ' of everyone on the five rolls was summoned.']);

  const days = A[0].daily.map((d) => d[0]), perDay = days.map((d, i) => s_((a) => (a.daily[i] || [0, 0])[1]));
  s = K.slide('Hearings', 'The busiest hearing slot listed ' + heavy.max_slot + ' cases; the median slot in ' + heavy.name + ' listed ' + heavy.median_slot, indian(s_((a) => a.slots)) + ' hearing slots, 28 August to 12 October');
  s.addChart(pres.charts.BAR, [
    { name: 'Median cases per slot', labels: names, values: A.map((a) => a.median_slot) },
    { name: 'Busiest single slot', labels: names, values: A.map((a) => a.max_slot) },
  ], K.chart({ x: M, y: TOP, w: 6.2, h: CH, barDir: 'col', barGrouping: 'clustered', chartColors: ['0E5E6F', P.accent], showValue: true, dataLabelPosition: 'outEnd', showLegend: true, valAxisHidden: true }));
  s.addChart(pres.charts.LINE, [{ name: 'Cases listed per day', labels: days, values: perDay }],
    K.chart({ x: 7.0, y: TOP, w: W - M - 7.0, h: CH, chartColors: [P.accent], lineSize: 2, lineDataSymbol: 'none', catAxisLabelFontSize: 9, showTitle: true, title: 'Cases listed per day, all five', valAxisLabelFormatCode: '#,##0' }));
  s.addNotes('The Commission extended the calendar on 7 September: claims to 7 October, hearings to 5 November, final roll 9 November. The schedules here are those in the September lists. The length of a slot is not recorded.');

  // ---- Questions
  K.qa(K.slide('Questions put to this analysis', 'What the lists say about moves, religion, the 2002 roll and age'), [
    ['Were most of those struck off not people who had moved away?', 'The largest recorded reason is "permanently shifted", ' + pct(rsh('Permanently Shifted')) + ' of removals, and the Old City has a large moving population. But ' + pct(rsh('Untraceable/Absent')) + ' were entered as untraceable or absent, ' + pct(rsh('Death')) + ' as dead and ' + pct(rsh('Already enrolled')) + ' as enrolled elsewhere. Each is an officer\'s entry, not a finding.'],
    ['Was the revision aimed at Muslim electors?', 'The lists do not show that. Inside the same polling part, Hindu-name electors were struck off more often than Muslim-name electors. What the lists show is who carried the burden: the old, and those who could not be traced to the 2002 roll.'],
    ['Why does the 2002 roll matter so much?', 'The revision asks each elector to show a link to the 2002 intensive revision, through their own name or a parent\'s. Where the lists record it, electors with no link were struck off ' + Math.min(...UL.map((u) => u.diff_pp)).toFixed(0) + ' to ' + Math.max(...UL.map((u) => u.diff_pp)).toFixed(0) + ' points more often than linked electors in the same part.'],
    ['Why are the old struck off so often?', pct(age[age.length - 1]) + ' of electors aged 80 and over were struck off, against ' + pct(age[0]) + ' of those aged 18 to 24. Some of that is death. The rest falls on electors least able to answer a visit, attend a hearing or produce papers.'],
  ]);
  K.qa(K.slide('Questions put to this analysis', 'What the lists say about hearings, results, reliability and coverage'), [
    ['Could the hearings be held properly?', indian(t.hearing) + ' electors kept on the draft roll were summoned. The busiest single slot listed ' + heavy.max_slot + ' cases, in ' + heavy.name + ', where the median slot listed ' + heavy.median_slot + '. The lists do not record how long a slot was.'],
    ['Did this change an election result?', 'No election has been held on the revised roll. Every one of the five constituencies lost more names than its 2023 winning margin, and in ' + andj(overV.map((a) => a.name)) + ' the names struck off outnumber every valid vote cast in 2023.'],
    ['How reliable are the lists?', 'For four constituencies the counts agree exactly with an independent count of the same lists, as do the recorded reasons and women\'s share. The Malakpet list used here is incomplete: ' + indian(mal.deleted) + ' names against 1,47,799 in the published list, with no part numbers or 2002 link.'],
    ['Why only five constituencies?', 'These are the five Old City seats whose full lists were available elector by elector. The figures describe these five and no others.'],
  ]);

  // ---- Limits
  s = K.slide('Limits', 'What the lists show, and what they cannot show');
  K.box(s, 'How many electors were struck off, from which parts, and who they were by age, sex, religion estimated from names, and link to the 2002 roll. Because the lists hold every elector, each group has a true removal rate.', M, TOP - 0.4, 5.95, 2.3, 15);
  K.box(s, 'Whether any single removal was right. A household that moved out is a correct "shifted" deletion; the files cannot tell it from an elector who was at home and missed. Religion and age are given separately, never together.', 6.78, TOP - 0.4, 5.95, 2.3, 15);
  K.body(s, 'These are the September lists. The final roll is due on 9 November, so restorations after hearings are not in these counts. Malakpet\'s list is read by polling-station name (' + mal.parts + ' stations) and ' + indian(mal.unaccounted) + ' electors on its roll appear in none of the three outcomes.', M, TOP + 2.2, W - 2 * M, 2.2, 16);

  s = K.slide('What the Election Commission should do', 'Before the final roll');
  K.numbered(s, [
    'Record and publish the basis for every removal entered as "untraceable or absent", ' + indian(s_((a) => a.reasons['Untraceable/Absent'])) + ' names: the visits made and the notice given.',
    'Publish how removals of electors with no link to the 2002 roll were decided.',
    'Schedule hearings so that each case can be heard, rather than listing hundreds of cases in one slot.',
    'Explain the removals in the ' + o60.length + ' parts that lost more than 60% of their roll.',
    'Publish restorations after hearings, part by part, so the final count can be set against these lists.',
  ], M, TOP - 0.3, W - 2 * M, CH + 0.3, 17);

  // ---- Method
  s = K.slide('Method', 'Where the figures come from and how the rates are defined');
  K.bullets(s, [
    'Source: the September 2026 SIR lists for the five constituencies, which record the outcome for every elector on the pre-revision roll: struck off (with the officer\'s reason), kept but summoned to a hearing (with the rule), or kept.',
    'Removal rate: electors on the absent-shifted-dead list divided by electors on the pre-revision roll, for each group. In Bihar the lists hold only the removed, so the Bihar deck gives shares of removals instead.',
    'Within-part difference: one group\'s rate minus another\'s inside each polling part, pooled with each part weighted by its smaller group; parts with fewer than 20 of either are left out. This holds the locality and the officer fixed.',
    'Part correlations: Spearman rank correlations across parts with at least 100 electors, within each constituency.',
    '2023 results: the declared Assembly results. Only counts are published: no name, EPIC number or address.',
  ], M, TOP - 0.3, W - 2 * M, CH + 0.3, 15);

  closing(pres, K, P, 'The full analysis', ['The dashboard, the part explorer for every polling part, and the full report with a chapter for each constituency, are published online alongside this deck.', 'Varna Sri Raman']);
  K.contents(toc);
  return pres.writeFile({ fileName: path.join(OUT, 'hyderabad-old-city-sir-2026-deck.pptx') });
}

// ============================================================ ALL INDIA
function india() {
  const N = J('india/states.json'), T = N.total, S = N.states, P = N.by_phase;
  const Pal = { dark: '1F4E79', darker: '163A5C', accent: '1F618D', light: 'D6E4F0', soft: 'EAF1F8', band: ['C0392B', 'E67E22', '27AE60', '1F618D', '8E44AD'], foot: 'SIR 2025-26 · All India · Varna Sri Raman · aggregates only; no names or EPIC numbers' };
  const pres = new pptxgen(); pres.layout = 'LAYOUT_WIDE'; pres.author = 'Varna Sri Raman'; pres.title = 'SIR 2025-26: All India';
  const K = kit(pres, Pal);
  const RK = ['dead', 'shifted_absent_other', 'duplicate'], RN = { dead: 'Dead', shifted_absent_other: 'Shifted, absent or other', duplicate: 'Enrolled more than once' };
  const RC = { dead: GREY, shifted_absent_other: '1F618D', duplicate: 'D4AC0D' };
  const crore = (x) => (x / 1e7).toFixed(2) + ' crore';
  const has = S.filter((s) => s.removed != null), split = S.filter((s) => s.shares);
  const rated = has.filter((s) => s.per_100 != null).sort((a, b) => b.per_100 - a.per_100);
  const big = split.filter((s) => s.removed >= 1e6).sort((a, b) => b.shares.shifted_absent_other - a.shares.shifted_absent_other);
  const hiDead = big.slice().sort((a, b) => b.shares.dead - a.shares.dead)[0], hiDup = big.slice().sort((a, b) => b.shares.duplicate - a.shares.duplicate)[0];
  const ph = ['1', '2', '3'], PL = ['Phase 1 (Bihar)', 'Phase 2 (' + P['2'].states + ')', 'Phase 3 (' + P['3'].states + ')'];

  cover(pres, K, Pal, 'Special Intensive Revision · India 2025-26', crore(T.removed) + ' names were left off the draft rolls, and four in five were not entered as dead',
    'The reason recorded for every removal, state by state: women among the removed, and what goes with the removal rate',
    [[crore(T.removed), 'left off the draft rolls in ' + T.states + ' states and union territories'], [pct(T.shares.shifted_absent_other), 'entered as shifted, absent or other'], [pct(T.shares.dead), 'entered as dead'], [pct(T.shares.duplicate), 'entered as enrolled more than once']])
    .addNotes('Outside Bihar the figures are the Chief Electoral Officers\' own, from their press notes or as reported in the press; Bihar is counted from the deletion lists. Shares are of the removals each state split by reason.');
  const toc = contentsSlide(pres, K, Pal);

  let s = K.slide('All India', crore(T.removed) + ' names left off the draft rolls, ' + T.per_100.toFixed(1) + ' for every 100 electors', 'All ' + T.states + ' states and union territories that have published a draft roll; Tripura publishes in December');
  K.stats(s, [[crore(T.removed), 'names left off the draft rolls'], [crore(T.shifted_absent_other), 'entered as shifted, absent or other'], [crore(T.dead), 'entered as dead'], [crore(T.duplicate), 'entered as enrolled more than once']], TOP, 1.7);
  K.body(s, 'A reason is what an officer entered after a visit or its absence, not a finding. Deaths are about one in five of the removals split by reason. The other four in five rest on an entry that the elector was not where the roll placed them, or was on it twice. ' + (T.unsplit / 1e5).toFixed(1) + ' lakh names are in states that have not published a full split.', M, TOP + 2.1, W - 2 * M, 2.4, 17);

  {
    const BIN = [8, 12, 16, 20], FILL = ['DEEBF7', '9ECAE1', '2878B3', '1C5F96', '08306B'], byS = {};
    S.forEach((x) => { byS[x.state] = x; });
    s = K.slide('All India', andj(rated.slice(0, 4).map((x) => x.state)) + ' removed the most for every 100 electors', 'Removed per 100 electors; one tile per state or union territory, placed roughly where it lies, with no boundaries');
    const sz = 0.56, gap = 0.06, x0 = M + 0.2, y0 = TOP - 0.35;
    N.tiles.forEach((t) => {
      const x = byS[t.state], v = x ? x.per_100 : null, b = v == null ? null : BIN.filter((c) => v >= c).length;
      const fx = x0 + t.col * (sz + gap), fy = y0 + t.row * (sz + gap);
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: fx, y: fy, w: sz, h: sz, rectRadius: 0.05, fill: { color: b == null ? 'F2F3F4' : FILL[b] }, line: b == null ? { color: '95A5A6', width: 0.75, dashType: 'dash' } : { type: 'none' } });
      s.addText([{ text: t.code, options: { bold: true, fontSize: 10, breakLine: true } }, { text: v == null ? '–' : v.toFixed(1), options: { fontSize: 9 } }],
        { x: fx, y: fy, w: sz, h: sz, align: 'center', valign: 'middle', fontFace: BODY, color: b == null || b < 2 ? INK : 'FFFFFF', margin: 0, isTextBox: true });
    });
    const labs = ['under 8', '8 to 12', '12 to 16', '16 to 20', '20 or more', 'no rate'];
    labs.forEach((l, i) => {
      s.addShape(pres.shapes.RECTANGLE, { x: 7.0, y: TOP + 2.2 + i * 0.36, w: 0.26, h: 0.26, fill: { color: i < 5 ? FILL[i] : 'F2F3F4' }, line: i < 5 ? { type: 'none' } : { color: '95A5A6', width: 0.75, dashType: 'dash' } });
      s.addText(l, { x: 7.35, y: TOP + 2.17 + i * 0.36, w: 1.6, h: 0.32, fontFace: BODY, fontSize: 11, color: INK, margin: 0, isTextBox: true, valign: 'middle' });
    });
    K.bullets(s, [rated[0].state + ' ' + rated[0].per_100.toFixed(1) + ', ' + rated[1].state + ' ' + rated[1].per_100.toFixed(1) + ', ' + rated[2].state + ' ' + rated[2].per_100.toFixed(1) + '.', 'Fewest: ' + rated[rated.length - 1].state + ' ' + rated[rated.length - 1].per_100.toFixed(1) + '.', 'Grey: not in the revision, no draft yet (Tripura), or no exact roll before it (Chandigarh).'], 9.2, TOP, W - M - 9.2, 2.2, 12.5);
  }

  s = K.slide('All India', 'The share entered as dead fell from ' + pct(P['1'].shares.dead, 0) + ' in Bihar to ' + pct(P['3'].shares.dead, 0) + ' in phase 3', 'Names left off the draft rolls in each phase, by reason, in lakh');
  s.addChart(pres.charts.BAR, RK.map((k) => ({ name: RN[k], labels: PL, values: ph.map((p) => +(P[p][k] / 1e5).toFixed(1)) })).concat([{ name: 'Not split', labels: PL, values: ph.map((p) => +(P[p].unsplit / 1e5).toFixed(1)) }]),
    K.chart(Object.assign({}, K.left, { barDir: 'col', barGrouping: 'stacked', chartColors: [RC.dead, RC.shifted_absent_other, RC.duplicate, '8E7CC3'], showLegend: true, valAxisLabelFormatCode: '#,##0' })));
  K.right(s, ph.map((p, i) => PL[i] + ': ' + (P[p].removed / 1e5).toFixed(1) + ' lakh removed, ' + P[p].per_100.toFixed(1) + ' per 100 electors; dead ' + pct(P[p].shares.dead) + ', shifted, absent or other ' + pct(P[p].shares.shifted_absent_other) + '.'), 13.5);

  s = K.slide('All India', rated[0].state + ' removed ' + rated[0].per_100.toFixed(1) + ' names per 100 electors, the most of any state', 'Names left off the draft roll per 100 electors on the roll before the revision');
  const rv = rated.slice().reverse();
  s.addChart(pres.charts.BAR, [{ name: 'Per 100 electors', labels: rv.map((x) => x.state), values: rv.map((x) => x.per_100) }],
    K.chart(Object.assign({}, K.left, { y: TOP - 0.4, h: CH + 0.45, barDir: 'bar', chartColors: rv.map((x) => x.state === 'Bihar' ? 'C0392B' : '1F618D'), showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0', dataLabelFontSize: 8, catAxisLabelFontSize: 8, valAxisHidden: true })));
  K.right(s, [rated[rated.length - 1].state + ' removed the fewest, ' + rated[rated.length - 1].per_100.toFixed(1) + ' per 100.', 'Bihar, in red, removed ' + S.find((x) => x.state === 'Bihar').per_100.toFixed(1) + ' per 100 at the draft stage.', 'Rates carry the rounding of states that published their rolls in lakh or crore. Chandigarh has no exact roll before the revision.'], 13);

  s = K.slide('All India', 'Among states that removed ten lakh names or more, the shifted, absent or other share ran from ' + pct(big[big.length - 1].shares.shifted_absent_other, 0) + ' to ' + pct(big[0].shares.shifted_absent_other, 0), 'Each state\'s removals split by the reason entered; states that published a split');
  const mv = split.slice().sort((a, b) => a.shares.shifted_absent_other - b.shares.shifted_absent_other);
  s.addChart(pres.charts.BAR, RK.map((k) => ({ name: RN[k], labels: mv.map((x) => x.state), values: mv.map((x) => x.shares[k]) })),
    K.chart(Object.assign({}, K.left, { y: TOP - 0.4, h: CH + 0.45, barDir: 'bar', barGrouping: 'percentStacked', chartColors: RK.map((k) => RC[k]), showLegend: true, catAxisLabelFontSize: 8, valAxisHidden: true })));
  K.right(s, ['Lowest: ' + big[big.length - 1].state + ', ' + pct(big[big.length - 1].shares.shifted_absent_other) + '. Highest: ' + big[0].state + ', ' + pct(big[0].shares.shifted_absent_other) + '.', 'Of these, dead is highest in ' + hiDead.state + ' (' + pct(hiDead.shares.dead) + '), enrolled more than once in ' + hiDup.state + ' (' + pct(hiDup.shares.duplicate) + ').', 'One revision under one set of instructions produced very different mixes of reasons, and the Commission has not explained why.'], 13);

  const rows = S.slice().sort((a, b) => (b.removed || 0) - (a.removed || 0));
  const trow = (x) => [x.state, x.phase, x.removed == null ? '–' : indian(x.removed), x.per_100 == null ? '–' : x.per_100.toFixed(1), x.shares ? pct(x.shares.dead) : '–', x.shares ? pct(x.shares.shifted_absent_other) : '–', x.shares ? pct(x.shares.duplicate) : '–', x.split === 'complete' ? (x.figures === 'rounded' ? 'rounded' : '') : x.split === 'short' ? 'short' : x.split === 'none' ? 'no split' : 'no draft'];
  const TH = ['State or UT', 'Phase', 'Removed', 'Per 100', 'Dead', 'Shifted, absent, other', 'Duplicate', 'Note'], TW = [3.2, 0.8, 1.8, 1.1, 1.1, 2.2, 1.3, 1.3];
  s = K.slide('All India', 'Every state and union territory, the sixteen largest', 'Names left off the draft roll, and the share of those split by reason');
  K.table(s, TH, rows.slice(0, 16).map(trow), M, TOP - 0.3, 12.8, TW, 11, [0, 7]);
  s = K.slide('All India', 'Every state and union territory, the remaining sixteen', 'Rounded: published in lakh or crore. Short: the reasons leave some names unexplained. No split: none found');
  K.table(s, TH, rows.slice(16).map(trow), M, TOP - 0.3, 12.8, TW, 11, [0, 7]);

  const G = N.gender.slice().sort((a, b) => b.gap - a.gap), gOver = G.filter((g) => g.gap > 1), gUnder = G.filter((g) => g.gap < -1);
  s = K.slide('All India', 'In ' + gOver.length + ' of the ' + G.length + ' states with a split by sex, women are a larger share of the removed than of the roll', 'Women\'s share of names removed and of the roll; most phase 3 states published no split by sex');
  const gv = G.slice().reverse();
  s.addChart(pres.charts.BAR, [
    { name: 'Women, % of the roll', labels: gv.map((g) => g.state), values: gv.map((g) => g.women_share_roll) },
    { name: 'Women, % of names removed', labels: gv.map((g) => g.state), values: gv.map((g) => g.women_share_removed) },
  ], K.chart(Object.assign({}, K.left, { barDir: 'bar', barGrouping: 'clustered', chartColors: [GREY, 'AF3B6E'], showLegend: true, valAxisMinVal: 40, valAxisMaxVal: 60 })));
  K.right(s, [
    'Largest gap: ' + G[0].state + ', ' + G[0].gap.toFixed(1) + ' points; then ' + G[1].state + ' and ' + G[2].state + '.',
    (gUnder.length ? gUnder.map((g) => g.state).join(' and ') + ' runs the other way, by ' + (-gUnder[0].gap).toFixed(1) + ' points.' : ''),
    'Figures are exact for ' + G.filter((g) => g.quality === 'exact' || g.quality === 'lists').length + ' states; rounded, from an earlier roll or unverified for the rest. Bihar is compared with the 2011 population.',
  ], 13);

  const CR = N.correlations, CL = { income_pc: 'Income per head', urban_pct: 'Urban share', literacy: 'Literacy', female_literacy: 'Women\'s literacy', muslim_pct: 'Muslim share', sc_pct: 'SC share', st_pct: 'ST share', sex_ratio: 'Sex ratio', out_migration: 'Born here, living elsewhere', in_migration: 'Living here, born elsewhere' };
  const ctop = CR.slice().sort((a, b) => Math.abs(b.per_100_all) - Math.abs(a.per_100_all))[0], cm = CR.find((c) => c.key === 'muslim_pct');
  const fr = (v) => v == null ? '–' : v.toFixed(2);
  s = K.slide('All India', 'The removal rate goes with in-migration across all states (' + fr(ctop.per_100_all) + '), but only because of phase 3; in phase 2 it is ' + fr(ctop.per_100_phase2), 'Rank correlations across states with each state\'s removals per 100 electors; under 0.2 either way is read as none');
  K.table(s, ['Characteristic', 'All states', 'Phase 2', 'Phase 3', 'Share enrolled twice, larger states'], CR.slice().sort((a, b) => b.per_100_all - a.per_100_all).map((c) => [CL[c.key], fr(c.per_100_all), fr(c.per_100_phase2), fr(c.per_100_phase3), fr(c.duplicate_big)]), M, TOP - 0.3, 7.9, [2.9, 1.1, 1.1, 1.1, 1.7], 12);
  K.right(s, [
    'In phase 3 income, urban share, migration and the Muslim share rise together, because the large destination states are revised alongside the North-East. ' + ctop.n_per_100_phase3 + ' states cannot separate them.',
    'Muslim share: ' + fr(cm.per_100_all) + ' across all states, ' + fr(cm.per_100_phase2) + ' in phase 2. No consistent relationship.',
    'Border states removed fewer: a median of ' + N.border.per_100_yes.toFixed(1) + ' per 100 against ' + N.border.per_100_no.toFixed(1) + ' in the interior.',
    'A state-level relationship says nothing about who was removed within a state.',
  ], 12.5);

  s = K.slide('All India', 'After the draft, ' + (N.after_draft.removed / 1e5).toFixed(1) + ' lakh more names were removed in ' + N.after_draft.states + ' states, with no reason given', 'What the state figures show, and what they cannot');
  K.box(s, 'They show how many names each state left off its draft roll and the reason its officers entered: dead, shifted or absent (with "others" where reported), or enrolled more than once.', M, TOP - 0.4, 5.95, 2.1, 15);
  K.box(s, 'They cannot show whether an entry was right, or break removals down by sex, age or booth. Outside Bihar they are the states\' published totals, some rounded, gathered from press notes and reports.', 6.78, TOP - 0.4, 5.95, 2.1, 15);
  K.body(s, 'Removals after the draft, at hearings and on objections, are outside every figure by reason, because no state has said why. Twelve phase 3 final rolls are still to come. The Election Commission has published no state table of its own.', M, TOP + 2.0, W - 2 * M, 2.2, 16);

  // ---- The Election Commission
  s = K.slide('What the Election Commission should do', 'Publish its own table, and the lists behind it');
  K.numbered(s, [
    'Publish a state-by-state table of its own, with the reason for every removal at the draft and after it, exact rather than rounded.',
    'Publish the deletion lists with the reason against each name for every state, as it did for Bihar.',
    'Publish the basis for entries marked absent and enrolled more than once.',
    'Publish the outcome of every claim and objection, so that restorations can be set against removals.',
    'Explain why the mix of reasons differs so widely between states under one set of instructions.',
  ], M, TOP - 0.3, W - 2 * M, CH + 0.3, 17);

  s = K.slide('Method', 'Where the figures come from');
  K.bullets(s, [
    'All India: each state\'s Chief Electoral Officer\'s figures at the draft roll. Press notes read directly for ' + andj(S.filter((x) => x.source === 'primary').map((x) => x.state)) + '; the rest as reported in the press, each linked on the method page and in the downloadable table.',
    'Bihar: counted from the phase 1 deletion lists, with shifted and absent combined to match the other states.',
    'Reasons grouped into the three every state reported: dead; shifted, absent or other; enrolled more than once.',
    'The state rows add to ' + crore(T.removed) + ', against about 13.3 crore reported nationally on 30 September 2026; the difference is rounding.',
    'No name, EPIC number or address is published.',
  ], M, TOP - 0.3, W - 2 * M, CH + 0.3, 15);

  closing(pres, K, Pal, 'The full analysis', ['The All India table with a source for every row, and the full report, are published online alongside this deck.', 'Varna Sri Raman']);
  K.contents(toc);
  return pres.writeFile({ fileName: path.join(OUT, 'sir-india-deck.pptx') });
}

fs.mkdirSync(OUT, { recursive: true });
Promise.all([india(), bihar(), hyderabad()]).then((f) => console.log('wrote', f.join(', ')));
