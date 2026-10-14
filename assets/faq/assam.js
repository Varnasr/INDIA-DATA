/* Questions and answers for the Assam pages, in English only for now.
   The FAQ tab shows them all; each page shows those tagged with its key
   (main, method, faq). The "In short" points for each page are in short. */
(function () {
  var P;
  SIR.faq('as', 'assam/faq/', function () {
    return P || (P = SIR.json('data/assam/summary.json').then(function (d) {
      var S = d.state, Z = d.seats, T = d.tribunals, X = d.detention, N = d.nrc, A = T.assembly_2026, n = SIR.n, lk = function (x) { return SIR.lk(x, 2); };
      var kind = 'Assam had a Special Revision of its roll in 2025-26, ordered by the Election Commission on 17 November 2025, and was left out of the Special Intensive Revision. No existing elector filled an enumeration form or showed a document to stay on the roll.';
      var flag = lk(S.flagged) + ' names were flagged for deletion with the draft roll of 27 December 2025, as dead, shifted, or entered more than once. The draft still held ' + n(S.draft_vs_jan) + ' more names than the roll of January 2025.';
      var fin = 'The final roll of 10 February 2026 holds ' + n(S.final) + ' electors, ' + n(S.draft - S.final) + ' fewer than the draft and ' + n(S.final_vs_jan) + ' more than the roll of January 2025.';
      var dv = n(S.d_voters_draft) + ' D-voters, electors whose citizenship a Foreigners Tribunal has yet to decide, were carried onto the draft unchanged and kept out of the house-to-house check.';
      var seat = 'Between the draft and the final roll, the roll fell in ' + Z.fell + ' of the 126 constituencies and rose in ' + Z.rose + '. Women were ' + SIR.pct(Z.women_fall_pct) + ' of the net fall, against ' + SIR.pct(Z.women_draft_pct) + ' of the draft.';
      var det = 'In November 2019 the six detention centres held ' + n(X.inmates) + ' people, ' + n(X.women) + ' of them women, and ' + X.died + ' people held in them died in hospital between March 2019 and February 2020.';
      var QA = [
        ['Why did Assam have a different revision?', kind + ' The order gives no reason why Assam was treated differently. Assam\'s citizenship questions run through the Foreigners Tribunals and the 2019 NRC, and the order says nothing about either beyond keeping D-voters as they were.', ['main', 'faq']],
        ['How many names were flagged in Assam?', flag + ' No figure from the Chief Electoral Officer says how many of the flagged names were off the published draft, so the pages call them flagged. ' + fin, ['main', 'faq']],
        ['What is a D-voter?', 'A doubtful voter, an elector whose citizenship has been questioned and sent to a Foreigners Tribunal. The category exists only in Assam. ' + dv + ' Their entries can be changed or deleted only on the order of a tribunal or a court. The Ministry of Home Affairs counted ' + n(d.d_voters[1].value) + ' in October 2019.', ['main', 'faq']],
        ['What did the tribunals decide?', 'To October 2019 they had declared ' + n(T.to_oct2019.foreigners) + ' people foreigners and ' + n(T.to_oct2019.indian) + ' Indian, and ' + n(T.pending_dec2020) + ' cases were pending at the end of 2020. In July 2026 the Chief Minister told the Assembly, as the press reported, that of ' + n(A.d_voter_cases_disposed_cumulative) + ' D-voter cases decided, ' + n(A.d_voters_declared_foreigners_by_FTs) + ' ended in a declaration of foreigner and ' + n(A.d_voters_declared_indian_by_FTs) + ' in a declaration of Indian. The report does not say what became of the other ' + n(A.d_voter_disposals_not_described) + '.', ['main', 'faq']],
        ['What do the figures say about detention?', det + ' These are the most recent figures for each centre that we found in a primary source, the Ministry of Home Affairs\' answers to the Lok Sabha. A centre for ' + n(X.matia_capacity) + ' at Matia was under construction in March 2020.', ['main', 'faq']],
        ['Is the revision connected to the NRC?', 'The order for the revision does not mention the NRC. The 2019 NRC left out ' + n(N.left_out) + ' of ' + n(N.applied) + ' applicants. By December 2021 no rejection orders had been issued, so those left out had not yet been able to appeal to a tribunal.', ['main', 'faq']],
        ['What do the constituency tables show?', 'The Chief Electoral Officer published the final roll of February 2024, the draft and the final roll by constituency and sex, and all three are on this page. Every constituency\'s draft held more names than its roll of February 2024. ' + seat + ' The tables give the net change only, so they cannot say how many names were deleted in a seat and how many added, and they say nothing about why.', ['main', 'method', 'faq']],
        ['Where do the figures come from?', 'The rules are from the Election Commission\'s order of 17 November 2025, read in full. The roll figures are the Chief Electoral Officer\'s, as The Hindu, The Tribune, India Today, the New Indian Express and All India Radio reported them. D-voters, tribunals, detention and the NRC are from the Ministry of Home Affairs\' answers to the Lok Sabha from 2019 to 2021, and for 2026 from the Assembly as the press reported it. The method page names each one.', ['method', 'faq']]
      ];
      var short = {
        main: [[kind, flag, seat, dv, det], 'The draft and final rolls by constituency are the Chief Electoral Officer\'s own tables, and the count of names flagged is the officer\'s as reported in the press. The constituency tables give the net change only. A reason entered for a flagged name is what the officer wrote down, and nobody checked it. The detention figures are from 2019 and 2020.'],
        method: [[kind, 'Every count on the Assam pages agrees with its parts. That holds for the draft with and without D-voters, the final roll by sex, the detention centres and their totals, and the tribunals\' yearly decisions and theirs.'], ''],
        faq: [[kind, flag, dv], '']
      };
      return { qa: QA, short: short };
    }));
  });
})();
