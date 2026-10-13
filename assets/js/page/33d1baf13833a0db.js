SIR.json('data/updates.json').then(function (U) {
  var root = document.body.getAttribute('data-root') || '';
  var fmt = function (d) { return new Date(d + 'T00:00:00').toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' }); };
  document.getElementById('updates').innerHTML = U.entries.map(function (e) {
    return '<h2 id="d-' + e.date + '">' + fmt(e.date) + '</h2><ul>' + e.items.map(function (it) {
      return '<li>' + (it[1] ? '<a href="' + root + SIR.esc(it[1]) + '">' + SIR.esc(it[0]) + '</a>' : SIR.esc(it[0])) + '</li>';
    }).join('') + '</ul>';
  }).join('');
}).catch(SIR.fail);
