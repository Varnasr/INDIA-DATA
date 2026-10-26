SIR.json('data/updates.json').then(function (U) {
  var root = document.body.getAttribute('data-root') || '';
  var fmt = function (d) { return new Date(d + 'T00:00:00').toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' }); };
  document.getElementById('updates').innerHTML = U.entries.map(function (e) {
    return '<h2 id="d-' + e.date + '">' + fmt(e.date) + '</h2><ul>' + e.items.map(function (it) {
      // the section name before the first colon is the link, and the rest
      // reads as plain text, so a long item is not one long underline
      var t = it[0], i = t.indexOf(': '), head = i > 0 ? t.slice(0, i) : '', rest = i > 0 ? t.slice(i + 2) : t;
      if (!it[1]) return '<li>' + SIR.esc(t) + '</li>';
      if (!head) return '<li><a href="' + root + SIR.esc(it[1]) + '">' + SIR.esc(t) + '</a></li>';
      return '<li><a class="upd-sec" href="' + root + SIR.esc(it[1]) + '">' + SIR.esc(head) + '</a>. ' + SIR.esc(rest.charAt(0).toUpperCase() + rest.slice(1)) + (/[.?]$/.test(rest) ? '' : '.') + '</li>';
    }).join('') + '</ul>';
  }).join('');
}).catch(SIR.fail);
