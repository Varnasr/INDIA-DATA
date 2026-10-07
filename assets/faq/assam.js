/* Questions and answers for the Assam pages, in English only for now.
   The FAQ tab shows them all; each page shows those tagged with its key
   (main, method, faq). The "In short" points for each page are in short. */
(function () {
  var P;
  SIR.faq('as', 'assam/faq/', function () {
    return P || (P = SIR.json('data/assam/summary.json').then(function (d) {
      var S = d.state, T = d.tribunals, X = d.detention, N = d.nrc, A = T.assembly_2026, n = SIR.n, lk = function (x) { return SIR.lk(x, 2); };
      var kind = 'Assam had a Special Revision of its roll in 2025-26, ordered by the Election Commission on 17 November 2025, and was left out of the Special Intensive Revision. No existing elector filled an enumeration form or showed a document to stay on the roll.';
      var flag = lk(S.flagged) + ' names were flagged for deletion with the draft roll of 27 December 2025, as dead, shifted, or entered more than once. The draft still held ' + n(S.draft_vs_jan) + ' more names than the roll of January 2025.';
      var fin = 'The final roll of 10 February 2026 holds ' + n(S.final) + ' electors, ' + n(S.draft - S.final) + ' fewer than the draft and ' + n(S.final_vs_jan) + ' more than the roll of January 2025.';
      var dv = n(S.d_voters_draft) + ' D-voters, electors whose citizenship a Foreigners Tribunal has yet to decide, were carried onto the draft unchanged and kept out of the house-to-house check.';
      var det = 'In November 2019 the six detention centres held ' + n(X.inmates) + ' people, ' + n(X.women) + ' of them women, and ' + X.died + ' people held in them died in hospital between March 2019 and February 2020.';
      var QA = [
        ['Why did Assam have a different revision?', kind + ' The order gives no reason why Assam was treated differently. Assam\'s citizenship questions run through the Foreigners Tribunals and the 2019 NRC, and the order says nothing about either beyond keeping D-voters as they were.', ['main', 'faq']],
        ['How many names were removed in Assam?', flag + ' No figure from the Chief Electoral Officer says how many of the flagged names were off the published draft, so the pages call them flagged. ' + fin, ['main', 'faq']],
        ['What is a D-voter?', 'A doubtful voter, an elector whose citizenship has been questioned and sent to a Foreigners Tribunal. The category exists only in Assam. ' + dv + ' Their entries can be changed or removed only on the order of a tribunal or a court. The Ministry of Home Affairs counted ' + n(d.d_voters[1].value) + ' in October 2019.', ['main', 'faq']],
        ['What did the tribunals decide?', 'To October 2019 they had declared ' + n(T.to_oct2019.foreigners) + ' people foreigners and ' + n(T.to_oct2019.indian) + ' Indian, and ' + n(T.pending_dec2020) + ' cases were pending at the end of 2020. In July 2026 the Chief Minister told the Assembly, as the press reported, that of ' + n(A.d_voter_cases_disposed_cumulative) + ' D-voter cases decided, ' + n(A.d_voters_declared_foreigners_by_FTs) + ' ended in a declaration of foreigner and ' + n(A.d_voters_declared_indian_by_FTs) + ' in a declaration of Indian. The report does not say what became of the other ' + n(A.d_voter_disposals_not_described) + '.', ['main', 'faq']],
        ['What do the figures say about detention?', det + ' These are the most recent figures for each centre that we found in a primary source, the Ministry of Home Affairs\' answers to the Lok Sabha. A centre for ' + n(X.matia_capacity) + ' at Matia was under construction in March 2020.', ['main', 'faq']],
        ['Is the revision connected to the NRC?', 'The order for the revision does not mention the NRC. The 2019 NRC left out ' + n(N.left_out) + ' of ' + n(N.applied) + ' applicants. By December 2021 no rejection orders had been issued, so those left out had not yet been able to appeal to a tribunal.', ['main', 'faq']],
        ['Why is there no district or constituency table?', 'The Chief Electoral Officer published the draft and final rolls by constituency, but the office\'s website could not be reached from outside India while this page was made. Every state figure here is the Chief Electoral Officer\'s as reported in the press. The tables will be added when they can be read.', ['main', 'method', 'faq']],
        ['Where do the figures come from?', 'The rules are from the Election Commission\'s order of 17 November 2025, read in full. The roll figures are the Chief Electoral Officer\'s, as The Hindu, The Tribune, India Today, the New Indian Express and All India Radio reported them. D-voters, tribunals, detention and the NRC are from the Ministry of Home Affairs\' answers to the Lok Sabha from 2019 to 2021, and for 2026 from the Assembly as the press reported it. The method page names each one.', ['method', 'faq']]
      ];
      var short = {
        main: [[kind, flag, dv, det], 'The roll figures are the Chief Electoral Officer\'s as reported in the press, and no district or constituency table could be read. A reason for deletion is what the officer wrote down, and nobody checked it. The detention figures are from 2019 and 2020.'],
        method: [[kind, 'Every count on the Assam pages is checked against its parts, the draft with and without D-voters, the final roll by sex, the detention centres against their totals and the tribunals\' yearly decisions against theirs.'], ''],
        faq: [[kind, flag, dv], '']
      };
      return { qa: QA, short: short };
    }));
  });
})();
