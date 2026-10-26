/* A chart alone, for another site's frame (site/pages/embed, written by
   scripts/make_embed_pages.py). The all-India chart reads the state table;
   a state's chart reads the constituency table its seat pages read and adds
   it up by district, in the state's own measure as assets/seat.js names it,
   so a state is never set against another. Each chart names its source and
   links back to the place's own pages. English only. ?theme=dark or light
   sets the colours; otherwise they follow the reader's system. */
(function () {
  var d1 = function (v) { return SIR.d(v, 1); };
  var body = document.body, back = body.getAttribute('data-back') || 'https://offtheroll.in/';
  var m = /[?&]theme=(dark|light)\b/.exec(location.search);
  if (m) document.documentElement.setAttribute('data-theme', m[1]);

  function credit(src) {
    document.getElementById('emSrc').innerHTML = 'Source: ' + src + ' Chart: <a href="' + SIR.esc(back) + '" target="_blank" rel="noopener">Off the Roll</a>, CC BY 4.0.';
  }

  SIR.embedChart = function () {
    var st = (location.pathname.match(/embed\/([a-z]+)\/(?:index\.html)?$/) || [])[1] || 'india';
    if (st === 'india') {
      return SIR.json('data/india/states.json').then(function (D) {
        var S = D.states.filter(function (s) { return s.per_100 != null; }).sort(function (a, b) { return b.per_100 - a.per_100; });
        document.getElementById('emSub').textContent = 'Names left off each state\'s draft roll for every 100 electors on its roll before the revision. Across the ' + S.length + ' states and union territories with a rate, ' + d1(D.total.per_100) + ' of every 100.';
        VIZ.lollipop('vEmbed', { label: 'Names left off per 100 electors, by state', axis: 'Left off per 100 electors',
          rows: S.map(function (s) { return { name: s.state, v: s.per_100, text: d1(s.per_100), tok: '--fill-red', hi: true }; }) });
        credit('the draft rolls and press notes of the Chief Electoral Officers, added up state by state.');
      }).catch(SIR.fail);
    }
    var C = (SIR.seatCfg || {})[st];
    if (!C) return SIR.fail(new Error('no chart for ' + st));
    return SIR.json('data/' + st + '/constituencies.json').then(function (A) {
      var L = C.lead, by = SIR.groupBy(A, 'district');
      var rate = function (rows) { return L.per * SIR.sum(rows, function (r) { return r[L.count] || 0; }) / SIR.sum(rows, function (r) { return r[L.base] || 0; }); };
      var rows = Object.keys(by).map(function (k) { return { name: k, v: rate(by[k]) }; }).sort(function (a, b) { return b.v - a.v; });
      var all = rate(A);
      document.getElementById('emSub').textContent = C.label + ': the ' + L.what + ', per ' + SIR.n(L.per) + ' on ' + L.of + ', district by district. The state as a whole: ' + d1(all) + '.';
      VIZ.lollipop('vEmbed', { label: C.label + ', ' + L.what + ' per ' + L.per + ', by district', axis: 'Per ' + L.per,
        rows: rows.map(function (r) { return { name: r.name, v: Math.max(r.v, 0), text: d1(r.v), tok: '--fill-red', hi: true }; })
          .concat([{ name: C.label, v: Math.max(all, 0), text: d1(all), tok: '--fill-grey', hi: true }]) });
      credit('the constituency table behind the ' + C.label + ' pages, added up by district. Their method page names where each figure comes from.');
    }).catch(SIR.fail);
  };
})();
