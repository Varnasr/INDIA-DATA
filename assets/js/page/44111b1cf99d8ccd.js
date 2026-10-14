Promise.all([SIR.json('data/tamilnadu/summary.json'), SIR.json('data/tamilnadu/constituencies.json')]).then(function (r) {
  var S = r[0], A = r[1];
  var G = [['TVK', '--fill-amber'], ['DMK', '--fill-red'], ['AIADMK', '--fill-navy']];
  var groups = G.map(function (g) { return { label: g[0], test: function (a) { return a.winner === g[0]; }, tok: g[1] }; })
    .concat([{ label: L('Other parties'), test: function (a) { return ['TVK', 'DMK', 'AIADMK'].indexOf(a.winner) < 0; }, tok: '--fill-grey' }]);
  var maxX = Math.max.apply(null, A.map(function (a) { return a.removed; })), minX = Math.min.apply(null, A.map(function (a) { return a.removed; }));
  SIR.chart('cScatter', { type: 'scatter', data: { datasets: groups.map(function (g) {
      return { label: g.label, data: A.filter(g.test).map(function (a) { return { x: a.removed, y: a.margin, n: a.name, w: a.winner }; }), $token: g.tok, pointRadius: 3.5 };
    }).concat([{ type: 'line', label: L('Margin equals names left off'), data: [{ x: minX, y: minX }, { x: maxX, y: maxX }], $token: '--fill-other', pointRadius: 0, borderDash: [5, 4], borderWidth: 1.5 }]) },
    options: { plugins: { tooltip: { callbacks: { label: function (c) { return c.raw.n ? L('{n} ({w}): {x} left off, margin {y}', { n: c.raw.n, w: c.raw.w, x: SIR.n(c.raw.x), y: SIR.n(c.raw.y) }) : ''; } } } },
      scales: { x: { type: 'logarithmic', title: { display: true, text: L('Names left off the draft roll (log scale)') } }, y: { type: 'logarithmic', title: { display: true, text: L('2026 winning margin, votes (log scale)') } } } } });
  document.getElementById('fScatter').innerHTML = L('<b>In {k} of the {n} constituencies, more names were left off the draft roll than the 2026 winning margin.</b> The names left off and the margins rise together a little (rank correlation between the rate left off and the margin as a share of votes, {rho}, where 0 means the two are unrelated and 1 means they rise in step), so the seats that lost the most names were not the closest contests.', { k: S.over_margin, n: S.acs, rho: SIR.d(S.rho_rate_margin, 2) });

  var counts = [[L('Left off the draft'), S.over_margin], [L('Net fall at the final roll'), S.net_over_margin], [L('Living left off, at turnout'), S.could_change]];
  document.getElementById('cCounts').innerHTML = counts.map(function (c) {
    return '<div class="big"><b>' + c[1] + '</b><span class="of">' + L('of {n} seats', { n: S.acs }) + '</span><i style="--w:' + (100 * c[1] / S.acs).toFixed(1) + '%"></i><span>' + c[0] + '</span></div>';
  }).join('');
  document.getElementById('fCounts').innerHTML = L('<b>Even on the narrowest count, the voters left off outnumber the margin in {k} of the {n} seats.</b> In the other {o}, the runner-up could not have won even if every living person left off had voted, at the seat\'s turnout, for the runner-up. The lists cannot show how anyone left off would have voted.', { k: S.could_change, n: S.acs, o: S.acs - S.could_change });

  var sg = function (v) { return (v > 0 ? '+' : '') + SIR.d(v, 1); };
  SIR.table(document.getElementById('tWin'), [
    { k: 'party', label: L('Party that won'), left: true }, { k: 'seats', label: L('Seats') },
    { k: 'per_100', label: L('Left off per 100'), fmt: function (v) { return SIR.d(v, 1); } },
    { k: 'vs_district', label: L('Against own district'), fmt: sg },
    { k: 'over_margin', label: L('Left off over margin') }
  ], S.winners, { sort: 'seats' });
  var W = {}; S.winners.forEach(function (w) { W[w.party] = w; });
  var big = ['TVK', 'DMK', 'AIADMK'];
  VIZ.strip('vSwarm', { label: L('Names left off per 100 electors in every constituency, by the party that won it in 2026'), axis: L('Left off per 100 electors'), r: 4,
    key: [[L('Chennai'), '--fill-red'], [L('Rest of the state'), '--fill-navy']],
    rows: big.concat(['other']).map(function (w) {
      var pts = A.filter(function (a) { return w === 'other' ? big.indexOf(a.winner) < 0 : a.winner === w; });
      return { name: w === 'other' ? L('Other parties') : L('{p} ({n} seats)', { p: w, n: pts.length }), tok: '--fill-navy',
        points: pts.map(function (a) { return { v: a.per_100, tok: a.district === 'Chennai' ? '--fill-red' : null, label: L('{n} ({d}): {v} per 100', { n: a.name, d: a.district, v: SIR.d(a.per_100, 1) }) }; }) };
    }) });
  document.getElementById('fWin').innerHTML = L('<b>Seats won by TVK lost {t} of every 100 electors, against {d} in DMK seats and {a} in AIADMK seats.</b> Most of the gap is about where the seats are. Against their own districts, TVK seats come out at {tv}, DMK seats at {dv} and AIADMK seats at {av}. {c} of the {n} seats changed hands from 2021.', {
    t: SIR.d(W.TVK.per_100, 1), d: SIR.d(W.DMK.per_100, 1), a: SIR.d(W.AIADMK.per_100, 1), tv: sg(W.TVK.vs_district), dv: sg(W.DMK.vs_district), av: sg(W.AIADMK.vs_district), c: S.changed_hands, n: S.acs });

  SIR.table(document.getElementById('tAc'), [
    { k: 'ac', label: L('No.') }, { k: 'name', label: L('Constituency'), left: true }, { k: 'district', label: L('District'), left: true },
    { k: 'removed', label: L('Left off'), fmt: SIR.n }, { k: 'net_fall', label: L('Net fall'), fmt: SIR.n },
    { k: 'winner', label: L('Won 2026'), left: true }, { k: 'runner_up', label: L('Second'), left: true },
    { k: 'margin', label: L('Margin'), fmt: SIR.n }, { k: 'turnout', label: L('Turnout %'), fmt: function (v) { return SIR.d(v, 1); } },
    { k: 'winner_2021', label: L('Won 2021'), left: true }
  ], A, { sort: 'removed' });
  SIR.showFaq('tn', 'elections');
}).catch(SIR.fail);
