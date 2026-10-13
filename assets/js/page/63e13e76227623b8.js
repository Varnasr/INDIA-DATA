Promise.all([SIR.json('data/gujarat/summary.json'), SIR.json('data/gujarat/districts.json'), SIR.json('data/gujarat/constituencies.json'), SIR.json('data/india/notices.json')]).then(function (r) {
  var S = r[0], D = r[1], A = r[2], NT = r[3].states.filter(function (x) { return x.state === 'Gujarat'; })[0], n = SIR.n, d1 = function (v) { return SIR.d(v, 1); };
  var lk = function (x) { return SIR.lk(x, 1); }, cr = function (x) { return (x / 1e7).toFixed(2) + ' crore'; };
  var C = S.city, R = S.rest, isCity = function (d) { return S.city_names.indexOf(d) >= 0; };
  var DL = function (iso) { var p = iso.split('-'); return +p[2] + ' ' + ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][+p[1] - 1] + ' ' + p[0]; };
  var RS = [['dead', 'Dead'], ['absent', 'Untraceable or absent'], ['shifted', 'Shifted for good'], ['enrolled_elsewhere', 'Already enrolled elsewhere'], ['other', 'Other']];

  VIZ.waterfall('vWater', { label: 'Gujarat: the roll from before the revision to the final roll', from: Math.floor(S.draft * 0.8 / 1e7) * 1e7, steps: [
    { name: 'Roll before the revision', v: S.before, kind: 'total' }].concat(RS.map(function (k) { return { name: k[1], v: S.reasons[k[0]], kind: 'down' }; }), [
    { name: 'Draft roll', v: S.draft, kind: 'total' }, { name: 'Net change after the draft', v: S.net, kind: 'up' }, { name: 'Final roll', v: S.final, kind: 'total' }]) });
  document.getElementById('fWater').innerHTML = '<b>The draft roll left off ' + lk(S.removed) + ' names, ' + d1(S.per_100) + ' of every 100 electors on the roll before the revision.</b> The roll fell from ' + cr(S.before) + ' names to ' + cr(S.draft) + ' (one crore is ten million). ' +
    'The final roll of ' + DL(S.final_date) + ' holds ' + cr(S.final) + '. It is ' + lk(S.net) + ' larger than the draft and still ' + lk(S.net_fall) + ' smaller than the roll before the revision.';

  VIZ.strip('vDist', { label: 'Names left off per 100 electors, every constituency, by district', axis: 'Left off per 100 electors on the roll before the revision', r: 4.5,
    key: [['Ahmedabad and Surat', '--fill-red'], ['Other districts', '--fill-navy']],
    rows: D.map(function (d) { return { name: d.district, tok: d.city ? '--fill-red' : '--fill-navy',
      points: A.filter(function (a) { return a.district === d.district; }).map(function (a) { return { v: a.per_100, label: a.ac + '. ' + a.name + ': ' + d1(a.per_100) + ' per 100' }; }) }; }) });
  var last = D[D.length - 1];
  document.getElementById('fDist').innerHTML = '<b>' + D[0].district + ' left off ' + d1(D[0].per_100) + ' of every 100 electors and ' + D[1].district + ' ' + d1(D[1].per_100) + ', against ' + d1(S.per_100) + ' for the state.</b> ' +
    D[2].district + ' comes next, at ' + d1(D[2].per_100) + ', and ' + last.district + ' left off the fewest, ' + d1(last.per_100) + '. ' +
    'Of the ' + S.acs + ' constituencies, ' + S.acs_over_25 + ' left off 25 or more of every 100 and ' + S.acs_under_10 + ' fewer than 10. ' + S.rate_max + ' in ' + S.rate_max_district + ' left off the most, ' + d1(S.rate_max_v) + ', and ' + S.rate_min + ' in ' + S.rate_min_district + ' the fewest, ' + d1(S.rate_min_v) + '.';

  VIZ.rank('vReason', { label: 'Names left off the draft in Gujarat, by the reason entered', axis: 'Lakh', fmt: function (v) { return SIR.lk(v * 1e5); },
    rows: RS.map(function (k) { return { name: k[1], v: S.reasons[k[0]] / 1e5, col: '--fill-navy' }; }).sort(function (a, b) { return b.v - a.v; }) });
  VIZ.heat('vMix', { label: 'Share of each district\'s names left off, by reason', cols: RS.map(function (k) { return k[1]; }), tok: ['--fill-purple', '--fill-teal', '--fill-navy', '--fill-amber', '--fill-grey'], unit: '%',
    rows: D.map(function (d) { return { name: d.district, v: RS.map(function (k) { return d[k[0] + '_share']; }) }; }) });
  var byDead = D.slice().sort(function (a, b) { return b.dead_share - a.dead_share; }), byShift = D.slice().sort(function (a, b) { return b.shifted_share - a.shifted_share; });
  document.getElementById('fMix').innerHTML = '<b>' + SIR.pct(S.shares.shifted) + ' of the names left off were entered as shifted for good, ' + SIR.pct(S.shares.dead) + ' as dead and ' + SIR.pct(S.shares.absent) + ' as untraceable or absent.</b> ' +
    SIR.pct(S.shares.enrolled_elsewhere) + ' were already enrolled at another place and ' + SIR.pct(S.shares.other) + ' were left off for some other reason. ' +
    'The share entered as shifted is highest in ' + byShift[0].district + ', at ' + SIR.pct(byShift[0].shifted_share) + '. Where fewer names were left off, more of them were entered as dead, up to ' + SIR.pct(byDead[0].dead_share) + ' in ' + byDead[0].district + '. ' +
    'Across the ' + S.acs + ' constituencies the rank correlation between the rate left off and the share entered as dead is ' + SIR.d(S.rho_rate_dead, 2) + '. A rank correlation runs from minus 1, where one measure falls in step as the other rises, through 0, where the two are unrelated, to 1, where they rise in step.';

  var tiles = [[SIR.pct(C.share_of_roll), 'of the state\'s roll before the revision', C.share_of_roll],
    [SIR.pct(C.share_of_removed), 'of the names left off', C.share_of_removed],
    [d1(C.per_100), 'left off per 100 electors, against ' + d1(R.per_100) + ' in the other 31 districts', C.per_100]];
  document.getElementById('cCity').innerHTML = tiles.map(function (t) {
    return '<div class="big"><b>' + t[0] + '</b><i style="--w:' + t[2].toFixed(1) + '%"></i><span>' + t[1] + '</span></div>';
  }).join('');
  var CA = A.filter(function (a) { return isCity(a.district); }).sort(function (a, b) { return b.per_100 - a.per_100; });
  VIZ.lollipop('vCity', { label: 'Names left off per 100 electors in every constituency of Ahmedabad and Surat districts', axis: 'Left off per 100 electors on the roll before the revision', ref: S.per_100,
    rows: CA.map(function (a) { return { name: a.name, v: a.per_100, text: d1(a.per_100), tok: a.district === 'Surat' ? '--fill-red' : '--fill-navy', hi: a.per_100 > S.per_100 }; }) });
  var cAbove = CA.filter(function (a) { return a.per_100 > S.per_100; }).length, sur = D.filter(function (d) { return d.district === 'Surat'; })[0];
  document.getElementById('fCity').innerHTML = '<b>Ahmedabad and Surat hold ' + SIR.pct(C.share_of_roll) + ' of Gujarat\'s roll and ' + SIR.pct(C.share_of_removed) + ' of the names left off, ' + lk(C.removed) + ' names in all.</b> ' +
    'Their ' + C.acs + ' constituencies lost ' + d1(C.per_100) + ' of every 100 electors, against ' + d1(R.per_100) + ' in the rest of the state, and ' + cAbove + ' of the ' + C.acs + ' lost more than the state\'s ' + d1(S.per_100) + '. ' +
    'In the chart Surat\'s seats are in red and Ahmedabad\'s in blue. ' + SIR.pct(C.shifted_share) + ' of the two districts\' names were entered as shifted for good, against ' + SIR.pct(R.shifted_share) + ' elsewhere, and ' + SIR.pct(C.dead_share) + ' as dead, against ' + SIR.pct(R.dead_share) + '. ' +
    'In Surat district, ' + SIR.pct(sur.shifted_share) + ' were entered as shifted.';

  document.getElementById('fWomen').innerHTML = '<b>None of the tables published for Gujarat counts anything by sex.</b> The CEO\'s tables give the roll before the revision, the names left off, the draft and the final roll as totals only, for the state, the districts and the constituencies. So nobody outside the Election Commission can yet say whether women were left off more often than men, here or in any district.';

  var FD = D.slice().sort(function (a, b) { return b.added_per_100 - a.added_per_100; });
  VIZ.dots('vAfter', { label: 'Names added and deleted after the draft, per 100 electors on the draft, by district', axis: 'Per 100 electors on the draft roll', cats: FD.map(function (d) { return d.district; }),
    series: [{ name: 'Added', col: '--fill-teal', vals: FD.map(function (d) { return d.added_per_100; }) }, { name: 'Deleted', col: '--fill-red', vals: FD.map(function (d) { return d.deleted_per_100; }) }] });
  var AH = S.ahmedabad.slice().sort(function (a, b) { return b.deleted_per_100 - a.deleted_per_100; });
  VIZ.scatter('vAhd', { label: 'Ahmedabad: names left off the draft and names deleted after it, by constituency', xMin: 0, yMin: 0,
    xAxis: 'Left off the draft, per 100 on the roll before', yAxis: 'Deleted after the draft, per 100 on the draft',
    key: [['BJP won in 2022', '--fill-nda'], ['Congress won in 2022', '--fill-india']],
    points: AH.map(function (a) { return { x: a.removed_per_100, y: a.deleted_per_100, tok: a.winner_party === 'BJP' ? '--fill-nda' : '--fill-india', label: a.ac + '. ' + a.name + ': ' + n(a.deleted) + ' deleted, ' + n(a.added) + ' added after the draft' }; }) });
  var addTop = AH.slice().sort(function (a, b) { return b.added - a.added; })[0];
  document.getElementById('fAhd').innerHTML = '<b>' + AH[0].name + ' lost the most after the draft, ' + n(AH[0].deleted) + ' names, ' + SIR.d(AH[0].deleted_per_100, 1) + ' for every 100 on its draft' + (function () { var sh = AH.filter(function (a) { return a.final < a.draft; }); return sh.length === 1 && sh[0] === AH[0] ? ', and it is the only one of the 21 seats whose final roll is smaller than its draft.' : '. ' + sh.length + ' of the 21 seats end with a final roll smaller than the draft.'; })() + '</b> ' +
    'Across the 21, the seats that lost more names at the draft also lost more after it (rank correlation ' + SIR.d(S.ahd_rho_removed_deleted, 2) + '). ' + addTop.name + ' added the most, ' + n(addTop.added) + '. The names added count people enrolling for the first time too, so they say little about names put back. These seat figures are from the press.';
  VIZ.slope('vFinal', { label: 'Names left off per 100 electors at the draft and the net fall at the final roll, by district',
    aName: 'At the draft', bName: 'At the final roll',
    rows: D.map(function (d, i) { return { name: d.district, a: d.per_100, b: d.net_per_100, hi: d.city, lab: !d.city && i < 4 }; }) });
  var maxAdd = FD[0], maxDel = D.slice().sort(function (a, b) { return b.deleted - a.deleted; })[0];
  document.getElementById('fFinal').innerHTML = '<b>Between the draft and the final roll, ' + lk(S.added) + ' names were added and ' + lk(S.deleted) + ' deleted, a net rise of ' + lk(S.net) + '.</b> ' +
    'That is at most ' + SIR.pct(S.made_up_pct) + ' of the names left off the draft, because the names added count new voters as well as names put back. The final roll is still ' + d1(S.net_per_100) + ' of every 100 electors smaller than the roll before the revision. ' +
    maxAdd.district + ' added the most for its size, ' + d1(maxAdd.added_per_100) + ' per 100 on its draft. ' + maxDel.district + ' deleted the most names, ' + n(maxDel.deleted) + ', so its roll rose by ' + n(maxDel.net) + ' only. ' +
    (S.net_negative.length ? S.net_negative.join(' and ') + ' deleted more names than it added. ' : '') +
    'Ahmedabad\'s roll is ' + d1(D.filter(function (d) { return d.district === 'Ahmedabad'; })[0].net_per_100) + ' per 100 and Surat\'s ' + d1(sur.net_per_100) + ' per 100 smaller than before the revision.';

  document.getElementById('fNotice').innerHTML = (NT && NT.notices ? 'Of the electors kept on the draft roll, about ' + lk(NT.notices) + ' were to be sent a notice to prove their entry at a hearing, ' + d1(NT.per_100) + ' of every 100, according to <a href="' + NT.source_url + '">The Times of India</a> of ' + DL(NT.date) + '. ' : '') +
    'How many names were deleted after a hearing has not been published separately. The deletions above count every name taken off between the draft and the final roll.';

  SIR.table(document.getElementById('tDist'), [
    { k: 'district', label: 'District', left: true }, { k: 'acs', label: 'Seats' },
    { k: 'before', label: 'Roll before', fmt: n }, { k: 'removed', label: 'Left off', fmt: n }, { k: 'per_100', label: 'Per 100', fmt: d1 },
    { k: 'dead', label: 'Dead', fmt: n }, { k: 'absent', label: 'Untraceable or absent', fmt: n }, { k: 'shifted', label: 'Shifted', fmt: n },
    { k: 'enrolled_elsewhere', label: 'Enrolled elsewhere', fmt: n }, { k: 'other', label: 'Other', fmt: n },
    { k: 'added', label: 'Added after draft', fmt: n }, { k: 'deleted', label: 'Deleted after draft', fmt: n },
    { k: 'final', label: 'Final roll', fmt: n }, { k: 'net_per_100', label: 'Net fall per 100', fmt: d1 }
  ], D, { sort: 'per_100' });
  SIR.table(document.getElementById('tAc'), [
    { k: 'ac', label: 'No.' }, { k: 'name', label: 'Constituency', left: true }, { k: 'district', label: 'District', left: true },
    { k: 'before', label: 'Roll before', fmt: n }, { k: 'removed', label: 'Left off', fmt: n }, { k: 'per_100', label: 'Per 100', fmt: d1 },
    { k: 'dead', label: 'Dead', fmt: n }, { k: 'absent', label: 'Untraceable or absent', fmt: n }, { k: 'shifted', label: 'Shifted', fmt: n },
    { k: 'enrolled_elsewhere', label: 'Enrolled elsewhere', fmt: n }, { k: 'other', label: 'Other', fmt: n }, { k: 'draft', label: 'Draft roll', fmt: n }
  ], A, { sort: 'per_100' });

  var seatsOf = function (d) { return A.filter(function (a) { return a.district === d.district; }); }, byName = {};
  D.forEach(function (d) { byName[d.district] = d; });
  var sel = function (id) { var b = document.getElementById('vMap'); if (b.__select) b.__select(id); };
  var DSET = { rows: D, key: function (d) { return SIR.slug(d.district); }, label: function (d) { return d.district + ' district'; },
    card: function (d) { return SIR.facts([['Roll before the revision', n(d.before)], ['Left off the draft', n(d.removed)], ['Per 100 electors', d1(d.per_100)],
      ['Entered as dead', n(d.dead)], ['Untraceable or absent', n(d.absent)], ['Shifted for good', n(d.shifted)], ['Already enrolled elsewhere', n(d.enrolled_elsewhere)], ['Other', n(d.other)],
      ['Added after the draft', n(d.added)], ['Deleted after the draft', n(d.deleted)], ['Fall at the final roll, per 100', d1(d.net_per_100)], ['Constituencies', n(d.acs)]]) +
      '<p class="note">Its constituencies</p>' + SIR.goList(seatsOf(d), function (a) { return 'ac-' + a.ac; }, function (a) { return a.ac + '. ' + a.name; }); },
    pick: function (d) { sel(d.id); },
    share: function (d) { return d.district + ' district, Gujarat. The SIR draft roll of 19 December 2025 left off ' + n(d.removed) + ' names here, ' + d1(d.per_100) + ' of every 100 electors on the roll before the revision. ' + n(d.dead) + ' were entered as dead. These are the Chief Electoral Officer\'s tables as published in the press. A reason is what the officer wrote down, and nobody checked it.'; } };
  var F = SIR.finder('finder', { seatPages: true, rows: A, more: [DSET], prompt: 'Find a constituency or district', placeholder: 'Type a name, a number or a district', key: function (a) { return 'ac-' + a.ac; }, label: function (a) { return a.ac + '. ' + a.name + ' (' + a.district + ')'; },
    pick: function (a) { sel(byName[a.district].id); },
    card: function (a) { return SIR.facts([['Roll before the revision', n(a.before)], ['Left off the draft', n(a.removed)], ['Per 100 electors', d1(a.per_100)],
      ['Against its district, per 100', (a.vs_district > 0 ? '+' : '') + d1(a.vs_district)],
      ['Entered as dead', n(a.dead)], ['Untraceable or absent', n(a.absent)], ['Shifted for good', n(a.shifted)], ['Already enrolled elsewhere', n(a.enrolled_elsewhere)], ['Other', n(a.other)],
      ['Won in 2022', a.winner_party + ' · margin ' + n(a.margin)], ['Left off more than the margin', a.over_margin ? 'Yes' : 'No']]); },
    share: function (a) { return a.name + ', Gujarat. The SIR draft roll of 19 December 2025 left off ' + n(a.removed) + ' names here, ' + d1(a.per_100) + ' of every 100 electors. ' + n(a.removed - a.dead) + ' of them were not entered as dead. The seat was won in 2022 by ' + n(a.margin) + ' votes. These are the Chief Electoral Officer\'s tables as published in the press. A reason is what the officer wrote down, and nobody checked it.'; } });
  SIR.json('data/geo/gujarat.json').then(function (geo) {
    var byId = {}; D.forEach(function (d) { byId[d.id] = d; });
    VIZ.map('vMap', { geo: geo, label: 'Map of names left off the draft per 100 electors, by district', title: 'Left off per 100 electors',
      v: function (id) { return byId[id] ? byId[id].per_100 : null; }, name: function (id) { return byId[id] ? byId[id].district : ''; },
      pick: function (id) { if (byId[id]) F.select(byId[id]); } });
    var it = F.item[SIR.hashId()]; if (it && it.s.pick) it.s.pick(it.r);
    SIR.tools();
  });
  SIR.showFaq('gj', 'main');
}).catch(SIR.fail);
