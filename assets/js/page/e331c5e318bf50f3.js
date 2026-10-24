Promise.all([SIR.json('data/india/states.json'), SIR.json('data/india/process.json'), SIR.json('data/india/disputes.json'), SIR.json('data/india/rti.json'),
  SIR.json('data/india/women.json'), SIR.json('data/india/margins.json'), SIR.json('data/bihar/impact.json'), SIR.json('data/india/brief.json')]).then(function (r) {
  var I = r[0], P = r[1], Dp = r[2], R = r[3], W = r[4].summary, M = r[5], Im = r[6], B = r[7], n = SIR.n, esc = SIR.esc, T = I.total, F = I.final;
  var sec = function (id) { var s = Dp.sections.filter(function (x) { return x.id === id; })[0]; return s ? (s.items || []).length : 0; };
  var lo = Math.min(Im.summary.booth_lower.flips, Im.summary.booth_upper.flips), hi = Math.max(Im.summary.booth_lower.flips, Im.summary.booth_upper.flips);
  var over = M.removed.assembly_over, seats = M.removed.assembly_seats;

  SIR.inShort([
    SIR.lk(T.removed) + ' names were left off the draft rolls of ' + T.states + ' states and union territories, ' + SIR.d(T.per_100, 1) + ' of every 100 electors.',
    'Taken together, the ' + F.states + ' final rolls made up at most ' + SIR.d(F.made_up_pct, 1) + '% of the names left off (' + SIR.d(F.made_up_pct_ex_withheld, 1) + '% without West Bengal\'s ' + SIR.lk(F.withheld, 0) + ' names held for adjudication), and that rise counts new voters too.',
    'Women were the larger share of the names left off in ' + W.over + ' of the ' + W.states + ' states that published a count by sex.',
    'In ' + M.removed.states.join(' and ') + ', more names were left off or deleted than the winning margin in ' + n(over) + ' of ' + n(seats) + ' assembly seats. That means those names could have decided those seats. It does not show that they did.'
  ], 'This page gathers the findings of the other pages and adds the law on protest. It is general information and is not legal advice. Nothing on it says what anyone intended.');

  document.getElementById('happened').innerHTML = [
    'The Election Commission revised the electoral rolls of ' + T.states + ' states and union territories house by house, in three phases from June 2025. Every elector on the roll had to fill in and return a fresh form, and a name whose form did not come back was left off the draft roll.',
    SIR.lk(T.removed) + ' names were left off the drafts. The officers recorded ' + SIR.d(T.shares.shifted_absent_other, 1) + '% as shifted, absent or another reason, ' + SIR.d(T.shares.dead, 1) + '% as dead and ' + SIR.d(T.shares.duplicate, 1) + '% as enrolled more than once.',
    'Taken together, in the ' + F.states + ' states whose final rolls are out, the roll grew after the draft by at most ' + SIR.d(F.made_up_pct, 1) + '% of the names left off, or ' + SIR.d(F.made_up_pct_ex_withheld, 1) + '% without West Bengal\'s ' + SIR.lk(F.withheld, 0) + ' names held for adjudication. State by state the share ran much higher in some places, and <a href="../compare/#how-much-the-final-roll-made-up">Reserved seats, final rolls and borders</a> gives each one. That rise counts new electors as well as names put back, so the share put back is no larger and may be smaller.',
    'Women were the larger share of the names left off in ' + W.over + ' of ' + W.states + ' states and ' + W.district_over + ' of ' + W.district_n + ' districts with a count by sex. <a href="../women/">Women</a> has every count.',
    'In ' + M.removed.states.join(' and ') + ', more names were left off or deleted than the winning margin in ' + n(over) + ' of ' + n(seats) + ' assembly seats. <a href="../numbers/#against-the-winning-margins">Against the winning margins</a> sets out every comparison.'
  ].map(function (t) { return '<li>' + t + '</li>'; }).join('');

  // the burdens carry {placeholders} for counts taken from the schedules
  var moves = function (r) { return r.steps.filter(function (st) { return st.kind !== 'published'; }).length - 1; };
  var ph = function (p) { return P.schedules.filter(function (r) { return r.phase === p; }); };
  var fill = { p2_states: ph('II').length, p2_again: ph('II').filter(function (r) { return moves(r) > 1; }).length,
    p3_states: ph('III').length, p3_moved: ph('III').filter(function (r) { return moves(r) > 0; }).length };
  var claims = I.states.filter(function (s) { return s.removed && s.added_after_draft != null; });
  fill.claims_states = claims.length;
  fill.claims_fewer = claims.filter(function (s) { return s.added_after_draft < s.removed; }).length;
  fill.claims_lead = fill.claims_fewer === fill.claims_states ? 'All ' + fill.claims_states + ' states that published both counts' : fill.claims_fewer + ' of the ' + fill.claims_states + ' states that published both counts';
  fill.claims_under10 = claims.filter(function (s) { return 100 * s.added_after_draft / s.removed < 10; }).length;
  var docs = P.burdens.map(function (b) {
    return '<li><b>' + esc(b.title) + '.</b> ' + esc(b.text.replace(/\{(\w+)\}/g, function (m, k) { return fill[k]; })) + ' ' + b.src.map(function (s) { return '<a href="' + esc(s.url) + '" rel="noopener">' + esc(s.name) + '</a>'; }).join(', ') + '.</li>';
  });
  docs.push('<li><b>In the courts.</b> ' + n(sec('courts')) + ' court orders and cases are listed on <a href="../disputes/">Protests and disputes</a>, each linked to the order or report.</li>');
  document.getElementById('documented').innerHTML = docs.join('');

  document.getElementById('reported').innerHTML = [
    '<b>Inside the Commission.</b> The Indian Express reported that two of the three Election Commissioners objected on record, at least 14 times, to decisions taken in the Commission\'s name. The Commission called the notes suggestions and said every decision was unanimous. <a href="../process/#inside-the-commission">Inside the Commission</a> sets out the account by date.',
    '<b>Form 7 objections in bulk.</b> ' + n(sec('form7')) + ' reports of objections filed by a few people at once, some on forms with the elector\'s details already printed. An objection does not delete a name by itself. <a href="../disputes/#form7">The Form 7 section</a> lists each one.',
    '<b>Changes to the software.</b> ' + n(sec('software') + sec('instructions')) + ' reports of changes to the Commission\'s software and of instructions given without a written order. <a href="../disputes/">Protests and disputes</a> lists each with its source.',
    '<b>Requests under the RTI Act.</b> ' + n(R.counts.items) + ' applications whose replies were reported, and in ' + n((R.by_outcome['no record held'] || 0)) + ' of them the authority said it held no record of what was asked. <a href="../rti/">RTI replies</a> lists each one.',
    '<b>Other reports.</b> ' + n(P.reported.length) + ' press reports on how the revision was run, each attributed to its outlet, are on <a href="../process/#reported-not-confirmed-by-a-document">How the revision was run</a>.'
  ].map(function (t) { return '<li>' + t + '</li>'; }).join('');

  document.getElementById('cannotSeat').innerHTML = 'They cannot show that the names left off or deleted decided an election. In Bihar, the one state where how those electors would have voted can be estimated, the estimates have ' + lo + ' to ' + hi + ' seats changing hands, in both directions. <a href="../../bihar/results/">Bihar\'s elections page</a> sets out how.';

  document.getElementById('asof').textContent = SIR.date(B.as_of);
  var html = '';
  B.groups.forEach(function (g) {
    var its = B.rights.filter(function (x) { return x.group === g; }); if (!its.length) return;
    html += '<h3>' + esc(g) + '</h3><ol class="nfacts rights">' + its.map(function (x) {
      return '<li><p>' + esc(x.point) + '</p><p class="nsrc"><a href="' + esc(x.url) + '" rel="noopener">' + esc(x.law) + '</a></p>' +
        '<details><summary>The words of the law</summary><blockquote>' + esc(x.quote) + '</blockquote></details></li>';
    }).join('') + '</ol>';
  });
  document.getElementById('secEnd').insertAdjacentHTML('beforebegin', html);

  SIR.anchors && SIR.anchors();
  SIR.toc && SIR.toc();
  SIR.showFaq('india', 'brief');
  SIR.jump && SIR.jump();
}).catch(SIR.fail);
