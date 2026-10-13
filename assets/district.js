/* One page per district, for the states whose revision was published by
   district: Uttar Pradesh, Maharashtra and Karnataka. Like the constituency
   pages (assets/seat.js), the page's source holds only its state and the
   district's slug, and everything is drawn from the published JSON when the
   page loads: the district's own districts.json row, and its NFHS-5
   circumstances from data/india/factors.json, read against the state's
   other districts. A circumstance is set beside the removals, never named
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
      limits: 'Karnataka published its revision by its 34 election districts and none of it by constituency, and no split of the names left off by sex.' }
  };
  var slug = function (s) { return SIR.slug(s).slice(2); };
  var median = function (v) { v = v.slice().sort(function (a, b) { return a - b; }); var m = v.length >> 1; return v.length % 2 ? v[m] : (v[m - 1] + v[m]) / 2; };

  SIR.districtPage = function () {
    var st = document.body.getAttribute('data-district-state'), key = document.body.getAttribute('data-district'), C = CFG[st];
    var root = document.body.getAttribute('data-root') || '';
    return Promise.all([SIR.json('data/' + st + '/districts.json'), SIR.json('data/india/factors.json')]).then(function (r) {
      var D = r[0], F = r[1], d = D.filter(function (x) { return slug(x.district) === key; })[0];
      if (!d) throw new Error('no district ' + key + ' in ' + st);
      var rate = function (x) { return 100 * x[C.count] / x[C.base]; };
      var all = D.slice().sort(function (a, b) { return rate(b) - rate(a); });
      var rk = all.indexOf(d) + 1, stR = 100 * D.reduce(function (t, x) { return t + x[C.count]; }, 0) / D.reduce(function (t, x) { return t + x[C.base]; }, 0);
      var name = d.district + (d.now ? ' (now ' + d.now + ')' : '');
      document.querySelector('.page-head h1').textContent = name;
      document.title = name + ', ' + C.label + ' | ' + document.title.split('|').pop().trim();
      document.getElementById('dSub').innerHTML = 'One of ' + D.length + ' districts in ' + C.label + '. Measured by the names left off the draft roll, per 100 on the roll before the revision.';
      var stPage = root + st + '/';

      var pts = ['In ' + SIR.esc(name) + ' ' + n(d[C.count]) + ' names were left off the draft roll, ' + d1(rate(d)) + ' of every 100 on the roll before the revision, against ' + d1(stR) + ' in ' + C.label + '.',
        'It ranks ' + rk + ' of ' + D.length + ' districts, where 1 lost the most. ' + C.label + '\'s districts run from ' + d1(rate(all[all.length - 1])) + ' in ' + SIR.esc(all[all.length - 1].district) + ' to ' + d1(rate(all[0])) + ' in ' + SIR.esc(all[0].district) + '.'];
      if (C.reasons) {
        var top = C.reasons.slice().sort(function (x, y) { return d[y[0]] - d[x[0]]; })[0];
        pts.push(pct(100 * d[top[0]] / d[C.count]) + ' were entered as ' + top[1].toLowerCase() + '. A reason is ' + OFFICER + '.');
      }
      SIR.inShort(pts, C.limits);

      VIZ.lollipop('vCompare', { label: name + ': names left off per 100, against every district of ' + C.label, axis: 'Per 100 on the roll before',
        rows: all.map(function (x) { return { name: x.district, v: rate(x), text: d1(rate(x)), tok: x === d ? '--fill-red' : '--fill-navy', hi: x === d }; }) });
      document.getElementById('fCompare').innerHTML = '<b>' + SIR.esc(name) + ' lost ' + d1(rate(d)) + ' of every 100 names, ' + (rate(d) > stR ? 'above' : 'below') + ' the state\'s ' + d1(stR) + '.</b> It is marked in red among all ' + D.length + ' districts.';

      if (C.reasons) {
        VIZ.lollipop('vReasons', { label: name + ': names left off by the reason entered', axis: 'Names',
          rows: C.reasons.map(function (x) { return { name: x[1], v: d[x[0]], text: n(d[x[0]]) + ' (' + pct(100 * d[x[0]] / d[C.count]) + ')', tok: '--fill-navy', hi: true }; }) });
        document.getElementById('fReasons').innerHTML = 'Each name left off carries one reason, and a reason is ' + OFFICER + '. In the state as a whole the shares were ' +
          C.reasons.map(function (x) { var t = D.reduce(function (s, y) { return s + y[x[0]]; }, 0), c = D.reduce(function (s, y) { return s + y[C.count]; }, 0); return pct(100 * t / c) + ' ' + x[1].toLowerCase(); }).join(', ').replace(/, ([^,]*)$/, ' and $1') + '.';
      } else document.getElementById('sReasons').hidden = true;

      // NFHS-5 circumstances, against the state's other districts
      var U = F.units.filter(function (u) { return u.state === C.state; });
      var u = U.filter(function (x) { return x.districts.map(function (y) { return y.toLowerCase(); }).indexOf(d.district.toLowerCase()) >= 0 || x.unit.toLowerCase() === d.district.toLowerCase(); })[0];
      var S = F.states.filter(function (x) { return x.state === C.state; })[0];
      if (u) {
        var rows = F.factors.filter(function (f) { return f.source === 'nfhs' && u[f.key] != null; }).map(function (f) {
          var v = U.map(function (x) { return x[f.key]; }).filter(function (x) { return x != null; }), sorted = v.slice().sort(function (a, b) { return b - a; });
          var cor = S && S.survey && S.survey[f.key];
          return '<tr><td>' + f.label + '</td><td class="num">' + (f.key === 'sex_ratio' ? n(u[f.key]) : d1(u[f.key])) + '</td><td class="num">' + (f.key === 'sex_ratio' ? n(median(v)) : d1(median(v))) + '</td><td class="num">' + (sorted.indexOf(u[f.key]) + 1) + ' of ' + v.length + '</td><td class="num">' + (cor ? SIR.d(cor.rho, 2) + (cor.clear ? '' : ' (could be chance)') : '') + '</td></tr>';
        });
        document.getElementById('tFactors').innerHTML = '<thead><tr><th scope="col">NFHS-5, 2019-21</th><th class="num" scope="col">' + SIR.esc(u.unit) + '</th><th class="num" scope="col">Typical district</th><th class="num" scope="col">Rank, highest first</th><th class="num" scope="col">Across the districts, with the share left off</th></tr></thead><tbody>' + rows.join('') + '</tbody>';
        document.getElementById('fFactors').innerHTML = (u.districts.length > 1 ? 'The survey counts ' + SIR.esc(u.unit) + ' as one district, ' + u.districts.map(SIR.esc).join(', ') + '. ' : '') +
          'The last column is the rank correlation, across all of ' + C.label + '\'s districts, between each circumstance and the share of names left off, where 0 means unrelated. Circumstances move together, so none of them can be named as a cause, and a district\'s own figure says nothing about why its names were left off. Sex ratio is women per 1,000 men. The <a href="' + root + 'india/factors/">district factors page</a> has every state.';
      } else document.getElementById('sFactors').hidden = true;

      if (C.womenDraft) {
        document.getElementById('fWomen').innerHTML = 'Women are ' + pct(d[C.womenDraft]) + ' of ' + SIR.esc(name) + '\'s draft roll. The names left off were not published by sex, so women\'s share of them cannot be counted.';
      } else document.getElementById('sWomen').hidden = true;

      if (C.after) {
        document.getElementById('fAfter').innerHTML = 'From the draft to ' + C.after.what + ', ' + SIR.esc(name) + '\'s roll ' + (d[C.after.later] >= d[C.after.draft] ? 'rose by ' + n(d[C.after.later] - d[C.after.draft]) : 'fell by ' + n(d[C.after.draft] - d[C.after.later])) + '. The rise counts new voters too, so it is the most that could have been restored.';
      } else document.getElementById('sAfter').hidden = true;

      document.getElementById('dLinks').innerHTML = '<a class="btn" href="' + stPage + '#d-' + key + '">' + C.label + ', with this district on the map</a> <a class="btn" href="' + stPage + 'method/">Sources and method</a>';
      document.getElementById('others').innerHTML = all.filter(function (x) { return x !== d; }).map(function (x) { return '<a class="chip" href="../' + slug(x.district) + '/">' + SIR.esc(x.district) + '</a>'; }).join(' ');
      document.getElementById('pageFaq').innerHTML = '<div class="qa"><h3>Where do these figures come from?</h3><p>From the same tables as the <a href="' + stPage + '">' + C.label + '</a> pages, which give every source on their method page, and from the National Family Health Survey 2019-21 for the circumstances. Every figure is worked out when the page loads.</p></div>' +
        '<div class="qa"><h3>Does a circumstance explain the removals?</h3><p>No. A district\'s schooling, fuel or sanitation figures sit beside its removals, and the correlations across districts say which districts lost more, never why.</p></div>';
      if (C.seats) SIR.json('data/' + st + '/constituencies.json').then(function (A) {
        var mine = A.filter(function (a) { return a.district === d.district; }).sort(function (a, b) { return a.ac - b.ac; });
        document.getElementById('dLinks').insertAdjacentHTML('beforeend', '<p class="note">Its ' + mine.length + ' constituencies, each with its own page</p><p class="golist">' +
          mine.map(function (a) { return '<a class="chip" href="' + root + st + '/seat/' + a.ac + '/">' + SIR.esc(a.ac + '. ' + a.name) + '</a>'; }).join(' ') + '</p>');
      });
      SIR.tools();
    }).catch(SIR.fail);
  };
})();
