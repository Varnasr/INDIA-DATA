/* Questions and answers for the All India pages. The FAQ tab shows them all;
   each page shows those tagged with its key (main, method). The landing page
   keeps its own "In short" box; this file supplies the others. */
(function () {
  var P;
  SIR.faq('india', 'india/faq/', function () {
    return P || (P = SIR.json('data/india/states.json').then(function (d) {
      var T = d.total, S = d.states, A = d.adults, F = d.final, GG = d.gender, AD = d.after_draft;
      var cr = function (x) { return L('{x} crore', { x: (x / 1e7).toFixed(2) }); };
      var rated = S.filter(function (s) { return s.per_100 != null; }).sort(function (a, b) { return b.per_100 - a.per_100; });
      var wOver = GG.filter(function (g) { return g.gap > 1; }).length;
      var inc = d.correlations.filter(function (c) { return c.key === 'income_pc'; })[0];
      var fem = L('In {over} of the {n} states that report removals by sex, women are a bigger share of the names removed than of the roll.', { over: wOver, n: GG.length });
      var back = L('In the {n} states with a final roll, the rolls grew back by at most {m} of what the drafts removed, and that rise includes new voters.', { n: F.states, m: SIR.pct(F.made_up_pct) });
      var QA = [
        [L('How many names did the revision remove across India?'),
         L('{r} across {s} states and union territories when the draft rolls were published, {p} of every 100 electors on the rolls before the revision. Removals after the draft add {a} more in the {k} states that have reported them.', { r: cr(T.removed), s: T.states, p: SIR.d(T.per_100, 1), a: SIR.lakh(AD.removed), k: AD.states }), ['numbers', 'main', 'faq']],
        [L('Why were the names removed?'),
         L('Where a reason was given, {dead} were entered as dead, {sao} as shifted, absent or other, and {dup} as enrolled more than once. States reported their reasons in different ways, and the method page sets out how each was counted.', { dead: SIR.pct(T.shares.dead), sao: SIR.pct(T.shares.shifted_absent_other), dup: SIR.pct(T.shares.duplicate) }), ['main']],
        [L('Why did some states remove far more names than others?'),
         L('{hi} removed {hir} of every 100 electors and {lo} {lor}, under the same rules.', { hi: rated[0].state, hir: SIR.d(rated[0].per_100, 1), lo: rated[rated.length - 1].state, lor: SIR.d(rated[rated.length - 1].per_100, 1) }) + ' ' +
         (inc && Math.abs(inc.per_100_phase2) < 0.2 && Math.abs(inc.per_100_phase3) >= 0.2 ?
           L('Across all states the removal rate rises with income per head (rank correlation {all}), but only among the states revised in 2026 ({p3}). Among those revised from November 2025 it is {p2}, which is no relationship. The figures show where removals were heavy, and cannot show why.', { all: SIR.d(inc.per_100_all, 2), p3: SIR.d(inc.per_100_phase3, 2), p2: SIR.d(inc.per_100_phase2, 2) }) :
           L('The figures show where removals were heavy, and cannot show why.')), ['main']],
        [L('Were women removed more than men?'), fem, ['main', 'faq']],
        [L('Were the names put back on the final roll?'), L('Few of them.') + ' ' + back, ['numbers', 'main', 'faq']],
        [L('Why did the cities lose more names than their states?'),
         L('The lists do not say. In the cities most of the names left off were entered as shifted or absent. That fits people who had moved and were registered somewhere else, and it fits people who still live there and were out when the officer called. The count is the same either way.'), ['cities', 'faq']],
        [L('What counts as a city on the cities page?'),
         L('Its districts, because no state published its figures by city boundary. Each city\'s districts and its suburbs are listed at the foot of the page. Kolkata and Kochi are measured by the fall in the roll, because their states published no names left off below the state.'), ['cities', 'faq']],
        [L('Why is Patna not ranked with the other cities?'),
         L('Bihar published its roll before the revision for the state only, so its rate is counted against the 2025 roll, a different base from the other cities\'. On that count Patna lost fewer names than Bihar as a whole.'), ['cities', 'faq']],
        [L('Were the rolls over-full before the revision?'),
         L('Mostly not. Across the {n} states with population projections, the rolls held {pre} of adults before the revision, and only {k} had more names on the roll than adults.', { n: A.states, pre: SIR.pct(100 * A.roll_total / A.adults_total), k: A.over_100.length }) + ' ' +
         (Math.abs(A.rho_rate) < 0.2 ? L('States with the fullest rolls did not remove more.') : ''), ['main']],
        [L('Where do these figures come from?'),
         L('From each state\'s Chief Electoral Officer, as announced with the draft and final rolls. The Election Commission has published no national table. For Bihar they are counted from the deletion lists themselves.'), ['numbers', 'method', 'faq']],
        [L('Why are some rows marked as rounded or short?'),
         L('Some states announced figures rounded to the nearest thousand or lakh, and some gave reasons that do not add up to their own total. Those rows are kept as the state published them and flagged, so a reader can see how far each one can be trusted.'), ['numbers', 'method', 'faq']],
        [L('Why do some states look short of electors?'),
         L('The adult figures are population projections, which count people where they live. A state that draws migrants counts them as residents while many are still registered to vote in their home states, so its roll looks short.'), ['method']],
        [L('Does this show that the removals were intended to change results?'),
         L('No list of removals can show intent. The lists show where the removals fell, who was removed and how the numbers compare with the margins. They cannot show whose votes these were or whether each removal was right.'), ['main', 'method']],
        [L('What does "not yet found" mean for a final roll?'),
         L('That the latest schedule we could read set a date for the final roll, the date has passed, and we have not found the roll published. The Commission may have moved the date in an order we have not read, or the state may have published the roll where we have not looked. It says nothing about why a roll is late.'), ['progress', 'faq']],
        [L('Which states are not in the revision?'),
         L('Assam was given a special revision in place of an intensive one. Himachal Pradesh, Jammu and Kashmir and Ladakh were left out of the order, which said their dates would be announced later. Every other state and union territory is in it.'), ['progress', 'faq']],
        [L('Where do the dates come from?'),
         L('From the Election Commission\'s orders and the states\' own press notes, each listed with its document on the page about <a href="../process/">how the revision was run</a>. Where a state has published its final roll, the date it came out replaces the date it was due.'), ['progress', 'faq']],
        [L('Can I look up my own name here?'),
         L('No. Only counts are published on this site. To check your own entry, use the Election Commission\'s voter search.'), ['main']]
      ];
      var SHORT = {
        faq: [[
          L('The revision removed {r} names across {s} states and union territories at the draft, {p} of every 100 electors.', { r: cr(T.removed), s: T.states, p: SIR.d(T.per_100, 1) }),
          L('Where a reason was given, {sao} were entered as shifted, absent or other, and {dead} as dead.', { sao: SIR.pct(T.shares.shifted_absent_other), dead: SIR.pct(T.shares.dead) }),
          fem, back], L('A reason on the list is what the officer wrote down, and nobody checked it.')],
        method: [[
          L('The Election Commission has published no national table of removals, so each row is the state\'s own announcement.'),
          L('Rows are flagged where the figures were rounded or where the reasons do not add up to the total.'),
          L('For Bihar the figures are counted from the deletion lists on this site.')],
          L('Population projections count people where they live, so states that draw migrants look short of electors who are registered in their home states.')]
      };
      return { qa: QA, short: SHORT };
    }));
  });
})();
