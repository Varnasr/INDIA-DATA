/* Questions and answers for the Uttarakhand pages, in English only for now.
   The FAQ tab shows them all; each page shows those tagged with its key
   (main, method, faq). The "In short" points for each page are in short. */
(function () {
  var P;
  SIR.faq('uk', 'uttarakhand/faq/', function () {
    return P || (P = Promise.all([SIR.json('data/uttarakhand/summary.json'), SIR.json('data/uttarakhand/districts.json')]).then(function (r) {
      var s = r[0], D = r[1], lk = function (x) { return SIR.lk(x, 2); }, d1 = function (v) { return SIR.d(v, 1); };
      var scale = 'Uttarakhand\'s draft roll left off ' + lk(s.left_off) + ' names, ' + d1(s.per_100) + ' of every 100 electors on the roll before the revision.';
      var after = 'After the draft, ' + lk(s.claims) + ' names were added and ' + lk(s.objections) + ' removed, so the final roll of 3 October 2026 holds ' + SIR.n(s.net) + ' more than the draft. That is ' + d1(s.made_up_pct) + ' for every 100 left off.';
      var plains = 'The four plains districts hold ' + SIR.pct(s.plains.draft_pct) + ' of the draft roll and account for ' + SIR.pct(s.plains.objections_pct) + ' of the names removed after it.';
      var women = 'Women were ' + SIR.pct(s.women_draft_pct) + ' of the draft roll and ' + SIR.pct(s.women_objections_pct) + ' of the names removed after it, more than their share in ' + s.acs_women_over + ' of the 70 constituencies.';
      var reasons = SIR.pct(s.shares.absent_or_shifted) + ' of those left off were entered as absent or shifted, ' + SIR.pct(s.shares.dead) + ' as dead and ' + SIR.pct(s.shares.duplicate) + ' as enrolled at more than one place.';
      var QA = [
        ['How many names did the revision remove in Uttarakhand?', scale + ' The draft roll is the list published once the enumeration forms were collected, and a name whose form did not come back was left off it. ' + reasons + ' A reason is what the officer wrote down, and nobody checked it. These figures were published for the state as a whole only.', ['main', 'faq']],
        ['How many came back before the final roll?', after + ' The names added include people enrolling for the first time, so this is the most that could have been put back, and fewer than that in fact. The final roll is ' + lk(-s.final_vs_before) + ' smaller than the roll before the revision.', ['main', 'faq']],
        ['Where were names removed after the draft?', plains + ' ' + s.obj_max + ' removed ' + d1(s.obj_max_v) + ' for every 1,000 on its draft, the most of any constituency, and ' + s.obj_min + ' ' + d1(s.obj_min_v) + '. In ' + s.acs_lost + ' constituencies more names were removed than added, so the final roll is smaller than the draft.', ['main', 'faq']],
        ['Were women removed more than men after the draft?', women + ' In ' + s.gap_max + ' they were ' + SIR.pct(s.gap_max_pct) + ' of the ' + SIR.n(s.gap_max_n) + ' removed. The table gives the count by sex and no reason, so it cannot say why. Women were also ' + SIR.pct(s.women_claims_pct) + ' of the names added.', ['main', 'faq']],
        ['Why is there no figure for the names left off in each constituency?', 'The Chief Electoral Officer published the roll before the revision and the names left off for the state only. The constituency table starts at the draft. So every constituency figure on these pages is about what happened between the draft and the final roll.', ['main', 'method', 'faq']],
        ['Where do the figures come from?', 'From two press notes of Uttarakhand\'s Chief Electoral Officer, who keeps the state\'s rolls for the Election Commission. The note of 14 July 2026 gives the roll before, the draft and the four reasons. The note of 3 October 2026 gives the final roll and a table of every constituency, by sex, which the site transcribed and checked row by row. The method page has both links.', ['method', 'faq']]
      ];
      var short = {
        main: [[scale, after, plains, women], 'The names left off and their reasons were published for Uttarakhand as a whole. Every constituency figure is about the change from the draft to the final roll.'],
        method: [[scale, 'Every one of the 70 constituencies adds up, by sex, from the draft to the final roll, and the constituencies add up to the printed district and state totals.'], ''],
        faq: [[scale, after, women], '']
      };
      return { qa: QA, short: short };
    }));
  });
})();
