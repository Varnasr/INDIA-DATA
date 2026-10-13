Promise.all([SIR.json('data/westbengal/summary.json'), SIR.json('data/westbengal/constituencies.json')]).then(function (r) {
  var S = r[0], A = r[1];
  var groups = [{ label: 'BJP', test: function (a) { return a.winner === 'BJP'; }, tok: '--fill-amber' },
    { label: 'AITC', test: function (a) { return a.winner === 'AITC'; }, tok: '--fill-teal' },
    { label: L('Other parties'), test: function (a) { return ['BJP', 'AITC'].indexOf(a.winner) < 0; }, tok: '--fill-grey' }];
  var maxX = Math.max.apply(null, A.map(function (a) { return a.fall; }));
  SIR.chart('cScatter', { type: 'scatter', data: { datasets: groups.map(function (g) {
      return { label: g.label, data: A.filter(g.test).map(function (a) { return { x: a.fall, y: a.margin, n: a.name, w: a.winner }; }), $token: g.tok, pointRadius: 3.5 };
    }).concat([{ type: 'line', label: L('Margin equals the fall in the roll'), data: [{ x: 0, y: 0 }, { x: maxX, y: maxX }], $token: '--fill-other', pointRadius: 0, borderDash: [5, 4], borderWidth: 1.5 }]) },
    options: { plugins: { tooltip: { callbacks: { label: function (c) { return c.raw.n ? L('{n} ({w}): roll fell by {x}, margin {y}', { n: c.raw.n, w: c.raw.w, x: SIR.n(c.raw.x), y: SIR.n(c.raw.y) }) : ''; } } } },
      scales: { x: { beginAtZero: true, title: { display: true, text: L('Fall in the roll, 2024 to 2026') } }, y: { beginAtZero: true, title: { display: true, text: L('2026 winning margin, votes') } } } } });
  document.getElementById('fScatter').innerHTML = L('<b>In {k} of the {n} constituencies, the roll fell by more than the 2026 winning margin.</b> The fall and the margin as a share of votes are close to unrelated (rank correlation {rho}, where 0 means the two are unrelated and 1 means they rise in step), so the seats whose rolls shrank most were not the closest contests.', { k: S.over_margin, n: S.acs, rho: SIR.d(S.rho_rate_margin, 2) });

  var counts = [[L('Fall to the draft roll'), S.draft_over_margin], [L('Fall to the election roll'), S.over_margin], [L('Fall to the election roll, at turnout'), S.could_change]];
  document.getElementById('cCounts').innerHTML = counts.map(function (c) {
    return '<div class="big"><b>' + c[1] + '</b><span class="of">' + L('of {n} seats', { n: S.acs }) + '</span><i style="--w:' + (100 * c[1] / S.acs).toFixed(1) + '%"></i><span>' + c[0] + '</span></div>';
  }).join('');
  document.getElementById('fCounts').innerHTML = L('<b>Counting the fall at each seat\'s own turnout, it still exceeds the margin in {k} of the {n} seats.</b> In the other {o}, the runner-up could not have won even if every elector missing from the roll had voted, at the seat\'s turnout, for the runner-up. The fall counts the dead and ordinary changes to the roll too, and nobody can know how anyone missing from it would have voted.', { k: S.could_change, n: S.acs, o: S.acs - S.could_change });

  var sg = function (v) { return (v > 0 ? '+' : '') + SIR.d(v, 1); };
  SIR.table(document.getElementById('tWin'), [
    { k: 'party', label: L('Party that won'), left: true }, { k: 'seats', label: L('Seats') },
    { k: 'per_100', label: L('Fall per 100'), fmt: function (v) { return SIR.d(v, 1); } },
    { k: 'vs_district', label: L('Against own district'), fmt: sg },
    { k: 'over_margin', label: L('Fall over margin') }
  ], S.winners, { sort: 'seats' });
  var W = {}; S.winners.forEach(function (w) { W[w.party] = w; });
  VIZ.strip('vSwarm', { label: L('Fall in the roll per 100 electors in every constituency, by the party that won it in 2026'), axis: L('Fall per 100 electors on the 2024 roll'), r: 3.5,
    key: [[L('Kolkata'), '--fill-red'], [L('Rest of the state'), '--fill-navy']],
    rows: ['BJP', 'AITC', 'other'].map(function (w) {
      var pts = A.filter(function (a) { return w === 'other' ? ['BJP', 'AITC'].indexOf(a.winner) < 0 : a.winner === w; });
      return { name: w === 'other' ? L('Other parties') : L('{p} ({n} seats)', { p: w, n: pts.length }), tok: '--fill-navy',
        points: pts.map(function (a) { return { v: Math.max(a.per_100, 0), tok: /^Kolkata/.test(a.district) ? '--fill-red' : null, label: L('{n} ({d}): {v} per 100', { n: a.name, d: a.district, v: SIR.d(a.per_100, 1) }) }; }) };
    }) });
  document.getElementById('fWin').innerHTML = L('<b>The BJP won {b} seats and the AITC {t}. The roll fell by {bp} per 100 in the seats the BJP won and by {tp} in those the AITC won.</b> Set against their own districts, the two come out at {bv} and {tv}, so the difference is about where the seats are. The fall exceeded the margin in {bo} of the BJP\'s seats and {to} of the AITC\'s.', {
    b: W.BJP.seats, t: W.AITC.seats, bp: SIR.d(W.BJP.per_100, 1), tp: SIR.d(W.AITC.per_100, 1), bv: sg(W.BJP.vs_district), tv: sg(W.AITC.vs_district), bo: W.BJP.over_margin, to: W.AITC.over_margin });

  SIR.table(document.getElementById('tAc'), [
    { k: 'ac', label: L('No.') }, { k: 'name', label: L('Constituency'), left: true }, { k: 'district', label: L('District'), left: true },
    { k: 'fall', label: L('Fall'), fmt: SIR.n }, { k: 'per_100', label: L('Fall per 100'), fmt: function (v) { return SIR.d(v, 1); } },
    { k: 'winner', label: L('Won 2026'), left: true }, { k: 'runner_up', label: L('Second'), left: true },
    { k: 'margin', label: L('Margin'), fmt: SIR.n }, { k: 'turnout', label: L('Turnout %'), fmt: function (v) { return SIR.d(v, 1); } }
  ], A, { sort: 'fall' });
  SIR.showFaq('wb', 'elections');
}).catch(SIR.fail);
