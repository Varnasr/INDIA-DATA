Promise.all([SIR.json('data/india/ssr_draft.json'), SIR.json('data/india/process.json'), SIR.json('data/india/states.json'), SIR.json('data/india/now.json').catch(function () { return null; })]).then(function (r) {
  var G = r[0].states, P = r[1], S = {}, NW = (r[3] && r[3].pages) || {}, E = SIR.esc, D = SIR.date;
  r[2].states.forEach(function (s) { S[s.state] = s; });
  var today = SIR.owin ? SIR.owin.today : new Date(Date.now() + 5.5 * 36e5).toISOString().slice(0, 10);
  var and = function (a) { return a.length < 2 ? a.join('') : a.slice(0, -1).join(', ') + L(' and ') + a[a.length - 1]; };
  var nm = function (g) { return E(g.state); };

  // each state's standing: a draft on record, due and not found, still to
  // come, or postponed with no new dates
  G.forEach(function (g) {
    var x = g.draft;
    g.k = x ? 'got' : g.postponed ? 'post' : g.due < today ? 'late' : 'wait';
    // the final roll of the intensive revision: the draft's own base where a
    // draft is recorded, else the final roll on record for the state
    var s = S[g.state] || {};
    g.base = x && x.base != null ? x.base : s.electors_final != null ? s.electors_final : null;
    g.baseDate = x && x.base != null ? x.base_date : s.electors_final != null ? s.final_date : null;
    if (!x) return;
    // a draft the press describes as unchanged from the final roll, with no
    // official count (figures "total" and no change), is shown as reported,
    // and no change is worked out from it
    g.c = x.change == null ? 'nobase' : x.figures === 'total' && x.change === 0 ? 'same' : 'calc';
    if (g.c === 'calc') g.per = 100 * x.change / x.base;
    if (x.men && x.women) g.ratio = Math.round(1000 * x.women / x.men);
  });
  var by = function (k) { return G.filter(function (g) { return g.k === k; }); };
  var got = by('got'), late = by('late'), wait = by('wait'), post = by('post');
  var calc = got.filter(function (g) { return g.c === 'calc'; }), same = got.filter(function (g) { return g.c === 'same'; });
  var up = calc.filter(function (g) { return g.draft.change > 0; }), down = calc.filter(function (g) { return g.draft.change < 0; });
  var press = got.filter(function (g) { return g.draft.press; });
  var waitDue = wait.map(function (g) { return g.due; }).sort();

  SIR.inShort([
    L('On {t}, a count of the draft roll is on record for {n} of the {a} states and union territories in the special summary revision.', { t: D(today), n: got.length, a: G.length }),
    !calc.length ? '' : up.length === calc.length ? L('Each of the {m} drafts that can be set against a final roll of the intensive revision is larger than that final roll.', { m: calc.length })
      : L('Of the {m} drafts that can be set against a final roll of the intensive revision, {k} are larger than that final roll and {j} are smaller.', { m: calc.length, k: up.length, j: down.length }),
    same.length ? L('No official count of the draft has been found in {s}. The press reported it as unchanged from the final roll, so it is shown at that figure as reported, and no change is worked out for it.', { s: and(same.map(nm)) }) : '',
    got.length ? L('{p} of the {n} counts come from a press report and {o} from an official document.', { p: press.length, n: got.length, o: got.length - press.length }) : '',
    late.length ? L('The draft was due in {s}, and no published count of it has been found.', { s: and(late.map(nm)) }) : '',
    wait.length ? L('{n} more drafts are due between {a} and {b}.', { n: wait.length, a: D(waitDue[0]), b: D(waitDue[waitDue.length - 1]) }) : '',
    post.map(function (g) { return L('The special summary revision in {s} was postponed on {d}, and no new dates have been given.', { s: nm(g), d: D(g.postponed) }); }).join(' ')
  ], L('The change from the final roll is a net figure. New electors and names deleted since the final roll are counted together in it, so it does not say how many names were added or deleted.'));

  document.getElementById('kpis').innerHTML = [
    [got.length, L('drafts on record')], [late.length, L('drafts due and not found')], [wait.length, L('drafts still to come')], [post.length, L('postponed')]
  ].map(function (k) { return '<div><b>' + k[0] + '</b><span>' + k[1] + '</span></div>'; }).join('');

  // the orders: a step is an order where it first names a state, and a change
  // of dates where every state it names was already in an earlier step
  var seen = {}, orders = [], moved = [];
  var steps = P.timeline.filter(function (t) { return t.ssr; }).sort(function (a, b) { return a.date < b.date ? -1 : a.date > b.date ? 1 : 0; });
  steps.forEach(function (t) {
    var fresh = t.ssr.states.filter(function (s) { return !seen[s]; });
    if (fresh.length) orders.push(t);
    else if (!t.ssr.postponed) t.ssr.states.forEach(function (s) { if (moved.indexOf(s) < 0) moved.push(s); });
    t.ssr.states.forEach(function (s) { seen[s] = true; });
  });
  var q = orders.length ? orders[0].ssr.qualifying : null;
  document.getElementById('sWhat').innerHTML = L('The Commission ordered a special summary revision of the roll in {n} states and union territories where the revision of the roll had ended, in orders of {d}. It acts under section 21 of the Representation of the People Act, 1950, and the qualifying date is {q}.', { n: G.length, d: and(orders.map(function (t) { return D(t.date); })), q: D(q) }) +
    (moved.length ? ' ' + L('The dates were later changed in {s}, and the table below gives the latest dates for each state.', { s: and(moved.sort().map(E)) }) : '');
  document.getElementById('sForms').innerHTML = L('Outside the intensive revision, the forms of the Registration of Electors Rules, 1960 are used. Form 6 is the application to be added to the roll, Form 7 the objection to a name and Form 8 the correction of an entry.') +
    ' <a href="../../help/#form6">' + L('How to ask to be added on Form 6, or to correct an entry on Form 8') + '</a>';
  // how it differs from the intensive revision, in the words of the order
  // that began it and of the one report that compares the two
  var sir = P.timeline.filter(function (t) { return /Only electors whose enumeration forms came back/.test(t.text); })[0];
  var ka = steps.filter(function (t) { return t.ssr.states.indexOf('Karnataka') >= 0 && /booth level officers will not visit homes/.test(t.text); })[0];
  var nie = ka && ka.src.filter(function (s) { return /New Indian Express/.test(s.name); })[0];
  var link = function (s, t) { return s ? ' (<a href="' + E(s.url) + '" rel="noopener" lang="en">' + E(t || s.name) + '</a>)' : ''; };
  document.getElementById('sDiff').innerHTML = (sir ? L('The intensive revision began with booth level officers visiting every household with an enumeration form, and the Commission\'s order of {d} said that only electors whose forms came back would be on the draft roll.', { d: D(sir.date) }) + link(sir.src[0]) : '') +
    (nie ? ' ' + L('In Karnataka an official of the Chief Electoral Officer\'s office told The New Indian Express that booth level officers will not visit homes with forms in the summary revision, as they did in the intensive revision, and the paper reported that cases will not be heard as they were in the intensive revision.') + link(nie) : '');
  var first = orders[0];
  document.getElementById('sRules').innerHTML = first ? L('The Commission\'s letter of {d} says that no claim may be refused, and no name deleted, because a person cannot give an Aadhaar number. It requires the registration officer to check deletions in person where they pass 2 per cent of a polling station\'s roll, or where one person has objected in more than five cases.', { d: D(first.date) }) + link(first.src[0]) : '';
  document.getElementById('sOrders').innerHTML = steps.map(function (t) {
    return '<li><time datetime="' + t.date + '">' + D(t.date) + '</time> <span lang="en">' + E(t.title) + '</span>. ' +
      L('It names {s}.', { s: and(t.ssr.states.map(E)) }) + ' <span class="muted">' +
      t.src.map(function (s) { return '<a href="' + E(s.url) + '" rel="noopener" lang="en">' + E(s.name) + '</a>'; }).join(' · ') + '</span></li>';
  }).join('');

  // the chart: the change for every 100 electors on the final roll, in
  // alphabetical order, an official count navy and a press count amber
  var pc = function (v) { return (v > 0 ? '+' : v < 0 ? '−' : '') + SIR.d(Math.abs(v), 1); };
  if (calc.length) {
    VIZ.rank('vChange', { label: L('Change from the final roll of the intensive revision to the draft of the summary revision, for every 100 electors on the final roll'), axis: L('Change for every 100 electors on the final roll'), fmt: pc,
      rows: calc.map(function (g) { return { name: g.state, v: g.per, col: g.draft.press ? '--fill-amber' : '--fill-navy' }; }) });
    var lo = Math.min.apply(null, calc.map(function (g) { return g.per; })), hi = Math.max.apply(null, calc.map(function (g) { return g.per; }));
    document.getElementById('nChange').textContent = L('A navy dot is a count from an official document and an amber dot a count from a press report.') + (same.length ? ' ' + L('{s} is left out, because its draft is reported as unchanged and no count of it has been found.', { s: and(same.map(function (g) { return g.state; })) }) : '');
    document.getElementById('fChange').innerHTML = '<b>' + L('The change runs from {a} to {b} for every 100 electors on the final roll.', { a: pc(lo), b: pc(hi) }) + '</b>';
  }

  // the table
  var notes = [];
  var cell = function (a, b) { return a + (b ? '<small>' + b + '</small>' : ''); };
  var rows = G.map(function (g) {
    var x = g.draft, pg = NW[g.state];
    var name = pg ? '<a href="../../' + E(pg.path) + '">' + nm(g) + '</a>' : nm(g);
    var base = g.base != null ? cell(SIR.n(g.base), D(g.baseDate)) : L('No final roll of the intensive revision');
    var dr = x ? cell(SIR.n(x.electors), L('Published on {d}', { d: D(x.date) }))
      : g.k === 'post' ? L('Postponed on {d}, no new date given', { d: D(g.postponed) })
      : g.k === 'late' ? L('Due on {d}, no count found', { d: D(g.due) }) : L('Due on {d}', { d: D(g.due) });
    var ch = '';
    if (x && g.c === 'calc') ch = cell((x.change > 0 ? '+' : x.change < 0 ? '−' : '') + SIR.n(Math.abs(x.change)), L('{p} for every 100', { p: pc(g.per) }));
    else if (x && g.c === 'same') ch = L('Reported as unchanged, no change worked out');
    else if (x && (x.added != null || x.deleted != null)) ch = x.added != null && x.deleted != null ? L('{a} added and {d} deleted, as reported', { a: SIR.n(x.added), d: SIR.n(x.deleted) }) : x.added != null ? L('{a} added, as reported', { a: SIR.n(x.added) }) : L('{d} deleted, as reported', { d: SIR.n(x.deleted) });
    var sex = x && x.men != null ? L('Men {m}, women {w}, third gender {t}', { m: SIR.n(x.men), w: SIR.n(x.women), t: SIR.n(x.third || 0) }) : x ? L('Not given') : '';
    if (x) {
      if (x.note) notes.push('<li id="sn-' + notes.length + '"><b>' + nm(g) + '.</b> ' + E(x.note) + '</li>');
      dr += '<small><a href="' + E(x.url) + '" rel="noopener" lang="en">' + E(x.site) + '</a>, ' + (x.press ? L('press report') : L('official document')) +
        (x.note ? ', <a href="#sn-' + (notes.length - 1) + '">' + L('note {n}', { n: notes.length }) + '</a>' : '') + '</small>';
    }
    var off = g.k === 'post';
    // one span a cell, so the phone layout keeps a figure and its line under it together
    return [name].concat([base, dr, ch, x ? cell(g.ratio != null ? SIR.n(g.ratio) : '', sex) : '', off ? '' : cell(D(g.claims_end), L('Final roll due on {d}', { d: D(g.final_due) }))]
      .map(function (v) { return v ? '<span style="overflow-wrap:anywhere">' + v + '</span>' : ''; }));
  });
  SIR.table('tSsr', [{ h: L('State or union territory') }, { h: L('Final roll, intensive revision') }, { h: L('Draft roll, summary revision') }, { h: L('Change from the final roll') },
    { h: L('Women per 1,000 men on the draft') }, { h: L('Claims and objections until') }], rows);
  document.getElementById('nDrafts').innerHTML = notes.join('');
  document.getElementById('nSsr').innerHTML = L('The dates are the latest each state\'s schedule gives. Where a revision was postponed, the dates that were put off are not shown.') + ' ' +
    L('Every order and change of dates, with its document, is on the page about <a href="../process/">how the revision was run</a>.');
  SIR.tools();
}).catch(SIR.fail);
