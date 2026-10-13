/* Questions and answers for the Gujarat pages, in English only for now. The
   FAQ tab shows them all; each page shows those tagged with its key (main,
   elections, method, faq). The "In short" points for each page are in short. */
(function () {
  var P;
  SIR.faq('gj', 'gujarat/faq/', function () {
    return P || (P = Promise.all([SIR.json('data/gujarat/summary.json'), SIR.json('data/gujarat/districts.json'), SIR.json('data/india/notices.json')]).then(function (r) {
      var s = r[0], D = r[1], NT = r[2].states.filter(function (x) { return x.state === 'Gujarat'; })[0];
      var lk = function (x) { return SIR.lk(x, 1); }, cr = function (x) { return (x / 1e7).toFixed(2) + ' crore'; }, d1 = function (v) { return SIR.d(v, 1); };
      var sg = function (v) { return (v > 0 ? '+' : '') + d1(v); };
      var C = s.city, R = s.rest, W = {}, last = D[D.length - 1];
      s.winners.forEach(function (w) { W[w.party] = w; });
      var DL = function (iso) { var p = iso.split('-'); return +p[2] + ' ' + ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][+p[1] - 1] + ' ' + p[0]; };
      var scale = 'Gujarat\'s draft roll of ' + DL(s.draft_date) + ' left off ' + lk(s.removed) + ' names, ' + d1(s.per_100) + ' of every 100 electors on the roll before the revision.';
      var margin = 'In ' + s.over_margin + ' of the ' + s.acs + ' constituencies, more names were left off than the 2022 winning margin, and in ' + s.narrow_over_margin + ' even leaving out the names entered as dead or as enrolled elsewhere.';
      var city = 'Ahmedabad and Surat districts hold ' + SIR.pct(C.share_of_roll) + ' of the state\'s roll and ' + SIR.pct(C.share_of_removed) + ' of the names left off. They lost ' + d1(C.per_100) + ' of every 100 electors, against ' + d1(R.per_100) + ' in the other 31 districts.';
      var where = D[0].district + ' left off the most, ' + d1(D[0].per_100) + ' per 100, and ' + s.rate_max + ' the most of any constituency, ' + d1(s.rate_max_v) + '. ' + last.district + ' left off the fewest of the districts, ' + d1(last.per_100) + '.';
      var reasons = SIR.pct(s.shares.shifted) + ' of the names left off were entered as shifted for good, ' + SIR.pct(s.shares.dead) + ' as dead and ' + SIR.pct(s.shares.absent) + ' as untraceable or absent.';
      var final = 'The final roll of ' + DL(s.final_date) + ' is ' + lk(s.net) + ' larger than the draft, at most ' + SIR.pct(s.made_up_pct) + ' of the names left off, and still ' + lk(s.net_fall) + ' smaller than the roll before the revision.';
      var sex = 'No table published for Gujarat splits anything by sex, so whether women were left off more often than men cannot be counted.';
      var party = 'Seats the BJP won in 2022 lost ' + d1(W.BJP.per_100) + ' per 100 and the Congress\'s ' + d1(W.INC.per_100) + '. Set against their own districts the two are ' + sg(W.BJP.vs_district) + ' and ' + sg(W.INC.vs_district) + ' points, so the difference comes mostly from where each party\'s seats are.';
      var press = 'The figures are the tables of the Chief Electoral Officer (CEO), who keeps the state\'s rolls for the Election Commission, as published in the press. The CEO\'s own website carries none of them.';
      var QA = [
        ['How many names did the revision leave off in Gujarat?', scale + ' The draft roll is the list published once the enumeration forms were collected. Every elector on the roll was given a form to fill in and return, and a name whose form did not come back was left off the draft. The roll before the revision held ' + cr(s.before) + ' names and the draft ' + cr(s.draft) + '. One crore is ten million.', ['main', 'faq']],
        ['Why were the names left off?', reasons + ' ' + SIR.pct(s.shares.enrolled_elsewhere) + ' were already enrolled at another place and ' + SIR.pct(s.shares.other) + ' were left off for some other reason. A reason is what the officer wrote down, and nobody checked it.', ['main', 'faq']],
        ['Where were the most names left off?', where + ' ' + s.acs_over_25 + ' of the ' + s.acs + ' constituencies left off 25 or more of every 100 electors.', ['main', 'faq']],
        ['How do Ahmedabad and Surat compare with the rest of the state?', city + ' More of their names were entered as shifted for good, ' + SIR.pct(C.shifted_share) + ' against ' + SIR.pct(R.shifted_share) + ' elsewhere.', ['main', 'faq']],
        ['Could the names left off have changed the 2022 result?', margin + ' The winning margin is the winner\'s votes less the runner-up\'s. The election came three years before the revision, so this measures how large the removals are against the votes that decide a seat. Larger than the margin means large enough to decide a seat, and it says nothing about whether it would have. Nobody can say how anyone left off would have voted.', ['elections', 'faq']],
        ['Did one party\'s seats lose more names?', party + ' The BJP won most of the seats in Ahmedabad and Surat, where the most names were left off.', ['elections', 'faq']],
        ['Were women left off more than men?', sex + ' The Chief Electoral Officer\'s tables give the roll before the revision, the names left off, the draft and the final roll as totals only.', ['main', 'method', 'faq']],
        ['Have the names been put back?', final + ' The names added after the draft count new voters as well as names put back, so how many of those left off are back on the roll cannot be counted. The final roll is published by district only.' + (NT && NT.notices ? ' About ' + lk(NT.notices) + ' electors kept on the draft were to be sent a notice to prove their entry, according to the press.' : ''), ['main', 'faq']],
        ['Where do the figures come from?', press + ' They are images of the CEO office\'s printed tables, by district and by constituency, carried by DeshGujarat, and every row adds up to the printed totals. The 2022 result is from the Election Commission\'s own statistical report. The <a href="../method/">method page</a> gives each source.', ['method', 'faq']],
        ['Can I look up my own name here?', 'No. Only counts are published on this site. To check your own entry, use the Election Commission\'s voter search.', ['main']]
      ];
      var limits = press + ' Nothing is split by sex or age, and the final roll is by district only.';
      var short = {
        main: [[scale, margin, city, where, final], limits],
        elections: [[margin, (s.closest20_over === 20 ? 'In every one of the twenty closest seats of 2022, the names left off were more than the margin.' : 'In ' + s.closest20_over + ' of the twenty closest seats of 2022, the names left off were more than the margin.'), party], limits],
        method: [[scale, 'Every constituency row adds up two ways, and every column adds up to the printed district and state totals.', 'The printed final roll is ' + SIR.n(s.final_gap) + ' electors more than the draft plus the net change, and both are kept as printed.'], limits],
        faq: [[scale, margin, city], limits]
      };
      return { qa: QA, short: short };
    }));
  });
})();
