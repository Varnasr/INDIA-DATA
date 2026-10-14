SIR.json('data/hyderabad/summary.json').then(function (s) {
  var A = s.acs, names = A.map(function (a) { return a.name; }), pal = ['--fill-red', '--fill-navy', '--fill-amber', '--fill-india', '--fill-other'];
  SIR.chart('cAge', { type: 'line', data: { labels: s.bands, datasets: A.map(function (a, i) { return { label: a.name, data: a.age_rate, $token: pal[i], tension: 0.2, pointRadius: 3 }; }) },
    options: { scales: { y: { beginAtZero: true, title: { display: true, text: L('% left off') } }, x: { title: { display: true, text: L('Age band') } } } } });
  var lo = A.map(function (a) { return a.age_rate[0]; }), hi = A.map(function (a) { return a.age_rate[7]; });
  document.getElementById('fAge').innerHTML = L('<b>In every constituency, the older the elector, the likelier the exclusion.</b> Between {hi_min} and {hi_max} of electors aged 80 and over were left off the draft, and {lo_min} to {lo_max} of those aged 18 to 24. Death explains part of the exclusions at the oldest ages. The recorded reasons are on the <a href="../">overview</a>.', { hi_min: SIR.pct(Math.min.apply(null, hi)), hi_max: SIR.pct(Math.max.apply(null, hi)), lo_min: SIR.pct(Math.min.apply(null, lo)), lo_max: SIR.pct(Math.max.apply(null, lo)) });

  SIR.chart('cRel', { type: 'bar', data: { labels: names, datasets: [
      { label: L('Hindu names'), data: A.map(function (a) { return a.hindu_rate; }), $token: '--fill-amber' },
      { label: L('Muslim names'), data: A.map(function (a) { return a.muslim_rate; }), $token: '--fill-india' }] },
    options: { scales: { y: { beginAtZero: true, title: { display: true, text: L('% left off') } } } } });
  SIR.chart('cRelW', { type: 'bar', data: { labels: names, datasets: [{ label: L('Hindu minus Muslim, within parts'), data: A.map(function (a) { return a.within_part.hindu_minus_muslim.diff_pp; }), $token: '--fill-navy' }] },
    options: { plugins: { legend: { display: false }, tooltip: { callbacks: { afterLabel: function (c) { var w = A[c.dataIndex].within_part.hindu_minus_muslim; return L('{higher} of {parts} parts: Hindu-name rate higher', { higher: w.a_higher, parts: w.parts }); } } } }, scales: { y: { beginAtZero: true, title: { display: true, text: L('Percentage points') } } } } });
  var W = A.map(function (a) { return a.within_part.hindu_minus_muslim; });
  var c = function (k) { return 100 * SIR.sum(A, function (a) { return a.counts[k]; }); };
  document.getElementById('fRel').innerHTML = L('<b>Across the five constituencies, {hindu} of Hindu-name electors were left off the draft and {muslim} of Muslim-name electors.</b> Inside the same polling part the gap is {gap_min} to {gap_max} points, and it runs the same way in {higher} of the {parts} parts large enough to compare.', { hindu: SIR.pct(c('hin_asd') / SIR.sum(A, function (a) { return a.counts.hin_all; })), muslim: SIR.pct(c('mus_asd') / SIR.sum(A, function (a) { return a.counts.mus_all; })), gap_min: SIR.d(Math.min.apply(null, W.map(function (w) { return w.diff_pp; })), 1), gap_max: SIR.d(Math.max.apply(null, W.map(function (w) { return w.diff_pp; })), 1), higher: SIR.sum(W, 'a_higher'), parts: SIR.sum(W, 'parts') });

  var LK = A.filter(function (a) { return a.linked; });
  SIR.chart('cLink', { type: 'bar', data: { labels: LK.map(function (a) { return a.name; }), datasets: [
      { label: L('Linked to 2002'), data: LK.map(function (a) { return a.linked_rate; }), $token: '--fill-navy' },
      { label: L('No 2002 link'), data: LK.map(function (a) { return a.unlinked_rate; }), $token: '--fill-red' }] },
    options: { scales: { y: { beginAtZero: true, title: { display: true, text: L('% left off') } } } } });
  SIR.chart('cLinkShare', { type: 'bar', data: { labels: LK.map(function (a) { return a.name; }), datasets: [{ label: L('% of roll linked'), data: LK.map(function (a) { return a.linked_share_roll; }), $token: '--fill-navy' }] },
    options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, max: 100, title: { display: true, text: L('% of roll') } } } } });
  document.getElementById('fLink').innerHTML = L('<b>Electors with no link to the 2002 roll were about twice as likely to be left off the draft.</b> Inside the same polling part, unlinked electors were left off the draft {gaps}. The 2002 link is the revision\'s own test, so the gap shows how much the process relied on it.', { gaps: LK.map(function (a) { return L('{points} points more often in {name}', { points: SIR.d(a.within_part.unlinked_minus_linked.diff_pp, 0), name: a.name }); }).join(', ') });

  SIR.chart('cSex', { type: 'bar', data: { labels: names, datasets: [
      { label: L('Women'), data: A.map(function (a) { return a.female_rate; }), $token: '--female' },
      { label: L('Men'), data: A.map(function (a) { return a.male_rate; }), $token: '--male' }] },
    options: { scales: { y: { beginAtZero: true, title: { display: true, text: L('% left off') } } } } });
  SIR.table(document.getElementById('tSex'), [{ k: 'name', label: L('Constituency'), left: true }, { k: 'd', label: L('Women minus men (points)'), fmt: function (v) { return SIR.d(v, 1); } }, { k: 'w', label: L('Parts: women higher') }, { k: 'm', label: L('Parts: men higher') }],
    A.map(function (a) { var w = a.within_part.female_minus_male; return { name: a.name, d: w.diff_pp, w: w.a_higher, m: w.b_higher }; }), { sort: 'name', dir: 1 });
  document.getElementById('fSex').innerHTML = L('<b>Women and men were left off the draft at similar rates.</b> Men were left off the draft slightly more often in Charminar, Yakutpura and Malakpet, and women in Chandrayangutta and Bahadurpura. Inside the same part the gaps are under two and a half points.');
}).catch(SIR.fail);
