/* Questions and answers for the Tamil Nadu pages. The FAQ tab shows them all;
   each page shows those tagged with its key (main, elections, method). The
   "In short" points for each page are in SHORT. */
(function () {
  var P;
  SIR.faq('tn', 'tamilnadu/faq/', function () {
    return P || (P = SIR.json('data/tamilnadu/summary.json').then(function (s) {
      var C = s.chennai, W = {};
      s.winners.forEach(function (w) { W[w.party] = w; });
      var sg = function (v) { return (v > 0 ? '+' : '') + SIR.d(v, 1); };
      var cr = function (x) { return L('{x} crore', { x: (x / 1e7).toFixed(2) }); };
      var scale = L('The revision left {r} names off Tamil Nadu\'s draft roll, {p} of every 100 electors on the roll before it began.', { r: SIR.lakh(s.removed), p: SIR.d(s.per_100, 1) });
      var chen = L('Chennai lost {p} of every 100 electors, {x} times the state\'s rate of {sp}. Its {k} constituencies hold {roll} of the state\'s roll and {rem} of the names removed.', { p: SIR.d(C.per_100, 1), x: SIR.d(C.per_100 / s.per_100, 1), sp: SIR.d(s.per_100, 1), k: C.acs, roll: SIR.pct(s.chennai_share_of_roll), rem: SIR.pct(s.chennai_share_of_removed) });
      var why = L('{sh} were entered as shifted or absent, {dead} as dead and {mult} as enrolled in more than one place.', { sh: SIR.pct(s.shares.shifted_absent), dead: SIR.pct(s.shares.dead), mult: SIR.pct(s.shares.multiple) });
      var margin = L('In {k} of the {n} constituencies, more names were left off the draft roll than the 2026 winning margin.', { k: s.over_margin, n: s.acs });
      var back = L('The final roll of 23 February 2026 was {a} larger than the draft. That rise is at most {m} of the names removed, and it includes new voters.', { a: SIR.lakh(s.added_net), m: SIR.pct(s.made_up_pct) });
      var QA = [
        [L('How many names did the revision remove in Tamil Nadu?'),
         scale + ' ' + L('The roll before the revision held {b} names and the draft roll {d}.', { b: cr(s.before), d: cr(s.draft) }), ['main', 'faq']],
        [L('Why were the names removed?'),
         why + ' ' + L('A reason on the list is what the officer wrote down, and nobody checked it.'), ['main', 'faq']],
        [L('Where were removals heaviest?'),
         chen + ' ' + L('{a} and {b} come next. The seat with the most removals for its size is {hi}, at {hiv} per 100, and the one with the fewest is {lo}, at {lov}.', { a: s.top_districts[1], b: s.top_districts[2], hi: s.rate_max, hiv: SIR.d(s.rate_max_v, 1), lo: s.rate_min, lov: SIR.d(s.rate_min_v, 1) }), ['main']],
        [L('Do seats with more removals record more of them as shifted or absent?'),
         L('Yes. Across the {n} constituencies the removal rate and the share entered as shifted or absent rise together (rank correlation {rho}). Where many names were removed, most were marked as people who had moved or could not be found.', { n: s.acs, rho: SIR.d(s.rho_rate_shifted, 2) }), ['main']],
        [L('Were the names put back on the final roll?'),
         back + ' ' + L('Once the final roll is counted, the roll is still {f} smaller than before the revision, {p} of every 100 electors.', { f: SIR.lakh(s.net_fall), p: SIR.d(s.net_per_100, 1) }), ['main', 'elections', 'faq']],
        [L('Were women removed more than men?'),
         L('The Chief Electoral Officer has not published the removals by sex, or the roll by sex before the revision, so this cannot be counted. Women were {d} of the draft roll and {f} of the final roll.', { d: SIR.pct(s.women_draft_pct), f: SIR.pct(s.women_final_pct) }), ['main', 'method', 'faq']],
        [L('Could the removals have changed the 2026 result?'),
         margin + ' ' + L('Counting the names removed other than those marked dead, at each seat\'s own turnout, the removed voters outnumber the margin in {k} seats. In the other {o}, the runner-up could not have won even if every one of them had voted for the runner-up. The lists cannot show how anyone removed would have voted.', { k: s.could_change, o: s.acs - s.could_change }), ['elections', 'faq']],
        [L('Did the removals fall more heavily on one party\'s seats?'),
         L('Seats won by TVK lost {t} of every 100 electors, against {d} in seats won by the DMK and {a} in seats won by the AIADMK. Most of that gap is about where the seats are. TVK won most of the city seats, and the city seats lost the most names. Set against the average of their own district, TVK seats come out at {tv} per 100, DMK seats at {dv} and AIADMK seats at {av}, where a minus means fewer removals than the district as a whole.', { t: SIR.d(W.TVK.per_100, 1), d: SIR.d(W.DMK.per_100, 1), a: SIR.d(W.AIADMK.per_100, 1), tv: sg(W.TVK.vs_district), dv: sg(W.DMK.vs_district), av: sg(W.AIADMK.vs_district) }), ['elections', 'faq']],
        [L('Where do these figures come from?'),
         L('The removals by constituency and reason, and the draft and final rolls by constituency, are the Chief Electoral Officer\'s own tables. The 2026 result is from the Election Commission\'s result pages, and the 2021 result from the Commission\'s statistical report, through a published compilation of it. The <a href="../method/">method page</a> gives each source.'), ['method', 'faq']],
        [L('Why is the roll before the revision the draft roll plus the names removed?'),
         L('The Chief Electoral Officer published the removals against the draft roll, constituency by constituency, but no constituency table of the roll the revision started from. The draft plus the removals is that roll, and it adds up to the state total announced with the draft.'), ['method']],
        [L('Does this show that the removals were intended to change results?'),
         L('No list of removals can show intent. The tables show where the removals fell, on what recorded reason, and how the numbers compare with the margins. They cannot show whose votes these were or whether each removal was right.'), ['elections', 'method']],
        [L('Can I look up my own name here?'),
         L('No. Only counts are published on this site. To check your own entry, use the Election Commission\'s voter search.'), ['main']]
      ];
      var limits = L('A reason on the list is what the officer wrote down, and nobody checked it. The tables show where names were removed and cannot show why.');
      var SHORT = {
        main: [[scale, why, chen, back], limits],
        elections: [[margin,
          L('Once the names added for the final roll are counted, the fall in the roll still exceeds the margin in {k} seats.', { k: s.net_over_margin }),
          L('TVK won {t} seats, the DMK {d} and the AIADMK {a}. {c} of the {n} seats changed hands from 2021.', { t: s.seats_2026.TVK, d: s.seats_2026.DMK, a: s.seats_2026.AIADMK, c: s.changed_hands, n: s.acs }),
          L('Seats won by TVK lost the most names, mainly because TVK won most of the city seats.')],
          L('The lists cannot show how anyone removed would have voted, or whether each removal was right.')],
        method: [[
          L('The removals, both rolls and the 2026 result are published constituency by constituency, and every table adds up to its own totals.'),
          L('The Chief Electoral Officer has published no split of the removals by sex or age.'),
          L('The 2021 result is from the Election Commission\'s statistical report, through a published compilation of it.')],
          L('A reason on the list is what the officer wrote down, and nobody checked it.')],
        faq: [[scale, why, chen, margin], limits]
      };
      return { qa: QA, short: SHORT };
    }));
  });
})();
