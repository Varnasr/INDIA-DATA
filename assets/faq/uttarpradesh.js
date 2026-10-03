/* Questions and answers for the Uttar Pradesh pages, in English only for now.
   The FAQ tab shows them all; each page shows those tagged with its key (main,
   method, faq). The "In short" points for each page are in short. */
(function () {
  var P;
  SIR.faq('up', 'uttarpradesh/faq/', function () {
    return P || (P = Promise.all([SIR.json('data/uttarpradesh/summary.json'), SIR.json('data/uttarpradesh/districts.json')]).then(function (r) {
      var s = r[0], D = r[1];
      var cr = function (x) { return (x / 1e7).toFixed(2) + ' crore'; }, lk = function (x) { return (x / 1e5).toFixed(1) + ' lakh'; }, d1 = function (v) { return SIR.d(v, 1); };
      var last = D[D.length - 1];
      var scale = 'Uttar Pradesh\'s draft roll left off ' + cr(s.left_off) + ' names, ' + d1(s.per_100) + ' of every 100 electors on the roll of 27 October 2025.';
      var reasons = SIR.pct(s.shares.shifted) + ' were entered as permanently shifted, ' + SIR.pct(s.shares.untraceable_absent) + ' as untraceable or absent, ' + SIR.pct(s.shares.dead) + ' as dead and ' + SIR.pct(s.shares.multiple) + ' as already enrolled elsewhere.';
      var where = D[0].district + ' left off ' + d1(D[0].per_100) + ' of every 100 electors, the most of the 75 districts, and ' + s.over_20 + ' districts left off 20 or more. ' + last.district + ' left off the fewest, ' + d1(last.per_100) + '.';
      var after = 'The final roll of 10 April 2026 was ' + lk(s.net_rise) + ' larger than the draft, ' + SIR.pct(s.made_up_pct) + ' of what the draft left off. That rise counts new voters too, so it is the most that can have been put back.';
      var women = 'Women were ' + SIR.pct(s.draft_women_pct) + ' of the draft roll and ' + SIR.pct(s.rise_women_pct) + ' of the rise to the final roll. No split by sex of the names left off has been published.';
      var QA = [
        ['How many names did the revision remove in Uttar Pradesh?', scale + ' ' + reasons + ' A reason is what the officer wrote down, and nobody checked it.', ['main', 'faq']],
        ['Where were the most names left off?', where + ' The cities stand out. Lucknow, Ghaziabad, Kanpur Nagar and Meerut are four of the five districts with the highest rates.', ['main', 'faq']],
        ['Were the names put back?', after + ' A further ' + lk(s.removed_after) + ' were removed after the draft, as reported in the press.', ['main', 'faq']],
        ['Were women removed more than men?', women + ' As reported in the press, women were ' + SIR.pct(s.form6_women_pct) + ' of the Form 6 claims to be added after the draft and ' + SIR.pct(s.form7_women_pct) + ' of the electors whose deletion was sought through Form 7.', ['main', 'faq']],
        ['Why is there no constituency or map?', 'The Chief Electoral Officer\'s table is by district. No table of the revision by assembly constituency could be found, and the Chief Electoral Officer\'s site cannot be reached from outside India. The only other source below the district is the lists of individual electors, which this site does not open.', ['main', 'method', 'faq']],
        ['Where do the figures come from?', 'The district table is the Chief Electoral Officer\'s handout of 6 January 2026, as photographed and published by India TV, and every row of it adds up two ways. The rolls by sex are from the Chief Electoral Officer\'s own posts, and the forms and later removals from press reports quoting the Chief Electoral Officer. The method page has every link.', ['method', 'faq']]
      ];
      var short = {
        main: [[scale, reasons, where, after, women], 'The figures are by district only, from the Chief Electoral Officer\'s table as published in the press.'],
        method: [[scale, 'The district table is the Chief Electoral Officer\'s, as photographed and published by India TV, and every row is checked two ways.'], ''],
        faq: [[scale, where, after], '']
      };
      return { qa: QA, short: short };
    }));
  });
})();
