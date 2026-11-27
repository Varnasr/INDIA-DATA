SIR.json('data/westbengal/tribunals.json').then(function (T) {
  var E = SIR.esc, D = SIR.date, R = T.rows, byId = {};
  R.concat(T.derived).forEach(function (x) { byId[x.id] = x; });
  var BASIS = {
    official: [L('Official document'), '--fill-navy'], unidentified: [L('An official document named without its date or number'), '--fill-pink'], court: [L('Supreme Court order'), '--fill-teal'], counsel: [L('Counsel in court'), '--fill-amber'],
    analysis: [L('Independent count of the appeal portal'), '--fill-purple'], press: [L('The newspaper\'s own statement'), '--fill-grey'], unnamed: [L('A source the newspaper does not name'), '--fill-red']
  };
  var MEASURE = {
    filed: L('Appeals filed'), decided: L('Appeals decided'), pending: L('Appeals pending'), on_roll: L('Decided with the name on the roll'),
    off_roll: L('Decided with the name off the roll'), share_on_roll: L('Share of decided appeals in favour of the elector'),
    tribunals: L('Tribunals'), resigned: L('Tribunal judges who resigned'), per_day: L('Appeals a judge can hear in a day')
  };
  // what each basis means, shown above the table
  var MEANS = {
    official: L('The Commission\'s affidavit or its annexure, or the Chief Electoral Officer\'s reply under the RTI Act, which the report or copy that gives the figure identifies by its number, date or paragraph.'),
    unidentified: L('A newspaper names the official document a figure comes from, such as the Commission\'s affidavit, and gives neither its date nor its number, so the document cannot be found from the report. It is kept apart from the official documents.'),
    court: L('The Supreme Court\'s own order.'),
    counsel: L('What a named lawyer told the Supreme Court at a hearing, as a report of the hearing gives it.'),
    analysis: L('A count by the Civic Research Group, an independent group, of the appeals listed on the tribunals\' portal.'),
    press: L('The newspaper states the figure and names no source for it.'),
    unnamed: L('The newspaper gives the figure from a person it does not name.')
  };
  var KIND = { all: L('all appeals'), by_deleted: L('appeals by deleted electors'), against_inclusion: L('appeals against inclusion') };
  var fig = function (x) {
    var v = x.measure === 'share_on_roll' ? L('{x} per cent', { x: SIR.n(x.value) }) : x.approx === 'range' ? L('{a} to {b}', { a: SIR.n(x.value), b: SIR.n(x.value_hi) }) : SIR.n(x.value);
    return { over: L('over {x}', { x: v }), 'at least': L('at least {x}', { x: v }), nearly: L('nearly {x}', { x: v }), about: L('about {x}', { x: v }), 'a little over': L('a little over {x}', { x: v }) }[x.approx] || v;
  };
  var when = function (x) {
    return x.date_kind === 'as_of' ? L('Figure as on {d}', { d: D(x.date) }) : x.date_kind === 'said' ? L('Said or filed on {d}', { d: D(x.date) }) : L('Report of {d}, the figure undated', { d: D(x.date) });
  };
  var what = function (x) { return MEASURE[x.measure] + (x.appeals && x.appeals !== 'all' ? ', ' + KIND[x.appeals] : ''); };
  var src = function (x) { return '<a href="' + E(x.url) + '" rel="noopener" lang="en">' + E(x.source) + '</a>'; };

  var lo = T.latest_official, F = byId[lo.filed], Dc = byId[lo.decided], P = byId[lo.pending];
  document.getElementById('kpis').innerHTML = [
    [SIR.lakh(F.value), L('appeals filed, Election Commission, {d}', { d: D(F.date) })], [SIR.lakh(Dc.value), L('decided by then')], [SIR.lakh(P.value), L('pending')],
    [T.counts.rows, L('figures from {n} sources', { n: T.counts.sources })], [T.counts.flags, L('pairs of figures that differ')]
  ].map(function (k) { return '<div><b>' + k[0] + '</b><span>' + k[1] + '</span></div>'; }).join('');

  // the orders and events, in the site's words, each with its document
  var O = {
    ordered: L('The Supreme Court provided for tribunals of former Chief Justices and judges to hear appeals against the orders of the judicial officers, to be notified by the Election Commission in consultation with the Chief Justice of the High Court at Calcutta. The order repeats that, as its order of 24 February 2026 had said, no such appeal could go to an executive or administrative officer.'),
    working: L('The Supreme Court\'s order records that the tribunals were to begin work on this day. Appeals decided by 21 and 27 April were to take effect through a supplementary roll before polling, and a pending appeal gave no right to vote.'),
    chief_justice: L('The Supreme Court declined to take up fresh grievances about the appeals and gave the parties liberty to approach the Chief Justice of the High Court at Calcutta, Supreme Court Observer reported.'),
    portal: L('The judges refused to log in to a new portal the Commission had introduced, The Times of India reported, and the tribunals could not upload their orders.'),
    uploads: L('After the Commission changed the portal, the tribunals began uploading orders again after a gap of nearly 45 days, sources told The Times of India.'),
    priority: L('The Supreme Court directed the tribunals to hear the appeals of deleted electors first and to defer the appeals against inclusion. It directed the Commission, with the Chief Justice of the High Court, to increase the strength of the tribunals, Hindustan Times reported.')
  };
  document.getElementById('orders').innerHTML = T.orders.map(function (o) {
    return '<li><time datetime="' + o.date + '">' + D(o.date) + '</time>. ' + O[o.key] + ' <span class="muted">' + src(o) + ', <a href="../../india/disputes/#d-' + E(o.item) + '">' + L('the entry') + '</a></span></li>';
  }).join('');

  // the chart: appeals decided, every kind together
  var pts = R.filter(function (x) { return x.measure === 'decided' && x.appeals === 'all'; }).concat(T.derived);
  var day = function (iso) { return Date.parse(iso + 'T00:00:00Z') / 864e5; };
  var used = Object.keys(BASIS).filter(function (b) { return pts.some(function (x) { return x.basis === b; }); });
  SIR.chart('cDecided', { type: 'scatter', data: { datasets: used.map(function (b) {
      return { label: BASIS[b][0], $token: BASIS[b][1], pointRadius: 6, pointHoverRadius: 8,
        data: pts.filter(function (x) { return x.basis === b; }).map(function (x) { return { x: day(x.date), y: x.value, r: x }; }) };
    }) },
    options: { plugins: { tooltip: { callbacks: { label: function (c) { var x = c.raw.r;
      return L('{v} decided, {who}, as {src} gives it, {d}', { v: x.from ? SIR.n(x.value) : fig(x), who: x.who, src: x.source, d: D(x.date) }) + (x.from ? ' ' + L('(two figures added)') : ''); } } } },
      scales: { x: { type: 'linear', title: { display: true, text: L('Date of the count') }, ticks: { callback: function (v) { var d = new Date(v * 864e5).toISOString().slice(0, 10); return D(d).replace(/ \d{4}$/, ''); } } },
        y: { type: 'logarithmic', title: { display: true, text: L('Appeals decided, all kinds') }, ticks: { callback: function (v) { return Math.abs(Math.log10(v) - Math.round(Math.log10(v))) < 1e-9 ? SIR.n(v) : ''; } } } } } });
  var cs = R.filter(function (x) { return x.basis === 'counsel' && x.measure === 'decided'; });
  var cl = cs.reduce(function (m, x) { return x.date > m ? x.date : m; }, '');
  cs = cs.filter(function (x) { return x.date === cl; });
  document.getElementById('nDecided').textContent = L('A count from counsel or from a newspaper is drawn as given. Where a source says "a little over" or "about", the dot sits at the number it names.');
  document.getElementById('fDecided').innerHTML = '<b>' + L('By the Election Commission\'s affidavit, {d} of {f} appeals had been decided on {t}.', { d: SIR.n(Dc.value), f: SIR.n(F.value), t: D(Dc.date) }) + '</b> ' +
    (cs.length > 1 ? L('Newspapers reported the count counsel gave at the hearing of {d} differently, from {a} to {b} appeals decided.', { d: D(cl), a: SIR.n(Math.min.apply(null, cs.map(function (x) { return x.value; }))), b: SIR.n(Math.max.apply(null, cs.map(function (x) { return x.value; }))) }) : '');

  // where the sources differ
  var WHY = function (w, a, b, m) {
    var v = { a: a, b: b };
    return w === 'date' ? L('{a} and {b} give different figures for the same date.', v) : w === 'document' ? L('{a} and {b} give different figures from the same document.', v)
      : w === 'week' ? L('{a} and {b}, a week or less apart, give different figures.', v) : m === 'resigned' ? L('{b} is lower than the earlier figure from {a}, though a count of judges who have resigned cannot fall.', v)
      : L('{b} is lower than the earlier figure from {a}, though a count of appeals filed or decided cannot fall.', v);
  };
  var one = function (x) { return L('{src}, {who}, {d}, "{w}"', { src: E(x.source), who: E(x.who), d: D(x.date), w: '<span lang="en">' + E(x.as_written) + '</span>' }); };
  document.getElementById('flags').innerHTML = T.flags.map(function (f, i) {
    var a = byId[f.rows[0]], b = byId[f.rows[1]];
    return '<li id="fl-' + i + '"><b>' + what(a) + '.</b> ' + WHY(f.why, E(a.source), E(b.source), f.measure) + ' ' + one(a) + '. ' + one(b) + '.</li>';
  }).join('');

  // the table
  var notes = [];
  var rows = R.map(function (x) {
    var n = '';
    if (x.note) { notes.push('<li id="tn-' + x.id + '">' + E(x.note) + '</li>'); n = ' <a href="#tn-' + x.id + '">' + L('note {n}', { n: notes.length }) + '</a>'; }
    var fl = (x.flags || []).map(function (i) { return '<a href="#fl-' + i + '">' + L('differs') + '</a>'; }).join(' ');
    var item = /^wb-adj:/.test(x.item) ? '<a href="../">' + L('West Bengal overview') + '</a>' : x.item.indexOf('rti-') === 0 ? '<a href="../../india/rti/#r-' + E(x.item) + '">' + L('the entry') + '</a>' : '<a href="../../india/disputes/#d-' + E(x.item) + '">' + L('the entry') + '</a>';
    return [D(x.date) + '<small>' + when(x) + '</small>', what(x), '<b>' + fig(x) + '</b><small lang="en">"' + E(x.as_written) + '"</small>' + (fl ? '<small>' + fl + '</small>' : ''),
      BASIS[x.basis][0] + '<small>' + E(x.who) + '</small>', src(x) + '<small>' + item + n + (x.paywall ? ', ' + L('subscription') : '') + '</small>'].map(function (v) { return '<span style="overflow-wrap:anywhere">' + v + '</span>'; });
  });
  SIR.table('tObs', [{ h: L('Date') }, { h: L('What is counted') }, { h: L('Figure, and the words of the source') }, { h: L('Who gives it') }, { h: L('Where it was read') }], rows);
  document.getElementById('notes').innerHTML = notes.join('');
  document.getElementById('bases').innerHTML = Object.keys(BASIS).filter(function (b) { return R.some(function (x) { return x.basis === b; }); })
    .map(function (b) { return '<li><b>' + BASIS[b][0] + '.</b> ' + MEANS[b] + '</li>'; }).join('');
  SIR.showFaq('wb', 'tribunals');
}).catch(SIR.fail);
