Promise.all([SIR.json('data/bihar/identity.json'), SIR.json('data/bihar/constituencies.json'), SIR.json('data/bihar/summary.json'), SIR.json('data/bihar/reasons.json')]).then(function (r) {
  var RS = r[3];
  var id = r[0], acs = r[1], s = r[2], D = id.districts, t = s.totals;
  // ---- gender
  var fs = 100 * t.female / (t.female + t.male), popF = t.female_share_roll;
  var above = D.filter(function (d) { return d.female_share_deleted > d.female_share_roll; }).length;
  document.getElementById('kGender').innerHTML = [[SIR.pct(fs), L('of those removed were women')], [SIR.pct(popF, 2), L('women on the roll before the revision')],
    [L('{a} of {b}', { a: above, b: D.length }), L('districts where women were removed out of proportion')], [SIR.n(t.female - t.male), L('more women than men removed, both phases')]]
    .map(function (k) { return '<div><b>' + k[0] + '</b><span>' + k[1] + '</span></div>'; }).join('');
  SIR.chart('cGender', { type: 'scatter', data: { datasets: [
      { label: L('District'), data: D.map(function (d) { return { x: d.female_share_roll, y: d.female_share_deleted, n: d.district }; }), $token: '--female', pointRadius: 4 },
      { label: L('Equal share'), type: 'line', data: [{ x: 46, y: 46 }, { x: 51, y: 51 }], $token: '--fill-grey', pointRadius: 0, borderDash: [4, 4] }] },
    options: { plugins: { tooltip: { callbacks: { label: function (c) { return c.raw.n ? L('{n}: {y}% of removals, {x}% of population', { n: c.raw.n, y: c.raw.y, x: c.raw.x }) : ''; } } } },
      scales: { x: { min: 46, max: 51, title: { display: true, text: L('Women, % of the roll before the revision') } }, y: { min: 46, max: 63, title: { display: true, text: L('Women, % of removals') } } } } });
  var G = SIR.groupBy(acs, 'al2025'), als = ['NDA', 'INDIA', 'Other'], ALN = { Other: L('Other') };
  SIR.chart('cGenderAl', { type: 'bar', data: { labels: als.map(function (a) { return (ALN[a] || a) + ' (' + G[a].length + ')'; }), datasets: [{ label: L('Women %'), data: als.map(function (a) { return 100 * SIR.sum(G[a], 't_f') / (SIR.sum(G[a], 't_f') + SIR.sum(G[a], 't_m')); }), $tokens: als.map(function (a) { return SIR.alliance[a]; }) }] },
    options: { plugins: { legend: { display: false } }, scales: { y: { min: 40, title: { display: true, text: L('Women, % of removals') } } } } });
  var RK = ['shifted', 'absent', 'already_enrolled', 'dead'], RN = { dead: L('Dead'), shifted: L('Shifted'), absent: L('Absent'), already_enrolled: L('Already enrolled') }, RC = { dead: '--muted', shifted: '--navy', absent: '--red', already_enrolled: '--amber' };
  SIR.chart('cGenderReason', { type: 'line', data: { labels: RS.bands, datasets: RK.map(function (k) { return { label: RN[k], data: RS.by_age[k].map(function (v, i) { return +(100 * RS.by_age_women[k][i] / v).toFixed(1); }), $token: RC[k], borderWidth: 2, pointRadius: 3, borderDash: k === 'dead' ? [4, 4] : undefined }; }) },
    options: { scales: { x: { title: { display: true, text: L('Age') } }, y: { min: 40, max: 80, title: { display: true, text: L('Women, % of removals') } } } } });
  var xsF = SIR.sum(RK, function (k) { return RS.by_sex[k].F - RS.by_sex[k].M; }), xsS = RS.by_sex.shifted.F - RS.by_sex.shifted.M;
  var yS = RS.by_age.shifted[0] + RS.by_age.shifted[1], yW = RS.by_age_women.shifted[0] + RS.by_age_women.shifted[1];
  var gaps = D.map(function (d) { return d.female_share_deleted - d.female_share_roll; });
  document.getElementById('fGender').innerHTML = L('<b>Women were removed out of proportion in {a} of {b} districts</b>, by {lo} to {hi} points above their share of the roll they were removed from. The roll records sex, so this needs no guessing from names. Phase 1 removed {xs} more women than men, and {xs_shifted} of that difference were marked shifted. Among those marked shifted at ages 18 to 29, {young} are women. Marriage could account for that number. It does not account for where it falls, as the next section shows. The lists do not show whether any of these women were enrolled again where they now live.', { xs: SIR.n(xsF), xs_shifted: SIR.n(xsS), young: SIR.pct(100 * yW / yS), a: above, b: D.length, lo: SIR.d(Math.min.apply(null, gaps), 1), hi: SIR.d(Math.max.apply(null, gaps), 1) });

  // ---- religion
  var cls = t.hindu + t.muslim + t.unknown, lo = 100 * t.muslim / cls, hi = 100 * (t.muslim + t.unknown) / cls;
  document.getElementById('kRel').innerHTML = [[L('{lo} to {hi}', { lo: SIR.pct(lo), hi: SIR.pct(hi) }), L('Muslim-name share of removals')], ['16.87%', L('Muslim share of population, 2011')], ['17.70%', L('Muslim share, 2023 caste survey')], [SIR.pct(100 * t.unknown / cls), L('of removed names unclassified')]]
    .map(function (k) { return '<div><b>' + k[0] + '</b><span>' + k[1] + '</span></div>'; }).join('');
  var Ds = D.slice().sort(function (a, b) { return b.muslim_share_population_2011 - a.muslim_share_population_2011; });
  SIR.chart('cRel', { type: 'bar', data: { labels: Ds.map(function (d) { return d.district; }), datasets: [
      { type: 'bar', label: L('Muslim-name share of removals (range)'), data: Ds.map(function (d) { return [d.muslim_share_deleted_low, d.muslim_share_deleted_high]; }), $token: '--fill-other', barPercentage: 0.75, order: 2 },
      { type: 'line', label: L('Muslim share of population, 2011'), data: Ds.map(function (d) { return d.muslim_share_population_2011; }), showLine: false, $token: '--ink', pointRadius: 4, pointHoverRadius: 5, order: 1 },
      { type: 'line', label: L('Muslim share of population, carried forward to 2025'), data: Ds.map(function (d) { return d.muslim_share_projected_2025; }), showLine: false, $token: '--ink', pointStyle: 'circle', pointRadius: 4, pointHoverRadius: 5, pointBackgroundColor: 'rgba(0,0,0,0)', borderWidth: 1.5, order: 0 }] },
    options: { indexAxis: 'y', scales: { y: { ticks: { autoSkip: false } }, x: { beginAtZero: true, title: { display: true, text: L('% of removals, and % of population') } } } } });
  var pin = D.filter(function (d) { return d.muslim_share_projected_2025 >= d.muslim_share_deleted_low && d.muslim_share_projected_2025 <= d.muslim_share_deleted_high; });
  var pclear = D.filter(function (d) { return d.muslim_share_deleted_low - d.muslim_share_projected_2025 > 1; });
  document.getElementById('fProj').innerHTML = L('<b>Carried forward to 2025, the census shares give much the same picture.</b> At each district\'s growth rates from 2001 to 2011, Bihar\'s Muslim share comes to {st} in 2025, close to the {sv} counted by the 2023 caste survey, and no district moves by more than {mx} points. On the 2025 shares the range holds the population share in {inside} of {n} districts, and the lowest estimate is more than a point above it in {clear} districts ({list}).', { st: SIR.pct(id.muslim_projected_2025), sv: SIR.pct(id.survey_baseline.Muslim), mx: SIR.d(Math.max.apply(null, D.map(function (d) { return Math.abs(d.muslim_share_projected_2025 - d.muslim_share_population_2011); })), 1), inside: pin.length, n: D.length, clear: pclear.length, list: pclear.map(function (d) { return d.district; }).join(', ') });
  var inside = D.filter(function (d) { return d.muslim_share_population_2011 >= d.muslim_share_deleted_low && d.muslim_share_population_2011 <= d.muslim_share_deleted_high; });
  var over = D.filter(function (d) { return d.muslim_share_deleted_low > d.muslim_share_population_2011; });
  var clear = over.filter(function (d) { return d.muslim_share_deleted_low - d.muslim_share_population_2011 > 1; }).sort(function (a, b) { return (b.muslim_share_deleted_low / b.muslim_share_population_2011) - (a.muslim_share_deleted_low / a.muslim_share_population_2011); });
  var rr = clear.map(function (d) { return d.muslim_share_deleted_low / d.muslim_share_population_2011; });
  document.getElementById('fRel').innerHTML = L('<b>For the state as a whole the range, {lo} to {hi}, includes the 2011 share of 16.87%. District by district it often does not.</b> The census share falls inside the range in {inside} of {n} districts. In the other {over}, more Muslim-name electors were removed than the 2011 share would predict, even if none of the unclassified names is counted. Most of those gaps are a point or less. <b>In {clear} districts the gap is more than a point.</b> They are {list}. All {clear} are in south and central Bihar, where Muslims are a small minority, and there even the low end of the range is {rmin} to {rmax}% above the population share. Muslims in Bihar are younger than average, so their share of <em>electors</em> is smaller than their share of the population, and that would make these gaps wider. Migration into Patna and mistakes in name classification could make them narrower.', { lo: SIR.pct(lo), hi: SIR.pct(hi), inside: inside.length, n: D.length, over: over.length, clear: clear.length, list: clear.map(function (d) { return L('{d} ({lo} at least, against {pop})', { d: d.district, lo: SIR.pct(d.muslim_share_deleted_low), pop: SIR.pct(d.muslim_share_population_2011) }); }).join(', '), rmin: Math.round(100 * (Math.min.apply(null, rr) - 1)), rmax: Math.round(100 * (Math.max.apply(null, rr) - 1)) });

  // ---- caste
  var C = id.caste, who = 'guardian', GR = ['General', 'BC', 'EBC', 'SC', 'ST', 'Muslim'], charts = {};
  var GL = { General: L('General'), Muslim: L('Muslim') }, gl = function (g) { return GL[g] || g; };
  function drawCaste() {
    var c = C[who];
    [charts.cover, charts.comp, charts.bounds].forEach(function (x) { if (x) x.destroy(); });
    SIR.charts = SIR.charts.filter(function (x) { return [charts.cover, charts.comp, charts.bounds].indexOf(x) < 0; });
    charts.cover = SIR.chart('cCover', { type: 'bar', data: { labels: [L('A: project mapping'), L('B: strict')], datasets: [
        { label: L('Placed in a group'), data: [c.A.coverage_pct, c.B.coverage_pct], $token: '--fill-navy' },
        { label: L('Spans groups'), data: [c.A.cross_pct, c.B.cross_pct], $token: '--fill-amber' },
        { label: L('No caste information (Devi, Kumar…)'), data: [c.A.no_information_pct, c.B.no_information_pct], $token: '--fill-grey' },
        { label: L('Not in either list'), data: [c.A.unmatched_pct, c.B.unmatched_pct], $token: '--fill-other' }] },
      options: { indexAxis: 'y', scales: { x: { stacked: true, max: 100, title: { display: true, text: L('% of all removals') } }, y: { stacked: true } } } });
    charts.comp = SIR.chart('cComp', { type: 'bar', data: { labels: GR.map(gl), datasets: [
        { label: L('A: project mapping'), data: GR.map(function (g) { return c.A.groups[g].share_of_classified; }), $token: '--fill-other' },
        { label: L('B: strict'), data: GR.map(function (g) { return c.B.groups[g].share_of_classified; }), $token: '--fill-navy' },
        { label: L('2023 survey'), data: GR.map(function (g) { return c.B.groups[g].survey_share; }), $token: '--fill-grey' }] },
      options: { scales: { y: { beginAtZero: true, title: { display: true, text: L('% of classified removals') } } } } });
    charts.bounds = SIR.chart('cBounds', { type: 'bar', data: { labels: GR.map(gl), datasets: [
        { label: L('Share of all removals, B (low to high)'), data: GR.map(function (g) { return [c.B.groups[g].share_low, c.B.groups[g].share_high]; }), $token: '--fill-navy' }] },
      options: { indexAxis: 'y', plugins: { legend: { display: false } }, scales: { x: { min: 0, max: 100, title: { display: true, text: L('% of all removals') } } } } });
    SIR.table(document.getElementById('tSur'), [
      { k: 'surname', label: L('Surname (as romanised in the lists)'), left: true }, { k: 'deleted', label: L('Removed'), fmt: SIR.n },
      { k: 'mapping', label: L('A: project mapping'), left: true }, { k: 'strict', label: L('B: strict'), left: true }
    ], c.top_surnames.map(function (x) { var nm = { none: L('no caste information'), cross: L('spans groups'), unmatched: L('not listed') }; return { surname: x.surname, deleted: x.deleted, mapping: nm[x.mapping] || x.mapping, strict: nm[x.strict] || x.strict }; }), { sort: 'deleted' });
    document.getElementById('fCaste').innerHTML = (function () {
      var gs = ['General', 'BC', 'EBC', 'SC', 'ST', 'Muslim'], up = [], down = [], split = [];
      gs.forEach(function (g) { var a = c.A.groups[g].ratio_to_survey, b = c.B.groups[g].ratio_to_survey; (a >= 1 && b >= 1 ? up : a < 1 && b < 1 ? down : split).push(g); });
      // "3.21 under A and 1.36 under B for General, 1.01 and 1.52 for SC and ..."
      var ratioList = function (list) {
        var parts = list.map(function (g, i) { var v = { g: gl(g), a: SIR.d(c.A.groups[g].ratio_to_survey, 2), b: SIR.d(c.B.groups[g].ratio_to_survey, 2) }; return i ? L('{a} and {b} for {g}', v) : L('{a} under A and {b} under B for {g}', v); });
        return parts.length < 2 ? parts.join('') : parts.slice(0, -1).join(', ') + L(' and ') + parts[parts.length - 1];
      };
      var and = function (list) { var a = list.map(gl); return a.length < 2 ? a.join('') : a.slice(0, -1).join(', ') + L(' and ') + a[a.length - 1]; };
      var ratios = ratioList(up.concat(down));
      return L('<b>Under both classifications, {up} families are removed at or above their share of Bihar\'s population, and {down} families below it.</b>', { up: and(up), down: and(down) }) + ' ' +
        (who === 'guardian' ? L('Using the surnames of fathers and husbands, the ratios to the 2023 survey share are {ratios}.', { ratios: ratios }) : L('Using the electors\' own surnames, the ratios to the 2023 survey share are {ratios}.', { ratios: ratios })) +
        (split.length ? ' ' + (split.length > 1 ? L('The two classifications disagree on {list}, with ratios of {ratios}, so no reading is offered for those groups.', { list: and(split), ratios: ratioList(split) }) : L('The two classifications disagree on {list}, with ratios of {ratios}, so no reading is offered for that group.', { list: and(split), ratios: ratioList(split) })) : '') +
        ' ' + L('Surnames shared by several castes cannot be placed, so these are shares of the removals each classification could place, {a} under A and {b} under B.', { a: SIR.pct(c.A.coverage_pct, 0), b: SIR.pct(c.B.coverage_pct, 0) });
    })();
  }
  drawCaste();
  document.querySelectorAll('[data-who]').forEach(function (b) { b.addEventListener('click', function () {
    who = b.getAttribute('data-who'); document.querySelectorAll('[data-who]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }); drawCaste(); }); });
  return SIR.json('data/bihar/tests.json').then(function (T) {
    var De = T.deaths, Ma = T.marriage;
    document.getElementById('kTests').innerHTML = [[SIR.d(De.years_of_deaths, 1), L('years of Bihar\'s adult deaths, in the names entered as dead')],
      [SIR.pct(De.women_share_dead), L('of those entered as dead were women')], [SIR.pct(De.women_share_expected), L('women\'s share of adult deaths, 2024')],
      [SIR.n(Ma.excess), L('more young women than young men marked shifted')]].map(function (k) { return '<div><b>' + k[0] + '</b><span>' + k[1] + '</span></div>'; }).join('');
    document.getElementById('fDeaths').innerHTML = L('<b>The {dead} names entered as dead equal about {y} years of adult deaths in Bihar.</b> At 2024 death rates, the state\'s population aged 20 and over has about {ad} deaths a year. The ages of those entered as dead are close to those of registered deaths. {o1} of those aged 25 or over were 70 or older, and {o2} of registered deaths at those ages in 2024. <b>Women are {wd} of those entered as dead, but {we} of adult deaths.</b> That is {wdn} women, where {wen} would be expected if the names matched the deaths the state actually has. Women were only {rw} of registered deaths at 25 and over in 2024, so women\'s deaths are registered less often and more of them may have stayed on the roll. The other possibility is that more women who are alive were entered as dead. The lists cannot tell the two apart.', {
      dead: SIR.lakh(De.dead_removed), y: SIR.d(De.years_of_deaths, 1), ad: SIR.lakh(De.adult_deaths), o1: SIR.pct(De.over70_share_dead), o2: SIR.pct(De.over70_share_registered),
      wd: SIR.pct(De.women_share_dead), we: SIR.pct(De.women_share_expected), wdn: SIR.lakh(De.women_dead), wen: SIR.lakh(De.women_expected), rw: SIR.pct(De.registered_women_share) });
    SIR.chart('cMarr', { type: 'scatter', data: { datasets: [{ label: L('Districts'), data: Ma.districts.map(function (d) { return { x: d.recent_marriage_pct, y: d.women_share, n: d.district }; }), $token: '--fill-navy', pointRadius: 4 }] },
      options: { plugins: { legend: { display: false }, tooltip: { callbacks: { label: function (c) { return L('{name}: {x} moved on marriage, {y} women', { name: c.raw.n, x: SIR.pct(c.raw.x), y: SIR.pct(c.raw.y) }); } } } },
        scales: { x: { title: { display: true, text: L('Women who moved on marriage in the ten years to 2011, % of women') } }, y: { title: { display: true, text: L('Women\'s share of those aged 18 to 29 marked shifted') } } } } });
    var rel = Math.abs(Ma.rho_share) < 0.2
      ? L('District by district, the share of women among the young marked shifted has no relationship with how much women moved on marriage (rank correlation {r}).', { r: SIR.d(Ma.rho_share, 2) })
      : (Ma.rho_share < 0
        ? L('District by district, the relationship runs the other way. Where more women had moved on marriage, women were a smaller share of the young marked shifted (rank correlation {r}).', { r: SIR.d(Ma.rho_share, 2) })
        : L('District by district, where more women had moved on marriage, women were a larger share of the young marked shifted (rank correlation {r}).', { r: SIR.d(Ma.rho_share, 2) }));
    document.getElementById('fMarr').innerHTML = L('<b>Among those aged 18 to 29 marked shifted, {f} were women and {m} men, so women outnumber men by {x}.</b> Marriage alone could account for a number that size. In the ten years before the 2011 census, {mr} women in Bihar moved on marriage, about {py} a year, so the excess is about {yrs} of one year\'s marriage moves. {rel} Women were the largest share in {top}. The census counts women in the district they moved to. So it measures marriage movement in general, and cannot show who left the roll at home. The figures are also fifteen years old.', {
      f: SIR.n(Ma.young_shifted_f), m: SIR.n(Ma.young_shifted_m), x: SIR.n(Ma.excess), mr: SIR.lakh(Ma.recent_marriage), py: SIR.lakh(Ma.recent_marriage_per_year), yrs: SIR.d(Ma.excess_years, 2), rel: rel, top: Ma.top.join(', ') });
  });
}).catch(SIR.fail);
