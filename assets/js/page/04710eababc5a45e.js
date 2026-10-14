SIR.json('data/bihar/districts.json').then(function (ds) {
  var col = function (b) { return /Nepal/.test(b) ? '--fill-navy' : /Bengal/.test(b) ? '--fill-other' : /Jharkhand/.test(b) ? '--fill-amber' : /Uttar/.test(b) ? '--fill-india' : '--fill-grey'; };
  var ranked = ds.slice().sort(function (a, b) { return b.per_100 - a.per_100; });
  SIR.chart('cRank', { type: 'bar', data: { labels: ranked.map(function (d) { return d.district; }), datasets: [{ label: L('Per 100 electors'), data: ranked.map(function (d) { return d.per_100; }), $tokens: ranked.map(function (d) { return col(d.border); }) }] },
    options: { indexAxis: 'y', plugins: { legend: { display: false }, tooltip: { callbacks: { afterLabel: function (c) { var bd = ranked[c.dataIndex].border; return L('Border: {b}', { b: bd === 'Interior' ? L('Interior') : bd.replace(/;/g, ', ') }); } } } }, scales: { y: { ticks: { autoSkip: false } }, x: { beginAtZero: true, title: { display: true, text: L('Left off or deleted per 100 electors') } } } } });

  var F = [
    ['gddp_pc', L('Income per head, 2022-23 (₹ at 2011-12 prices)'), L('Does income relate to the names left off or deleted?')],
    ['urban_pct', L('Urban population, 2011 (%)'), L('Does urbanisation matter?')],
    ['women_literate', L('Women aged 15 to 49 who are literate, 2019-20 (%)'), L('Does women\'s literacy relate to the names left off or deleted?')],
    ['child_marriage', L('Women aged 20 to 24 married before 18, 2019-20 (%)'), L('Does early marriage relate to the names left off or deleted?')],
    ['density', L('Density, 2011 (per sq km)'), L('Does density matter?')],
    ['electors_per_booth', L('Electors per booth, 2025'), L('Does booth size relate to the names left off or deleted?')]
  ];
  var y = ds.map(function (d) { return d.per_100; }), rows = [];
  document.getElementById('scatters').innerHTML = F.map(function (f, i) { return '<div class="panel"><h3>' + f[2] + '</h3><p id="p' + i + '"></p><div class="chart"><canvas id="s' + i + '" aria-label="' + L('{f} against names left off or deleted per 100 electors', { f: f[1] }) + '"></canvas></div></div>'; }).join('');
  F.forEach(function (f, i) {
    var x = ds.map(function (d) { return d[f[0]]; }), r = SIR.corr(x, y), rho = SIR.spearman(x, y);
    rows.push({ f: f[1], r: r, rho: rho });
    document.getElementById('p' + i).textContent = L('r = {r}, ρ = {rho}.', { r: SIR.d(r, 2), rho: SIR.d(rho, 2) }) + ' ' + (Math.abs(rho) < 0.2 ? L('No clear relationship.') : (rho > 0 ? L('Higher values go with more names left off or deleted.') : L('Higher values go with fewer names left off or deleted.')));
    SIR.chart('s' + i, { type: 'scatter', data: { datasets: [{ label: L('District'), data: ds.map(function (d) { return { x: d[f[0]], y: d.per_100, n: d.district }; }), $token: '--fill-navy', pointRadius: 4 }] },
      options: { plugins: { legend: { display: false }, tooltip: { callbacks: { label: function (c) { return L('{n}: {x}, {y} per 100', { n: c.raw.n, x: SIR.n(c.raw.x), y: c.raw.y }); } } } },
        scales: { x: { title: { display: true, text: f[1] } }, y: { title: { display: true, text: L('Left off or deleted per 100 electors') } } } } });
  });
  SIR.table(document.getElementById('tCorr'), [{ k: 'f', label: L('Characteristic'), left: true }, { k: 'r', label: L('Linear r').replace(/r$/, '<span class="sym">r</span>'), fmt: function (v) { return SIR.d(v, 2); } }, { k: 'rho', label: L('Rank ρ').replace('ρ', '<span class="sym">ρ</span>'), fmt: function (v) { return SIR.d(v, 2); } }], rows, { sort: 'rho' });
  SIR.table(document.getElementById('tbl'), [
    { k: 'district', label: L('District'), left: true }, { k: 'acs', label: L('Seats') }, { k: 'deleted', label: L('Left off or deleted'), fmt: SIR.n },
    { k: 'per_100', label: L('Per 100'), fmt: function (v) { return SIR.d(v, 2); } }, { k: 'per_booth', label: L('Per booth'), fmt: function (v) { return SIR.d(v); } },
    { k: 'gddp_pc', label: L('Income per head (₹)'), fmt: SIR.n }, { k: 'urban_pct', label: L('Urban %'), fmt: function (v) { return SIR.d(v); } },
    { k: 'women_literate', label: L('Women literate %'), fmt: function (v) { return SIR.d(v); } }, { k: 'border', label: L('Border'), left: true, fmt: function (v) { return v === 'Interior' ? L('Interior') : SIR.esc(v.replace(/;/g, ', ')); } }
  ], ds, { sort: 'per_100' });
}).catch(SIR.fail);
