SIR.json('data/india/events.json').then(function (D) {
  var n = SIR.n, esc = SIR.esc;
  // today in India, whatever the reader's own clock says
  var today = new Date(Date.now() + 330 * 60000).toISOString().slice(0, 10);
  var last = function (e) { return e.end || e.start; };
  var next = D.events.filter(function (e) { return last(e) >= today; });
  var past = D.events.filter(function (e) { return last(e) < today; }).reverse();
  var when = function (e) { return SIR.date(e.start) + (e.end ? ' to ' + SIR.date(e.end) : '') + (e.time ? ', ' + esc(e.time) : ''); };
  var li = function (e) {
    return '<li id="ev-' + esc(e.id.replace(/^ev-/, '')) + '"><p><b>' + when(e) + '</b>. ' + esc(e.title) + ' <span class="tag">' + esc(e.kind) + '</span>' + (e.party ? ' <span class="tag">political party</span>' : '') + '</p>' +
      '<p>' + esc(e.organiser) + '. ' + esc(e.place) + '.</p><p>' + esc(e.what) + '</p>' +
      '<p class="nsrc"><a href="' + esc(e.url) + '" rel="noopener">' + (e.source_kind === 'organiser' ? 'The organiser\'s announcement' : 'The report that gives the date') + '</a>. ' +
      (e.source_kind === 'organiser' ? '<span class="tag primary">organiser</span>' : '<span class="tag press">report</span>') + '</p>' +
      '<details><summary>The words of the source</summary><blockquote>' + esc(e.quote) + '</blockquote></details></li>';
  };
  SIR.inShort([
    next.length ? n(next.length) + (next.length === 1 ? ' event is' : ' events are') + ' coming up, the next on ' + SIR.date(next[0].start) + '.' : 'No event coming up has been announced in a source we could read.',
    n(past.length) + ' past events are listed, from ' + (past.length ? SIR.date(past[past.length - 1].start) : '') + '.',
    n(D.events.filter(function (e) { return e.party; }).length) + ' of the events were organised by political parties, and each is marked.'
  ], 'Each event links to the announcement or report that gives its date. Plans change, so check with the organiser.');
  document.getElementById('kpis').innerHTML = [
    [n(next.length), 'coming up'], [n(past.length), 'past'], [n(D.events.filter(function (e) { return e.kind === 'hearing'; }).length), 'public hearings'],
    [n(D.events.filter(function (e) { return e.party; }).length), 'by political parties']
  ].map(function (x) { return '<div><b>' + x[0] + '</b><span>' + x[1] + '</span></div>'; }).join('');
  document.getElementById('next').innerHTML = next.length ? next.map(li).join('') : '<li>No event coming up has been announced in a source we could read.</li>';
  document.getElementById('past').innerHTML = past.map(li).join('');
  document.getElementById('scope').textContent = D.scope;
  SIR.anchors && SIR.anchors();
  SIR.toc && SIR.toc();
  SIR.showFaq('india', 'events');
  SIR.jump && SIR.jump();
}).catch(SIR.fail);
