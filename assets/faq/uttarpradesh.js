/* Questions and answers for the Uttar Pradesh pages, in English only for now.
   The FAQ tab shows them all; each page shows those tagged with its key (main,
   method, faq). The "In short" points for each page are in short. */
(function () {
  var P;
  SIR.faq('up', 'uttarpradesh/faq/', function () {
    return P || (P = Promise.all([SIR.json('data/uttarpradesh/summary.json'), SIR.json('data/uttarpradesh/districts.json'), SIR.json('data/uttarpradesh/analysis.json')]).then(function (r) {
      var s = r[0], D = r[1], A = r[2], X = A.sex, U = A.urban, M = A.margins, N = A.notices;
      var cr = function (x) { return (x / 1e7).toFixed(2) + ' crore'; }, lk = function (x) { return SIR.lk(x, 1); }, d1 = function (v) { return SIR.d(v, 1); };
      var last = D[D.length - 1], n0 = SIR.n;
      var scale = 'Uttar Pradesh\'s draft roll left off ' + cr(s.left_off) + ' names, ' + d1(s.per_100) + ' of every 100 electors on the roll of 27 October 2025.';
      var reasons = SIR.pct(s.shares.shifted) + ' were entered as permanently shifted, ' + SIR.pct(s.shares.untraceable_absent) + ' as untraceable or absent, ' + SIR.pct(s.shares.dead) + ' as dead and ' + SIR.pct(s.shares.multiple) + ' as already enrolled elsewhere.';
      var where = D[0].district + ' left off ' + d1(D[0].per_100) + ' of every 100 electors, the most of the 75 districts, and ' + s.over_20 + ' districts left off 20 or more. ' + last.district + ' left off the fewest, ' + d1(last.per_100) + '.';
      var after = 'The final roll of 10 April 2026 was ' + lk(s.net_rise) + ' larger than the draft, ' + SIR.pct(s.made_up_pct) + ' of what the draft left off. That rise counts new voters too, so it is the most that can have been put back.';
      var women = 'Women were ' + SIR.pct(X.women_share) + ' of the names left off and ' + SIR.pct(X.women_share_before) + ' of the roll before the revision. ' + d1(X.women_per_100) + ' of every 100 women on the roll were left off, against ' + d1(X.men_per_100) + ' of every 100 men, by the Chief Electoral Officer\'s rounded figures.';
      var towns = 'Urban areas lost ' + d1(U.urban_per_100) + ' of every 100 electors and rural areas ' + d1(U.rural_per_100) + ', by the Chief Electoral Officer\'s figures as the press reported them.';
      var margin = 'No count by constituency was published. If each district\'s names left off are shared out over its seats by their electors, the share is larger than the 2022 winning margin in ' + M.over + ' of the ' + M.n + ' seats. This estimates how many seats the names left off could have decided. It cannot say which seats, or that any result changed.';
      var notices = 'After the draft, notices went to ' + cr(N.all) + ' electors, ' + d1(N.per_100_draft) + ' of every 100 on it, and ' + lk(N.removed_after.no_response) + ' were deleted for not answering one.';
      var QA = [
        ['How many names were left off the draft in Uttar Pradesh?', scale + ' The draft roll is the list published once the enumeration forms were collected, and a name whose form did not come back was left off it. ' + reasons + ' A reason is what the officer wrote down, and nobody checked it.', ['main', 'faq']],
        ['Where were the most names left off?', where + ' The cities stand out. Lucknow, Ghaziabad, Kanpur Nagar and Meerut are four of the five districts that left off the most per 100 electors.', ['main', 'faq']],
        ['Were the names put back?', after + ' The final roll is the draft after the names added and deleted on claims and objections. A further ' + lk(s.removed_after) + ' were deleted after the draft, according to the press.', ['main', 'faq']],
        ['Were more women than men left off?', women + ' The Chief Electoral Officer said ' + lk(X.father_left_off) + ' women over 25 still registered at their father\'s address were among those left off. After the draft, an elector asks to be added with Form 6, and an objection to a name already on the roll is made with Form 7. According to the press, women were ' + SIR.pct(s.form6_women_pct) + ' of the Form 6 claims and ' + SIR.pct(s.form7_women_pct) + ' of the electors whose deletion was sought through Form 7.', ['main', 'faq']],
        ['Did towns lose more names than villages?', towns + ' Urban areas held ' + SIR.pct(U.urban_share_roll) + ' of the roll and ' + SIR.pct(U.urban_share_left) + ' of the names left off. The districts that lost the most also entered more of their names as untraceable or absent, the reason that rests on the least.', ['main', 'faq']],
        ['Could the names left off have changed election results?', margin + ' No figure by constituency has been published, so each district\'s count is spread over its seats by their 2022 electors. The spread gives how many seats, never which, and the people left off would not all have voted, nor all for one side.', ['main', 'faq']],
        ['What happened to the notices?', notices + ' ' + n0(N.aeros) + ' assistant registration officers heard them, about ' + n0(N.per_aero) + ' notices each. In all ' + lk(N.removed_after.total) + ' names were deleted after the draft, as the press reported the Chief Electoral Officer\'s figures.', ['main', 'faq']],
        ['Why are there no constituency figures?', 'The Chief Electoral Officer, who keeps the state\'s rolls, published the revision by district. No table of it by assembly constituency, the area that elects one member of the assembly, could be found. The only other source below the district is the lists of individual electors, which this site does not open. So the map and the tables stop at the district.', ['main', 'method', 'faq']],
        ['Where do the figures come from?', 'The district table is the Chief Electoral Officer\'s handout of 6 January 2026, as photographed and published in the press by India TV. Every row of it adds up two ways. The rolls by sex are from the Chief Electoral Officer\'s own posts. The forms and the later deletions are from press reports quoting the Chief Electoral Officer. The method page has every link.', ['method', 'faq']]
      ];
      var short = {
        main: [[scale, women, towns, where, margin, notices], 'The figures are by district only, from the Chief Electoral Officer\'s table as published in the press. The split by sex, by urban and rural area and the notices are the Chief Electoral Officer\'s figures as the press reported them, rounded to the lakh.'],
        method: [[scale, 'The district table is the Chief Electoral Officer\'s, as photographed and published by India TV, and every row adds up two ways.'], ''],
        faq: [[scale, women, towns, after], '']
      };
      return { qa: QA, short: short };
    }));
  });
})();
