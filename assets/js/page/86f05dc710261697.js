SIR.json('data/india/process.json').then(function (P) {
  var T = P.timeline, E = SIR.esc;
  var WHO = { eci: 'Election Commission', sc: 'Supreme Court', ceo: 'State election officer' };
  // In short: every count below is taken from the data
  // a state's schedule changes are its orders after the first; a line drawn
  // from what the state actually published is not a change
  var moves = function (r) { return r.steps.filter(function (st) { return st.kind !== 'published'; }).length - 1; };
  var p2 = P.schedules.filter(function (r) { return r.phase === 'II'; });
  var p2twice = p2.filter(function (r) { return moves(r) > 1; }).length;
  var p3 = P.schedules.filter(function (r) { return r.phase === 'III'; });
  var p3moved = p3.filter(function (r) { return moves(r) > 0; }).length;
  var bySC = T.filter(function (t) { return t.who === 'sc'; }).length;
  SIR.inShort([
    'The revision began in Bihar on 24 June 2025 and by 14 May 2026 had been ordered everywhere except Himachal Pradesh, Jammu and Kashmir and Ladakh. Assam was given a different kind of revision.',
    'In Phase II, all ' + p2.length + ' states and union territories had their dates moved a week, and the Commission named ' + p2twice + ' of them for a second move. In Phase III, the dates of ' + p3moved + ' of ' + p3.length + ' states and union territories moved by the orders and notes on this page.',
    'What an elector had to show changed as the revision went on. In June 2025 it was one of eleven documents, and Aadhaar was added for identity on the Supreme Court\'s order in September. In Phase II no documents were asked for while forms were filled in. From 26 September 2026, documents were collected at home from those sent notices.',
    bySC + ' of the ' + T.length + ' entries below are orders or the judgment of the Supreme Court. In West Bengal it had judges decide the claims, and 60,06,675 names were marked under adjudication on the final roll.',
    'The Indian Express reported that two of the three Election Commissioners objected on record at least 14 times in 10 months to decisions taken in the Commission\'s name without them, on Form 6, on who controls the roll software, and on appeals in West Bengal. Three days after calling the notes part of its decision-making, the Commission announced nine decisions that met several of them. <a href="#inside-the-commission">Inside the Commission</a> sets the account out by date.'
  ], 'Every section rests on documents issued by the Election Commission, the Supreme Court and the states\' election officers, except the list of press reports, which is marked as such. Some orders could not be found, and they are listed at the foot of the page.');

  document.getElementById('kpis').innerHTML = [
    [T.length, 'rule and schedule changes, each with its document'],
    [P.schedules.length, 'states and union territories with dates drawn'],
    [P.schedules.reduce(function (n, r) { return n + moves(r); }, 0), 'times a state\'s dates were changed, in the orders and notes on this page'],
    [P.gaps.length, 'documents that could not be found or questions still open']
  ].map(function (k) { return '<div><b>' + k[0] + '</b><span>' + k[1] + '</span></div>'; }).join('');

  // the timeline
  // each entry has its own address, #t-<date>, so a link opens on it
  var seen = {};
  T.forEach(function (t) { var k = 't-' + t.date; seen[k] = (seen[k] || 0) + 1; t.id = k + (seen[k] > 1 ? '-' + seen[k] : ''); });
  var tl = document.getElementById('timeline'), fw = '', fp = '';
  function draw() {
    var lastY = '';
    tl.innerHTML = T.filter(function (t) { return (!fw || t.who === fw) && (!fp || t.phase === fp); }).map(function (t) {
      var y = t.date.slice(0, 4), head = y !== lastY ? '<li class="pyear" aria-hidden="true">' + y + '</li>' : '';
      lastY = y;
      return head + '<li class="pitem ' + t.who + '"><div class="pdate"><time datetime="' + t.date + '">' + SIR.date(t.date) + '</time><span class="pwho">' + WHO[t.who] + ' · ' + E(t.phase) + '</span></div>' +
        '<div class="pbody"><h3 id="' + t.id + '">' + E(t.title) + '</h3><p>' + E(t.text) + '</p><p class="psrc">' + t.src.map(function (s) { return '<a href="' + E(s.url) + '" rel="noopener" target="_blank">' + E(s.name) + '</a>'; }).join(' · ') + '</p></div></li>';
    }).join('') || '<li class="pitem"><div class="pbody"><p>Nothing matches both choices.</p></div></li>';
    SIR.anchors(tl);
  }
  document.querySelectorAll('.pfilter .chip').forEach(function (b) {
    b.addEventListener('click', function () {
      var grp = b.hasAttribute('data-who') ? 'data-who' : 'data-ph';
      document.querySelectorAll('.pfilter .chip[' + grp + ']').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      if (grp === 'data-who') fw = b.getAttribute('data-who'); else fp = b.getAttribute('data-ph');
      draw();
    });
  });
  draw();

  // what made it harder to stay on the roll
  var srcs = function (a) { return '<p class="psrc">' + (a || []).map(function (x) { return '<a href="' + E(x.url) + '"' + (x.url.charAt(0) === '#' ? '' : ' rel="noopener" target="_blank"') + '>' + E(x.name) + '</a>'; }).join(' · ') + '</p>'; };
  // the burdens carry {placeholders} for counts taken from the schedules and,
  // once the state table is in, from the claims and objections after the draft
  var fill = { p2_states: p2.length, p2_again: p2twice, p3_states: p3.length, p3_moved: p3moved };
  var drawBurdens = function () {
    document.getElementById('burdens').innerHTML = P.burdens.filter(function (b) { return !/\{claims_/.test(b.text) || fill.claims_states != null; }).map(function (b) {
      return '<li><h3>' + E(b.title) + '</h3><p>' + E(b.text.replace(/\{(\w+)\}/g, function (m, k) { return fill[k]; })) + '</p>' + srcs(b.src) + '</li>';
    }).join('');
  };
  drawBurdens();

  // Form 6, Form 7 and the declaration
  var fl = document.getElementById('forms'), lastFY = '';
  fl.innerHTML = P.forms.map(function (t, i) {
    var y = t.date.slice(0, 4), head = y !== lastFY ? '<li class="pyear" aria-hidden="true">' + y + '</li>' : '';
    lastFY = y;
    return head + '<li class="pitem ' + t.who + '"><div class="pdate"><time datetime="' + t.date + '">' + SIR.date(t.date) + '</time><span class="pwho">' + WHO[t.who] + '</span></div>' +
      '<div class="pbody"><h3 id="f-' + t.date + '-' + (i + 1) + '">' + E(t.title) + '</h3><p>' + E(t.text) + '</p>' + srcs(t.src) + '</div></li>';
  }).join('');
  SIR.anchors(fl);

  // inside the Commission: The Indian Express's account, by date
  var I = P.inside, LT = { ecs: '--fill-red', officers: '--fill-purple', commission: '--fill-navy', goa: '--fill-amber', court: '--fill-teal', press: '--fill-grey' };
  var IL = I.lanes.map(function (l) { return [l[0], l[1], LT[l[0]]]; }), lname = {}; I.lanes.forEach(function (l) { lname[l[0]] = l[1]; });
  var nE = I.events.filter(function (e) { return e.lane === 'ecs'; }).length, G = I.goa, W = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'];
  document.getElementById('iSub').textContent = 'Two of the three Election Commissioners, Sukhbir Singh Sandhu and Vivek Joshi, put objections on file that the Chief Election Commissioner was copied on. ' + I.note + ' The chart puts each dated note, letter and reply in its own lane, and the numbers match the list under it.';
  VIZ.lanes('vInside', { label: 'The Indian Express\'s account of the objections inside the Election Commission, November 2025 to October 2026', lanes: IL, dark: ['--fill-amber', '--fill-teal', '--fill-grey'], events: I.events });
  document.getElementById('fInside').innerHTML = '<b>The paper dated ' + nE + ' of the two Commissioners\' notes and letters. It says there were at least 14.</b> They asked for Form 6 to stay as the law sets it, for the officers who keep each constituency\'s roll to keep control of it in the software, and for an outside audit of that software. In Goa, ' + W[G.messages] + ' messages in ' + W[G.days] + ' days asked for a way to put back ' + G.eligible + ' electors the state\'s officers had heard and found eligible, and the final roll went out without them. By 26 September, the Commission said, ' + G.filled_form6 + ' of them had applied again on Form 6.';
  document.getElementById('inside').innerHTML = I.events.map(function (e, i) {
    return '<li class="pitem ilane ' + e.lane + '"><div class="pdate"><b class="inum">' + (i + 1) + '</b> <time datetime="' + e.date + '">' + SIR.date(e.date) + '</time><span class="pwho">' + E(lname[e.lane]) + '</span></div>' +
      '<div class="pbody"><h3 id="i-' + (i + 1) + '">' + E(e.title) + '</h3><p>' + E(e.text) + '</p><p class="psrc">' + (e.url ? '<a href="' + E(e.url) + '" rel="noopener" target="_blank">' + E(e.outlet) + ', ' + E(e.headline) + '</a>' : E(e.headline)) + '</p></div></li>';
  }).join('');
  SIR.anchors(document.getElementById('inside'));
  document.getElementById('nInside').innerHTML = E(I.issue) + ' <a href="../../' + E(I.pdf.url) + '">' + E(I.pdf.label) + '</a>. ' + E(I.pdf.rights) + ' The Commission did not answer the questions the paper sent on 21 September. What it said in public is in entries ' + (I.events.map(function (e, i) { return e.lane === 'commission' && e.date >= '2026-09-23' ? i + 1 : 0; }).filter(Boolean).join(', ').replace(/, (\d+)$/, ' and $1')) + '. The press reports further down carry the same account by topic, with the responses each report gave.';

  // the reported list, by topic
  var R = P.reported, rt = '', rbox = document.getElementById('reported');
  var topics = []; R.forEach(function (r) { if (topics.indexOf(r.topic) < 0) topics.push(r.topic); });
  document.getElementById('rFilter').innerHTML = '<button type="button" class="chip" data-t="" aria-pressed="true">Everything</button>' +
    topics.map(function (t) { return '<button type="button" class="chip" data-t="' + E(t) + '" aria-pressed="false">' + E(t) + '</button>'; }).join('');
  function drawR() {
    rbox.innerHTML = topics.filter(function (t) { return !rt || t === rt; }).map(function (t) {
      return '<h3 class="ph">' + E(t) + '</h3><ul class="reported">' + R.filter(function (r) { return r.topic === t; }).map(function (r) {
        return '<li><p class="rmeta"><b>' + E(r.outlet) + '</b>, <time datetime="' + r.date + '">' + SIR.date(r.date) + '</time></p><p>' + E(r.text) + '</p>' +
          (r.response ? '<p class="rresp"><span>The response reported</span> ' + E(r.response) + '</p>' : '') +
          '<p class="psrc"><a href="' + E(r.url) + '" rel="noopener" target="_blank">' + E(r.headline) + '</a></p></li>';
      }).join('') + '</ul>';
    }).join('');
  }
  document.getElementById('rFilter').addEventListener('click', function (e) {
    var b = e.target.closest('.chip'); if (!b) return;
    rt = b.getAttribute('data-t');
    document.querySelectorAll('#rFilter .chip').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
    drawR();
  });
  drawR();

  // claims and objections after the draft, from the All India figures
  SIR.json('data/india/states.json').then(function (S) {
    var N = function (v) { return v == null ? '' : SIR.n(v); };
    var rows = S.states.filter(function (r) { return r.removed && r.added_after_draft != null; })
      .map(function (r) { return { s: r.state, rm: r.removed, ad: r.added_after_draft, ra: r.removed_after_draft, per: 100 * r.added_after_draft / r.removed }; })
      .sort(function (a, b) { return a.per - b.per; });
    VIZ.lollipop('vClaims', { label: 'Names added after the draft for every 100 removed at it, by state', axis: 'Added after the draft, per 100 removed at it',
      rows: rows.map(function (r) { return { name: r.s, v: r.per, text: r.per.toFixed(1), tok: r.per < 10 ? '--fill-red' : '--fill-navy', hi: r.per < 10 }; }) });
    document.getElementById('tClaims').innerHTML = '<thead><tr><th scope="col" class="l">State</th><th scope="col">Added per 100 removed</th><th scope="col">Removed at draft</th><th scope="col">Added after</th><th scope="col">Removed after</th></tr></thead><tbody>' +
      rows.map(function (r) { return '<tr><th scope="row" class="l">' + E(r.s) + '</th><td>' + r.per.toFixed(1) + '</td><td>' + N(r.rm) + '</td><td>' + N(r.ad) + '</td><td>' + N(r.ra) + '</td></tr>'; }).join('') + '</tbody>';
    var low = rows.filter(function (r) { return r.per < 10; }).length;
    fill.claims_states = rows.length; fill.claims_fewer = rows.filter(function (r) { return r.per < 100; }).length; fill.claims_under10 = low;
    fill.claims_lead = fill.claims_fewer === fill.claims_states ? 'All ' + fill.claims_states + ' states that published both counts' : fill.claims_fewer + ' of the ' + fill.claims_states + ' states that published both counts';
    drawBurdens();
    document.getElementById('nClaims').innerHTML = 'In ' + low + ' of these ' + rows.length + ' states and union territories, fewer than 10 names were added after the draft for every 100 removed at it. ' + E(P.claims_note) + ' The other states published only the net change from draft to final, or no final roll yet, and are on the <a href="../">All India page</a>.' + srcs(P.claims_src);
    SIR.tools();
  }).catch(function () {});

  // notices: electors kept on the draft but sent a notice
  SIR.json('data/india/notices.json').then(function (T) {
    var N = function (v) { return v == null ? '' : SIR.n(v); }, lk = function (v) { return v >= 1e7 ? (v / 1e7).toFixed(2) + ' crore' : (v / 1e5).toFixed(1) + ' lakh'; };
    var R = T.states.filter(function (r) { return r.per_100 != null; });
    VIZ.lollipop('vNotices', { label: 'Electors sent a notice for every 100 on the draft roll, by state', axis: 'Notices per 100 electors on the draft roll',
      rows: R.map(function (r) { return { name: r.state, v: r.per_100, text: r.per_100.toFixed(1) + (r.rounded ? '*' : ''), tok: r.kind === 'primary' ? '--fill-navy' : '--fill-amber', hi: r.kind === 'primary' }; }) });
    var both = R.filter(function (r) { return r.no_mapping != null && r.discrepancy != null; }), moreD = both.filter(function (r) { return r.discrepancy > r.no_mapping; });
    document.getElementById('fNotices').innerHTML = '<b>Across the ' + T.with_total + ' states with a published total, ' + lk(T.notices_total) + ' electors on the draft rolls were sent a notice, ' + T.per_100.toFixed(1) + ' of every 100.</b> ' + R[0].state + ' sent the most for its size, ' + R[0].per_100.toFixed(1) + ' per 100, and ' + R[R.length - 1].state + ' the fewest, ' + R[R.length - 1].per_100.toFixed(1) + '. Of the ' + both.length + ' states that gave the two lists, the discrepancy list was the larger in ' + moreD.length + '. Only ' + T.primary + ' of the totals come from a Chief Electoral Officer\'s or a court\'s own document.';
    var how = function (r) { return r.how === 'sum' ? 'sum of the two lists' : r.how ? 'published total' : ''; };
    document.getElementById('tNotices').innerHTML = '<thead><tr><th scope="col" class="l">State</th><th scope="col">Notices</th><th scope="col">Per 100 on the draft</th><th scope="col">No mapping</th><th scope="col">Discrepancy list</th><th scope="col">Deleted after a notice</th><th scope="col" class="l">Total is</th><th scope="col" class="l">Source</th></tr></thead><tbody>' +
      T.states.map(function (r) { return '<tr><th scope="row" class="l">' + E(r.state) + '</th><td>' + N(r.notices) + (r.rounded ? '*' : '') + '</td><td>' + (r.per_100 == null ? '' : r.per_100.toFixed(1)) + '</td><td>' + N(r.no_mapping) + '</td><td>' + N(r.discrepancy) + '</td><td>' + N(r.deleted_after_notice) + (r.deleted_kind === 'press' && r.kind === 'primary' ? '†' : '') + '</td><td class="l">' + how(r) + '</td><td class="l">' + (r.source_url ? '<a href="' + E(r.source_url) + '">' + (r.kind === 'primary' ? 'document' : 'press') + '</a>' : (r.lists_source ? '<a href="' + E(r.lists_source) + '">press</a>' : '')) + '</td></tr>'; }).join('') + '</tbody>';
    document.getElementById('nNotices').innerHTML = 'An asterisk marks a figure published rounded, in lakh or crore. Most phase 3 figures are running counts, taken while notices were still being heard. An elector can be on both lists, so the two need not add up to the total. In Uttar Pradesh two press reports split the same 3.26 crore differently, and the split used here, from The Times of India, is the one that adds up. West Bengal\'s total is the Supreme Court\'s reading of the record on 19 January 2026. The court\'s order gives only the discrepancy list, and the two lists are always taken from one source, so West Bengal\'s come from an earlier Commission breakdown reported by the press. A dagger marks a figure in a row whose total rests on a document but which came through the press. West Bengal\'s deletions are the adjudication outcome as The Indian Express reported it on 7 April 2026. A state with only one list, or two reports that disagree, has no total here. Deleted after a notice counts names struck off for not answering or for failing the hearing, where a state reported it, and many of these are interim. In Hyderabad\'s Old City the two lists can be told apart polling part by polling part, on the <a href="../../hyderabad/hearings/">hearings page</a>. The download gives every figure with its date and source.';
    SIR.tools();
  }).catch(function () {});

  // the schedules
  // #s-<state> (a link from a state's page) outlines that state's row
  var key = function (n) { return 's-' + n.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''); };
  var G = function (id, rows, label, mark) {
    VIZ.gantt(id, { label: label, mark: mark, rows: rows.map(function (r) { return { name: r.state, steps: r.steps }; }) });
  };
  var drawG = function () {
    var h = SIR.hashId(), hit = null;
    P.schedules.forEach(function (r) { if (key(r.state) === h) hit = r; });
    var m = hit && hit.state;
    G('vG1', P.schedules.filter(function (r) { return r.phase === 'I'; }), 'Bihar\'s schedule, from the order of 24 June 2025', m);
    G('vG2', p2, 'Phase II schedules, as set on 27 October 2025 and as moved', m);
    G('vG3', p3, 'Phase III schedules, as set on 14 May 2026 and as moved', m);
    if (hit) { var pn = document.getElementById({ I: 'pG1', II: 'pG2', III: 'pG3' }[hit.phase]); if (pn) pn.scrollIntoView({ block: 'start' }); }
  };
  drawG();
  window.addEventListener('hashchange', drawG);
  document.getElementById('nG2').textContent = 'The release of 11 December 2025 names Gujarat both among the states moved to a draft on 19 December and among those keeping 16 December, and does not name Puducherry. ' + P.notes.p2final;
  document.getElementById('nG3').textContent = P.notes.p3later + ' ' + P.notes.tripura + ' ' + P.notes.uttarakhand;
  document.getElementById('gaps').innerHTML = P.gaps.map(function (g) { return '<li>' + E(g) + '</li>'; }).join('');
  document.getElementById('asof').textContent = SIR.date(P.as_of);
  SIR.tools();
}).catch(SIR.fail);
