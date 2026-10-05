/* Questions and answers for the Hyderabad pages. The FAQ tab shows them all;
   each page shows those tagged with its key (dash, explorer, people, parts,
   hearings, telangana, method). */
(function () {
  var P;
  SIR.faq('hyd', 'hyderabad/faq/', function () {
    return P || (P = Promise.all([SIR.json('data/hyderabad/summary.json'), SIR.json('data/hyderabad/telangana.json'), SIR.json('data/hyderabad/impact.json'), SIR.json('data/hyderabad/parts.json')]).then(function (r) {
  var s = r[0], TG = r[1], HI = r[2].seats;
  var A = s.acs, t = s.totals, sum = function (f) { return SIR.sum(A, f); };
  var R = function (r) { return 100 * sum(function (a) { return a.reasons[r]; }) / t.deleted; };
  var W = A.map(function (a) { return a.within_part.hindu_minus_muslim; }), LK = A.filter(function (a) { return a.linked; });
  var ul = LK.map(function (a) { return a.within_part.unlinked_minus_linked.diff_pp; });
  var age = s.bands.map(function (b, i) { return 100 * sum(function (a) { return a.counts.age_asd[i]; }) / sum(function (a) { return a.age_all[i]; }); });
  var valid = A.filter(function (a) { return a.e2023.deleted_over_valid > 100; }).map(function (a) { return a.name; });
  var yak = A.filter(function (a) { return a.name === 'Yakutpura'; })[0], mal = A.filter(function (a) { return a.name === 'Malakpet'; })[0];
  var heavy = A.slice().sort(function (a, b) { return b.max_slot - a.max_slot; })[0];
  var QA = [
    [L('Is the Old City an outlier?'),
     L('No. On the state\'s draft figures the five Old City seats lost {oc} of their roll, and Hyderabad\'s other ten seats lost {oh}. The draft left off {h} across Hyderabad district and {r} in the rest of Telangana. The removals are heavy across the whole city. <a href="../telangana/">Hyderabad and Telangana</a>.', { oc: SIR.pct(TG.old_city.rate), oh: SIR.pct(TG.other_hyderabad.rate), h: SIR.pct(TG.hyderabad.rate), r: SIR.pct(TG.rest_of_state.rate) })],
    [L('Were most of those struck off simply people who had moved away?'),
     L('The commonest recorded reason is "permanently shifted", at {shifted} of removals, and many people do move in and out of the Old City. But {untraceable} were entered as "untraceable or absent", {death} as dead and {enrolled} as enrolled elsewhere.', { shifted: SIR.pct(R('Permanently Shifted')), untraceable: SIR.pct(R('Untraceable/Absent')), death: SIR.pct(R('Death')), enrolled: SIR.pct(R('Already enrolled')) }) + ' ' + L('Each is what an officer wrote down, and nobody has checked it.') + ' ' + L('The untraceable entries in particular record only that an officer did not find someone.')],
    [L('Was the revision aimed at Muslim electors?'),
     L('The lists do not show that.') + ' ' + L('Inside the same polling part, Hindu-name electors were struck off more often than Muslim-name electors, by {gap_min} to {gap_max} points.', { gap_min: SIR.d(Math.min.apply(null, W.map(function (w) { return w.diff_pp; })), 0), gap_max: SIR.d(Math.max.apply(null, W.map(function (w) { return w.diff_pp; })), 0) }) + ' ' + L('What the lists do show is who bore the removals. They fell hardest on the old and on those who could not be traced to the 2002 roll. <a href="../people/">Age, sex, religion, 2002</a>.')],
    [L('Why does the 2002 roll matter so much?'),
     L('The revision asks each elector to show a link to the 2002 intensive revision, through their own name or a parent\'s.') + ' ' + L('Where the lists record it, electors with no such link were struck off {gap_min} to {gap_max} points more often than linked electors in the same part.', { gap_min: SIR.d(Math.min.apply(null, ul), 0), gap_max: SIR.d(Math.max.apply(null, ul), 0) }) + ' ' + L('Anyone who moved into the city after 2002, or whose family name is spelt differently on the old roll, starts at a disadvantage.')],
    [L('Why are the old struck off so often?'),
     L('{old} of electors aged 80 and over were struck off, against {young} of those aged 18 to 24.', { old: SIR.pct(age[7]), young: SIR.pct(age[0]) }) + ' ' + L('Some of that is death.') + ' ' + L('The rest is electors least able to answer a visit, attend a hearing or produce papers.')],
    [L('Could hearings be held properly?'),
     L('{summoned} electors kept on the draft roll were summoned.', { summoned: SIR.n(t.hearing) }) + ' ' + L('The heaviest single slot listed {cases} cases, in {name}.', { cases: SIR.n(heavy.max_slot), name: heavy.name }) + ' ' + L('The lists do not record how long a slot lasted. <a href="../hearings/">Hearings</a>.')],
    [L('Did this change an election result?'),
     L('No election has been held on the revised roll.') + ' ' + L('What can be measured is the scale. Every one of the five constituencies lost more names than its 2023 winning margin, and in {names} more names were struck off than there were valid votes in 2023.', { names: valid.join(L(' and ')) }) + ' ' + L('Yakutpura was won by {margin} votes and lost {deleted} names.', { margin: SIR.n(yak.e2023.margin), deleted: SIR.n(yak.deleted) }) + ' ' + L('Measured against the 2023 margins, only Yakutpura is close. Its runner-up would need {yak} of the removed electors who would vote, at 2023 turnout, to overturn a margin of {m}. In {mid} the runner-up would need {r1} to {r2}, and in {none} no split of the removed would be enough.', {
       yak: SIR.pct(HI.filter(function (x) { return x.name === 'Yakutpura'; })[0].breakeven), m: SIR.n(yak.e2023.margin),
       mid: HI.filter(function (x) { return x.breakeven >= 55 && x.breakeven <= 100; }).map(function (x) { return x.name; }).join(L(' and ')),
       r1: SIR.pct(Math.min.apply(null, HI.filter(function (x) { return x.breakeven >= 55 && x.breakeven <= 100; }).map(function (x) { return x.breakeven; }))),
       r2: SIR.pct(Math.max.apply(null, HI.filter(function (x) { return x.breakeven >= 55 && x.breakeven <= 100; }).map(function (x) { return x.breakeven; }))),
       none: HI.filter(function (x) { return x.breakeven > 100; }).map(function (x) { return x.name; }).join(L(' and ')) }) + ' ' + L('Muslim names are a smaller share of those struck off than of the roll in all five seats, by {lo} to {hi} points, so where Muslim electors lean to AIMIM, the removals take fewer of its voters than of its opponents\'.', {
       lo: SIR.d(Math.min.apply(null, HI.map(function (x) { return x.muslim_share_roll - x.muslim_share_removed; })), 1), hi: SIR.d(Math.max.apply(null, HI.map(function (x) { return x.muslim_share_roll - x.muslim_share_removed; })), 1) })],
    [L('How reliable are the lists?'),
     L('For Charminar, Yakutpura, Chandrayangutta and Bahadurpura, the counts of names struck off, the recorded reasons and women\'s share all agree exactly with a separate count of the same lists.') + ' ' + L('The Malakpet list used here is incomplete. It holds {held} names against 1,47,799 in an independent count of the published list, and it carries no part numbers or 2002 link.', { held: SIR.n(mal.deleted) })],
    [L('Why only five constituencies?'),
     L('The elector-by-elector lists were compiled for these five seats only. Hyderabad district\'s other ten seats, including Nampally and Karwan, appear only as the state\'s totals, on the Hyderabad and Telangana page. The figures here describe these five and no others.')],
    [L('Why are no names published?'),
     L('The analysis looks at the revision as a whole. Only counts are published, and no name, EPIC number or address appears anywhere on these pages.')]
  ];
  var TAGS = [['telangana', 'dash'], ['dash', 'explorer'], ['people', 'dash', 'parts'], ['people'], ['people'], ['hearings', 'dash'], ['dash', 'telangana'],
    ['method', 'explorer'], ['method', 'telangana', 'dash'], ['method', 'explorer']];
  QA.forEach(function (q, i) { q.push(TAGS[i]); });
  var AND = function (a) { return a.length < 2 ? a.join('') : a.slice(0, -1).join(', ') + L(' and ') + a[a.length - 1]; };
  var PQ = A.map(function (a) { return a.part_rate_quartiles; }), plo = Math.min.apply(null, PQ.map(function (q) { return q[0]; })), phi = Math.max.apply(null, PQ.map(function (q) { return q[4]; }));
  var over60 = SIR.sum(A, 'parts_over_60'), MS = A.map(function (a) { return a.part_correlations.muslim_share_vs_rate; });
  var rules = s.rules.map(function (k) { return [k, SIR.sum(A, function (a) { return a.rules[k]; })]; }), rAll = SIR.sum(rules, function (x) { return x[1]; });
  var medSlot = SIR.median(A.map(function (a) { return a.median_slot; }));
  QA.push([L('How much do polling parts differ?'),
    L('A great deal. Part rates run from {lo}% to {hi}%, and {over} parts lost more than 60% of their roll. The table on this page sets each part against the typical part in its own constituency.', { lo: SIR.d(plo, 1), hi: SIR.d(phi, 1), over: over60 }), ['parts', 'explorer']]);
  if (Math.max.apply(null, MS) < 0) QA.push([L('Were parts with more Muslim electors hit harder?'),
    L('No. In every constituency, parts with a larger share of Muslim names on the roll had lower removal rates (rank correlations {a} to {b}).', { a: SIR.d(Math.min.apply(null, MS), 2), b: SIR.d(Math.max.apply(null, MS), 2) }), ['parts']]);
  QA.push([L('On what grounds were electors summoned to a hearing?'),
    L('Under seven Election Commission rules. The commonest were {r1} ({p1}), {r2} ({p2}) and {r3} ({p3}). A flag says the paperwork did not line up, and says nothing about whether the elector was entitled to vote.', {
      r1: rules[0][0], p1: SIR.pct(100 * rules[0][1] / rAll), r2: rules[1][0], p2: SIR.pct(100 * rules[1][1] / rAll), r3: rules[2][0], p3: SIR.pct(100 * rules[2][1] / rAll) }), ['hearings']]);
  QA.push([L('Can I look up my own name here?'),
    L('No. Only counts are published on this site. To check your own entry, use the Election Commission\'s voter search.'), ['explorer', 'dash']]);
  QA.push([L('Why does Malakpet look different in the explorer?'),
    L('Its list has no part numbers and no link to the 2002 roll. It is read by polling-station name instead, {n} stations, and it is given no linked or unlinked rate.', { n: mal.parts }), ['explorer', 'method']]);
  QA.push([L('Where do the Telangana figures come from?'),
    L('From the state\'s own draft-roll totals for its {d} districts and for the 15 seats of Hyderabad district. They give the roll before the revision and the names left off the draft, and nothing about who was removed or why.', { d: TG.districts.length }), ['telangana', 'method']]);

  // ---- "In short" for each page.
  var FR = 100 * sum(function (a) { return a.counts.f_asd; }) / sum(function (a) { return a.counts.f_all; }), MR = 100 * sum(function (a) { return a.counts.m_asd; }) / sum(function (a) { return a.counts.m_all; });
  var wmin = Math.min.apply(null, W.map(function (w) { return w.diff_pp; })), wmax = Math.max.apply(null, W.map(function (w) { return w.diff_pp; }));
  var within = wmin > 0 ? L('The removals hit every community. Inside the same polling part, Hindu-name electors were struck off more often than Muslim-name electors, by {a} to {b} points.', { a: SIR.d(wmin, 1), b: SIR.d(wmax, 1) }) : null;
  var link = ul.length ? L('Electors the lists could not link to the 2002 roll were struck off {a} to {b} points more often than those they could.', { a: SIR.d(Math.min.apply(null, ul), 1), b: SIR.d(Math.max.apply(null, ul), 1) }) : null;
  var oldy = L('Electors aged 80 and over were struck off most often, {old} of them against {young} of those aged 18 to 24.', { old: SIR.pct(age[7]), young: SIR.pct(age[0]) });
  var OC = TG.old_city, OH = TG.other_hyderabad, TR = TG.rest_of_state, TS = TG.seats;
  var ocMax = Math.max.apply(null, TS.filter(function (x) { return x.old_city; }).map(function (x) { return x.rate; }));
  var NOTE_REASON = L('A reason on the list is what the officer wrote down, and nobody checked it.');
  var NOTE_NAMES = L('Religion is guessed from names. Age and sex come from the roll.');
  var head = [
    L('Four in ten electors in five Old City constituencies were struck off the roll, {del} people, {rate} of the {el} on it.', { del: SIR.lakh(t.deleted), rate: SIR.pct(t.rate), el: SIR.lakh(t.electors) }),
    L('Another {h} electors who stayed on the draft roll were summoned to a hearing to prove they were entitled to vote.', { h: SIR.lakh(t.hearing) }),
    L('Every one of the five lost more names than its 2023 winning margin. {seat}, won by {margin} votes, lost {lost}.', { seat: yak.name, margin: SIR.n(yak.e2023.margin), lost: SIR.n(yak.deleted) }),
    TG.hyderabad.rate > 2 * TR.rate ? L('Across Hyderabad the revision struck off people at more than twice the rate of the rest of Telangana, {h} of the roll against {r}.', { h: SIR.pct(TG.hyderabad.rate), r: SIR.pct(TR.rate) })
      : L('Across Hyderabad the revision struck off {h} of the roll, against {r} in the rest of Telangana.', { h: SIR.pct(TG.hyderabad.rate), r: SIR.pct(TR.rate) })
  ];
  var SHORT = {
    dash: [head, NOTE_REASON], faq: [head, NOTE_REASON],
    explorer: [[
      L('The five constituencies are made up of {n} polling parts, and the explorer shows each one, with how many were struck off, why, and who.', { n: SIR.n(t.parts) }),
      L('Part rates run from {lo}% to {hi}%.', { lo: SIR.d(plo, 1), hi: SIR.d(phi, 1) }),
      L('Choose a constituency and then a part to see its own figures. Each part has its own link, which can be shared.')],
      L('Malakpet\'s list has no part numbers, so its figures are grouped by polling station instead.')],
    people: [[
      oldy, link, within,
      Math.abs(FR - MR) < 2 ? L('Women and men were struck off at close to the same rate, {f} against {m}.', { f: SIR.pct(FR), m: SIR.pct(MR) })
        : L('Women were struck off at {f} and men at {m}.', { f: SIR.pct(FR), m: SIR.pct(MR) })], NOTE_NAMES],
    parts: [[
      L('The five constituencies have {n} polling parts, and the share struck off runs from {lo}% in one to {hi}% in another.', { n: SIR.n(t.parts), lo: SIR.d(plo, 1), hi: SIR.d(phi, 1) }),
      L('In {over} parts more than 60% of the roll was struck off.', { over: over60 }),
      Math.max.apply(null, MS) < 0 ? L('In every constituency, parts with more Muslim names on the roll lost a smaller share.') : null], NOTE_NAMES],
    hearings: [[
      L('{h} electors who stayed on the draft roll were summoned to a hearing.', { h: SIR.lakh(t.hearing) }),
      L('The commonest ground was that the elector could not be traced to the last intensive revision, {p} of flags. Names that did not match came next.', { p: SIR.pct(100 * rules[0][1] / rAll) }),
      L('The busiest sitting listed {max} cases, in {name}, and a typical one listed {med}.', { max: SIR.n(heavy.max_slot), name: heavy.name, med: SIR.n(medSlot) })],
      L('The lists record how many cases each sitting listed, and nothing about how long it lasted.')],
    telangana: [[
      L('On the state\'s own figures, four in ten Old City electors were struck off, {oc}, and Hyderabad\'s other ten seats lost even more, {oh}.', { oc: SIR.pct(OC.rate), oh: SIR.pct(OH.rate) }),
      L('{n} seats outside the Old City lost more than any Old City seat.', { n: TS.filter(function (x) { return !x.old_city && x.rate > ocMax; }).length }),
      TG.hyderabad.rate > 2 * TR.rate ? L('Across Hyderabad district the revision struck off {h} of the roll, more than twice the rate of the rest of Telangana, {r}.', { h: SIR.pct(TG.hyderabad.rate), r: SIR.pct(TR.rate) })
        : L('Across Hyderabad district the revision struck off {h} of the roll, against {r} in the rest of Telangana.', { h: SIR.pct(TG.hyderabad.rate), r: SIR.pct(TR.rate) })],
      L('These are totals only. The state has not published who was removed, or why, seat by seat.')],
    method: [[
      L('The figures come from the lists of names struck off and of electors summoned to hearings in the five constituencies, and from the state\'s draft-roll totals.'),
      L('The lists cover every elector on the roll before the revision, so each group has its own rate.'),
      L('Religion is guessed from names. Age and sex come from the roll.'),
      L('Only counts are published. No name, EPIC number or address appears anywhere on this site.')], NOTE_REASON]
  };
  return { qa: QA, short: SHORT };
  }));
  });
})();
