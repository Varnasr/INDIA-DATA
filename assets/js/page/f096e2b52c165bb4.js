Promise.all([SIR.json('data/kerala/summary.json'), SIR.json('data/kerala/constituencies.json')]).then(function (r) {
  var S = r[0], A = r[1], big = ['INC', 'CPI(M)', 'IUML'];
  var groups = [{ label: 'INC', tok: '--fill-teal' }, { label: 'CPI(M)', tok: '--fill-red' }, { label: 'IUML', tok: '--fill-navy' }].map(function (g) { g.test = function (a) { return a.winner === g.label; }; return g; })
    .concat([{ label: L('Other parties'), test: function (a) { return big.indexOf(a.winner) < 0; }, tok: '--fill-grey' }]);
  var maxX = Math.max.apply(null, A.map(function (a) { return a.fall_draft; }));
  SIR.chart('cScatter', { type: 'scatter', data: { datasets: groups.map(function (g) {
      return { label: g.label, data: A.filter(g.test).map(function (a) { return { x: a.fall_draft, y: a.margin, n: a.name, w: a.winner }; }), $token: g.tok, pointRadius: 3.5 };
    }).concat([{ type: 'line', label: L('Margin equals the fall in the roll'), data: [{ x: 0, y: 0 }, { x: maxX, y: maxX }], $token: '--fill-other', pointRadius: 0, borderDash: [5, 4], borderWidth: 1.5 }]) },
    options: { plugins: { tooltip: { callbacks: { label: function (c) { return c.raw.n ? L('{n} ({w}): roll fell by {x}, margin {y}', { n: c.raw.n, w: c.raw.w, x: SIR.n(c.raw.x), y: SIR.n(c.raw.y) }) : ''; } } } },
      scales: { x: { beginAtZero: true, title: { display: true, text: L('Fall in the roll, January 2025 to the draft') } }, y: { beginAtZero: true, title: { display: true, text: L('2026 winning margin, votes') } } } } });
  document.getElementById('fScatter').innerHTML = L('<b>In {k} of the {n} constituencies, the roll fell by more at the draft than the 2026 winning margin.</b> The fall and the margin as a share of votes are close to unrelated (rank correlation {rho}, where 0 means the two are unrelated and 1 means they rise in step).', { k: S.draft_over_margin, n: S.acs, rho: SIR.d(S.rho_rate_margin, 2) });

  var counts = [[L('Fall to the draft roll'), S.draft_over_margin], [L('Fall to the election roll'), S.over_margin], [L('Fall to the election roll, at turnout'), S.could_change]];
  document.getElementById('cCounts').innerHTML = counts.map(function (c) {
    return '<div class="big"><b>' + c[1] + '</b><span class="of">' + L('of {n} seats', { n: S.acs }) + '</span><i style="--w:' + (100 * c[1] / S.acs).toFixed(1) + '%"></i><span>' + c[0] + '</span></div>';
  }).join('');
  document.getElementById('fCounts').innerHTML = L('<b>By the election the roll had grown back by {back} since the draft, new voters included, and was still smaller than in January 2025 by more than the margin in {k} seats.</b> Counted at each seat\'s own turnout, that is {t} seats. Nobody can know how anyone missing from the roll would have voted.', { back: SIR.lakh(S.added_final + S.added_election), k: S.over_margin, t: S.could_change });

  var sg = function (v) { return (v > 0 ? '+' : '') + SIR.d(v, 1); };
  SIR.table(document.getElementById('tWin'), [
    { k: 'party', label: L('Party that won'), left: true }, { k: 'seats', label: L('Seats') },
    { k: 'draft_per_100', label: L('Fall per 100'), fmt: function (v) { return SIR.d(v, 1); } },
    { k: 'vs_district', label: L('Against own district'), fmt: sg },
    { k: 'over_margin', label: L('Fall over margin') }
  ], S.winners, { sort: 'seats' });
  var W = {}; S.winners.forEach(function (w) { W[w.party] = w; });
  VIZ.strip('vSwarm', { label: L('Fall in the roll at the draft per 100 electors in every constituency, by the party that won it in 2026'), axis: L('Fall per 100 electors on the January 2025 roll'), r: 4,
    key: [[L('Thiruvananthapuram'), '--fill-red'], [L('Rest of the state'), '--fill-navy']],
    rows: big.concat(['other']).map(function (w) {
      var pts = A.filter(function (a) { return w === 'other' ? big.indexOf(a.winner) < 0 : a.winner === w; });
      return { name: w === 'other' ? L('Other parties') : L('{p} ({n} seats)', { p: w, n: pts.length }), tok: '--fill-navy',
        points: pts.map(function (a) { return { v: a.draft_per_100, tok: a.district === 'Thiruvananthapuram' ? '--fill-red' : null, label: L('{n} ({d}): {v} per 100', { n: a.name, d: a.district, v: SIR.d(a.draft_per_100, 1) }) }; }) };
    }) });
  document.getElementById('fWin').innerHTML = L('<b>The INC won {i} seats, the CPI(M) {c} and the IUML {u}. The roll fell at the draft by {ip} per 100 in the INC\'s seats, {cp} in the CPI(M)\'s and {up} in the IUML\'s.</b> Set against their own districts they come out at {iv}, {cv} and {uv}, so most of the difference is about where the seats are.', {
    i: W.INC.seats, c: W['CPI(M)'].seats, u: W.IUML.seats, ip: SIR.d(W.INC.draft_per_100, 1), cp: SIR.d(W['CPI(M)'].draft_per_100, 1), up: SIR.d(W.IUML.draft_per_100, 1), iv: sg(W.INC.vs_district), cv: sg(W['CPI(M)'].vs_district), uv: sg(W.IUML.vs_district) });

  SIR.table(document.getElementById('tAc'), [
    { k: 'ac', label: L('No.') }, { k: 'name', label: L('Constituency'), left: true }, { k: 'district', label: L('District'), left: true },
    { k: 'fall_draft', label: L('Fall to draft'), fmt: SIR.n }, { k: 'fall', label: L('Fall to 2026'), fmt: SIR.n },
    { k: 'winner', label: L('Won 2026'), left: true }, { k: 'runner_up', label: L('Second'), left: true },
    { k: 'margin', label: L('Margin'), fmt: SIR.n }, { k: 'turnout', label: L('Turnout %'), fmt: function (v) { return SIR.d(v, 1); } }
  ], A, { sort: 'fall_draft' });
  SIR.showFaq('kl', 'elections');
}).catch(SIR.fail);
