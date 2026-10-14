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
  var LEVEL = { district: ['district', 'districts'], region: ['region', 'regions'], ac: ['constituency', 'constituencies'], pc: ['parliamentary constituency', 'parliamentary constituencies'], island: ['island', 'islands'], tehsil: ['tehsil', 'tehsils'], ward: ['ward', 'wards'] };
  var SEATED = ['meghalaya', 'manipur', 'odisha'];
  // the deeper sections of a full analysis, for a state with complete district
  // (and, where SEATED, constituency) tables: each in the state's own measure
  var MEASURE = {
    meghalaya: { d: { c: function (x) { return x.removed; }, b: 'before', per: 100, what: 'names left off the draft, per 100 on the roll before the revision' },
      s: { c: function (x) { return x.removed; }, what: 'names left off the draft', are: 'are', year: 2023 } },
    manipur: { d: { c: function (x) { return x.fall; }, b: 'before', per: 100, what: 'fall in the roll from the roll before the revision to the final roll, per 100 on the roll before' },
      s: { c: function (x) { return x.fall; }, what: 'fall in the roll from the roll before to the final roll', year: 2022 } },
    odisha: { d: { c: function (x) { return x.before - x.draft; }, b: 'before', per: 100, what: 'fall in the roll from January 2025 to the draft, per 100 on the January 2025 roll' },
      s: { c: function (x) { return x.removed; }, what: 'names removed after the draft', are: 'are', year: 2024 } },
    andhrapradesh: { d: { c: function (x) { return x.removed; }, b: 'before', per: 100, what: 'names left off the draft, per 100 on the roll before the revision' } },
    chhattisgarh: { d: { c: function (x) { return x.final - x.draft; }, b: 'draft', per: 100, what: 'rise in the roll from the draft to the final roll, per 100 on the draft' } },
    mizoram: { d: { c: function (x) { return x.final - x.draft; }, b: 'draft', per: 100, what: 'rise in the roll from the draft to the final roll, per 100 on the draft' } }
  };
  function deeper(d, box) {
    var M = MEASURE[S.slug], seated = SEATED.indexOf(S.slug) >= 0;
    Promise.all([SIR.json('data/' + S.slug + '/districts.json'), seated ? SIR.json('data/' + S.slug + '/constituencies.json') : null]).then(function (r) {
      var D = r[0], A = r[1], m = M.d, rate = function (x) { return m.per * m.c(x) / x[m.b]; };
      var st = m.per * D.reduce(function (t, x) { return t + m.c(x); }, 0) / D.reduce(function (t, x) { return t + x[m.b]; }, 0);
      var srt = D.slice().sort(function (a, b) { return rate(b) - rate(a); }), hi = srt[0], lo = srt[srt.length - 1];
      var el = document.createElement('section');
      el.innerHTML = '<h2 id="by-district">By district</h2><p class="sub">Measured by the ' + m.what + '.</p>' +
        '<div class="grid"><div class="panel wide" id="pDist"><div class="vizbox" id="vDist"></div></div></div><p class="finding" id="fDist"></p>' +
        '<details class="figs"><summary>Every district, in figures</summary><div class="twrap fit"><table id="tDist"></table></div></details>' +
        '<p class="golist"><span class="note">Every district has its own page:</span> ' + D.map(function (x) { return '<a class="chip" href="district/' + SIR.slug(x.district).slice(2) + '/">' + SIR.esc(x.district) + '</a>'; }).join(' ') + '</p>';
      box.appendChild(el);
      VIZ.lollipop('vDist', { label: d.state + ': the ' + m.what + ', by district', axis: 'Per ' + n(m.per),
        rows: srt.map(function (x) { var v = rate(x); return { name: x.district, v: Math.max(v, 0), text: d1(v), tok: '--fill-navy', hi: true }; }) });
      var sv = function (v) { return v < 0 ? 'minus ' + d1(-v) : d1(v); };
      document.getElementById('fDist').innerHTML = '<b>' + SIR.esc(hi.district) + ' is highest at ' + sv(rate(hi)) + ' per ' + n(m.per) + ' and ' + SIR.esc(lo.district) + ' lowest at ' + sv(rate(lo)) + ', against ' + sv(st) + ' for ' + SIR.esc(d.state) + '.</b>' + (rate(lo) < 0 ? ' A negative figure is a change the other way.' : '');
      SIR.table(document.getElementById('tDist'), [{ k: 'district', label: 'District', left: true }, { k: '_c', label: 'Count', fmt: n }, { k: '_b', label: 'Out of', fmt: n }, { k: '_r', label: 'Per ' + n(m.per), fmt: d1 }],
        D.map(function (x) { return { district: x.district, _c: m.c(x), _b: x[m.b], _r: rate(x) }; }), { sort: '_r' });
      if (!A) return;
      var s = M.s, over = A.filter(function (a) { return a.margin != null && s.c(a) > a.margin; });
      var es = document.createElement('section');
      es.innerHTML = '<h2 id="against-the-winning-margins">Against the winning margins</h2><p class="sub">Each constituency\'s ' + s.what + ' against the winning margin at its ' + s.year + ' Assembly election, from the Election Commission\'s results.</p>' +
        '<div class="grid"><div class="panel wide" id="pMargin"><div class="vizbox" id="vMargin"></div></div></div><p class="finding" id="fMargin"></p>' +
        '<details class="figs"><summary>Every constituency, in figures</summary><div class="twrap fit"><table id="tSeats"></table></div></details>';
      box.appendChild(es);
      VIZ.scatter('vMargin', { label: 'The ' + s.what + ' in each constituency against its ' + s.year + ' winning margin', diag: true, xMin: 0, yMin: 0,
        xAxis: s.year + ' winning margin', yAxis: s.what.charAt(0).toUpperCase() + s.what.slice(1), diagLabel: 'equal to the margin',
        points: A.filter(function (a) { return a.margin != null; }).map(function (a) { return { x: a.margin, y: Math.max(s.c(a), 0), tok: s.c(a) > a.margin ? '--fill-red' : '--fill-navy', label: a.name + ' (' + a.winner + '): ' + n(s.c(a)) + ', margin ' + n(a.margin) }; }) });
      document.getElementById('fMargin').innerHTML = '<b>In ' + over.length + ' of ' + A.length + ' constituencies the ' + s.what + ' ' + (s.are || 'is') + ' larger than the ' + s.year + ' winning margin.</b> Larger than the margin means large enough to decide a seat, never that it did, and the figures cannot show how anyone would have voted.';
      SIR.table(document.getElementById('tSeats'), [{ k: 'ac', label: 'No.' }, { k: 'name', label: 'Constituency', left: true }, { k: 'district', label: 'District', left: true }, { k: '_c', label: 'Count', fmt: n }, { k: 'winner', label: 'Won ' + s.year, left: true }, { k: 'margin', label: 'Margin', fmt: n }],
        A.map(function (a) { return { ac: a.ac, name: a.name, district: a.district, _c: s.c(a), winner: a.winner || '', margin: a.margin }; }), { sort: '_c' });
      SIR.tools();
    });
  }
  var hyph = function (s) { return s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''); };

  function load() {
    return P || (P = SIR.json('data/' + S.slug + '/summary.json').then(function (d) { d.v = {}; Object.keys(d.figures).forEach(function (k) { d.v[k] = d.figures[k].v; }); return d; }));
  }
  function press(d, k) { var f = d.figures[k]; return f && f.press; }
  // the name in a sentence: 'the Andaman and Nicobar Islands', and its possessive
  function nm(d, cap) { return d.article ? (cap ? 'The ' : 'the ') + d.state : d.state; }
  function poss(d, cap) { return nm(d, cap) + (/s$/.test(d.state) ? '\'' : '\'s'); }
  // who reported a press figure: the press, a state government, or both
  function via(d, keys) {
    var src = {}, by = {};
    d.sources.forEach(function (x) { src[x.id] = x; });
    keys.forEach(function (k) { var f = d.figures[k]; if (f && f.press) by[/^Government of/.test((src[f.src] || {}).title || '') ? 'gov' : 'press'] = 1; });
    return by.gov && by.press ? ', as the press and the state government reported' : by.gov ? ', as the state government reported' : by.press ? ', as reported in the press' : '';
  }
  // how the published reasons stand against the names left off
  function reasonGap(d) {
    var v = d.v, ks = ['dead', 'shifted_absent_other', 'duplicate'].filter(function (k) { return v[k] != null; });
    if (!ks.length || v.removed == null) return null;
    var sum = ks.reduce(function (a, k) { return a + v[k]; }, 0), gap = v.removed - sum;
    var rounded = ks.some(function (k) { return d.figures[k].rounded; }), unit = 1;
    if (rounded) while (unit < 1e5 && ks.every(function (k) { return v[k] % (unit * 10) === 0; })) unit *= 10;
    if (rounded && Math.abs(gap) <= unit / 2 * ks.length) return { kind: 'rounded', gap: gap };
    return { kind: gap > 0 ? 'short' : gap < 0 ? 'over' : 'exact', gap: gap };
  }
  function gapNote(d) {
    var g = reasonGap(d);
    if (!g) return '';
    if (g.kind === 'rounded') return 'The reasons were published only in lakh, so they add to the names left off at that rounding.';
    if (g.kind === 'short') return g.gap === 1 ? 'The published reasons leave one name without a reason.' : 'The published reasons leave ' + lk(g.gap) + ' names without a reason.';
    if (g.kind === 'over') return 'The published reasons add to ' + (g.gap === -1 ? 'one' : lk(-g.gap)) + ' more than the names left off.';
    return '';
  }
  function anyPress(d) { return Object.keys(d.figures).some(function (k) { return d.figures[k].press; }); }

  // the findings, the questions and the limits line, all from the figures
  function sentences(d) {
    var v = d.v, R = d.rates, st = d.state, out = {};
    if (d.revision === 'no_draft') {
      out.scale = nm(d, 1) + ' has not yet published a draft roll, so no count of names left off exists for it.';
      return out;
    }
    if (v.removed != null) {
      out.scale = poss(d, 1) + ' draft roll' + (d.dates.draft ? ' of ' + DATE(d.dates.draft) : '') + ' left off ' + lk(v.removed) + ' names' +
        (R.per_100 != null ? ', ' + d1(R.per_100) + ' of every 100 electors on the roll before the revision' : '') + via(d, ['removed', 'roll_before']) + '.';
    } else if (v.draft != null) {
      out.scale = poss(d, 1) + ' draft roll' + (d.dates.draft ? ' of ' + DATE(d.dates.draft) : '') + ' holds ' + lk(v.draft) + ' electors. No count of the names left off was found.';
    }
    if (R.shares) out.reasons = pc(R.shares.shifted_absent_other) + ' of the names left off were entered as shifted, absent or for another reason, ' + pc(R.shares.dead) + ' as dead and ' + pc(R.shares.duplicate) + ' as enrolled more than once' + ((reasonGap(d) || {}).kind === 'short' ? ', as far as the published reasons go.' : '.');
    if (v.final != null) {
      out.final = 'The final roll' + (d.dates.final ? ' of ' + DATE(d.dates.final) : '') + ' holds ' + lk(v.final) + ' electors' +
        (v.added_after != null && v.removed_after != null ? '. After the draft ' + lk(v.added_after) + ' names were added and ' + lk(v.removed_after) + ' removed' : '') +
        (v.net_after != null && v.net_after < 0 ? (v.added_after != null && v.removed_after != null ? ', so the roll fell by a further ' : '. The roll fell by a further ') + lk(-v.net_after) + ' after the draft.' :
         R.made_up_pct != null ? ', and the net rise is ' + d1(R.made_up_pct) + ' for every 100 left off. It counts people enrolling for the first time, so fewer than that were put back.' : '.');
    }
    if (R.women_removed_pct != null && R.women_before_pct != null)
      out.women = 'Women were ' + pc(R.women_removed_pct) + ' of the names left off and ' + pc(R.women_before_pct) + ' of the roll before the revision' +
        (R.women_per_100 != null ? ', ' + d1(R.women_per_100) + ' of every 100 women against ' + d1(R.men_per_100) + ' of every 100 men.' : '.');
    else if (R.women_final_pct != null) out.women = 'Women are ' + pc(R.women_final_pct) + ' of the final roll. No split of the names left off by sex was found.';
    if (v.notices != null) out.notices = (d.dates.notices ? 'By ' + DATE(d.dates.notices) + ', ' + lk(v.notices) + ' electors kept on the draft had been sent a notice' : lk(v.notices) + ' electors kept on the draft were to be sent a notice') + via(d, ['notices']) + '.';
    return out;
  }

  function limits(d) {
    var parts = [];
    if (anyPress(d)) parts.push('Figures marked as press reached us through newspapers, broadcasters or state government releases and were not read from a document of the Election Commission or the Chief Electoral Officer.');
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
    else if (v.net_after != null && v.net_after < 0) kp.push([lk(-v.net_after), 'fewer electors on the final roll than on the draft']);
    else if (R.made_up_pct != null) kp.push([d1(R.made_up_pct), 'per 100 left off, the net rise after the draft']);
    if (kp.length) h.push('<div class="kpis">' + kp.map(function (k) { return '<div><b>' + k[0] + '</b><span>' + k[1] + '</span></div>'; }).join('') + '</div>');

    // a state whose constituency table is complete has a page per seat and
    // per district (build_states.py SEATS), reached from this finder
    var seated = SEATED.indexOf(S.slug) >= 0;
    if (seated) h.push('<h2 id="find-a-constituency-or-district">Find a constituency or district</h2><p class="sub">Every constituency and district has a page of its own, set against its district and the state.</p><div class="finder" id="finder"></div>');
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
        '<details class="figs"><summary>Every ' + lv[0] + ', in figures</summary><div class="twrap fit" tabindex="0" role="region" aria-label="Every ' + lv[0] + ', in figures"><table id="tT' + i + '"></table></div></details>');
    });
    if (s.notices) h.push('<h2 id="notices">Notices</h2><p>' + s.notices + ' The counts for every state are on <a href="../india/process/#notices-the-no-mapping-list-and-the-discrepancy-list">How the revision was run</a>.</p>');
    h.push('<p class="note">' + SIR.esc(poss(d, 1)) + ' dates are drawn beside every other state\'s on <a href="../india/process/#s-' + hyph(d.state) + '">How the revision was run</a>.' + (d.revision === 'no_draft' ? ' The <a href="method/">method page</a> lists each source.' : ' Every figure on this page is in the CSV on the Downloads page, and the <a href="method/">method page</a> lists each source.') + '</p>');
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
      document.getElementById('nReason').textContent = ((s.reasons || '') + ' ' + gapNote(d)).trim();
    }
    if (R.women_removed_pct != null) {
      VIZ.dumbbell('vWomen', { label: 'Women\'s share of the roll before the revision and of the names left off', min: Math.floor(Math.min(R.women_before_pct, R.women_removed_pct) / 5) * 5 - 5, step: 5,
        aName: 'Share of the roll before', aTok: '--fill-grey', bName: 'Share of the names left off', bTok: '--fill-red', rows: [{ name: d.state, a: R.women_before_pct, b: R.women_removed_pct }] });
    }
    d.tables.forEach(function (t, i) { table(t, i, d); });
    if (MEASURE[S.slug]) deeper(d, box);
    if (seated) Promise.all([SIR.json('data/' + S.slug + '/constituencies.json'), SIR.json('data/' + S.slug + '/districts.json')]).then(function (r) {
      var A = r[0], D = r[1];
      var facts = function (x) {
        var f = [];
        if (x.before != null) f.push(['Roll before the revision', n(x.before)]);
        if (x.draft != null) f.push(['Draft roll', n(x.draft)]);
        if (x.removed != null && x.before != null) f.push(['Left off the draft', n(x.removed) + ', ' + d1(100 * x.removed / x.before) + ' per 100']);
        if (x.added != null) f.push(['Added after the draft', n(x.added)]);
        if (x.removed != null && x.before == null) f.push(['Removed after the draft', n(x.removed)]);
        if (x.removed_after != null) f.push(['Removed after the draft', n(x.removed_after)]);
        if (x.final != null) f.push(['Final roll', n(x.final)]);
        if (x.margin != null) f.push(['Winning margin', n(x.margin) + (x.winner ? ', ' + x.winner : '')]);
        return SIR.facts(f);
      };
      var say = function (x, nm2) { return nm2 + ', ' + d.state + '. ' + (x.removed != null && x.before != null ? n(x.removed) + ' names were left off the draft roll, ' + d1(100 * x.removed / x.before) + ' of every 100 on the roll before the revision.' : x.final != null && x.draft != null ? 'From the draft to the final roll the roll ' + (x.final >= x.draft ? 'rose by ' + n(x.final - x.draft) : 'fell by ' + n(x.draft - x.final)) + '.' : '') + ' Counts from the Chief Electoral Officer\'s tables.'; };
      var seatsOf = function (x) { return A.filter(function (a) { return a.district === x.district; }); };
      var DSET = { rows: D, key: function (x) { return SIR.slug(x.district); }, label: function (x) { return x.district + ' district'; },
        card: function (x) { return facts(x) + '<p class="note">Its constituencies</p>' + SIR.goList(seatsOf(x), function (a) { return 'ac-' + a.ac; }, function (a) { return a.ac + '. ' + a.name; }); },
        share: function (x) { return say(x, x.district + ' district'); } };
      SIR.finder('finder', { seatPages: true, districtPages: true, rows: A, more: [DSET], prompt: 'Find a constituency or district', placeholder: 'Type a name, a number or a district',
        key: function (a) { return 'ac-' + a.ac; }, label: function (a) { return a.ac + '. ' + a.name + ' (' + a.district + ')'; },
        card: facts, share: function (a) { return say(a, a.name); } });
    });
    SIR.showFaq(S.id, 'main');
  }

  function table(t, i, d) {
    var lv = LEVEL[t.level], rows = t.rows.slice(), note = document.getElementById('nT' + i), cols, data;
    if (t.kind === 'left_off' && !rows.some(function (r) { return r.per_100 != null; })) {
      document.getElementById('pT' + i).hidden = true;
      cols = [{ h: lv[0].charAt(0).toUpperCase() + lv[0].slice(1) }, { h: t.removed_label || 'Left off', num: true }, { h: 'Dead', num: true }, { h: 'Shifted, absent or other', num: true }, { h: 'Enrolled more than once', num: true }];
      data = rows.map(function (r) { var o = function (x) { return x == null ? '–' : n(x); }; return [SIR.esc(r.name), o(r.removed), o(r.dead), o(r.shifted_absent_other), o(r.duplicate)]; });
      document.getElementById('tT' + i).closest('details').open = true;
    } else if (t.kind === 'left_off') {
      rows = rows.filter(function (r) { return r.per_100 != null; });
      rows.sort(function (a, b) { return b.per_100 - a.per_100; });
      VIZ.lollipop('vT' + i, { label: 'Names left off per 100 electors, by ' + lv[0], axis: 'Per 100 electors on the roll before', rows: rows.map(function (r) { return { name: r.name, v: r.per_100, text: d1(r.per_100), tok: '--fill-red', hi: true }; }) });
      var last = rows[rows.length - 1];
      // a short partial table is a few named rows, so it ranks them among themselves only
      if (rows.length === 1) note.textContent = rows[0].name + ' left off ' + d1(rows[0].per_100) + ' of every 100 electors.';
      else if (t.partial && rows.length === 2) note.textContent = 'Of the two, ' + rows[0].name + ' lost more for its size, ' + d1(rows[0].per_100) + ' of every 100 electors, against ' + d1(last.per_100) + ' in ' + last.name + '.';
      else note.textContent = (t.partial && rows.length === 3 ? 'Of the three, ' + rows[0].name : rows[0].name) + ' lost the most for its size, ' + d1(rows[0].per_100) + ' of every 100 electors, and ' + last.name + ' the least, ' + d1(last.per_100) + '.';
      cols = [{ h: lv[0].charAt(0).toUpperCase() + lv[0].slice(1) }, { h: 'Roll before', num: true }, { h: 'Draft', num: true }, { h: t.removed_label || 'Left off', num: true }, { h: 'Per 100', num: true }];
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
      var withDraft = key === 'final' && rows.some(function (r) { return r.draft != null; });
      cols = [{ h: lv[0].charAt(0).toUpperCase() + lv[0].slice(1) }].concat(withDraft ? [{ h: 'Draft', num: true }] : [], [{ h: key === 'draft' ? 'Draft' : 'Final', num: true }, { h: 'Women', num: true }, { h: 'Women, per cent', num: true }]);
      data = rows.map(function (r) { return [SIR.esc(r.name)].concat(withDraft ? [r.draft == null ? '–' : n(r.draft)] : [], [n(r[key]), r.women == null ? '–' : n(r.women), r.women_pct == null ? '–' : pc(r.women_pct)]); });
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

  // why there is no table below the state, in whole sentences: the reason
  // given in cannot_show, without the item's opening phrase
  function below(d) {
    var where = d.ut ? 'union territory' : 'state';
    if (d.revision === 'no_draft') return 'No draft roll has been published, so there are no figures for ' + nm(d) + ' yet, for the ' + where + ' or below it.';
    var item = (d.cannot_show || []).filter(function (t) { return /district|constituenc|ward|sector|below the/i.test(t); })[0] || '';
    var rest = item.replace(/^[^.]*\.\s*/, '');
    return rest && !/^No table below the (state|union territory) was found\.?$/.test(rest) ? rest : 'No table below the ' + where + ' was found for ' + nm(d) + '.';
  }

  SIR.faq(S.id, S.slug + '/faq/', function () {
    return load().then(function (d) {
      var s = sentences(d), v = d.v, QA = [], lim = limits(d);
      if (s.scale) QA.push(['How many names were left off in ' + nm(d) + '?', s.scale + (s.reasons ? ' ' + s.reasons + ' ' + (gapNote(d) ? gapNote(d) + ' ' : '') + 'A reason is what the officer wrote down, and nobody checked it.' : ''), ['main', 'faq']]);
      if (s.final) QA.push(['How many came back before the final roll?', s.final, ['main', 'faq']]);
      if (s.women) QA.push(['Were women left off more than men?', s.women, ['main', 'faq']]);
      if (d.tables.length) QA.push(['Is there a figure for each district or constituency?', d.tables.map(function (t) { return t.title + (t.partial ? ', for some ' + LEVEL[t.level][1] + ' only' : '') + (t.press ? ', from the press' : '') + '.'; }).join(' '), ['main', 'faq']]);
      else QA.push(['Is there a figure for each district or constituency?', below(d), ['main', 'faq']]);
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
