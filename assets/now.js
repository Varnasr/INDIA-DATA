// "What to do now" in one state: the steps open to an elector on the day the
// page is read, chosen by the stage the state's revision has reached. The
// stage is SIR.owin's (assets/sir.js), worked out in the browser from
// process.json and states.json exactly as the claims box on the state's
// overview works it out, so the page moves on with the date and needs no
// rebuild. The page source (site/pages/<place>/now/, from
// scripts/make_now_pages.py) names the state in <main data-now>.
//
// Every step names the documents it rests on by a key into
// data/india/now.json (scripts/build_now.py), which fails to build if a key
// no longer resolves; check_data.py fails if this file names a key that
// now.json lacks. Where the documents say nothing, the page says nothing.
(function () {
  var main = document.querySelector('main[data-now]');
  if (!main || !window.SIR) return;
  var SIR = window.SIR, E = SIR.esc, D = SIR.date, N = SIR.n, root = SIR.root;
  var name = main.getAttribute('data-now');
  var ready = Promise.all([SIR.json('data/india/process.json'), SIR.json('data/india/states.json'), SIR.json('data/india/now.json')]);
  var C = {};
  var p = function (x) { return x ? '<p>' + x + '</p>' : ''; };
  var tel = function (x) { return '<a href="tel:' + x.replace(/-/g, '') + '">' + x + '</a>'; };

  // the documents behind a section, as the help page lists them
  function src(keys, extra) {
    var seen = {}, li = [];
    keys.forEach(function (k) {
      if (!k) return;
      var c = C[k];
      if (!c) { if (window.console) console.error('data/india/now.json has no source ' + k); return; }
      c.items.forEach(function (it) {
        if (seen[it.name + it.url]) return;
        seen[it.name + it.url] = 1;
        li.push('<li><a href="' + E(it.url) + '" rel="noopener">' + E(it.name) + '</a>' +
          (it.quote ? '<blockquote>' + E(it.quote) + '</blockquote>' : '') + '</li>');
      });
      if (c.disputes) li.push('<li lang="' + E(L.lang) + '" dir="auto"><a href="' + root + E(c.disputes) + '">' + L('The hearing, on the protests and disputes page') + '</a></li>');
    });
    (extra || []).forEach(function (it) { li.push('<li><a href="' + E(it.url) + '" rel="noopener">' + E(it.name) + '</a></li>'); });
    return li.length ? '<details class="hsrc"><summary>' + L('Where this comes from') + '</summary><ul lang="en" dir="ltr">' + li.join('') + '</ul></details>' : '';
  }
  function sec(id, h, body, keys, extra) {
    return body ? '<h2 id="' + id + '">' + h + '</h2>' + body + src(keys || [], extra) : '';
  }
  // the schedule steps and press report the dates come from, as the box names them
  function steps(r) {
    var out = (r && r.src || []).filter(function (st) { return st.src; }).map(function (st) { return { name: st.label, url: st.src }; });
    if (r && r.rep) out.push({ name: r.rep.outlet + ', ' + D(r.rep.date), url: r.rep.url });
    return out;
  }

  function draw(d) {
    var P = d[0], S = {}, X = d[2], pg = X.pages[name], T = SIR.owin.today;
    C = X.cite;
    d[1].states.forEach(function (s) { S[s.state] = s; });
    if (!pg) throw new Error('data/india/now.json has no page for ' + name);
    var s = E(name), r = SIR.owin.stage(P, S, name, T);
    var sc = P.schedules.filter(function (x) { return x.state === name; })[0];
    var decl = pg.phase === 'III' ? 'c_decl_III' : pg.phase === 'II' ? 'c_decl_II' : null;
    var kind = !r ? 'nodraft' : r.k === 'open' ? 'open' : r.k === 'closed' ? 'closed' : 'final';
    document.getElementById('nowH').textContent = L('What to do now in {s}', { s: name });
    var box = document.getElementById('nowBox');
    if (r) {
      box.className = 'owin ' + r.k;
      box.setAttribute('aria-label', L('Claims and objections'));
      box.innerHTML = SIR.owin.html(r, P);
      box.hidden = false;
    }
    var ceo = pg.ceo.length ? '<h3 id="the-chief-electoral-officer">' + L('The Chief Electoral Officer of {s}', { s: s }) + '</h3><ul class="nowlinks">' +
      pg.ceo.map(function (c) {
        return '<li><a href="' + E(c[1]) + '" rel="noopener">' + (c[0] === 'x' ? L('The Chief Electoral Officer\'s account on X') : L('The Chief Electoral Officer\'s website')) + '</a></li>';
      }).join('') + '</ul>' : '';
    var out = [], short = [];

    if (kind === 'open') {
      out.push(sec('check-the-draft-roll', L('Check whether your name is on the draft roll'),
        p(L('The Election Commission said in its release of {d} that after the draft, Chief Electoral Officers were to put online the lists of electors found absent, shifted, dead or enrolled twice, searchable by EPIC number, the number on the voter identity card.', { d: D(C.c_lists.date) })) +
        p(L('Under the Commission\'s order of {d}, the claims and objections received are to be listed every working day on the notice board and on the Chief Electoral Officer\'s website.', { d: D(C.c_listed_daily.date) })) + ceo,
        ['c_lists', 'c_listed_daily']));
      var off = p(L('The Commission\'s order of {d} lets an elector whose enumeration form was not handed in on time file Form 6, with the declaration that goes with it, during the period for claims and objections.', { d: D(C.c_form6_late.date) }));
      if (decl === 'c_decl_III') off += p(L('For this phase of the revision, the Commission\'s letter of {d} keeps the same declaration, Annexure IV, with Form 6. It lets you link to your own or a relative\'s entry in the roll of the state\'s last intensive revision.', { d: D(C.c_decl_III.date) }));
      if (decl === 'c_decl_II') off += p(L('For this phase of the revision, the Commission\'s letter of {d} set the declaration, Annexure IV. It asks for your own or a relative\'s entry in the roll of the last intensive revision.', { d: D(C.c_decl_II.date) }));
      off += p(L('Get Form 6 from the booth level officer, the registration officer\'s office, voters.eci.gov.in or the ECINet app. Hand it to the booth level officer or the registration officer, or file it online, and keep the reference number.'));
      out.push(sec('left-off-the-draft', L('If you were on the roll before the revision and are not on the draft'), off, ['c_form6_late', 'c_h_form6_sir', decl, 'c_h_get_form6']));
      if (pg.bench && C[pg.bench]) {
        out.push('<h3 id="what-the-supreme-court-bench-said">' + L('What the Supreme Court bench said on {d}', { d: D(C[pg.bench].date) }) + '</h3>' +
          p(L('At its hearing of {d} on the petition about Delhi\'s revision, the Supreme Court bench said that an elector left off the draft who had only been away for a time should be allowed to submit the enumeration form, and that one who had moved to another address in Delhi should be allowed Form 8, as The Indian Express reported. These were remarks made at the hearing, and no written order was reported.', { d: D(C[pg.bench].date) })) +
          src([pg.bench]));
      }
      out.push(sec('applying-for-the-first-time', L('If you are applying for the first time'),
        p(L('A person who has never been on the roll applies on Form 6, the application to be added to the roll. During the revision it goes with the same declaration.')), ['c_h_get_form6', decl]));
      out.push(sec('objecting-to-a-name', L('To object to a name on the roll'),
        p(L('Form 7 is the form for objecting to a name on the roll, or to a name proposed to be added. No entry can be deleted from the draft without an inquiry and a fair and reasonable chance for the person to be heard, and the registration officer has to pass a written order with reasons.')), ['c_h_form7']));
      out.push(sec('correcting-an-entry', L('To correct an entry, or after a move'),
        p(L('Form 8 is for a mistake in your own entry and for a change of address within the state.')) +
        (decl === 'c_decl_III' ? p(L('Under the Commission\'s letter of {d}, anyone moving in from another state files Form 8 with the same declaration.', { d: D(C.c_decl_III.date) })) : ''),
        ['c_h_get_form6', decl === 'c_decl_III' ? decl : null]));
      if (decl) {
        out.push(sec('documents', L('Documents'),
          p(L('Documents are asked for when the registration officer sends a notice because the details in the declaration are missing or do not match.')) +
          p(L('The Commission\'s letter of {d} sets the list of documents that are accepted.', { d: D(C[decl].date) })), ['c_decl_II', decl]));
      }
      out.push(sec('the-deadline', L('The deadline'),
        p(L('The last day for claims and objections in {s} is {c}.', { s: s, c: D(r.c1) }) + (r.rep && r.rep.claims_end === r.c1 ? ' ' + L('That date is as {o} reported on {r}.', { o: E(r.rep.outlet), r: D(r.rep.date) }) : '')) +
        p(L('After the revision, Form 6 can still be filed at any time under continuous updation, until ten days before the last date for nominations in an election. No name can be added after the last date for nominations until that election is over.')),
        ['c_h_anytime'], steps(r)));
      short = [L('Claims and objections in {s} are open until {c}.', { s: s, c: D(r.c1) }),
        L('Until that day an elector left off the draft can ask on Form 6 to be put back, an elector can object to a name on Form 7, and an entry can be corrected on Form 8.'),
        pg.bench && C[pg.bench] ? L('On {d} the Supreme Court bench said at a hearing that Delhi electors left off the draft who had only been away for a time should be allowed to submit the enumeration form, and those who had moved within Delhi should be allowed Form 8. No written order was reported.', { d: D(C[pg.bench].date) }) : '',
        L('The voter helpline is {a}, and the free legal aid helpline is {b}.', { a: tel('1950'), b: tel('15100') })];
    } else if (kind === 'closed') {
      out.push(sec('what-a-notice-is', L('What a notice is'),
        p(L('An elector who is on the draft roll can still be sent a notice to show that the entry is right. Notices go to electors who could not be linked to the roll of the last intensive revision, which is the no-mapping list, and to those whose link showed a discrepancy, which is the logical discrepancy list. An elector can be on both lists.')) +
        (decl === 'c_decl_III' ? p(L('The Commission\'s order of {d} said that the lists of those sent notices were to be published.', { d: D(C.c_notices_III.date) })) : '') +
        p('<a href="' + root + 'about-the-data/#notices">' + L('Notices, in About the data') + '</a>'),
        [decl === 'c_decl_III' ? 'c_notices_III' : null]));
      out.push(sec('the-hearing', L('The hearing'),
        p(L('The Commission said on {d} that booth level officers would collect at home the documents of electors sent a notice for no mapping or a discrepancy, and upload them for the registration officer, so that these electors need not come to the office. A hearing would be held only in exceptional cases, as the registration officer decides, preferably online, and a family member the elector authorises could attend.', { d: D(C.c_docs_home.date) })) +
        p(L('If someone has objected to your name on Form 7, you should get a notice with the date, time and place of the hearing. Take your documents, and ask for the registration officer\'s decision in writing, because an appeal needs it.')) +
        p(L('No entry can be deleted from the draft without an inquiry and a fair and reasonable chance for the person to be heard.')),
        ['c_docs_home', 'c_h_hearing', 'c_h_form7']));
      out.push(sec('what-comes-next', L('What comes next'),
        p(L('A decision of the registration officer on your name can be appealed, first to the District Magistrate and then to the state\'s Chief Electoral Officer.')) +
        p(L('Once the revision is over in the state, an elector who is not on the final roll can still apply on Form 6 at any time under continuous updation.')) +
        p('<a href="' + root + 'help/#appeal">' + L('How to appeal, step by step') + '</a>'),
        ['c_h_appeal', 'c_h_anytime'], steps(r)));
      short = [r.c1 && r.c1 < T ? L('Claims and objections in {s} closed on {c}.', { s: s, c: D(r.c1) }) : '',
        r.n1 ? (r.n1 >= T ? L('Notices are being heard and decided until {n}.', { n: D(r.n1) }) : L('Notices were to be heard and decided by {n}.', { n: D(r.n1) })) : '',
        r.f ? (r.rep ? L('The final roll is due on {f}, as {o} reported on {r}.', { f: D(r.f), o: E(r.rep.outlet) + (/,/.test(r.rep.outlet) ? ',' : ''), r: D(r.rep.date) }) : L('The final roll is due on {f}.', { f: D(r.f) })) : '',
        L('Once the revision is over in the state, an elector who is not on the final roll can still apply on Form 6 at any time under continuous updation.')];
    } else if (kind === 'final') {
      var fs = S[name] && S[name].final_source;
      out.push(sec('the-final-roll', L('The final roll'),
        (r.k === 'final' && fs && fs.url ? p('<a href="' + E(fs.url) + '" rel="noopener">' + (fs.source === 'press' ? L('The final roll, as the press reported it') : L('The final roll, as published')) + '</a>') : '') + ceo));
      out.push(sec('appealing-a-decision', L('Appealing a decision'),
        p(L('If the registration officer\'s decision on your name goes against you, you can appeal to the District Magistrate under section 24(a) of the Representation of the People Act, 1950, read with rule 27 of the Registration of Electors Rules, 1960. Chief Electoral Officers\' notes on final rolls give 15 days from the registration officer\'s decision for this first appeal.')) +
        p(L('If the District Magistrate\'s order also goes against you, a second appeal lies to the state\'s Chief Electoral Officer under section 24(b), within 30 days of the District Magistrate\'s order, under the Commission\'s order of {d}.', { d: D(C.c_h_appeal_order.date) })) +
        p(L('The appeal is a memorandum you sign, with a copy of the order appealed from. Keep copies and receipts of everything you hand in.')),
        ['c_h_appeal', 'c_h_appeal_order']));
      out.push(sec('not-on-the-final-roll', L('If you are not on the final roll'),
        p(L('A person who is no longer on the roll applies again on Form 6 as a new elector, as paragraph 14.7.4.1 of the Commission\'s Manual on Electoral Rolls says. Section 23(1) of the Representation of the People Act, 1950 lets anyone whose name is not on the roll apply to be added.')) +
        p(L('An elector who is not on the final roll can still apply on Form 6 at any time under continuous updation.') + ' ' + L('No name can be added after the last date for nominations in an election until that election is over, so apply well before one is called.')) +
        p(L('In its letter of {d}, the Commission told booth level officers to compare the roll from before the revision with the present one, list the electors missing from it, and help those still eligible fill in Form 6.', { d: D(C.c_h_drive.date) })) +
        p('<a href="' + root + 'help/#form6">' + L('What the ordinary Form 6 asks an applicant to declare') + '</a>'),
        ['c_h_reapply', 'c_h_anytime', 'c_h_drive', 'c_h_drive_form6']));
      short = [r.k === 'final' ? (r.pub ? L('The final roll was published on {d}.', { d: D(r.pub) }) : L('The final roll has been published.'))
        : L('The final roll was due on {f}. When these dates were last checked, on {a}, it had not been found published.', { f: D(r.f), a: D(P.as_of) }),
        L('A decision on your name can be appealed to the District Magistrate within 15 days, and then to the Chief Electoral Officer within 30 days of the District Magistrate\'s order.'),
        L('An elector who is not on the final roll can still apply on Form 6 at any time under continuous updation.')];
    } else {
      var rows = '', srcs = [];
      if (sc) {
        var last = function (k) { return sc.steps.slice().reverse().filter(function (st) { return st[k]; })[0]; };
        [['enum', L('House-to-house enumeration')], ['draft', L('Draft roll')], ['claims', L('Claims and objections')], ['notice', L('Notices heard and decided')], ['final', L('Final roll')]].forEach(function (f) {
          var st = last(f[0]);
          if (!st) return;
          var v = st[f[0]];
          rows += '<tr><th scope="row" class="l">' + f[1] + '</th><td class="l">' + (typeof v === 'string' ? D(v) : L('{a} to {b}', { a: D(v[0]), b: D(v[1]) })) + '</td><td class="l" lang="en">' + E(st.label) + '</td></tr>';
          if (st.src && srcs.every(function (x) { return x.url !== st.src; })) srcs.push({ name: st.label, url: st.src });
        });
        // a later draft or final date the press reported, as the box and the
        // line under the kicker take it, marked as reported
        var rep = (P.reported_dates || []).filter(function (x) { return x.state === name; })
          .sort(function (a, b) { return a.date < b.date ? -1 : a.date > b.date ? 1 : 0; }).pop();
        if (rep) {
          [['draft', L('Draft roll')], ['final', L('Final roll')]].forEach(function (f) {
            if (!rep[f[0]]) return;
            rows += '<tr><th scope="row" class="l">' + f[1] + '</th><td class="l">' + L('{d}, as reported', { d: D(rep[f[0]]) }) + '</td><td class="l" lang="en">' + E(rep.outlet) + ', ' + D(rep.date) + '</td></tr>';
          });
          srcs.push({ name: rep.outlet + ', ' + D(rep.date), url: rep.url });
        }
      }
      out.push(sec('the-dates-on-record', L('The dates on record'),
        p(sc ? L('No draft roll of the revision in {s} is on record yet. The latest schedule on record sets these dates.', { s: s }) : L('No schedule for the revision in {s} is on record.', { s: s })) +
        (rows ? '<div class="twrap" tabindex="0" role="region" aria-label="' + E(L('The dates on record')) + '"><table><thead><tr><th scope="col" class="l">' + L('Step') + '</th><th scope="col" class="l">' + L('Date') + '</th><th scope="col" class="l">' + L('Set by') + '</th></tr></thead><tbody>' + rows + '</tbody></table></div>' : ''),
        [], srcs));
      short = [L('No draft roll of the revision in {s} is on record yet.', { s: s })];
    }

    // the state's own figures
    var nt = pg.notices, fig = '';
    if (nt) {
      var row = function (label, x, n, date) {
        if (n == null) return '';
        return '<tr><th scope="row" class="l">' + label + '</th><td>' + N(n) + (x && x.rounded ? '*' : '') + '</td><td class="l">' + (date ? D(date) : '') + '</td><td class="l">' +
          (x && x.url ? '<a href="' + E(x.url) + '" rel="noopener">' + (x.kind === 'primary' ? L('Document') : L('Press report')) + '</a>' : '') + '</td></tr>';
      };
      var lists = { url: nt.lists_url, kind: nt.lists_url === nt.url ? nt.kind : 'press' };
      fig += '<div class="twrap" tabindex="0" role="region" aria-label="' + E(L('Notices in {s}', { s: name })) + '"><table><thead><tr><th scope="col" class="l">' + L('Notices in {s}', { s: s }) + '</th><th scope="col">' + L('Count') + '</th><th scope="col" class="l">' + L('As of') + '</th><th scope="col" class="l">' + L('Source') + '</th></tr></thead><tbody>' +
        row(L('Notices sent'), nt, nt.n, nt.date) +
        row(L('On the no-mapping list'), lists, nt.no_mapping, nt.lists_url === nt.url ? nt.date : null) +
        row(L('On the logical discrepancy list'), lists, nt.discrepancy, nt.lists_url === nt.url ? nt.date : null) +
        (nt.hearings ? row(L('Notices heard or verified'), nt.hearings, nt.hearings.n, nt.hearings.date) : '') +
        (nt.deleted ? row(L('Deleted after a notice'), nt.deleted, nt.deleted.n, nt.deleted.date) : '') +
        '</tbody></table></div>' +
        '<p class="note">' + L('An asterisk marks a figure published rounded, or as about or over a number. An elector can be on both lists, so the two lists need not add up to the notices sent.') + '</p>';
    } else {
      fig += p(L('No count of the notices sent in {s} is on record.', { s: s }));
    }
    var extra = [];
    if (pg.split) {
      fig += p(L('The Chief Electoral Officer\'s press note gives the names left off as shifted, absent or other in one figure. The Hindu\'s count of {d}, from the Chief Electoral Officer\'s booth-wise lists of names left off, put {a} lakh of them as permanently shifted and {b} lakh as untraceable or absent.', { d: D(pg.split.date), a: pg.split.shifted, b: pg.split.absent }));
      extra.push({ name: pg.split.name, url: pg.split.url });
    }
    fig += p('<a href="' + root + E(pg.overview) + '">' + L('Every figure for {s}, on its overview', { s: E(pg.label) }) + '</a>');
    out.push(sec('the-figures', L('The figures for {s}', { s: s }), fig, [], extra));

    // where to get help, and the state in the courts
    var help = p(L('The voter helpline is {a}, and the toll-free number {b} answers from 8 am to 8 pm. Complaints are recorded on the National Grievance Service Portal, so note the complaint number.', { a: tel('1950'), b: tel('1800-11-1950') })) +
      p(L('The Book-a-Call with BLO feature of the ECINet app puts you in touch with your booth level officer.')) +
      p(L('Under section 12 of the Legal Services Authorities Act, 1987, free legal help is open to women, children, members of Scheduled Castes and Scheduled Tribes, people with disabilities, industrial workers, victims of disaster and people below an income limit set by each state. Ask at the District Legal Services Authority at the district court, or call {c}.', { c: tel('15100') }));
    if (pg.orgs) help += p('<a href="' + root + 'help/?state=' + encodeURIComponent(name) + '#organisations-that-have-helped-electors">' +
      (pg.orgs === 1 ? L('One organisation that has helped electors in {s}', { s: s }) : L('{k} organisations that have helped electors in {s}', { k: N(pg.orgs), s: s })) + '</a>');
    help += p('<a href="' + root + 'help/">' + L('Every step, with the law or order it rests on') + '</a>');
    out.push(sec('where-to-get-help', L('Where to get help'), help, ['c_h_helpline', 'c_h_legal']));
    if (pg.courts.length) {
      out.push('<h3 id="in-the-courts">' + L('{s} in the courts', { s: s }) + '</h3>' +
        p(L('The protests and disputes page reports each court matter about {s} with its source. Each link opens the matters before one court.', { s: s })) +
        '<ul class="nowlinks">' + pg.courts.map(function (c) {
          return '<li><a href="' + root + 'india/disputes/?state=' + encodeURIComponent(name) + '&amp;court=' + encodeURIComponent(c[0]) + '#courts" lang="en">' + E(c[0]) + '</a> <span class="nsrc">' + (c[1] === 1 ? L('One item') : L('{n} items', { n: N(c[1]) })) + '</span></li>';
        }).join('') + '</ul>');
    }

    document.getElementById('nowBody').innerHTML = out.join('');
    main.setAttribute('data-now-stage', kind);
    if (SIR.anchors) SIR.anchors();
    return {
      qa: [
        [L('What is the difference between a name left off the draft and a name deleted?'),
          L('A name on the roll before the revision whose enumeration form did not come back was left off the draft. A name taken off the roll by an officer\'s order after the draft, on an objection in Form 7 or on the officer\'s own motion, is deleted, and that order can be appealed. <a href="{u}">Words we use</a> sets out the difference.', { u: root + 'about-the-data/#words-we-use' })],
        [L('Can a name be added after the revision is over?'),
          L('Form 6 can be filed at any time under continuous updation, until ten days before the last date for nominations in an election. No name can be added after the last date for nominations until that election is over.')],
        [L('Where are the steps set out in full?'),
          L('<a href="{u}">Left off the roll? What to do</a> sets out each step with the law or order it rests on, and lists organisations that have helped electors.', { u: root + 'help/' })]
      ],
      short: { faq: [short, L('These steps are general information drawn from the law and the Election Commission\'s orders, and they are not legal advice on any one case. The registration officer, the Chief Electoral Officer and the District Legal Services Authority can say how a step works in {s}.', { s: s })] }
    };
  }

  SIR.faq('now', 'help/', function () { return ready.then(draw); });
})();
