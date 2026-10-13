Promise.all([SIR.json('data/bihar/summary.json'), SIR.json('data/bihar/constituencies.json'), SIR.json('data/bihar/districts.json'), SIR.json('data/bihar/identity.json')]).then(function (r) {
  var s = r[0], acs = r[1], ds = r[2], id = r[3], t = s.totals;
  var fixes = []; Object.keys(s.label_fixes).forEach(function (pc) { Object.keys(s.label_fixes[pc]).forEach(function (src) { var f = s.label_fixes[pc][src]; fixes.push({ pc: pc, src: src, party: f.party, status: f.status, evidence: f.evidence }); }); });
  SIR.table(document.getElementById('tFix'), [{ k: 'pc', label: L('Seat'), left: true }, { k: 'src', label: L('Name in the list'), left: true }, { k: 'party', label: L('Party'), left: true }, { k: 'status', label: L('Status'), left: true }, { k: 'evidence', label: L('Evidence'), left: true }], fixes, { sort: 'pc', dir: 1 });
  SIR.table(document.getElementById('tRec'), [
    { k: 'pc', label: L('Seat'), left: true }, { k: 'first', label: L('First'), left: true }, { k: 'first_share', label: L('Booth sum %'), fmt: function (v) { return SIR.d(v, 2); } }, { k: 'published_first_share', label: L('Declared %'), fmt: function (v) { return SIR.d(v, 2); } },
    { k: 'second', label: L('Second'), left: true }, { k: 'second_share', label: L('Booth sum %'), fmt: function (v) { return SIR.d(v, 2); } }, { k: 'published_second_share', label: L('Declared %'), fmt: function (v) { return SIR.d(v, 2); } },
    { k: 'match', label: L('Matches'), left: true, fmt: function (v) { return v ? L('yes') : L('<b>no</b>'); } }], s.label_verification, { sort: 'pc', dir: 1 });

  var rate = function (rows) { return 100 * SIR.sum(rows, 'total') / SIR.sum(rows, 'electorate_2025'); };
  var AL = s.by_alliance_label, w = s.within_seat_2024, I = s.intensity, fs = 100 * t.female / (t.female + t.male);
  var cls = t.hindu + t.muslim + t.unknown, byR = SIR.groupBy(acs, 'reserved'), by25 = SIR.groupBy(acs, 'win2025');
  var border = acs.filter(function (a) { return a.border && a.border !== 'Interior'; }), interior = acs.filter(function (a) { return !a.border || a.border === 'Interior'; });
  var dr = ds.map(function (d) { return d.per_100; }), eb = ds.map(function (d) { return d.electors_per_booth; });
  var ranked = acs.slice().sort(function (a, b) { return b.per_100 - a.per_100; });
  var D = id.districts, fOver = D.filter(function (d) { return d.female_share_deleted > d.female_share_roll; }).length;
  var inside = D.filter(function (d) { return d.muslim_share_population_2011 >= d.muslim_share_deleted_low && d.muslim_share_population_2011 <= d.muslim_share_deleted_high; }).length;
  var cg = id.caste.guardian, both = function (g) { return cg.A.groups[g].ratio_to_survey >= 1 && cg.B.groups[g].ratio_to_survey >= 1; }, neither = function (g) { return cg.A.groups[g].ratio_to_survey < 1 && cg.B.groups[g].ratio_to_survey < 1; };
  var G = ['General', 'BC', 'EBC', 'SC', 'ST', 'Muslim'];
  var andList = function (a) { return a.length < 2 ? a.join('') : a.slice(0, -1).join(', ') + L(' and ') + a[a.length - 1]; };
  // Group names shown in prose: two are English words, the rest acronyms.
  var GW = { General: L('General'), Muslim: L('Muslim') }, GN = function (g) { return GW[g] || g; };
  var withM = acs.filter(function (a) { return a.margin2025; }), overM = withM.filter(function (a) { return a.total > a.margin2025; });
  var b200 = SIR.sum(acs, 'booths_200'), last = I.bins[I.bins.length - 1];
  var QA = [
    [L('How many names were removed, and where?'),
     L('{total} across both phases, {p1} in phase 1 and {p2} in phase 2, or {rate} for every 100 electors on the 2025 roll. The rate runs from {low} per 100 in {low_seat} to {high} in {high_seat}. The highest seats are {top}. <a href="../explorer/">Explorer</a>.', { total: SIR.n(t.total), p1: SIR.n(t.p1), p2: SIR.n(t.p2), rate: SIR.d(100 * t.total / t.electorate_2025, 2), low: SIR.d(ranked[ranked.length - 1].per_100, 1), low_seat: ranked[ranked.length - 1].name, high: SIR.d(ranked[0].per_100, 1), high_seat: ranked[0].name, top: ranked.slice(0, 5).map(function (a) { return a.name + ' (' + SIR.d(a.per_100, 1) + ')'; }).join(', ') })],
    [L('Did NDA and INDIA ground lose names at the same rate?'),
     L('No. Seats the NDA won in 2025 lost {nda25} names per 100 electors and seats INDIA won lost {india25}. By the 2024 Lok Sabha leader the figures are {nda24} and {india24}, and by the 2020 winner {nda20} and {india20}. Inside the same constituency, NDA-led booths lost {gap} more names each than INDIA-led booths, in {seats_higher} of {seats_compared} seats. Of the booths that lost 400 names or more, {nda_pct}% were NDA-led. <a href="../results/">Elections</a>.', { nda25: SIR.d(AL['2025'].NDA.per_100, 2), india25: SIR.d(AL['2025'].INDIA.per_100, 2), nda24: SIR.d(AL['2024'].NDA.per_100, 2), india24: SIR.d(AL['2024'].INDIA.per_100, 2), nda20: SIR.d(AL['2020'].NDA.per_100, 2), india20: SIR.d(AL['2020'].INDIA.per_100, 2), gap: SIR.d(w.pooled_nda_minus_india, 1), seats_higher: w.seats_nda_higher, seats_compared: w.seats_compared, nda_pct: SIR.d(last.nda_pct, 0) })],
    [L('Were women removed out of proportion?'),
     L('Yes. Women are {share} of those removed and {roll} of the roll they were removed from. Their share of the removed is higher than their share of the roll in {over} of {districts} districts. Sex is recorded on the roll. <a href="../people/">Women, religion and caste</a>.', { share: SIR.pct(fs), roll: SIR.pct(t.female_share_roll), over: fOver, districts: D.length })],
    [L('Which caste groups carried the removals?'),
     L('Going by the surname of the father or husband and comparing with the 2023 caste survey, {both} families are removed at or above their share of the population under both classifications, and {neither} families below it. The two classifications disagree on {disagree}. <a href="../people/">Women, religion and caste</a>.', { both: andList(G.filter(both).map(GN)), neither: andList(G.filter(neither).map(GN)), disagree: andList(G.filter(function (g) { return !both(g) && !neither(g); }).map(GN)) })],
    [L('How does the Muslim share of removals compare with the population?'),
     L('Names classified Muslim are {low} of removals, and {high} if every unclassified name is counted, against 16.87% of the population in 2011 and 17.70% in the 2023 survey. The census share lies inside that range in {inside} of {districts} districts. <a href="../people/">Women, religion and caste</a>.', { low: SIR.pct(100 * t.muslim / cls), high: SIR.pct(100 * (t.muslim + t.unknown) / cls), inside: inside, districts: D.length })],
    [L('Do border constituencies differ from the interior?'),
     L('Border constituencies lost {border} per 100 electors, the interior {interior}. <a href="../border/">Border</a>.', { border: SIR.d(rate(border), 2), interior: SIR.d(rate(interior), 2) })],
    [L('Do reserved seats differ?'),
     L('The {sc_seats} seats reserved for Scheduled Castes lost {sc_rate} names per 100 electors, the {st_seats} reserved for Scheduled Tribes lost {st_rate}, and the general seats lost {gen_rate}.', { sc_seats: byR.SC.length, sc_rate: SIR.d(rate(byR.SC), 2), st_seats: byR.ST.length, st_rate: SIR.d(rate(byR.ST), 2), gen_rate: SIR.d(rate(byR.GEN), 2) })],
    [L('Do removals exceed winning margins?'),
     L('In {over} of {seats} seats the revision removed more names than the 2025 winning margin. <a href="../results/">Elections</a>.', { over: overM.length, seats: withM.length })],
    [L('How do the parties\' seats compare?'),
     L('Removals per 100 electors in the seats each party won in 2025: {parties}.', { parties: ['BJP', 'JD(U)', 'LJP(RV)', 'RJD', 'INC', 'AIMIM'].filter(function (p) { return by25[p]; }).map(function (p) { return L('{party} {rate} ({seats} seats)', { party: p, rate: SIR.d(rate(by25[p]), 2), seats: by25[p].length }); }).join(', ') })],
    [L('Does booth size relate to removal intensity?'),
     L('Across districts, electors per booth and removals per 100 electors have a rank correlation of {rho}.', { rho: SIR.d(SIR.spearman(eb, dr), 2) })],
    [L('Which booths stand out?'),
     L('{b200} booths lost 200 or more names and {b400} lost 400 or more. Each constituency\'s booths can be sorted in the <a href="../explorer/">explorer</a>.', { b200: SIR.n(b200), b400: SIR.n(last.booths) })]
  ];
  document.getElementById('qas').innerHTML = QA.map(function (q, i) {
    return '<div class="qa"><h3>' + (i + 1) + '. ' + q[0] + '</h3><p>' + q[1] + '</p></div>';
  }).join('');
}).catch(SIR.fail);
