/* Questions and answers for the Karnataka pages. The FAQ tab shows them all;
   each page shows those tagged with its key (main, method). The "In short"
   points for each page are in SHORT. */
(function () {
  var P;
  SIR.faq('ka', 'karnataka/faq/', function () {
    return P || (P = SIR.json('data/karnataka/summary.json').then(function (s) {
      var B = s.bengaluru, R = s.rest;
      var cr = function (x) { return L('{x} crore', { x: (x / 1e7).toFixed(2) }); };
      var scale = L('The revision left {r} names off Karnataka\'s draft roll, {p} of every 100 electors on the roll before it began.', { r: SIR.lakh(s.removed), p: SIR.d(s.per_100, 1) });
      var blr = L('Bengaluru\'s four districts lost {p} of every 100 electors. They hold {roll} of the state\'s roll and {rem} of the names removed.', { p: SIR.d(B.per_100, 1), roll: SIR.pct(B.share_of_roll), rem: SIR.pct(B.share_of_removed) });
      var why = L('{sh} were entered as shifted, {ab} as absent, {dead} as dead and {dup} as already enrolled elsewhere.', { sh: SIR.pct(s.shares.shifted), ab: SIR.pct(s.shares.absent), dead: SIR.pct(s.shares.dead), dup: SIR.pct(s.shares.duplicate) });
      var back = L('By 25 September the roll had risen by {a} since the draft, {m} of the names removed. In Bengaluru it rose by {ba}.', { a: SIR.n(s.added_sep), m: SIR.pct(s.made_up_pct), ba: SIR.n(B.added_sep) });
      var QA = [
        [L('How many names did the revision remove in Karnataka?'),
         scale + ' ' + L('The roll of 16 June 2026 held {b} names and the draft roll of 24 August {d}.', { b: cr(s.before), d: cr(s.draft) }), ['main', 'faq']],
        [L('Why were the names removed?'),
         why + ' ' + L('A reason on the list is what the officer wrote down, and nobody checked it.'), ['main', 'faq']],
        [L('Where were removals heaviest?'),
         blr + ' ' + L('Outside Bengaluru the highest is {a} at {av} per 100, and the lowest is {lo} at {lov}.', { a: s.top[4].district, av: SIR.d(s.top[4].per_100, 1), lo: s.low[2].district, lov: SIR.d(s.low[2].per_100, 1) }), ['main', 'faq']],
        [L('Were Bengaluru\'s names removed for different reasons?'),
         L('Yes. In Bengaluru {sa} of the names removed were entered as shifted or absent and {dead} as dead. In the rest of the state the figures are {rsa} and {rdead}. Across all 34 districts, the more names a district removed, the larger the share marked shifted or absent (rank correlation {rho}).', { sa: SIR.pct(B.shifted_absent_share), dead: SIR.pct(B.dead_share), rsa: SIR.pct(R.shifted_absent_share), rdead: SIR.pct(R.dead_share), rho: SIR.d(s.rho_rate_shifted, 2) }), ['main']],
        [L('Have the names been put back?'),
         back + ' ' + L('That rise counts new voters too, so it is the most that could have been restored. The final roll is due on 27 October 2026.'), ['main', 'faq']],
        [L('Were women removed more than men?'),
         L('This cannot be counted from the Chief Electoral Officer\'s tables. The roll before the revision is published as a total only, and the names removed are not split by sex. Women were {d} of the draft roll and {f} of the roll of 25 September.', { d: SIR.pct(s.women_draft_pct), f: SIR.pct(s.women_sep_pct) }), ['main', 'method', 'faq']],
        [L('Why is there no table by constituency?'),
         L('The Chief Electoral Officer published the revision by its 34 election districts and for the state, and no table by assembly constituency. So the removals cannot be set against the margins of the 2023 election.'), ['method', 'faq']],
        [L('Where do these figures come from?'),
         L('The removals by district and reason, and the draft roll by district and sex, are from the Chief Electoral Officer\'s press note of 24 August 2026. The roll of 25 September is from the press note of that date. The <a href="../method/">method page</a> gives each source.'), ['method', 'faq']],
        [L('Can I look up my own name here?'),
         L('No. Only counts are published on this site. To check your own entry, use the Election Commission\'s voter search.'), ['main']]
      ];
      var limits = L('A reason on the list is what the officer wrote down, and nobody checked it. The tables show where names were removed and cannot show why.');
      var SHORT = {
        main: [[scale, blr, why, back], limits],
        method: [[
          L('The removals and the draft roll are published by the Chief Electoral Officer by election district, and every table adds up to its state row.'),
          L('Nothing has been published by assembly constituency, and the removals are not split by sex or age.'),
          L('The final roll is due on 27 October 2026.')],
          L('A reason on the list is what the officer wrote down, and nobody checked it.')],
        faq: [[scale, blr, why, back], limits]
      };
      return { qa: QA, short: SHORT };
    }));
  });
})();
