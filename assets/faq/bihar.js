/* Questions and answers for the Bihar pages. The FAQ tab shows them all;
   each page shows those tagged with its key (dash, explorer, results,
   people, border, districts, method). */
(function () {
  var P;
  SIR.faq('bihar', 'bihar/faq/', function () {
    return P || (P = Promise.all([SIR.json('data/bihar/summary.json'), SIR.json('data/bihar/constituencies.json'), SIR.json('data/bihar/identity.json'), SIR.json('data/bihar/reasons.json'), SIR.json('data/bihar/final.json'), SIR.json('data/bihar/tests.json'), SIR.json('data/bihar/impact.json'), SIR.json('data/bihar/swing.json'), SIR.json('data/bihar/districts.json'), SIR.json('data/bihar/robust.json')]).then(function (r) {
  var IM = r[6], IS = IM.summary, IB = IM.breakeven_bands.lower, SW = r[7].summary, swn = SW.thirds.map(function (t) { return t.d_lead_adj; });
  var FN = r[4], FT = FN.totals, TD = r[5].deaths, TM = r[5].marriage;
  var RS = r[3], RT = RS.totals, rp = function (k) { return SIR.pct(100 * RT[k] / RS.total); };
  var xsF = SIR.sum(Object.keys(RT), function (k) { return RS.by_sex[k].F - RS.by_sex[k].M; }), xsS = RS.by_sex.shifted.F - RS.by_sex.shifted.M;
  var yS = RS.by_age.shifted[0] + RS.by_age.shifted[1], yW = RS.by_age_women.shifted[0] + RS.by_age_women.shifted[1];
  var s = r[0], acs = r[1], id = r[2], t = s.totals, AL = s.by_alliance_label, W = s.within_seat_2024, D = id.districts;
  var withM = acs.filter(function (a) { return a.margin2025; }), over = withM.filter(function (a) { return a.total > a.margin2025; });
  var took = withM.filter(function (a) { return a.al2020 === 'INDIA' && a.al2025 === 'NDA'; }), tookOver = took.filter(function (a) { return a.total > a.margin2025; });
  var held = withM.filter(function (a) { return a.al2020 === 'INDIA' && a.al2025 === 'INDIA'; });
  var pre = function (rows) { return 100 * SIR.sum(rows, 'total') / SIR.sum(rows, function (a) { return a.electorate_2025 + a.total; }); };
  var cls = t.hindu + t.muslim + t.unknown, fs = 100 * t.female / (t.female + t.male);
  var fOver = D.filter(function (d) { return d.female_share_deleted > d.female_share_roll; }).length;
  var inside = D.filter(function (d) { return d.muslim_share_population_2011 >= d.muslim_share_deleted_low && d.muslim_share_population_2011 <= d.muslim_share_deleted_high; }).length;
  var above = D.filter(function (d) { return d.muslim_share_deleted_low > d.muslim_share_population_2011 + 1; }).map(function (d) { return d.district; });
  var cg = id.caste.guardian, G = ['General', 'BC', 'EBC', 'SC', 'ST', 'Muslim'];
  var AND0 = function (a) { return a.length < 2 ? a.join('') : a.slice(0, -1).join(', ') + L(' and ') + a[a.length - 1]; };
  var CAP = function (x) { return x.charAt(0).toUpperCase() + x.slice(1); };
  // Group names shown in prose: two are English words, the rest acronyms.
  var GW = { General: L('General'), Muslim: L('Muslim') }, GN = function (g) { return GW[g] || g; };
  var up = G.filter(function (g) { return cg.A.groups[g].ratio_to_survey >= 1 && cg.B.groups[g].ratio_to_survey >= 1; }), down = G.filter(function (g) { return cg.A.groups[g].ratio_to_survey < 1 && cg.B.groups[g].ratio_to_survey < 1; });
  var QA = [
    [L('Were most of the removed dead, or moved away?'),
     L('That is what the entries say for most of them, and nobody checked the entries. The phase 1 list gives a reason for every one of the {removed} names. {shifted} were entered as permanently shifted, {dead} as dead, {absent} as absent and {enrolled} as already enrolled elsewhere. Someone marked "shifted" may have been away for work when the officer called, and someone marked "absent" may have been at home. The {absent_n} marked absent rest on the least of the four, because the entry records only that the officer did not find the elector. The phase 2 lists give no reasons.', { removed: SIR.n(RS.total), shifted: rp('shifted'), dead: rp('dead'), absent: rp('absent'), enrolled: rp('already_enrolled'), absent_n: SIR.n(RT.absent) })],
    [L('Did the removals exceed the margins by which seats were won?'),
     L('Yes, in {over} of {seats} constituencies. Of the {took} seats INDIA held in 2020 and the NDA won in 2025, {took_over} lost more names than the NDA\'s winning margin. That does not mean those results would have gone the other way. It means the roll changed by more than the vote that decided the seat, so the removals could have decided it. Nobody outside the Election Commission can say whose names they were.', { over: over.length, seats: withM.length, took: took.length, took_over: tookOver.length })],
    [L('Could the removals have changed who won?'),
     L('In many seats they could have. In {n} of {seats} seats the removed electors who would have voted were enough to change the result had they backed the runner-up, and in {k} a lean of just over half among them would have done it. The lists do not say how they would have voted. Going by how their own booths voted in 2024, {k1} to {k2} seats would have changed hands, some each way. <a href="../results/">Elections</a>.', {
       n: IM.seats_total - IB.over_100, seats: IM.seats_total, k: IB.under_55, k1: IS.booth_lower.flips, k2: IS.booth_upper.flips })],
    [L('So was the revision clean?'),
     L('The lists give every reason to doubt it. {total} names came off the roll, women were removed out of proportion in every district, women were a larger share of those entered as dead than of the state\'s adult deaths, and the final roll put back at most {m} of those removed at the draft. A voter wrongly removed has lost a vote whichever way it would have gone. What the election results cannot show is whether the removals moved votes between the alliances. <a href="../results/#swing">Elections</a>.', { total: SIR.lakh(t.total), m: SIR.pct(FT.made_up_pct) })],
    [L('Are the names entered as dead plausible?'),
     L('In number, yes. They equal about {y} years of Bihar\'s adult deaths at 2024 death rates, and their ages are close to those of registered deaths. By sex, no. Women are {wd} of those entered as dead but {we} of adult deaths. Either women\'s deaths, which are registered less often, stayed on the roll longer, or women still alive were entered as dead. <a href="../people/">Women, religion and caste</a>.', { y: SIR.d(TD.years_of_deaths, 1), wd: SIR.pct(TD.women_share_dead), we: SIR.pct(TD.women_share_expected) })],
    [L('Is marriage why so many young women were marked shifted?'),
     L('It can explain the number but not the places. The {x} more young women than young men marked shifted come to about {yrs} of one year\'s marriage moves at 2011 census rates. But districts where more women had moved on marriage do not have more women among the young marked shifted (rank correlation {r}).', { x: SIR.n(TM.excess), yrs: SIR.d(TM.excess_years, 2), r: SIR.d(TM.rho_share, 2) })],
    [L('Were the names removed at the draft put back?'),
     L('Most of them were not. After the draft, {a} names were added on claims and {r} removed on objections, so the final roll rose by {na}, or {m} of the {p1} removed at the draft. New electors are part of that rise, so at most that many can have been put back. The final roll was {nf} smaller than the roll before the revision, smaller in every seat, and in {net} of {seats} seats the fall that remained was larger than the 2025 winning margin. Women were {wadd} of those added and {wp1} of those removed at the draft. <a href="../results/">Deletions and results</a>.', { a: SIR.lakh(FT.added), r: SIR.lakh(FT.removed_after), na: SIR.lakh(FT.net_after), m: SIR.pct(FT.made_up_pct), p1: SIR.lakh(FT.p1), nf: SIR.lakh(FT.net_fall_press), net: FN.margin.net, seats: FN.margin.seats, wadd: SIR.pct(FT.women_share_added), wp1: SIR.pct(FT.women_share_p1) })],
    [L('Did NDA seats lose more names than INDIA seats?'),
     L('They did. Seats the NDA won in 2020 lost {nda} names per 100 electors, and seats INDIA won lost {india}. Booths the NDA led in 2024 lost {gap} more names each than INDIA-led booths in the same constituency. A booth\'s leading party shows how most of its voters voted in 2024, and says nothing about the removed electors, since every booth has voters on both sides. The seats INDIA lost in 2025 did not lose names faster than the seats it kept ({lost} and {kept} per 100 electors on the roll before the revision, taken as the 2025 roll plus the names removed). What the lists do establish is how large the removals were against the margins.', { nda: SIR.d(AL['2020'].NDA.per_100, 2), india: SIR.d(AL['2020'].INDIA.per_100, 2), gap: SIR.d(W.pooled_nda_minus_india, 1), lost: SIR.d(pre(took), 2), kept: SIR.d(pre(held), 2) })],
    [L('Why are women over-represented?'),
     L('Women are {share} of those removed and {roll} of the roll they were removed from, and their share of the removed is higher than their share of the roll in {over} of {districts} districts. The roll records sex, so this needs no guessing. Phase 1 removed {xs} more women than men, and {xs_shifted} of that difference were marked shifted. Among those marked shifted at ages 18 to 29, {young} are women. Marriage could account for that number but not for the districts where it falls. The lists do not show whether any of these women were enrolled again where they now live, and any who were not have lost the vote.', { share: SIR.pct(fs), roll: SIR.pct(t.female_share_roll), over: fOver, districts: D.length, xs: SIR.n(xsF), xs_shifted: SIR.n(xsS), young: SIR.pct(100 * yW / yS) })],
    [L('Were Muslims removed out of proportion?'),
     L('Names the booth lists classify as Muslim are {low} of removals, and {high} if every unclassified name were Muslim, against 16.87% of the population in 2011 and 17.70% in the 2023 caste survey. The census share lies inside that range in {inside} of {districts} districts. In {above} districts the classified Muslim share alone is more than a point above the census share. They are {above_list}. <a href="../people/">Women, religion and caste</a>.', { low: SIR.pct(100 * t.muslim / cls), high: SIR.pct(100 * (t.muslim + t.unknown) / cls), inside: inside, districts: D.length, above: above.length, above_list: AND0(above) })],
    [L('How can caste be read from surnames?'),
     L('Only partly. That is why two classifications are used and only results that hold under both are reported. Going by the surname of the father or husband, {up} families are removed at or above their share in the 2023 caste survey under both, and {down} families below it.', { up: AND0(up.map(GN)), down: AND0(down.map(GN)) })],
    [L('How reliable are the lists?'),
     L('The booth list covers every one of Bihar\'s {booths} polling booths and adds up to {p1b} phase 1 removals, {p1} women and men and {tg} third-gender electors. The constituency totals for both phases match the Chief Electoral Officer\'s table. Votes added up from the booths give the declared winner and runner-up in all 40 Lok Sabha seats.', { booths: SIR.n(t.booths), p1b: SIR.n(t.p1_booths), p1: SIR.n(t.p1), tg: SIR.n(t.p1_booths - t.p1) })],
    [L('Does this show that the removals were intended to change results?'),
     L('No list of removals can show intent. The lists show where the removals fell, who was removed and how the numbers compare with the margins. They cannot show whose votes these were or whether each removal was right.')],
    [L('Why are no names published?'),
     L('The analysis looks at the revision as a whole. Only counts are published, and no name, EPIC number or address appears anywhere on these pages.')]
  ];
  var TAGS = [['dash', 'explorer'], ['results', 'dash'], ['results'], ['results', 'dash'], ['people'], ['people'], ['results', 'dash'], ['results'],
    ['people', 'dash'], ['people', 'border'], ['people'], ['method', 'explorer'], ['method', 'dash', 'border'], ['method', 'explorer']];
  QA.forEach(function (q, i) { q.push(TAGS[i]); });

  // ---- Questions for the pages the FAQ tab did not cover.
  var AND = function (a) { return a.length < 2 ? a.join('') : a.slice(0, -1).join(', ') + L(' and ') + a[a.length - 1]; };
  var bor = acs.filter(function (a) { return a.border && a.border !== 'Interior'; }), inn = acs.filter(function (a) { return !a.border || a.border === 'Interior'; });
  var rt = function (rows) { return 100 * SIR.sum(rows, 'total') / SIR.sum(rows, 'electorate_2025'); };
  var ms = function (rows, hi) { return 100 * SIR.sum(rows, function (a) { return a.muslim + (hi ? a.unknown : 0); }) / SIR.sum(rows, function (a) { return a.hindu + a.muslim + a.unknown; }); };
  var BG = SIR.groupBy(bor, 'border'), belts = Object.keys(BG).sort(function (x, y) { return rt(BG[y]) - rt(BG[x]); });
  var beltName = function (k) { return k.split(';').join(L(' and ')); };
  QA.push([L('Did seats on the border lose more names?'),
    L('Somewhat more. The {n} seats on a border lost {b} names per 100 electors, and the {i} interior seats {in}. Border seats hold {el} of Bihar\'s electors and account for {sh} of the removals. The heaviest belt was the seats bordering {top}, at {topr} per 100.', {
      n: bor.length, b: SIR.d(rt(bor), 2), i: inn.length, in: SIR.d(rt(inn), 2), el: SIR.pct(100 * SIR.sum(bor, 'electorate_2025') / SIR.sum(acs, 'electorate_2025')),
      sh: SIR.pct(100 * SIR.sum(bor, 'total') / SIR.sum(acs, 'total')), top: beltName(belts[0]), topr: SIR.d(rt(BG[belts[0]]), 2) }), ['border']]);
  QA.push([L('Were more Muslim names removed near the border?'),
    L('A larger share, yes. Names the lists classify as Muslim are {lo} to {hi} of removals in border seats and {ilo} to {ihi} in the interior. Several border belts, Seemanchal above all, have large Muslim populations, so some of that difference follows from who lives there. The page on women, religion and caste compares each district with its own population.', {
      lo: SIR.pct(ms(bor, false)), hi: SIR.pct(ms(bor, true)), ilo: SIR.pct(ms(inn, false)), ihi: SIR.pct(ms(inn, true)) }), ['border']]);
  QA.push([L('Does this show that people not entitled to vote were removed near the border?'),
    L('No. The lists give one of four reasons for each name, dead, shifted, absent or already enrolled elsewhere. None of them is a finding that a person was not entitled to vote, and the lists have no category for it.'), ['border', 'method']]);
  var DD = r[8].slice().sort(function (x, y) { return y.per_100 - x.per_100; });
  var FAC = [['gddp_pc', L('income per head')], ['urban_pct', L('the share living in towns')], ['women_literate', L('women\'s literacy')], ['child_marriage', L('early marriage')], ['density', L('population density')], ['electors_per_booth', L('booth size')]];
  var rho = FAC.map(function (f) { var ok = DD.filter(function (d) { return d[f[0]] != null; }); return [f[1], SIR.spearman(ok.map(function (d) { return d[f[0]]; }), ok.map(function (d) { return d.per_100; }))]; });
  var linked = rho.filter(function (x) { return Math.abs(x[1]) >= 0.2; }), unl = rho.filter(function (x) { return Math.abs(x[1]) < 0.2; });
  QA.push([L('Which districts lost the most names?'),
    L('{a}, {b} and {c} lost the most for their size, {ar}, {br} and {cr} names per 100 electors. {y} and {z} lost the fewest, {yr} and {zr}. The <a href="../districts/">Districts</a> page gives all {n} districts.', {
      a: DD[0].district, b: DD[1].district, c: DD[2].district, ar: SIR.d(DD[0].per_100, 1), br: SIR.d(DD[1].per_100, 1), cr: SIR.d(DD[2].per_100, 1),
      y: DD[DD.length - 2].district, z: DD[DD.length - 1].district, yr: SIR.d(DD[DD.length - 2].per_100, 1), zr: SIR.d(DD[DD.length - 1].per_100, 1), n: DD.length }), ['districts']]);
  var FL = linked.length > 1 ? function (o) { return L('Of the {n} things compared, {k} move with the removal rate, {list}.', o); } : function (o) { return L('Of the {n} things compared, one moves with the removal rate, {list}.', o); };
  QA.push([L('Do less urban or less schooled districts lose more names?'),
    (linked.length ? FL({ n: FAC.length, k: linked.length, list: AND(linked.map(function (x, i) { return i ? L('{f} ({r})', { f: x[0], r: SIR.d(x[1], 2) }) : L('{f} (rank correlation {r})', { f: x[0], r: SIR.d(x[1], 2) }); })) }) + ' ' : '') +
    (unl.length ? (unl.length > 1 ? L('{list} show no relationship.', { list: CAP(AND(unl.map(function (x) { return x[0]; }))) }) : L('{list} shows no relationship.', { list: CAP(unl[0][0]) })) + ' ' : '') +
    L('A relationship across districts says nothing about why any one name was removed.'), ['districts']]);
  QA.push([L('Why is every relationship here called rough?'),
    L('There are only {n} districts, and a few large ones can pull a line one way. Each is shown with two measures. One of them uses ranks, so that a single extreme district cannot drive it, and a rank correlation under 0.2 either way is read as no relationship.', { n: DD.length }), ['districts', 'method']]);
  var H = s.booth_histogram, b200 = ['200-249', '250-299', '300-399', '400+'].reduce(function (x, k) { return x + H[k]; }, 0), BI = s.intensity.bins;
  QA.push([L('Why did some booths lose far more names than others?'),
    L('Most booths lost fewer than 100 names, but {n} of {all} lost 200 or more. The lists record a reason for each name but not why one officer entered so many more than another. The heavier the removals in a booth, the more likely it was to have been led by the NDA in 2024, {lo} of the lightest booths against {hi} of the heaviest.', {
      n: SIR.n(b200), all: SIR.n(t.booths), lo: SIR.pct(BI[0].nda_pct), hi: SIR.pct(BI[BI.length - 1].nda_pct) }), ['explorer', 'results']]);
  QA.push([L('Can I look up my own name here?'),
    L('No. Only counts are published on this site. To check your own entry, use the Election Commission\'s voter search.'), ['explorer', 'dash']]);

  var RB = r[9];
  QA.push([L('How sure are these findings?'),
    L('Each was measured again within each district, within each seat and with Seemanchal left out. Two survive every check. More names were removed than the winning margin in {a} of {n} seats on the draft count and {b} on the final roll, and women were removed out of proportion in all {d} districts and {s} of {n} constituencies. That more names were removed on NDA ground holds inside seats, where NDA-led booths lost more in {h} of {c} seats. Whether seats with more removals swung further to the NDA changes with the comparison. <a href="../results/#sure">Elections</a>.', {
      a: RB.margins.draft, b: RB.margins.net, n: RB.margins.seats, d: RB.women.districts, s: RB.women.seats_over, h: RB.ground.within_seat.nda_higher, c: RB.ground.within_seat.seats }), ['results', 'method', 'dash']]);

  // ---- "In short" for each page, every figure from the data.
  var cls2 = t.hindu + t.muslim + t.unknown, avgB = t.p1 / t.booths;
  var fem = fOver === D.length ? L('Women were more likely to be removed. They are {w} of the names removed and {roll} of the roll they were removed from, and their share of the removed is higher in all {n} districts.', { w: SIR.pct(fs), roll: SIR.pct(t.female_share_roll), n: D.length })
    : L('Women were more likely to be removed. They are {w} of the names removed and {roll} of the roll they were removed from, and their share of the removed is higher in {k} of {n} districts.', { w: SIR.pct(fs), roll: SIR.pct(t.female_share_roll), k: fOver, n: D.length });
  var NOTE_NAMES = L('Religion and caste are guessed from names and given as ranges.');
  var NOTE_REASON = L('A reason on the list is what the officer wrote down, and nobody checked it.');
  var head = [
    L('The revision took {total} names off Bihar\'s roll, {r} of every 100 electors and as many as {share} of all the votes cast in the election that followed.', { total: SIR.lakh(t.total), r: SIR.d(100 * t.total / t.electorate_2025, 2), share: SIR.pct(100 * t.total / SIR.sum(acs, 'votes2025')) }),
    fem,
    L('In {over} of {seats} constituencies more names came off the roll than the 2025 winning margin. Once claims were heard, the final roll made up at most {m} of the names removed at the draft.', { over: over.length, seats: withM.length, m: SIR.pct(FT.made_up_pct) }),
    L('In {n} constituencies the removed electors who would have voted were enough to change the result had they backed the runner-up.', { n: IM.seats_total - IB.over_100 })
  ];
  var SHORT = {
    dash: [head, NOTE_NAMES], faq: [head, NOTE_NAMES],
    explorer: [[
      L('The first phase removed names from every one of Bihar\'s {booths} polling booths, {avg} per booth on average.', { booths: SIR.n(t.booths), avg: SIR.d(avgB, 0) }),
      L('Most booths lost fewer than 100 names, but {n} lost 200 or more.', { n: SIR.n(b200) }),
      L('The heavier the removals in a booth, the more likely it was to have voted NDA in 2024, {lo} of the lightest booths against {hi} of the heaviest.', { lo: SIR.pct(BI[0].nda_pct), hi: SIR.pct(BI[BI.length - 1].nda_pct) }),
      L('Choose a district and then a constituency to see its own figures, set against the margin by which the seat was won.')], NOTE_NAMES],
    results: [[
      L('In {over} of {seats} constituencies more names were removed than the 2025 winning margin. That includes {took_over} of the {took} seats the NDA took from INDIA.', { over: over.length, seats: withM.length, took_over: tookOver.length, took: took.length }),
      L('After claims and objections the final roll was still smaller than the roll before the revision in every seat, and in {net} seats the fall that remained was larger than the margin.', { net: FN.margin.net }),
      L('In {n} of {seats} seats the removed electors who would have voted were enough to change the result had they backed the runner-up, and in {k} a lean of just over half among them would have done it.', { n: IM.seats_total - IB.over_100, seats: IM.seats_total, k: IB.under_55 }),
      L('Inside the same constituency, booths that voted NDA in 2024 lost {gap} more names each than those that voted INDIA, and more in {h} of {c} seats.', { gap: SIR.d(W.pooled_nda_minus_india, 1), h: W.seats_nda_higher, c: W.seats_compared })],
      L('The lists show where the removals fell. They cannot show whose votes the removed names were, and the election results cannot show whether the removals moved votes between the alliances.')],
    people: [[
      fOver === D.length ? L('Women are {w} of the names removed and {roll} of the roll they were removed from. Their share of the removed is higher in all {n} districts.', { w: SIR.pct(fs), roll: SIR.pct(t.female_share_roll), n: D.length })
        : L('Women are {w} of the names removed and {roll} of the roll they were removed from. Their share of the removed is higher in {k} of {n} districts.', { w: SIR.pct(fs), roll: SIR.pct(t.female_share_roll), k: fOver, n: D.length }),
      L('Women are {wd} of the names entered as dead but only {we} of adult deaths in Bihar, so either women\'s deaths stayed on the roll longer or living women were entered as dead.', { wd: SIR.pct(TD.women_share_dead), we: SIR.pct(TD.women_share_expected) }),
      L('Names classified as Muslim are {low} to {high} of the removed, against 17.70% of the population in the 2023 caste survey.', { low: SIR.pct(100 * t.muslim / cls2), high: SIR.pct(100 * (t.muslim + t.unknown) / cls2) }),
      up.length ? L('By the surname of the father or husband, {up} families are removed at or above their share in the caste survey under both classifications.', { up: AND(up.map(GN)) }) : null], NOTE_NAMES],
    border: [[
      L('Border seats lost {b} names per 100 electors, and interior seats {i}. The heaviest were the seats bordering {top}, at {topr}.', { b: SIR.d(rt(bor), 2), i: SIR.d(rt(inn), 2), top: beltName(belts[0]), topr: SIR.d(rt(BG[belts[0]]), 2) }),
      L('Border seats hold {el} of Bihar\'s electors and account for {sh} of the removals.', { el: SIR.pct(100 * SIR.sum(bor, 'electorate_2025') / SIR.sum(acs, 'electorate_2025')), sh: SIR.pct(100 * SIR.sum(bor, 'total') / SIR.sum(acs, 'total')) }),
      L('Names classified as Muslim are {lo} to {hi} of removals in border seats and {ilo} to {ihi} in the interior.', { lo: SIR.pct(ms(bor, false)), hi: SIR.pct(ms(bor, true)), ilo: SIR.pct(ms(inn, false)), ihi: SIR.pct(ms(inn, true)) })],
      L('None of the reasons on the lists is a finding that a person was not entitled to vote.')],
    districts: [[
      L('{a} lost the most names for its size, {ar} per 100 electors, and {z} the fewest, {zr}.', { a: DD[0].district, ar: SIR.d(DD[0].per_100, 1), z: DD[DD.length - 1].district, zr: SIR.d(DD[DD.length - 1].per_100, 1) }),
      linked.length ? L('Across districts the removal rate moves with {list}.', { list: AND(linked.map(function (x) { return x[0]; })) }) : null,
      unl.length ? L('It shows no relationship with {list}.', { list: AND(unl.map(function (x) { return x[0]; })) }) : null],
      L('With only {n} districts every one of these links is rough, and none of them says why any one name was removed.', { n: DD.length })],
    method: [[
      L('The figures come from the Chief Electoral Officer\'s lists of removed names for both phases, the return for the final roll, and the Election Commission\'s results.'),
      L('The booth lists cover all {booths} polling booths and add up to the official totals in every constituency.', { booths: SIR.n(t.booths) }),
      L('Sex is recorded on the roll. Religion and caste are guessed from names and given as ranges.'),
      L('Only counts are published. No name, EPIC number or address appears anywhere on this site.')], NOTE_REASON]
  };
  return { qa: QA, short: SHORT };
  }));
  });
})();
