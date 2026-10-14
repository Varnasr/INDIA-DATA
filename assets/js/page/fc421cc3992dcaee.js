SIR.json('data/assam/summary.json').then(function (d) {
  var S = d.state, T = d.tribunals, X = d.detention, N = d.nrc, n = SIR.n, lk = function (x) { return SIR.lk(x, 2); }, d1 = function (v) { return SIR.d(v, 1); };
  var A = T.assembly_2026;
  // the research notes are written in clauses; the page shows them as sentences
  var cap = function (t) { return t.charAt(0).toUpperCase() + t.slice(1); };
  var sent = function (t) { return t ? t.split('; ').map(cap).join('. ').replace(/([^.])$/, '$1.') : ''; };

  document.getElementById('kpis').innerHTML = [
    [lk(S.flagged), 'names flagged for deletion with the draft'],
    [n(S.d_voters_draft), 'D-voters carried onto the draft unchanged'],
    [n(N.left_out), 'people left out of the 2019 NRC'],
    [n(X.inmates), 'people held in six detention centres, 28 November 2019']
  ].map(function (k) { return '<div><b>' + k[0] + '</b><span>' + k[1] + '</span></div>'; }).join('');

  SIR.table('tRules', [{ h: 'Rule' }, { h: 'Assam, Special Revision' }, { h: 'Para' }, { h: 'SIR states' }],
    d.rules.map(function (r) { return [SIR.esc(cap(r.aspect)), SIR.esc(sent(r.assam)), SIR.esc(r.para), SIR.esc(sent(r.sir || ''))]; }));
  document.getElementById('fRules').innerHTML = '<b>In Assam no existing elector filled a form or showed a document to stay on the roll.</b> Booth officers checked a printed list of the electors already on it, and names came off through the ordinary forms, Form 7 for an objection and Form 8 for an elector who has moved. The order makes no link to the 2005 roll or to any earlier one, and says nothing about the NRC.';

  var jan = S.roll_jan2025;
  VIZ.waterfall('vWater', { label: 'Assam: the roll of January 2025, the draft of 27 December 2025 and the final roll of 10 February 2026', from: Math.floor(S.final * 0.96 / 1e6) * 1e6, steps: [
    { name: 'Roll of January 2025', v: jan, kind: 'total' }, { name: 'Net change to the draft', v: S.draft_vs_jan, kind: 'up' }, { name: 'Draft roll', v: S.draft, kind: 'total' },
    { name: 'Net change to the final roll', v: S.draft - S.final, kind: 'down' }, { name: 'Final roll', v: S.final, kind: 'total' }] });
  document.getElementById('fWater').innerHTML = '<b>The draft roll held ' + n(S.draft_vs_jan) + ' more names than the roll of January 2025, and the final roll ' + n(S.draft - S.final) + ' fewer than the draft.</b> The final roll of ' + (S.final / 1e7).toFixed(2) + ' crore electors is ' + n(S.final_vs_jan) + ' larger than the roll of January 2025. Women are ' + SIR.pct(S.women_final_pct, 2) + ' of it. The January 2025 figure is the Chief Electoral Officer\'s as reported in the press, and the Commission published no count of the names added and removed in between, only the totals.';

  var Z = d.seats, AC = d.acs;
  var DS = []; AC.forEach(function (a) { if (DS.indexOf(a.district) < 0) DS.push(a.district); });
  var dfall = function (k) { var r = AC.filter(function (a) { return a.district === k; }); var dr = r.reduce(function (t, a) { return t + a.draft; }, 0), fi = r.reduce(function (t, a) { return t + a.final; }, 0); return 1000 * (dr - fi) / dr; };
  DS.sort(function (a, b) { return dfall(b) - dfall(a); });
  VIZ.strip('vSeat', { label: 'Fall in the roll from the draft to the final roll, per 1,000 on the draft, every constituency, by district', axis: 'Fall from the draft to the final roll, per 1,000 on the draft (below zero, the roll rose)', r: 4,
    rows: DS.map(function (k) { return { name: k, tok: '--fill-navy',
      points: AC.filter(function (a) { return a.district === k; }).map(function (a) { return { v: a.fall_per_1000, label: a.name + ': ' + (a.fall_per_1000 < 0 ? 'rose ' : 'fell ') + d1(Math.abs(a.fall_per_1000)) + ' per 1,000' }; }) }; }) });
  var srt = AC.slice().sort(function (a, b) { return b.fall_per_1000 - a.fall_per_1000; }), hi = srt[0], lo = srt[srt.length - 1];
  document.getElementById('fSeat').innerHTML = '<b>Between the draft and the final roll, the roll fell in ' + Z.fell + ' of Assam\'s 126 constituencies and rose in ' + Z.rose + '.</b> It fell most in ' + hi.name + ' (' + hi.district + '), by ' + d1(hi.fall_per_1000) + ' for every 1,000 on the draft, and rose most in ' + lo.name + ' (' + lo.district + '), by ' + d1(-lo.fall_per_1000) + '. Every constituency\'s draft held more names than its final roll of February 2024, which is ' + n(Z.draft - Z.roll_2024) + ' more across the state.';
  document.getElementById('fSeatW').innerHTML = '<b>Women were ' + SIR.pct(Z.women_fall_pct) + ' of the net fall from the draft to the final roll, against ' + SIR.pct(Z.women_draft_pct) + ' of the draft.</b> Of the ' + Z.fell + ' constituencies whose roll fell, women\'s share of the fall was above their share of the draft in ' + Z.women_over_in + '. The tables give the net change only, so they cannot say whether more women were removed or fewer were added.';
  SIR.table('tSeat', [{ h: 'No.' }, { h: 'Constituency' }, { h: 'District' }, { h: 'Roll, Feb 2024' }, { h: 'Draft' }, { h: 'Final' }, { h: 'Fall per 1,000 on the draft' }],
    AC.map(function (a) { return [a.ac, SIR.esc(a.name) + (a.reserved ? ' (' + a.reserved + ')' : ''), SIR.esc(a.district), n(a.roll_2024), n(a.draft), n(a.final), d1(a.fall_per_1000)]; }));

  // the finder: every constituency and district, each with a page of its own
  SIR.json('data/assam/districts.json').then(function (D) {
    var per = function (x) { return 1000 * (x.draft - x.final) / x.draft; };
    var move = function (x) { return x.final <= x.draft ? 'Fell by ' + n(x.draft - x.final) + ', ' + d1(per(x)) + ' per 1,000 on the draft' : 'Rose by ' + n(x.final - x.draft) + ', ' + d1(-per(x)) + ' per 1,000 on the draft'; };
    var say = function (x, nm) { return nm + ', Assam. From the draft to the final roll of the Special Revision, the roll ' + (x.final <= x.draft ? 'fell by ' + n(x.draft - x.final) : 'rose by ' + n(x.final - x.draft)) + ', names added less names removed. These are counts from the Chief Electoral Officer\'s tables.'; };
    var seatsOf = function (d) { return AC.filter(function (a) { return a.district === d.district; }); };
    var DSET = { rows: D, key: function (d) { return SIR.slug(d.district); }, label: function (d) { return d.district + ' district'; },
      card: function (d) { return SIR.facts([['Draft roll', n(d.draft)], ['Final roll', n(d.final)], ['Change from the draft', move(d)], ['Constituencies', n(d.acs)]]) + '<p class="note">Its constituencies</p>' + SIR.goList(seatsOf(d), function (a) { return 'ac-' + a.ac; }, function (a) { return a.ac + '. ' + a.name; }); },
      share: function (d) { return say(d, d.district + ' district'); } };
    SIR.finder('finder', { seatPages: true, districtPages: true, rows: AC, more: [DSET], prompt: 'Find a constituency or district', placeholder: 'Type a name, a number or a district',
      key: function (a) { return 'ac-' + a.ac; }, label: function (a) { return a.ac + '. ' + a.name + ' (' + a.district + ')'; },
      card: function (a) { return SIR.facts([['Roll, February 2024', n(a.roll_2024)], ['Draft roll', n(a.draft)], ['Final roll', n(a.final)], ['Change from the draft', move(a)]]); },
      share: function (a) { return say(a, a.name); } });
  });

  VIZ.lollipop('vFlag', { label: 'Names flagged for deletion with the draft roll, by the reason entered', axis: 'Lakh',
    rows: [['Shifted', S.flagged_shifted], ['Dead', S.flagged_dead], ['Entered more than once, or entries alike', S.flagged_multiple]].map(function (x) { return { name: x[0], v: x[1] / 1e5, text: lk(x[1]), tok: '--fill-navy', hi: true }; }) });
  document.getElementById('nFlag').textContent = 'The Chief Electoral Officer gave ' + n(S.flagged) + ' names under these three reasons, ' + d1(S.flagged_per_100_draft) + ' for every 100 on the draft. Most reports called them names identified or flagged for deletion. No figure from the Chief Electoral Officer says how many of them were off the published draft, and the draft is larger than the roll of January 2025, so this page calls them flagged. The count reached us through the press, and no split by district, constituency or sex was found.';

  VIZ.lollipop('vDv', { label: 'D-voters on Assam\'s roll, from 1997 to July 2026', axis: 'Thousand',
    rows: d.d_voters.map(function (r) { return { name: (r.as_of === '1997' ? '1997' : r.as_of === '2019-10' ? 'October 2019' : r.as_of === '2025-12-27' ? 'Draft roll, December 2025' : 'July 2026') + (r.primary ? '' : ' (press)'), v: r.value / 1e3, text: n(r.value), tok: r.primary ? '--fill-red' : '--fill-grey', hi: true }; }) });
  var w19 = d.d_voters.filter(function (r) { return r.women; })[0];
  document.getElementById('nDv').textContent = 'The Ministry of Home Affairs told the Lok Sabha that Assam had ' + n(w19.value) + ' D-voters in October 2019, ' + n(w19.women) + ' of them women, ' + SIR.pct(100 * w19.women / w19.value) + '. The other three figures are the Chief Electoral Officer\'s and the Chief Minister\'s, as reported in the press. The 1997 figure is the number when the category was first used.';

  VIZ.lollipop('vFt', { label: 'Cases decided by the Foreigners Tribunals each year, 2016 to 2020', axis: 'Thousand',
    rows: T.disposed.map(function (r) { return { name: String(r.year), v: r.value / 1e3, text: n(r.value), tok: '--fill-navy', hi: true }; }) });
  var o19 = T.to_oct2019;
  document.getElementById('nFt').textContent = 'To October 2019, ' + n(o19.referred) + ' matters had been referred to the tribunals. ' + n(o19.foreigners) + ' people had been declared foreigners and ' + n(o19.indian) + ' declared Indian. ' + n(T.pending_dec2020) + ' cases were pending at the end of 2020, before ' + T.tribunals_2021 + ' tribunals. All of these are the Ministry of Home Affairs\' answers to the Lok Sabha.';

  VIZ.lollipop('vFt26', { label: 'D-voter cases referred to the tribunals, and what the Assembly was told became of them, July 2026 (press)', axis: 'Thousand',
    rows: [['Referred since 1997', A.d_voter_cases_referred_to_FTs_cumulative, '--fill-grey'], ['Declared Indian', A.d_voters_declared_indian_by_FTs, '--fill-navy'], ['Declared foreigners', A.d_voters_declared_foreigners_by_FTs, '--fill-red'],
           ['Decided, outcome not given in the report', A.d_voter_disposals_not_described, '--fill-grey'], ['Not yet decided', A.d_voter_cases_pending_implied, '--fill-grey']].map(function (x) { return { name: x[0], v: x[2] ? x[1] / 1e3 : 0, text: n(x[1]), tok: x[2], hi: true }; }) });
  document.getElementById('nFt26').textContent = 'These figures are from the Chief Minister\'s reply in the Assam Assembly of 13 July 2026, as The Assam Tribune reported it. Of ' + n(A.d_voter_cases_disposed_cumulative) + ' D-voter cases decided, the report gives an outcome for ' + n(A.d_voters_declared_foreigners_by_FTs + A.d_voters_declared_indian_by_FTs) + '. The pending figure is the cases referred less the cases decided. The same reply gave ' + n(A.border_police_cases_declared_foreigners) + ' people declared foreigners from Border Police cases and ' + n(A.declared_foreigners_expelled_total) + ' declared foreigners expelled in all. The Wire reported from the same session that ' + n(T.sent_to_bangladesh_2024_26) + ' people were sent to Bangladesh between July 2024 and June 2026, ' + n(T.declared_sent_to_bangladesh_2024_26) + ' of them declared foreigners.';

  VIZ.dots('vDet', { label: 'Capacity of each detention centre in March 2020, and the people held in it on 28 November 2019', axis: 'People',
    cats: X.centres.map(function (c) { return c.centre; }),
    series: [{ name: 'Capacity, March 2020', col: '--fill-grey', vals: X.centres.map(function (c) { return c.capacity; }) },
             { name: 'Men held, November 2019', col: '--fill-navy', vals: X.centres.map(function (c) { return c.men; }) },
             { name: 'Women held, November 2019', col: '--fill-red', vals: X.centres.map(function (c) { return c.women; }) }] });
  var kk = X.centres.filter(function (c) { return c.centre === 'Kokrajhar'; })[0];
  document.getElementById('nDet').textContent = 'The six centres held ' + n(X.men) + ' men and ' + n(X.women) + ' women on 28 November 2019, in space for ' + n(X.capacity) + '. Men and women are kept apart, and Kokrajhar held ' + kk.women + ' of the women. A seventh centre at Matia in Goalpara, for ' + n(X.matia_capacity) + ' people, was under construction in March 2020.';
  document.getElementById('fDet').innerHTML = '<b>' + X.died + ' people held in Assam\'s detention centres died in hospital between 1 March 2019 and 29 February 2020.</b> At the end of 2019, ' + X.over_3_years_declared + ' declared foreigners and ' + X.over_3_years_convicted + ' convicted foreigners had been held for more than three years, and ' + X.released_after_3_years + ' had been released after three years under the Supreme Court\'s order of 10 May 2019. ' + X.detained_2019 + ' declared foreigners were detained in 2019. Every figure here is from the Ministry of Home Affairs\' answers to the Lok Sabha, which put them on the information of the Assam government.';

  VIZ.lollipop('vNrc', { label: 'Assam\'s NRC, the lists of 31 August 2019', axis: 'Lakh',
    rows: [['Found eligible', N.included], ['Left out', N.left_out]].map(function (x, i) { return { name: x[0], v: x[1] / 1e5, text: lk(x[1]), tok: i ? '--fill-red' : '--fill-grey', hi: true }; }) });
  document.getElementById('nNrc').textContent = n(N.left_out) + ' of the ' + n(N.applied) + ' people who applied were left out of the NRC, ' + SIR.pct(N.left_out_pct, 1) + '. The decision on D-voters and their descendants was kept on hold on the Supreme Court\'s direction. The Ministry told the Lok Sabha in March and December 2021 that no rejection orders had yet been issued, so no one left out had yet appealed to a tribunal. The count of applicants is the State Coordinator\'s, as reported in the press, and equals those found eligible and those left out added together.';

  SIR.table('tSched', [{ h: 'Step' }, { h: 'What happened' }, { h: 'From' }, { h: 'To' }],
    d.schedule.map(function (r) { return [r.step, SIR.esc(r.activity), r.start || '', r.end || '']; }));
  SIR.showFaq('as', 'main');
}).catch(SIR.fail);
