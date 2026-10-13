SIR.json('data/india/states.json').then(function (I) {
  var PAGE = { 'Delhi': 'delhi/', 'Chandigarh': 'chandigarh/', 'Puducherry': 'puducherry/', 'Lakshadweep': 'lakshadweep/', 'Andaman and Nicobar Islands': 'andaman/', 'Dadra and Nagar Haveli and Daman and Diu': 'dnhdd/' };
  var SHORT = { 'Andaman and Nicobar Islands': 'Andaman and Nicobar', 'Dadra and Nagar Haveli and Daman and Diu': 'Dadra, Daman and Diu' };
  var nm = function (s) { return SHORT[s.state] || s.state; };
  var U = I.states.filter(function (s) { return PAGE[s.state]; }).sort(function (a, b) { return b.per_100 - a.per_100; });
  var d1 = function (x) { return SIR.d(x, 1); }, n = SIR.n, list = function (a) { return a.join(', ').replace(/, ([^,]*)$/, ' and $1'); };
  var all = I.total.per_100, hi = U[0], lo = U[U.length - 1], above = U.filter(function (s) { return s.per_100 > all; });
  var why = U.filter(function (s) { return s.shares; }), fin = U.filter(function (s) { return s.made_up_pct != null; });
  var G = I.gender.filter(function (g) { return PAGE[g.state]; });
  var tot = U.reduce(function (t, s) { return t + s.removed; }, 0), bef = U.reduce(function (t, s) { return t + s.electors_before; }, 0);

  SIR.inShort([
    'The six union territories in the revision left ' + SIR.lakh(tot) + ' names off their draft rolls, ' + d1(100 * tot / bef) + ' of every 100 electors on their rolls before it. ' + SIR.n(Math.round(100 * U.filter(function (s) { return s.state === 'Delhi'; })[0].removed / tot)) + ' in every 100 of those names were in Delhi.',
    hi.state + ' left off ' + d1(hi.per_100) + ' of every 100 electors and ' + lo.state + ' ' + d1(lo.per_100) + '. ' + list(above.map(nm)) + ' were above the rate for every state and territory together, ' + d1(all) + '.',
    (function () {
      var top = function (s) { var x = s.shares; return x.dead > x.shifted_absent_other && x.dead > x.duplicate ? 'dead' : x.duplicate > x.shifted_absent_other ? 'duplicate' : 'shifted'; };
      var odd = why.filter(function (s) { return top(s) !== 'shifted'; });
      return 'In ' + (why.length - odd.length) + ' of the ' + why.length + ' territories with the reasons published, the largest share of names was entered as shifted, absent or for another reason.' +
        odd.map(function (s) { return ' In ' + s.state + ' the largest share, ' + SIR.pct(s.shares[top(s)]) + ', was entered as ' + (top(s) === 'dead' ? 'dead' : 'enrolled more than once') + '.'; }).join('');
    })(),
    G.length ? 'Women were a smaller share of the names left off than of the roll in ' + list(G.filter(function (g) { return g.gap < 0; }).map(function (g) { return g.state; })) + ', the territories that published the split by sex.' : ''
  ], (function () {
    // which territories' figures came through the press, and which published no reasons, from the state table
    var press = U.filter(function (s) { return s.source === 'press'; }).map(function (s) { return s.state; }), none = U.filter(function (s) { return !s.shares; }).map(function (s) { return s.state; });
    return 'Jammu and Kashmir and Ladakh were not in the revision.' + (press.length ? ' The figures for ' + list(press) + ' reached us through press reports of the official figures.' : '') +
      (none.length ? ' ' + list(none) + ' published no count of the reasons.' : '');
  })());

  document.getElementById('kpis').innerHTML = [
    [SIR.lakh(tot), 'names left off in the six territories'],
    [d1(100 * tot / bef), 'of every 100 electors on their rolls'],
    [d1(hi.per_100), 'per 100 in ' + hi.state + ', the highest'],
    [d1(lo.per_100), 'per 100 in ' + lo.state + ', the lowest']
  ].map(function (k) { return '<div><b>' + k[0] + '</b><span>' + k[1] + '</span></div>'; }).join('');

  VIZ.lollipop('vRate', { label: 'Names left off the draft roll per 100 electors, in each union territory', axis: 'Per 100 electors on the roll before', ref: all,
    rows: U.map(function (s) { return { name: nm(s), v: s.per_100, text: d1(s.per_100), tok: '--fill-red', hi: true }; }) });
  document.getElementById('nRate').textContent = 'The line marks ' + d1(all) + ', the rate for every state and territory in the revision together. The territories ran the revision in two phases, Puducherry, Lakshadweep and Andaman and Nicobar from November 2025 and the other three in 2026.';
  document.getElementById('fRate').innerHTML = '<b>' + hi.state + ' left off ' + d1(hi.per_100) + ' of every 100 electors, the most of any territory, and ' + lo.state + ' ' + d1(lo.per_100) + ', the fewest.</b> Delhi alone left off ' + SIR.lakh(U.filter(function (s) { return s.state === 'Delhi'; })[0].removed) + ' names.';

  VIZ.dots('vWhy', { label: 'Share of each territory\'s names left off under each reason', axis: 'Per cent of the names left off',
    cats: why.map(nm),
    series: [{ name: 'Shifted, absent or other', col: '--fill-navy', vals: why.map(function (s) { return s.shares.shifted_absent_other; }) },
             { name: 'Dead', col: '--fill-grey', vals: why.map(function (s) { return s.shares.dead; }) },
             { name: 'Enrolled more than once', col: '--fill-red', vals: why.map(function (s) { return s.shares.duplicate; }) }] });
  document.getElementById('nWhy').textContent = 'Dadra and Nagar Haveli and Daman and Diu is left out, because only rounded shares were reported for it. Lakshadweep left off ' + n(U.filter(function (s) { return s.state === 'Lakshadweep'; })[0].removed) + ' names in all, so its shares rest on few.';

  VIZ.lollipop('vBack', { label: 'Net change from the draft to the final roll, per 100 names left off', axis: 'Per 100 left off at the draft',
    rows: fin.sort(function (a, b) { return b.made_up_pct - a.made_up_pct; }).map(function (s) { return { name: nm(s), v: Math.max(s.made_up_pct, 0), text: d1(s.made_up_pct), tok: s.made_up_pct < 0 ? '--fill-red' : '--fill-navy', hi: true }; }) });
  var shrank = fin.filter(function (s) { return s.made_up_pct < 0; }), wait = U.filter(function (s) { return s.made_up_pct == null; });
  document.getElementById('nBack').textContent = (shrank.length ? 'In ' + list(shrank.map(function (s) { return s.state; })) + ' the final roll is smaller than the draft. ' : '') + (wait.length ? list(wait.map(function (s) { return s.state; })) + (wait.length > 1 ? ' have' : ' has') + ' no final roll yet.' : '');

  if (G.length) {
    VIZ.dumbbell('vWomen', { label: 'Women\'s share of the roll before the revision and of the names left off', min: 40, step: 5,
      aName: 'Share of the roll before', aTok: '--fill-grey', bName: 'Share of the names left off', bTok: '--fill-red', rows: G.map(function (g) { return { name: g.state, a: g.women_share_roll, b: g.women_share_removed }; }) });
    document.getElementById('nWomen').textContent = 'Only ' + list(G.map(function (g) { return g.state; })) + ' published the roll by sex both before the revision and at the draft. ' + (G.every(function (g) { return g.gap < 0; }) ? 'In ' + (G.length > 1 ? 'both' : 'it') + ', men made up a larger share of the names left off than of the roll. ' : '') + 'The figures cannot say why.';
  }

  SIR.table('tUts', [{ h: 'Territory' }, { h: 'Roll before', num: true }, { h: 'Left off', num: true }, { h: 'Per 100', num: true }, { h: 'Final roll', num: true }, { h: 'Source' }],
    U.map(function (s) { return ['<a href="../../' + PAGE[s.state] + '">' + SIR.esc(s.state) + '</a>', n(s.electors_before), n(s.removed), d1(s.per_100), s.electors_final ? n(s.electors_final) : 'not yet', s.source === 'primary' ? 'Official' : 'Press']; }));
  SIR.showFaq('india', 'uts');
}).catch(SIR.fail);
