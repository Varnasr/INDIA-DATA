// The page reads in English, Hindi and Bengali. The translations live in
// help.json (tr.hi, tr.bn), keyed by the English sentence, and build_help.py
// fails if one is missing. Quotations from the sources stay in their own words.
SIR.json('data/india/help.json').then(function (H) {
  var esc = SIR.esc, n = SIR.n, C = H.counts;
  var lg = (L.lang === 'hi' || L.lang === 'bn') ? L.lang : 'en', TR = (H.tr || {})[lg] || {};
  var t = function (s, v) { var o = TR[s] || s; if (v) Object.keys(v).forEach(function (k) { o = o.split('{' + k + '}').join(v[k]); }); return o; };
  var art = document.getElementById('helpart');
  if (lg !== 'en') {
    art.setAttribute('lang', lg);
    document.getElementById('hlang').textContent = t('This translation has not yet been checked by a native reader, and the English page governs. Every step links to the document it rests on, and the quotations from those documents are in their own words.');
  }
  document.getElementById('hlead').textContent = t("This page sets out what the law and the Election Commission's own orders give an elector whose name was left off the draft or the final roll, and where to get help. It is general information drawn from those documents, and it is not legal advice on any one case. The state's Chief Electoral Officer, the registration officer and the District Legal Services Authority can say how a step works in a particular state.");
  document.getElementById('hEndorse').textContent = t('Listing an organisation here is not an endorsement, and leaving one out says nothing about it. If you know of an organisation that helped electors, or a listing is out of date, write to the address at the foot of the page with a link that shows it.');
  document.getElementById('hOrgH').textContent = t('Organisations that have helped electors');
  document.getElementById('hStateL').textContent = t('State');
  SIR.inShort([
    t('A name left off can be put back. Form 6 asks for it, during the revision and at any time after it, until ten days before the last date for nominations in an election.'),
    t('In the revision, no name could be struck off the draft roll without an inquiry and a fair chance to be heard, followed by a written order with reasons.'),
    t("A decision can be appealed twice, first to the District Magistrate and then to the state's Chief Electoral Officer."),
    t('The voter helpline is 1950, and the free legal aid helpline is 15100.'),
    t('{o} organisations in {s} states are listed with the help they gave, each with a report that shows it.', { o: n(C.orgs), s: n(C.states) })
  ], t("This page gives general information from the law and the Commission's orders. It is not legal advice on any one case, and the list of organisations is not complete."));

  document.getElementById('kpis').innerHTML = [['Form 6', t('to be added back')], [t('2 appeals'), t('District Magistrate, then the CEO')], ['1950', t('voter helpline')], ['15100', t('free legal aid helpline')]]
    .map(function (x) { var tel = /^\d+$/.test(x[0]) ? '<a href="tel:' + x[0] + '">' + x[0] + '</a>' : esc(x[0]); return '<div><b>' + tel + '</b><span>' + esc(x[1]) + '</span></div>'; }).join('');
  // every helpline number on the page can be tapped to call
  (function call(root) {
    var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null), t, hits = [];
    while ((t = w.nextNode())) if (/\b(1800-11-1950|1950|15100)\b/.test(t.nodeValue) && !t.parentNode.closest('a,script,style,.ncontact')) hits.push(t);
    hits.forEach(function (t) { var sp = document.createElement('span');
      // 1950 is also the year of the Representation of the People Act, which is no number to call
      sp.innerHTML = esc(t.nodeValue).replace(/\b(1800-11-1950|1950|15100)\b/g, function (m, x, at, all) { return /Act,?\s*$/.test(all.slice(Math.max(0, at - 8), at)) ? m : '<a href="tel:' + m.replace(/-/g, '') + '">' + m + '</a>'; });
      t.parentNode.replaceChild(sp, t); });
    window.__helpCall = call;
  })(document.querySelector('main'));

  // each remedy straight into the article, so it keeps the reading column
  document.getElementById('steps').outerHTML = H.remedies.map(function (r) {
    return '<h2 id="' + esc(r.id) + '">' + esc(t(r.title)) + '</h2><p>' + esc(t(r.plain)) + '</p>' +
      (r.steps.length ? '<ol class="hsteps">' + r.steps.map(function (s) { return '<li>' + esc(t(s)) + '</li>'; }).join('') + '</ol>' : '') +
      '<details class="hsrc"><summary>' + esc(t('Where this comes from')) + '</summary><ul lang="en">' + r.sources.map(function (s) {
        return '<li><a href="' + esc(s.url) + '" rel="noopener">' + esc(s.doc) + '</a>' + (s.status === 'press' ? ' <span class="tag press">' + esc(t('report')) + '</span>' : '') +
          (s.quote ? '<blockquote>' + esc(s.quote) + '</blockquote>' : '') + '</li>';
      }).join('') + '</ul></details>';
  }).join('');

  document.getElementById('orgSub').textContent = t('Groups that ran help desks, camps, helplines or legal help during the revision, {o} of them in {s} states, each with the report that shows the help it gave and when it was last reported active. The list leaves out political parties and anything led by a party office-holder. It is incomplete, and nothing was found that could be checked for the other states.', { o: n(C.orgs), s: n(C.states) });
  var sel = document.getElementById('orgState'), place = function (s) { return s === 'India' ? t('Across India') : t(s); };
  sel.innerHTML = '<option value="">' + esc(t('Every state')) + '</option>' + H.org_states.concat(['India']).map(function (s) {
    var k = H.orgs.filter(function (o) { return o.state === s; }).length; return '<option value="' + esc(s) + '">' + esc(place(s)) + ' (' + k + ')</option>'; }).join('');
  var end = document.getElementById('orgEnd');
  // a contact line is plain text; its website, email and phone numbers become links
  // a report dated by month only (an annual report) shows its month and year
  function fdate(d) { return /^\d{4}-\d{2}$/.test(d || '') ? SIR.date(d + '-01').replace(/^\d+\s+/, '') : SIR.date(d); }
  function linkify(x) {
    return esc(x).replace(/\b([\w.+-]+@[\w-]+(\.[\w-]+)+)\b/g, '<a href="mailto:$1">$1</a>')
      .replace(/(^|[\s(])((?:www\.)?[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:org|in|net|com)(?:\.in)?(?:\/[\w\/.-]*)?)(?=[\s,.;)]|$)/gi, function (m, a, d) { return /@/.test(d) ? m : a + '<a href="https://' + d.replace(/\.$/, '') + '" rel="noopener">' + d + '</a>'; })
      .replace(/(\+?\d[\d -]{8,}\d)/g, function (m) { return '<a href="tel:' + m.replace(/[^\d+]/g, '') + '">' + m + '</a>'; });
  }
  function draw() {
    var st = sel.value, rows = H.orgs.filter(function (o) { return !st || o.state === st; });
    document.querySelectorAll('.orgs').forEach(function (x) { x.remove(); });
    end.insertAdjacentHTML('beforebegin', '<ul class="orgs">' + rows.map(function (o) {
      var since = o.active_as_of && o.active_as_of !== o.source_date ? ' ' + t('Last reported active {d}.', { d: SIR.date(o.active_as_of) }) : '';
      return '<li><p class="on"><b lang="en">' + esc(o.name) + '</b><span>' + esc(place(o.state)) + '</span></p><p>' + esc(t(o.what)) + '</p>' +
        (o.contact ? '<p class="ncontact"><b>' + esc(t(o.contact_level === 'parent body' ? 'Contact, through the main office' : 'Contact')) + '</b> <span lang="en">' + linkify(o.contact) + '</span> <a class="csrc" href="' + esc(o.contact_src) + '" rel="noopener">' + esc(t('Where this is printed')) + '</a></p>' : '') +
        '<p class="nsrc">' + (/^https?:/.test(o.how_to_reach || '') ? '<a href="' + esc(o.how_to_reach) + '" rel="noopener">' + esc(t('Website')) + '</a> · ' : '') +
        esc(t('Shown by')) + ' <a href="' + esc(o.source_url) + '" rel="noopener">' + esc(o.source_outlet) + '</a>, ' + fdate(o.source_date) + '.' + esc(since) + '</p></li>';
    }).join('') + '</ul>');
    document.getElementById('orgCount').textContent = st ? t(rows.length === 1 ? 'One organisation in {p}.' : '{k} organisations in {p}.', { k: n(rows.length), p: st === 'India' ? t('more than one state') : place(st) }) : t('{k} organisations in all.', { k: n(rows.length) });
  }
  // ?state=<name> opens the list on one state, so a state page can link to its own
  var want = new URLSearchParams(location.search).get('state');
  if (want && [].some.call(sel.options, function (o) { return o.value === want; })) sel.value = want;
  sel.addEventListener('change', function () {
    var u = new URLSearchParams(location.search); if (sel.value) u.set('state', sel.value); else u.delete('state');
    history.replaceState(null, '', location.pathname + (u.toString() ? '?' + u : '') + location.hash); draw(); });
  draw();
  window.__helpCall(document.querySelector("main"));
  SIR.anchors && SIR.anchors();
  SIR.toc && SIR.toc();
  SIR.jump && SIR.jump();
}).catch(SIR.fail);
