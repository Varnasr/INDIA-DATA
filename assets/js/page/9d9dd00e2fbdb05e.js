  // one state is featured each day, in the large card, and the other states
  // follow in alphabetical order, so a reader can find a state in the same
  // place every day. Only a state with an analysis of its own is featured,
  // so the large card always carries a figure.
  (function () {
    var box = document.querySelector('.hubs.states'), st = [].slice.call(box.querySelectorAll('a.hub.st'));
    // the featured state changes every day, by a shuffle seeded by the day, so every visitor
    // sees the same order on the same day
    var seed = SIR.day() >>> 0, rnd = function () { seed = (seed + 0x6D2B79F5) >>> 0; var t = seed; t = Math.imul(t ^ t >>> 15, t | 1); t ^= t + Math.imul(t ^ t >>> 7, t | 61); return ((t ^ t >>> 14) >>> 0) / 4294967296; };
    var order = st.slice();
    for (var i = order.length - 1; i > 0; i--) { var j = Math.floor(rnd() * (i + 1)), t = order[i]; order[i] = order[j]; order[j] = t; }
    var big = order.filter(function (a) { return !a.hasAttribute('data-st'); })[0];
    order.splice(order.indexOf(big), 1);
    big.classList.add('big');
    box.appendChild(big);
    order.sort(function (a, b) { return a.querySelector('b').textContent.localeCompare(b.querySelector('b').textContent); });
    order.forEach(function (a) { box.appendChild(a); });
  })();
