/* Questions and answers for the Kerala pages. The FAQ tab shows them all;
   each page shows those tagged with its key (main, elections, method). The
   "In short" points for each page are in SHORT. */
(function () {
  var P;
  SIR.faq('kl', 'kerala/faq/', function () {
    return P || (P = Promise.all([SIR.json('data/kerala/summary.json'), SIR.json('data/kerala/districts.json')]).then(function (r) {
      var s = r[0], D = r[1], W = {};
      s.winners.forEach(function (w) { W[w.party] = w; });
      var cr = function (x) { return L('{x} crore', { x: (x / 1e7).toFixed(2) }); };
      var scale = L('Kerala\'s draft roll was {f} smaller than its roll of January 2025, {p} of every 100 electors.', { f: SIR.lakh(s.fall_draft), p: SIR.d(s.draft_per_100, 1) });
      var women = L('Women were {wf} of that fall, against {w} of the roll, and more than their share in all {n} districts.', { wf: SIR.pct(s.women_fall_pct), w: SIR.pct(s.women_2025_pct), n: s.districts });
      var where = L('{a} fell most, by {av} per 100, and {lo} least, by {lov}.', { a: D[0].district, av: SIR.d(D[0].draft_per_100, 1), lo: D[D.length - 1].district, lov: SIR.d(D[D.length - 1].draft_per_100, 1) });
      var back = L('By the 2026 election the roll had risen {b} from the draft, which counts new voters as well as names put back, and it was {e} smaller than in January 2025.', { b: SIR.lakh(s.election - s.draft), e: SIR.lakh(s.fall) });
      var margin = L('In {k} of the {n} constituencies, the roll fell by more at the draft than the 2026 winning margin.', { k: s.draft_over_margin, n: s.acs });
      var QA = [
        [L('How much smaller was Kerala\'s roll after the revision?'),
         scale + ' ' + L('The roll of January 2025 held {b}, the draft {d}, the final roll {f} and the roll of March 2026 {e}.', { b: cr(s.roll_2025), d: cr(s.draft), f: cr(s.final), e: cr(s.election) }), ['main', 'faq']],
        [L('Why do these pages measure the fall in the roll and not the removals?'),
         L('The Chief Electoral Officer has published no table of the names left off the draft, by constituency or for the state, while every roll is published by constituency. The fall from January 2025 to the draft takes in the ordinary changes of 2025 too. For the state it is within half a lakh of the count of names left off reported with the draft, but for one constituency it may differ more.'), ['main', 'elections', 'method', 'faq']],
        [L('Where did the roll fall most?'),
         where + ' ' + L('{b} and {c} come next.', { b: D[1].district, c: D[2].district }), ['main', 'faq']],
        [L('Were women removed more than men?'),
         women + ' ' + L('They were more than their share in {k} of the {acs} constituencies. Of the rise after the draft, women were {wa}.', { k: s.acs_women_over, acs: s.acs, wa: SIR.pct(s.women_added_pct) }), ['main', 'faq']],
        [L('Were the names put back?'),
         back + ' ' + L('In {k} districts the roll was larger at the election than in January 2025. The rise counts new voters as well as names put back, so it cannot show who among those left off returned.', { k: D.filter(function (d) { return d.per_100 < 0; }).length }), ['main', 'faq']],
        [L('Could the fall in the roll have changed the 2026 result?'),
         margin + ' ' + L('By the election most of it had been made up, and the roll was smaller than in January 2025 by more than the margin in {k} seats, or {t} counted at each seat\'s turnout. Nobody can know how anyone missing from the roll would have voted.', { k: s.over_margin, t: s.could_change }), ['elections', 'faq']],
        [L('Did the roll fall more in one party\'s seats?'),
         L('The roll fell at the draft by {i} per 100 in the INC\'s {is} seats, {c} in the CPI(M)\'s {cs} and {u} in the IUML\'s {us}. Against their own districts the three are within about a point of zero, so most of the difference is about where the seats are.', { i: SIR.d(W.INC.draft_per_100, 1), is: W.INC.seats, c: SIR.d(W['CPI(M)'].draft_per_100, 1), cs: W['CPI(M)'].seats, u: SIR.d(W.IUML.draft_per_100, 1), us: W.IUML.seats }), ['elections', 'faq']],
        [L('Where do these figures come from?'),
         L('The four rolls by constituency and sex are the Chief Electoral Officer\'s own tables, and the 2026 result is from the Election Commission\'s result pages. The <a href="../method/">method page</a> gives each source.'), ['method', 'faq']],
        [L('Does this show that the removals were intended to change results?'),
         L('No list of removals can show intent. The tables show where the roll fell and how that compares with the margins. They cannot show whose votes these were or whether each removal was right.'), ['elections', 'method']],
        [L('Can I look up my own name here?'),
         L('No. Only counts are published on this site. To check your own entry, use the Election Commission\'s voter search.'), ['main']]
      ];
      var limits = L('No count of the names removed is published by constituency, so these pages measure the fall in the roll from January 2025, which takes in ordinary changes as well as the revision.');
      var SHORT = {
        main: [[scale, women, where, back], limits],
        elections: [[margin,
          L('By the election the roll was smaller than in January 2025 by more than the margin in {k} seats.', { k: s.over_margin }),
          L('The INC won {i} seats, the CPI(M) {c} and the IUML {u}.', { i: W.INC.seats, c: W['CPI(M)'].seats, u: W.IUML.seats })],
          L('The rise after the draft counts new voters too, and the lists cannot show how anyone missing from the roll would have voted.')],
        method: [[
          L('Every roll from January 2025 to March 2026 is published by constituency and by sex, and every table adds up to its own totals.'),
          L('No count of the names left off the draft has been published by the Chief Electoral Officer.'),
          L('The fall in the roll takes in ordinary changes as well as the revision.')],
          limits],
        faq: [[scale, women, where, margin], limits]
      };
      return { qa: QA, short: SHORT };
    }));
  });
})();
