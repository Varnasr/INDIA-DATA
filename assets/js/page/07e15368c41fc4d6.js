Promise.all([SIR.json('data/tamilnadu/summary.json'), SIR.json('data/tamilnadu/districts.json'), SIR.json('data/tamilnadu/constituencies.json')]).then(function (r) {
  var S = r[0], D = r[1], A = r[2];
  var RS = [['dead', L('Dead'), '--fill-grey'], ['shifted_absent', L('Shifted or absent'), '--fill-navy'], ['multiple', L('Enrolled in more than one place'), '--fill-amber']];
  var labels = D.map(function (d) { return d.district; });
  VIZ.lollipop('cDist', { label: L('Names left off per 100 electors, by district'), axis: L('Left off per 100 electors'),
    rows: D.map(function (d) { return { name: d.district, v: d.per_100, text: SIR.d(d.per_100, 1), tok: d.district === 'Chennai' ? '--fill-red' : '--fill-navy', hi: d.district === 'Chennai' }; }) });
  var low = D[D.length - 1];
  document.getElementById('fDist').innerHTML = L('<b>Chennai lost {c} of every 100 electors, against {s} for the state.</b> The next four are {next}. {lo} lost the fewest, {lov}.', {
    c: SIR.d(D[0].per_100, 1), s: SIR.d(S.per_100, 1), lo: low.district, lov: SIR.d(low.per_100, 1),
    next: D.slice(1, 5).map(function (d) { return L('{s} ({v})', { s: d.district, v: SIR.d(d.per_100, 1) }); }).join(', ') });

  VIZ.heat('cMix', { label: L('Share of each district\'s names left off, by reason'), cols: RS.map(function (k) { return k[1]; }), tok: ['--fill-purple', '--fill-navy', '--fill-amber'], unit: '%',
    rows: D.map(function (d) { return { name: d.district, v: RS.map(function (k) { return 100 * d[k[0]] / d.removed; }) }; }) });
  var byDead = D.slice().sort(function (a, b) { return b.dead_share - a.dead_share; });
  document.getElementById('fMix').innerHTML = L('<b>Across the state, {sh} of the names were entered as shifted or absent and {dead} as dead.</b> In Chennai the share entered as shifted or absent is {csh}. Where fewer names were left off, more of them were entered as dead, up to {dmax} in {dmaxn}. A reason on the list is what the officer wrote down, and nobody checked it.', {
    sh: SIR.pct(S.shares.shifted_absent), dead: SIR.pct(S.shares.dead), csh: SIR.pct(S.chennai.shifted_share), dmax: SIR.pct(byDead[0].dead_share), dmaxn: byDead[0].district });

  var C = A.filter(function (a) { return a.district === 'Chennai'; }).sort(function (a, b) { return b.per_100 - a.per_100; });
  SIR.chart('cChennai', { type: 'bar', data: { labels: C.map(function (a) { return a.name; }), datasets: RS.map(function (k) { return { label: k[1], data: C.map(function (a) { return +(100 * a[k[0]] / a.before).toFixed(1); }), $token: k[2] }; }) },
    options: { indexAxis: 'y', scales: { y: { stacked: true, ticks: { autoSkip: false } }, x: { stacked: true, beginAtZero: true, title: { display: true, text: L('Left off per 100 electors') } } } } });
  document.getElementById('fChennai').innerHTML = L('<b>Every one of Chennai\'s {n} constituencies lost more than {min} of every 100 electors.</b> {hi} lost {hiv}, the most of any seat in the state. Chennai holds {roll} of the state\'s roll and {rem} of the names left off the draft.', {
    n: C.length, min: Math.floor(C[C.length - 1].per_100), hi: C[0].name, hiv: SIR.d(C[0].per_100, 1), roll: SIR.pct(S.chennai_share_of_roll), rem: SIR.pct(S.chennai_share_of_removed) });

  VIZ.waterfall('vWater', { label: L('Tamil Nadu: the roll from before the revision to the final roll'), from: Math.floor(S.draft * 0.8 / 1e5) * 1e5, steps: [
    { name: L('Roll before the revision'), v: S.before, kind: 'total' }, { name: L('Dead'), v: S.dead, kind: 'down' },
    { name: L('Shifted or absent'), v: S.shifted_absent, kind: 'down' }, { name: L('Enrolled in more than one place'), v: S.multiple, kind: 'down' },
    { name: L('Draft roll'), v: S.draft, kind: 'total' }, { name: L('Net change after the draft'), v: S.added_net, kind: 'up' },
    { name: L('Final roll'), v: S.final, kind: 'total' }] });
  VIZ.slope('vFinal', { label: L('Names left off per 100 electors at the draft and the net fall at the final roll, by district'),
    aName: L('At the draft'), bName: L('At the final roll'),
    rows: D.map(function (d, i) { return { name: d.district, a: d.per_100, b: d.net_per_100, hi: d.district === 'Chennai', lab: i > 0 && i < 4 }; }) });
  document.getElementById('fFinal').innerHTML = L('<b>The final roll is {a} larger than the draft, and still {f} smaller than the roll before the revision.</b> That is a fall of {p} of every 100 electors. The rise from the draft is at most {m} of the names left off, and it includes new voters. Chennai\'s roll is {c} per 100 smaller than before.', {
    a: SIR.lakh(S.added_net), f: SIR.lakh(S.net_fall), p: SIR.d(S.net_per_100, 1), m: SIR.pct(S.made_up_pct), c: SIR.d(S.chennai.net_per_100, 1) });

  SIR.table(document.getElementById('tAc'), [
    { k: 'ac', label: L('No.') }, { k: 'name', label: L('Constituency'), left: true }, { k: 'district', label: L('District'), left: true },
    { k: 'before', label: L('Roll before'), fmt: SIR.n }, { k: 'removed', label: L('Left off'), fmt: SIR.n },
    { k: 'per_100', label: L('Per 100'), fmt: function (v) { return SIR.d(v, 1); } },
    { k: 'shifted_absent', label: L('Shifted or absent'), fmt: SIR.n }, { k: 'dead', label: L('Dead'), fmt: SIR.n },
    { k: 'final', label: L('Final roll'), fmt: SIR.n }, { k: 'net_per_100', label: L('Net fall per 100'), fmt: function (v) { return SIR.d(v, 1); } }
  ], A, { sort: 'per_100' });

  // women: the fall from the January 2025 roll to the draft, by district
  var WJ = {}; A.forEach(function (a) { var w = WJ[a.district] || (WJ[a.district] = { name: a.district, jw: 0, j: 0, fw: 0, f: 0 }); w.j += a.jan2025; w.jw += a.jan2025 * a.jan2025_women_pct / 100; w.f += a.fall_jan; w.fw += a.fall_jan * a.fall_jan_women_pct / 100; });
  var WJR = Object.keys(WJ).map(function (k) { var w = WJ[k]; return { name: w.name, a: 100 * w.jw / w.j, b: 100 * w.fw / w.f }; }).sort(function (x, y) { return (y.b - y.a) - (x.b - x.a); });
  VIZ.dumbbell('vWomenJan', { label: L('Women\'s share of the January 2025 roll and of the fall from it to the draft, by district'), min: 46, step: 2, ref: 50,
    aName: L('Women\'s share of the January 2025 roll, %'), aTok: '--fill-grey', bName: L('Women\'s share of the fall to the draft, %'), bTok: '--fill-red', rows: WJR });
  document.getElementById('fWomenJan').innerHTML = L('<b>From the final roll of January 2025 to the draft, the roll fell by {f}, and women were {w} of that fall against {r} of the January roll.</b> {pw} of every 100 women on that roll and {pm} of every 100 men were not on the draft. Women\'s share of the fall was above their share of the roll in {k} of the {n} constituencies, most of all in {x}, at {xw}. The fall also counts ten months of ordinary deaths, moves and new names, so it is not the names left off the draft.',
    { f: SIR.lakh(S.fall_jan), w: SIR.pct(S.fall_jan_women_pct), r: SIR.pct(S.jan2025_women_pct), pw: SIR.d(S.fall_jan_per_100_women, 1), pm: SIR.d(S.fall_jan_per_100_men, 1), k: S.acs_women_fall_over, n: S.acs, x: S.women_fall_max, xw: SIR.pct(S.women_fall_max_pct) });

  // women after the draft, summed from the constituency rolls
  var WD = {}; A.forEach(function (a) { var w = WD[a.district] || (WD[a.district] = { name: a.district, dw: 0, fw: 0, d: 0, f: 0 }); w.dw += a.draft_women; w.fw += a.final_women; w.d += a.draft; w.f += a.final; });
  var WR = Object.keys(WD).map(function (k) { var w = WD[k]; return { name: w.name, a: 100 * w.dw / w.d, b: 100 * (w.fw - w.dw) / (w.f - w.d) }; }).sort(function (x, y) { return (y.b - y.a) - (x.b - x.a); });
  VIZ.dumbbell('vWomen', { label: L('Women\'s share of the draft roll and of the net rise to the final roll, by district'), min: 48, step: 2, ref: 50,
    aName: L('Women\'s share of the draft roll, %'), aTok: '--fill-grey', bName: L('Women\'s share of the net rise to the final roll, %'), bTok: '--fill-red', rows: WR });
  var tw = A.reduce(function (t, a) { t.dw += a.draft_women; t.fw += a.final_women; t.d += a.draft; t.f += a.final; return t; }, { dw: 0, fw: 0, d: 0, f: 0 });
  var kw = WR.filter(function (w) { return w.b > w.a; }).length, wv = { d: SIR.pct(100 * tw.dw / tw.d), r: SIR.pct(100 * (tw.fw - tw.dw) / (tw.f - tw.d)), k: kw, n: WR.length };
  document.getElementById('fWomen').innerHTML = (kw === WR.length
    ? L('<b>Women were {d} of the draft roll and {r} of the net rise to the final roll.</b> Their share of the rise was higher than their share of the draft in all {n} districts. The rise counts new voters as well as names put back, so it does not say how many women\'s names were restored.', wv)
    : L('<b>Women were {d} of the draft roll and {r} of the net rise to the final roll.</b> Their share of the rise was higher than their share of the draft in {k} of the {n} districts. The rise counts new voters as well as names put back, so it does not say how many women\'s names were restored.', wv));

  SIR.table(document.getElementById('tDist'), [
    { k: 'district', label: L('District'), left: true }, { k: 'acs', label: L('Seats') },
    { k: 'before', label: L('Roll before'), fmt: SIR.n }, { k: 'removed', label: L('Left off'), fmt: SIR.n },
    { k: 'per_100', label: L('Per 100'), fmt: function (v) { return SIR.d(v, 1); } },
    { k: 'dead', label: L('Dead'), fmt: SIR.n }, { k: 'shifted_absent', label: L('Shifted or absent'), fmt: SIR.n }, { k: 'multiple', label: L('Enrolled in more than one place'), fmt: SIR.n },
    { k: 'final', label: L('Final roll'), fmt: SIR.n }, { k: 'net_per_100', label: L('Net fall per 100'), fmt: function (v) { return SIR.d(v, 1); } }
  ], D, { sort: 'per_100' });
  SIR.json('data/geo/tamilnadu.json').then(function (geo) {
    var byAc = {}; A.forEach(function (a) { byAc[a.ac] = a; });
    var seatsOf = function (d) { return A.filter(function (a) { return a.district === d.district; }); };
    var DSET = { rows: D, key: function (d) { return SIR.slug(d.district); }, label: function (d) { return L('{d} district', { d: d.district }); },
      card: function (d) { return SIR.facts([
        [L('Names left off the draft'), SIR.n(d.removed)], [L('Per 100 electors'), SIR.d(d.per_100, 1)],
        [L('Entered as dead'), SIR.n(d.dead)], [L('Shifted or absent'), SIR.n(d.shifted_absent)], [L('Enrolled in more than one place'), SIR.n(d.multiple)],
        [L('Fall at the final roll, per 100'), SIR.d(d.net_per_100, 1)], [L('Constituencies'), SIR.n(d.acs)]]) + '<p class="note">' + L('Its constituencies') + '</p>' + SIR.goList(seatsOf(d), function (a) { return 'ac-' + a.ac; }, function (a) { return a.ac + '. ' + a.name; }); },
      share: function (d) { return L('{d} district, Tamil Nadu. {r} names were left off the draft roll here, {p} of every 100 electors, across {n} constituencies. These are counts from the Chief Electoral Officer\'s published tables. A reason on the list is what the officer wrote down, and nobody checked it.', { d: d.district, r: SIR.n(d.removed), p: SIR.d(d.per_100, 1), n: d.acs }); },
      pick: function (d) { var b = document.getElementById('vMap'); if (b.__select) b.__select(seatsOf(d).map(function (a) { return a.ac; })); } };
    var F = SIR.finder('finder', { seatPages: true, districtPages: true, rows: A, more: [DSET], prompt: L('Find a constituency or district'), placeholder: L('Type a name, a number or a district'), key: function (a) { return 'ac-' + a.ac; }, label: function (a) { return a.ac + '. ' + a.name + ' (' + a.district + ')'; },
      card: function (a) { return SIR.facts([
        [L('Names left off the draft'), SIR.n(a.removed)], [L('Per 100 electors'), SIR.d(a.per_100, 1)],
        [L('Entered as dead'), SIR.n(a.dead)], [L('Not entered as dead'), SIR.n(a.removed - a.dead)],
        [L('Shifted or absent'), SIR.n(a.shifted_absent)], [L('Enrolled in more than one place'), SIR.n(a.multiple)],
        [L('Fall at the final roll, per 100'), SIR.d(a.net_per_100, 1)], [L('Won in 2026'), a.winner + ' · ' + L('margin {m}', { m: SIR.n(a.margin) })],
        [L('Left off more than the margin'), a.over_margin ? L('Yes') : L('No')]]); },
      share: function (a) { return L('{n}, Tamil Nadu. {r} names were left off the draft roll here, {p} of every 100 electors. {nd} of them were not entered as dead. The seat was won in 2026 by {m} votes. These are counts from the Chief Electoral Officer\'s published tables. A reason on the list is what the officer wrote down, and nobody checked it.', { n: a.name, r: SIR.n(a.removed), p: SIR.d(a.per_100, 1), nd: SIR.n(a.removed - a.dead), m: SIR.n(a.margin) }); },
      pick: function (a) { var b = document.getElementById('vMap'); if (b.__select) b.__select(a.ac); } });
    VIZ.map('vMap', { geo: geo, label: L('Map of names left off per 100 electors, by constituency'), title: L('Left off per 100 electors'),
      v: function (ac) { return byAc[ac] ? byAc[ac].per_100 : null; }, name: function (ac) { return byAc[ac] ? byAc[ac].name : ''; },
      inset: { name: L('Chennai'), acs: A.filter(function (a) { return a.district === 'Chennai'; }).map(function (a) { return a.ac; }), left: true },
      pick: function (ac) { if (byAc[ac]) F.select(byAc[ac]); } });
    var it = F.item[SIR.hashId()]; if (it && it.s.pick) it.s.pick(it.r);
    SIR.tools();
  });
  SIR.showFaq('tn', 'main');
}).catch(SIR.fail);
