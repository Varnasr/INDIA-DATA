/* Questions and answers for the Maharashtra pages, in English only for now.
   The FAQ tab shows them all; each page shows those tagged with its key (main,
   method, faq). The "In short" points for each page are in short. */
(function () {
  var P;
  SIR.faq('mh', 'maharashtra/faq/', function () {
    return P || (P = Promise.all([SIR.json('data/maharashtra/summary.json'), SIR.json('data/maharashtra/districts.json'), SIR.json('data/india/notices.json')]).then(function (r) {
      var s = r[0], D = r[1], NT = r[2].states.filter(function (x) { return x.state === 'Maharashtra'; })[0];
      var cr = function (x) { return (x / 1e7).toFixed(2) + ' crore'; }, lk = function (x) { return SIR.lk(x, 1); }, d1 = function (v) { return SIR.d(v, 1); };
      var C = s.city, R = s.rest, last = D[D.length - 1], most = D.filter(function (d) { return d.district === s.most_names; })[0];
      var list = function (a) { return a.slice(0, -1).join(', ') + ' and ' + a[a.length - 1]; };
      var DL = function (iso) { var p = iso.split('-'); return +p[2] + ' ' + ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][+p[1] - 1] + ' ' + p[0]; };
      var scale = 'Maharashtra\'s draft roll of ' + DL(s.draft_date) + ' left off ' + cr(s.left_off) + ' names, ' + d1(s.per_100) + ' of every 100 electors on the roll before the revision.';
      var where = D[0].district + ' left off ' + d1(D[0].per_100) + ' of every 100 electors, the most of the ' + s.districts + ' districts, and ' + list(D.slice(1, 5).map(function (d) { return d.district; })) + ' come next. ' + last.district + ' left off the fewest, ' + d1(last.per_100) + '.';
      var city = 'The five districts of Mumbai City, Mumbai Suburban, Thane, Palghar and Pune hold ' + SIR.pct(C.share_of_roll) + ' of the state\'s roll and ' + SIR.pct(C.share_of_left_off) + ' of the names left off. They lost ' + d1(C.per_100) + ' of every 100 electors, against ' + d1(R.per_100) + ' in the other ' + (s.districts - s.city_names.length) + ' districts.';
      var mostS = most.district + ' lost the most names of any district, ' + lk(most.left_off) + '.';
      var notices = NT && NT.notices ? 'Of the electors kept on the draft roll, ' + cr(NT.notices) + ' were sent a notice to prove their entry, according to the press, ' + d1(NT.per_100) + ' of every 100.' : '';
      var after = 'Claims and objections run to ' + DL(s.claims_to) + ', and the final roll is due on ' + DL(s.final_due) + '. Until it is out, nobody can say how many of the names left off will be put back.';
      var sh = s.reason_shares;
      var reasons = SIR.pct(sh.shifted) + ' of the names left off were entered as shifted for good, ' + SIR.pct(sh.absent) + ' as untraceable or absent, ' + SIR.pct(sh.dead) + ' as dead, ' + SIR.pct(sh.duplicate) + ' as enrolled at another place and ' + SIR.pct(sh.other) + ' under another reason, by the Chief Electoral Officer\'s own tables.';
      var seats = s.top_acs[0].name + ' lost ' + d1(s.top_acs[0].per_100) + ' of every 100 names, the most of the ' + s.acs_n + ' constituencies, and in ' + s.over_margin + ' of them more names were left off than the 2024 winning margin.';
      var QA = [
        ['How many names did the revision leave off in Maharashtra?', scale + ' The draft roll is the list published once the enumeration forms were collected. Every elector on the roll was given an enumeration form to fill in and return, and a name whose form did not come back was left off the draft. The roll before the revision held ' + cr(s.before) + ' names and the draft ' + cr(s.draft) + '.', ['main', 'faq']],
        ['Where were the most names left off?', where + ' ' + mostS + ' ' + s.over_30 + ' districts left off 30 or more of every 100 electors, and ' + s.under_15 + ' left off fewer than 15.', ['main', 'faq']],
        ['How do Mumbai and Pune compare with the rest of the state?', city, ['main', 'faq']],
        ['Why were the names left off?', reasons + ' The five add up to the names left off exactly, for the state, every district and every constituency. A reason is what the officer wrote down, and nobody checked it.', ['main', 'method', 'faq']],
        ['Could the names left off have changed the 2024 result?', seats + ' Scaled down by each seat\'s 2024 turnout it is ' + s.turnout_over_margin + '. Larger than the margin means large enough to decide a seat, and it says nothing about whether it would have. Nobody can know how anyone left off would have voted.', ['main', 'faq']],
        ['Were women left off more than men?', 'This cannot be counted. The Chief Electoral Officer published the draft roll by sex and nothing else by sex. The roll before the revision and the names left off are given as totals only. Women are ' + SIR.pct(s.women_draft_pct) + ' of the draft roll, from ' + SIR.pct(s.women_low.pct) + ' in ' + s.women_low.district + ' to ' + SIR.pct(s.women_high.pct) + ' in ' + s.women_high.district + '.', ['main', 'method', 'faq']],
        ['Have the names been put back?', after + (notices ? ' ' + notices : ''), ['main', 'faq']],
        ['Where do the constituency figures come from?', 'The Chief Electoral Officer published every one of the 288 constituencies in two tables. A statement enclosed with its press note of 16 September 2026 gives the roll before the revision and the names left off, and its tables of 1 September 2026 give the five reasons and the draft roll by sex. Every constituency adds up within itself and to its district, and the districts add up to the state.', ['main', 'method', 'faq']],
        ['Where do the figures come from?', 'The draft roll by district and sex, and the names left off by district, are from the Chief Electoral Officer\'s press note of ' + DL(s.draft_date) + '. The constituency figures and the reasons are from its tables of 1 and 16 September 2026, and the notices from its release of 4 September. Every figure adds up to the state figures in the note. The <a href="../method/">method page</a> gives each source.', ['method', 'faq']],
        ['Can I look up my own name here?', 'No. Only counts are published on this site. To check your own entry, use the Election Commission\'s voter search.', ['main']]
      ];
      var limits = 'The Chief Electoral Officer published no split of the names left off by sex, and a reason is what the officer wrote down, so these pages show where names were left off and what was entered, and cannot show why.';
      var short = {
        main: [[scale, seats, where, city, reasons, after], limits],
        method: [[scale, 'Every figure is from the Chief Electoral Officer\'s own tables, for the state, all 36 districts and all 288 constituencies, and every column adds up to the state figures.', 'Nothing has been published on the names left off by sex.'], limits],
        faq: [[scale, where, city], limits]
      };
      return { qa: QA, short: short };
    }));
  });
})();
