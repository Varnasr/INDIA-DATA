/* One page per assembly constituency, drawn from the state's own published
   constituencies.json when the page loads, so no figure is written into the
   page. A seat page's source is three lines: its state and its number, in
   <body data-seat-state data-seat-ac> (scripts/make_seat_pages.py writes
   them), and this script.

   Each state is read in its own measure, named beside every figure, and a
   seat is set against its own district and its own state, never against a
   seat of another state. Sections a state's tables cannot fill are left out
   and the limits line says what is missing. English only, like the other
   2026 state pages. */
(function () {
  var n = SIR.n, d1 = function (v) { return SIR.d(v, 1); }, lk = function (x) { return SIR.lk(x, 2); };
  var pct = function (v) { return SIR.pct(v); };
  var OFFICER = 'what the officer wrote down, and nobody checked it';

  // count/base: the lead measure; what: its name; of: what it is out of
  var CFG = {
    tamilnadu: { label: 'Tamil Nadu', faq: 'tn', lead: { count: 'removed', base: 'before', per: 100, what: 'names left off the draft roll', of: 'the roll before the revision', press: false },
      reasons: [['shifted_absent', 'Shifted or absent'], ['dead', 'Dead'], ['multiple', 'Enrolled at more than one place']],
      women: { share: 'fall_jan_women_pct', roll: 'jan2025_women_pct', what: 'the fall from the final roll of January 2025 to the draft', of: 'the January 2025 roll' },
      after: { draft: 'draft', final: 'final' },
      election: { year: 2026, count: 'removed', voters: 'removed_voters', votersWhat: 'living names left off, at the seat\'s turnout', turnout: 'turnout', prev: 'winner_2021' },
      limits: 'The Chief Electoral Officer published the names left off by reason for every constituency, and no split of them by sex or age.' },
    westbengal: { label: 'West Bengal', faq: 'wb', lead: { count: 'fall_draft', base: 'roll_2024', per: 100, what: 'fall in the roll from the 2024 Lok Sabha roll to the draft', of: 'the 2024 roll' },
      second: { count: 'fall', base: 'roll_2024', what: 'fall to the roll the 2026 election was held on' },
      women: { count: 'women_fall', of: 'fall', roll: 'women_2024_pct', what: 'the fall from the 2024 roll to the election roll' },
      election: { year: 2026, count: 'fall', voters: 'fall_voters', votersWhat: 'fall in the roll, at the seat\'s turnout', turnout: 'turnout' },
      limits: 'West Bengal published its removals for the state only, so every constituency figure is the fall in the roll, which takes in 18 months of ordinary deaths, moves and new names as well. It is a different count from the names removed.' },
    kerala: { label: 'Kerala', faq: 'kl', lead: { count: 'fall_draft', base: 'roll_2025', per: 100, what: 'fall in the roll from the January 2025 roll to the draft', of: 'the January 2025 roll' },
      second: { count: 'fall', base: 'roll_2025', what: 'fall to the roll the 2026 election was held on' },
      women: { share: 'women_fall_pct', roll: 'women_2025_pct', what: 'the fall from the January 2025 roll to the draft' },
      election: { year: 2026, count: 'fall', voters: 'fall_voters', votersWhat: 'fall in the roll, at the seat\'s turnout', turnout: 'turnout' },
      limits: 'No table of the names left off has been published for Kerala, even for the state, so every constituency figure is the fall in the roll, which also takes in ordinary deaths, moves and new names. It is a different count from the names removed.' },
    delhi: { label: 'Delhi', faq: 'dl', lead: { count: 'left_off', base: 'roll_before', per: 100, what: 'names left off the draft roll (forms not collected)', of: 'the roll before the revision' },
      election: { year: 2025, count: 'left_off', turnout: 'turnout_2025', overTurnout: 'at_turnout_over_margin' },
      limits: 'The reasons and the split by sex were published for Delhi as a whole only. The final roll is still to come.' },
    uttarakhand: { label: 'Uttarakhand', faq: 'uk', lead: { count: 'left_off', base: 'roll_before', per: 100, what: 'names left off the draft roll', of: 'the roll before the revision' },
      notices: { count: 'notices', base: 'draft' },
      claims: { added: 'claims', removed: 'objections', draft: 'draft', final: 'final', womenRemoved: 'women_objections_pct', womenDraft: 'women_draft_pct' },
      limits: 'The reasons for leaving a name off, and the split by sex of the names left off, were published for Uttarakhand as a whole only.' },
    gujarat: { label: 'Gujarat', faq: 'gj', lead: { count: 'removed', base: 'before', per: 100, what: 'names left off the draft roll', of: 'the roll before the revision' },
      map: { winner: 'winner_party', runner_up: 'runner_up_party' },
      reasons: [['shifted', 'Shifted for good'], ['dead', 'Dead'], ['absent', 'Untraceable or absent'], ['enrolled_elsewhere', 'Already enrolled elsewhere'], ['other', 'Other']],
      election: { year: 2022, count: 'removed', voters: 'at_turnout', votersWhat: 'names not entered as dead, at the seat\'s 2022 turnout', turnout: 'turnout_2022' },
      limits: 'The tables are the Chief Electoral Officer\'s as published in the press. Nothing is split by sex or age, and the final roll is by district only.' },
    rajasthan: { label: 'Rajasthan', faq: 'rj', lead: { count: 'fall', base: 'roll_2023', per: 100, what: 'fall in the roll from the 2023 election roll to the final roll', of: 'the 2023 roll', to: 'the final roll' },
      election: { year: 2023, count: 'fall', voters: 'fall_voters', votersWhat: 'fall in the roll, at the seat\'s turnout', turnout: 'turnout' },
      press: true,
      limits: 'The Chief Electoral Officer published the names left off for the state only, so the main constituency figure is the change in the roll over more than two years, which takes in ordinary deaths, moves and new voters. It is a different count from the names left off. A seat whose roll grew shows a negative fall. For 110 constituencies the District Election Officers\' counts of the names left off were printed by Dainik Bhaskar or Amar Ujala, and where they were, this page gives them as press figures.' },
    bihar: { label: 'Bihar', faq: 'bihar', lead: { count: 'total', base: 'electorate_2025', per: 100, what: 'names removed in both phases', of: 'the 2025 election roll', say: 'names were removed in the two phases of the revision', short: 'names removed' },
      map: { winner: 'win2025', runner_up: 'ru2025', margin: 'margin2025' },
      reasons: [['r_shifted', 'Shifted'], ['r_dead', 'Dead'], ['r_absent', 'Absent'], ['r_enrolled', 'Already enrolled']], reasonsOf: 'p1', reasonsWhat: 'the first phase',
      election: { year: 2025, count: 'total', turnout: 'turnout2025', prev: 'win2020', prevYear: 2020 },
      booths: true,
      limits: 'Reasons are counted for the first phase only, from the lists. Every rate is per 100 on the 2025 election roll.' }
  };

  function sum(rows, k) { return rows.reduce(function (t, r) { return t + (r[k] || 0); }, 0); }
  function rate(rows, c) { return c.per * sum(rows, c.count) / sum(rows, c.base); }

  SIR.seatPage = function () {
    var st = document.body.getAttribute('data-seat-state'), no = +document.body.getAttribute('data-seat-ac'), C = CFG[st];
    var root = document.body.getAttribute('data-root') || '';
    return SIR.json('data/' + st + '/constituencies.json').then(function (A) {
      var a = A.filter(function (r) { return r.ac === no; })[0];
      if (!a || !C) throw new Error('no constituency ' + no + ' in ' + st);
      // a state's own field names for the winner, runner-up and margin
      if (C.map) A.forEach(function (r) { Object.keys(C.map).forEach(function (k) { r[k] = r[C.map[k]]; }); });
      var L = C.lead, D = A.filter(function (r) { return r.district === a.district; });
      var seatR = L.per * a[L.count] / a[L.base], distR = rate(D, L), stR = rate(A, L);
      var ranked = A.slice().sort(function (x, y) { return y[L.count] / y[L.base] - x[L.count] / x[L.base]; });
      var rank = ranked.indexOf(a) + 1, drank = D.slice().sort(function (x, y) { return y[L.count] / y[L.base] - x[L.count] / x[L.base]; }).indexOf(a) + 1;
      var stPage = root + st + '/';
      var cmp = function (v, ref) { return v > ref ? 'above' : v < ref ? 'below' : 'the same as'; };
      var falls = L.what.indexOf('fall') === 0;

      document.querySelector('.page-head h1').textContent = a.name + ' (' + a.ac + ')';
      document.title = a.name + ' (' + a.ac + '), ' + C.label + ' | ' + document.title.split('|').pop().trim();
      var head = document.getElementById('seatSub');
      head.innerHTML = 'Assembly constituency ' + a.ac + ' of ' + A.length + ' in ' + C.label + ', in ' + SIR.esc(a.district) + ' district. Measured by the ' + L.what + ', per ' + L.per + ' on ' + L.of + '.';

      var pts = [];
      pts.push('In ' + SIR.esc(a.name) + ' ' + (falls ? 'the roll fell by ' + n(a[L.count]) + ' from ' + L.of + ' to ' + (L.to || 'the draft') : n(a[L.count]) + ' ' + (L.say || 'names were left off the draft roll')) + ', ' + d1(seatR) + ' of every ' + L.per + ' on ' + L.of + '.');
      pts.push('That is ' + cmp(seatR, distR) + ' ' + SIR.esc(a.district) + ' district (' + d1(distR) + ') and ' + cmp(seatR, stR) + ' ' + C.label + ' (' + d1(stR) + '). It ranks ' + rank + ' of ' + A.length + ' in the state, where 1 ' + (falls ? 'fell' : 'lost') + ' the most, and ' + drank + ' of ' + D.length + ' in its district.');
      if (C.reasons) {
        var top = C.reasons.slice().sort(function (x, y) { return a[y[0]] - a[x[0]]; })[0];
        var RO = C.reasonsOf || L.count;
        pts.push(pct(100 * a[top[0]] / a[RO]) + ' of the names ' + (C.reasonsWhat ? 'removed in ' + C.reasonsWhat : 'left off') + ' were entered as ' + top[1].toLowerCase() + '. A reason is ' + OFFICER + '.');
      }
      if (C.notices) pts.push(n(a.notices) + ' electors on its draft, ' + d1(100 * a.notices / a.draft) + ' of every 100, were in line for a notice to prove their entry, against ' + d1(100 * sum(A, 'notices') / sum(A, 'draft')) + ' in the state.');
      if (C.election) {
        var E = C.election;
        var big = a[E.count] > a.margin, what = falls ? 'The fall in the roll' : 'The ' + (L.short || 'names left off');
        pts.push('The ' + E.year + ' winner was ' + SIR.esc(a.winner) + ', by ' + n(a.margin) + ' votes over ' + SIR.esc(a.runner_up) + '. ' + what + (big
          ? (falls ? ' is larger than that margin' : ' outnumber that margin') + ', large enough to decide the seat, which says nothing about whether it did.'
          : falls ? ' is smaller than that margin. The names removed may be more than the fall, because the fall nets out names added.'
            : ' are fewer than that margin, so the runner-up could not have won even if every one of them had voted for the runner-up.'));
      }
      if (C.claims) pts.push('After the draft, ' + n(a.claims) + ' names were added and ' + n(a.objections) + ' removed, and women were ' + pct(a.women_objections_pct) + ' of those removed against ' + pct(a.women_draft_pct) + ' of the draft.');
      var Pr = C.press && a.press;
      if (Pr) pts.splice(2, 0, 'By the District Election Officer\'s figures as ' + Pr.outlet + ' printed them, ' + n(Pr.left_off) + ' names were left off its draft' + (Pr.per_100 != null ? ', ' + d1(Pr.per_100) + ' of every 100 on the roll before the revision' : '') + '. ' + (Pr.left_off > a.margin ? 'That is more than the 2023 winning margin of ' + n(a.margin) + ', large enough to decide the seat, which says nothing about whether it would have.' : 'That is fewer than the 2023 winning margin of ' + n(a.margin) + '.'));
      SIR.inShort(pts, C.limits);
      if (Pr) {
        var PD = A.filter(function (r) { return r.district === a.district && r.press && r.press.per_100 != null; }), PS = A.filter(function (r) { return r.press && r.press.per_100 != null; });
        var pRate = function (rows) { return 100 * sum(rows.map(function (r) { return r.press; }), 'left_off') / sum(rows.map(function (r) { return r.press; }), 'roll_before'); };
        document.getElementById('sPress').hidden = false;
        if (Pr.per_100 != null) {
          var prow = [[a.name, Pr.per_100, '--fill-red']];
          if (PD.length > 1) prow.push(['The ' + PD.length + ' seats of ' + a.district + ' printed', pRate(PD), '--fill-navy']);
          prow.push(['All ' + PS.length + ' seats printed in ' + C.label, pRate(PS), '--fill-grey']);
          VIZ.lollipop('vPress', { label: a.name + ': names left off the draft per 100 on the roll before, as the press printed them', axis: 'Per 100',
            rows: prow.map(function (r) { return { name: r[0], v: r[1], text: d1(r[1]), tok: r[2], hi: true }; }) });
        } else document.getElementById('vPress').parentNode.parentNode.hidden = true;
        var PRS = [['dead', 'as dead'], ['shifted', 'as shifted for good'], ['absent', 'as absent'], ['duplicate', 'as enrolled at more than one place'], ['other', 'under another reason']];
        document.getElementById('fPress').innerHTML = '<b>' + n(Pr.left_off) + ' names were left off ' + SIR.esc(a.name) + '\'s draft roll.</b> ' +
          (Pr.dead != null ? 'Of these, ' + PRS.map(function (r, i) { return n(Pr[r[0]]) + (i ? ' ' : ' were entered ') + r[1]; }).join(', ').replace(/, ([^,]*)$/, ' and $1') + '. A reason is ' + OFFICER + '. ' : '') +
          (Pr.after_per_100 != null ? 'From the draft to the final roll its roll ' + (Pr.after_per_100 >= 0 ? 'grew by ' + d1(Pr.after_per_100) : 'fell by ' + d1(-Pr.after_per_100)) + ' per 100, a net change that counts new voters too. ' : '') +
          'These are the District Election Officer\'s figures as ' + Pr.outlet + ' printed them on 16 or 17 December 2025. The Chief Electoral Officer has published no such table.' + (Pr.clean ? '' : ' This row does not add up as printed. It is kept as printed, and the method page lists the slips in the printed tables.');
      }

      // the seat against its district and state
      VIZ.lollipop('vCompare', { label: a.name + ': ' + L.what + ' per ' + L.per + ', against its district and the state', axis: 'Per ' + L.per,
        rows: [[a.name, seatR, '--fill-red'], [a.district + ' district', distR, '--fill-navy'], [C.label, stR, '--fill-grey']].map(function (r) { return { name: r[0], v: r[1], text: d1(r[1]), tok: r[2], hi: true }; }) });
      document.getElementById('fCompare').innerHTML = '<b>' + SIR.esc(a.name) + ' ' + (falls ? 'fell by ' : 'lost ') + d1(seatR) + ' of every ' + L.per + ', against ' + d1(distR) + ' in its district and ' + d1(stR) + ' in the state.</b> ' + C.label + '\'s constituencies run from ' + d1(L.per * ranked[ranked.length - 1][L.count] / ranked[ranked.length - 1][L.base]) + ' in ' + SIR.esc(ranked[ranked.length - 1].name) + ' to ' + d1(L.per * ranked[0][L.count] / ranked[0][L.base]) + ' in ' + SIR.esc(ranked[0].name) + '.';

      // the district's seats
      var DS = D.slice().sort(function (x, y) { return y[L.count] / y[L.base] - x[L.count] / x[L.base]; });
      VIZ.lollipop('vDistrict', { label: 'Every constituency of ' + a.district + ' district, ' + L.what + ' per ' + L.per, axis: 'Per ' + L.per,
        rows: DS.map(function (r) { var v = L.per * r[L.count] / r[L.base]; return { name: r.name, v: Math.max(v, 0), text: d1(v), tok: r === a ? '--fill-red' : '--fill-navy', hi: r === a }; }) });
      document.getElementById('dLinks').innerHTML = '<p class="note">Open another constituency of ' + SIR.esc(a.district) + ' district:</p><p class="golist">' +
        DS.filter(function (r) { return r !== a; }).map(function (r) { return '<a class="chip" href="../' + r.ac + '/">' + SIR.esc(r.name) + '</a>'; }).join(' ') + '</p>';

      // what each state published beyond the lead count
      var more = [];
      if (C.reasons) {
        VIZ.lollipop('vReasons', { label: a.name + ': names left off by the reason entered', axis: 'Names',
          rows: C.reasons.map(function (r) { return { name: r[1], v: a[r[0]], text: n(a[r[0]]) + ' (' + pct(100 * a[r[0]] / a[C.reasonsOf || L.count]) + ')', tok: '--fill-navy', hi: true }; }) });
        document.getElementById('fReasons').innerHTML = (C.reasonsWhat ? 'Reasons were recorded for ' + C.reasonsWhat + '. ' : '') + 'Each name carries one reason. A reason is ' + OFFICER + '. In the state as a whole the shares were ' + C.reasons.map(function (r) { return pct(100 * sum(A, r[0]) / sum(A, C.reasonsOf || L.count)) + ' ' + r[1].toLowerCase(); }).join(', ').replace(/, ([^,]*)$/, ' and $1') + '.';
      } else document.getElementById('sReasons').hidden = true;

      var W = C.women;
      if (W) {
        var ws = W.share ? a[W.share] : (a[W.of] > 0 ? 100 * a[W.count] / a[W.of] : null);
        if (ws != null) {
          VIZ.lollipop('vWomen', { label: a.name + ': women\'s share of ' + W.of + ' and of ' + W.what, axis: 'Per cent', max: 100, step: 20, ref: 50,
            rows: [['Women, share of ' + (W.of || 'the roll'), a[W.roll], '--fill-grey'], ['Women, share of the fall', ws, '--fill-red']].map(function (r) { return { name: r[0], v: r[1], text: pct(r[1]), tok: r[2], hi: true }; }) });
          document.getElementById('fWomen').innerHTML = '<b>Women were ' + pct(ws) + ' of ' + W.what + ' in ' + SIR.esc(a.name) + ', against ' + pct(a[W.roll]) + ' of the roll.</b> The fall counts ordinary changes too, so it is not the names removed, and it cannot say why anyone left the roll.';
        } else document.getElementById('sWomen').hidden = true;
      } else if (C.claims) {
        VIZ.lollipop('vWomen', { label: a.name + ': women\'s share of the draft and of the names removed after it', axis: 'Per cent', max: 100, step: 20, ref: 50,
          rows: [['Women, share of the draft', a.women_draft_pct, '--fill-grey'], ['Women, share of those removed after the draft', a.women_objections_pct, '--fill-red']].map(function (r) { return { name: r[0], v: r[1] || 0, text: r[1] == null ? 'none' : pct(r[1]), tok: r[2], hi: true }; }) });
        document.getElementById('fWomen').innerHTML = 'The Chief Electoral Officer\'s table of the final roll counts the names removed after the draft by sex, and gives no reason for any of them.';
      } else document.getElementById('sWomen').hidden = true;

      var E2 = C.election;
      if (E2) {
        var rows = [['Winning margin, ' + E2.year, a.margin, '--fill-navy'], [falls ? 'Fall in the roll' : (L.short || 'names left off').replace(/^./, function (c) { return c.toUpperCase(); }), a[E2.count], '--fill-red']];
        if (E2.voters && a[E2.voters] != null) rows.push([E2.votersWhat.charAt(0).toUpperCase() + E2.votersWhat.slice(1), a[E2.voters], '--fill-red']);
        VIZ.lollipop('vElection', { label: a.name + ': the ' + E2.year + ' winning margin against the ' + (falls ? 'fall in the roll' : (L.short || 'names left off')), axis: 'Votes or names',
          rows: rows.map(function (r) { return { name: r[0], v: Math.max(r[1], 0), text: n(r[1]), tok: r[2], hi: true }; }) });
        var over = A.filter(function (r) { return r[E2.count] > r.margin; }).length;
        document.getElementById('fElection').innerHTML = '<b>' + SIR.esc(a.winner) + ' won ' + SIR.esc(a.name) + ' in ' + E2.year + ' by ' + n(a.margin) + ' votes' + (E2.turnout && a[E2.turnout] ? ', on a turnout of ' + d1(a[E2.turnout]) + ' per cent' : '') + '.</b> ' +
          (E2.prev && a[E2.prev] ? 'In ' + (E2.prevYear || 2021) + ' the seat was won by ' + SIR.esc(a[E2.prev]) + '. ' : '') +
          'Across ' + C.label + ', the ' + (falls ? 'fall in the roll is larger than' : (L.short || 'names left off') + ' outnumber') + ' the margin in ' + over + ' of ' + A.length + ' seats. Larger than the margin means large enough to decide a seat, never that it did, and the lists cannot show how anyone left off would have voted.';
      } else document.getElementById('sElection').hidden = true;

      if (C.claims) {
        VIZ.lollipop('vAfter', { label: a.name + ': names added and removed after the draft', axis: 'Names',
          rows: [['Added after the draft', a.claims, '--fill-teal'], ['Removed after the draft', a.objections, '--fill-red']].map(function (r) { return { name: r[0], v: r[1], text: n(r[1]), tok: r[2], hi: true }; }) });
        document.getElementById('fAfter').innerHTML = 'The final roll holds ' + n(a.final) + ', ' + (a.final >= a.draft ? n(a.final - a.draft) + ' more' : n(a.draft - a.final) + ' fewer') + ' than the draft. The names added include people enrolling for the first time, so they say little about names put back.';
      } else if (C.after) {
        VIZ.lollipop('vAfter', { label: a.name + ': the draft and the final roll', axis: 'Electors',
          rows: [['Roll before the revision', a[L.base], '--fill-navy'], ['Draft roll', a.draft, '--fill-red'], ['Final roll', a.final, '--fill-navy']].map(function (r) { return { name: r[0], v: r[1], text: n(r[1]), tok: r[2], hi: true }; }) });
        document.getElementById('fAfter').innerHTML = 'The final roll is ' + n(a.final - a.draft) + ' larger than the draft. That rise counts people enrolling for the first time as well as names put back, so it is the most that could have been put back.';
      } else document.getElementById('sAfter').hidden = true;

      var CASE = { 'uttarakhand-67': 'kichha', 'delhi-52': 'tughlakabad', 'gujarat-54': 'danilimda' }[st + '-' + a.ac];
      document.getElementById('seatLinks').innerHTML = (CASE ? '<a class="btn" href="' + root + 'india/cases/#' + CASE + '">A case study of this constituency</a> ' : '') + (C.booths ? '<a class="btn" href="' + stPage + 'explorer/#ac' + ('00' + a.ac).slice(-3) + '">Its polling booths</a> ' : '') + '<a class="btn" href="' + stPage + (st === 'bihar' ? 'results/' : '') + '#ac-' + a.ac + '">' + C.label + ', with this constituency on the map</a> <a class="btn" href="' + stPage + 'method/">Sources and method</a> <a class="btn" href="' + root + 'india/constituencies/">Find another constituency</a>';
      document.getElementById('pageFaq').innerHTML = '<div class="qa"><h3>Where do these figures come from?</h3><p>From the same tables as the <a href="' + stPage + '">' + C.label + '</a> pages, which give every source on their method page. Every figure here is worked out from them when the page loads.</p></div>' +
        '<div class="qa"><h3>Can this page say who was left off, or why?</h3><p>No. The site publishes counts only, never a name. ' + (C.reasons ? 'A reason on the list is ' + OFFICER + '. ' : '') + 'Nothing here says whether any person should have been on the roll.</p></div>';
      SIR.tools();
    }).catch(SIR.fail);
  };
})();
