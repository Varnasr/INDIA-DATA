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
      var wOver = GG.filter(function (g) { return g.women_share_removed > g.women_share_roll; }).length;
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
           L('Across all states the removal rate rises with income per head (rank correlation {all}), but only among the states revised in 2026 ({p3}). Among those ordered in October 2025, with house visits from November, it is {p2}, which is no relationship. The figures show where removals were heavy, and cannot show why.', { all: SIR.d(inc.per_100_all, 2), p3: SIR.d(inc.per_100_phase3, 2), p2: SIR.d(inc.per_100_phase2, 2) }) :
           L('The figures show where removals were heavy, and cannot show why.')), ['main']],
        [L('Were women removed more than men?'), fem, ['main', 'faq']],
        [L('Were the names put back on the final roll?'), L('Few of them.') + ' ' + back, ['numbers', 'main', 'faq']],
        [L('Why did the cities lose more names than their states?'),
         L('The lists do not say. In the cities most of the names left off were entered as shifted or absent. That fits people who had moved and were registered somewhere else, and it fits people who still live there and were out when the officer called. The count is the same either way.'), ['cities', 'faq']],
        [L('What counts as a city on the cities page?'),
         L('Its districts, because no state published its figures by city boundary. Each city\'s districts and its suburbs are listed at the foot of the page. Kolkata and Kochi are measured by the fall in the roll, because their states published no names left off below the state.'), ['cities', 'faq']],
        [L('Why is Patna not ranked with the other cities?'),
         L('Bihar published its roll before the revision for the state only, so its rate is counted against the 2025 roll, a different base from the other cities\'. On that count Patna lost fewer names than Bihar as a whole.'), ['cities', 'faq']],
        [L('Why were more women removed than men?'),
         L('The lists do not say. They record what happened to each entry and nothing about why. In Bihar, the one state whose lists were counted name by name, women were a larger share of those entered as dead than of the state\'s adult deaths, and marriage does not explain where young women were marked as shifted.'), ['women', 'faq']],
        [L('Which states published the removals by sex?'),
         L('{n} states and union territories, listed at the foot of the women page with a note on how good each figure is. The others published totals only, so nothing can be said about women there.', { n: GG.length }), ['women', 'faq']],
        [L('Why is Delhi different?'),
         L('In Delhi men were left off more often than women. The figures do not say why. Delhi draws more men than women from other states for work, and a man registered both in Delhi and in his home state would be removed from one of them, but the counts cannot show whether that is what happened.'), ['women', 'faq']],
        [L('Did village districts or town districts lose more names?'),
         L('In most states with figures by district, the more of a district\'s people lived in towns, the more names it lost for its size. Much of that comes from the cities, and in some states it holds among village and small-town districts too. The urban page sets out each state in its own measure.'), ['urban', 'faq']],
        [L('How is a district called rural, mixed or urban?'),
         L('By the share of its people living in towns at the 2011 Census, the last count by district. Under 20 in every 100 is rural, 20 to 50 is mixed and above 50 is urban. A district made after 2011 is counted under the district it was mostly made from.'), ['urban', 'faq']],
        [L('Do poorer or less schooled districts lose more names?'),
         L('Not as a rule. In several states with survey figures by district, the districts where women had more years of school and more homes cooked with gas lost more names, and those are mostly the more urban districts. The district factors page gives every state, including those that run the other way, and it cannot say why, because these circumstances move together.'), ['factors', 'faq']],
        [L('Where do the district circumstances come from?'),
         L('From the National Family Health Survey 2019-21, which published a fact sheet for every district, and from the 2011 Census for urban share and density. A district made after the survey is counted under the district it was made from.'), ['factors', 'faq']],
        [L('Where can I find how many names were added and removed in each constituency after the draft?'),
         L('Only Uttarakhand published that, constituency by constituency. Tamil Nadu, Kerala and West Bengal published their draft and a later roll by constituency, so the change between them is a net figure, which counts new voters as well as names put back. <a href="../constituencies/">The constituencies page</a> puts all four states in one table and one download.'), ['constituencies', 'faq']],
        [L('Where do the protests and disputes on this site come from?'),
         L('From the courts\' own orders, the Assemblies\' records, the Commission\'s own documents and named press reports. Each item links to its source and quotes it, and a second reader matched every one to that source. A report that could not be matched is left off and named at the foot of <a href="../disputes/">the disputes page</a>.'), ['disputes', 'faq']],
        [L('How many RTI applications have been filed about the SIR?'),
         L('No published figure answers that. No authority publishes the number of applications under the Right to Information Act by subject, in any state or district. The Central Information Commission\'s yearly returns give each public authority\'s total with no split by subject. <a href="../rti/">The RTI page</a> lists the applications whose replies were published or reported.'), ['rti', 'faq']],
        [L('Does this site say the revision was meant to remove voters?'),
         L('No. The counts show how many names were left off, where, and the reason an officer wrote against each. They cannot show what anyone intended, and the site does not claim to know. <a href="../brief/">The SIR in brief</a> separates what is documented from what has been reported and from what the figures cannot show.'), ['brief', 'faq']],
        [L('Is the section on protest legal advice?'),
         L('No. It is general information about the law, each point read against the bare act, the Constitution, the judgment or NALSA\'s own site by two readers. The facts of a particular protest can change how the law applies, and rules on permission differ from place to place, so ask a lawyer or the local legal services authority. The national legal aid helpline is 15100.'), ['brief', 'faq']],
        [L('Does a piece listed under further reading have the site\'s agreement?'),
         L('No. Every piece there was opened and read twice, to check its title, its outlet, its date and the one line that says what it shows. That is all the listing vouches for. The pieces disagree with each other in places, most of all on whether the deletions changed the result in West Bengal, and the page says so.'), ['reading', 'faq']],
        [L('Can I suggest a piece to read or watch?'),
         L('Yes. Send it through <a href="../../share/">the form for sharing a list</a>. A piece is added once it has been read and its summary checked against it.'), ['reading', 'faq']],
        [L('Why do some commentators say more than this site does?'),
         L('Some use data the site does not hold, such as the outcomes of West Bengal\'s adjudication seat by seat. Some compare groups of seats without allowing for the other ways those seats differ. Some read a purpose into a pattern in the figures, which the lists cannot show. The panels on <a href="../reading/#what-others-say">the reading page</a> set each claim beside the site\'s own figures and say where those figures stop.'), ['reading', 'faq']],
        [L('Can I send you an RTI reply I received?'),
         L('Yes. Send it through <a href="../../share/">the form for sharing a list</a>, with the date you filed the application. We publish what was asked and what came back, and we name you only if you ask us to.'), ['rti', 'faq']],
        [L('What is a bulk Form 7 objection?'),
         L('Form 7 is the form for objecting to a name on the roll, for example because the person has died or moved. Several states reported many objections filed by a few people at once, some on forms with the elector\'s details already printed. An objection does not remove a name by itself. The officer has to give the elector notice and decide. <a href="../disputes/#form7">The disputes page</a> lists the reports and what officials did.'), ['disputes', 'faq']],
        [L('Did the Commission change its software during the revision?'),
         L('The press reported several changes to ECINET and ERONET while the revision was under way, including new options for clearing notices that appeared on 30 September 2026 and were explained to officers by video. The Commission has said its software gives field officers access by role. <a href="../disputes/#software">The disputes page</a> lists each report with the Commission\'s reply where one was given.'), ['disputes', 'faq']],
        [L('Is the SIR the same as the NRC?'),
         L('No. The NRC is a register of citizens under the Citizenship Act, and the SIR was a revision of the electoral rolls under the law on elections. The Supreme Court held on 27 May 2026 that declining to enrol someone does not declare that person not to be a citizen, and that deciding citizenship belongs to the authority under the Citizenship Act. <a href="../nrc/">The NRC page</a> sets the two side by side.'), ['nrc', 'faq']],
        [L('Has an NRC been prepared for the whole country?'),
         L('No. In answers to the Lok Sabha from February 2020 to March 2023, the Ministry of Home Affairs said the Government had taken no decision to prepare one at the national level. Assam\'s register was updated under rules made for Assam alone.'), ['nrc', 'faq']],
        [L('How many people were left out of Assam\'s NRC?'),
         L('The lists published on 31 August 2019 found 3,11,21,004 people eligible and left out 19,06,657. The Ministry of Home Affairs told the Lok Sabha in 2021 that the final NRC had not been issued and that no rejection orders had gone out, so no one left out had yet appealed to a Foreigners Tribunal.'), ['nrc', 'faq']],
        [L('Which union territories were in the revision?'),
         L('Six of the eight. Delhi, Chandigarh, Puducherry, Lakshadweep, Andaman and Nicobar, and Dadra and Nagar Haveli and Daman and Diu were revised. Jammu and Kashmir and Ladakh were left out of the order, which said their dates would be announced later. Each territory has its own page.'), ['uts', 'faq']],
        [L('Did seats reserved for Scheduled Castes and Tribes lose more names?'),
         L('No. In the states with figures by constituency, reserved seats lost a smaller share of their roll than general seats, and mostly still did when set against the general seats of their own district. A reserved seat describes a place, though, and most of its electors usually do not belong to the group it is reserved for, so this says nothing about which electors were removed.'), ['compare', 'faq']],
        [L('Did border districts lose more names?'),
         L('Not in any one way. On the Government of India\'s own list of border districts, they lost more than the rest of their state in Bihar and Uttarakhand, about the same in Uttar Pradesh, and fewer in Gujarat and West Bengal. A border district\'s rate says nothing about any elector\'s citizenship.'), ['compare', 'faq']],
        [L('Where does the list of border districts come from?'),
         L('It is the Government of India\'s list of Border Guarding Districts, printed in the Staff Selection Commission\'s notice of 1 December 2025 for constables in the Home Ministry\'s armed police forces. No district on it was picked by this site. Its seven Bihar districts are the seven Nepal-border districts the Bihar pages use.'), ['compare', 'faq']],
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
