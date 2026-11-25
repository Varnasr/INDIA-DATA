Promise.all([SIR.json('data/india/disputes.json'), SIR.json('data/geo/india.json')]).then(function (r) {
  var D = r[0], geo = r[1], n = SIR.n, esc = SIR.esc, C = D.counts, k = 0;

  // Next in court: hearings and deadlines from today in India onwards, in
  // the reader's language, each linked to its source and to its entry below
  var lang = window.L && L.lang || 'en';
  var today = new Date(Date.now() + 330 * 60000).toISOString().slice(0, 10);
  var MON = [L('January'), L('February'), L('March'), L('April'), L('May'), L('June'), L('July'), L('August'), L('September'), L('October'), L('November'), L('December')];
  var day = function (iso) { var p = iso.split('-'); return L('{d} {m} {y}', { d: +p[2], m: MON[+p[1] - 1], y: p[0] }); };
  var when = { exact: function (s) { return s; }, approximate: function (s) { return L('About {date}', { date: s }); }, tentative: function (s) { return L('{date}, listed tentatively', { date: s }); } };
  (function () {
    var box = document.getElementById('nextCourt');
    var ahead = (D.listings || []).filter(function (x) { return x.date >= today; });
    if (!ahead.length) { box.innerHTML = '<li><p>' + L('No hearing or deadline ahead has been dated.') + '</p></li>'; return; }
    box.innerHTML = ahead.map(function (x) {
      var tr = (x.t || {})[lang], own = lang === 'en' || !tr, f = own ? x : tr;
      var txt = function (s) { return own && lang !== 'en' ? '<span lang="en" dir="ltr">' + esc(s) + '</span>' : esc(s); };
      return '<li id="nc-' + esc(x.id) + '"><p><b>' + L('{date}, {court}', { date: (when[x.date_kind] || when.exact)(day(x.date)), court: txt(f.court) }) + '</b></p>' +
        '<p>' + txt(f.matter) + '</p><p>' + txt(f.due) + '</p>' +
        '<p class="nsrc">' + L('<a href="{src}">{outlet}</a> gives the date. <a href="{entry}">A related entry is below.</a>', { src: esc(x.source_url), outlet: esc(x.source_name), entry: '#d-' + esc(x.disputes_id) }) + '</p></li>';
    }).join('');
  })();
  var INTRO = {
    courts: 'Petitions in the Supreme Court and the High Courts, and what the courts ordered. Where the court\'s own order was found it is quoted. Otherwise the report is.',
    resolutions: 'Resolutions passed by state Assemblies about the revision.',
    protests: 'Marches, rallies and meetings against the revision or parts of it. A party\'s claim is its own, and is attributed to it.',
    boycotts: 'Booth level officers and teachers\' unions who protested their workload or refused the work.',
    form7: 'Form 7 is the form for objecting to a name on the roll. These are reports of objections filed in bulk, some on forms with the elector\'s details already printed, and what officials did about them.',
    software: 'Changes to ECINET and ERONET, the Commission\'s software, and to the checks it runs on electors, during the revision.',
    instructions: 'Instructions officers say they received orally, by message or by video, without a written order, and instructions that changed while the work was under way.',
    errors: 'Living electors marked dead, wrong photographs, duplicates and other errors reported on the rolls.',
    deaths: 'Deaths of booth level officers and of electors that families or colleagues linked to the revision. These are their accounts as reported, and the reports give the officials\' replies where there were any.'
  };
  var GROUP = { courts: 0, resolutions: 1, protests: 1, boycotts: 1, form7: 2, software: 3, instructions: 3, errors: 4, deaths: 4 };
  var GNAME = ['Courts', 'Assemblies and protests', 'Form 7', 'Software and instructions', 'Errors and deaths'];
  var secCount = {};
  D.sections.forEach(function (s) { secCount[s.id] = s.items.length; });

  var topState = Object.keys(D.by_state)[0];
  SIR.inShort([
    n(C.items) + ' court orders, resolutions, protests and reports from ' + SIR.date(C.first) + ' to ' + SIR.date(C.last) + ', touching ' + n(C.states) + ' states and union territories.',
    (secCount.courts ? n(secCount.courts) + ' are court cases, ' : '') + n(C.primary) + ' rest on the court\'s, the Assembly\'s or the Commission\'s own document, and the rest on named press reports.',
    secCount.form7 ? n(secCount.form7) + ' concern Form 7 objections filed in bulk, some on forms with the elector\'s details already printed.' : '',
    (secCount.software || 0) + (secCount.instructions || 0) ? n((secCount.software || 0) + (secCount.instructions || 0)) + ' concern changes to the Commission\'s software or instructions given without a written order.' : '',
    topState ? 'The most items concern ' + topState + ', ' + n(D.by_state[topState]) + '.' : ''
  ], 'A report on this page is what the outlet reported. Where a party alleges something, the allegation is the party\'s. Nothing here says what anyone intended, and nothing says whether any person is a citizen.');

  document.getElementById('kpis').innerHTML = [
    [n(C.items), 'items, each with its source'], [n(C.primary), 'from the document itself'],
    [n(C.states), 'states and territories'], [n(secCount.courts || 0), 'court cases and orders']
  ].map(function (x) { return '<div><b>' + x[0] + '</b><span>' + x[1] + '</span></div>'; }).join('');

  // the map and the ranked list beside it, so a phone does not depend on hover
  var ALIAS = { 'Andaman & Nicobar': 'Andaman and Nicobar Islands', 'Jammu & Kashmir': 'Jammu and Kashmir', 'Andaman and Nicobar': 'Andaman and Nicobar Islands' };
  var byId = {};
  geo.features.forEach(function (f) { byId[f.properties.ac] = ALIAS[f.properties.name] || f.properties.name; });
  var cnt = function (name) { for (var s in D.by_state) if ((ALIAS[s] || s) === name) return D.by_state[s]; return null; };
  VIZ.map('vMap', { geo: geo, label: 'Map of the number of items on this page by state', title: 'Items on this page',
    v: function (id) { return cnt(byId[id]); }, name: function (id) { return byId[id] || ''; }, fmt: function (v) { return n(v); },
    // whole-number bins, so a legend never reads 1 to 1
    breaks: (function () { var mx = Math.max.apply(null, Object.keys(D.by_state).map(function (s) { return D.by_state[s]; })); var st = Math.max(1, Math.ceil(mx / 5)); return [st, 2 * st, 3 * st, 4 * st]; })() });
  VIZ.lollipop('vStates', { label: 'Items on this page by state', axis: 'Items',
    rows: Object.keys(D.by_state).map(function (s) { return { name: s, v: D.by_state[s], text: n(D.by_state[s]), tok: '--fill-red', hi: true }; }) });

  var months = Object.keys(D.by_month);
  VIZ.heat('vMonths', { label: 'Items by month and group', cols: GNAME, tok: ['--fill-navy', '--fill-red', '--fill-amber', '--fill-grey', '--fill-red'],
    max: Math.max.apply(null, months.map(function (m) { return Math.max.apply(null, [0, 1, 2, 3, 4].map(function (g) { return Object.keys(D.by_month[m]).reduce(function (a, s) { return a + (GROUP[s] === g ? D.by_month[m][s] : 0); }, 0); })); })),
    rows: months.map(function (m) {
      return { name: new Date(m + '-01').toLocaleDateString('en-IN', { month: 'short', year: 'numeric' }),
        v: [0, 1, 2, 3, 4].map(function (g) { var t = Object.keys(D.by_month[m]).reduce(function (a, s) { return a + (GROUP[s] === g ? D.by_month[m][s] : 0); }, 0); return t || null; }) };
    }) });

  // every item in one list, so the filters can run over all of them
  var ALL = [];
  D.sections.forEach(function (sec) { sec.items.forEach(function (it) { ALL.push({ sec: sec, it: it, h: (it.claim + ' ' + it.response + ' ' + it.quote + ' ' + it.outlet + ' ' + it.case + ' ' + it.state + ' ' + it.court + ' ' + it.places.join(' ') + ' ' + it.actors.join(' ') + ' ' + it.issues.join(' ')).toLowerCase() }); }); });
  var F = { state: 'fState', issue: 'fIssue', court: 'fCourt', actor: 'fActor', place: 'fPlace' };
  var valsOf = { state: function (it) { return it.states; }, issue: function (it) { return it.issues; }, court: function (it) { return it.court ? [it.court] : []; }, actor: function (it) { return it.actors; }, place: function (it) { return it.places; } };
  var ANY = { state: 'Every state', issue: 'Every issue', court: 'Every court', actor: 'Every party or body', place: 'Every place' };
  Object.keys(F).forEach(function (k) {
    var c = {};
    ALL.forEach(function (a) { valsOf[k](a.it).forEach(function (v) { c[v] = (c[v] || 0) + 1; }); });
    var keys = Object.keys(c).sort(function (a, b) { return k === 'state' || k === 'place' || k === 'court' ? a.localeCompare(b) : c[b] - c[a] || a.localeCompare(b); });
    document.getElementById(F[k]).innerHTML = '<option value="">' + ANY[k] + '</option>' + keys.map(function (v) { return '<option value="' + esc(v) + '">' + esc(v) + ' (' + c[v] + ')</option>'; }).join('');
  });
  var li = function (it) {
    var where = it.place ? esc(it.place) : esc(it.state);
    var src = '<a href="' + esc(it.url) + '" rel="noopener">' + esc(it.outlet) + '</a>, ' + SIR.date(it.date) + ', ' + where + (it.case ? ', ' + esc(it.case) : '') + '.' +
      (it.kind === 'primary' ? ' <span class="tag primary">document</span>' : ' <span class="tag press">report</span>');
    return '<li id="d-' + esc(it.id) + '"><p>' + esc(it.claim) + '</p>' +
      (it.response ? '<p class="nresp">' + esc(it.response) + '</p>' : '') +
      '<p class="nsrc">' + src + '</p>' +
      (it.issues.length ? '<p class="dtags">' + it.issues.map(function (x) { return '<span>' + esc(x) + '</span>'; }).join('') + '</p>' : '') +
      (it.quote ? '<details><summary>The words of the source</summary><blockquote>' + esc(it.quote) + '</blockquote></details>' : '') + '</li>';
  };

  // Where things stand in the state chosen in the filter: the roll figures,
  // the summary revision, the next date in court and the items about it, all
  // computed from the data files, which are fetched only once a state is chosen
  var SECNAME = { courts: L('In the courts'), resolutions: L('Resolutions in the Assemblies'), protests: L('Protests by parties and groups'),
    boycotts: L('Booth officers\' protests'), form7: L('Form 7 objections and pre-printed forms'), software: L('Changes to the software'),
    instructions: L('Instructions given without a written order'), errors: L('Wrong entries reported on the rolls'), deaths: L('Deaths reported during the revision') };
  // the state pages whose address is not the one now.json gives as the overview
  var OVERVIEW = { 'Telangana': 'hyderabad/telangana/', 'Assam': 'assam/' };
  // a state that had another kind of revision, as Where the revision stands says
  var SPECIAL = { 'Assam': 1 };
  var sumBox = document.getElementById('stateSum'), sumAsk = 0;
  // the first sentence of an item, which names what happened and who reported
  // it; a full stop after an initial or a short title (V., G.N., No.) does not end one
  var NOTEND = { Nos: 1, Mrs: 1, Smt: 1, Shri: 1, Sri: 1, Ltd: 1, Inc: 1, Hon: 1, Govt: 1, Art: 1, Sec: 1, Vol: 1, Ors: 1, Anr: 1 };
  function first(t) {
    var re = /([^\s.]{3,})\.\s+(?=[A-Z"'\u2018\u201c(])/g, m;
    while ((m = re.exec(t))) if (!NOTEND[m[1]]) return t.slice(0, m.index + m[1].length + 1);
    return t;
  }
  function stateSum(st) {
    var ask = ++sumAsk;
    if (!st || st === 'All India' || st === 'India') { sumBox.hidden = true; sumBox.innerHTML = ''; return; }
    Promise.all([SIR.json('data/india/states.json'), SIR.json('data/india/ssr_draft.json'), SIR.json('data/india/now.json')]).then(function (r) {
      if (ask !== sumAsk) return;
      var S = r[0].states.filter(function (x) { return x.state === st; })[0], R = r[1].states.filter(function (x) { return x.state === st; })[0], NP = r[2].pages[st];
      var nm = lang === 'en' ? esc(st) : '<span lang="en" dir="ltr">' + esc(st) + '</span>';
      var en = function (t) { return lang === 'en' ? esc(t) : '<span lang="en" dir="ltr">' + esc(t) + '</span>'; };
      var root = SIR.root, h = '<h2 id="ssH">' + L('Where things stand in {state}', { state: nm }) + '</h2>';
      // the roll in the intensive revision
      var roll = [];
      if (S && S.electors_before != null && S.removed != null) {
        // the draft as published: where the final roll is on record it is the
        // final roll less the net change after the draft, which in Bihar is
        // 4,462 fewer than the roll before less the names left off. A gap of a
        // handful (Punjab, 27) is left as the states table gives it.
        var fin = S.electors_final != null, draft = S.electors_before - S.removed,
          gap = fin && S.net_after_draft != null ? draft - (S.electors_final - S.net_after_draft) : 0;
        if (Math.abs(gap) > 100) draft -= gap; else gap = 0;
        h += '<div class="kpis">' + [[n(S.electors_before), L('on the roll before the revision')], [n(draft), L('on the draft roll')],
          [fin ? n(S.electors_final) : L('Not yet'), L('on the final roll')], [fin && S.net_fall_per_100 != null ? SIR.d(S.net_fall_per_100, 1) : L('Not yet'), L('fall in the roll for every 100 electors')]]
          .map(function (x) { return '<div><b>' + x[0] + '</b><span>' + x[1] + '</span></div>'; }).join('') + '</div>';
        roll.push(L('The roll before the revision held {before} electors. The draft roll of {date} held {draft}, and {left} names were left off it, {per} for every 100.',
          { before: n(S.electors_before), date: day(S.draft_date), draft: n(draft), left: n(S.removed), per: SIR.d(S.per_100, 1) }));
        if (gap > 0) roll.push(L('The roll before the revision less the names left off is {g} more than the draft roll, because the two figures come from different counts.', { g: n(gap) }));
        if (S.source === 'press') roll.push(L('The figures for the draft roll are as the press reported them.'));
        if (fin) {
          roll.push(S.final_date ? L('The final roll of {date} held {final} electors.', { date: day(S.final_date), final: n(S.electors_final) }) : L('The final roll held {final} electors. The day it was published was not found.', { final: n(S.electors_final) }));
          if (S.net_fall != null) roll.push(S.net_fall === S.electors_before - S.electors_final
            ? L('The fall in the roll, from the roll before the revision to the final roll, is {fall}, or {per} for every 100 electors.', { fall: n(S.net_fall), per: SIR.d(S.net_fall_per_100, 1) })
            : L('The fall in the roll, the names left off less the net number added after the draft, is {fall}, or {per} for every 100 electors.', { fall: n(S.net_fall), per: SIR.d(S.net_fall_per_100, 1) }));
          if (S.withheld) roll.push(L('Another {w} names were held for adjudication and are not on the final roll.', { w: n(S.withheld) }));
          if (S.final_source && S.final_source.source === 'press') roll.push(L('The figures for the final roll are as the press reported them.'));
        } else roll.push(L('No final roll has been found yet.'));
      } else roll.push(SPECIAL[st] ? L('{state} was given a special revision in place of an intensive one.', { state: nm }) : L('No draft roll of the intensive revision has been found for {state}.', { state: nm }));
      roll.push(L('<a href="{href}">Where the revision stands</a> gives the stage each state has reached.', { href: root + 'india/progress/' }));
      h += '<h3>' + L('The intensive revision') + '</h3><p>' + roll.join(' ') + '</p>';
      // the summary revision for 1 January 2027
      if (R && R.postponed && !R.draft) {
        // postponed with no new dates: the dates that were put off are not shown,
        // as on the summary revision page
        h += '<h3>' + L('The summary revision') + '</h3><p>' + L('The special summary revision in {s} was postponed on {d}, and no new dates have been given.', { s: nm, d: day(R.postponed) }) + '</p>';
      } else if (R) {
        var ss = [];
        if (R.draft) {
          ss.push(L('In the summary revision for 1 January 2027, the draft roll of {date} held {electors} electors.', { date: day(R.draft.date), electors: n(R.draft.electors) }));
          if (R.draft.press) ss.push(L('The summary revision figures are as the press reported them.'));
        } else ss.push(R.due < today ? L('The draft roll of the summary revision for 1 January 2027 was due on {date} and has not been found yet.', { date: day(R.due) }) : L('The draft roll of the summary revision for 1 January 2027 is due on {date}.', { date: day(R.due) }));
        if (R.claims_end) ss.push(R.claims_end < today ? L('Claims and objections closed on {date}.', { date: day(R.claims_end) }) : L('Claims and objections close on {date}.', { date: day(R.claims_end) }));
        if (R.final_due) ss.push(L('The final roll is due on {date}.', { date: day(R.final_due) }));
        h += '<h3>' + L('The summary revision') + '</h3><p>' + ss.join(' ') + '</p>';
      }
      // the next date in court
      var ahead = (D.listings || []).filter(function (x) { return x.date >= today; });
      var mine = ahead.filter(function (x) { return x.state === st; }).sort(function (a, b) { return a.date < b.date ? -1 : a.date > b.date ? 1 : 0; }), mat = '', all = ahead.filter(function (x) { return x.state === 'India'; }).length, cs = [];
      if (mine.length) {
        var x = mine[0], tr = (x.t || {})[lang], own = lang === 'en' || !tr, f = own ? x : tr, txt = own ? en : esc;
        cs.push(L('The next date in court for {state} is {date}, before the {court}.', { state: nm, date: (when[x.date_kind] || when.exact)(day(x.date)), court: txt(f.court) }));
        // the matter is a description, so in English it goes into a sentence;
        // in another language it stands on its own line, as in Next in court
        var lead = own && /^(The|A|An|Petitions?|Applications?|Appeals?) /.exec(f.matter);
        if (lead) cs.push(txt('It concerns ' + f.matter.charAt(0).toLowerCase() + f.matter.slice(1).replace(/\.$/, '') + '.'));
        else mat = '<p>' + txt(f.matter) + '</p>';
        cs.push(L('<a href="{href}">It is under Next in court, above.</a>', { href: '#nc-' + esc(x.id) }));
        if (mine.length > 1) cs.push(mine.length === 2 ? L('One more date ahead concerns {state}.', { state: nm }) : L('{k} more dates ahead concern {state}.', { k: n(mine.length - 1), state: nm }));
      } else cs.push(L('No hearing or deadline ahead has been dated for {state}.', { state: nm }));
      if (all) cs.push(all === 1 ? L('Next in court also lists one date ahead in a matter that concerns the whole country.') : L('Next in court also lists {k} dates ahead in matters that concern the whole country.', { k: n(all) }));
      h += '<h3>' + L('In court') + '</h3>' + (mat ? '<p>' + cs.shift() + '</p>' + mat : '') + '<p>' + cs.join(' ') + '</p>';
      // the items about the state, by section, and the three most recent
      var its = ALL.filter(function (a) { return a.it.states.indexOf(st) >= 0; });
      if (its.length) {
        var by = {};
        its.forEach(function (a) { by[a.sec.id] = (by[a.sec.id] || 0) + 1; });
        var link = function (id, label) { return document.getElementById(id) ? '<a href="#' + esc(id) + '">' + label + '</a>' : label; };
        h += '<h3>' + L('Items about {state}', { state: nm }) + '</h3><p>' + (its.length === 1 ? L('One item concerns {state}.', { state: nm }) : L('{k} items concern {state}.', { k: n(its.length), state: nm })) + '</p>' +
          '<ul class="sscount">' + D.sections.filter(function (sec) { return by[sec.id]; }).map(function (sec) { return '<li>' + link(sec.id, SECNAME[sec.id] || esc(sec.title)) + ' <b>' + n(by[sec.id]) + '</b></li>'; }).join('') + '</ul>';
        var rec = its.slice().sort(function (a, b) { return b.it.date.localeCompare(a.it.date); }).slice(0, 3);
        h += '<p>' + (rec.length === 1 ? L('The most recent item') : L('The {k} most recent items', { k: n(rec.length) })) + '</p><ul class="ssrecent">' + rec.map(function (a) {
          return '<li><p>' + link('d-' + a.it.id, day(a.it.date)) + '</p><p lang="en" dir="ltr">' + esc(first(a.it.claim)) + '</p></li>';
        }).join('') + '</ul>';
      }
      // the state's own pages
      var pg = [];
      if (NP && NP.path) pg.push('<a href="' + root + esc(NP.path) + '">' + L('What to do now in {state}', { state: nm }) + '</a>');
      var ov = OVERVIEW[st] || (NP && NP.overview);
      if (ov) pg.push('<a href="' + root + esc(ov) + '">' + L('The {state} overview', { state: nm }) + '</a>');
      if (pg.length) h += '<ul class="sslinks">' + pg.map(function (x) { return '<li>' + x + '</li>'; }).join('') + '</ul>';
      sumBox.innerHTML = h;
      sumBox.lang = lang; sumBox.dir = document.documentElement.dir || 'ltr';
      sumBox.hidden = false;
    }).catch(function () { if (ask === sumAsk) { sumBox.hidden = true; } });
  }
  // the sections go straight into the article, so they keep the reading column
  var end = document.getElementById('secEnd');
  function render() {
    var q = document.getElementById('dq').value.trim().toLowerCase(), want = {};
    Object.keys(F).forEach(function (k) { want[k] = document.getElementById(F[k]).value; });
    var toks = q ? q.split(/\s+/) : [];
    var keep = ALL.filter(function (a) {
      return toks.every(function (t) { return a.h.indexOf(t) >= 0; }) && Object.keys(F).every(function (k) { return !want[k] || valsOf[k](a.it).indexOf(want[k]) >= 0; });
    });
    document.querySelectorAll('.dsec').forEach(function (x) { x.remove(); });
    var k = 0, html = '';
    D.sections.forEach(function (sec) {
      var its = keep.filter(function (a) { return a.sec === sec; });
      if (!its.length) return;
      var start = k + 1; k += its.length;
      html += '<h2 class="dsec" id="' + sec.id + '">' + esc(sec.title) + '</h2><p class="sub dsec">' + INTRO[sec.id] + '</p><ol class="nfacts dsec" start="' + start + '">' + its.map(function (a) { return li(a.it); }).join('') + '</ol>';
    });
    end.insertAdjacentHTML('beforebegin', html);
    stateSum(want.state);
    var on = toks.length || Object.keys(F).some(function (x) { return want[x]; });
    document.getElementById('dCount').textContent = on ? (keep.length ? n(keep.length) + ' of ' + n(ALL.length) + ' items match.' : 'No item matches. Clear a filter or change the search.') : n(ALL.length) + ' items in all.';
    // the address keeps the filters, so the list can be sent as a link
    var u = new URLSearchParams(location.search);
    Object.keys(F).forEach(function (x) { if (want[x]) u.set(x, want[x]); else u.delete(x); });
    if (q) u.set('q', q); else u.delete('q');
    var qs = u.toString();
    history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + location.hash);
    SIR.anchors && SIR.anchors();
  }
  var init = new URLSearchParams(location.search);
  // links shared before the issue was renamed still open on it
  var OLD = { issue: { 'Deletions': 'Names left off or deleted' } };
  Object.keys(F).forEach(function (x) { var v = init.get(x), sel = document.getElementById(F[x]); if (v && OLD[x] && OLD[x][v]) v = OLD[x][v]; if (v && [].some.call(sel.options, function (o) { return o.value === v; })) sel.value = v; });
  if (init.get('q')) document.getElementById('dq').value = init.get('q');
  document.getElementById('dfilter').addEventListener('input', render);
  document.getElementById('dfilter').addEventListener('change', render);
  document.getElementById('fClear').addEventListener('click', function () { document.getElementById('dq').value = ''; Object.keys(F).forEach(function (x) { document.getElementById(F[x]).value = ''; }); render(); });
  render();
  document.getElementById('unconfirmed').innerHTML = D.unconfirmed.length ? D.unconfirmed.map(function (u) {
    return '<li>' + esc(u.outlet || '') + (u.date ? ', ' + SIR.date(u.date) : '') + ', "' + esc(u.headline || '') + '". ' + esc(u.reason) + '</li>';
  }).join('') : '<li>Every report found was matched to its source.</li>';

  SIR.anchors && SIR.anchors();
  SIR.toc && SIR.toc();
  SIR.showFaq('india', 'disputes');
  SIR.jump && SIR.jump();
}).catch(SIR.fail);
