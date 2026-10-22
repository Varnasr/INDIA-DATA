SIR.json('data/india/disputes.json').then(function (D) {
  var n = SIR.n, esc = SIR.esc, its = [], secs = {};
  D.sections.forEach(function (s) {
    secs[s.id] = s.title;
    s.items.forEach(function (i) { if ((i.issues || []).some(function (x) { return /ECINET/.test(x); })) its.push(i); });
  });
  its.sort(function (a, b) { return a.date < b.date ? -1 : a.date > b.date ? 1 : 0; });
  var prim = its.filter(function (i) { return i.kind === 'primary'; }).length, months = {};
  its.forEach(function (i) { var m = i.date.slice(0, 7); months[m] = (months[m] || 0) + 1; });
  var first = its[0], last = its[its.length - 1];
  SIR.inShort([
    n(its.length) + ' items about ECINET or ERONET on the disputes page, from ' + SIR.date(first.date) + ' to ' + SIR.date(last.date) + '.',
    n(prim) + ' of them are official documents, the press notes of the Commission or of a Chief Electoral Officer, and the rest are reports.',
    'They sit in ' + n(Object.keys(its.reduce(function (a, i) { a[i.section] = 1; return a; }, {})).length) + ' sections of the disputes page.'
  ], 'Each item is what its source says. The review of ECINET\'s code cannot say whether any control it found was used.');
  document.getElementById('kpis').innerHTML = [
    [n(its.length), 'items'], [n(prim), 'official documents'], [SIR.date(first.date), 'first item'], [SIR.date(last.date), 'latest item']
  ].map(function (x) { return '<div><b>' + x[0] + '</b><span>' + x[1] + '</span></div>'; }).join('');
  var ms = Object.keys(months).sort();
  VIZ.lollipop('vMonth', { label: 'Items about ECINET or ERONET, by month of report', axis: 'Items',
    rows: ms.map(function (m) { return { name: SIR.date(m + '-01').replace(/^1 /, ''), v: months[m], text: n(months[m]), tok: '--fill-navy', hi: true }; }) });
  document.getElementById('list').innerHTML = its.map(function (i) {
    return '<li id="e-' + esc(i.id) + '"><p><b>' + SIR.date(i.date) + '</b>, ' + esc(i.state || 'All India') + '. <span class="tag">' + esc(secs[i.section] || '') + '</span></p>' +
      '<p>' + esc(i.claim) + '</p>' + (i.response ? '<p class="nresp">' + esc(i.response) + '</p>' : '') +
      '<p class="nsrc"><a href="' + esc(i.url) + '" rel="noopener">' + esc(i.outlet) + '</a>, "' + esc(i.headline) + '". ' +
      (i.kind === 'primary' ? '<span class="tag primary">document</span>' : '<span class="tag press">report</span>') +
      ' <a href="../disputes/#d-' + esc(i.id) + '">On the disputes page</a>.</p>' +
      (i.quote ? '<details><summary>The words of the source</summary><blockquote>' + esc(i.quote) + '</blockquote></details>' : '') + '</li>';
  }).join('');
  SIR.anchors && SIR.anchors();
  SIR.toc && SIR.toc();
  SIR.showFaq('india', 'ecinet');
  SIR.jump && SIR.jump();
}).catch(SIR.fail);
