(function () {
  var X = DASH, n = X.n, d = X.d, pct = X.pct, lakh = X.lakh, esc = X.esc, sum = X.sum, median = X.median, rho = X.rho;
  var C = X.C, kpis = X.kpis, banner = X.banner, card = X.card, section = X.section, grid = X.grid, barOpts = X.barOpts, hbar = X.hbar, chart = X.chart;
  var main = document.getElementById('content');
  var ACC = ['#8B1E3F', '#0E5E6F', '#E0A526', '#1F618D', '#8E7CC3'];

  Promise.all([SIR.json('data/hyderabad/summary.json'), SIR.json('data/hyderabad/parts.json'), SIR.json('data/hyderabad/telangana.json')]).then(function (r) {
    var TGS = r[2].seats, S = r[0], A = S.acs, t = S.totals, names = A.map(function (a) { return a.name; });
    var F = r[1].fields, PR = r[1].rows.map(function (row) { var o = {}; F.forEach(function (f, i) { o[f] = row[i]; }); if (o.locality === 'nan') o.locality = null; return o; });
    var byName = {}; A.forEach(function (a) { byName[a.name] = a; });
    var s = function (f) { return sum(A, f); };
    var LK = A.filter(function (a) { return a.linked; });
    var ageAll = S.bands.map(function (b, i) { return 100 * s(function (a) { return a.counts.age_asd[i]; }) / s(function (a) { return a.age_all[i]; }); });
    var reasonTot = S.reasons.map(function (k) { return s(function (a) { return a.reasons[k]; }); });
    var rsh = function (k) { return 100 * s(function (a) { return a.reasons[k]; }) / t.deleted; };
    var untrAC = A.map(function (a) { return 100 * a.reasons['Untraceable/Absent'] / a.deleted; });
    var overM = A.filter(function (a) { return a.deleted > a.e2023.margin; }), overV = A.filter(function (a) { return a.e2023.deleted_over_valid > 100; });
    var yak = byName.Yakutpura;
    var hin = 100 * s(function (a) { return a.counts.hin_asd; }) / s(function (a) { return a.counts.hin_all; });
    var mus = 100 * s(function (a) { return a.counts.mus_asd; }) / s(function (a) { return a.counts.mus_all; });
    var HM = A.map(function (a) { return a.within_part.hindu_minus_muslim; });
    var hmParts = sum(HM, 'parts'), hmA = sum(HM, 'a_higher');
    var UL = LK.map(function (a) { return a.within_part.unlinked_minus_linked; });
    var ulParts = sum(UL, 'parts'), ulA = sum(UL, 'a_higher');
    var lkRate = 100 * sum(LK, function (a) { return a.counts.lk_asd; }) / sum(LK, function (a) { return a.counts.lk_all; });
    var ulRate = 100 * sum(LK, function (a) { return a.deleted - a.counts.lk_asd; }) / sum(LK, function (a) { return a.electors - a.counts.lk_all; });
    var fRate = 100 * s(function (a) { return a.counts.f_asd; }) / s(function (a) { return a.counts.f_all; });
    var mRate = 100 * s(function (a) { return a.counts.m_asd; }) / s(function (a) { return a.counts.m_all; });
    var FM = A.map(function (a) { return a.within_part.female_minus_male.diff_pp; });
    var slots = s('slots'), heavy = A.slice().sort(function (a, b) { return b.max_slot - a.max_slot; })[0];
    var ruleTot = S.rules.map(function (k) { return s(function (a) { return a.rules[k] || 0; }); });
    var P100 = PR.filter(function (p) { return p.electors >= 100; });
    var over60 = P100.filter(function (p) { return p.rate > 60; });
    var minMax = function (arr) { return [Math.min.apply(null, arr), Math.max.apply(null, arr)]; };
    var rateRange = minMax(P100.map(function (p) { return p.rate; }));
    var mc = A.map(function (a) { return a.part_correlations.muslim_share_vs_rate; });
    var sortedRate = A.slice().sort(function (a, b) { return b.rate - a.rate; });
    var andList = function (xs) { return xs.length ? xs.reduce(function (acc, x) { return acc === null ? x : L('{a} and {b}', { a: acc, b: x }); }, null) : ''; };
    var html = '';

    // ============================================================ OVERVIEW
    chart('ov1', { type: 'bar', data: { labels: names, datasets: [
      { label: L('Left off'), data: A.map(function (a) { return a.rate; }), backgroundColor: C.red },
      { label: L('Kept, summoned to a hearing'), data: A.map(function (a) { return a.hearing_rate; }), backgroundColor: C.yellow },
      { label: L('Kept, untouched'), data: A.map(function (a) { return 100 - a.rate - a.hearing_rate - 100 * a.unaccounted / a.electors; }), backgroundColor: C.dblue }] },
      options: { indexAxis: 'y', plugins: { legend: { position: 'bottom' } }, scales: { x: { stacked: true, max: 100, title: { display: true, text: L('% of the pre-revision roll') } }, y: { stacked: true } } } });
    var ov2 = hbar(names, A.map(function (a) { return a.e2023.deleted_over_margin; }), ACC, L('Names left off ÷ 2023 winning margin (log scale)'));
    ov2.options.scales.x = { type: 'logarithmic', min: 1, title: ov2.options.scales.x.title };
    chart('ov2', ov2);
    chart('ov3', { type: 'bar', data: { labels: S.bands, datasets: [{ label: L('Left off'), data: ageAll.map(function (v) { return +v.toFixed(1); }), backgroundColor: C.maroon }] }, options: barOpts(L('Age band'), L('% of the band left off')) });
    chart('ov4', { type: 'bar', data: { labels: LK.map(function (a) { return a.name; }), datasets: [{ label: L('Linked to the 2002 roll'), data: LK.map(function (a) { return a.linked_rate; }), backgroundColor: C.ikat }, { label: L('No link to the 2002 roll'), data: LK.map(function (a) { return a.unlinked_rate; }), backgroundColor: C.red }] }, options: barOpts('', L('% left off'), { plugins: { legend: { position: 'bottom' } } }) });
    chart('ov5', { type: 'doughnut', data: { labels: S.reasons, datasets: [{ data: reasonTot, backgroundColor: [C.dblue, C.red, C.grey, C.gold] }] }, options: { plugins: { legend: { position: 'bottom' } } } });
    chart('ov6', { type: 'bar', data: { labels: names, datasets: [{ label: L('Median cases per slot'), data: A.map(function (a) { return a.median_slot; }), backgroundColor: C.ikat }, { label: L('Heaviest single slot'), data: A.map(function (a) { return a.max_slot; }), backgroundColor: C.maroon }] }, options: barOpts('', L('Cases listed for one hearing slot'), { plugins: { legend: { position: 'bottom' } } }) });
    html += section('overview',
      kpis([[n(t.electors), L('Electors on the pre-revision rolls')], [n(t.deleted), L('Left off')], [pct(t.rate), L('Of the rolls left off')], [n(t.hearing), L('Kept, summoned to a hearing')], [L('{a} of {b}', { a: overM.length, b: A.length }), L('Seats where names left off the draft exceed the 2023 margin')], [n(t.parts), L('Polling parts')]]) +
      '<div class="hubs"><a class="hub" href="explorer/"><b>' + L('Part explorer') + '</b><span>' + L('Any constituency and any of its {parts} polling parts, with every fate, reason and rule.', { parts: n(t.parts) }) + '</span></a><a class="hub" href="telangana/"><b>' + L('Hyderabad and Telangana') + '</b><span>' + L('The five seats against the rest of the city and the state.') + '</span></a><a class="hub" href="faq/"><b>' + L('Questions and answers') + '</b><span>' + L('The criticisms put to this analysis, answered from the lists.') + '</span></a><div class="hub"><b>' + L('The full report') + '</b><span>' + L('Part I on the five constituencies together, Part II a chapter for each, and what the Election Commission should do.') + '</span><span class="dl"><a href="report/">' + L('Read online') + '</a> · <a href="../reports/hyderabad-old-city-sir-2026-report.pdf" download>' + L('PDF') + '</a> · <a href="../reports/hyderabad-old-city-sir-2026-deck.pptx" download>' + L('Slides') + '</a></span></div></div>' +
      grid(
        card(1, 'ov1', L('What happened to each elector, by constituency'), L('Of {electors} electors on the rolls before the revision, {rate} were left off the draft. Another {hearing} stayed on the draft roll, the roll published after the exclusions, but were summoned to a hearing. {top} lost the largest share ({topRate}) and {bottom} the smallest ({bottomRate}).', { electors: n(t.electors), rate: pct(t.rate), hearing: pct(100 * t.hearing / t.electors), top: sortedRate[0].name, topRate: pct(sortedRate[0].rate), bottom: sortedRate[4].name, bottomRate: pct(sortedRate[4].rate) }) + (sortedRate[0].linked ? '' : ' ' + L('{top}\'s list is incomplete. On the state\'s own figures it lost {stRate} of its roll.', { top: sortedRate[0].name, stRate: pct(TGS.filter(function (x) { return x.name === sortedRate[0].name; })[0].rate) }))) +
        card(2, 'ov2', L('Names left off against the 2023 winning margin'), L('The winning margin is the winner\'s lead over the runner-up. In all {count} constituencies more names were left off the draft than that margin. {seat} lost {times} times its 2023 margin, and in {list} the names left off the draft outnumber every valid vote cast in 2023.', { count: A.length, seat: yak.name, times: d(yak.e2023.deleted_over_margin, 1), list: andList(overV.map(function (a) { return a.name; })) })) +
        card(3, 'ov3', L('Share left off, by age'), L('{old} of electors aged 80 and over were left off the draft, against {young} of those aged 18 to 24.', { old: pct(ageAll[7]), young: pct(ageAll[0]) })) +
        card(4, 'ov4', L('The link to the 2002 roll'), L('An elector is linked when their own name or a parent\'s can be found on the roll of 2002, the last intensive revision. A polling part is the smallest section of the roll. Inside the same part, electors with no link were left off the draft {lo} to {hi} points more often than linked electors.', { lo: d(Math.min.apply(null, UL.map(function (u) { return u.diff_pp; })), 0), hi: d(Math.max.apply(null, UL.map(function (u) { return u.diff_pp; })), 0) })) +
        card(5, 'ov5', L('Reasons the officers recorded'), L('Of the names left off the draft, {shifted} were marked "permanently shifted", {untraceable} "untraceable or absent", {dead} dead and {enrolled} enrolled elsewhere.', { shifted: pct(rsh('Permanently Shifted')), untraceable: pct(rsh('Untraceable/Absent')), dead: pct(rsh('Death')), enrolled: pct(rsh('Already enrolled')) })) +
        card(6, 'ov6', L('Cases listed for each hearing slot'), L('A slot is one sitting on the hearing schedule. The heaviest single slot listed {cases} cases, in {seat}. The lists do not record how long a slot lasted.', { cases: n(heavy.max_slot), seat: heavy.name }))
      ) +
      '<div class="card wide"><div class="card-title"><span>' + L('The five constituencies') + '</span></div><div class="twrap" tabindex="0" role="region" aria-label="' + L('The five constituencies') + '"><table><thead><tr><th scope="col" class="l">' + L('Constituency') + '</th><th scope="col">' + L('Electors') + '</th><th scope="col">' + L('Left off') + '</th><th scope="col">' + L('% left off') + '</th><th scope="col">' + L('% summoned') + '</th><th scope="col" class="l">' + L('2023 winner') + '</th><th scope="col">' + L('2023 margin') + '</th><th scope="col">' + L('Left off ÷ margin') + '</th><th scope="col">' + L('Left off ÷ valid votes') + '</th></tr></thead><tbody>' +
      A.map(function (a) { return '<tr><td class="l"><a href="explorer/#' + a.name + '">' + a.name + '</a></td><td>' + n(a.electors) + '</td><td>' + n(a.deleted) + '</td><td>' + d(a.rate, 1) + '</td><td>' + d(a.hearing_rate, 1) + '</td><td class="l">' + esc(a.e2023.winner) + '</td><td>' + n(a.e2023.margin) + '</td><td>' + d(a.e2023.deleted_over_margin, 1) + '×</td><td>' + d(a.e2023.deleted_over_valid, 1) + '%</td></tr>'; }).join('') +
      '</tbody></table></div><div class="chart-takeaway">' + X.ICON + ' ' + L('Each constituency name opens it in the part explorer.') + '</div></div>');

    // ============================================================ DELETIONS
    var tops = A.map(function (a) { return a.name; });
    chart('de1', { type: 'bar', data: { labels: names, datasets: S.reasons.map(function (k, i) { return { label: k, data: A.map(function (a) { return +(100 * a.reasons[k] / a.deleted).toFixed(1); }), backgroundColor: [C.dblue, C.red, C.grey, C.gold][i] }; }) }, options: { indexAxis: 'y', plugins: { legend: { position: 'bottom' } }, scales: { x: { stacked: true, max: 100, title: { display: true, text: L('% of names left off the draft') } }, y: { stacked: true } } } });
    chart('de2', { type: 'bar', data: { labels: names, datasets: [{ label: L('Left off'), data: A.map(function (a) { return a.deleted; }), backgroundColor: ACC }] }, options: barOpts('', L('Names left off')) });
    chart('de3', hbar(names, untrAC.map(function (v) { return +v.toFixed(1); }), C.red, L('"Untraceable or absent", % of names left off the draft')));
    chart('de4', { type: 'bar', data: { labels: names, datasets: [{ label: L('Deaths recorded'), data: A.map(function (a) { return a.reasons.Death; }), backgroundColor: C.grey }, { label: L('Left off, aged 70 and over'), data: A.map(function (a) { return a.counts.age_asd[6] + a.counts.age_asd[7]; }), backgroundColor: C.maroon }] }, options: barOpts('', L('Electors'), { plugins: { legend: { position: 'bottom' } } }) });
    chart('de5', { type: 'bar', data: { labels: names, datasets: [{ label: L('In none of the three fates'), data: A.map(function (a) { return a.unaccounted; }), backgroundColor: C.grey }] }, options: barOpts('', L('Electors')) });
    chart('de6', hbar(names, A.map(function (a) { return +(100 * a.reasons['Already enrolled'] / a.deleted).toFixed(1); }), C.gold, L('"Already enrolled", % of names left off the draft')));
    var deaths = s(function (a) { return a.reasons.Death; }), old70 = s(function (a) { return a.counts.age_asd[6] + a.counts.age_asd[7]; });
    var unA = minMax(untrAC);
    html += section('deletions',
      kpis([[pct(rsh('Permanently Shifted')), L('"Permanently shifted"')], [pct(rsh('Untraceable/Absent')), L('"Untraceable or absent"')], [pct(rsh('Death')), L('Dead')], [pct(rsh('Already enrolled')), L('Enrolled elsewhere')]]) +
      banner(L('Reasons recorded'), L('The list of the absent, shifted and dead, the ASD list, is the Election Commission\'s list of names to be left off the draft. It gives one reason for each name, and most say the elector moved. The share marked untraceable runs from {lo} to {hi} between constituencies. Those entries record only that the officer did not find the person.', { lo: pct(unA[0]), hi: pct(unA[1]) })) +
      grid(
        card(1, 'de1', L('Reasons, constituency by constituency'), L('The share marked untraceable or absent is {list}.', { list: A.map(function (a, i) { return L('{share} in {name}', { share: pct(untrAC[i]), name: a.name }); }).join(', ') })) +
        card(2, 'de2', L('Names left off in each constituency'), A.slice().sort(function (a, b) { return b.deleted - a.deleted; }).map(function (a) { return a.name + ' ' + n(a.deleted); }).join(', ') + '.') +
        card(3, 'de3', L('"Untraceable or absent" in each constituency'), L('{top} records {hi} of its exclusions as untraceable or absent, and {bottom} {lo}.', { top: A[untrAC.indexOf(unA[1])].name, hi: pct(unA[1]), bottom: A[untrAC.indexOf(unA[0])].name, lo: pct(unA[0]) })) +
        card(4, 'de4', L('Deaths recorded and older electors left off the draft'), L('{deaths} deaths were recorded, and {old} electors aged 70 and over were left off the draft, so death accounts for only part of the exclusions at the oldest ages.', { deaths: n(deaths), old: n(old70) })) +
        card(5, 'de5', L('Electors the lists do not account for'), L('Each elector on a roll should end up left off, summoned or untouched. These electors are in none of the three: {list}. {seat}\'s list is incomplete and is read by polling-station name.', { list: A.map(function (a) { return a.name + ' ' + n(a.unaccounted); }).join(', '), seat: 'Malakpet' })) +
        card(6, 'de6', L('Enrolled elsewhere'), L('Names left off because the elector is already enrolled on another roll make up {share} of all exclusions, the smallest of the four reasons.', { share: pct(rsh('Already enrolled')) }))
      ));

    // ============================================================ AGE AND SEX
    chart('ag1', { type: 'line', data: { labels: S.bands, datasets: A.map(function (a, i) { return { label: a.name, data: a.age_rate, borderColor: ACC[i], backgroundColor: ACC[i], tension: 0.3, pointRadius: 3 }; }) }, options: barOpts(L('Age band'), L('% left off'), { plugins: { legend: { position: 'bottom' } } }) });
    chart('ag2', { type: 'bar', data: { labels: S.bands, datasets: [{ label: L('Share of all names left off the draft'), data: S.bands.map(function (b, i) { return +(100 * s(function (a) { return a.counts.age_asd[i]; }) / t.deleted).toFixed(1); }), backgroundColor: C.ikat }] }, options: barOpts(L('Age band'), L('% of names left off the draft')) });
    chart('ag3', { type: 'bar', data: { labels: names, datasets: [{ label: L('Women'), data: A.map(function (a) { return a.female_rate; }), backgroundColor: C.pink }, { label: L('Men'), data: A.map(function (a) { return a.male_rate; }), backgroundColor: C.dblue }] }, options: barOpts('', L('% left off'), { plugins: { legend: { position: 'bottom' } } }) });
    chart('ag4', hbar(names, FM, FM.map(function (v) { return v > 0 ? C.pink : C.dblue; }), L('Women\'s rate minus men\'s, inside each part (points)')));
    chart('ag5', { type: 'bar', data: { labels: names, datasets: [{ label: L('Women, % of the roll'), data: A.map(function (a) { return a.female_share_roll; }), backgroundColor: C.grey }, { label: L('Women, % of those left off'), data: A.map(function (a) { return a.female_share_deleted; }), backgroundColor: C.pink }] }, options: barOpts('', '%', { plugins: { legend: { position: 'bottom' } }, scales: { y: { min: 40, max: 55, title: { display: true, text: '%' } } } }) });
    chart('ag6', hbar(names, A.map(function (a) { return a.age_rate[7]; }), C.maroon, L('% of electors aged 80+ left off')));
    var a80 = minMax(A.map(function (a) { return a.age_rate[7]; })), a18 = minMax(A.map(function (a) { return a.age_rate[0]; }));
    html += section('age',
      kpis([[pct(ageAll[7]), L('Aged 80+ left off')], [pct(ageAll[0]), L('Aged 18 to 24 left off')], [pct(fRate), L('Women left off')], [pct(mRate), L('Men left off')]]) +
      banner(L('Age and sex'), L('In every constituency, the older the elector, the likelier the exclusion. Between {oldLo} and {oldHi} of electors aged 80 and over were left off the draft, and {youngLo} to {youngHi} of those aged 18 to 24. Women and men were left off the draft at similar rates.', { oldLo: pct(a80[0]), oldHi: pct(a80[1]), youngLo: pct(a18[0]), youngHi: pct(a18[1]) })) +
      grid(
        card(1, 'ag1', L('Share left off by age, in each constituency'), L('The rate roughly doubles between ages 18 to 24 and 30 to 39, when almost nobody dies, so death does not explain it all.')) +
        card(2, 'ag2', L('Those left off, by age'), L('How the names left off the draft divide among the age bands.')) +
        card(3, 'ag3', L('Women and men left off'), L('Women {women}, men {men} across the five constituencies.', { women: pct(fRate), men: pct(mRate) })) +
        card(4, 'ag4', L('Women against men, inside the same polling part'), L('Comparing inside a part holds the neighbourhood constant. The gap runs from {lo} to {hi} points and changes sign between constituencies.', { lo: d(Math.min.apply(null, FM), 1), hi: d(Math.max.apply(null, FM), 1) })) +
        card(5, 'ag5', L('Women\'s share of the roll and of those left off'), L('Women\'s share of those left off sits close to their share of the roll in every constituency.')) +
        card(6, 'ag6', L('Electors aged 80 and over left off'), A.map(function (a) { return a.name + ' ' + pct(a.age_rate[7]); }).join(', ') + '.')
      ));

    // ============================================================ RELIGION
    chart('re1', { type: 'bar', data: { labels: names, datasets: [{ label: L('Hindu names'), data: A.map(function (a) { return a.hindu_rate; }), backgroundColor: C.gold }, { label: L('Muslim names'), data: A.map(function (a) { return a.muslim_rate; }), backgroundColor: C.india }] }, options: barOpts('', L('% left off'), { plugins: { legend: { position: 'bottom' } } }) });
    chart('re2', hbar(names, HM.map(function (w) { return w.diff_pp; }), C.dblue, L('Hindu-name rate minus Muslim-name rate, inside each part (points)')));
    var sc = P100.filter(function (p) { return p.muslim_share_roll != null; });
    chart('re3', { type: 'scatter', data: { datasets: A.map(function (a, i) { return { label: a.name, data: sc.filter(function (p) { return p.ac === a.name; }).map(function (p) { return { x: p.muslim_share_roll, y: p.rate }; }), backgroundColor: ACC[i], pointRadius: 2.5 }; }) }, options: { plugins: { legend: { position: 'bottom' } }, scales: { x: { min: 0, max: 100, title: { display: true, text: L('Muslim-name share of the part\'s roll (%)') } }, y: { title: { display: true, text: L('% of the part left off') } } } } });
    chart('re4', hbar(names, mc, C.purple, L('Rank correlation across parts: Muslim share and exclusion rate')));
    chart('re5', hbar(names, A.map(function (a) { return a.muslim_share_roll; }), C.india, L('Muslim-name share of the pre-revision roll (%)')));
    chart('re6', { type: 'bar', data: { labels: names, datasets: [{ label: L('Parts where Hindu-name rate was higher'), data: HM.map(function (w) { return w.a_higher; }), backgroundColor: C.gold }, { label: L('Parts where Muslim-name rate was higher'), data: HM.map(function (w) { return w.b_higher; }), backgroundColor: C.india }] }, options: { plugins: { legend: { position: 'bottom' } }, scales: { x: { stacked: true }, y: { stacked: true, title: { display: true, text: L('Polling parts') } } } } });
    var hmR = minMax(HM.map(function (w) { return w.diff_pp; })), mcR = minMax(mc);
    html += section('religion',
      kpis([[pct(hin), L('Hindu-name electors left off the draft')], [pct(mus), L('Muslim-name electors left off the draft')], [L('{a} of {b}', { a: hmA, b: hmParts }), L('Comparable parts where the Hindu-name rate was higher')], [pct(100 * s(function (a) { return a.counts.mus_all; }) / t.electors), L('Muslim-name share of the rolls')]]) +
      banner(L('Religion'), L('Across the five constituencies {hindu} of Hindu-name electors were left off the draft, and {muslim} of Muslim-name electors. Inside the same polling part the gap is {lo} to {hi} points in the same direction. Religion is guessed from names, and the lists give religion and age separately, so part of the gap may come from age.', { hindu: pct(hin), muslim: pct(mus), lo: d(hmR[0], 1), hi: d(hmR[1], 1) })) +
      grid(
        card(1, 're1', L('Hindu-name and Muslim-name electors left off the draft'), L('Hindu-name electors were left off the draft more often in every constituency.')) +
        card(2, 're2', L('The religion gap inside each part'), L('The gap holds inside the same part, at {lo} to {hi} points, pooled across parts with at least 20 of each group.', { lo: d(hmR[0], 1), hi: d(hmR[1], 1) })) +
        card(3, 're3', L('Muslim-name share of a part against its exclusion rate'), L('Parts with more Muslim-name electors lost a smaller share of their roll. Each dot is a polling part with at least 100 electors.'), { size: 'tall' }) +
        card(4, 're4', L('How strong that pattern is'), L('A rank correlation, from -1 to 1, measures how closely the parts\' order on one measure follows their order on another. A negative value means the exclusion rate falls as the Muslim-name share rises. Here it runs from {lo} to {hi}, negative in every constituency.', { lo: d(mcR[0], 2), hi: d(mcR[1], 2) }), { size: 'tall' }) +
        card(5, 're5', L('Muslim-name share of each roll'), L('Share of each roll before the revision whose names are classified Muslim.')) +
        card(6, 're6', L('Parts where the gap runs each way'), L('The Hindu-name rate was higher in {a} of the {b} parts large enough to compare.', { a: hmA, b: hmParts }))
      ));

    // ============================================================ 2002 LINK
    chart('li1', { type: 'bar', data: { labels: LK.map(function (a) { return a.name; }), datasets: [{ label: L('Linked'), data: LK.map(function (a) { return a.linked_rate; }), backgroundColor: C.ikat }, { label: L('Not linked'), data: LK.map(function (a) { return a.unlinked_rate; }), backgroundColor: C.red }] }, options: barOpts('', L('% left off'), { plugins: { legend: { position: 'bottom' } } }) });
    chart('li2', hbar(LK.map(function (a) { return a.name; }), UL.map(function (u) { return u.diff_pp; }), C.red, L('Unlinked rate minus linked rate, inside each part (points)')));
    chart('li3', hbar(LK.map(function (a) { return a.name; }), LK.map(function (a) { return a.linked_share_roll; }), C.ikat, L('% of the roll linked to 2002')));
    chart('li4', { type: 'bar', data: { labels: LK.map(function (a) { return a.name; }), datasets: [{ label: L('Parts where unlinked electors fared worse'), data: UL.map(function (u) { return u.a_higher; }), backgroundColor: C.red }, { label: L('Parts where linked electors fared worse'), data: UL.map(function (u) { return u.b_higher; }), backgroundColor: C.ikat }] }, options: { plugins: { legend: { position: 'bottom' } }, scales: { x: { stacked: true }, y: { stacked: true, title: { display: true, text: L('Polling parts') } } } } });
    chart('li5', hbar(names, A.map(function (a) { return a.nomap; }), C.maroon, L('Kept, on the no-mapping list')));
    chart('li6', { type: 'doughnut', data: { labels: [L('Linked, left off'), L('Linked, kept'), L('Not linked, left off'), L('Not linked, kept')], datasets: [{ data: [sum(LK, function (a) { return a.counts.lk_asd; }), sum(LK, function (a) { return a.counts.lk_all - a.counts.lk_asd; }), sum(LK, function (a) { return a.deleted - a.counts.lk_asd; }), sum(LK, function (a) { return (a.electors - a.counts.lk_all) - (a.deleted - a.counts.lk_asd); })], backgroundColor: [C.ikat, '#9CC5CE', C.red, '#E6A39A'] }] }, options: { plugins: { legend: { position: 'bottom' } } } });
    var ulR = minMax(UL.map(function (u) { return u.diff_pp; }));
    html += section('link',
      kpis([[pct(ulRate), L('Unlinked electors left off the draft')], [pct(lkRate), L('Linked electors left off the draft')], [L('+{lo} to +{hi}', { lo: d(ulR[0], 0), hi: d(ulR[1], 0) }), L('Points more, inside the same part')], [L('{a} of {b}', { a: n(ulA), b: n(ulParts) }), L('Parts where unlinked electors fared worse')]]) +
      banner(L('The 2002 roll'), L('The revision asks each elector to show a link to the 2002 intensive revision, through their own name or a parent\'s. Electors with no link were about twice as likely to be left off the draft, and the gap holds inside the same polling part in {a} of {b} parts. Anyone who moved to the city after 2002, or whose family name is spelt differently on the old roll, starts at a disadvantage. {seat}\'s list does not record the link.', { a: n(ulA), b: n(ulParts), seat: 'Malakpet' })) +
      grid(
        card(1, 'li1', L('Linked and unlinked electors left off the draft'), L('{linked} of linked electors were left off the draft and {unlinked} of unlinked electors, in the four constituencies whose lists record the link.', { linked: pct(lkRate), unlinked: pct(ulRate) })) +
        card(2, 'li2', L('The link gap inside each part'), L('Unlinked rate minus linked rate inside the same part, in points: {list}.', { list: LK.map(function (a, i) { return a.name + ' +' + d(UL[i].diff_pp, 1); }).join(', ') })) +
        card(3, 'li3', L('Share of each roll linked to 2002'), L('About half of each roll links to 2002.')) +
        card(4, 'li4', L('Parts where unlinked electors fared worse'), L('Unlinked electors were left off the draft more often in {a} of {b} parts.', { a: n(ulA), b: n(ulParts) })) +
        card(5, 'li5', L('Kept electors on the no-mapping list'), L('The no-mapping list holds electors who could not be traced to the last intensive revision. {count} electors kept on the draft roll were put on it and summoned to prove their link.', { count: n(s('nomap')) })) +
        card(6, 'li6', L('Linked and unlinked, left off and kept'), L('Electors in the four constituencies with linkage, by link and by fate.'))
      ));

    // ============================================================ HEARINGS
    var days = {}; A.forEach(function (a) { a.daily.forEach(function (x) { days[x[0]] = (days[x[0]] || 0) + x[1]; }); });
    var mon = { Aug: 8, Sep: 9, Oct: 10 }, dk = Object.keys(days).sort(function (p, q) { var a = p.split(' '), b = q.split(' '); return (mon[a[1]] * 100 + +a[0]) - (mon[b[1]] * 100 + +b[0]); });
    chart('he1', hbar(names, A.map(function (a) { return a.hearing_rate; }), C.yellow, L('% of the pre-revision roll summoned')));
    chart('he2', hbar(S.rules, ruleTot, C.ikat, L('Electors flagged')));
    chart('he3', { type: 'bar', data: { labels: dk, datasets: [{ label: L('Cases listed'), data: dk.map(function (k) { return days[k]; }), backgroundColor: C.gold }] }, options: barOpts('', L('Cases listed per day')) });
    chart('he4', { type: 'bar', data: { labels: names, datasets: [{ label: L('Median cases per slot'), data: A.map(function (a) { return a.median_slot; }), backgroundColor: C.ikat }, { label: L('Heaviest single slot'), data: A.map(function (a) { return a.max_slot; }), backgroundColor: C.maroon }] }, options: barOpts('', L('Cases per slot'), { plugins: { legend: { position: 'bottom' } } }) });
    chart('he5', { type: 'bar', data: { labels: names, datasets: S.rules.map(function (k, i) { return { label: k, data: A.map(function (a) { return a.rules[k] || 0; }), backgroundColor: [C.maroon, C.ikat, C.gold, C.dblue, C.purple, C.grey, C.pink][i] }; }) }, options: { indexAxis: 'y', plugins: { legend: { position: 'bottom' } }, scales: { x: { stacked: true, title: { display: true, text: L('Flags') } }, y: { stacked: true } } } });
    chart('he6', hbar(names, A.map(function (a) { return a.slots; }), C.dblue, L('Hearing slots scheduled')));
    var peak = dk.reduce(function (m, k) { return days[k] > days[m] ? k : m; }, dk[0]);
    html += section('hearings',
      kpis([[n(t.hearing), L('Kept, summoned to a hearing')], [pct(100 * t.hearing / t.electors), L('Of the pre-revision roll')], [n(slots), L('Hearing slots')], [n(heavy.max_slot), L('Cases in the heaviest single slot')]]) +
      banner(L('Hearings'), L('An elector kept on the draft roll could still be summoned to prove eligibility. {count} were. Not being traceable to the last intensive revision was the commonest reason, {share} of flags. The heaviest single slot listed {cases} cases, in {seat}, where the typical slot listed {median}.', { count: n(t.hearing), share: pct(100 * ruleTot[0] / sum(ruleTot, function (x) { return x; })), cases: n(heavy.max_slot), seat: heavy.name, median: n(heavy.median_slot) })) +
      grid(
        card(1, 'he1', L('Share of each roll summoned'), L('{list} of each roll.', { list: A.map(function (a) { return a.name + ' ' + pct(a.hearing_rate); }).join(', ') })) +
        card(2, 'he2', L('Rules that sent electors to a hearing'), L('One elector can carry more than one rule, so the flags sum to more than the people summoned.'), { size: 'tall' }) +
        card(3, 'he3', L('Cases listed each day'), L('The busiest day, {day}, listed {cases} cases across the five constituencies.', { day: peak.replace(/^0/, ''), cases: n(days[peak]) }), { size: 'tall' }) +
        card(4, 'he4', L('Cases per slot'), L('Cases in the typical (median) slot, by constituency: {list}.', { list: A.map(function (a) { return a.name + ' ' + n(a.median_slot); }).join(', ') })) +
        card(5, 'he5', L('Rules, constituency by constituency'), L('Flags under each rule, constituency by constituency.'), { size: 'tall' }) +
        card(6, 'he6', L('Hearing slots scheduled'), L('{slots} slots across the five constituencies, 28 August to 12 October.', { slots: n(slots) }))
      ));

    // ============================================================ PARTS
    var bins = [0, 20, 30, 40, 50, 60, 70, 101], binL = [L('under 20%'), '20–30%', '30–40%', '40–50%', '50–60%', '60–70%', '70% +'];
    chart('pa1', { type: 'bar', data: { labels: binL, datasets: [{ label: L('Parts'), data: binL.map(function (l, i) { return P100.filter(function (p) { return p.rate >= bins[i] && p.rate < bins[i + 1]; }).length; }), backgroundColor: binL.map(function (l, i) { return i >= 5 ? C.red : C.ikat; }) }] }, options: barOpts(L('Share of the part left off'), L('Polling parts')) });
    chart('pa2', { type: 'bar', data: { labels: names, datasets: [{ label: L('Lowest to highest part'), data: A.map(function (a) { var q = a.part_rate_quartiles; return [q[0], q[4]]; }), backgroundColor: 'rgba(149,165,166,0.45)', barPercentage: 0.5 }, { label: L('Middle half of parts'), data: A.map(function (a) { var q = a.part_rate_quartiles; return [q[1], q[3]]; }), backgroundColor: C.maroon, barPercentage: 0.5 }] }, options: { indexAxis: 'y', plugins: { legend: { position: 'bottom' } }, scales: { x: { min: 0, max: 100, title: { display: true, text: L('% of the part left off') } }, y: { stacked: true } } } });
    chart('pa3', hbar(names, A.map(function (a) { return a.parts_over_60; }), C.red, L('Parts that lost more than 60% of their roll')));
    var topP = P100.slice().sort(function (a, b) { return b.rate - a.rate; }).slice(0, 15);
    chart('pa4', hbar(topP.map(function (p) { return p.ac + ' ' + p.part + (p.locality ? ' · ' + p.locality : ''); }), topP.map(function (p) { return p.rate; }), topP.map(function (p) { return ACC[names.indexOf(p.ac)]; }), L('% of the part left off')));
    var su = P100.filter(function (p) { return p.untraceable_share_of_deleted != null && p.deleted >= 20; });
    chart('pa5', { type: 'scatter', data: { datasets: A.map(function (a, i) { return { label: a.name, data: su.filter(function (p) { return p.ac === a.name; }).map(function (p) { return { x: p.untraceable_share_of_deleted, y: p.rate }; }), backgroundColor: ACC[i], pointRadius: 2.5 }; }) }, options: { plugins: { legend: { position: 'bottom' } }, scales: { x: { min: 0, max: 100, title: { display: true, text: L('"Untraceable", % of the part\'s exclusions') } }, y: { title: { display: true, text: L('% of the part left off') } } } } });
    chart('pa6', hbar(names, A.map(function (a) { return a.part_correlations.untraceable_share_vs_rate; }), C.grey, L('Rank correlation across parts: untraceable share and exclusion rate')));
    html += section('parts',
      kpis([[n(t.parts), L('Polling parts')], [L('{lo}% to {hi}%', { lo: d(rateRange[0], 0), hi: d(rateRange[1], 0) }), L('Range of part exclusion rates')], [over60.length, L('Parts that lost more than 60%')], [pct(median(P100.map(function (p) { return p.rate; }))), L('Exclusion rate in the typical part')]]) +
      banner(L('Polling parts'), L('Part exclusion rates run from {lo}% to {hi}%, and {count} parts lost more than 60% of their roll: {list}.', { lo: d(rateRange[0], 0), hi: d(rateRange[1], 0), count: over60.length, list: A.filter(function (a) { return a.parts_over_60; }).map(function (a) { return L('{count} in {name}', { count: a.parts_over_60, name: a.name }); }).join(', ') })) +
      grid(
        card(1, 'pa1', L('How part rates are spread'), L('Parts with at least 100 electors, by the share of their roll left off.')) +
        card(2, 'pa2', L('Range of part rates in each constituency'), L('The bar runs from the lowest part to the highest, and the dark band covers the middle half.')) +
        card(3, 'pa3', L('Parts that lost more than 60% of their roll'), A.map(function (a) { return a.name + ' ' + a.parts_over_60; }).join(', ') + '.') +
        card(4, 'pa4', L('The fifteen heaviest parts'), L('These fifteen parts lost the largest shares of their rolls. Each can be opened in the part explorer.'), { size: 'tall' }) +
        card(5, 'pa5', L('"Untraceable" against the part\'s exclusion rate'), L('The share of a part\'s exclusions entered as untraceable hardly rises with its exclusion rate.'), { size: 'tall' }) +
        card(6, 'pa6', L('How strong that relationship is'), L('Rank correlations by constituency: {list}.', { list: A.map(function (a) { return a.name + ' ' + d(a.part_correlations.untraceable_share_vs_rate, 2); }).join(', ') }), { size: 'tall' })
      ) +
      '<div class="card wide"><div class="card-title"><span>' + L('All {count} parts', { count: n(PR.length) }) + '</span></div><div class="search"><label for="partq">' + L('Find a part or locality') + '</label><input id="partq" type="search" placeholder="' + L('e.g. {place}', { place: 'Kalikaman' }) + '"></div><div class="twrap scroll" tabindex="0" role="region" aria-label="' + L('All polling parts') + '"><table id="partTable"></table></div><div class="chart-takeaway">' + X.ICON + ' ' + L('Click a column heading to sort the table. Each part number opens that part in the part explorer. {seat} is listed by polling station.', { seat: 'Malakpet' }) + '</div></div>');

    // ============================================================ ELECTORAL
    chart('el1', { type: 'bar', data: { labels: names, datasets: [{ label: L('2023 winning margin'), data: A.map(function (a) { return a.e2023.margin; }), backgroundColor: C.grey }, { label: L('Names left off'), data: A.map(function (a) { return a.deleted; }), backgroundColor: C.red }] }, options: barOpts('', L('Votes or names'), { plugins: { legend: { position: 'bottom' } } }) });
    chart('el2', { type: 'bar', data: { labels: names, datasets: [{ label: L('Valid votes cast, 2023'), data: A.map(function (a) { return a.e2023.valid; }), backgroundColor: C.ikat }, { label: L('Names left off'), data: A.map(function (a) { return a.deleted; }), backgroundColor: C.red }] }, options: barOpts('', L('Votes or names'), { plugins: { legend: { position: 'bottom' } } }) });
    chart('el3', hbar(names, A.map(function (a) { return a.e2023.deleted_over_valid; }), A.map(function (a) { return a.e2023.deleted_over_valid > 100 ? C.red : C.gold; }), L('Names left off as % of valid votes cast in 2023')));
    chart('el4', { type: 'bar', data: { labels: names, datasets: [{ label: L('Winner\'s votes, 2023'), data: A.map(function (a) { return a.e2023.winner_votes; }), backgroundColor: C.dblue }, { label: L('Names left off'), data: A.map(function (a) { return a.deleted; }), backgroundColor: C.red }] }, options: barOpts('', L('Votes or names'), { plugins: { legend: { position: 'bottom' } } }) });
    html += section('electoral',
      kpis([[L('{a} of {b}', { a: overM.length, b: A.length }), L('Seats where names left off the draft exceed the 2023 margin')], [L('{a} of {b}', { a: overV.length, b: A.length }), L('Seats where they exceed all valid votes cast')], [n(yak.e2023.margin), L('{seat}\'s 2023 margin', { seat: yak.name })], [n(yak.deleted), L('Names left off in {seat}', { seat: yak.name })]]) +
      banner(L('Electoral stakes'), L('Every constituency lost more names than its 2023 winning margin, and in {list} the names left off the draft outnumber every valid vote cast in 2023. The next election will be held on the revised roll. These figures measure scale. The roll records nothing about how those left off would have voted.', { list: andList(overV.map(function (a) { return a.name; })) })) +
      grid(
        card(1, 'el1', L('Names left off against the margin'), A.map(function (a) { return a.name + ' ' + d(a.e2023.deleted_over_margin, 1) + '×'; }).join(', ') + '.') +
        card(2, 'el2', L('Names left off against the votes cast'), L('Names left off as a share of valid votes: {list}.', { list: A.map(function (a) { return a.name + ' ' + d(a.e2023.deleted_over_valid, 0) + '%'; }).join(', ') })) +
        card(3, 'el3', L('Seats where exclusions exceed the whole vote'), andList(overV.map(function (a) { return a.name; })) + '.') +
        card(4, 'el4', L('Against the winner\'s own vote'), L('In {a} of {b} constituencies more names were left off the draft than the winner received in 2023.', { a: A.filter(function (a) { return a.deleted > a.e2023.winner_votes; }).length, b: A.length }))
      ));

    // ============================================================ RESEARCH
    var RQ = [
      [L('How many names were left off the draft, and where?'), L('{deleted} of {electors} electors on the five pre-revision rolls, {rate}. By constituency: {list}.', { deleted: n(t.deleted), electors: n(t.electors), rate: pct(t.rate), list: sortedRate.map(function (a) { return a.name + ' ' + pct(a.rate); }).join(', ') })],
      [L('Did the exclusions exceed the margins that decided seats?'), L('{seat} was won by {margin} votes and lost {lost} names. In all {count} constituencies the names left off the draft exceed the 2023 winning margin, and in {list} they exceed every valid vote cast in 2023.', { count: A.length, seat: yak.name, margin: n(yak.e2023.margin), lost: n(yak.deleted), list: andList(overV.map(function (a) { return a.name; })) })],
      [L('Who carried the burden?'), L('{old} of electors aged 80 and over were left off the draft. Electors with no link to the 2002 roll were left off the draft {lo} to {hi} points more often than linked electors in the same part. The burden fell hardest on these two groups.', { old: pct(ageAll[7]), lo: d(ulR[0], 0), hi: d(ulR[1], 0) })],
      [L('Were women left off more often than men?'), L('No. Women {women}, men {men}, and inside parts the gap runs one way in some constituencies and the other way in others.', { women: pct(fRate), men: pct(mRate) })],
      [L('Were Muslim-name electors left off the draft more often?'), L('No, less often. {hindu} of Hindu-name electors and {muslim} of Muslim-name electors were left off the draft, and inside the same part the gap runs the same way in {a} of {b} comparable parts. The lists cannot separate this from age.', { hindu: pct(hin), muslim: pct(mus), a: hmA, b: hmParts })],
      [L('Could the hearings be held as scheduled?'), L('{count} electors were summoned across {slots} slots, and the heaviest single slot listed {cases} cases. The lists record how many cases each slot listed and nothing about how long it lasted.', { count: n(t.hearing), slots: n(slots), cases: n(heavy.max_slot) })],
      [L('What should the Election Commission publish before the final roll?'), L('It should publish the basis for each exclusion entered as "untraceable or absent" and for each exclusion of an elector with no link to the 2002 roll. It should also publish, part by part, the names put back after hearings, before the final roll comes out.')]
    ];
    html += section('research', X.qa(RQ) + '<p><a href="faq/">' + L('More questions and answers') + '</a> · <a href="method/">' + L('Full method and the research questions') + '</a></p>');

    // ============================================================ METHODS
    html += section('methodology',
      '<div class="methodology"><h2>' + L('Data sources') + '</h2><ul><li>' + L('Pre-revision rolls, the list of the absent, shifted and dead, and the discrepancy and no-mapping lists: the Chief Electoral Officer (CEO), Telangana, for the five constituencies, September 2026, added up by polling part. The elector-by-elector lists were compiled for these five seats only, which is why the analysis covers five.') + '</li><li>' + L('Religion is guessed from each elector\'s name, because the roll does not record it. A second classification, made separately, agrees on 99% of names.') + '</li><li>' + L('Hearing schedules come from the same lists, 28 August to 12 October.') + '</li><li>' + L('2023 Assembly result: Election Commission of India.') + '</li></ul></div>' +
      '<div class="methodology"><h2>' + L('How the figures are built') + '</h2><p>' + L('The lists cover every elector on the roll before the revision, so each group\'s exclusion rate is exact and comes from no sample. A within-part difference compares two groups inside the same polling part, which holds the neighbourhood and the booth officer constant. The differences are pooled across parts with at least 20 of each group, and each part is weighted by its smaller group. Part counts add up exactly to the constituency totals.') + '</p></div>' +
      '<div class="methodology"><h2>' + L('What this shows and what it does not') + '</h2><p>' + L('The lists show how many electors were left off the draft and from which parts, with each person\'s age and sex, a religion guessed from the name, and whether they link to the 2002 roll. They cannot show whether any single exclusion was right. The {seat} list used here is incomplete and has no part numbers or 2002 link. These are the September lists, so names put back after hearings are not in these counts.', { seat: 'Malakpet' }) + '</p><p><a href="method/">' + L('Full method') + '</a></p></div>');

    main.innerHTML = html;

    // ------------------------------------------------------------------ parts table
    var cols = [['ac', L('Constituency'), 1], ['part', L('Part')], ['locality', L('Locality'), 1], ['electors', L('Electors')], ['deleted', L('Left off')], ['rate', L('% left off')], ['hearing_rate', L('% summoned')], ['muslim_share_roll', L('Muslim names %')], ['untraceable_share_of_deleted', L('Untraceable % of exclusions')]];
    var key = 'rate', dir = -1, q = '';
    function renderTable() {
      var list = PR.filter(function (p) { return !q || (p.ac + ' ' + p.part + ' ' + (p.locality || '')).toLowerCase().indexOf(q) >= 0; }).sort(function (a, b) { var x = a[key], y = b[key]; if (typeof x === 'string' || typeof y === 'string') return dir * String(x || '').localeCompare(String(y || '')); return dir * ((x == null ? -1e9 : x) - (y == null ? -1e9 : y)); });
      document.getElementById('partTable').innerHTML = '<thead><tr>' + cols.map(function (c) { return '<th scope="col" class="' + (c[2] ? 'l' : '') + '" aria-sort="' + (c[0] === key ? (dir < 0 ? 'descending' : 'ascending') : 'none') + '"><button type="button" data-k="' + c[0] + '">' + c[1] + '</button></th>'; }).join('') + '</tr></thead><tbody>' +
        list.map(function (p) { return '<tr><td class="l">' + p.ac + '</td><td><a href="explorer/#' + p.ac + '-' + p.part + '">' + p.part + '</a></td><td class="l">' + esc(p.locality || '–') + '</td><td>' + n(p.electors) + '</td><td>' + n(p.deleted) + '</td><td>' + d(p.rate, 1) + '</td><td>' + d(p.hearing_rate, 1) + '</td><td>' + d(p.muslim_share_roll, 0) + '</td><td>' + d(p.untraceable_share_of_deleted, 0) + '</td></tr>'; }).join('') + '</tbody>';
    }
    document.getElementById('partTable').addEventListener('click', function (e) { var b = e.target.closest('th button'); if (!b) return; var k = b.getAttribute('data-k'); dir = k === key ? -dir : -1; key = k; renderTable(); });
    document.getElementById('partq').addEventListener('input', function () { q = this.value.trim().toLowerCase(); renderTable(); });
    renderTable();

    DASH.start(main, 'hyderabad-sir');
  }).catch(function (e) { main.innerHTML = '<p role="alert">' + L('The dashboard data did not load ({msg}). Please reload the page.', { msg: esc(e.message) }) + '</p>'; });
})();
