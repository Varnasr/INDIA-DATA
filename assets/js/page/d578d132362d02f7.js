Promise.all([SIR.json('data/hyderabad/summary.json'), SIR.json('data/hyderabad/parts.json')]).then(function (r) {
  var s = r[0], P = r[1], A = s.acs, t = s.totals;
  var by = function (k, desc) { return A.slice().sort(function (x, y) { return desc ? y[k] - x[k] : x[k] - y[k]; }); };
  var c = function (k) { return SIR.sum(A, function (a) { return a.counts[k]; }); };
  var list = function (arr, fn) { return arr.map(fn).join(', '); };
  var reasonTot = function (r) { return SIR.sum(A, function (a) { return a.reasons[r]; }); };
  var mal = A.filter(function (a) { return !a.linked; })[0];
  var LK = A.filter(function (a) { return a.linked; });
  var hi = by('rate', true), marg = A.slice().sort(function (x, y) { return y.e2023.deleted_over_margin - x.e2023.deleted_over_margin; });
  var over = A.filter(function (a) { return a.e2023.deleted_over_valid > 100; });
  var ms = A.map(function (a) { return a.part_correlations.muslim_share_vs_rate; });
  var ut = A.map(function (a) { return a.part_correlations.untraceable_share_vs_rate; });
  var W = A.map(function (a) { return a.within_part.hindu_minus_muslim; });
  var FM = A.map(function (a) { return a.within_part.female_minus_male; });
  var UL = LK.map(function (a) { return a.within_part.unlinked_minus_linked; });
  var idx = P.fields.indexOf('rate'), rates = P.rows.map(function (x) { return x[idx]; });
  var age = s.bands.map(function (bd, i) { return 100 * SIR.sum(A, function (a) { return a.counts.age_asd[i]; }) / SIR.sum(A, function (a) { return a.age_all[i]; }); });
  var heard = SIR.sum(A, 'hearing');
  var ruleTot = s.rules.map(function (ru) { return [ru, SIR.sum(A, function (a) { return a.rules[ru]; })]; }).sort(function (x, y) { return y[1] - x[1]; });

  document.getElementById('limits').innerHTML = [
    [L('Why a name was struck'), L('A household that moved out of the Old City is rightly marked "shifted", and the files cannot tell it apart from an elector who was at home when the officer missed them.')],
    [L('Religion together with age'), L('Religion and age are counted separately and never together, so a gap by religion may partly be a gap by age if one group is older.')],
    [L('Malakpet'), L('The Malakpet list used here holds {held} struck-off names. An independent count of the published Malakpet list gives 1,47,799, so about 5,100 names are missing from this copy.', { held: SIR.n(mal.deleted) }) + ' ' + L('For the other four constituencies the two counts agree exactly.') + ' ' + L('{name}\'s list also carries no part numbers and no 2002 linkage.', { name: mal.name }) + ' ' + L('It is read by polling-station name, which gives {stations} stations instead of parts, and {unaccounted} electors on its roll are in none of the three outcomes, compared with {others} across the other four seats together.', { stations: mal.parts, unaccounted: SIR.n(mal.unaccounted), others: SIR.n(SIR.sum(LK, 'unaccounted')) })],
    [L('The final roll'), L('These are the September lists. The Commission extended the calendar on 7 September, as Telangana Today reported, with claims to 7 October, hearings to 5 November and the final roll on 9 November. Names put back after hearings are not in these counts.')],
    [L('Five constituencies'), L('The elector-by-elector lists were compiled for these five seats only. They are a chosen group, so they cannot stand for Hyderabad as a whole. The district\'s other ten seats appear only as the state\'s totals, on the Hyderabad and Telangana page.')]
  ].map(function (q) { return '<div class="qa"><h3>' + q[0] + '</h3><p>' + q[1] + '</p></div>'; }).join('');

  var QA = [
    [L('How many names were struck off, and where?'),
     L('{deleted} of {electors} electors on the five pre-revision rolls, {rate}.', { deleted: SIR.n(t.deleted), electors: SIR.n(t.electors), rate: SIR.pct(t.rate) }) + ' ' + L('The share struck off was {list}.', { list: list(hi, function (a) { return L('{rate} in {name}', { rate: SIR.pct(a.rate), name: a.name }); }) }) + ' ' + L('The five seats are within eleven points of one another. The variation that matters is inside them (Q7).')],
    [L('What reasons did the officers record?'),
     list(s.reasons, function (re) { return re + ' ' + SIR.pct(100 * reasonTot(re) / t.deleted); }) + '. ' + L('The mix varies a lot. Untraceable or absent is {list}.', { list: list(A, function (a) { return L('{n} in {name}', { n: SIR.pct(100 * a.reasons['Untraceable/Absent'] / a.deleted), name: a.name }); }) })],
    [L('Does deletion rise with age?'),
     L('Yes, though not smoothly.') + ' ' + list(s.bands, function (bd, i) { return bd + ': ' + SIR.pct(age[i]); }) + '. ' + L('Death accounts for {deaths} deletions, a large part of the removals over age 70. The rate doubles between ages 18 to 24 and 30 to 39, when almost nobody dies, so death does not explain it all.', { deaths: SIR.n(reasonTot('Death')) })],
    [L('Were women struck off more often than men?'),
     L('Women {women}, men {men}.', { women: SIR.pct(100 * c('f_asd') / c('f_all')), men: SIR.pct(100 * c('m_asd') / c('m_all')) }) + ' ' + L('Within parts the gap is {gap_min} to {gap_max} points and changes sign between constituencies.', { gap_min: SIR.d(Math.min.apply(null, FM.map(function (w) { return w.diff_pp; })), 1), gap_max: SIR.d(Math.max.apply(null, FM.map(function (w) { return w.diff_pp; })), 1) })],
    [L('Were Muslim-name electors struck off more often?'),
     L('No, less often.') + ' ' + L('Hindu-name electors {hindu}, Muslim-name electors {muslim}.', { hindu: SIR.pct(100 * c('hin_asd') / c('hin_all')), muslim: SIR.pct(100 * c('mus_asd') / c('mus_all')) }) + ' ' + L('Inside the same part Hindu-name electors were struck off {gap_min} to {gap_max} points more, in {higher} of {parts} comparable parts.', { gap_min: SIR.d(Math.min.apply(null, W.map(function (w) { return w.diff_pp; })), 1), gap_max: SIR.d(Math.max.apply(null, W.map(function (w) { return w.diff_pp; })), 1), higher: SIR.sum(W, 'a_higher'), parts: SIR.sum(W, 'parts') }) + ' ' + L('The files cannot rule out that this comes from age, or from people who did move out (see the limits above).')],
    [L('How much did the 2002 link matter?'),
     L('More than any other attribute in the files.') + ' ' + L('Unlinked electors were struck off {list}, within the same part, and in {higher} of {parts} parts.', { list: list(LK, function (a) { return L('{points} points more in {name}', { points: SIR.d(a.within_part.unlinked_minus_linked.diff_pp, 1), name: a.name }); }), higher: SIR.sum(UL, 'a_higher'), parts: SIR.sum(UL, 'parts') }) + ' ' + L('Linked share of the roll: {list}.', { list: list(LK, function (a) { return SIR.pct(a.linked_share_roll) + ' (' + a.name + ')'; }) }) + ' ' + L('Not measurable for {name}.', { name: mal.name })],
    [L('Were deletions spread evenly across parts?'),
     L('No.') + ' ' + L('Part rates run from {low}% to {high}%, and {over} parts lost more than 60% of their roll ({where}).', { low: SIR.d(Math.min.apply(null, rates), 0), high: SIR.d(Math.max.apply(null, rates), 0), over: SIR.sum(A, 'parts_over_60'), where: list(A.filter(function (a) { return a.parts_over_60; }), function (a) { return L('{n} in {name}', { n: a.parts_over_60, name: a.name }); }) }) + ' ' + L('The middle half of parts in each constituency, from Q1 to Q3: {list}.', { list: list(A, function (a) { return L('{name} {q1} to {q3}', { name: a.name, q1: a.part_rate_quartiles[1], q3: a.part_rate_quartiles[3] }); }) }) + ' ' + L('<a href="../parts/">Parts</a> lists the outliers.')],
    [L('Did parts with more Muslim electors lose more names?'),
     L('Fewer.') + ' ' + L('Across parts the Muslim-name share and the deletion rate have rank correlations of {r_from} to {r_to}, negative in all five constituencies.', { r_from: SIR.d(Math.max.apply(null, ms), 2), r_to: SIR.d(Math.min.apply(null, ms), 2) }) + ' ' + L('Together with Q5, the comparison across parts and the comparison between people point the same way.')],
    [L('Does "untraceable" cluster where deletion is heaviest?'),
     L('Barely.') + ' ' + L('The rank correlation between a part\'s untraceable share and its deletion rate runs from {r_from} to {r_to}, and the share of electors aged 80 and over does no better.', { r_from: SIR.d(Math.min.apply(null, ut), 2), r_to: SIR.d(Math.max.apply(null, ut), 2) }) + ' ' + L('The one part characteristic that moves with the rate in every constituency is the Muslim-name share (Q8).')],
    [L('Who was summoned, and why?'),
     L('{summoned} electors kept on the draft roll were summoned, {share} of the pre-revision roll.', { summoned: SIR.n(heard), share: SIR.pct(100 * heard / t.electors) }) + ' ' + L('The flags, rule by rule, were {list}.', { list: list(ruleTot, function (x) { return x[0] + ' ' + SIR.n(x[1]); }) }) + ' ' + L('See <a href="../hearings/">hearings</a>.')],
    [L('Could the hearings be held as scheduled?'),
     L('The typical slot listed {list}.', { list: list(A, function (a) { return L('{n} cases in {name}', { n: SIR.d(a.median_slot, 0), name: a.name }); }) }) + ' ' + L('The heaviest single slot listed {list}.', { list: list(A, function (a) { return L('{n} cases in {name}', { n: SIR.n(a.max_slot), name: a.name }); }) }) + ' ' + L('The lists do not record how long a slot lasted.')],
    [L('How do deletions compare with the 2023 result?'),
     L('In every seat the names struck off exceed the 2023 winning margin, by {list}.', { list: list(marg, function (a) { return L('{times} times in {name}', { name: a.name, times: SIR.d(a.e2023.deleted_over_margin, 1) }); }) }) + ' ' + L('In {names} they exceed the total valid votes cast in 2023.', { names: over.map(function (a) { return a.name; }).join(L(' and ')) }) + ' ' + L('Yakutpura was decided by {margin} votes.', { margin: SIR.n(A.filter(function (a) { return a.name === 'Yakutpura'; })[0].e2023.margin) }) + ' ' + L('None of this says whom the removed would have voted for, because the roll records nothing of the kind.')],
    [L('Are the files internally consistent?'),
     L('Part counts sum exactly to the constituency totals for all five.') + ' ' + L('Electors in none of the three fates number {list}.', { list: list(A, function (a) { return L('{n} in {name}', { n: SIR.n(a.unaccounted), name: a.name }); }) }) + ' ' + L('Malakpet\'s {n} is why its figures should be read beside the state\'s own count for the seat, on the <a href="../telangana/">Hyderabad and Telangana</a> page.', { n: SIR.n(mal.unaccounted) })]
  ];
  document.getElementById('qas').innerHTML = QA.map(function (q, i) {
    return '<div class="qa"><h3>' + L('Q{n}. {question}', { n: i + 1, question: q[0] }) + '</h3><p>' + q[1] + '</p></div>';
  }).join('');
}).catch(SIR.fail);
