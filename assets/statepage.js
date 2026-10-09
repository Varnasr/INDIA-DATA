/* The shared state page. Every state and union territory listed in
   scripts/build_states.py is drawn from its data/<slug>/summary.json by this
   one script: the overview (page key 'main'), the method page ('method') and
   the questions ('faq'). Each page sets window.STATE = {id, slug} before
   loading it. English only, like the other 2026 state pages; the sentences
   are plain strings computed from the figures, never written by hand. */
(function () {
  var S = window.STATE;
  if (!S) return;
  var P;
  var n = function (x) { return SIR.n(x); };
  var lk = function (x) { return x >= 1e7 ? (x / 1e7).toFixed(2) + ' crore' : x >= 1e5 ? (x / 1e5).toFixed(2) + ' lakh' : SIR.n(x); };
  var d1 = function (x) { return SIR.d(x, 1); };
  var pc = function (x) { return SIR.pct(x); };
  var DATE = function (s) {
    if (!s) return '';
    var M = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'], p = s.split('-');
    return (+p[2]) + ' ' + M[+p[1] - 1] + ' ' + p[0];
  };
  var LEVEL = { district: ['district', 'districts'], ac: ['constituency', 'constituencies'], pc: ['parliamentary constituency', 'parliamentary constituencies'], island: ['island', 'islands'], tehsil: ['tehsil', 'tehsils'], ward: ['ward', 'wards'] };
  var hyph = function (s) { return s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''); };

  function load() {
    return P || (P = SIR.json('data/' + S.slug + '/summary.json').then(function (d) { d.v = {}; Object.keys(d.figures).forEach(function (k) { d.v[k] = d.figures[k].v; }); return d; }));
  }
  function press(d, k) { var f = d.figures[k]; return f && f.press; }
  function anyPress(d) { return Object.keys(d.figures).some(function (k) { return d.figures[k].press; }); }

  // the findings, the questions and the limits line, all from the figures
  function sentences(d) {
    var v = d.v, R = d.rates, st = d.state, out = {};
    if (d.revision === 'no_draft') {
      out.scale = st + ' has not yet published a draft roll, so no count of names left off exists for it.';
      return out;
    }
    if (v.removed != null) {
      out.scale = st + '\'s draft roll' + (d.dates.draft ? ' of ' + DATE(d.dates.draft) : '') + ' left off ' + lk(v.removed) + ' names' +
        (R.per_100 != null ? ', ' + d1(R.per_100) + ' of every 100 electors on the roll before the revision.' : '.');
    } else if (v.draft != null) {
      out.scale = st + '\'s draft roll' + (d.dates.draft ? ' of ' + DATE(d.dates.draft) : '') + ' holds ' + lk(v.draft) + ' electors. No count of the names left off was found.';
    }
    if (R.shares) out.reasons = pc(R.shares.shifted_absent_other) + ' of the names left off were entered as shifted, absent or for another reason, ' + pc(R.shares.dead) + ' as dead and ' + pc(R.shares.duplicate) + ' as enrolled more than once' + (d.reasons_complete ? '.' : ', as far as the published reasons go.');
    if (v.final != null) {
      out.final = 'The final roll' + (d.dates.final ? ' of ' + DATE(d.dates.final) : '') + ' holds ' + lk(v.final) + ' electors' +
        (v.added_after != null && v.removed_after != null ? '. After the draft ' + lk(v.added_after) + ' names were added and ' + lk(v.removed_after) + ' removed' : '') +
        (R.made_up_pct != null ? ', and the net rise is ' + d1(R.made_up_pct) + ' for every 100 left off. It counts people enrolling for the first time, so fewer than that were put back.' : '.');
    }
    if (R.women_removed_pct != null && R.women_before_pct != null)
      out.women = 'Women were ' + pc(R.women_removed_pct) + ' of the names left off and ' + pc(R.women_before_pct) + ' of the roll before the revision' +
        (R.women_per_100 != null ? ', ' + d1(R.women_per_100) + ' of every 100 women against ' + d1(R.men_per_100) + ' of every 100 men.' : '.');
    else if (R.women_final_pct != null) out.women = 'Women are ' + pc(R.women_final_pct) + ' of the final roll. No split of the names left off by sex was found.';
    if (v.notices != null) out.notices = lk(v.notices) + ' electors kept on the draft were to be sent a notice' + (press(d, 'notices') ? ', as reported in the press.' : '.');
    return out;
  }

  function limits(d) {
    var parts = [];
    if (anyPress(d)) parts.push('Figures marked as press reached us through newspapers or broadcasters and were not read from an official document.');
    if (d.v.dead != null) parts.push('A reason is what the officer wrote down, and nobody checked it.');
    return parts.join(' ');
  }

  // ---- the overview
  function main(d) {
    var box = document.getElementById('sp'), v = d.v, R = d.rates, s = sentences(d), h = [];
    var kp = [];
    if (v.removed != null) kp.push([lk(v.removed), 'names left off the draft roll' + (press(d, 'removed') ? ' (press)' : '')]);
    if (R.per_100 != null) kp.push([d1(R.per_100), 'of every 100 electors']);
    if (v.final != null) kp.push([lk(v.final), 'electors on the final roll' + (press(d, 'final') ? ' (press)' : '')]);
    else if (v.draft != null) kp.push([lk(v.draft), 'electors on the draft roll' + (press(d, 'draft') ? ' (press)' : '')]);
    if (R.women_removed_pct != null) kp.push([pc(R.women_removed_pct), 'women among the names left off']);
    else if (R.made_up_pct != null) kp.push([d1(R.made_up_pct), 'per 100 left off, the net rise after the draft']);
    if (kp.length) h.push('<div class="kpis">' + kp.map(function (k) { return '<div><b>' + k[0] + '</b><span>' + k[1] + '</span></div>'; }).join('') + '</div>');

    if (d.revision === 'no_draft') {
      h.push('<h2 id="where-the-revision-stands">Where the revision stands</h2><p>' + s.scale + '</p>');
      (d.notes || []).forEach(function (t) { h.push('<p>' + SIR.esc(t) + '</p>'); });
    }
    var steps = [];
    if (v.roll_before != null && v.draft != null) {
      steps.push({ name: 'Roll before the revision', v: v.roll_before, kind: 'total' }, { name: 'Left off the draft', v: v.roll_before - v.draft, kind: 'down' }, { name: 'Draft roll', v: v.draft, kind: 'total' });
      if (v.added_after != null && v.removed_after != null && v.final != null) steps.push({ name: 'Added after the draft', v: v.added_after, kind: 'up' }, { name: 'Removed after the draft', v: v.removed_after, kind: 'down' });
      else if (v.final != null) steps.push({ name: v.final >= v.draft ? 'Net rise after the draft' : 'Net fall after the draft', v: Math.abs(v.final - v.draft), kind: v.final >= v.draft ? 'up' : 'down' });
      if (v.final != null) steps.push({ name: 'Final roll', v: v.final, kind: 'total' });
      h.push('<h2 id="the-roll-step-by-step">The roll, step by step</h2><p class="sub">The roll before the revision is the list of electors ' + (d.dates.roll_before ? 'on ' + DATE(d.dates.roll_before) : 'when the revision began') + '. The draft roll' + (d.dates.draft ? ' of ' + DATE(d.dates.draft) : '') + ' is the list published once the enumeration forms were collected, and a name whose form did not come back was left off it.' + (v.final != null ? ' Electors could then ask to be added or object to names until the final roll' + (d.dates.final ? ' of ' + DATE(d.dates.final) : '') + '.' : '') + ' The bars start above zero so that the changes can be seen.</p>' +
        '<div class="grid"><div class="panel wide" id="pWater"><div class="vizbox" id="vWater"></div></div></div><p class="finding" id="fWater"></p>');
    }
    if (v.dead != null || v.shifted_absent_other != null) h.push('<h2 id="the-reasons">The reasons</h2><p class="sub">The reason entered against each name left off, as the Chief Electoral Officer published it' + (press(d, 'dead') ? ', through the press' : '') + '. A reason is what the officer wrote down, and nobody checked it.</p><div class="grid"><div class="panel wide" id="pReason"><div class="vizbox" id="vReason"></div><p id="nReason"></p></div></div>');
    if (s.women) h.push('<h2 id="women">Women</h2><p>' + s.women + '</p>' + (R.women_removed_pct != null ? '<div class="grid"><div class="panel wide" id="pWomen"><div class="vizbox" id="vWomen"></div></div></div>' : ''));
    d.tables.forEach(function (t, i) {
      var lv = LEVEL[t.level], tag = (t.press ? ' The figures reached us through the press.' : '') + (t.partial ? ' Only some ' + lv[1] + ' were published, so the rows do not add up to the state.' : '');
      h.push('<h2 id="' + hyph(t.title) + '">' + SIR.esc(t.title) + '</h2>' + (t.note ? '<p class="sub">' + SIR.esc(t.note) + tag + '</p>' : tag ? '<p class="sub">' + tag.trim() + '</p>' : '') +
        '<div class="grid"><div class="panel wide" id="pT' + i + '"><div class="vizbox" id="vT' + i + '"></div><p id="nT' + i + '"></p></div></div>' +
        '<details class="figs"><summary>Every ' + lv[0] + ', in figures</summary><div class="twrap fit"><table id="tT' + i + '"></table></div></details>');
    });
    if (s.notices) h.push('<h2 id="notices">Notices</h2><p>' + s.notices + ' The counts for every state are on <a href="../india/process/#notices-the-no-mapping-list-and-the-discrepancy-list">How the revision was run</a>.</p>');
    h.push('<p class="note">' + SIR.esc(d.state) + '\'s dates are drawn beside every other state\'s on <a href="../india/process/#s-' + hyph(d.state) + '">How the revision was run</a>. Every figure on this page is in the CSV on the Downloads page, and the <a href="method/">method page</a> lists each source.</p>');
    box.innerHTML = h.join('');

    if (steps.length) {
      var lo = Math.min.apply(null, steps.filter(function (x) { return x.kind === 'total'; }).map(function (x) { return x.v; }));
      VIZ.waterfall('vWater', { label: d.state + ': the roll before the revision, the draft' + (v.final != null ? ' and the final roll' : ''), from: Math.floor(lo * 0.85 / Math.pow(10, String(Math.floor(lo)).length - 2)) * Math.pow(10, String(Math.floor(lo)).length - 2), steps: steps });
      document.getElementById('fWater').innerHTML = '<b>' + (s.scale || '') + '</b> ' + (s.final || '');
    }
    if (v.dead != null || v.shifted_absent_other != null) {
      var rr = [['Shifted, absent or other', v.shifted_absent_other], ['Dead', v.dead], ['Enrolled more than once', v.duplicate]].filter(function (x) { return x[1] != null; });
      var big = Math.max.apply(null, rr.map(function (x) { return x[1]; })) >= 1e5;
      VIZ.lollipop('vReason', { label: 'Names left off the draft, by the reason entered', axis: big ? 'Lakh' : 'Names', rows: rr.map(function (x) { return { name: x[0], v: big ? x[1] / 1e5 : x[1], text: lk(x[1]), tok: '--fill-navy', hi: true }; }) });
      document.getElementById('nReason').textContent = (s.reasons || '') + (d.reasons_complete ? '' : ' The published reasons do not account for every name left off.');
    }
    if (R.women_removed_pct != null) {
      VIZ.dumbbell('vWomen', { label: 'Women\'s share of the roll before the revision and of the names left off', min: Math.floor(Math.min(R.women_before_pct, R.women_removed_pct) / 5) * 5 - 5, step: 5,
        aName: 'Share of the roll before', aTok: '--fill-grey', bName: 'Share of the names left off', bTok: '--fill-red', rows: [{ name: d.state, a: R.women_before_pct, b: R.women_removed_pct }] });
    }
    d.tables.forEach(function (t, i) { table(t, i, d); });
    SIR.showFaq(S.id, 'main');
  }

  function table(t, i, d) {
    var lv = LEVEL[t.level], rows = t.rows.slice(), note = document.getElementById('nT' + i), cols, data;
    if (t.kind === 'left_off' && !rows.some(function (r) { return r.per_100 != null; })) {
      document.getElementById('pT' + i).hidden = true;
      cols = [{ h: lv[0].charAt(0).toUpperCase() + lv[0].slice(1) }, { h: 'Left off', num: true }, { h: 'Dead', num: true }, { h: 'Shifted, absent or other', num: true }, { h: 'Enrolled more than once', num: true }];
      data = rows.map(function (r) { var o = function (x) { return x == null ? '–' : n(x); }; return [SIR.esc(r.name), o(r.removed), o(r.dead), o(r.shifted_absent_other), o(r.duplicate)]; });
      document.getElementById('tT' + i).closest('details').open = true;
    } else if (t.kind === 'left_off') {
      rows = rows.filter(function (r) { return r.per_100 != null; });
      rows.sort(function (a, b) { return b.per_100 - a.per_100; });
      VIZ.lollipop('vT' + i, { label: 'Names left off per 100 electors, by ' + lv[0], axis: 'Per 100 electors on the roll before', rows: rows.map(function (r) { return { name: r.name, v: r.per_100, text: d1(r.per_100), tok: '--fill-red', hi: true }; }) });
      note.textContent = rows[0].name + ' lost the most for its size, ' + d1(rows[0].per_100) + ' of every 100 electors, and ' + rows[rows.length - 1].name + ' the least, ' + d1(rows[rows.length - 1].per_100) + '.';
      cols = [{ h: lv[0].charAt(0).toUpperCase() + lv[0].slice(1) }, { h: 'Roll before', num: true }, { h: 'Draft', num: true }, { h: 'Left off', num: true }, { h: 'Per 100', num: true }];
      data = rows.map(function (r) { return [SIR.esc(r.name), n(r.before), n(r.draft), n(r.removed), d1(r.per_100)]; });
    } else if (t.kind === 'after') {
      rows.sort(function (a, b) { return (b.removed_1000 || 0) - (a.removed_1000 || 0); });
      VIZ.dots('vT' + i, { label: 'Names added and removed after the draft, per 1,000 on each ' + lv[0] + '\'s draft roll', axis: 'Per 1,000 on the draft',
        cats: rows.map(function (r) { return r.name; }),
        series: [{ name: 'Added after the draft', col: '--fill-navy', vals: rows.map(function (r) { return r.added_1000; }) }, { name: 'Removed after the draft', col: '--fill-red', vals: rows.map(function (r) { return r.removed_1000; }) }] });
      var lost = rows.filter(function (r) { return r.final != null && r.final < r.draft; });
      note.textContent = rows[0].name + ' removed the most after the draft for its size, ' + d1(rows[0].removed_1000) + ' for every 1,000 on its draft. ' +
        (lost.length ? 'In ' + lost.length + ' of ' + rows.length + ' ' + lv[1] + ' more names were removed than added, so the final roll is smaller than the draft.' : 'In every ' + lv[0] + ' more names were added than removed.');
      cols = [{ h: lv[0].charAt(0).toUpperCase() + lv[0].slice(1) }, { h: 'Draft', num: true }, { h: 'Added', num: true }, { h: 'Removed', num: true }, { h: 'Final', num: true }];
      data = rows.map(function (r) { return [SIR.esc(r.name), n(r.draft), r.added == null ? '–' : n(r.added), r.removed == null ? '–' : n(r.removed), r.final == null ? '–' : n(r.final)]; });
    } else if (t.kind === 'fall') {
      rows.sort(function (a, b) { return b.fall_100 - a.fall_100; });
      VIZ.lollipop('vT' + i, { label: 'Fall in the roll per 100, by ' + lv[0], axis: 'Per 100 on the earlier roll', rows: rows.map(function (r) { return { name: r.name, v: Math.max(r.fall_100, 0), text: d1(r.fall_100), tok: '--fill-red', hi: true }; }) });
      note.textContent = 'The fall in the roll takes in ordinary deaths, moves and new voters as well as the revision, so it is a different count from the names left off.';
      cols = [{ h: lv[0].charAt(0).toUpperCase() + lv[0].slice(1) }, { h: 'Earlier roll', num: true }, { h: 'Later roll', num: true }, { h: 'Fall per 100', num: true }];
      data = rows.map(function (r) { return [SIR.esc(r.name), n(r.before), n(r.final != null ? r.final : r.draft), d1(r.fall_100)]; });
    } else {
      var key = t.kind;
      rows.sort(function (a, b) { return b[key] - a[key]; });
      var big = rows[0][key] >= 1e5;
      VIZ.lollipop('vT' + i, { label: 'Electors on the ' + (key === 'draft' ? 'draft' : 'final') + ' roll, by ' + lv[0], axis: big ? 'Lakh' : 'Electors', rows: rows.map(function (r) { return { name: r.name, v: big ? r[key] / 1e5 : r[key], text: lk(r[key]), tok: '--fill-navy', hi: true }; }) });
      var w = rows.filter(function (r) { return r.women_pct != null; });
      note.textContent = w.length ? 'Women are ' + pc(Math.min.apply(null, w.map(function (r) { return r.women_pct; }))) + ' to ' + pc(Math.max.apply(null, w.map(function (r) { return r.women_pct; }))) + ' of each ' + lv[0] + '\'s ' + key + ' roll.' : 'Only the ' + key + ' roll was published by ' + lv[0] + ', so these figures show its size and nothing about the names left off.';
      cols = [{ h: lv[0].charAt(0).toUpperCase() + lv[0].slice(1) }, { h: key === 'draft' ? 'Draft' : 'Final', num: true }, { h: 'Women', num: true }, { h: 'Women, per cent', num: true }];
      data = rows.map(function (r) { return [SIR.esc(r.name), n(r[key]), r.women == null ? '–' : n(r.women), r.women_pct == null ? '–' : pc(r.women_pct)]; });
    }
    SIR.table('tT' + i, cols, data);
  }

  // ---- the method page
  function method(d) {
    var box = document.getElementById('sp'), h = [];
    h.push('<h2 id="where-the-figures-come-from">Where the figures come from</h2><ul class="plain">' + d.sources.map(function (s) {
      return '<li>' + (s.url ? '<a href="' + SIR.esc(s.url) + '" rel="noopener">' + SIR.esc(s.title) + '</a>' : SIR.esc(s.title)) + (s.primary ? '' : ' (press)') + '.</li>';
    }).join('') + '</ul>');
    if ((d.notes || []).length) h.push('<h2 id="notes-on-the-figures">Notes on the figures</h2>' + d.notes.map(function (t) { return '<p>' + SIR.esc(t) + '</p>'; }).join(''));
    h.push('<h2 id="the-checks">The checks</h2><p>The page is not built unless the figures agree with each other wherever they can be compared. The roll before less the draft must equal the names left off, the reasons must add to the names left off where all were published, the draft plus the net change must equal the final roll, men, women and third gender must add to each total, and every full table must add to the state figure in each column it shares with it.</p>');
    if ((d.cannot_show || []).length) h.push('<h2 id="what-these-figures-cannot-show">What these figures cannot show</h2><ul class="plain">' + d.cannot_show.map(function (t) { return '<li>' + SIR.esc(t) + '</li>'; }).join('') + '<li>Whether each removal was right.</li></ul>');
    box.innerHTML = h.join('');
    SIR.showFaq(S.id, 'method');
  }

  SIR.faq(S.id, S.slug + '/faq/', function () {
    return load().then(function (d) {
      var s = sentences(d), v = d.v, QA = [], lim = limits(d);
      if (s.scale) QA.push(['How many names were left off in ' + d.state + '?', s.scale + (s.reasons ? ' ' + s.reasons + ' A reason is what the officer wrote down, and nobody checked it.' : ''), ['main', 'faq']]);
      if (s.final) QA.push(['How many came back before the final roll?', s.final, ['main', 'faq']]);
      if (s.women) QA.push(['Were women left off more than men?', s.women, ['main', 'faq']]);
      if (d.tables.length) QA.push(['Is there a figure for each district or constituency?', d.tables.map(function (t) { return t.title + (t.partial ? ', for some ' + LEVEL[t.level][1] + ' only' : '') + (t.press ? ', from the press' : '') + '.'; }).join(' '), ['main', 'faq']]);
      else QA.push(['Is there a figure for each district or constituency?', 'No table below the state was found for ' + d.state + '. ' + ((d.cannot_show || [])[0] || ''), ['main', 'faq']]);
      QA.push(['Where do the figures come from?', 'From ' + d.sources.length + (d.sources.length === 1 ? ' document' : ' documents') + ', ' + d.sources.filter(function (x) { return x.primary; }).length + ' of them the Election Commission\'s or the Chief Electoral Officer\'s own. The method page names each one.', ['method', 'faq']]);
      var pts = [s.scale, s.reasons, s.final, s.women].filter(Boolean);
      return { qa: QA, short: { main: [pts, lim], method: [[s.scale, 'Every figure on these pages is checked against the others wherever they can be compared.'].filter(Boolean), ''], faq: [pts.slice(0, 3), ''] } };
    });
  });

  SIR.statePage = function (page) {
    return load().then(function (d) {
      if (page === 'method') method(d); else if (page === 'faq') SIR.showFaq(S.id); else main(d);
    }).catch(SIR.fail);
  };
})();
