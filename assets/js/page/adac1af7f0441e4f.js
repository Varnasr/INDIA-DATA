Promise.all([SIR.json('data/gujarat/summary.json'), SIR.json('data/gujarat/constituencies.json')]).then(function (r) {
  var S = r[0], A = r[1], n = SIR.n, d1 = function (v) { return SIR.d(v, 1); };
  var tokOf = function (p) { return p === 'BJP' ? '--fill-nda' : p === 'INC' ? '--fill-india' : '--fill-purple'; };
  var isCity = function (a) { return S.city_names.indexOf(a.district) >= 0; };

  VIZ.scatter('vScatter', { label: 'Names left off each constituency\'s draft roll against its 2022 winning margin', diag: true, xMin: 0, yMin: 0,
    xAxis: '2022 winning margin, votes', yAxis: 'Names left off the draft',
    key: [['BJP won', '--fill-nda'], ['Congress won', '--fill-india'], ['Others won', '--fill-purple']],
    points: A.map(function (a) { return { x: a.margin, y: a.removed, tok: tokOf(a.winner_party), label: a.ac + '. ' + a.name + ' (' + a.winner_party + '): ' + n(a.removed) + ' left off, margin ' + n(a.margin) }; }) });
  document.getElementById('fScatter').innerHTML = '<b>In ' + S.over_margin + ' of the ' + S.acs + ' constituencies, more names were left off the draft roll than the 2022 winning margin.</b> ' +
    'The seats that lost the most names were mostly not close contests. Across the ' + S.acs + ' seats the rank correlation between the rate left off and the margin is ' + SIR.d(S.rho_rate_margin, 2) + ', where 0 means the two are unrelated and 1 means they rise in step, because the city seats that lost the most were won by wide margins. ' +
    'Larger than the margin means large enough to decide a seat, and it says nothing about whether it would have.';

  var counts = [['Every name left off', S.over_margin], ['Leaving out the dead', S.alive_over_margin], ['Leaving out the dead and those enrolled elsewhere', S.narrow_over_margin], ['Leaving out the dead, at 2022 turnout', S.turnout_over_margin]];
  document.getElementById('cCounts').innerHTML = counts.map(function (c) {
    return '<div class="big"><b>' + c[1] + '</b><span class="of">of ' + S.acs + ' seats</span><i style="--w:' + (100 * c[1] / S.acs).toFixed(1) + '%"></i><span>' + c[0] + '</span></div>';
  }).join('');
  document.getElementById('fCounts').innerHTML = '<b>Leaving out the dead, the names left off outnumber the 2022 margin in ' + S.alive_over_margin + ' of the ' + S.acs + ' seats, and in ' + S.turnout_over_margin + ' at each seat\'s 2022 turnout.</b> Turnout across the state was ' + SIR.d(S.turnout_2022, 1) + ' per cent. ' +
    'In ' + (S.acs - S.narrow_over_margin) + ' seats, even the names neither dead nor enrolled elsewhere fall short of the margin, so there the runner-up could not have won even if every one of those electors had voted, and voted for the runner-up. Not everyone on a roll votes, so every count here is the most the names could weigh, and the lists cannot show how anyone left off would have voted.';

  var CL = A.slice().sort(function (a, b) { return a.margin - b.margin; }).slice(0, 20);
  VIZ.dots('vClose', { label: 'The 20 closest seats of 2022: the winning margin and the names left off in 2025', axis: 'Votes or names', cats: CL.map(function (a) { return a.name + ' (' + a.winner_party + ')'; }),
    series: [{ name: '2022 margin', col: '--fill-navy', vals: CL.map(function (a) { return a.margin; }) }, { name: 'Left off in 2025', col: '--fill-red', vals: CL.map(function (a) { return a.removed; }) }] });
  var clOver = CL.filter(function (a) { return a.over_margin; }).length, c0 = S.closest[0], c1 = S.closest[1];
  var clParty = {}; CL.forEach(function (a) { clParty[a.winner_party] = (clParty[a.winner_party] || 0) + 1; });
  document.getElementById('fClose').innerHTML = '<b>In ' + (clOver === CL.length ? 'every one' : clOver) + ' of the ' + CL.length + ' closest seats, the names left off were more than the margin.</b> ' +
    c0.name + ' was won by ' + n(c0.margin) + ' votes and lost ' + n(c0.removed) + ' names, and ' + c1.name + ' was won by ' + n(c1.margin) + ' and lost ' + n(c1.removed) + '. ' +
    'Of the twenty, ' + (function (a) { return a.length < 2 ? a.join('') : a.slice(0, -1).join(', ') + ' and ' + a[a.length - 1]; })(Object.keys(clParty).sort(function (a, b) { return clParty[b] - clParty[a]; }).map(function (p) { return clParty[p] + ' were won by the ' + (p === 'INC' ? 'Congress' : p === 'IND' ? 'independents' : p); })) + '.';

  var W = {}; S.winners.forEach(function (w) { W[w.party] = w; });
  var groups = [['BJP', 'BJP'], ['INC', 'Congress'], ['other', 'AAP, SP and independents']];
  VIZ.strip('vSwarm', { label: 'Names left off per 100 electors in every constituency, by the party that won it in 2022', axis: 'Left off per 100 electors', r: 4,
    key: [['Ahmedabad and Surat', '--fill-red'], ['Rest of the state', '--fill-navy']],
    rows: groups.map(function (g) {
      var pts = A.filter(function (a) { return g[0] === 'other' ? ['BJP', 'INC'].indexOf(a.winner_party) < 0 : a.winner_party === g[0]; });
      return { name: g[1] + ' (' + pts.length + ' seats)', tok: '--fill-navy',
        points: pts.map(function (a) { return { v: a.per_100, tok: isCity(a) ? '--fill-red' : null, label: a.name + ' (' + a.district + ', ' + a.winner_party + '): ' + d1(a.per_100) + ' per 100' }; }) };
    }) });
  var sg = function (v) { return (v > 0 ? '+' : '') + d1(v); };
  SIR.table(document.getElementById('tWin'), [
    { k: 'party', label: 'Party that won', left: true }, { k: 'seats', label: 'Seats' },
    { k: 'per_100', label: 'Left off per 100', fmt: d1 }, { k: 'vs_district', label: 'Against own district', fmt: sg },
    { k: 'over_margin', label: 'Left off more than the margin' }
  ], S.winners, { sort: 'seats' });
  var cityBJP = A.filter(function (a) { return isCity(a) && a.winner_party === 'BJP'; }).length, cityAll = A.filter(isCity).length;
  document.getElementById('fWin').innerHTML = '<b>Seats the BJP won in 2022 lost ' + d1(W.BJP.per_100) + ' of every 100 electors, against ' + d1(W.INC.per_100) + ' in the Congress\'s seats and ' + d1(W.AAP.per_100) + ' in the AAP\'s.</b> ' +
    'Most of that gap is about where the seats are. The BJP won ' + cityBJP + ' of the ' + cityAll + ' seats in Ahmedabad and Surat districts, where the most names were left off. Set against their own districts, the BJP\'s seats come out at ' + sg(W.BJP.vs_district) + ', the Congress\'s at ' + sg(W.INC.vs_district) + ' and the AAP\'s at ' + sg(W.AAP.vs_district) + ' per 100. ' +
    'The names left off were more than the margin in ' + W.BJP.over_margin + ' of the BJP\'s ' + W.BJP.seats + ' seats and in ' + W.INC.over_margin + ' of the Congress\'s ' + W.INC.seats + '.';

  SIR.table(document.getElementById('tAc'), [
    { k: 'ac', label: 'No.' }, { k: 'name', label: 'Constituency', left: true }, { k: 'district', label: 'District', left: true },
    { k: 'removed', label: 'Left off', fmt: n }, { k: 'per_100', label: 'Per 100', fmt: d1 }, { k: 'vs_district', label: 'Against district', fmt: sg },
    { k: 'winner_party', label: 'Won 2022', left: true }, { k: 'runner_up_party', label: 'Second', left: true },
    { k: 'margin', label: 'Margin', fmt: n }, { k: 'over_margin', label: 'Left off over margin', fmt: function (v) { return v ? 'Yes' : 'No'; } }
  ], A, { sort: 'removed' });
  SIR.showFaq('gj', 'elections');
}).catch(SIR.fail);