// The all-India map: names left off per 100 electors, from data/india/states.json
Promise.all([SIR.json('data/india/states.json'), SIR.json('data/geo/india.json'), SIR.json('data/india/women.json'), SIR.json('data/india/cities.json'), SIR.json('data/india/margins.json'), SIR.json('data/india/notices.json'), SIR.json('data/bihar/tests.json')]).then(function (r) {
  var I = r[0], geo = r[1], W = r[2].summary, C = r[3].summary, M = r[4], NT = r[5], BT = r[6], byName = {}, byId = {};
  var ALIAS = { 'Andaman & Nicobar': 'Andaman and Nicobar Islands', 'Jammu & Kashmir': 'Jammu and Kashmir' };
  var PAGE = { 'Bihar': 'bihar/', 'Tamil Nadu': 'tamilnadu/', 'Karnataka': 'karnataka/', 'West Bengal': 'westbengal/', 'Kerala': 'kerala/', 'Rajasthan': 'rajasthan/', 'Uttar Pradesh': 'uttarpradesh/', 'Delhi': 'delhi/', 'Maharashtra': 'maharashtra/', 'Gujarat': 'gujarat/', 'Uttarakhand': 'uttarakhand/', 'Telangana': 'hyderabad/telangana/', 'Assam': 'assam/', 'Madhya Pradesh': 'madhyapradesh/', 'Chhattisgarh': 'chhattisgarh/', 'Puducherry': 'puducherry/', 'Goa': 'goa/', 'Andaman and Nicobar Islands': 'andaman/', 'Lakshadweep': 'lakshadweep/', 'Andhra Pradesh': 'andhrapradesh/', 'Jharkhand': 'jharkhand/', 'Haryana': 'haryana/', 'Punjab': 'punjab/', 'Odisha': 'odisha/', 'Meghalaya': 'meghalaya/', 'Arunachal Pradesh': 'arunachal/', 'Manipur': 'manipur/', 'Nagaland': 'nagaland/', 'Dadra and Nagar Haveli and Daman and Diu': 'dnhdd/', 'Chandigarh': 'chandigarh/', 'Mizoram': 'mizoram/', 'Sikkim': 'sikkim/', 'Tripura': 'tripura/' };
  I.states.forEach(function (st) { byName[st.state] = st; });
  geo.features.forEach(function (f) { var n = ALIAS[f.properties.name] || f.properties.name; byId[f.properties.ac] = { name: n, st: byName[n] }; });
  var v = function (id) { var x = byId[id]; return x && x.st && x.st.per_100 != null ? x.st.per_100 : null; };
  VIZ.map('vIndia', { geo: geo, label: L('Map of names left off the draft rolls per 100 electors, by state'), title: L('Left off per 100 electors'),
    v: v, name: function (id) { return byId[id] ? byId[id].name : ''; },
    pick: function (id) { var x = byId[id]; if (!x) return; location.href = PAGE[x.name] || 'india/'; } });
  var have = I.states.filter(function (st) { return st.per_100 != null; }).sort(function (a, b) { return b.per_100 - a.per_100; });
  var hi = have[0], lo = have[have.length - 1];
  document.getElementById('fIndia').innerHTML = L('<b>{r} names were left off the draft rolls of {n} states and union territories, {p} of every 100 electors.</b> The share runs from {lov} per 100 in {lon} to {hiv} in {hin}.', {
    r: SIR.n(I.total.removed), n: I.total.states, p: SIR.d(I.total.per_100, 1), lov: SIR.d(lo.per_100, 1), lon: lo.state, hiv: SIR.d(hi.per_100, 1), hin: hi.state });
  // the dot grid: one dot for each of 100 electors, the left-off ones red
  var red = Math.round(I.total.per_100), dots = document.getElementById('dots');
  dots.setAttribute('aria-label', L('{p} of every 100 electors were left off the draft rolls.', { p: SIR.d(I.total.per_100, 1) }));
  dots.innerHTML = Array.from({ length: 100 }, function (x, i) { return '<i' + (i < red ? ' class="on"' : '') + '></i>'; }).join('');
  var cr = function (x) { return L('{x} crore', { x: (x / 1e7).toFixed(2) }); };
  // the first two figures stay; the other two come from this list, two a day
  // in turn (SIR.day(), counted in India, so every visitor sees the same two).
  // The shares by reason are taken over the names with a published reason
  // (total.shares), which leaves out total.unsplit.
  var X = I.total, ab = M.assembly.filter(function (a) { return a.kind === 'removed'; });
  var pool = [
    [X.states, L('states and union territories in the revision')],
    [SIR.d(hi.per_100, 1), L('per 100 in {s}, the highest share', { s: hi.state })],
    [SIR.d(lo.per_100, 1), L('per 100 in {s}, the lowest share', { s: lo.state })],
    [SIR.d(X.shares.dead, 1) + '%', L('of the names left off whose reason was published were entered as dead')],
    [SIR.d(X.shares.shifted_absent_other, 1) + '%', L('of the names left off whose reason was published were entered as shifted, absent or for another reason')],
    [cr(X.duplicate), L('names were entered as enrolled more than once')],
    [L('{a} of {b}', { a: W.over, b: W.states }), L('states where women were a larger share of the names left off than of the roll')],
    [L('{a} of {b}', { a: C.above_state, b: C.compared }), L('large cities measured against their state that lost more names than it')],
    [L('{a} of {b}', { a: ab.reduce(function (t, a) { return t + a.over_margin; }, 0), b: ab.reduce(function (t, a) { return t + a.seats; }, 0) }), L('assembly seats in {s} where more names were left off or deleted than the winning margin', { s: ab.map(function (a) { return a.state; }).reduce(function (x, y) { return L('{a} and {b}', { a: x, b: y }); }) })]
  ];
  var k0 = (SIR.day() * 3) % pool.length, picks = [0, 1, 2].map(function (i) { return pool[(k0 + i) % pool.length]; });
  // the first two figures stay: the count, and that count as one in every k
  // electors on the rolls before the revision
  document.getElementById('kpis').innerHTML = [[cr(I.total.removed), L('names left off the draft rolls')], [L('1 in {k}', { k: Math.round(100 / I.total.per_100) }), L('electors was left off the draft rolls')]].concat(picks.slice(0, 2))
    .map(function (k) { return '<div><b>' + k[0] + '</b><span>' + k[1] + '</span></div>'; }).join('');
  // What the counts show: four lines that stay, and two one-state lines a day
  // from a pool kept in a fixed order (never sorted by value), each line a
  // link to the page that carries its figure. Every number comes from the data.
  var F = I.final, NN = NT;
  var line = function (href, text, note) { return '<li><a href="' + href + '">' + text + '</a>' + (note ? '<small>' + note + '</small>' : '') + '</li>'; };
  var fixed = [
    line('india/#the-three-reasons-by-phase', L('Of the names left off the draft rolls whose reason was published, {x} in every 100 were entered as dead.', { x: SIR.d(X.shares.dead, 1) }),
      L('A reason on the list is what the officer wrote down, and nobody checked it.')),
    line('india/#after-the-final-rolls', L('In the {n} states and union territories with a final roll, the final rolls came out {x} larger than the drafts, at most {p} in every 100 of the {y} names left off, and that rise includes new voters.', { n: F.states, x: SIR.lakh(F.net_after_draft), p: SIR.d(F.made_up_pct, 1), y: SIR.lakh(F.removed) })),
    line('india/process/#notices-the-no-mapping-list-and-the-discrepancy-list', L('Across the {n} states with a published total, {x} electors on the draft rolls were sent a notice, {p} in every 100. A notice is not a deletion.', { n: NN.with_total, x: SIR.lakh(NN.notices_total), p: SIR.d(NN.per_100, 1) })),
    line('india/women/', L('In {o} of the {n} states and union territories that published the names left off by sex, women were a larger share of those names than of the roll.', { o: W.over, n: W.states }))
  ];
  var Ma = BT.marriage, De = BT.deaths, spool = [
    line('bihar/people/#young-women-marked-shifted-against-marriage-movement-by-dist', L('Among the names left off Bihar\'s draft as shifted at ages 18 to 29, {w} were women and {m} were men.', { w: SIR.n(Ma.young_shifted_f), m: SIR.n(Ma.young_shifted_m) })),
    line('bihar/people/#two-reasons-set-against-the-records', L('In Bihar, the {x} names left off the draft as dead equal about {y} years of the state\'s adult deaths.', { x: SIR.lakh(De.dead_removed), y: SIR.d(De.years_of_deaths, 1) }))
  ];
  // the cities measured by the names left off the draft against the roll
  // before the revision, with a rest of the state, in alphabetical order
  r[3].cities.filter(function (c) { return c.measure === 'left_off' && !c.roll_2025 && c.rest; })
    .sort(function (a, b) { return a.city.localeCompare(b.city); })
    .forEach(function (c) { spool.push(line('india/cities/#each-city-against-its-state', L('In {city}, {a} of every 100 electors were left off the draft, against {b} in the rest of {state}.', { city: c.city, a: SIR.d(c.core.per_100, 1), b: SIR.d(c.rest.per_100, 1), state: c.state }))); });
  // margins: only the states whose count is of names left off, alphabetically
  var MW = { 'names left off the draft': function (v) { return L('In {state}, the names left off the draft outnumbered the {y} winning margin in {k} of {n} constituencies.', v); },
    'names left off or deleted, both phases': function (v) { return L('In {state}, the names left off the draft or deleted after it outnumbered the {y} winning margin in {k} of {n} constituencies.', v); } };
  M.assembly.filter(function (a) { return a.kind === 'removed' && MW[a.label]; }).sort(function (a, b) { return a.state.localeCompare(b.state); }).forEach(function (a) {
    var href = a.page + (a.state === 'Bihar' ? '#1-removals-against-the-2025-margin' : a.state === 'Tamil Nadu' ? '#names-removed-against-the-winning-margin' : '');
    spool.push(line(href, MW[a.label]({ state: a.state, y: a.election, k: a.over_margin, n: a.seats }), L('That does not show that any result would have changed.')));
  });
  var s0 = (SIR.day() * 2) % spool.length;
  document.getElementById('strip').innerHTML = fixed.concat([spool[s0], spool[(s0 + 1) % spool.length]]).join('');
  // the same figures as a ranked list, so a phone does not depend on the map
  var max = hi.per_100, rows = have.slice(), at = rows.findIndex(function (st) { return st.per_100 < I.total.per_100; });
  rows.splice(at < 0 ? rows.length : at, 0, { state: L('All India'), per_100: I.total.per_100, all: true });
  document.getElementById('rank').innerHTML = '<thead><tr><th class="l">' + L('State') + '</th><th>' + L('Per 100 electors') + '</th><th class="l" style="width:40%"><span class="sr-only">' + L('Per 100 electors') + '</span></th></tr></thead><tbody>' +
    rows.map(function (st) {
      var nm = PAGE[st.state] ? '<a href="' + PAGE[st.state] + '">' + SIR.esc(st.state) + '</a>' : SIR.esc(st.state);
      return '<tr' + (st.all ? ' class="all"' : '') + '><td class="l">' + nm + '</td><td>' + SIR.d(st.per_100, 1) + '</td><td class="l"><div class="bar" style="width:' + (100 * st.per_100 / max).toFixed(1) + '%"></div></td></tr>';
    }).join('') + '</tbody>';
  SIR.tools();
}).catch(SIR.fail);
