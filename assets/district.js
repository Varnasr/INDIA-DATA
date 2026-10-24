/* One page per district, in every state whose figures were published by
   district, each in that state's own measure. Like the constituency
   pages (assets/seat.js), the page's source holds only its state and the
   district's slug, and everything is drawn from the published JSON when the
   page loads: the district's own districts.json row, and its NFHS-5
   circumstances from data/india/factors.json, read against the state's
   other districts. A circumstance is set beside the names lost, never named
   as their cause. English only. */
(function () {
  var n = SIR.n, d1 = function (v) { return SIR.d(v, 1); }, pct = function (v) { return SIR.pct(v); };
  var OFFICER = 'what the officer wrote down, and nobody checked it';
  var CFG = {
    uttarpradesh: { label: 'Uttar Pradesh', state: 'Uttar Pradesh', count: 'total', base: 'roll_before',
      reasons: [['shifted', 'Shifted for good'], ['untraceable_absent', 'Untraceable or absent'], ['dead', 'Dead'], ['multiple', 'Enrolled more than once'], ['others', 'Other']],
      limits: 'The district table is the Chief Electoral Officer\'s, as published in the press. No split by sex of the names left off was published below the state, and no table by constituency.' },
    maharashtra: { label: 'Maharashtra', state: 'Maharashtra', count: 'left_off', base: 'before',
      reasons: [['shifted', 'Shifted for good'], ['absent', 'Untraceable or absent'], ['dead', 'Dead'], ['duplicate', 'Enrolled at another place'], ['other', 'Other']],
      womenDraft: 'women_draft_pct', seats: true,
      limits: 'The Chief Electoral Officer published no split of the names left off by sex. The final roll is still to come.' },
    karnataka: { label: 'Karnataka', state: 'Karnataka', count: 'removed', base: 'before',
      reasons: [['shifted', 'Shifted'], ['absent', 'Absent'], ['dead', 'Dead'], ['duplicate', 'Enrolled more than once'], ['other', 'Other']],
      after: { draft: 'draft', later: 'sep', what: 'the roll of 9 October 2026' },
      limits: 'Karnataka published its revision by its 34 election districts and none of it by constituency, and no split of the names left off by sex.' },
    bihar: { label: 'Bihar', state: 'Bihar', count: 'deleted', base: function (x) { return 100 * x.deleted / x.per_100; }, seats: true, page: 'bihar/districts/', anchor: false,
      sub: 'Measured by the names left off the draft or deleted after it in the two phases of the revision, per 100 electors on the 2025 roll.',
      noun: 'names left off or deleted', verb: 'were left off the draft or deleted after it in the two phases of the revision', per: 'per 100 electors on the 2025 roll', identity: true,
      limits: 'The reasons were published for phase 1 only, and phase 2 carries none. Women\'s share is of the phase 1 list.' },
    tamilnadu: { label: 'Tamil Nadu', state: 'Tamil Nadu', count: 'removed', base: 'before', seats: true,
      reasons: [['shifted_absent', 'Shifted or absent'], ['dead', 'Dead'], ['multiple', 'Enrolled more than once']],
      after: { draft: function (x) { return x.before - x.removed; }, later: 'final', what: 'the final roll' },
      limits: 'The Chief Electoral Officer has published no split of the names left off by sex or age. A seat\'s roll before is its draft plus its names left off.' },
    westbengal: { label: 'West Bengal', state: 'West Bengal', count: function (x) { return x.roll_2024 - x.draft; }, base: 'roll_2024', seats: true, fall: true,
      second: { count: function (x) { return x.roll_2024 - x.election; }, what: 'from the 2024 roll to the roll the 2026 election was held on' },
      sub: 'Measured by the fall in the roll from the 2024 Lok Sabha roll to the draft, per 100 on the 2024 roll. The fall takes in 18 months of ordinary deaths, moves and new voters, so it is a different count from the names left off the draft.',
      noun: 'fall in the roll', verb: 'is the fall in the roll from the 2024 Lok Sabha roll to the draft', per: 'per 100 on the 2024 roll',
      women: function (d, nm) { return 'Women were ' + pct(d.women_fall_pct) + ' of the fall in ' + nm + '\'s roll from 2024 to the roll at the 2026 nominations, against ' + pct(d.women_2024_pct) + ' of the 2024 roll.'; },
      limits: 'The Chief Electoral Officer published the names left off the draft for the state only. Below the state this is the fall in the roll, which also takes in ordinary changes.' },
    kerala: { label: 'Kerala', state: 'Kerala', count: function (x) { return x.roll_2025 - x.draft; }, base: 'roll_2025', seats: true, fall: true,
      second: { count: function (x) { return x.roll_2025 - x.election; }, what: 'from the January 2025 roll to the roll the 2026 election was held on' },
      sub: 'Measured by the fall in the roll from the final roll of January 2025 to the draft, per 100 on the January 2025 roll. No table of the names left off has been published, even for the state.',
      noun: 'fall in the roll', verb: 'is the fall in the roll from January 2025 to the draft', per: 'per 100 on the January 2025 roll',
      women: function (d, nm) { return 'Women were ' + pct(d.women_fall_pct) + ' of the fall in ' + nm + '\'s roll, against ' + pct(d.women_2025_pct) + ' of the January 2025 roll.'; },
      after: { draft: 'draft', later: 'final', what: 'the final roll' },
      limits: 'No table of the names left off has been published. The fall in the roll also takes in ordinary changes over ten months.' },
    delhi: { label: 'Delhi', state: 'Delhi', count: 'left_off', base: 'roll_before', seats: true,
      limits: 'The reasons and the split by sex were published for Delhi as a whole only.' },
    gujarat: { label: 'Gujarat', state: 'Gujarat', count: 'removed', base: 'before', seats: true,
      reasons: [['shifted', 'Shifted'], ['dead', 'Dead'], ['absent', 'Absent'], ['enrolled_elsewhere', 'Enrolled elsewhere'], ['other', 'Other']],
      claims: function (d, nm) { return 'After the draft, ' + n(d.added) + ' names were added in ' + nm + ' and ' + n(d.deleted) + ' deleted, and the final roll is ' + n(d.final) + '. The additions count new voters too, so they are the most that could have been restored.'; },
      limits: 'The tables are the Chief Electoral Officer\'s, as published in the press. No split by sex or age was published.' },
    rajasthan: { label: 'Rajasthan', state: 'Rajasthan', count: 'fall', base: 'roll_2023', seats: true, fall: true,
      sub: 'Measured by the change in the roll of general electors from the 2023 election roll to the final roll of 12 March 2026, per 100 on the 2023 roll. It spans more than two years of new voters, deaths and moves, so it is a different count from the names left off.',
      noun: 'fall in the roll', verb: 'is the fall in the roll from the 2023 election roll to the final roll of March 2026', per: 'per 100 on the 2023 roll',
      women: function (d, nm) { return 'Women were ' + pct(d.women_2023_pct) + ' of ' + nm + '\'s roll in 2023 and ' + pct(d.women_2026_pct) + ' of its final roll in 2026.'; },
      limits: 'The names left off were published for the state only. Below the state this is the change in the roll over more than two years.' },
    assam: { label: 'Assam', state: 'Assam', count: 'fall', base: 'draft', seats: true, fall: true, per: 'per 100 on the draft',
      sub: 'Measured by the fall in the roll from the draft to the final roll of the Special Revision, per 100 on the draft. It is the net fall, names deleted less names added, and the tables do not give the two apart.',
      noun: 'fall in the roll', verb: 'is the fall in the roll from the draft to the final roll',
      women: function (d, nm) { return d.women_fall_pct == null ? 'Women were ' + pct(d.draft_women_pct) + ' of ' + nm + '\'s draft roll. Its roll rose after the draft, so there is no fall to divide by sex.' : 'Women were ' + pct(d.women_fall_pct) + ' of the fall in ' + nm + '\'s roll after the draft, against ' + pct(d.draft_women_pct) + ' of its draft roll.'; },
      limits: 'Assam held a Special Revision, which ran on different rules from the SIR. The names flagged for deletion were published for the state only, through the press.' },
    meghalaya: { label: 'Meghalaya', state: 'Meghalaya', count: 'removed', base: 'before', seats: true,
      reasons: [['shifted_absent_other', 'Shifted, absent or other'], ['dead', 'Dead'], ['duplicate', 'Enrolled more than once']],
      limits: 'The split by sex of the names left off was published for the state only.' },
    manipur: { label: 'Manipur', state: 'Manipur', count: 'fall', base: 'before', seats: true, fall: true,
      sub: 'Measured by the fall in the roll from the roll before the revision to the final roll, per 100 on the roll before. It takes in the names left off and everything added or deleted after the draft together.',
      noun: 'fall in the roll', verb: 'is the fall in the roll from the roll before the revision to the final roll', per: 'per 100 on the roll before the revision',
      women: function (d, nm) { return 'Women are ' + pct(100 * d.women / d.final) + ' of ' + nm + '\'s final roll. The names left off were split by sex for the state only.'; },
      limits: 'The reasons and the split by sex of the names left off were published for the state only.' },
    odisha: { label: 'Odisha', state: 'Odisha', count: function (x) { return x.before - x.draft; }, base: 'before', seats: true, fall: true,
      sub: 'Measured by the fall in the roll from the final roll of January 2025 to the draft, per 100 on the January 2025 roll. The revision started from the roll of 17 May 2026, so the fall takes in more than a year of ordinary changes as well as the names left off.',
      noun: 'fall in the roll', verb: 'is the fall in the roll from January 2025 to the draft', per: 'per 100 on the January 2025 roll',
      claims: function (d, nm) { return 'After the draft, ' + n(d.added) + ' names were added in ' + nm + ' and ' + n(d.removed) + ' deleted, and the final roll is ' + n(d.final) + '. The additions count new voters too, so they are the most that could have been restored.'; },
      limits: 'The names left off the draft were published by district and for the state, and the reasons for the state only.' },
    andhrapradesh: { label: 'Andhra Pradesh', state: 'Andhra Pradesh', count: 'removed', base: 'before', womenDraft: 'draft_women_pct',
      limits: 'Andhra Pradesh published the names left off by district, with no reasons and no split by sex below the state.' },
    chhattisgarh: { label: 'Chhattisgarh', state: 'Chhattisgarh', count: function (x) { return x.final - x.draft; }, base: 'draft', fall: true, rise: true, per: 'per 100 on the draft',
      sub: 'Measured by the rise in the roll from the draft to the final roll, per 100 on the draft. It is the net change, names added less names deleted, and a district whose roll shrank shows a fall. The names left off the draft were published for the state only.',
      noun: 'rise in the roll', verb: 'is the rise in the roll from the draft to the final roll',
      claims: function (d, nm) { return 'After the draft, ' + n(d.added) + ' names were added in ' + nm + ' and ' + n(d.removed) + ' deleted, and the final roll is ' + n(d.final) + '. The additions count new voters too, so they are the most that could have been restored.'; },
      limits: 'The names left off the draft, and their reasons, were published for the state only.' },
    mizoram: { label: 'Mizoram', state: 'Mizoram', count: function (x) { return x.final - x.draft; }, base: 'draft', fall: true, rise: true, per: 'per 100 on the draft',
      sub: 'Measured by the rise in the roll from the draft to the final roll, per 100 on the draft. It is the net change, names added less names deleted, and a district whose roll shrank shows a fall. The names left off the draft were published for the state only.',
      noun: 'rise in the roll', verb: 'is the rise in the roll from the draft to the final roll',
      women: function (d, nm) { return 'Women are ' + pct(100 * d.women / d.final) + ' of ' + nm + '\'s final roll.'; },
      limits: 'The names left off the draft, and their reasons, were published for the state only.' },
    telangana: { label: 'Telangana', state: 'Telangana', file: 'hyderabad/telangana.json', rows: 'districts', count: 'removed', base: 'electors_pre', page: 'hyderabad/telangana/', anchor: false, method: 'hyderabad/method/',
      limits: 'Telangana\'s draft-roll totals are published by district and for Hyderabad\'s fifteen constituencies. The reasons and the split by sex are not.' },
    uttarakhand: { label: 'Uttarakhand', state: 'Uttarakhand', count: 'left_off', base: 'roll_before', seats: true,
      women: function (d, nm) { return 'Women were ' + pct(d.women_draft_pct) + ' of ' + nm + '\'s draft roll, ' + pct(d.women_claims_pct) + ' of the claims admitted after it and ' + pct(d.women_objections_pct) + ' of the names deleted after it.'; },
      claims: function (d, nm) { return 'After the draft, ' + nm + ' admitted ' + n(d.claims) + ' claims (' + d1(d.claims_per_1000) + ' per 1,000 on the draft) and ' + n(d.objections) + ' objections (' + d1(d.objections_per_1000) + ' per 1,000). ' + n(d.notices) + ' electors were sent a notice, ' + d1(d.notices_per_100) + ' per 100 on the draft.'; },
      limits: 'The reasons were published for the state only.' }
  };
  var val = function (x, f) { return typeof f === 'function' ? f(x) : x[f]; };
  var slug = function (s) { return SIR.slug(s).slice(2); };
  var median = function (v) { v = v.slice().sort(function (a, b) { return a - b; }); var m = v.length >> 1; return v.length % 2 ? v[m] : (v[m - 1] + v[m]) / 2; };

  SIR.districtPage = function () {
    var st = document.body.getAttribute('data-district-state'), key = document.body.getAttribute('data-district'), C = CFG[st];
    var root = document.body.getAttribute('data-root') || '';
    return Promise.all([SIR.json('data/' + (C.file || st + '/districts.json')), SIR.json('data/india/factors.json')]).then(function (r) {
      var D = C.rows ? r[0][C.rows] : r[0], F = r[1], d = D.filter(function (x) { return slug(x.district) === key; })[0];
      if (!d) throw new Error('no district ' + key + ' in ' + st);
      var rate = function (x) { return 100 * val(x, C.count) / val(x, C.base); };
      var all = D.slice().sort(function (a, b) { return rate(b) - rate(a); });
      var rk = all.indexOf(d) + 1, stR = 100 * D.reduce(function (t, x) { return t + val(x, C.count); }, 0) / D.reduce(function (t, x) { return t + val(x, C.base); }, 0);
      var name = d.district + (d.now ? ' (now ' + d.now + ')' : '');
      document.querySelector('.page-head h1').textContent = name;
      document.title = name + ', ' + C.label + ' | ' + document.title.split('|').pop().trim();
      document.getElementById('dSub').innerHTML = 'One of ' + D.length + ' districts in ' + C.label + '. ' + (C.sub || 'Measured by the names left off the draft roll, per 100 on the roll before the revision.');
      var stPage = root + (C.page || st + '/'), noun = C.noun || 'names left off', per = C.per || 'per 100 on the roll before the revision';

      var span = C.fall ? C.verb.replace(/^is the [^ ]+ in the roll /, '') : '';
      // a fall (or, with rise: true, a rise) can run the other way: say so in words
      var up = C.rise ? 'rose' : 'fell', other = C.rise ? 'fell' : 'grew', otherN = C.rise ? 'fall' : 'rise';
      var sv = function (v) { return v < 0 ? 'a ' + otherN + ' of ' + d1(-v) : d1(v); };
      var first = C.fall && val(d, C.count) < 0 ? 'In ' + SIR.esc(name) + ' the roll ' + other + ' ' + span + ', by ' + n(-val(d, C.count)) + ', a ' + otherN + ' of ' + d1(-rate(d)) + ' ' + per + '. Across ' + C.label + ' the roll ' + (stR >= 0 ? up : other) + ' by ' + d1(Math.abs(stR)) + ' per 100.'
        : C.fall ? 'In ' + SIR.esc(name) + ' the ' + noun + ' ' + span + ' was ' + n(val(d, C.count)) + ', ' + d1(rate(d)) + ' ' + per + ', against ' + sv(stR) + ' in ' + C.label + '.'
        : 'In ' + SIR.esc(name) + ' ' + n(val(d, C.count)) + ' names ' + (C.verb || 'were left off the draft roll') + ', ' + d1(rate(d)) + ' ' + per + ', against ' + d1(stR) + ' in ' + C.label + '.';
      var pts = [first,
        'It ranks ' + rk + ' of ' + D.length + ' districts, where 1 is the highest. ' + C.label + '\'s districts run from ' + sv(rate(all[all.length - 1])) + ' in ' + SIR.esc(all[all.length - 1].district) + ' to ' + sv(rate(all[0])) + ' in ' + SIR.esc(all[0].district) + '.'];
      if (C.second) {
        var S2 = C.second, r2 = function (x) { return 100 * val(x, S2.count) / val(x, C.base); };
        var st2 = 100 * D.reduce(function (t, x) { return t + val(x, S2.count); }, 0) / D.reduce(function (t, x) { return t + val(x, C.base); }, 0);
        pts.splice(1, 0, 'Measured ' + S2.what + ', the roll ' + (val(d, S2.count) < 0 ? 'grew by ' + n(-val(d, S2.count)) + ', a rise of ' + d1(-r2(d)) : 'fell by ' + n(val(d, S2.count)) + ', ' + d1(r2(d))) + ' ' + per + ', against ' + (st2 < 0 ? 'a rise of ' : 'a fall of ') + d1(Math.abs(st2)) + ' in ' + C.label + '. This second count takes in the names added after the draft as well.');
      }
      if (C.reasons) {
        var top = C.reasons.slice().sort(function (x, y) { return d[y[0]] - d[x[0]]; })[0];
        pts.push(pct(100 * d[top[0]] / val(d, C.count)) + ' were entered as ' + top[1].toLowerCase() + '. A reason is ' + OFFICER + '.');
      }
      SIR.inShort(pts, C.limits);

      VIZ.lollipop('vCompare', { label: name + ': ' + noun + ' ' + per + ', against every district of ' + C.label, axis: per.charAt(0).toUpperCase() + per.slice(1),
        rows: all.map(function (x) { return { name: x.district, v: rate(x), text: d1(rate(x)), tok: x === d ? '--fill-red' : '--fill-navy', hi: x === d }; }) });
      document.getElementById('fCompare').innerHTML = C.fall && rate(d) < 0 ? '<b>' + SIR.esc(name) + '\'s roll ' + other + ' by ' + d1(-rate(d)) + ' ' + per + ', while ' + C.label + '\'s roll ' + (stR >= 0 ? up : other) + ' by ' + d1(Math.abs(stR)) + '.</b> It is marked in red among all ' + D.length + ' districts.' : '<b>' + (C.fall ? 'The ' + noun + ' in ' + SIR.esc(name) + ' was ' + sv(rate(d)) + ' ' + per : SIR.esc(name) + ' lost ' + d1(rate(d)) + ' of every 100 names') + ', ' + (rate(d) > stR ? 'above' : 'below') + ' the state\'s ' + (C.fall ? sv(stR) : d1(stR)) + '.</b> It is marked in red among all ' + D.length + ' districts.';

      if (C.reasons) {
        VIZ.lollipop('vReasons', { label: name + ': names left off by the reason entered', axis: 'Names',
          rows: C.reasons.map(function (x) { return { name: x[1], v: d[x[0]], text: n(d[x[0]]) + ' (' + pct(100 * d[x[0]] / val(d, C.count)) + ')', tok: '--fill-navy', hi: true }; }) });
        document.getElementById('fReasons').innerHTML = 'Each name left off carries one reason, and a reason is ' + OFFICER + '. In the state as a whole the shares were ' +
          C.reasons.map(function (x) { var t = D.reduce(function (s, y) { return s + y[x[0]]; }, 0), c = D.reduce(function (s, y) { return s + val(y, C.count); }, 0); return pct(100 * t / c) + ' ' + x[1].toLowerCase(); }).join(', ').replace(/, ([^,]*)$/, ' and $1') + '.';
      } else document.getElementById('sReasons').hidden = true;

      // NFHS-5 circumstances, against the state's other districts
      var U = F.units.filter(function (u) { return u.state === C.state; });
      var u = U.filter(function (x) { return x.districts.map(function (y) { return y.toLowerCase(); }).indexOf(d.district.toLowerCase()) >= 0 || x.unit.toLowerCase() === d.district.toLowerCase(); })[0];
      var S = F.states.filter(function (x) { return x.state === C.state; })[0];
      if (u) {
        var rows = F.factors.filter(function (f) { return f.source === 'nfhs' && u[f.key] != null; }).map(function (f) {
          var v = U.map(function (x) { return x[f.key]; }).filter(function (x) { return x != null; }), sorted = v.slice().sort(function (a, b) { return b - a; });
          var cor = S && S.survey && S.survey[f.key];
          return [f.label, f.key === 'sex_ratio' ? n(u[f.key]) : d1(u[f.key]), f.key === 'sex_ratio' ? n(median(v)) : d1(median(v)), (sorted.indexOf(u[f.key]) + 1) + ' of ' + v.length, cor ? SIR.d(cor.rho, 2) + (cor.clear ? '' : ' (could be chance)') : null];
        });
        SIR.table('tFactors', [{ h: 'NFHS-5, 2019-21' }, { h: SIR.esc(u.unit), num: true }, { h: 'Typical district', num: true }, { h: 'Rank, highest first', num: true }, { h: 'Link with the share left off', num: true }], rows);
        document.getElementById('fFactors').innerHTML = (u.districts.length > 1 ? 'The survey counts ' + SIR.esc(u.unit) + ' as one district, ' + u.districts.map(SIR.esc).join(', ') + '. ' : '') +
          'The last column, the link with the share left off, is the rank correlation, across all of ' + C.label + '\'s districts, between each circumstance and the share of names left off, where 0 means unrelated. Circumstances move together, so none of them can be named as a cause, and a district\'s own figure says nothing about why its names were left off. Sex ratio is women per 1,000 men. The <a href="' + root + 'india/factors/">district factors page</a> has every state.';
      } else document.getElementById('sFactors').hidden = true;

      if (C.identity) SIR.json('data/bihar/identity.json').then(function (I) {
        var w = I.districts.filter(function (x) { return x.district === d.district; })[0];
        if (!w) return;
        document.getElementById('sWomen').hidden = false;
        document.getElementById('fWomen').innerHTML = 'Women were ' + pct(w.female_share_deleted) + ' of ' + SIR.esc(name) + '\'s phase 1 list of names left off the draft, against ' + pct(w.female_share_roll) + ' of its roll before the revision.';
      });
      if (C.women) {
        document.getElementById('fWomen').innerHTML = C.women(d, SIR.esc(name));
      } else if (C.womenDraft) {
        document.getElementById('fWomen').innerHTML = 'Women are ' + pct(d[C.womenDraft]) + ' of ' + SIR.esc(name) + '\'s draft roll. The names left off were not published by sex, so women\'s share of them cannot be counted.';
      } else document.getElementById('sWomen').hidden = true;

      if (C.claims) {
        document.getElementById('fAfter').innerHTML = C.claims(d, SIR.esc(name));
      } else if (C.after) {
        var a0 = val(d, C.after.draft), a1 = val(d, C.after.later);
        document.getElementById('fAfter').innerHTML = 'From the draft to ' + C.after.what + ', ' + SIR.esc(name) + '\'s roll ' + (a1 >= a0 ? 'rose by ' + n(a1 - a0) : 'fell by ' + n(a0 - a1)) + '. The rise counts new voters too, so it is the most that could have been restored.';
      } else document.getElementById('sAfter').hidden = true;

      var CASE = { 'uttarpradesh-lucknow': 'lucknow', 'karnataka-b-b-m-p-south': 'bbmp-south' }[st + '-' + key];
      document.getElementById('dLinks').innerHTML = (CASE ? '<a class="btn" href="' + root + 'india/cases/#' + CASE + '">A case study of this district</a> ' : '') + '<a class="btn" href="' + stPage + (C.anchor === false ? '' : '#d-' + key) + '">' + C.label + (C.anchor === false ? ', every district' : ', with this district on the map') + '</a> <a class="btn" href="' + root + (C.method || st + '/method/') + '">Sources and method</a>';
      document.getElementById('others').innerHTML = all.filter(function (x) { return x !== d; }).map(function (x) { return '<a class="chip" href="../' + slug(x.district) + '/">' + SIR.esc(x.district) + '</a>'; }).join(' ');
      document.getElementById('pageFaq').innerHTML = '<div class="qa"><h3>Where do these figures come from?</h3><p>From the same tables as the <a href="' + stPage + '">' + C.label + '</a> pages, which give every source on their method page, and from the National Family Health Survey 2019-21 for the circumstances.</p></div>' +
        '<div class="qa"><h3>Does a circumstance explain the names a district lost?</h3><p>No. A district\'s schooling, fuel or sanitation figures sit beside its count, and the correlations across districts say which districts lost more, never why.</p></div>';
      if (C.seats) SIR.json('data/' + st + '/constituencies.json').then(function (A) {
        var mine = A.filter(function (a) { return a.district === d.district; }).sort(function (a, b) { return a.ac - b.ac; });
        document.getElementById('dLinks').insertAdjacentHTML('beforeend', '<p class="note">Its ' + mine.length + ' constituencies, each with its own page</p><p class="golist">' +
          mine.map(function (a) { return '<a class="chip" href="' + root + st + '/seat/' + a.ac + '/">' + SIR.esc(a.ac + '. ' + a.name) + '</a>'; }).join(' ') + '</p>');
      });
      SIR.tools();
    }).catch(SIR.fail);
  };
})();
