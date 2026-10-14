Promise.all([SIR.json('data/uttarpradesh/summary.json'), SIR.json('data/uttarpradesh/districts.json'), SIR.json('data/uttarpradesh/analysis.json'),
  SIR.json('data/india/disputes.json'), SIR.json('data/india/help.json')]).then(function (r) {
  var S = r[0], D = r[1], A = r[2], n = SIR.n, d1 = function (v) { return SIR.d(v, 1); };
  var cr = function (x) { return (x / 1e7).toFixed(2) + ' crore'; }, lk = function (x) { return SIR.lk(x, 1); };
  var RN = { dead: 'Dead', untraceable_absent: 'Untraceable or absent', shifted: 'Permanently shifted', multiple: 'Already enrolled', others: 'Other' };
  var RK = ['shifted', 'untraceable_absent', 'dead', 'multiple', 'others'];
  VIZ.waterfall('vWater', { label: 'Uttar Pradesh: the roll from 27 October 2025 to the final roll of 10 April 2026', from: Math.floor(S.draft * 0.85 / 1e7) * 1e7, steps: [
    { name: 'Roll of 27 October 2025', v: S.roll_before, kind: 'total' }, { name: 'Left off the draft', v: S.left_off, kind: 'down' },
    { name: 'Draft roll', v: S.draft, kind: 'total' }, { name: 'Net change to the final roll', v: S.net_rise, kind: 'up' }, { name: 'Final roll', v: S.final, kind: 'total' }] });
  document.getElementById('fWater').innerHTML = '<b>The draft roll left off ' + cr(S.left_off) + ' names, ' + d1(S.per_100) + ' of every 100 electors.</b> The final roll was ' + lk(S.net_rise) + ' larger than the draft, ' + SIR.pct(S.made_up_pct) + ' of what the draft left off. That rise counts new voters as well as names put back, so it is the most that can have been put back. A further ' + lk(S.removed_after) + ' were deleted after the draft, as reported in the press.';

  VIZ.lollipop('vDist', { label: 'Names left off the draft roll per 100 electors, every district', axis: 'Left off per 100 electors on the roll of 27 October 2025', ref: S.per_100,
    rows: D.map(function (d) { return { name: d.district, v: d.per_100, text: d1(d.per_100), tok: d.per_100 >= 20 ? '--fill-red' : '--fill-navy', hi: d.per_100 >= 20 }; }) });
  document.getElementById('fDist').innerHTML = '<b>' + D[0].district + ' left off ' + d1(D[0].per_100) + ' of every 100 electors, ' + lk(D[0].total) + ' names, the most of any district.</b> ' + D[1].district + ', ' + D[2].district + ', ' + D[3].district + ' and ' + D[4].district + ' come next. ' + S.over_20 + ' of the 75 districts left off 20 or more per 100, against ' + d1(S.per_100) + ' for the state. ' + D[D.length - 1].district + ' left off the fewest, ' + d1(D[D.length - 1].per_100) + '. The upright line on the chart marks the rate for the state as a whole.';

  var top5 = D.slice().sort(function (a, b) { return b.total - a.total; }).slice(0, 5), tops = top5.map(function (d) { return d.district; });
  var RT = { shifted: '--fill-navy', untraceable_absent: '--fill-purple', dead: '--fill-grey', multiple: '--fill-amber', others: '--fill-other' };
  var tg = top5.map(function (d) { return { name: d.district, tok: '--fill-red' }; }).concat([{ name: 'Other ' + (D.length - 5) + ' districts', tok: '--fill-navy' }]);
  var links = [];
  RK.forEach(function (k, i) {
    top5.forEach(function (d, j) { links.push({ s: i, t: j, v: d[k] }); });
    links.push({ s: i, t: 5, v: S.reasons[k] - top5.reduce(function (a, d) { return a + d[k]; }, 0) });
  });
  VIZ.sankey('vFlow', { label: 'Names left off the draft roll, from the reason entered to the district', height: innerWidth < 600 ? 520 : 420, minH: innerWidth < 600 ? 44 : 34, lw: innerWidth < 600 ? 100 : 200,
    sources: RK.map(function (k) { return { name: RN[k], tok: RT[k] }; }), targets: tg, links: links });
  var hi5 = D.slice(0, 5).map(function (d) { return d.district; });
  VIZ.strip('vReason', { label: 'Share of each district\'s names left off, by the reason entered, every district', axis: 'Share of the district\'s names left off, %', r: 3.5, step: 10,
    key: [['Five highest rates', '--fill-red'], ['Other districts', '--fill-navy']],
    rows: RK.map(function (k) { return { name: RN[k], tok: '--fill-navy',
      points: D.map(function (d) { return { v: d[k + '_pct'], tok: hi5.indexOf(d.district) >= 0 ? '--fill-red' : '--fill-navy', label: d.district + ': ' + SIR.pct(d[k + '_pct']) + ' ' + RN[k].toLowerCase() }; }) }; }) });
  var hiAbs = D.slice().sort(function (a, b) { return b.untraceable_absent_pct - a.untraceable_absent_pct; })[0], hiDead = D.slice().sort(function (a, b) { return b.dead_pct - a.dead_pct; })[0];
  document.getElementById('fReason').innerHTML = '<b>Across the state, ' + SIR.pct(S.shares.shifted) + ' of the names left off were entered as permanently shifted, ' + SIR.pct(S.shares.untraceable_absent) + ' as untraceable or absent and ' + SIR.pct(S.shares.dead) + ' as dead.</b> ' + SIR.pct(S.shares.multiple) + ' were entered as already enrolled elsewhere. The share entered as untraceable or absent is highest in ' + hiAbs.district + ', ' + SIR.pct(hiAbs.untraceable_absent_pct) + ', and the share entered as dead in ' + hiDead.district + ', ' + SIR.pct(hiDead.dead_pct) + '.';

  // ---- when it happened
  var sched = A.schedule, first = sched[0], done = sched[sched.length - 1];
  var days = function (a, b) { return Math.round((Date.parse(b) - Date.parse(a)) / 864e5); };
  VIZ.gantt('vCal', { label: 'Uttar Pradesh: each schedule the Commission set, and the revision as it was carried out', single: true,
    rows: sched.map(function (x) { return { name: x.label, steps: [{ label: x.label, enum: x.enum, draft: x.draft, claims: x.claims, final: x.final }] }; }) });
  document.getElementById('fCal').innerHTML = '<b>The final roll came out on ' + SIR.date(done.final) + ', ' + days(first.final, done.final) + ' days after the date in the Commission\'s order of 27 October 2025.</b> The draft was published on ' + SIR.date(done.draft) + ', ' + days(first.draft, done.draft) + ' days later than that order set. Claims ran to ' + SIR.date(done.claims[1]) + ', and notices were heard until ' + SIR.date(done.notice[1]) + '.';

  // ---- the draft against earlier rolls
  var R = A.rolls, cr2 = function (x) { return (x / 1e7).toFixed(2); };
  VIZ.lollipop('vRolls', { label: 'Electors on each roll, in crore', axis: 'Electors, crore', rows: [
    { name: 'Assembly election, 2022', v: R.assembly_2022 / 1e7, text: cr2(R.assembly_2022), tok: '--fill-grey' },
    { name: 'Lok Sabha election, 2024', v: R.ls_2024 / 1e7, text: cr2(R.ls_2024), tok: '--fill-grey' },
    { name: 'Roll of 27 October 2025', v: S.roll_before / 1e7, text: cr2(S.roll_before), tok: '--fill-navy' },
    { name: 'Draft roll, 6 January 2026', v: S.draft / 1e7, text: cr2(S.draft), tok: '--fill-red', hi: true },
    { name: 'Final roll, 10 April 2026', v: S.final / 1e7, text: cr2(S.final), tok: '--fill-navy' },
    { name: 'People aged 18 and over, projected for March 2026', v: R.adults_2026 / 1e7, text: cr2(R.adults_2026), tok: '--fill-other' }] });
  document.getElementById('fRolls').innerHTML = '<b>The final roll holds ' + cr(R.assembly_2022 - S.final) + ' fewer electors than the roll of the 2022 Assembly election, and ' + cr(R.ls_2024 - S.final) + ' fewer than the roll of the 2024 Lok Sabha election.</b> The roll the revision started from held ' + d1(R.before_per_100_adults) + ' electors for every 100 people of voting age. The draft held ' + d1(R.draft_per_100_adults) + ' and the final roll ' + d1(R.final_per_100_adults) + '. The population figure is a projection, and if it is right, about ' + cr(R.adults_2026 - S.final) + ' adults living in the state are on no roll here, some of them because they are registered in another state or are not citizens.';

  // ---- towns and villages
  var U = A.urban, UB = A.factors.urban.bands;
  VIZ.lollipop('vUrban', { label: 'Names left off per 100 electors, urban and rural', axis: 'Left off per 100 electors on the roll of 27 October 2025', ref: S.per_100, rows: [
    { name: 'Urban areas (CEO, press)', v: U.urban_per_100, text: d1(U.urban_per_100), tok: '--fill-red', hi: true },
    { name: 'Rural areas (CEO, press)', v: U.rural_per_100, text: d1(U.rural_per_100), tok: '--fill-navy' }].concat(UB.map(function (b) {
      return { name: { rural: 'Rural districts', mixed: 'Mixed districts', urban: 'Urban districts' }[b.band] + ' (' + b.units + ')', v: b.per_100, text: d1(b.per_100), tok: b.band === 'urban' ? '--fill-red' : '--fill-grey' }; })) });
  document.getElementById('fUrban').innerHTML = '<b>Urban areas lost ' + d1(U.urban_per_100) + ' names for every 100 electors and rural areas ' + d1(U.rural_per_100) + '.</b> Urban areas held ' + SIR.pct(U.urban_share_roll) + ' of the roll and ' + SIR.pct(U.urban_share_left) + ' of the names left off, ' + cr(U.urban_left) + ' of them. The five districts where most people lived in towns in 2011 lost ' + d1(UB[2].per_100) + ' per 100 and the ' + UB[0].units + ' most rural ' + d1(UB[0].per_100) + '. The Hindustan Times printed the rural fall as 1.27 crore, but its own two rural rolls, and the 15.23% it gives, put it at ' + cr(U.rural_left) + ', which is the figure used here.';

  // ---- against the 2022 margins
  var M = A.margins;
  var BINS = [['Less than the margin', 0, 1], ['1 to 2 times the margin', 1, 2], ['2 to 5 times', 2, 5], ['5 to 10 times', 5, 10], ['10 times or more', 10, Infinity]];
  VIZ.lollipop('vMult', { label: 'Constituencies by how many times their 2022 margin the names left off came to', axis: 'Constituencies',
    rows: BINS.map(function (b, i) { var k = M.seats.filter(function (a) { var m = a.est / a.margin; return m >= b[1] && m < b[2]; }).length;
      return { name: b[0], v: k, text: n(k), tok: i === 0 ? '--fill-grey' : '--fill-red', hi: i === 4 }; }) });
  VIZ.scatter('vMargin', { label: 'Each constituency: its 2022 winning margin against the names left off, spread from its district', diag: true, xMin: 0, yMin: 0,
    xAxis: '2022 winning margin, votes', yAxis: 'Names left off, district spread by electors', diagLabel: 'left off = margin',
    key: [['Won by the NDA', '--fill-amber'], ['Won by the SP alliance', '--fill-red'], ['Won by another party', '--fill-grey']],
    points: M.seats.map(function (a) { return { x: a.margin, y: a.est, tok: a.alliance === 'NDA' ? '--fill-amber' : a.alliance === 'SP alliance' ? '--fill-red' : '--fill-grey',
      label: a.name + ' (' + a.district + '): margin ' + n(a.margin) + ', about ' + n(a.est) + ' left off' }; }) });
  document.getElementById('fMargin').innerHTML = '<b>On this spread, the names left off were larger than the 2022 winning margin in ' + M.over + ' of the ' + M.n + ' constituencies.</b> In the typical seat the margin was ' + n(M.median_margin) + ' votes and the spread puts ' + n(M.median_est) + ' names left off. All ' + M.under_5000 + ' seats won by fewer than 5,000 votes are among them. Larger than the margin means the names left off were large enough to decide the seat. It does not mean they did, since the people left off would not all have voted, nor all for one side. Spreading the state\'s total over the seats without the district split, as the All India margins page does, gives ' + M.state_even_over + '.';
  SIR.table(document.getElementById('tAll'), [{ k: 'a', label: 'Won in 2022 by', left: true }, { k: 'seats', label: 'Seats', fmt: n }, { k: 'over', label: 'Left off above the margin', fmt: n }, { k: 'per_100', label: 'Their districts\' rate per 100', fmt: d1 }],
    ['NDA', 'SP alliance', 'Other'].map(function (k) { return Object.assign({ a: k === 'Other' ? 'Another party' : k }, M.alliances[k]); }));

  // ---- the reasons against the rate
  var RH = A.reason_rho;
  VIZ.scatter('vAbsent', { label: 'Each district: names left off per 100 electors against the share entered as untraceable or absent', xMin: 0, yMin: 0,
    xAxis: 'Left off per 100 electors', yAxis: 'Untraceable or absent, % of names left off',
    points: D.map(function (d) { return { x: d.per_100, y: d.untraceable_absent_pct, tok: d.per_100 >= 20 ? '--fill-red' : '--fill-navy', label: d.district + ': ' + d1(d.per_100) + ' per 100, ' + SIR.pct(d.untraceable_absent_pct) + ' untraceable or absent' }; }) });
  document.getElementById('fAbsent').innerHTML = '<b>The rank correlation between a district\'s rate and the share it entered as untraceable or absent is ' + SIR.d(RH.untraceable_absent, 2) + '.</b> With the share entered as dead it is ' + SIR.d(RH.dead, 2) + ', and with the share entered as permanently shifted ' + SIR.d(RH.shifted, 2) + '. The districts that lost the most names lost them mostly as people the officers could not find, the least checkable of the five reasons.';

  // ---- district circumstances
  var FA = A.factors, rows = FA.rows.concat([{ label: 'Share of people in towns, 2011', rho: FA.urban.rho, clear: FA.urban.clear }]);
  VIZ.dots('vFactors', { label: 'Rank correlation between each district\'s rate and its circumstances', axis: 'Rank correlation',
    cats: rows.map(function (x) { return x.label; }), series: [{ name: 'Rank correlation with the rate', col: '--fill-navy', vals: rows.map(function (x) { return x.rho; }) }] });
  var clear = rows.filter(function (x) { return x.clear; });
  document.getElementById('fFactors').innerHTML = (clear.length ? '<b>' + clear.map(function (x) { return x.label.toLowerCase() + ' (' + SIR.d(x.rho, 2) + ')'; }).join(' and ') + ' ' + (clear.length > 1 ? 'are' : 'is') + ' the only circumstance clear of chance.</b> ' : '<b>No circumstance is clear of chance.</b> ') +
    'Schooling, early marriage, sanitation, registered deaths and the sex ratio show no relationship with the rate. Clean cooking fuel is most common in the towns, and the share of people in towns, ' + SIR.d(FA.urban.rho, 2) + ' across ' + FA.urban.units + ' districts of 2011, sits just short of the line. The rate follows the towns more than anything about schooling or women\'s lives.';

  document.getElementById('fWomen').innerHTML = (function (X) {
    return '<b>Women were ' + SIR.pct(X.women_share) + ' of the names left off and ' + SIR.pct(X.women_share_before) + ' of the roll before the revision.</b> For every 100 women on the roll, ' + d1(X.women_per_100) + ' were left off the draft, against ' + d1(X.men_per_100) + ' for every 100 men. The roll had ' + X.ratio_before + ' women for every 1,000 men in 2025, the draft ' + X.ratio_draft + ' and the final roll ' + X.ratio_final + '. Women were ' + SIR.pct(S.rise_women_pct) + ' of the rise from the draft to the final roll, ' + SIR.pct(S.form6_women_pct) + ' of the ' + lk(S.form6) + ' Form 6 claims, and ' + SIR.pct(S.form7_women_pct) + ' of the electors whose deletion was sought in the ' + lk(S.form7) + ' Form 7 objections.'; })(A.sex);
  document.getElementById('fFather').innerHTML = (function (X) {
    return '<b>The Chief Electoral Officer said ' + lk(X.father_left_off) + ' women over 25 still registered at their father\'s address were left off, and ' + lk(X.father_kept) + ' were kept.</b> He gave this as the main reason more women than men were left off, because a woman registered at her parents\' home and again at her husband\'s appears twice. That one group is ' + lk(X.father_beyond_multiple) + ' larger than every name in the state entered as already enrolled elsewhere, ' + lk(S.reasons.multiple) + ', so most of these women were entered under another reason, such as permanently shifted. The lists do not say whether each of them was on the roll a second time.'; })(A.sex);
  document.getElementById('nWomen').textContent = 'The split by sex and the figures on women registered at their father\'s address are the Chief Electoral Officer\'s, given to the Hindustan Times (18 January 2026) in lakh and crore. The two parts he gave of the 71.18 lakh women checked add to 71.55 lakh. The draft and final rolls by sex are the CEO\'s own exact figures.';
  VIZ.lollipop('vWomen', { label: 'Names left off per 100 on the roll before the revision, women and men', axis: 'Left off per 100 on the roll of 27 October 2025', ref: S.per_100, rows: [
    { name: 'Women', v: A.sex.women_per_100, text: d1(A.sex.women_per_100), tok: '--fill-red', hi: true }, { name: 'Men', v: A.sex.men_per_100, text: d1(A.sex.men_per_100), tok: '--fill-navy' }] });

  // ---- after the draft
  var N = A.notices, RA = N.removed_after;
  VIZ.lollipop('vAfter', { label: 'After the draft: notices, hearings, claims and deletions, in lakh', axis: 'Electors, lakh', rows: [
    { name: 'Notices sent', v: N.all / 1e5, text: lk(N.all), tok: '--fill-navy', hi: true },
    { name: 'Not linked to the 2003 roll', v: N.no_mapping / 1e5, text: lk(N.no_mapping), tok: '--fill-grey' },
    { name: 'A discrepancy in the form', v: N.discrepancy / 1e5, text: lk(N.discrepancy), tok: '--fill-grey' },
    { name: 'Heard by 7 March', v: N.held_by_7_march / 1e5, text: lk(N.held_by_7_march), tok: '--fill-grey' },
    { name: 'Form 6 claims to be added', v: N.form6 / 1e5, text: lk(N.form6), tok: '--fill-teal' },
    { name: 'Form 7 objections', v: N.form7 / 1e5, text: lk(N.form7), tok: '--fill-amber' },
    { name: 'Deleted after the draft', v: RA.total / 1e5, text: lk(RA.total), tok: '--fill-red' }] });
  document.getElementById('fAfter').innerHTML = '<b>Notices went to ' + cr(N.all) + ' electors kept on the draft, ' + d1(N.per_100_draft) + ' of every 100 on it.</b> ' + cr(N.no_mapping) + ' could not be linked to the roll of 2003 and ' + cr(N.discrepancy) + ' had a discrepancy the Commission\'s software found in their form, such as a name or a parent\'s name that did not match. They were heard by ' + n(N.aeros) + ' assistant registration officers under ' + n(N.eros) + ' registration officers, about ' + n(N.per_aero) + ' notices for each assistant officer, or about ' + n(N.per_aero_day) + ' for each of them every day from 21 January to 27 March. The Hindu reported the two groups as 1.4 crore and 2.02 crore, which add to more than the 3.26 crore total, so the split the Hindustan Times reported, which adds up, is used here.';
  VIZ.lollipop('vRemoved', { label: 'The ' + lk(RA.total) + ' names deleted after the draft, by the reason given', axis: 'Names deleted, lakh', rows: [
    { name: 'Did not answer a notice', v: RA.no_response / 1e5, text: lk(RA.no_response), tok: '--fill-red', hi: true },
    { name: 'Permanently shifted', v: RA.shifted / 1e5, text: lk(RA.shifted), tok: '--fill-navy' },
    { name: 'Already enrolled', v: RA.multiple / 1e5, text: lk(RA.multiple), tok: '--fill-amber' },
    { name: 'Dead', v: RA.dead / 1e5, text: lk(RA.dead), tok: '--fill-grey' },
    { name: 'Under age or not a citizen', v: RA.underage_or_noncitizen / 1e5, text: n(RA.underage_or_noncitizen), tok: '--fill-other' }] });
  document.getElementById('fRemoved').innerHTML = '<b>' + lk(RA.no_response) + ' of the ' + lk(RA.total) + ' names deleted after the draft were deleted because the elector did not answer a notice.</b> That is ' + d1(N.no_response_per_100_notices) + ' of every 100 electors sent one. ' + n(RA.underage_or_noncitizen) + ' were deleted as under age or not citizens. The reasons are the Chief Electoral Officer\'s, as The New Indian Express reported them, and the CEO did not say how many came through notices and how many through Form 7.';

  // ---- disputes and help
  var DI = [].concat.apply([], r[3].sections.map(function (x) { return x.items; })).filter(function (i) { return /Uttar Pradesh/.test(i.state); });
  var HO = r[4].orgs.filter(function (o) { return o.state === 'Uttar Pradesh'; });
  document.getElementById('fLinks').innerHTML = '<a href="../india/disputes/?state=' + encodeURIComponent('Uttar Pradesh') + '">' + n(DI.length) + ' court cases, Form 7 complaints, protests and reported deaths in Uttar Pradesh</a> are listed with their sources on Protests and Disputes. ' +
    (HO.length ? '<a href="../help/?state=' + encodeURIComponent('Uttar Pradesh') + '">' + n(HO.length) + ' organisations that helped electors in Uttar Pradesh</a> are on Left Off the Roll? What to Do, with what the law lets an elector do.' : 'What the law lets an elector do is on <a href="../help/">Left Off the Roll? What to Do</a>.');


  SIR.table(document.getElementById('tDist'), [
    { k: 'district', label: 'District', left: true }, { k: 'roll_before', label: 'Roll Oct 2025', fmt: n }, { k: 'draft', label: 'Draft roll', fmt: n },
    { k: 'total', label: 'Left off', fmt: n }, { k: 'per_100', label: 'Per 100', fmt: d1 },
    { k: 'shifted_pct', label: 'Shifted %', fmt: d1 }, { k: 'untraceable_absent_pct', label: 'Untraceable or absent %', fmt: d1 }, { k: 'dead_pct', label: 'Dead %', fmt: d1 }, { k: 'multiple_pct', label: 'Already enrolled %', fmt: d1 }
  ], D, { sort: 'per_100' });

  var F = SIR.finder('finder', { districtPages: true, rows: D, pick: function (d) { var b = document.getElementById('vMap'); if (b.__select && idOf[d.district]) b.__select(idOf[d.district]); }, prompt: 'Find a district', placeholder: 'Type a district\'s name', key: function (d) { return SIR.slug(d.district); }, label: function (d) { return d.district + ' district'; },
    card: function (d) { return SIR.facts([['Roll of 27 October 2025', n(d.roll_before)], ['Draft roll', n(d.draft)], ['Left off', n(d.total)], ['Per 100 electors', d1(d.per_100)],
      ['Entered as dead', n(d.dead)], ['Untraceable or absent', n(d.untraceable_absent)], ['Permanently shifted', n(d.shifted)], ['Already enrolled', n(d.multiple)], ['Other', n(d.others)]]); },
    share: function (d) { return d.district + ' district, Uttar Pradesh. The SIR draft roll left off ' + n(d.total) + ' names, ' + d1(d.per_100) + ' of every 100 electors. ' + n(d.dead) + ' were entered as dead, ' + n(d.untraceable_absent) + ' as untraceable or absent and ' + n(d.shifted) + ' as permanently shifted. A reason is what the officer wrote down, and nobody checked it. These are the Chief Electoral Officer\'s counts.'; } });
  var byName = {}, idOf = {}; D.forEach(function (d) { byName[d.district] = d; });
  SIR.json('data/geo/uttarpradesh.json').then(function (geo) {
    var byId = {};
    geo.features.forEach(function (f) { var d = byName[f.properties.name]; if (d) { byId[f.properties.ac] = d; idOf[d.district] = f.properties.ac; } });
    VIZ.map('vMap', { geo: geo, label: 'Map of names left off the draft per 100 electors, by district', title: 'Left off per 100 electors',
      v: function (id) { return byId[id] ? byId[id].per_100 : null; }, name: function (id) { return byId[id] ? byId[id].district : ''; },
      pick: function (id) { if (byId[id]) F.select(byId[id]); } });
    var it = F.item[SIR.hashId()]; if (it && it.s.pick) it.s.pick(it.r);
    SIR.tools();
  });
  SIR.showFaq('up', 'main');
}).catch(SIR.fail);
