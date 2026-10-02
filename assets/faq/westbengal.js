/* Questions and answers for the West Bengal pages. The FAQ tab shows them all;
   each page shows those tagged with its key (main, elections, method). The
   "In short" points for each page are in SHORT. */
(function () {
  var P;
  SIR.faq('wb', 'westbengal/faq/', function () {
    return P || (P = Promise.all([SIR.json('data/westbengal/summary.json'), SIR.json('data/westbengal/districts.json')]).then(function (r) {
      var s = r[0], D = r[1], p = s.pn05, W = {};
      s.winners.forEach(function (w) { W[w.party] = w; });
      var cr = function (x) { return L('{x} crore', { x: (x / 1e7).toFixed(2) }); };
      var scale = L('The revision left {r} names off West Bengal\'s draft roll, {pp} of every 100 electors, and held back another {adj} from the final roll for adjudication.', { r: SIR.lakh(p.removed), pp: SIR.d(p.removed_per_100, 1), adj: SIR.lakh(p.adjudication) });
      var fall = L('The roll the 2026 election was held on was {f} smaller than the 2024 roll, {pp} of every 100 electors. Kolkata North\'s fell by {kn} per 100.', { f: SIR.lakh(s.fall), pp: SIR.d(s.per_100, 1), kn: SIR.d(D[0].per_100, 1) });
      var women = L('Women were {w} of the names left off the draft roll, against {wr} of the roll before it.', { w: SIR.pct(p.women_removed_pct), wr: SIR.pct(p.women_before_pct) });
      var why = L('{dead} of the names left off the draft were entered as dead, {sh} as shifted and {ab} as absent.', { dead: SIR.pct(p.shares.dead), sh: SIR.pct(p.shares.shifted), ab: SIR.pct(p.shares.absent) });
      var margin = L('In {k} of the {n} constituencies, the roll fell by more than the 2026 winning margin.', { k: s.over_margin, n: s.acs });
      var QA = [
        [L('How many names did the revision remove in West Bengal?'),
         scale + ' ' + L('The roll of 27 October 2025 held {b}, the draft {d} and the final roll of 28 February 2026 {f}. By the 2026 nominations the roll had regained {back}, to {e}.', { b: cr(p.before), d: cr(p.draft), f: cr(p.final), back: SIR.lakh(s.after_final), e: cr(s.election) }), ['main', 'faq']],
        [L('Why were the names removed?'),
         why + ' ' + L('A reason on the list is what the officer wrote down, and nobody checked it.'), ['main', 'faq']],
        [L('Why do these pages compare the roll with 2024?'),
         L('No count of the names removed has been published by district or constituency. The rolls are published by constituency for the 2024 Lok Sabha nominations, the draft and the 2026 nominations, so the pages measure how much smaller each roll became. That fall includes ordinary changes to the roll before the revision as well as the revision itself, so it is called the fall in the roll and never the removals.'), ['main', 'elections', 'method', 'faq']],
        [L('Where did the roll fall most?'),
         fall + ' ' + L('{a} and {b} come next. {lo} fell the least, {lov} per 100.', { a: D[1].district, b: D[2].district, lo: D[D.length - 1].district, lov: SIR.d(D[D.length - 1].per_100, 1) }), ['main', 'faq']],
        [L('Were women removed more than men?'),
         women + ' ' + L('From 2024 to the election, women were {wf} of the fall in the roll and {w24} of the 2024 roll, and more than their share in {k} of the {n} districts.', { wf: SIR.pct(s.women_fall_pct), w24: SIR.pct(s.women_2024_pct), k: s.districts_women_over, n: s.districts }), ['main', 'faq']],
        [L('What happened to the names held back for adjudication?'),
         L('Judicial officers appointed on the Supreme Court\'s direction found {e} of the {u} eligible and {n} not eligible. {a} of those found not eligible appealed to the tribunals, and {r} were restored in time to vote. Another {i} appeals asked the tribunals to remove names the judicial officers had kept, and on 16 September {pp} of all appeals were still undecided. These are the Election Commission\'s figures as reported.', { e: SIR.lakh(s.adj.found_eligible), u: SIR.lakh(s.adj.under_adjudication), n: SIR.lakh(s.adj.found_not_eligible), a: SIR.lakh(s.adj.appeals_by_excluded), r: SIR.n(s.adj.restored_before_poll), i: SIR.lakh(s.adj.appeals_against_inclusion), pp: SIR.pct(s.adj.pending_pct) }), ['main', 'faq']],
        [L('Where were the names held back for adjudication?'),
         L('The {adj} names held back are counted for the state only. The nearest the constituency tables come is the change between the draft and the roll the election was held on, which is largest in Murshidabad, Malda and the two Dinajpurs.', { adj: SIR.lakh(p.adjudication) }), ['main', 'method']],
        [L('Could the fall in the roll have changed the 2026 result?'),
         margin + ' ' + L('Counted at each seat\'s own turnout, it still exceeds the margin in {k} seats. The fall includes the dead and ordinary changes, and nobody can know how anyone missing from the roll would have voted.', { k: s.could_change }), ['elections', 'faq']],
        [L('Did the roll fall more in one party\'s seats?'),
         L('The roll fell by {b} per 100 in the {bs} seats the BJP won and by {t} in the {ts} the AITC won. Against their own districts the two come out at {bv} and {tv}, so the difference is about where the seats are.', { b: SIR.d(W.BJP.per_100, 1), bs: W.BJP.seats, t: SIR.d(W.AITC.per_100, 1), ts: W.AITC.seats, bv: (W.BJP.vs_district > 0 ? '+' : '') + SIR.d(W.BJP.vs_district, 1), tv: (W.AITC.vs_district > 0 ? '+' : '') + SIR.d(W.AITC.vs_district, 1) }), ['elections', 'faq']],
        [L('Where do these figures come from?'),
         L('The state\'s revision is from the Chief Electoral Officer\'s press note PN-05-2026. The three rolls by constituency are the Chief Electoral Officer\'s own tables, and the 2026 result is from the Election Commission\'s result pages. The <a href="../method/">method page</a> gives each source.'), ['method', 'faq']],
        [L('Does this show that the removals were intended to change results?'),
         L('No list of removals can show intent. The tables show where the roll fell and how that compares with the margins. They cannot show whose votes these were or whether each removal was right.'), ['elections', 'method']],
        [L('Can I look up my own name here?'),
         L('No. Only counts are published on this site. To check your own entry, use the Election Commission\'s voter search.'), ['main']]
      ];
      var limits = L('No count of the names removed is published by district or constituency, so those pages measure the fall in the roll from 2024. A reason on the list is what the officer wrote down, and nobody checked it.');
      var SHORT = {
        main: [[scale, women, fall, why], limits],
        elections: [[margin,
          L('Counted at each seat\'s own turnout, the fall still exceeds the margin in {k} seats.', { k: s.could_change }),
          L('The BJP won {b} seats and the AITC {t}.', { b: s.seats_2026.BJP, t: s.seats_2026.AITC })],
          L('The fall in the roll includes ordinary changes since 2024 as well as the revision, and the lists cannot show how anyone missing from the roll would have voted.')],
        method: [[
          L('The removals and their reasons are published for the state only.'),
          L('The rolls of 2024, the draft and the 2026 election are published by constituency and by sex, and every table adds up to its own totals.'),
          L('The fall in the roll from 2024 includes ordinary changes as well as the revision.')],
          L('A reason on the list is what the officer wrote down, and nobody checked it.')],
        faq: [[scale, women, fall, margin], limits]
      };
      return { qa: QA, short: SHORT };
    }));
  });
})();
