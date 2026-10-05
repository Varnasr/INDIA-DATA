/* Questions and answers for the Rajasthan pages, in English only for now. The
   FAQ tab shows them all; each page shows those tagged with its key (main,
   method). The "In short" points for each page are in SHORT. */
(function () {
  var P;
  SIR.faq('rj', 'rajasthan/faq/', function () {
    return P || (P = Promise.all([SIR.json('data/rajasthan/summary.json'), SIR.json('data/rajasthan/districts.json')]).then(function (r) {
      var s = r[0], D = r[1], W = {};
      s.winners.forEach(function (w) { W[w.party] = w; });
      var lk = function (x) { return (x / 1e5).toFixed(1) + ' lakh'; }, d1 = function (v) { return SIR.d(v, 1); };
      var grew = D.filter(function (d) { return d.per_100 < 0; });
      var scale = 'Rajasthan\'s draft roll left off ' + lk(s.left_off) + ' names, ' + d1(s.left_per_100) + ' of every 100 electors on the roll before the revision.';
      var after = 'After the draft ' + lk(s.added) + ' were added and ' + lk(s.deleted_after) + ' more deleted, so ' + lk(s.removed_by_final) + ' had been removed by the time of the final roll. The final roll was ' + lk(s.final - s.draft) + ' larger than the draft, which is at most ' + SIR.pct(s.made_up_pct) + ' of what was left off.';
      var where = 'From the 2023 election to the final roll, the roll fell most in ' + D[0].district + ' (' + d1(D[0].per_100) + ' per 100) and grew in ' + grew.map(function (d) { return d.district; }).join(', ') + '.';
      var women = 'Women\'s share of the roll fell in ' + s.acs_women_fell + ' of ' + s.acs + ' constituencies, from ' + SIR.pct(s.women_2023_pct) + ' in 2023 to ' + SIR.pct(s.women_2026_pct) + ', and women were ' + SIR.pct(s.deleted_women_pct) + ' of the names deleted after the draft.';
      var margin = 'In ' + s.over_margin + ' of the 200 constituencies the roll fell by more than the 2023 winning margin.';
      var QA = [
        ['How many names did the revision remove in Rajasthan?', scale + ' The draft roll is the list published once the enumeration forms were collected, and a name whose form did not come back was left off it. ' + SIR.pct(100 * s.reasons_lakh.shifted_absent / s.reasons_lakh_sum) + ' were entered as shifted or absent, ' + SIR.pct(100 * s.reasons_lakh.dead / s.reasons_lakh_sum) + ' as dead and the rest as enrolled at more than one place. A reason is what the officer wrote down, and nobody checked it.', ['main', 'faq']],
        ['Were the names put back?', after + ' The rise counts new voters as well as names put back, so it cannot show how many of those left off returned.', ['main', 'faq']],
        ['Why do the district and constituency figures measure the change in the roll?', 'The Chief Electoral Officer, who keeps the state\'s rolls, published the names left off only as a state total. Below the state the only source is the lists of individual electors, which this site does not open. So the pages compare the roll of the 2023 election with the final SIR roll of March 2026, constituency by constituency. That change takes in more than two years of new voters, deaths and moves as well as the revision. For the state it is a fall of ' + lk(s.fall) + ', against ' + lk(s.left_off) + ' left off the draft.', ['main', 'method', 'faq']],
        ['Where did the roll fall most?', where + ' Across the constituencies it runs from a fall of ' + d1(s.rate_max_v) + ' per 100 in ' + s.rate_max + ' to a rise of ' + d1(-s.rate_min_v) + ' in ' + s.rate_min + '.', ['main', 'faq']],
        ['Were women removed more than men?', women + ' No split by sex of the names left off the draft has been published.', ['main', 'faq']],
        ['Could the change in the roll have changed the 2023 result?', margin + ' The winning margin is the winner\'s votes less the runner-up\'s. The revision came after that election, so this measures how large the change is against the votes that decide a seat. Larger than the margin means large enough to decide a seat, and it says nothing about whether it would have. Nobody can know how anyone missing from the roll would have voted.', ['main', 'faq']],
        ['Did the roll fall more in one party\'s seats?', 'The roll fell by ' + d1(W.BJP.per_100) + ' per 100 in the BJP\'s ' + W.BJP.seats + ' seats and ' + d1(W.INC.per_100) + ' in the Congress\'s ' + W.INC.seats + '. Set against the change in their own districts, the two are ' + d1(W.BJP.vs_district) + ' and ' + d1(W.INC.vs_district) + '. So most of the difference comes from where each party\'s seats are.', ['main', 'faq']],
        ['Where do the figures come from?', 'The state figures are the Chief Electoral Officer\'s press note of 16 December 2025 and fact sheet of 21 February 2026. The rolls by constituency are the Election Commission\'s 2023 statistical report and the Chief Electoral Officer\'s table of 12 March 2026. The method page has every link.', ['method', 'faq']]
      ];
      var short = {
        main: [[scale, after, where, women, margin], 'Below the state, the figures are the change in the roll from the 2023 election to March 2026, which takes in new voters, deaths and moves as well as the revision.'],
        method: [[scale, 'Below the state, the pages compare the roll of the 2023 election with the final SIR roll, because no count of the names left off was published by district or constituency.'], ''],
        faq: [[scale, after, margin], '']
      };
      return { qa: QA, short: short };
    }));
  });
})();
