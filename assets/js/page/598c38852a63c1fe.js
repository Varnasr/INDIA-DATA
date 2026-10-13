SIR.json('data/downloads.json').then(function (M) {
  var n = SIR.n, esc = SIR.esc, C = M.counts;
  var size = function (b) { return b == null ? '' : b >= 1048576 ? (b / 1048576).toFixed(1) + ' MB' : Math.max(1, Math.round(b / 1024)) + ' KB'; };
  var books = M.workbooks, src = 0;
  books.forEach(function (b) { b.sheets.forEach(function (s) { if (s.kind === 'source') src++; }); });

  SIR.inShort([
    n(C.published) + ' published tables and ' + n(src) + ' of the Chief Electoral Officers\' own tables, ' + n(C.rows) + ' rows in all.',
    'One Excel workbook for each state with its own pages, one for All India and one for the other twenty states and territories.',
    'Every workbook says what each sheet and each column holds, and what the table cannot show.',
    'Counts only. No file carries a name or an EPIC number.'
  ], 'The tables are free to reuse under CC BY 4.0. Cite the site, and the source each table names.');

  document.getElementById('kpis').innerHTML = [
    [n(C.workbooks), 'workbooks'], [n(C.tables), 'tables'], [n(C.rows), 'rows'], [size(M.zip.bytes), 'every table in one zip']
  ].map(function (x) { return '<div><b>' + x[0] + '</b><span>' + x[1] + '</span></div>'; }).join('');

  document.getElementById('zip').innerHTML = '<a class="btn" href="../' + esc(M.zip.file) + '" download>Download every table, CSV in a zip (' + size(M.zip.bytes) + ')</a>';

  // the Downloads button on every page opens this page at its own place's
  // workbook (#w-<id>); that one is opened, the first one otherwise
  var want = /^#w-/.test(location.hash) ? location.hash.slice(3) : '', open = Math.max(0, books.map(function (b) { return b.id; }).indexOf(want));
  var box = document.getElementById('books');
  box.innerHTML = books.map(function (b, i) {
    var rows = b.sheets.reduce(function (a, s) { return a + s.rows; }, 0);
    var body = b.sheets.map(function (s) {
      var link = s.kind === 'published' ? ' <a href="../' + esc(s.path) + '" download>CSV</a>' : '';
      return '<li><p class="sh"><b>' + esc(s.sheet) + '</b> <span class="tag ' + s.kind + '">' + (s.kind === 'published' ? 'published table' : 'source table') + '</span>' +
        ' <span class="meta">' + (s.level ? esc(s.level) + ', ' : '') + n(s.rows) + ' rows, ' + s.cols + ' columns</span>' + link + '</p>' +
        '<p>' + esc(s.what) + '</p>' + (s.cannot ? '<p class="cannot">' + esc(s.cannot) + '</p>' : '') + '</li>';
    }).join('');
    return '<section class="book" id="w-' + esc(b.id) + '"><div class="bh"><h3>' + esc(b.title) + '</h3>' +
      '<p class="meta">' + b.sheets.length + (b.sheets.length === 1 ? ' table, ' : ' tables, ') + n(rows) + ' rows</p>' +
      '<a class="btn" href="../' + esc(b.file) + '" download>Excel workbook (' + size(b.bytes) + ')</a>' +
      M.documents.filter(function (d) { return d.book === b.id; }).map(function (d) { return '<a class="btn" href="../' + esc(d.file) + '" download>' + esc(d.label) + ' (' + size(d.bytes) + ')</a>'; }).join('') + '</div>' +
      '<details class="figs"' + (i === open ? ' open' : '') + '><summary>What is in it</summary><ol class="sheets">' + body + '</ol></details></section>';
  }).join('');

  SIR.table('tDocs', [{ h: 'Place' }, { h: 'File' }, { h: 'Size', num: true }], M.documents.map(function (d) {
    return [esc(d.place), '<a href="../' + esc(d.file) + '" download>' + esc(d.label) + '</a>', size(d.bytes)];
  }));

  var all = [];
  books.forEach(function (b) { b.sheets.forEach(function (s) { s.columns.forEach(function (c) { all.push([b.title, s.sheet, c[0], c[1]]); }); }); });
  var q = document.getElementById('cq'), out = document.getElementById('cqN');
  function find() {
    var t = q.value.trim().toLowerCase();
    var hit = !t ? [] : all.filter(function (r) { return (r[2] + ' ' + r[3] + ' ' + r[1]).toLowerCase().indexOf(t) >= 0; });
    out.textContent = !t ? n(all.length) + ' columns in all. Type to find one.' : hit.length ? n(hit.length) + (hit.length === 1 ? ' column found.' : ' columns found.') + (hit.length > 100 ? ' The first 100 are shown.' : '') : 'No column matches.';
    SIR.table('tCols', [{ h: 'Workbook' }, { h: 'Sheet' }, { h: 'Column' }, { h: 'What it holds' }],
      hit.slice(0, 100).map(function (r) { return [esc(r[0]), esc(r[1]), '<code>' + esc(r[2]) + '</code>', esc(r[3])]; }));
  }
  q.addEventListener('input', find);
  find();
  SIR.jump && SIR.jump();
  var at = want && document.getElementById('w-' + want);
  if (at) { at.classList.add('here'); at.scrollIntoView(); }
  var pk = document.getElementById('wpick');
  pk.innerHTML = '<option value="">Choose a place</option>' + books.map(function (b) { return '<option value="' + esc(b.id) + '"' + (b.id === want ? ' selected' : '') + '>' + esc(b.title) + '</option>'; }).join('');
  pk.addEventListener('change', function () {
    var el = pk.value && document.getElementById('w-' + pk.value); if (!el) return;
    document.querySelectorAll('.dls .book.here').forEach(function (x) { x.classList.remove('here'); });
    el.classList.add('here'); var d = el.querySelector('details'); if (d) d.open = true;
    history.replaceState(null, '', '#w-' + pk.value); el.scrollIntoView();
  });
}).catch(SIR.fail);
