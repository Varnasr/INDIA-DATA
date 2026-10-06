/* Questions and answers for the Delhi pages, in English only for now. The
   FAQ tab shows them all; each page shows those tagged with its key (main,
   method, faq). The "In short" points for each page are in short. */
(function () {
  var P;
  SIR.faq('dl', 'delhi/faq/', function () {
    return P || (P = Promise.all([SIR.json('data/delhi/summary.json'), SIR.json('data/delhi/districts.json')]).then(function (r) {
      var s = r[0], D = r[1], lk = function (x) { return (x / 1e5).toFixed(1) + ' lakh'; }, d1 = function (v) { return SIR.d(v, 1); };
      var Pa = {}; s.parties.forEach(function (p) { Pa[p.party] = p; });
      var scale = 'Delhi\'s draft roll left off ' + lk(s.left_off) + ' names, ' + d1(s.per_100) + ' of every 100 electors on the roll before the revision.';
      var margin = 'In ' + s.over_margin + ' of the 70 constituencies, more names were left off than the 2025 winning margin.';
      var where = D[0].district + ' district left off the most, ' + d1(D[0].per_100) + ' per 100, and ' + s.rate_max + ' the most of any constituency, ' + d1(s.rate_max_v) + '.';
      var reasons = SIR.pct(s.shares.shifted_absent_other) + ' were entered as shifted, absent or other, and ' + SIR.pct(s.shares.dead) + ' as dead.';
      var sex = 'Men were left off more often than women, ' + d1(s.men_left_per_100) + ' per 100 men against ' + d1(s.women_left_per_100) + ' per 100 women.';
      var QA = [
        ['How many names did the revision remove in Delhi?', scale + ' The draft roll is the list published once the enumeration forms were collected, and a name whose form was not collected was left off it. ' + reasons + ' ' + SIR.pct(s.shares.duplicate) + ' were entered as enrolled at more than one place. A reason is what the officer wrote down, and nobody checked it.', ['main', 'faq']],
        ['Could the removals have changed the 2025 result?', margin + ' The winning margin is the winner\'s votes less the runner-up\'s. Not everyone on a roll votes, so scaled down by each seat\'s own 2025 turnout it is ' + s.at_turnout_over_margin + '. The election came before the revision, so this measures how large the removals are against the votes that decide a seat. Larger than the margin means large enough to decide a seat, and it says nothing about whether it would have. Nobody can say how anyone left off would have voted.', ['main', 'faq']],
        ['Did one party\'s seats lose more names?', 'The BJP\'s ' + Pa.BJP.seats + ' seats lost ' + d1(Pa.BJP.per_100) + ' per 100 and the AAP\'s ' + Pa.AAP.seats + ' lost ' + d1(Pa.AAP.per_100) + '. Set against the rate in their own districts, the two are ' + SIR.d(Pa.BJP.vs_district, 1) + ' and ' + SIR.d(Pa.AAP.vs_district, 1) + ' points. So the difference comes mostly from where each party\'s seats are.', ['main', 'faq']],
        ['Were women removed more than men?', sex + ' Women were ' + SIR.pct(s.women_before_pct) + ' of the roll before and ' + SIR.pct(s.women_left_off_pct) + ' of the names left off. The split by sex was published for Delhi as a whole only.', ['main', 'faq']],
        ['Where were the most names left off?', where + ' ' + s.acs_over_40 + ' constituencies left off 40 or more of every 100, and ' + s.rate_min + ' the fewest, ' + d1(s.rate_min_v) + '.', ['main', 'faq']],
        ['Where do the figures come from?', 'The state figures are the press note of 31 August 2026 from the Chief Electoral Officer, who keeps Delhi\'s rolls. The constituency figures are the Chief Electoral Officer\'s own table of the draft, by district and constituency, and they add up exactly to the state figures. The 2025 result is the Election Commission\'s. The method page has every link.', ['method', 'faq']]
      ];
      var short = {
        main: [[scale, margin, where, reasons, sex], 'The reasons and the split by sex are for Delhi as a whole, and there is no final roll yet.'],
        method: [[scale, 'The constituency figures add up exactly to the Chief Electoral Officer\'s state figures.'], ''],
        faq: [[scale, margin, where], '']
      };
      return { qa: QA, short: short };
    }));
  });
})();
