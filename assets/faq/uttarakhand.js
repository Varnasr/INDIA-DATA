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
      var plains = 'The four plains districts held ' + SIR.pct(s.plains.roll_before_pct) + ' of the roll before the revision, and account for ' + SIR.pct(s.plains.left_off_pct) + ' of the names left off the draft and ' + SIR.pct(s.plains.objections_pct) + ' of the names removed after it.';
      var seats = s.lo_max + ' lost ' + d1(s.lo_max_v) + ' of every 100 names on its roll before the revision, the most of the 70 constituencies, and ' + s.lo_min + ' ' + d1(s.lo_min_v) + ', the fewest.';
      var women = 'Women were ' + SIR.pct(s.women_draft_pct) + ' of the draft roll and ' + SIR.pct(s.women_objections_pct) + ' of the names removed after it, more than their share in ' + s.acs_women_over + ' of the 70 constituencies.';
      var reasons = SIR.pct(s.shares.absent_or_shifted) + ' of those left off were entered as absent or shifted, ' + SIR.pct(s.shares.dead) + ' as dead and ' + SIR.pct(s.shares.duplicate) + ' as enrolled at more than one place.';
      var QA = [
        ['How many names did the revision remove in Uttarakhand?', scale + ' The draft roll is the list published once the enumeration forms were collected, and a name whose form did not come back was left off it. ' + reasons + ' A reason is what the officer wrote down, and nobody checked it. The reasons were published for the state as a whole only, and the count of names left off for every constituency.', ['main', 'faq']],
        ['How many came back before the final roll?', after + ' The names added include people enrolling for the first time, so this is the most that could have been put back, and fewer than that in fact. The final roll is ' + lk(-s.final_vs_before) + ' smaller than the roll before the revision.', ['main', 'faq']],
        ['Where were names removed after the draft?', plains + ' ' + s.obj_max + ' removed ' + d1(s.obj_max_v) + ' for every 1,000 on its draft, the most of any constituency, and ' + s.obj_min + ' ' + d1(s.obj_min_v) + '. In ' + s.acs_lost + ' constituencies more names were removed than added, so the final roll is smaller than the draft.', ['main', 'faq']],
        ['Were women removed more than men after the draft?', women + ' In ' + s.gap_max + ' they were ' + SIR.pct(s.gap_max_pct) + ' of the ' + SIR.n(s.gap_max_n) + ' removed. The table gives the count by sex and no reason, so it cannot say why. Women were also ' + SIR.pct(s.women_claims_pct) + ' of the names added.', ['main', 'faq']],
        ['Where were the most names left off?', seats + ' By district, ' + s.dist_lo_max + ' lost ' + d1(s.dist_lo_max_v) + ' per 100 and ' + s.dist_lo_min + ' ' + d1(s.dist_lo_min_v) + '. The counts come from the Chief Electoral Officer\'s table of the draft, which gives the names left off for every constituency but no reason or sex below the state.', ['main', 'faq']],
        ['How many electors were sent a notice?', 'The Chief Electoral Officer\'s table of the draft counts ' + lk(s.notices) + ' electors on the draft, ' + d1(s.notices_per_100) + ' of every 100, in line for a notice to prove their entry: ' + lk(s.no_mapping) + ' who could not be linked to the 2003 roll and ' + lk(s.anomalies) + ' whose entry had an anomaly. The constituencies with more notices removed more names after the draft, with a rank correlation of ' + SIR.d(s.rho_notices_objections, 2) + '. The table does not say how many notices were heard or what came of them.', ['main', 'faq']],
        ['Where do the figures come from?', 'From three documents of Uttarakhand\'s Chief Electoral Officer, who keeps the state\'s rolls for the Election Commission. The press note of 14 July 2026 gives the roll before, the draft and the four reasons. A table published the same day gives, for every constituency, the draft, the names left off and the electors in line for a notice. The press note of 3 October 2026 gives the final roll and a table of every constituency by sex. The method page has the links.', ['method', 'faq']]
      ];
      var short = {
        main: [[scale, seats, after, plains, women], 'The reasons for leaving a name off, and the split by sex, were published for Uttarakhand as a whole only.'],
        method: [[scale, 'The names left off in the 70 constituencies add up to the state total, and every constituency adds up, by sex, from the draft to the final roll.'], ''],
        faq: [[scale, after, women], '']
      };
      return { qa: QA, short: short };
    }));
  });
})();
