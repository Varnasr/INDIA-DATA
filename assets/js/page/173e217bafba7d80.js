function tag(al) { return al ? '<span class="tag ' + al + '">' + al + '</span>' : ''; }
SIR.json('data/bihar/constituencies.json').then(function (acs) {
  acs.forEach(function (a) { a.border = a.border || 'Interior'; });
  var G = SIR.groupBy(acs, 'border');
  var order = Object.keys(G).sort(function (a, b) { return a === 'Interior' ? 1 : b === 'Interior' ? -1 : a.localeCompare(b); });
  var short = { 'Uttar Pradesh': 'UP', 'West Bengal': 'Bengal', 'Jharkhand': 'Jharkhand', 'Nepal': 'Nepal', 'Interior': L('Interior') };
  var lbl = function (k) { return k.split(';').map(function (x) { return short[x] || x; }).join(' + ') + ' (' + G[k].length + ')'; };
  var rate = function (rows) { return 100 * SIR.sum(rows, 'total') / SIR.sum(rows, 'electorate_2025'); };
  var tot = SIR.sum(acs, 'total'), el = SIR.sum(acs, 'electorate_2025');
  var border = acs.filter(function (a) { return a.border !== 'Interior'; }), interior = G.Interior;

  document.getElementById('kpis').innerHTML = [
    [border.length, L('constituencies on a border')],
    [SIR.d(rate(border), 2), L('left off or deleted per 100 electors, border')],
    [SIR.d(rate(interior), 2), L('left off or deleted per 100 electors, interior')],
    [SIR.pct(100 * SIR.sum(border, 'total') / tot), L('of all names left off or deleted were in border seats')]
  ].map(function (k) { return '<div><b>' + k[0] + '</b><span>' + k[1] + '</span></div>'; }).join('');

  SIR.chart('cRate', { type: 'bar', data: { labels: order.map(lbl), datasets: [{ label: L('Per 100 electors'), data: order.map(function (k) { return rate(G[k]); }),
      $tokens: order.map(function (k) { return k === 'Interior' ? '--fill-grey' : '--fill-navy'; }) }] },
    options: { indexAxis: 'y', plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true, title: { display: true, text: L('Left off or deleted per 100 electors') } } } } });

  SIR.chart('cShare', { type: 'bar', data: { labels: order.map(lbl), datasets: [
      { label: L('% of names left off or deleted'), data: order.map(function (k) { return 100 * SIR.sum(G[k], 'total') / tot; }), $token: '--fill-red' },
      { label: L('% of electorate'), data: order.map(function (k) { return 100 * SIR.sum(G[k], 'electorate_2025') / el; }), $token: '--fill-grey' }] },
    options: { indexAxis: 'y', scales: { x: { beginAtZero: true, title: { display: true, text: L('% of Bihar') } } } } });

  var rel = function (rows, hi) { var h = SIR.sum(rows, 'hindu'), m = SIR.sum(rows, 'muslim'), u = SIR.sum(rows, 'unknown'); return 100 * (m + (hi ? u : 0)) / (h + m + u); };
  SIR.chart('cWho', { type: 'bar', data: { labels: order.map(lbl), datasets: [
      { label: L('Women %'), data: order.map(function (k) { return 100 * SIR.sum(G[k], 't_f') / (SIR.sum(G[k], 't_f') + SIR.sum(G[k], 't_m')); }), $token: '--female' },
      { label: L('Muslim names, low %'), data: order.map(function (k) { return rel(G[k], false); }), $token: '--fill-india' },
      { label: L('Muslim names, high %'), data: order.map(function (k) { return rel(G[k], true); }), $token: '--fill-other' }] },
    options: { indexAxis: 'y', scales: { x: { beginAtZero: true, max: 100, title: { display: true, text: L('% of the names counted') } } } } });

  SIR.chart('cPhase', { type: 'bar', data: { labels: order.map(lbl), datasets: [{ label: L('Phase 2 as % of phase 1'), data: order.map(function (k) { return 100 * SIR.sum(G[k], 'p2') / SIR.sum(G[k], 'p1'); }), $token: '--fill-amber' }] },
    options: { indexAxis: 'y', plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true, title: { display: true, text: L('Phase 2 / phase 1, %') } } } } });

  SIR.table(document.getElementById('tbl'), [
    { k: 'name', label: L('Constituency'), left: true, fmt: function (v, r) { return SIR.esc(r.ac + ' ' + v); } }, { k: 'district', label: L('District'), left: true },
    { k: 'border', label: L('Border'), left: true, fmt: function (v) { return SIR.esc(v.replace(/;/g, ', ')); } },
    { k: 'total', label: L('Left off or deleted'), fmt: SIR.n }, { k: 'per_100', label: L('Per 100'), fmt: function (v) { return SIR.d(v, 2); } },
    { k: 'muslim_lo', label: L('Muslim names %'), fmt: function (v, r) { return L('{lo} to {hi}', { lo: SIR.d(v, 0), hi: SIR.d(r.muslim_hi, 0) }); } },
    { k: 'al2025', label: L('2025 winner'), left: true, fmt: function (v, r) { return tag(v) + ' ' + SIR.esc(r.win2025); } }
  ], border.map(function (a) { var c = a.hindu + a.muslim + a.unknown; a.muslim_lo = 100 * a.muslim / c; a.muslim_hi = 100 * (a.muslim + a.unknown) / c; return a; }), { sort: 'per_100' });
}).catch(SIR.fail);
