Promise.all([SIR.json('data/india/states.json'), SIR.json('data/bihar/summary.json'), SIR.json('data/hyderabad/summary.json'), SIR.json('data/tamilnadu/summary.json'), SIR.json('data/karnataka/summary.json'), SIR.json('data/westbengal/summary.json'), SIR.json('data/kerala/summary.json'), SIR.json('data/rajasthan/summary.json'), SIR.json('data/uttarpradesh/summary.json'), SIR.json('data/delhi/summary.json'), SIR.json('data/maharashtra/summary.json'), SIR.json('data/gujarat/summary.json'), SIR.json('data/uttarakhand/summary.json'), SIR.json('data/india/cities.json'), SIR.json('data/india/disputes_counts.json'), SIR.json('data/india/ac_finder.json'), SIR.json('data/india/women.json'), SIR.json('data/india/rti.json')]).then(function (r) {
  var T = r[0].total, B = r[1].totals, H = r[2].totals;
  var cr = function (x) { return L('{x} crore', { x: (x / 1e7).toFixed(2) }); };
  // the share as "one in every k", rounded to the nearest whole elector, so
  // the headline says how many of the roll that count was
  document.getElementById('headline').innerHTML = L('{r} names were <em>left off</em> India\'s draft rolls, one in every {k} electors.', { r: cr(T.removed), k: Math.round(100 / T.per_100) });
  document.getElementById('lede').innerHTML = L('The Election Commission revised the electoral rolls of {s} states and union territories house by house. The counts below show whose names were left off, where, and the reason written against each name.', { s: T.states });
  document.getElementById('hIndia').innerHTML = L('{r} names left off the draft rolls in {s} states and union territories, and the reasons each one recorded.', { r: cr(T.removed), s: T.states });
  document.getElementById('hBihar').innerHTML = L('{n} names left off or deleted across {acs} constituencies and {booths} booths, set against the 2025 election result.', { n: SIR.lakh(B.total), acs: B.acs, booths: SIR.n(B.booths) });
  document.getElementById('hHyd').innerHTML = L('{d} of {e} electors left off the draft in {k} constituencies, counted elector by elector.', { d: SIR.n(H.deleted), e: SIR.n(H.electors), k: r[2].acs.length });
  document.getElementById('hTn').innerHTML = L('{n} names left off the draft roll in {acs} constituencies, {p} of every 100 electors, set against the 2026 election result.', { n: SIR.lakh(r[3].removed), acs: r[3].acs, p: SIR.d(r[3].per_100, 1) });
  document.getElementById('hKa').innerHTML = L('{n} names left off the draft roll in {d} districts, {p} of every 100 electors, and {b} in Bengaluru alone.', { n: SIR.lakh(r[4].removed), d: r[4].districts, p: SIR.d(r[4].per_100, 1), b: SIR.lakh(r[4].bengaluru.removed) });
  document.getElementById('hWb').innerHTML = L('{n} names left off the draft roll and {a} held back for adjudication, and in {k} of {acs} constituencies the roll fell by more than the 2026 margin.', { n: SIR.lakh(r[5].pn05.removed), a: SIR.lakh(r[5].pn05.adjudication), k: r[5].over_margin, acs: r[5].acs });
  document.getElementById('hKl').innerHTML = L('Kerala published no count of the names left off by constituency. The draft roll was {f} smaller than in January 2025, and women were {w} of that fall.', { f: SIR.lakh(r[6].fall_draft), w: SIR.pct(r[6].women_fall_pct) });
  // every card leads with a count of names, and beneath it that count as a
  // share of the roll it came off. Each pair comes from one source, so the
  // two always describe the same thing. Kerala published no count of names
  // left off by constituency, so its card carries the fall in the roll and
  // says so. Bihar's card counts both phases, so its share says which roll.
  var byState = {}; r[0].states.forEach(function (x) { byState[x.state] = x; });
  var cnt = function (v) { return v >= 1e5 ? SIR.lakh(v) : SIR.n(v); };
  var N = {}, from = function (href, st) { var x = byState[st]; if (x && x.removed) N[href] = [cnt(x.removed), x.per_100]; };
  N['india/'] = [cr(T.removed), T.per_100];
  N['bihar/'] = [SIR.lakh(B.total), 100 * B.total / B.electorate_2025, L('{p} of the 2025 roll, both phases', { p: SIR.pct(100 * B.total / B.electorate_2025) })];
  N['hyderabad/'] = [SIR.lakh(H.deleted), 100 * H.deleted / H.electors];
  N['kerala/'] = [SIR.lakh(r[6].fall_draft), r[6].draft_per_100];
  [['tamilnadu/', 'Tamil Nadu'], ['karnataka/', 'Karnataka'], ['westbengal/', 'West Bengal'], ['rajasthan/', 'Rajasthan'], ['uttarpradesh/', 'Uttar Pradesh'],
    ['delhi/', 'Delhi'], ['maharashtra/', 'Maharashtra'], ['gujarat/', 'Gujarat'], ['uttarakhand/', 'Uttarakhand']].forEach(function (p) { from(p[0], p[1]); });
  // the states on the shared page take their figures from the All India table
  document.querySelectorAll('.hubs a.hub[data-st]').forEach(function (a) {
    var x = byState[a.getAttribute('data-st')];
    if (!x || !x.removed) return;
    from(a.getAttribute('href'), a.getAttribute('data-st'));
    var n = cnt(x.removed);
    a.querySelector('span').innerHTML = L('{n} names left off the draft roll, {p} of every 100 electors on the roll before the revision.', { n: n, p: SIR.d(x.per_100, 1) });
  });
  // the pinned cards lead with their own number, which is not a share of a roll
  N['india/cities/'] = [SIR.d(r[13].summary.times_max, 1) + '×'];
  N['india/women/'] = [r[16].summary.over + ' / ' + r[16].summary.states];
  N['india/disputes/'] = [SIR.n(r[14].counts.items)];
  N['india/rti/'] = [SIR.n(r[17].counts.items)];
  N['india/constituencies/'] = [SIR.n(r[15].rows.length)];
  document.getElementById('hWomen').innerHTML = L('Women were the larger share of the names left off in {o} of {n} states with a count by sex, and in {d} of {dn} districts.', { o: r[16].summary.over, n: r[16].summary.states, d: r[16].summary.district_over, dn: r[16].summary.district_n });
  document.getElementById('hDisp').innerHTML = L('{n} court orders, resolutions, protests and reports from {s} states and union territories, each with its source and the Commission\'s reply where one was reported.', { n: SIR.n(r[14].counts.items), s: r[14].counts.states });
  document.getElementById('hAcs').innerHTML = L('{n} constituencies in {p} places, each with its count in its own state\'s measure and a link to its page.', { n: SIR.n(r[15].rows.length), p: r[15].places.length });
  document.getElementById('hCities').innerHTML = L('In {a} of {n} large cities the city lost a larger share of its roll than its state, up to {x} times the state\'s rate.', { a: r[13].summary.above_state, n: r[13].summary.compared, x: SIR.d(r[13].summary.times_max, 1) });
  document.querySelectorAll('.hubs a.hub').forEach(function (a) {
    var v = N[a.getAttribute('href')]; if (!v) return;
    a.insertAdjacentHTML('afterbegin', '<em class="n">' + v[0] + (v[1] != null ? '<small>' + (v[2] || L('{p} of the roll', { p: SIR.pct(v[1]) })) + '</small>' : '') + '</em>');
  });
}).catch(SIR.fail);
