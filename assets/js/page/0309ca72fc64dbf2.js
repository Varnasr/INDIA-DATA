Promise.all([SIR.json('data/india/reads.json'), SIR.json('data/india/panels.json')]).then(function (r) {
  var D = r[0], PN = r[1];
  var n = SIR.n, esc = SIR.esc, C = D.counts;
  var by = function (g) { return D.items.filter(function (i) { return i.group === g; }); };
  SIR.inShort([
    n(C.items) + ' pieces from ' + n(C.outlets) + ' outlets and authors, ' + n(C.videos) + ' of them videos.',
    'Investigations of how the revision was run, data analyses of who was removed, research on the effect on results, court reporting, and the Election Commission\'s own account.',
    'On whether the deletions changed West Bengal\'s result, the pieces disagree, and the page sets them side by side.',
    n(PN.counts.people) + ' panels set ' + n(PN.counts.quotes) + ' quotations from politicians, officials and commentators beside the site\'s own figures, and say where those figures stop.'
  ], 'A listed piece is there because it adds evidence or argument about the revision. Its arguments are its own, the pieces disagree with each other in places, and listing one does not mean the site agrees with it.');

  var li = function (i) {
    return '<li><p><a href="' + esc(i.url) + '" rel="noopener"><b>' + esc(i.title) + '</b></a></p>' +
      '<p class="nsrc">' + esc(i.outlet) + (i.authors && i.outlet.indexOf(i.authors) < 0 ? ', ' + esc(i.authors) : '') + ', ' + SIR.date(i.date) +
      (i.video ? ' <span class="tag press">video' + (i.duration ? ', ' + esc(i.duration) : '') + '</span>' : '') + (i.subscription ? ' <span class="tag">subscription</span>' : '') + '</p>' +
      '<p>' + esc(i.shows) + '</p></li>';
  };
  var WB = ['newslaundry.com', 'caravanmagazine.in', 'debrajray', 'theindiaforum.in', 'K5qUfsPBSvQ'];
  document.getElementById('wb').innerHTML = D.items.filter(function (i) { return WB.some(function (w) { return i.url.indexOf(w) >= 0; }) && /Bengal|Bigger BJP/.test(i.title); })
    .map(function (i) { return '<li><a href="' + esc(i.url) + '" rel="noopener">' + esc(i.outlet) + '</a>, ' + SIR.date(i.date) + '. ' + esc(i.shows) + '</li>'; }).join('');

  // the panels: one per person, each quotation with what it rests on, the
  // site's figures and where they stop
  var pieceOf = function (p, id) { return p.pieces.filter(function (x) { return x.id === id; })[0]; };
  var row = function (k, v) { return v ? '<dt>' + k + '</dt><dd>' + esc(v) + '</dd>' : ''; };
  document.getElementById('pNav').innerHTML = 'There are panels on ' + PN.people.map(function (p) { return '<a href="#p-' + p.id + '">' + esc(p.name) + '</a>'; }).join(', ') + '.';
  document.getElementById('panels').innerHTML = PN.people.map(function (p) {
    return '<section class="pull" id="p-' + p.id + '" aria-labelledby="ph-' + p.id + '"><h3 id="ph-' + p.id + '">' + esc(p.name) + '</h3>' +
      '<p class="role">' + esc(p.role) + '</p><p>' + esc(p.intro) + '</p>' +
      '<ul class="srcs">' + p.pieces.map(function (x) {
        return '<li><a href="' + esc(x.url) + '" rel="noopener"' + (/[\u0900-\u097f]/.test(x.title) ? ' lang="hi"' : '') + '>' + esc(x.title) + '</a>' +
          (x.title_en ? ' (' + esc(x.title_en) + ')' : '') + (!x.title_en && /[.?!]$/.test(x.title) ? ' ' : '. ') + esc(x.outlet) + ', ' + SIR.date(x.date) + (x.length ? ', ' + esc(x.length) : '') + '.</li>';
      }).join('') + '</ul>' +
      '<ol class="pq">' + p.claims.map(function (c) {
        var pc = pieceOf(p, c.piece);
        return '<li><blockquote lang="' + c.lang + '">' + esc(c.quote) + '</blockquote>' +
          (c.translation ? '<p class="tr">' + esc(c.translation) + '</p>' : '') +
          '<p class="meta">' + esc(c.kind) + '. ' + esc(c.outlet || pc.outlet) + ', ' + SIR.date(pc.date) + (c.when ? ', at about ' + esc(c.when.replace(/~/g, '')) : '') + '.</p>' +
          (c.rests || c.site || c.stops ? '<dl>' + row('What it rests on', c.rests) + row("This site's figures", c.site) + row('Where the figures stop', c.stops) + '</dl>' : '') + '</li>';
      }).join('') + '</ol>' +
      '<div class="sides"><div><h4>Where the argument is strongest</h4><ul>' + p.strongest.map(function (t) { return '<li>' + esc(t) + '</li>'; }).join('') + '</ul></div>' +
      '<div><h4>Where it goes further than the figures</h4><ul>' + p.further.map(function (t) { return '<li>' + esc(t) + '</li>'; }).join('') + '</ul></div></div>' +
      (p.note ? '<p class="pnote">' + esc(p.note) + '</p>' : '') + '</section>';
  }).join('');

  var html = '';
  D.groups.forEach(function (g) {
    var its = by(g); if (!its.length) return;
    html += '<h2>' + esc(g) + '</h2><ol class="nfacts reads">' + its.map(li).join('') + '</ol>';
  });
  document.getElementById('secEnd').insertAdjacentHTML('beforebegin', html);

  SIR.anchors && SIR.anchors();
  SIR.toc && SIR.toc();
  SIR.showFaq('india', 'reading');
  SIR.jump && SIR.jump();
}).catch(SIR.fail);
