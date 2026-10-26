(function () {
  var C = SIR.seatCfg, n = SIR.n, esc = SIR.esc, d1 = function (v) { return SIR.d(v, 1); };
  var root = document.body.getAttribute('data-root') || '';
  var stSel = document.getElementById('cState'), seats = [].slice.call(document.querySelectorAll('.cseat'));
  var q = new URLSearchParams(location.search), A = [];
  var states = Object.keys(C).sort(function (a, b) { return C[a].label < C[b].label ? -1 : 1; });
  stSel.innerHTML = states.map(function (k) { return '<option value="' + k + '">' + esc(C[k].label) + '</option>'; }).join('');
  if (C[q.get('state')]) stSel.value = q.get('state');
  SIR.inShort([
    L('Constituencies are set only beside others of the same state, because each state published its own count and is measured in its own measure.'),
    L('The table gives each constituency in that measure, with its district, its rank in the state and its last winning margin.'),
    L('A count of names larger than a winning margin was large enough to decide the seat, which says nothing about whether it did.')
  ], L('Only counts are published, never a name.'));

  function rate(rows, Lm) { var c = 0, b = 0; rows.forEach(function (r) { c += r[Lm.count] || 0; b += r[Lm.base] || 0; }); return Lm.per * c / b; }

  function fillSeats(keep) {
    var opts = A.slice().sort(function (x, y) { return x.ac - y.ac; }).map(function (a) { return '<option value="' + a.ac + '">' + a.ac + '. ' + esc(a.name) + '</option>'; }).join('');
    var byNo = A.map(function (a) { return a.ac; }).sort(function (x, y) { return x - y; }), used = [];
    seats.forEach(function (s, i) {
      s.innerHTML = (i > 1 ? '<option value="">' + esc(L('None')) + '</option>' : '') + opts;
      var want = keep[i];
      if (want && byNo.indexOf(want) >= 0) s.value = String(want);
      // the first two are never empty: the lowest numbers not already chosen
      else if (i < 2) s.value = String(byNo.filter(function (v) { return used.indexOf(v) < 0 && keep.indexOf(v) < 0; })[0]);
      else s.value = '';
      if (s.value) used.push(+s.value);
    });
  }

  function draw() {
    var st = stSel.value, S = C[st], Lm = S.lead, E = S.election;
    var picked = [];
    seats.forEach(function (s) { var v = +s.value; if (v && picked.indexOf(v) < 0) picked.push(v); });
    var rows = picked.map(function (v) { return A.filter(function (a) { return a.ac === v; })[0]; }).filter(Boolean);
    var u = new URL(location.href); u.searchParams.set('state', st); u.searchParams.set('seats', picked.join(','));
    history.replaceState(null, '', u.pathname + u.search + u.hash);
    var ranked = A.slice().sort(function (x, y) { return y[Lm.count] / y[Lm.base] - x[Lm.count] / x[Lm.base]; });
    var stR = rate(A, Lm), falls = Lm.what.indexOf('fall') === 0;
    document.getElementById('cmMeasure').textContent = S.label + ' is measured by the ' + Lm.what + ', per ' + n(Lm.per) + ' on ' + Lm.of + '. ' + S.limits;
    VIZ.lollipop('vCmp', { label: S.label + ': ' + Lm.what + ' per ' + Lm.per + ', the chosen constituencies and the state', axis: 'Per ' + Lm.per,
      rows: rows.map(function (a) { var v = Lm.per * a[Lm.count] / a[Lm.base]; return { name: a.name, v: Math.max(v, 0), text: d1(v), tok: '--fill-red', hi: true }; })
        .concat([{ name: S.label, v: Math.max(stR, 0), text: d1(stR), tok: '--fill-grey', hi: true }]) });
    var line = function (label, f) { return '<tr><th scope="row">' + label + '</th>' + rows.map(function (a) { return '<td>' + f(a) + '</td>'; }).join('') + '</tr>'; };
    var cap = function (s) { return s.charAt(0).toUpperCase() + s.slice(1); };
    var body = line('District', function (a) { return esc(a.district); }) +
      line(cap(Lm.what) + ', per ' + n(Lm.per), function (a) { return d1(Lm.per * a[Lm.count] / a[Lm.base]); }) +
      line(cap(Lm.short || (falls ? 'fall in the roll' : 'names left off')), function (a) { return n(a[Lm.count]); }) +
      line(cap(Lm.of), function (a) { return n(a[Lm.base]); }) +
      line('Rank in the state, where 1 ' + (falls ? 'fell' : 'lost') + ' the most', function (a) { return (ranked.indexOf(a) + 1) + ' of ' + A.length; });
    if (E) {
      body += line('Winner in ' + E.year, function (a) { return esc(a.winner || a.win2025 || a.winner_party || ''); }) +
        line('Winning margin in ' + E.year, function (a) { return n(a.margin != null ? a.margin : a.margin2025); }) +
        line(cap(falls ? 'fall in the roll' : (Lm.short || 'names left off')) + ' larger than the margin?', function (a) { var m = a.margin != null ? a.margin : a.margin2025; return m == null ? '' : a[E.count] > m ? 'Yes' : 'No'; });
    }
    body += line('Its own page', function (a) { return '<a href="' + root + st + '/seat/' + a.ac + '/">' + esc(a.name) + '</a>'; });
    document.getElementById('tCmp').innerHTML = '<caption class="vh">' + esc(S.label) + ': the chosen constituencies</caption><thead><tr><th scope="col">Measure</th>' +
      rows.map(function (a) { return '<th scope="col">' + a.ac + '. ' + esc(a.name) + '</th>'; }).join('') + '</tr></thead><tbody>' + body + '</tbody>';
    var hi = rows.slice().sort(function (x, y) { return y[Lm.count] / y[Lm.base] - x[Lm.count] / x[Lm.base]; });
    document.getElementById('fCmp').innerHTML = rows.length < 2 ? 'Pick at least two different constituencies.' :
      '<b>Of the ' + rows.length + ' chosen, ' + esc(hi[0].name) + ' ' + (falls ? 'fell' : 'lost') + ' the most, ' + d1(Lm.per * hi[0][Lm.count] / hi[0][Lm.base]) + ' of every ' + n(Lm.per) +
      ', and ' + esc(hi[hi.length - 1].name) + ' the least, ' + d1(Lm.per * hi[hi.length - 1][Lm.count] / hi[hi.length - 1][Lm.base]) + '.</b> ' + S.label + ' as a whole: ' + d1(stR) + '.';
    SIR.tools && SIR.tools();
  }

  function load(keep) {
    var st = stSel.value;
    return SIR.json('data/' + st + '/constituencies.json').then(function (rows) {
      A = rows;
      var M = C[st].map;
      if (M) A.forEach(function (r) { Object.keys(M).forEach(function (k) { if (r[k] == null) r[k] = r[M[k]]; }); });
      var P = C[st].party;
      if (P) A.forEach(function (r) { r.winner = P[r.winner] || r.winner; });
      fillSeats(keep || []);
      draw();
    }).catch(SIR.fail);
  }
  stSel.addEventListener('change', function () { load([]); });
  seats.forEach(function (s) { s.addEventListener('change', draw); });
  load((q.get('seats') || '').split(',').map(Number).filter(Boolean)).then(function () { SIR.showFaq('india', 'seats'); });
})();
