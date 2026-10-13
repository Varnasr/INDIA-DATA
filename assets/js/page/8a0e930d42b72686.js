Promise.all([SIR.json('data/hyderabad/summary.json'), SIR.json('data/hyderabad/parts.json')]).then(function (r) {
  var s = r[0], F = r[1].fields, rows = r[1].rows.map(function (x) { var o = {}; F.forEach(function (f, i) { o[f] = x[i]; }); return o; });
  var A = s.acs, pal = { Charminar: '--fill-red', Yakutpura: '--fill-navy', Malakpet: '--fill-amber', Chandrayangutta: '--fill-india', Bahadurpura: '--fill-other' };
  var bins = []; for (var b = 0; b < 90; b += 5) bins.push(b);
  SIR.chart('cHist', { type: 'bar', data: { labels: bins.map(function (b) { return b + '–' + (b + 5); }), datasets: A.map(function (a) {
      return { label: a.name, data: bins.map(function (b) { return rows.filter(function (p) { return p.ac === a.name && p.rate >= b && p.rate < b + 5; }).length; }), $token: pal[a.name] }; }) },
    options: { scales: { x: { stacked: true, title: { display: true, text: L('% of part struck off') } }, y: { stacked: true, title: { display: true, text: L('Parts') } } } } });
  SIR.table(document.getElementById('tQ'), [{ k: 'name', label: L('Constituency'), left: true }, { k: 'q0', label: L('Low') }, { k: 'q1', label: L('Q1') }, { k: 'q2', label: L('Median') }, { k: 'q3', label: L('Q3') }, { k: 'q4', label: L('High') }, { k: 'o', label: L('Parts over 60%') }],
    A.map(function (a) { var q = a.part_rate_quartiles; return { name: a.name, q0: q[0], q1: q[1], q2: q[2], q3: q[3], q4: q[4], o: a.parts_over_60 }; }), { sort: 'name', dir: 1 });
  SIR.chart('cMus', { type: 'scatter', data: { datasets: A.map(function (a) {
      return { label: a.name, data: rows.filter(function (p) { return p.ac === a.name; }).map(function (p) { return { x: p.muslim_share_roll, y: p.rate, n: a.name + ' ' + (p.locality || L('part {part}', { part: p.part })) }; }), $token: pal[a.name], pointRadius: 2 }; }) },
    options: { plugins: { tooltip: { callbacks: { label: function (c) { return L('{name}: {muslim}% Muslim names, {rate}% struck off', { name: c.raw.n, muslim: SIR.d(c.raw.x, 0), rate: SIR.d(c.raw.y, 1) }); } } } },
      scales: { x: { min: 0, max: 100, title: { display: true, text: L('Muslim-name share of part roll (%)') } }, y: { beginAtZero: true, title: { display: true, text: L('% struck off') } } } } });
  SIR.table(document.getElementById('tCorr'), [{ k: 'name', label: L('Constituency'), left: true }, { k: 'm', label: L('Muslim share'), fmt: function (v) { return SIR.d(v, 2); } }, { k: 'o', label: L('Aged 80+ share'), fmt: function (v) { return SIR.d(v, 2); } }, { k: 'u', label: L('Untraceable share'), fmt: function (v) { return SIR.d(v, 2); } }],
    A.map(function (a) { var c = a.part_correlations; return { name: a.name, m: c.muslim_share_vs_rate, o: c.aged80_share_vs_rate, u: c.untraceable_share_vs_rate }; }), { sort: 'name', dir: 1 });
  var ms = A.map(function (a) { return a.part_correlations.muslim_share_vs_rate; });
  document.getElementById('fParts').innerHTML = L('<b>Part rates run from {low}% to {high}%, and {over} parts lost more than 60% of their roll</b>, {where}. In every constituency, parts with a larger Muslim-name share of the roll had lower removal rates (rank correlations {r_from} to {r_to}). The share of elderly electors and the share entered as untraceable hardly move with the rate.', { low: SIR.d(Math.min.apply(null, A.map(function (a) { return a.part_rate_quartiles[0]; })), 0), high: SIR.d(Math.max.apply(null, A.map(function (a) { return a.part_rate_quartiles[4]; })), 0), over: SIR.sum(A, 'parts_over_60'), where: A.filter(function (a) { return a.parts_over_60; }).map(function (a) { return L('{n} in {name}', { n: a.parts_over_60, name: a.name }); }).join(L(' and ')), r_from: SIR.d(Math.max.apply(null, ms), 2), r_to: SIR.d(Math.min.apply(null, ms), 2) });

  var med = {}; A.forEach(function (a) { med[a.name] = a.part_rate_quartiles[2]; });
  var sel = document.getElementById('fac'); sel.innerHTML += A.map(function (a) { return '<option>' + a.name + '</option>'; }).join('');
  function draw() {
    var ac = sel.value, R = rows.filter(function (p) { return !ac || p.ac === ac; }).map(function (p) { p.dev = p.rate - med[p.ac]; p.adev = Math.abs(p.dev); return p; });
    SIR.table(document.getElementById('tOut'), [{ k: 'ac', label: L('Constituency'), left: true }, { k: 'part', label: L('Part') }, { k: 'locality', label: L('Locality'), left: true },
      { k: 'electors', label: L('Electors'), fmt: SIR.n }, { k: 'rate', label: L('% struck off'), fmt: function (v) { return SIR.d(v, 1); } }, { k: 'dev', label: L('Points from median'), fmt: function (v) { return (v > 0 ? '+' : '') + SIR.d(v, 1); } },
      { k: 'muslim_share_roll', label: L('Muslim names %'), fmt: function (v) { return SIR.d(v, 0); } }, { k: 'untraceable_share_of_deleted', label: L('Untraceable % of deleted'), fmt: function (v) { return SIR.d(v, 0); } }, { k: 'adev', label: L('Distance'), fmt: function (v) { return SIR.d(v, 1); } }], R, { sort: 'adev', limit: 40 });
  }
  sel.addEventListener('change', draw); draw();
}).catch(SIR.fail);
