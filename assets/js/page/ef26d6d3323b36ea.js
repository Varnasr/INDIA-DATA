Promise.all([SIR.json('data/karnataka/summary.json'), SIR.json('data/karnataka/districts.json')]).then(function (r) {
  var S = r[0], D = r[1], B = S.bengaluru, R = S.rest;
  var RS = [['absent', L('Absent')], ['shifted', L('Shifted')], ['dead', L('Dead')], ['duplicate', L('Already enrolled')], ['other', L('Other')]];
  var tok = function (d) { return d.bengaluru ? '--fill-red' : '--fill-navy'; };
  VIZ.lollipop('cDist', { label: L('Names left off per 100 electors, by district'), axis: L('Left off per 100 electors'),
    rows: D.map(function (d) { return { name: d.district, v: d.per_100, text: SIR.d(d.per_100, 1), tok: tok(d), hi: d.bengaluru }; }) });
  var low = D[D.length - 1], next = D.filter(function (d) { return !d.bengaluru; });
  document.getElementById('fDist').innerHTML = L('<b>Bengaluru\'s four districts lost between {lo} and {hi} of every 100 electors, against {s} for the state.</b> The next highest is {n1} at {n1v}. {low} lost the fewest, {lowv}.', {
    lo: SIR.d(Math.min.apply(null, D.filter(function (d) { return d.bengaluru; }).map(function (d) { return d.per_100; })), 1),
    hi: SIR.d(D[0].per_100, 1), s: SIR.d(S.per_100, 1), n1: next[0].district, n1v: SIR.d(next[0].per_100, 1), low: low.district, lowv: SIR.d(low.per_100, 1) });

  var tiles = [[SIR.pct(B.share_of_roll), L('of the roll before the revision'), B.share_of_roll],
    [SIR.pct(B.share_of_removed), L('of the names left off the draft'), B.share_of_removed],
    [SIR.d(B.per_100, 1), L('left off per 100 electors, against {r} in the rest of the state', { r: SIR.d(R.per_100, 1) }), B.per_100]];
  document.getElementById('cBlr').innerHTML = tiles.map(function (t) {
    return '<div class="big"><b>' + t[0] + '</b><i style="--w:' + t[2].toFixed(1) + '%"></i><span>' + t[1] + '</span></div>';
  }).join('');
  document.getElementById('fBlr').innerHTML = L('<b>Bengaluru holds {roll} of Karnataka\'s roll and {rem} of the names left off the draft, {n} names in all.</b> {sa} of them were entered as shifted or absent and {dead} as dead. In the rest of the state the figures are {rsa} and {rdead}.', {
    roll: SIR.pct(B.share_of_roll), rem: SIR.pct(B.share_of_removed), n: SIR.lakh(B.removed), sa: SIR.pct(B.shifted_absent_share), dead: SIR.pct(B.dead_share), rsa: SIR.pct(R.shifted_absent_share), rdead: SIR.pct(R.dead_share) });

  VIZ.heat('cMix', { label: L('Share of each district\'s names left off, by reason'), cols: RS.map(function (k) { return k[1]; }), tok: ['--fill-amber', '--fill-navy', '--fill-purple', '--fill-red', '--fill-grey'], unit: '%',
    rows: D.map(function (d) { return { name: d.district, v: RS.map(function (k) { return d.shares[k[0]]; }) }; }) });
  document.getElementById('fMix').innerHTML = L('<b>Across the state, {sh} of the names were entered as shifted and {ab} as absent, {dead} as dead and {dup} as already enrolled elsewhere.</b> The more names a district lost, the larger the share marked shifted or absent (rank correlation {rho}, where 0 means the two are unrelated and 1 means they rise in step). Where fewer were left off, more were entered as dead, up to {dm} in {dmn}. A reason on the list is what the officer wrote down, and nobody checked it.', {
    sh: SIR.pct(S.shares.shifted), ab: SIR.pct(S.shares.absent), dead: SIR.pct(S.shares.dead), dup: SIR.pct(S.shares.duplicate), rho: SIR.d(S.rho_rate_shifted, 2), dm: SIR.pct(S.dead_max.share), dmn: S.dead_max.district });

  VIZ.waterfall('vWater', { label: L('Karnataka: the roll from 16 June to 9 October 2026'), from: Math.floor(S.draft * 0.8 / 1e6) * 1e6, steps: [
    { name: L('Roll of 16 June'), v: S.before, kind: 'total' }, { name: L('Shifted'), v: S.reasons.shifted, kind: 'down' },
    { name: L('Dead'), v: S.reasons.dead, kind: 'down' }, { name: L('Absent'), v: S.reasons.absent, kind: 'down' },
    { name: L('Already enrolled'), v: S.reasons.duplicate, kind: 'down' }, { name: L('Other'), v: S.reasons.other, kind: 'down' },
    { name: L('Draft roll'), v: S.draft, kind: 'total' }, { name: L('Net change after the draft'), v: S.added_sep, kind: 'up' },
    { name: L('Roll of 9 October'), v: S.sep, kind: 'total' }] });
  VIZ.multiples('vBack', { label: L('Each district\'s roll on 16 June, at the draft and on 9 October, 16 June = 100'), ref: 100,
    steps: [L('16 June'), L('Draft'), L('9 October')],
    panels: D.map(function (d) { return { name: d.district, hi: d.bengaluru, v: [100, 100 * d.draft / d.before, 100 * d.sep / d.before] }; }) });
  document.getElementById('fBack').innerHTML = L('<b>By 9 October the roll had risen by {a} since the draft, {m} of the {r} names left off.</b> In Bengaluru it rose by {ba}, against {bn} names left off. Elsewhere the rise came to {rm} of the names left off. The final roll may change this, and the rise includes new voters.', {
    a: SIR.n(S.added_sep), m: SIR.pct(S.made_up_pct), r: SIR.lakh(S.removed), ba: SIR.n(B.added_sep), bn: SIR.lakh(B.removed), rm: SIR.pct(R.made_up_pct) });

  document.getElementById('fWomen').innerHTML = L('<b>Women were {d} of the draft roll and {s} of the roll of 9 October.</b> The roll before the revision gives no count by sex, so these two figures cannot show whether women were left off more often than men.', { d: SIR.pct(S.women_draft_pct), s: SIR.pct(S.women_sep_pct) });

  SIR.table(document.getElementById('tDist'), [
    { k: 'district', label: L('District'), left: true },
    { k: 'before', label: L('Roll before'), fmt: SIR.n }, { k: 'removed', label: L('Left off'), fmt: SIR.n },
    { k: 'per_100', label: L('Per 100'), fmt: function (v) { return SIR.d(v, 1); } },
    { k: 'shifted', label: L('Shifted'), fmt: SIR.n }, { k: 'absent', label: L('Absent'), fmt: SIR.n },
    { k: 'dead', label: L('Dead'), fmt: SIR.n }, { k: 'duplicate', label: L('Already enrolled'), fmt: SIR.n },
    { k: 'sep', label: L('Roll of 9 Oct'), fmt: SIR.n }, { k: 'net_per_100', label: L('Net fall per 100'), fmt: function (v) { return SIR.d(v, 1); } }
  ], D, { sort: 'per_100' });
  var slugD = function (d) { return SIR.slug(d.district); };
  var byName = {}, idOf = {}; D.forEach(function (d) { byName[d.district] = d; });
  var F = SIR.finder('finder', { districtPages: true, rows: D, key: slugD, label: function (d) { return d.district; }, prompt: L('Find a district'), placeholder: L('Type a district name'),
    pick: function (d) { var b = document.getElementById('vMap'); if (b.__select && idOf[d.district]) b.__select(idOf[d.district]); },
    card: function (d) { return SIR.facts([
      [L('Roll of 16 June'), SIR.n(d.before)], [L('Names left off the draft'), SIR.n(d.removed)], [L('Per 100 electors'), SIR.d(d.per_100, 1)],
      [L('Shifted'), SIR.n(d.shifted)], [L('Absent'), SIR.n(d.absent)], [L('Dead'), SIR.n(d.dead)], [L('Already enrolled'), SIR.n(d.duplicate)],
      [L('Roll of 9 October'), SIR.n(d.sep)], [L('Change since the draft'), (d.added_sep >= 0 ? '+' : '') + SIR.n(d.added_sep)]]); },
    share: function (d) { return L('{n}, Karnataka. {r} names were left off the draft roll in this district, {p} of every 100 electors. {s} were entered as shifted and {dd} as dead. By 9 October the roll had changed by {a} since the draft. These are counts from the Chief Electoral Officer\'s press notes. A reason on the list is what the officer wrote down, and nobody checked it.', { n: d.district, r: SIR.n(d.removed), p: SIR.d(d.per_100, 1), s: SIR.n(d.shifted), dd: SIR.n(d.dead), a: (d.added_sep >= 0 ? '+' : '') + SIR.n(d.added_sep) }); } });
  SIR.json('data/geo/karnataka.json').then(function (geo) {
    var byId = {};
    geo.features.forEach(function (f) { var d = byName[f.properties.name]; if (d) { byId[f.properties.ac] = d; idOf[d.district] = f.properties.ac; } });
    VIZ.map('vMap', { geo: geo, label: L('Map of names left off the draft per 100 electors, by district'), title: L('Left off per 100 electors'),
      v: function (id) { return byId[id] ? byId[id].per_100 : null; }, name: function (id) { return byId[id] ? byId[id].district : ''; },
      inset: { name: L('Bengaluru city'), acs: geo.features.filter(function (f) { return /^B\.B\.M\.P/.test(f.properties.name); }).map(function (f) { return f.properties.ac; }), left: true },
      pick: function (id) { if (byId[id]) F.select(byId[id]); } });
    var it = F.item[SIR.hashId()]; if (it && it.s.pick) it.s.pick(it.r);
    SIR.tools();
  });
  SIR.showFaq('ka', 'main');
}).catch(SIR.fail);
