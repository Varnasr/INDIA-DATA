SIR.json('data/india/courts.json').then(function (D) {
  var n = SIR.n, esc = SIR.esc, C = D.counts, I = D.items, Lst = D.listings;
  var lang = window.L && L.lang || 'en';
  // dates in the reader's language, as the disputes page writes them
  var MON = [L('January'), L('February'), L('March'), L('April'), L('May'), L('June'), L('July'), L('August'), L('September'), L('October'), L('November'), L('December')];
  var day = function (iso) { var p = iso.split('-'); return L('{d} {m} {y}', { d: +p[2], m: MON[+p[1] - 1], y: p[0] }); };
  var today = new Date(Date.now() + 330 * 60000).toISOString().slice(0, 10);
  // English text from the entries, marked so a reader's language tools know it
  var en = function (s) { return '<span lang="en" dir="ltr">' + esc(s) + '</span>'; };
  var title = function (m) { return lang !== 'en' && m.t[lang] ? esc(m.t[lang]) : esc(m.title); };
  var entry = function (id) { return '../disputes/#d-' + esc(id); };
  var tag = function (it) { return it.kind === 'primary' ? '<span class="tag primary">' + L('document') + '</span>' : '<span class="tag press">' + L('report') + '</span>'; };
  var src = function (id) {
    var it = I[id];
    return '<a href="' + esc(it.url) + '" rel="noopener" lang="en" dir="ltr">' + esc(it.outlet) + '</a>, ' + day(it.date) + '. ' + tag(it) +
      ' <a href="' + entry(id) + '">' + L('The entry on the disputes page') + '</a>';
  };
  var full = function (id) {
    var it = I[id];
    return '<li id="c-' + esc(id) + '"><p lang="en" dir="ltr">' + esc(it.claim) + '</p>' +
      (it.response ? '<p class="nresp" lang="en" dir="ltr">' + esc(it.response) + '</p>' : '') + '<p class="nsrc">' + src(id) + '</p></li>';
  };
  var ahead = function (ids) { return ids.map(function (x) { return Lst[x]; }).filter(function (x) { return x && x.date >= today; }); };
  var WHEN = { exact: function (s) { return s; }, approximate: function (s) { return L('About {date}', { date: s }); }, tentative: function (s) { return L('{date}, listed tentatively', { date: s }); } };
  var listing = function (x) {
    var tr = (x.t || {})[lang], own = lang === 'en' || !tr, f = own ? x : tr, txt = own && lang !== 'en' ? en : esc;
    return '<p><b>' + L('{date}, {court}', { date: (WHEN[x.date_kind] || WHEN.exact)(day(x.date)), court: txt(f.court) }) + '</b></p>' +
      '<p>' + txt(f.due) + '</p><p class="nsrc">' + L('<a href="{src}">{outlet}</a> gives the date.', { src: esc(x.source_url), outlet: esc(x.source_name) }) + '</p>';
  };
  var WHY = { two: L('This entry names the case numbers of this matter and of another.'), cites: L('This entry cites an entry in this matter, or is cited by one, and no entry says they are the same case.') };

  var M = D.matters, withNext = M.filter(function (m) { return ahead(m.listings).length; });
  // the largest single case: a matter with a note holds separate cases
  var big = M.filter(function (m) { return !m.note; }).sort(function (a, b) { return b.items.length - a.items.length; })[0];
  SIR.inShort([
    L('{m} matters in the courts on the revision, holding {e} entries dated from {a} to {b}.', { m: n(C.matters), e: n(C.in_matters), a: day(C.first), b: day(C.last) }),
    L('The matter with the most entries is {t}, with {e}.', { t: title(big), e: n(big.items.length) }),
    withNext.length ? L('{k} of the matters have a hearing or a deadline dated ahead.', { k: n(withNext.length) }) : L('No matter has a hearing or a deadline dated ahead.'),
    L('{c} other cases before {k} courts are listed apart, because no entry ties them to a matter.', { c: n(D.other.filter(function (o) { return o.court; }).reduce(function (t, o) { return t + o.cases.length; }, 0)), k: n(D.other.filter(function (o) { return o.court; }).length) })
  ], L('Each entry is what the court\'s own document or the named report says. An entry is in a matter only where an entry says it is the same case. Nothing here says what anyone intended.'));

  document.getElementById('kpis').innerHTML = [
    [n(C.matters), L('matters')], [n(C.in_matters), L('entries in them')], [n(withNext.length), L('with a date ahead')], [n(C.other_cases), L('other cases')]
  ].map(function (x) { return '<div><b>' + x[0] + '</b><span>' + x[1] + '</span></div>'; }).join('');

  document.getElementById('mIndex').innerHTML = M.map(function (m) {
    var nx = ahead(m.listings)[0];
    return '<li><p><b><a href="#m-' + esc(m.id) + '">' + title(m) + '</a></b></p><p>' +
      L('{court}. {e} entries, from {a} to {b}.', { court: en(m.court), e: n(m.items.length), a: day(m.first), b: day(m.last) }) +
      (nx ? ' ' + L('Next date listed: {d}.', { d: day(nx.date) }) : '') + '</p></li>';
  }).join('');

  document.getElementById('mList').innerHTML = M.map(function (m) {
    var nx = ahead(m.listings), rx = ahead(m.related_listings), last = m.latest, doc = m.latest_document;
    var h = '<section class="cmatter" id="m-' + esc(m.id) + '"><h3>' + title(m) + '</h3>';
    h += '<p>' + L('{court}. {e} entries, from {a} to {b}.', { court: en(m.court), e: n(m.items.length), a: day(m.first), b: day(m.last) }) + '</p>';
    if (m.note) h += '<p class="note">' + (lang !== 'en' && m.nt[lang] ? esc(m.nt[lang]) : esc(m.note)) + '</p>';
    if (m.case_title) h += '<p>' + L('Case title, as <a href="{href}">an entry</a> gives it: {t}.', { href: entry(m.title_from), t: en(m.case_title) }) + '</p>';
    if (m.numbers.length) h += '<p>' + L('Case numbers: {list}.', { list: m.numbers.map(function (x) { return '<a href="' + entry(x.item) + '" lang="en" dir="ltr">' + esc(x.key) + '</a>'; }).join(', ') }) + '</p>';
    else h += '<p>' + L('No entry in this matter gives a case number.') + '</p>';
    if (m.actors.length) h += '<p>' + L('Parties and bodies the entries name: {list}.', { list: en(m.actors.join(', ')) }) + '</p>';
    if (m.page) h += '<p>' + L('<a href="{href}">The page on West Bengal\'s appellate tribunals</a> sets their figures side by side, each with its source.', { href: '../../' + esc(m.page) }) + '</p>';
    h += '<h4>' + L('Next in this matter') + '</h4>' + (nx.length ? nx.map(listing).join('') : '<p>' + L('No hearing or deadline ahead has been dated in this matter.') + '</p>');
    h += '<h4>' + L('The latest entry') + '</h4><ol class="nfacts">' + full(last) + '</ol>';
    if (doc && doc !== last) h += '<h4>' + L('The latest court document') + '</h4><ol class="nfacts">' + full(doc) + '</ol>';
    h += '<details><summary>' + L('Every entry in date order ({k})', { k: n(m.items.length) }) + '</summary><ol class="nfacts">' + m.items.map(full).join('') + '</ol></details>';
    if (m.related.length) {
      h += '<details><summary>' + L('Related entries outside this case ({k})', { k: n(m.related.length) }) + '</summary><ul class="nfacts">' + m.related.map(function (r) {
        var it = I[r.id];
        return '<li><p lang="en" dir="ltr">' + esc(it.claim) + '</p><p class="nresp">' + (WHY[r.why] || en(r.why)) + '</p><p class="nsrc">' + src(r.id) + '</p></li>';
      }).join('') + '</ul></details>';
      if (rx.length) h += '<p class="note">' + L('A related entry has a date ahead: {d}.', { d: rx.map(function (x) { return day(x.date); }).join(', ') }) + '</p>';
    }
    return h + '</section>';
  }).join('');

  document.getElementById('oList').innerHTML = D.other.map(function (o) {
    return '<h3>' + (o.court ? en(o.court) : L('Entries about work the courts ordered, before no single court')) + '</h3><ol class="nfacts">' + o.cases.map(function (c) {
      var nx = ahead(c.listings);
      return c.items.map(function (id, j) {
        var li = full(id);
        if (j === 0 && c.numbers.length) li = li.replace('<p class="nsrc">', '<p>' + L('Case numbers: {list}.', { list: en(c.numbers.join(', ')) }) + '</p><p class="nsrc">');
        if (j === c.items.length - 1 && nx.length) li = li.replace(/<\/li>$/, nx.map(listing).join('') + '</li>');
        return li;
      }).join('');
    }).join('') + '</ol>';
  }).join('');

  SIR.anchors && SIR.anchors();
  SIR.toc && SIR.toc();
  SIR.showFaq('india', 'courts');
  SIR.jump && SIR.jump();
}).catch(SIR.fail);
