SIR.json('data/india/process.json').then(function (P) {
  var T = P.timeline, E = SIR.esc;
  // an SVG element, for the two charts drawn on this page alone
  var mk = function (tag, attrs, parent, text) {
    var e = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (var k in attrs) if (attrs[k] != null) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    if (parent) parent.appendChild(e);
    return e;
  };
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
  ], 'Every section rests on documents issued by the Election Commission, the Supreme Court and the states\' election officers, except the census note, which rests on the Registrar General\'s notifications, and the list of press reports, which is marked as such. Some orders could not be found, and they are listed at the foot of the page.');

  document.getElementById('kpis').innerHTML = [
    [T.length, 'rule and schedule changes, each with its document'],
    [P.schedules.length, 'states and union territories with dates drawn'],
    [P.schedules.reduce(function (n, r) { return n + moves(r); }, 0), 'times a state\'s dates were changed, in the orders and notes on this page'],
    [P.gaps.length, 'documents that could not be found or questions still open']
  ].map(function (k) { return '<div><b>' + k[0] + '</b><span>' + k[1] + '</span></div>'; }).join('');

  // the census dates beside the summary revision, a dated note from the
  // Registrar General's notifications
  var C = P.census;
  document.getElementById('nCensus').innerHTML = 'Census dates as notified by <time datetime="' + C.date + '">' + SIR.date(C.date) + '</time>. ' + E(C.text) + ' ' +
    C.src.map(function (s) { return '<a href="' + E(s.url) + '" rel="noopener" target="_blank">' + E(s.name) + '</a>'; }).join(' · ');

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
    VIZ.lollipop('vClaims', { label: 'Names added after the draft for every 100 left off it, by state', axis: 'Added after the draft, per 100 left off it',
      rows: rows.map(function (r) { return { name: r.s, v: r.per, text: r.per.toFixed(1), tok: r.per < 10 ? '--fill-red' : '--fill-navy', hi: r.per < 10 }; }) });
    document.getElementById('tClaims').innerHTML = '<thead><tr><th scope="col" class="l">State</th><th scope="col">Added per 100 left off</th><th scope="col">Left off the draft</th><th scope="col">Added after</th><th scope="col">Deleted after</th></tr></thead><tbody>' +
      rows.map(function (r) { return '<tr><th scope="row" class="l">' + E(r.s) + '</th><td>' + r.per.toFixed(1) + '</td><td>' + N(r.rm) + '</td><td>' + N(r.ad) + '</td><td>' + N(r.ra) + '</td></tr>'; }).join('') + '</tbody>';
    var low = rows.filter(function (r) { return r.per < 10; }).length;
    fill.claims_states = rows.length; fill.claims_fewer = rows.filter(function (r) { return r.per < 100; }).length; fill.claims_under10 = low;
    fill.claims_lead = fill.claims_fewer === fill.claims_states ? 'All ' + fill.claims_states + ' states that published both counts' : fill.claims_fewer + ' of the ' + fill.claims_states + ' states that published both counts';
    drawBurdens();
    document.getElementById('nClaims').innerHTML = 'In ' + low + ' of these ' + rows.length + ' states and union territories, fewer than 10 names were added after the draft for every 100 left off it. ' + E(P.claims_note) + ' The other states published only the net change from draft to final, or no final roll yet, and are on the <a href="../">All India page</a>.' + srcs(P.claims_src);
    SIR.tools();
  }).catch(function () {});

  // bulk Form 7 filings, state by state, each row linked to its reports on the disputes page
  SIR.json('data/india/form7_bulk.json').then(function (B) {
    var C = B.counts, ST = {}, ctx = B.context;
    B.status.forEach(function (s) { ST[s[0]] = s[1]; });
    document.getElementById('nBulkRule').innerHTML = '<b>Two rules of the Commission apply to Form 7 filed in bulk.</b> ' + E(ctx.order.text.replace(/\.$/, '')) + ' (<a href="' + E(ctx.order.src.url) + '" rel="noopener" target="_blank">the Commission\'s letter of ' + SIR.date(ctx.order.date) + '</a>). ' +
      E(ctx.letter.text.replace(/\.$/, '')) + ' (<a href="../disputes/#d-' + E(ctx.letter.id) + '">the report</a>).';
    var count = function (r) {
      if (r.count == null) return '';
      return (r.count_q ? r.count_q + ' ' : '') + SIR.n(r.count) + (r.count_to ? ' to ' + SIR.n(r.count_to) : '') + ' ' + r.unit;
    };
    // one year is written once: 24 January to 11 February 2026
    var when = function (r) {
      if (r.first === r.last) return SIR.date(r.first);
      var a = SIR.date(r.first);
      return (r.first.slice(0, 4) === r.last.slice(0, 4) ? a.replace(/\s*\d{4}$/, '') : a) + ' to ' + SIR.date(r.last);
    };
    var row = function (r) {
      var what = (r.status.length ? '<span class="btags">' + r.status.map(function (s) { return '<span>' + E(ST[s]) + '</span>'; }).join('') + '</span>' : '') +
        (r.outcomes.length ? r.outcomes.map(function (o) { return E(o.text); }).join(' ') : (r.status.length ? '' : 'No outcome reported.'));
      return '<tr id="b-' + E(r.id) + '"><th scope="row" class="l">' + E(r.state) + '</th><td class="l">' + E(r.place) + '</td><td class="l nw">' + when(r) + '</td><td class="nw">' + count(r) + '</td><td class="l">' + E(r.filer) + '</td><td class="l">' + what + '</td><td class="l">' +
        r.entries.map(function (e) { return '<a href="../disputes/#d-' + E(e.id) + '">' + E(e.outlet) + ', ' + SIR.date(e.date) + '</a>'; }).join('<br>') + '</td></tr>';
    };
    var part = function (g, label) {
      var rs = B.rows.filter(function (r) { return r.group === g; });
      return rs.length ? '<tbody><tr class="bgroup"><th scope="colgroup" colspan="7" class="l">' + label + '</th></tr>' + rs.map(row).join('') + '</tbody>' : '';
    };
    document.getElementById('tBulk').innerHTML = '<thead><tr><th scope="col" class="l">State</th><th scope="col" class="l">Place</th><th scope="col" class="l">Reported</th><th scope="col">How many</th><th scope="col" class="l">Filed by</th><th scope="col" class="l">What happened</th><th scope="col" class="l">Reports</th></tr></thead>' +
      part('', 'Form 7 objections filed in bulk by people') +
      part('officers', 'Form 7s generated in registration officers\' names, which no person filed as an objector');
    document.getElementById('nBulk').textContent = 'The first part holds ' + C.rows + ' reports of bulk filing from ' + C.states + ' states and union territories, and ' + C.with_count + ' of them give a count. Of the ' + C.rows + ', ' +
      C.police + ' led to a police case or FIR and ' + C.court + ' came before a court. The counts cannot be added up, because some count forms and some count the electors objected to. The ' + C.officers + ' counts of forms in officers\' names are set apart from the rest because the reports say the software produced them.';
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
    document.getElementById('nNotices').innerHTML = 'An asterisk marks a figure published rounded, in lakh or crore. Most phase 3 figures are running counts, taken while notices were still being heard. An elector can be on both lists, so the two need not add up to the total. In Uttar Pradesh two press reports split the same 3.26 crore differently, and the split used here, from The Times of India, is the one that adds up. West Bengal\'s total is the Supreme Court\'s reading of the record on 19 January 2026. The court\'s order gives only the discrepancy list, and the two lists are always taken from one source, so West Bengal\'s come from an earlier Commission breakdown reported by the press. A dagger marks a figure in a row whose total rests on a document but which came through the press. West Bengal\'s deletions are the adjudication outcome as The Indian Express reported it on 7 April 2026. A state with only one list, or two reports that disagree, has no total here. Deleted after a notice counts names deleted for not answering or for failing the hearing, where a state reported it, and many of these are interim. In Hyderabad\'s Old City the two lists can be told apart polling part by polling part, on the <a href="../../hyderabad/hearings/">hearings page</a>. The download gives every figure with its date and source.';

    // the hearings: the latest counts by state, and how they moved where a
    // state published them on three dates or more
    var LATEST = function (r, c) { var a = r.series.filter(function (x) { return x.category === c; }); return a.length ? a[a.length - 1] : null; };
    var src = function (u, kind) { return u ? ' <a href="' + E(u) + '" rel="noopener" target="_blank">' + (kind === 'primary' ? 'document' : 'press') + '</a>' : ''; };
    var cnt = function (x) { return x ? SIR.n(x.count) + (x.rounded ? '*' : '') : ''; };
    var HR = T.states.filter(function (r) { return LATEST(r, 'hearings_held') || LATEST(r, 'deleted_after_notice'); })
      .sort(function (a, b) { return a.state < b.state ? -1 : 1; });
    document.getElementById('tHear').innerHTML = '<thead><tr><th scope="col" class="l">State</th><th scope="col">Notices sent</th><th scope="col" class="l">As of</th><th scope="col">Hearings held</th><th scope="col" class="l">As of</th><th scope="col">Deleted after a notice</th><th scope="col" class="l">As of</th></tr></thead><tbody>' +
      HR.map(function (r) {
        var h = LATEST(r, 'hearings_held'), d = LATEST(r, 'deleted_after_notice');
        return '<tr><th scope="row" class="l">' + E(r.state) + '</th><td>' + N(r.notices) + (r.rounded ? '*' : '') + '</td><td class="l">' + (r.date ? SIR.date(r.date) + src(r.source_url, r.kind) : '') + '</td>' +
          '<td>' + cnt(h) + '</td><td class="l">' + (h ? SIR.date(h.date) + src(h.source_url, h.kind) : '') + '</td>' +
          '<td>' + cnt(d) + '</td><td class="l">' + (d ? SIR.date(d.date) + src(d.source_url, d.kind) : '') + '</td></tr>';
      }).join('') + '</tbody>';
    var ndates = function (r) { var o = {}; r.series.forEach(function (x) { if (x.category !== 'all_notices') o[x.date] = 1; }); return Object.keys(o).length; };
    var TR = HR.filter(function (r) { return ndates(r) >= 3; });
    // the finding: the latest counts against the notices sent
    var per = function (x, r) { return x && r.notices ? 100 * x.count / r.notices : null; };
    var withH = TR.filter(function (r) { return per(LATEST(r, 'hearings_held'), r) != null; });
    var withD = TR.filter(function (r) { return per(LATEST(r, 'deleted_after_notice'), r) != null; });
    var andList = function (a) { return a.join(', ').replace(/, ([^,]*)$/, ' and $1'); };
    document.getElementById('fHear').innerHTML = '<b>By the latest counts, hearings had been held for ' + andList(withH.map(function (r, i) { var h = LATEST(r, 'hearings_held'); return Math.min(100, per(h, r)).toFixed(1) + (i ? '' : ' of every 100 electors sent a notice') + ' in ' + E(r.state) + ' by ' + SIR.date(h.date); })) + '.</b> ' +
      'For every 100 electors sent a notice, the names deleted after it numbered ' + andList(withD.map(function (r) { var d = LATEST(r, 'deleted_after_notice'); return per(d, r).toFixed(2) + ' in ' + E(r.state) + ' by ' + SIR.date(d.date); })) + '.';
    document.getElementById('nHear').innerHTML = 'An asterisk marks a figure published rounded, in lakh or crore, or as "about" or "over". Most of these are running counts, taken while notices were still being heard, and a later count replaces an earlier one. Where two reports give the same day, the one from a document is shown, or else the exact one. The word for a hearing varies. Karnataka counted house visits from 26 September, and the Delhi reports speak of electors verified or resolved. Deleted after a notice counts names deleted for not answering or for failing the hearing. Notices sent are the figures in the table above, and a hearing count can run a little past them when the two come from different reports. A share above 100 is shown as 100.';
    drawTrack('vHear', TR, 'Hearings held and names deleted after a notice, by date, in the states that published them on three dates or more');
    function drawTrack(id, rows, label) {
      var box = document.getElementById(id); if (!box || !rows.length) return;
      var cw = box.clientWidth || innerWidth, ph = cw < 600, W = ph ? Math.max(320, Math.min(cw, 599)) : Math.max(600, Math.min(cw, 1100));
      var cols = ph ? 1 : 2, pw = (W - (cols - 1) * 24) / cols, plotH = ph ? 92 : 100, capH = 18, headH = 24, rgt = 74, lft = 6;
      var MS = { hearings_held: ['Hearings held', '--fill-navy'], deleted_after_notice: ['Deleted after a notice', '--fill-red'] };
      var D = function (iso) { return Date.parse(iso + 'T00:00:00Z'); };
      var all = []; rows.forEach(function (r) { r.series.forEach(function (x) { if (x.category !== 'all_notices') all.push(D(x.date)); }); });
      var t0 = Math.min.apply(null, all) - 2 * 864e5, t1 = Math.max.apply(null, all) + 2 * 864e5;
      var block = cols === 2 ? headH + capH + plotH + 30 : headH + 2 * (capH + plotH + 30);
      var H = 6 + rows.length * block, s = mk('svg', { viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': label, class: 'viz', preserveAspectRatio: 'xMidYMid meet' });
      box.innerHTML = ''; box.appendChild(s); mk('title', {}, s, label);
      var mon = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      var csv = [['state', 'measure', 'date', 'count', 'rounded', 'source', 'url']];
      rows.forEach(function (r, ri) {
        var y0 = 6 + ri * block;
        if (ri) mk('line', { x1: 0, x2: W, y1: y0 - 4, y2: y0 - 4, class: 'vgrid' }, s);
        mk('text', { x: 0, y: y0 + 14, class: 'vname' }, s, r.state);
        ['hearings_held', 'deleted_after_notice'].forEach(function (c, ci) {
          var px = cols === 2 ? ci * (pw + 24) : 0, py = y0 + headH + (cols === 2 ? 0 : ci * (capH + plotH + 30));
          var pts = r.series.filter(function (x) { return x.category === c; });
          mk('text', { x: px, y: py + 12, class: 'vval' }, s, MS[c][0]);
          var top = py + capH + 4, bot = top + plotH, x0 = px + lft, x1 = px + pw - rgt;
          mk('rect', { x: px, y: top - 4, width: pw, height: plotH + 8, rx: 6, class: 'vpanel' }, s);
          var ref = c === 'hearings_held' && r.notices ? r.notices : null;
          var mx = Math.max.apply(null, pts.map(function (x) { return x.count; }).concat(ref ? [ref] : [1])) * 1.08;
          var X = function (iso) { return x0 + (x1 - x0) * (D(iso) - t0) / (t1 - t0); }, Y = function (v) { return bot - (bot - top) * v / mx; };
          // a tick on the first and the fifteenth of each month
          for (var t = new Date(t0); t.getTime() <= t1; t = new Date(t.getTime() + 864e5)) {
            if (t.getUTCDate() !== 1 && t.getUTCDate() !== 15) continue;
            var tx = X(t.toISOString().slice(0, 10));
            mk('line', { x1: tx, x2: tx, y1: top - 4, y2: bot + 4, class: 'vgrid' }, s);
            mk('text', { x: tx, y: bot + 18, 'text-anchor': 'middle', class: 'vval small' }, s, t.getUTCDate() + ' ' + mon[t.getUTCMonth()]);
          }
          mk('line', { x1: x0, x2: x1, y1: bot, y2: bot, class: 'vzero' }, s);
          if (ref) {
            mk('line', { x1: x0, x2: x1, y1: Y(ref), y2: Y(ref), class: 'vgrid', 'stroke-dasharray': '5 4', style: 'stroke:var(--muted)' }, s);
            mk('text', { x: x1 + 6, y: Y(ref), 'dominant-baseline': 'middle', class: 'vval small' }, s, 'sent ' + SIR.lk(ref));
          }
          if (!pts.length) { mk('text', { x: (x0 + x1) / 2, y: (top + bot) / 2, 'text-anchor': 'middle', 'dominant-baseline': 'middle', class: 'vval' }, s, 'No count published'); return; }
          if (pts.length > 1) mk('path', { d: pts.map(function (x, k) { return (k ? 'L' : 'M') + X(x.date) + ',' + Y(x.count); }).join(' '), class: 'vline', style: 'stroke:var(' + MS[c][1] + ');stroke-width:2' }, s);
          pts.forEach(function (x) {
            var dot = mk('circle', { cx: X(x.date), cy: Y(x.count), r: 4, style: x.kind === 'primary' ? 'fill:var(' + MS[c][1] + ')' : 'fill:var(--card);stroke:var(' + MS[c][1] + ');stroke-width:2' }, s);
            mk('title', {}, dot, r.state + ', ' + MS[c][0].toLowerCase() + ', ' + SIR.date(x.date) + ', ' + SIR.n(x.count) + (x.rounded ? ' (rounded)' : '') + (x.kind === 'primary' ? ', from a document' : ', from a press report'));
            csv.push([r.state, MS[c][0], x.date, x.count, x.rounded ? 'yes' : 'no', x.kind, x.source_url]);
          });
          var last = pts[pts.length - 1], lv = last.count >= 1e5 ? SIR.lk(last.count) : SIR.n(last.count);
          var ly = Y(last.count) + (ref && Math.abs(Y(last.count) - Y(ref)) < 12 ? 13 : 0);
          mk('text', { x: x1 + 6, y: ly, 'dominant-baseline': 'middle', class: 'vval' }, s, lv);
        });
      });
      box.__csv = csv;
    }
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
  // how each state's final roll date moved: every revision that set a final
  // date, in order, the dates the press reported and no order confirms, and
  // the day the final roll was published
  SIR.json('data/india/states.json').then(function (SJ) {
    var SS = {}; SJ.states.forEach(function (r) { SS[r.state] = r; });
    var DOC = function (u) { return /^https?:\/\/[^\/]*\.(gov|nic)\.in(\/|$)/.test(u || ''); };
    var on = function (lbl) { var m = /(\d\d)\.(\d\d)\.(\d{4})/.exec(lbl || ''); return m ? m[3] + '-' + m[2] + '-' + m[1] : null; };
    var day = function (a, b) { return Math.round((Date.parse(b) - Date.parse(a)) / 864e5); };
    var hist = P.schedules.map(function (sc) {
      var pts = [], last = '';
      sc.steps.forEach(function (st) {
        if (st.kind === 'published') return;
        last = on(st.label) || last;
        if (st.final) pts.push({ on: last, final: st.final, label: st.label, url: st.src, press: !DOC(st.src) });
      });
      (P.reported_dates || []).filter(function (d) { return d.state === sc.state && d.final; }).sort(function (a, b) { return a.date < b.date ? -1 : 1; }).forEach(function (d) {
        var at = 0; pts.forEach(function (p, k) { if (p.on <= d.date) at = k + 1; });
        pts.splice(at, 0, { on: d.date, final: d.final, label: 'Reported on ' + SIR.date(d.date) + ' by ' + d.outlet, url: d.url, press: true });
      });
      // a revision that left the final date where it was is not a move
      var kept = [];
      pts.forEach(function (p) { if (!kept.length || p.final !== kept[kept.length - 1].final) kept.push(p); });
      var s = SS[sc.state] || {}, pub = null;
      if (s.electors_final != null && s.final_date) pub = { final: s.final_date, label: 'Final roll published', url: s.final_source && s.final_source.url, press: !(s.final_source && s.final_source.source === 'primary'), pub: true };
      else sc.steps.forEach(function (st) { if (st.kind === 'published' && st.final) pub = { final: st.final, label: st.label, url: st.src, press: !DOC(st.src), pub: true }; });
      var all = kept.concat(pub ? [pub] : []);
      all.forEach(function (p, k) { p.n = k + 1; });
      var end = all.length ? all[all.length - 1].final : null;
      return { name: sc.state, phase: sc.phase, pts: all, moves: Math.max(0, kept.length - 1), first: kept.length ? kept[0].final : null, end: end,
        days: kept.length && end ? day(kept[0].final, end) : 0, late: pub && kept.length ? day(kept[kept.length - 1].final, pub.final) : 0, done: !!pub };
    });
    var tag = function (p) { return p.press ? ' (reported in the press)' : ''; };
    var shown = function (ph) { return hist.filter(function (h) { return h.phase === ph && (h.moves > 0 || h.late !== 0); }); };
    drawMoves('vM2', shown('II'), 'Phase II, the final roll date set by each revision and the day the final roll was published');
    drawMoves('vM3', shown('III'), 'Phase III, the final roll date set by each revision and the day the final roll was published');
    var set = hist.filter(function (h) { return h.first; }), moved = set.filter(function (h) { return h.moves > 0; }), later = set.filter(function (h) { return h.late > 0; });
    var most = set.filter(function (h) { return h.done; }).sort(function (a, b) { return b.days - a.days; })[0];
    var open = set.filter(function (h) { return !h.done && h.moves > 0; }).sort(function (a, b) { return b.days - a.days; });
    document.getElementById('fMoves').innerHTML = '<b>Of the ' + set.length + ' states and union territories with a final roll date set, ' + moved.length + ' had it moved at least once by an order, a note or a press report, and ' + later.length + ' published the final roll after the last date set for it.</b> ' +
      'Among the final rolls already out, ' + E(most.name) + '\'s came the furthest after the date first set for it, ' + most.days + ' days. Of the states still waiting for a final roll, ' + open.length + ' have had the date moved, ' +
      open.map(function (h) { return E(h.name) + ' ' + (h.moves === 1 ? 'once' : h.moves + ' times') + ' and ' + h.days + ' days in all'; }).join(', ').replace(/, ([^,]*)$/, ' and $1') + '.';
    document.getElementById('tMoves').innerHTML = '<thead><tr><th scope="col" class="l">State</th><th scope="col" class="l">Phase</th><th scope="col" class="l">First set for</th><th scope="col" class="l">Each revision of the final roll date, in order</th><th scope="col">Times moved</th><th scope="col">Days later than first set</th></tr></thead><tbody>' +
      hist.map(function (h) {
        return '<tr><th scope="row" class="l">' + E(h.name) + '</th><td class="l">' + h.phase + '</td><td class="l">' + (h.first ? SIR.date(h.first) : '') + '</td><td class="l">' +
          h.pts.map(function (p) { return p.n + '. ' + SIR.date(p.final) + ', ' + (p.url ? '<a href="' + E(p.url) + '" rel="noopener" target="_blank">' + E(p.label) + '</a>' : E(p.label)) + tag(p); }).join('<br>') +
          '</td><td>' + h.moves + '</td><td>' + (h.end ? h.days : '') + '</td></tr>';
      }).join('') + '</tbody>';
    document.getElementById('nMoves').innerHTML = 'Times moved counts the revisions that changed the final roll date. A revision that set no final date, or left it where it was, is not counted, and neither is the day the roll came out. Days later runs from the date first set to the day the final roll was published, or to the latest date set where it has not been. For most Phase II states the order that set the day the roll came out was not found. Dates reported in the press are given as reported, and no order on this page confirms them.';
    SIR.tools();
    function drawMoves(id, rows, label) {
      var box = document.getElementById(id); if (!box) return;
      if (!rows.length) { box.innerHTML = ''; return; }
      var D = function (iso) { return Date.parse(iso + 'T00:00:00Z'); };
      var cw = box.clientWidth || innerWidth, ph = cw < 600, W = ph ? Math.max(320, Math.min(cw, 599)) : Math.max(600, Math.min(cw, 1100));
      var lw = ph ? 112 : 230, R = 5, leg = 30, all = [];
      rows.forEach(function (r) { r.pts.forEach(function (p) { all.push(D(p.final)); }); });
      var a = new Date(Math.min.apply(null, all)), b = new Date(Math.max.apply(null, all));
      var m0 = Date.UTC(a.getUTCFullYear(), a.getUTCMonth(), 1), m1 = Date.UTC(b.getUTCFullYear(), b.getUTCMonth() + 1, 1);
      var X = function (t) { return lw + 14 + (W - lw - 30) * (t - m0) / (m1 - m0); };
      // points that would touch are stacked within their row
      rows.forEach(function (r) { var px = -99, lv = -1; r.lv = 0; r.pts.forEach(function (p) { var x = X(D(p.final)); lv = x - px < 2 * R + 8 ? lv + 1 : 0; p.lv = lv; px = x; r.lv = Math.max(r.lv, lv); }); r.h = 44 + 15 * r.lv; });
      var H = leg + rows.reduce(function (t, r) { return t + r.h; }, 0) + 26;
      var s = mk('svg', { viewBox: '0 0 ' + W + ' ' + H, role: 'group', 'aria-label': label, class: 'viz', preserveAspectRatio: 'xMidYMid meet' });
      box.innerHTML = ''; box.appendChild(s); mk('title', {}, s, label);
      var mon = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      var span = (m1 - m0) / 864e5;
      for (var m = new Date(m0), i = 0; m.getTime() <= m1; m = new Date(Date.UTC(m.getUTCFullYear(), m.getUTCMonth() + 1, 1)), i++) {
        mk('line', { x1: X(m.getTime()), x2: X(m.getTime()), y1: leg, y2: H - 22, class: 'vgrid' }, s);
        if (m.getTime() < m1 && (!ph || span < 150 || i % 2 === 0)) mk('text', { x: X(m.getTime()) + 2, y: H - 6, class: 'vval' }, s, mon[m.getUTCMonth()] + (m.getUTCMonth() === 0 || i === 0 ? ' ' + m.getUTCFullYear() : ''));
      }
      function mark(kind, x, y) {
        if (kind === 'pub') return mk('rect', { x: x - 4.5, y: y - 4.5, width: 9, height: 9, style: 'fill:var(--fill-navy)' }, s);
        return mk('circle', { cx: x, cy: y, r: R, style: kind === 'doc' ? 'fill:var(--fill-red)' : 'fill:var(--card);stroke:var(--fill-red);stroke-width:2' }, s);
      }
      [['doc', 'Order or note'], ['press', 'Press report'], ['pub', 'Published']].forEach(function (k, j) {
        var kx = 10 + j * (ph ? 104 : 150), ky = 12;
        mark(k[0], kx, ky);
        mk('text', { x: kx + 10, y: ky, 'dominant-baseline': 'middle', class: 'vval' }, s, k[1]);
      });
      var read = document.createElement('p');
      read.className = 'vread'; read.setAttribute('aria-live', 'polite');
      read.textContent = 'Hover over, tap or tab to a row for each revision.';
      box.appendChild(read);
      var hits = [], y = leg, csv = [['state', 'number', 'final roll date', 'set by', 'source', 'url']];
      rows.forEach(function (r, ri) {
        if (ri % 2) mk('rect', { x: 0, y: y, width: W, height: r.h, class: 'vband' }, s);
        var mid = y + 16;
        mk('text', { x: lw - 6, y: mid, 'text-anchor': 'end', 'dominant-baseline': 'middle', class: 'vname' }, s, ph ? SIR.short(r.name) : r.name);
        mk('text', { x: lw - 6, y: mid + 16, 'text-anchor': 'end', 'dominant-baseline': 'middle', class: 'vval small' }, s, r.moves + (r.moves === 1 ? ' move, ' : ' moves, ') + r.days + (r.days === 1 ? ' day' : ' days'));
        var Q = r.pts.map(function (p) { return { p: p, x: X(D(p.final)), y: mid + 4 + p.lv * 15 }; });
        if (Q.length > 1) mk('path', { d: Q.map(function (q, k) { return (k ? 'L' : 'M') + q.x + ',' + q.y; }).join(' '), style: 'stroke:var(--muted);stroke-width:1.5;fill:none' }, s);
        Q.forEach(function (q) {
          var g = mark(q.p.pub ? 'pub' : q.p.press ? 'press' : 'doc', q.x, q.y);
          mk('title', {}, g, r.name + ', ' + q.p.n + '. ' + SIR.date(q.p.final) + ', ' + q.p.label + tag(q.p));
          mk('text', q.p.lv ? { x: q.x + 9, y: q.y, 'dominant-baseline': 'middle', class: 'vval small' } : { x: q.x, y: q.y - 9, 'text-anchor': 'middle', class: 'vval small' }, s, q.p.n);
          csv.push([r.name, q.p.n, q.p.final, q.p.label, q.p.press ? 'press' : 'document', q.p.url || '']);
        });
        var tt = r.name + ', final roll date. ' + r.pts.map(function (p) { return p.n + ', ' + SIR.date(p.final) + ', ' + p.label + tag(p); }).join('. ');
        hits.push([mk('rect', { x: 0, y: y, width: W, height: r.h, class: 'vhit', tabindex: 0, role: 'button', 'aria-label': tt }, s), tt]);
        y += r.h;
      });
      hits.forEach(function (hp) {
        var show = function () { hits.forEach(function (o2) { o2[0].classList.toggle('on', o2 === hp); }); read.textContent = hp[1] + '.'; };
        ['mouseenter', 'focus', 'click'].forEach(function (ev) { hp[0].addEventListener(ev, show); });
        hp[0].addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); show(); } });
      });
      box.__csv = csv;
    }
  }).catch(function () {});
  document.getElementById('gaps').innerHTML =P.gaps.map(function (g) { return '<li>' + E(g) + '</li>'; }).join('');
  document.getElementById('asof').textContent = SIR.date(P.as_of);
  SIR.tools();
}).catch(SIR.fail);
