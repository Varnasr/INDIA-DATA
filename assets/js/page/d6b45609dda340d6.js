(function () {
  var path = location.pathname.toLowerCase();
  var fb = document.getElementById('fb404');
  if (fb) fb.href = '/feedback/?from=' + encodeURIComponent(location.pathname);
  var skip = { seat: 1, seats: 1, district: 1, districts: 1, page: 1, pages: 1, constituency: 1, index: 1, html: 1, www: 1, the: 1, and: 1 };
  var words = path.split(/[^a-z0-9]+/).filter(function (w) { return w.length > 2 && !skip[w]; });
  var first = path.split('/')[1] || '';
  if (!words.length && !first) return;
  SIR.json('data/search.json').then(function (S) {
    var norm = function (s) { return String(s).toLowerCase().replace(/[^a-z0-9]+/g, ' '); };
    var cand = S.pages.map(function (p) { return { t: (S.places[p[0]] || '') + ', ' + p[1], h: p[2] }; })
      .concat(S.rows.map(function (r) { return { t: r[2] + (r[3] ? ', ' + r[3] : '') + ' (' + (S.places[r[0]] || r[0]) + ')', h: r[4] }; }));
    // a word in the address counts in full when it is a word of the page's
    // name or address, and in part when the two share their first five
    // letters, so Khurdha still finds Khurda
    var near = function (w, t) { return t.length > 3 && w.length > 3 && w.slice(0, 5) === t.slice(0, 5); };
    // the state's own folder name says which place, so it picks the place's
    // overview and is not counted again as a word of every seat's name
    var own = words.filter(function (w) { return w !== first; });
    var kind = path.indexOf('/district/') >= 0 ? '/district/' : path.indexOf('/seat/') >= 0 ? '/seat/' : '';
    var scored = cand.map(function (c) {
      var toks = (norm(c.t) + ' ' + norm(c.h)).split(' '), s = 0;
      own.forEach(function (w) {
        if (toks.indexOf(w) >= 0) s += 2; else if (toks.some(function (t) { return near(w, t); })) s += 1;
      });
      var inPlace = first && c.h.split('/')[0] === first;
      if (inPlace && c.h === first + "/") s = Math.max(s, 1);
      if (s && inPlace) s += 1;
      if (s && kind && c.h.indexOf(kind) >= 0) s += 1;
      return { c: c, s: s };
    });
    var top = Math.max.apply(null, scored.map(function (x) { return x.s; }));
    scored = scored.filter(function (x) { return x.s >= 2 && x.s >= top * 0.75; })
      .sort(function (a, b) { return b.s - a.s || a.c.h.length - b.c.h.length; }).slice(0, 6);
    if (!scored.length) return;
    document.getElementById('guessList').innerHTML = scored.map(function (x) {
      return '<li><a href="/' + SIR.esc(x.c.h) + '">' + SIR.esc(x.c.t) + '</a></li>';
    }).join('');
    document.getElementById('guess').hidden = false;
  }).catch(function () {});
})();
