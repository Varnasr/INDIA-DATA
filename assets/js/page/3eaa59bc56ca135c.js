Promise.all([SIR.json('data/india/datasets.json'), SIR.json('data/india/states.json'), SIR.json('data/uttarpradesh/summary.json'), SIR.json('data/westbengal/tribunals.json')]).then(function (r) {
  var D = r[0], ST = {}, UP = r[2], TR = r[3].rows, n = SIR.n, esc = SIR.esc, S = D.sources, C = D.counts;
  r[1].states.forEach(function (s) { ST[s.state] = s; });
  var root = document.body.getAttribute('data-root') || '';
  var FILES = { 'data/uttarpradesh/summary.json': UP };

  // the official figure each comparison is set beside, read from its own file
  var official = function (c) {
    var o = c.official;
    if (o.value != null) return o.value;
    if (o.state) { var s = ST[o.state]; return o.field === 'draft' ? s.electors_before - s.removed : s[o.field]; }
    if (o.match) {
      var row = TR.filter(function (t) { return Object.keys(o.match).every(function (k) { return t[k] === o.match[k]; }); })[0];
      return row ? row.value : null;
    }
    return FILES[o.file] ? FILES[o.file][o.key] : null;
  };
  // what a figure written in lakh or crore rounds to, in its own unit
  var rounds = function (written, v) {
    var m = /^([\d.]+) (lakh|crore)$/.exec(written); if (!m) return null;
    var dec = (m[1].split('.')[1] || '').length, unit = m[2] === 'lakh' ? 1e5 : 1e7;
    return (v / unit).toFixed(dec) + ' ' + m[2];
  };
  var pct = function (x) { return SIR.d(x, x !== 0 && x < 0.1 ? Math.ceil(-Math.log10(x)) : 1); };
  var rows = [];
  D.entries.forEach(function (e) {
    e.compare.forEach(function (c) {
      var o = official(c), t = c.theirs, gap = '';
      if (o == null) return;
      if (c.relation === 'rounded') {
        var rd = rounds(c.as_written, o);
        gap = rd === c.as_written ? L('The official figure rounds to it') : L('The official figure rounds to {x}', { x: rd });
      } else if (c.relation === 'part') {
        gap = L('{p} per cent of the official figure', { p: SIR.d(100 * t / o, 1) });
      } else if (c.relation === 'floor') {
        gap = L('At least this many, {d} short of the official figure', { d: n(o - t) });
      } else {
        var dp = { d: n(Math.abs(t - o)), p: pct(100 * Math.abs(t - o) / o) };
        gap = t === o ? L('The same') : t > o ? L('{d} more, {p} per cent of the official figure', dp) : L('{d} fewer, {p} per cent of the official figure', dp);
      }
      var who = c.official.who ? '<br><span class="nsrc" lang="en" dir="ltr">' + esc(c.official.who) + '</span>' : '';
      rows.push({ e: e, c: c, o: o, cells: [
        '<a href="#ds-' + esc(e.id) + '" lang="en" dir="ltr">' + esc(e.maker) + '</a>',
        '<span lang="en" dir="ltr">' + esc(c.what) + (c.official.state ? ', ' + esc(c.official.state) : '') + '</span>',
        '<a href="' + esc(S[c.item].url) + '" rel="noopener">' + esc(c.as_written) + '</a>',
        n(o) + who, gap] });
    });
  });
  var H = [L('Made by'), L('What is counted'), L('Their figure'), L('Official figure'), L('How they compare')];
  document.getElementById('tDsCmp').innerHTML = '<thead><tr>' + H.map(function (h, i) { return '<th scope="col" class="' + (i === 2 || i === 3 ? 'num' : 'l') + '">' + h + '</th>'; }).join('') + '</tr></thead><tbody>' +
    rows.map(function (x) { return '<tr>' + x.cells.map(function (v, i) { return '<td class="' + (i === 2 || i === 3 ? 'num' : 'l') + '"' + (i ? ' data-label="' + esc(H[i]) + '"' : '') + '>' + v + '</td>'; }).join('') + '</tr>'; }).join('') + '</tbody>';

  // ---- In short, from the entries and the comparisons
  var same = rows.filter(function (x) { return x.c.relation === 'same'; });
  var eq = same.filter(function (x) { return x.c.theirs === x.o; }).length;
  var worst = same.slice().sort(function (a, b) { return Math.abs(b.c.theirs - b.o) / b.o - Math.abs(a.c.theirs - a.o) / a.o; })[0];
  SIR.inShort([
    L('{n} datasets and analyses of the revision by {m} makers, among them researchers, civic groups and newspapers, published from {f} to {l}. {d} of them are datasets that others can use, and the rest are published findings.', { n: C.entries, m: C.makers, f: SIR.date(C.first), l: SIR.date(C.last), d: C.datasets }),
    L('{t} of their totals count the same thing as an official figure. {e} of these equal it, and the widest gap is {p} per cent, in the count by {w}.', { t: same.length, e: eq, p: pct(100 * Math.abs(worst.c.theirs - worst.o) / worst.o), w: '<span lang="en" dir="ltr">' + esc(worst.e.maker) + '</span>' }),
    L('Several read the Commission\'s rolls and lists of names left off from the PDF files it publishes. The limits their makers state are given with each entry.'),
    L('None of these counts is official. A dataset with names is offered, where it is offered at all, through its maker, and each entry links the maker\'s own page or the report that carried its work.')
  ], L('A dataset or analysis is listed because it adds evidence about the revision. Its findings are its makers\', and a listing is not an endorsement.'));

  document.getElementById('kpis').innerHTML = [
    [n(C.entries), L('datasets and analyses')], [n(C.makers), L('makers')], [n(rows.length), L('figures set beside an official one')], [SIR.date(C.last), L('latest source')]
  ].map(function (x) { return '<div><b>' + x[0] + '</b><span>' + x[1] + '</span></div>'; }).join('');

  // ---- the entries
  var ACCESS = { 'public': L('Files anyone can download'), request: L('Published files, and fuller files on request'), aggregate: L('Counts published by the maker'), report: L('Published findings') };
  var KIND = { dataset: L('Dataset'), analysis: L('Analysis') };
  var on = function (s) {
    return s.from === 'disputes' ? '<a href="../disputes/#d-' + esc(s.id) + '">' + L('On the disputes page') + '</a>' : '<a href="../reading/#' + esc(s.group) + '">' + L('On the reading list') + '</a>';
  };
  var row = function (k, v) { return v ? '<dt>' + k + '</dt><dd lang="en" dir="ltr">' + v + '</dd>' : ''; };
  var card = function (e) {
    var cmp = rows.filter(function (x) { return x.e === e; });
    return '<section class="pull" id="ds-' + esc(e.id) + '" aria-labelledby="dh-' + esc(e.id) + '"><h3 id="dh-' + esc(e.id) + '" lang="en" dir="ltr">' + esc(e.maker) + '. ' + esc(e.name) + '</h3>' +
      '<p class="role">' + KIND[e.kind] + '. ' + ACCESS[e.access] + '.' + (e.states.length ? ' <span lang="en" dir="ltr">' + esc(e.states.join(', ')) + '</span>.' : '') + '</p>' +
      '<dl>' + row(L('What it covers'), esc(e.covers)) + row(L('How it was made'), esc(e.how)) + row(L('How it can be had'), esc(e.access_text) + ' <a href="' + esc(e.url) + '" rel="noopener">' + esc(e.via ? L('The report that carried it') : L('The maker\'s page')) + '</a>' + (e.via ? ' <span lang="en" dir="ltr">(' + esc(e.via) + ')</span>' : '') + '.') +
      row(L('Limits its makers state'), esc(e.limits)) +
      row(L('Beside the official figures'), (cmp.length ? cmp.map(function (x) { return esc(x.c.what) + (x.c.official.state ? ', ' + esc(x.c.official.state) : '') + ', ' + esc(x.c.as_written) + ' against ' + n(x.o) + '.'; }).join(' ') + ' ' : '') + esc(e.recorded)) + '</dl>' +
      '<p class="sub">' + L('Items that use it') + '</p><ul class="srcs" lang="en" dir="ltr">' + e.items.map(function (k) {
        var s = S[k];
        return '<li><a href="' + esc(s.url) + '" rel="noopener">' + esc(s.headline) + '</a>. ' + esc(s.outlet) + ', ' + SIR.date(s.date) + (s.subscription ? ', subscription' : '') + '. ' + on(s) + '.</li>';
      }).join('') + '</ul>' +
      (e.pages.length ? '<p class="pnote">' + L('Pages that use it') + ': ' + e.pages.map(function (p) { return '<a href="' + esc(root + p[0]) + '" lang="en" dir="ltr">' + esc(p[1]) + '</a>'; }).join(', ') + '.</p>' : '') + '</section>';
  };
  var box = document.getElementById('entries'), sel = document.getElementById('fState');
  var all = {}; D.entries.forEach(function (e) { e.states.forEach(function (s) { all[s] = 1; }); });
  sel.innerHTML = '<option value="">' + esc(L('Every state')) + '</option>' + Object.keys(all).sort().map(function (s) { return '<option>' + esc(s) + '</option>'; }).join('');
  var draw = function () {
    var s = sel.value;
    box.innerHTML = D.entries.filter(function (e) { return !s || e.states.indexOf(s) >= 0 || !e.states.length; }).map(card).join('');
  };
  sel.addEventListener('change', draw);
  draw();

  document.getElementById('cannot').innerHTML = L('A total that matches the official one shows that a maker read the same lists or rolls, and says nothing about whether the names on them were rightly left off or deleted. A figure that differs is shown with its gap, and the reason is given only where the maker states one. Some of the findings rest on names, which can join two different people of one name or classify a name wrongly, and the makers say so.');
  SIR.anchors && SIR.anchors();
  SIR.toc && SIR.toc();
  SIR.showFaq('india', 'datasets');
  SIR.jump && SIR.jump();
}).catch(SIR.fail);
