SIR.json('data/india/women.json').then(function (d) {
  var S = d.states, X = d.summary, p1 = function (x) { return SIR.d(x, 1); };
  var list = function (a) { return a.join(', ').replace(/, ([^,]*)$/, ' and $1'); };
  var over = S.filter(function (s) { return s.gap > 0; }), under = S.filter(function (s) { return s.gap < 0; });
  var big = S.filter(function (s) { return s.gap >= 1; });
  var top = S[0], dl = S.filter(function (s) { return s.state === 'Delhi'; })[0];
  var Q = { lists: 'counted from the lists', exact: 'official figures', rounded: 'official figures, rounded', proxy: 'an earlier roll as the base', unverified: 'a press analysis that names no source' };

  SIR.inShort([
    'In ' + over.length + ' of the ' + S.length + ' states and union territories that published the names left off by sex, women were a larger share of the names left off than of the roll. In ' + big.length + ' of them the gap was a point or more.',
    'The gap was widest in ' + top.state + ', ' + p1(top.gap) + ' points, where women were ' + p1(top.share_removed) + '% of the names left off and ' + p1(top.share_roll) + '% of the roll.' + (S[1] && top.gap - S[1].gap < 0.5 ? ' ' + S[1].state + ' came just behind, at ' + p1(S[1].gap) + ' points.' : '') + ' In ' + top.state + ' that is ' + p1(top.women_per_100) + ' of every 100 women against ' + p1(top.men_per_100) + ' of every 100 men.',
    'Below the state the pattern holds almost everywhere it can be followed. In ' + X.district_over + ' of ' + X.district_n + ' districts across Bihar, West Bengal, Kerala and Uttarakhand, women were a larger share of the district\'s count than of its roll.',
    'Delhi is the exception. ' + p1(dl.men_per_100) + ' of every 100 men were left off its draft roll, against ' + p1(dl.women_per_100) + ' of every 100 women.',
    'In Bihar women were ' + p1(d.bihar.dead_share) + '% of the names entered as dead. Their share of deaths in Bihar, from the death rates for women and men, would be about ' + p1(d.bihar.dead_expected) + '%.'
  ], 'The figures come from eleven states, and the table at the foot of the page says how good each one is. A reason on a list is what the officer wrote down, and nobody checked it.');

  document.getElementById('kpis').innerHTML = [
    [over.length + ' of ' + S.length, 'states where women were a larger share of the names left off than of the roll'],
    [p1(top.gap) + ' points', 'the widest gap, in ' + top.state],
    [X.district_over + ' of ' + X.district_n, 'districts, in four states, where the same was true'],
    [p1(d.bihar.dead_share) + '%', 'women among the names entered as dead in Bihar']
  ].map(function (k) { return '<div><b>' + k[0] + '</b><span>' + k[1] + '</span></div>'; }).join('');

  VIZ.dumbbell('vShare', { label: "Women's share of the roll before the revision and of the names left off, by state", min: 40, step: 5,
    aName: "Share of the roll before", aTok: '--fill-grey', bName: 'Share of the names left off', bTok: '--fill-red',
    rows: S.map(function (s) { return { name: s.state, a: s.share_roll, b: s.share_removed }; }) });
  document.getElementById('nShare').textContent = 'States are in order of the gap, widest first. Tamil Nadu\'s split by sex comes from a press analysis that names no source, and Kerala\'s base is the roll of January 2025, so read both with care. Bihar counts the first phase, the names left off the draft.';
  document.getElementById('fShare').innerHTML = '<b>Women were a larger share of the names left off than of the roll in ' + over.length + ' of ' + S.length + ' states.</b> In ' + list(S.filter(function (s) { return s.gap > 6; }).map(function (s) { return s.state; })) + ' the gap was more than six points. It was smaller in ' + list(S.filter(function (s) { return s.gap > 0 && s.gap <= 6; }).map(function (s) { return s.state; })) + '. Women were a smaller share of those left off than of the roll in ' + list(under.map(function (s) { return s.state; })) + '.';

  VIZ.dots('vRate', { label: 'Names left off per 100 women and per 100 men on the roll before the revision, by state', axis: 'Names left off per 100 electors of each sex',
    cats: S.map(function (s) { return s.state; }),
    series: [{ name: 'Per 100 men', col: '--fill-navy', vals: S.map(function (s) { return s.men_per_100; }) }, { name: 'Per 100 women', col: '--fill-red', vals: S.map(function (s) { return s.women_per_100; }) }] });
  var r13 = S.filter(function (s) { return s.ratio >= 1.3; });
  document.getElementById('nRate').textContent = 'In ' + list(r13.map(function (s) { return s.state; })) + ' a woman on the roll was at least 1.3 times as likely as a man to be left off the draft. In Delhi a man was ' + p1(dl.men_per_100 / dl.women_per_100) + ' times as likely as a woman.';

  var tokOf = function (v) { return v > 0 ? '--fill-red' : '--fill-grey'; };
  VIZ.strip('vDist', { label: "Women's share of each district's count less their share of its roll, in points", axis: 'Points above or below women\'s share of the roll', step: 5,
    key: [['Women a larger share than on the roll', '--fill-red'], ['Women a smaller share', '--fill-grey']],
    rows: d.districts.map(function (g) { return { name: g.state, points: g.rows.map(function (r) { return { v: r.gap, tok: tokOf(r.gap), label: r.district + ', ' + g.state + ': ' + (r.gap > 0 ? '+' : '') + p1(r.gap) + ' points' }; }) }; }) });
  document.getElementById('nDist').innerHTML = d.districts.map(function (g) {
    return 'In ' + g.state + ', counting the ' + g.measure + ', women were the larger share in ' + g.over + ' of ' + g.districts + ' districts.';
  }).join(' ') + ' In Uttarakhand the same held in ' + X.uk_acs_over + ' of its 70 constituencies, and in Kerala in ' + X.kl_acs_over + ' of 140.';

  VIZ.dots('vAfter', { label: "Women's share of the draft roll, of the names added after it and of the names deleted after it", axis: 'Per cent women',
    cats: d.after.map(function (a) { return a.state; }),
    series: [{ name: 'The draft roll', col: '--fill-grey', vals: d.after.map(function (a) { return a.draft; }) },
             { name: 'Added after the draft', col: '--fill-navy', vals: d.after.map(function (a) { return a.added; }) },
             { name: 'Deleted after the draft', col: '--fill-red', vals: d.after.map(function (a) { return a.removed; }) }] });
  var kl = d.after_added_only[0], up = d.after_added_only[1];
  var allUp = d.after.every(function (a) { return a.removed > a.draft && a.removed > a.added; });
  document.getElementById('nAfter').textContent = (allUp ? 'In all three, women were a larger share of the names deleted after the draft than of the draft roll itself, and a larger share of those deleted than of those added. ' : '') + 'Kerala published only the additions by sex, and women were ' + p1(kl.added) + '% of them. In Uttar Pradesh women were ' + p1(up.added) + '% of the rise from the draft to the final roll, against ' + p1(up.draft) + '% of the draft.';

  var B = d.bihar;
  VIZ.dumbbell('vBihar', { label: "Women's share in Bihar, expected and on the lists", min: 40, step: 5,
    aName: 'Expected from death rates, or share of the roll', aTok: '--fill-grey', bName: 'Share on the lists', bTok: '--fill-red',
    rows: [{ name: 'Entered as dead', a: B.dead_expected, b: B.dead_share },
           { name: 'Left off the draft', a: B.roll_before, b: B.removed_draft },
           { name: 'Deleted after the draft', a: B.draft, b: B.removed_after },
           { name: 'Added after the draft', a: B.draft, b: B.added }] });
  document.getElementById('nBihar').textContent = 'The names entered as dead come to about ' + p1(B.years_of_deaths) + ' years of adult deaths in Bihar. Women were ' + p1(B.dead_share) + '% of them. Bihar\'s death rates for women and men give an expected share of ' + p1(B.dead_expected) + '%, because more men than women die each year at most adult ages. So more women were entered as dead than the death rates would lead anyone to expect.';
  document.getElementById('nMarriage').textContent = 'Marriage is the second explanation worth testing, because a woman in Bihar usually moves to her husband\'s village when she marries. Young women were marked as shifted far more often than young men. The excess comes to ' + SIR.lakh(B.marriage_excess) + ' names, equal to about ' + Math.round(B.marriage_years * 12) + ' months of moves on marriage at the rate the 2011 Census counted them. The districts where young women were marked shifted most often are not the districts where marriage moves are most common. The rank correlation between the two is ' + SIR.d(B.marriage_rho, 2) + ', so marriage does not account for the pattern district by district.';

  SIR.table('tQual', [{ h: 'State' }, { h: 'Women, share of the roll', num: true }, { h: 'Women, share left off', num: true }, { h: 'Gap, points', num: true }, { h: 'Source' }],
    S.map(function (s) { return [s.source_url ? '<a href="' + SIR.esc(s.source_url) + '" rel="noopener">' + SIR.esc(s.state) + '</a>' : SIR.esc(s.state), p1(s.share_roll) + '%', p1(s.share_removed) + '%', p1(s.gap), Q[s.quality] || s.quality]; }));
  SIR.showFaq('india', 'women');
}).catch(SIR.fail);
