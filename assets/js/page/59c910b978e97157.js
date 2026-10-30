Promise.all([SIR.json('data/delhi/summary.json'), SIR.json('data/delhi/districts.json'), SIR.json('data/delhi/constituencies.json'), SIR.json('data/india/notices.json')]).then(function (r) {
  var S = r[0], D = r[1], A = r[2], NT = r[3].states.filter(function (x) { return x.state === 'Delhi'; })[0], n = SIR.n, d1 = function (v) { return SIR.d(v, 1); };
  var lk = function (x) { return SIR.lk(x, 1); };
  VIZ.waterfall('vWater', { label: 'Delhi: the roll before the revision and the draft roll of 31 August 2026', from: Math.floor(S.draft * 0.8 / 1e6) * 1e6, steps: [
    { name: 'Roll before the revision', v: S.roll_before, kind: 'total' }, { name: 'Left off the draft', v: S.left_off, kind: 'down' }, { name: 'Draft roll', v: S.draft, kind: 'total' }] });
  document.getElementById('fWater').innerHTML = '<b>The draft roll left off ' + lk(S.left_off) + ' names, ' + d1(S.per_100) + ' of every 100 electors.</b> In ' + S.acs_over_40 + ' of the 70 constituencies it left off 40 or more of every 100. It ranges from ' + d1(S.rate_min_v) + ' per 100 in ' + S.rate_min + ' to ' + d1(S.rate_max_v) + ' in ' + S.rate_max + '.';

  VIZ.lollipop('vReason', { label: 'Names left off the draft, by the reason entered', axis: 'Lakh',
    rows: [['Shifted, absent or other', S.reasons.shifted_absent_other], ['Dead', S.reasons.dead], ['Enrolled at more than one place', S.reasons.duplicate]].map(function (x) { return { name: x[0], v: x[1] / 1e5, text: lk(x[1]), tok: '--fill-navy', hi: true }; }) });
  document.getElementById('fReason').innerHTML = '<b>' + SIR.pct(S.shares.shifted_absent_other) + ' were entered as shifted, absent or other, ' + SIR.pct(S.shares.dead) + ' as dead and ' + SIR.pct(S.shares.duplicate) + ' as enrolled at more than one place.</b> The Chief Electoral Officer did not separate shifted from absent.';

  var top = D[0].district;
  VIZ.strip('vDist', { label: 'Names left off per 100 electors, every constituency, by district', axis: 'Left off per 100 electors on the roll before the revision', r: 4.5,
    key: [[top + ' district', '--fill-red'], ['Other districts', '--fill-navy']],
    rows: D.map(function (d) { return { name: d.district, tok: d.district === top ? '--fill-red' : '--fill-navy',
      points: A.filter(function (a) { return a.district === d.district; }).map(function (a) { return { v: a.per_100, label: a.name + ': ' + d1(a.per_100) + ' per 100' }; }) }; }) });
  document.getElementById('fDist').innerHTML = '<b>' + top + ' district left off ' + d1(D[0].per_100) + ' of every 100 electors, the most of the ' + D.length + '.</b> ' + D[1].district + ' and ' + D[2].district + ' come next, at ' + d1(D[1].per_100) + ' and ' + d1(D[2].per_100) + '. ' + D[D.length - 1].district + ' left off the fewest, ' + d1(D[D.length - 1].per_100) + '.';

  VIZ.lollipop('vSex', { label: 'Names left off per 100 men and per 100 women on the roll before the revision', axis: 'Left off per 100 on the roll before the revision',
    rows: [['Men', S.men_left_per_100, '--fill-navy'], ['Women', S.women_left_per_100, '--fill-pink']].map(function (x) { return { name: x[0], v: x[1], text: d1(x[1]), tok: x[2], hi: true }; }) });
  document.getElementById('fSex').innerHTML = '<b>Men were left off more often than women, ' + d1(S.men_left_per_100) + ' of every 100 men against ' + d1(S.women_left_per_100) + ' of every 100 women.</b> Women were ' + SIR.pct(S.women_before_pct) + ' of the roll before the revision and ' + SIR.pct(S.women_left_off_pct) + ' of the names left off, so their share of the draft roll rose to ' + SIR.pct(S.women_draft_pct) + '. These are state figures, with the roll before the revision by sex as reported in the press. The split by constituency was not published.';

  VIZ.scatter('vMargin', { label: 'Names left off each constituency\'s draft roll against its 2025 winning margin', diag: true, xMin: 0, yMin: 0,
    xAxis: '2025 winning margin', yAxis: 'Names left off the draft', diagLabel: 'left off = margin',
    key: [['BJP won', '--fill-nda'], ['AAP won', '--fill-india']],
    points: A.map(function (a) { return { x: a.margin, y: a.left_off, tok: a.winner === 'BJP' ? '--fill-nda' : '--fill-india', label: a.name + ' (' + a.winner + '): ' + n(a.left_off) + ' left off, margin ' + n(a.margin) }; }) });
  var P = {}; S.parties.forEach(function (p) { P[p.party] = p; });
  var under = A.filter(function (a) { return !a.over_margin; });
  document.getElementById('fMargin').innerHTML = '<b>In ' + S.over_margin + ' of the 70 constituencies, more names were left off the draft than the 2025 winning margin.</b> Not everyone on a roll votes, so scaled down by each seat\'s 2025 turnout it is ' + S.at_turnout_over_margin + '. ' + (under.length ? 'The exceptions are ' + under.map(function (a) { return a.name; }).join(' and ') + '. ' : '') + 'The BJP\'s ' + P.BJP.seats + ' seats lost ' + d1(P.BJP.per_100) + ' per 100 and the AAP\'s ' + P.AAP.seats + ' lost ' + d1(P.AAP.per_100) + '. Against their own districts the two are ' + SIR.d(P.BJP.vs_district, 1) + ' and ' + SIR.d(P.AAP.vs_district, 1) + ' points. So the difference comes mostly from where each party\'s seats are. Larger than the margin means large enough to decide a seat, and it says nothing about whether it would have.';

  document.getElementById('fAfter').innerHTML = (NT && NT.notices ? 'Of the electors left on the draft roll, ' + lk(NT.notices) + ' were sent a notice to prove their entry, ' + d1(NT.per_100) + ' of every 100. ' : '') + (NT && NT.no_mapping ? 'According to the press, ' + lk(NT.no_mapping) + ' of them were on the no-mapping list, of electors who could not be linked to the roll of the last intensive revision, and ' + lk(NT.discrepancy) + ' were on the logical discrepancy list, of entries whose details were flagged as not agreeing. ' : '') +
    'An elector asks to be added with Form 6, and an objection to a name already on the roll is made with Form 7. By 29 September, according to the press, ' + (S.form6_to_0929 >= 1e5 ? lk(S.form6_to_0929) : n(S.form6_to_0929)) + ' Form 6 claims and ' + (S.form7_to_0929 >= 1e5 ? lk(S.form7_to_0929) : n(S.form7_to_0929)) + ' Form 7 objections had been filed, counting those filed before the draft. Claims and objections can be made until ' + SIR.date(S.claims_to) + ', and the final roll is due on ' + SIR.date(S.final_due) + '.';

  SIR.table(document.getElementById('tDist'), [
    { k: 'district', label: 'District', left: true }, { k: 'acs', label: 'Seats' }, { k: 'roll_before', label: 'Roll before', fmt: n },
    { k: 'draft', label: 'Draft roll', fmt: n }, { k: 'left_off', label: 'Left off', fmt: n }, { k: 'per_100', label: 'Per 100', fmt: d1 }], D, { sort: 'per_100' });
  SIR.table(document.getElementById('tAc'), [
    { k: 'ac', label: 'No.' }, { k: 'name', label: 'Constituency', left: true }, { k: 'district', label: 'District', left: true },
    { k: 'roll_before', label: 'Roll before', fmt: n }, { k: 'draft', label: 'Draft roll', fmt: n }, { k: 'left_off', label: 'Left off', fmt: n },
    { k: 'per_100', label: 'Per 100', fmt: d1 }, { k: 'winner', label: 'Won 2025', left: true }, { k: 'margin', label: 'Margin 2025', fmt: n }], A, { sort: 'per_100' });

  var seatsOf = function (d) { return A.filter(function (a) { return a.district === d.district; }); };
  var DSET = { rows: D, key: function (d) { return SIR.slug(d.district); }, label: function (d) { return d.district + ' district'; },
    card: function (d) { return SIR.facts([['Roll before the revision', n(d.roll_before)], ['Draft roll', n(d.draft)], ['Left off', n(d.left_off)], ['Per 100 electors', d1(d.per_100)], ['Constituencies', n(d.acs)]]) + '<p class="note">Its constituencies</p>' + SIR.goList(seatsOf(d), function (a) { return 'ac-' + a.ac; }, function (a) { return a.ac + '. ' + a.name; }); },
    pick: function (d) { var b = document.getElementById('vMap'); if (b.__select) b.__select(seatsOf(d).map(function (a) { return a.ac; })); },
    share: function (d) { return d.district + ' district, Delhi. The SIR draft roll left off ' + n(d.left_off) + ' names, ' + d1(d.per_100) + ' of every 100 electors. These are counts from the Chief Electoral Officer\'s table of the draft.'; } };
  var F = SIR.finder('finder', { seatPages: true, districtPages: true, rows: A, more: [DSET], prompt: 'Find a constituency or district', placeholder: 'Type a name, a number or a district', key: function (a) { return 'ac-' + a.ac; }, label: function (a) { return a.ac + '. ' + a.name + ' (' + a.district + ')'; },
    pick: function (a) { var b = document.getElementById('vMap'); if (b.__select) b.__select(a.ac); },
    card: function (a) { return SIR.facts([['Roll before the revision', n(a.roll_before)], ['Draft roll', n(a.draft)], ['Left off', n(a.left_off)], ['Per 100 electors', d1(a.per_100)],
      ['Won in 2025', a.winner + ' · margin ' + n(a.margin)], ['Left off larger than the margin', a.over_margin ? 'Yes' : 'No']]); },
    share: function (a) { return a.name + ', Delhi. The SIR draft roll left off ' + n(a.left_off) + ' names, ' + d1(a.per_100) + ' of every 100 electors. The seat was won in 2025 by ' + n(a.margin) + ' votes. These are counts from the Chief Electoral Officer\'s table of the draft.'; } });
  SIR.json('data/geo/delhi.json').then(function (geo) {
    var byAc = {}; A.forEach(function (a) { byAc[a.ac] = a; });
    VIZ.map('vMap', { geo: geo, label: 'Map of names left off the draft per 100 electors, by constituency', title: 'Left off per 100 electors',
      v: function (ac) { return byAc[ac] ? byAc[ac].per_100 : null; }, name: function (ac) { return byAc[ac] ? byAc[ac].name : ''; },
      pick: function (ac) { if (byAc[ac]) F.select(byAc[ac]); } });
    var it = F.item[SIR.hashId()]; if (it && it.s.pick) it.s.pick(it.r);
    SIR.tools();
  });
  SIR.showFaq('dl', 'main');
}).catch(SIR.fail);
