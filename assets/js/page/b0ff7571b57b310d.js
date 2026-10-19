Promise.all([SIR.json('data/india/process.json'), SIR.json('data/india/states.json')]).then(function (r) {
  var P = r[0], S = {}, E = SIR.esc, asof = P.as_of;
  r[1].states.forEach(function (s) { S[s.state] = s; });
  var PAGE = { 'Bihar': 'bihar/', 'Telangana': 'hyderabad/telangana/', 'Tamil Nadu': 'tamilnadu/', 'Karnataka': 'karnataka/', 'West Bengal': 'westbengal/', 'Kerala': 'kerala/', 'Rajasthan': 'rajasthan/', 'Uttar Pradesh': 'uttarpradesh/', 'Delhi': 'delhi/', 'Maharashtra': 'maharashtra/', 'Gujarat': 'gujarat/', 'Uttarakhand': 'uttarakhand/' };
  var key = function (s) { return 's-' + s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''); };
  var within = function (a, b) { return a && b && a <= asof && asof <= b; };
  // one schedule per state: each date taken from the latest step that gives it,
  // then the draft and final rolls as the state actually published them
  // dates the press reports and no document we read confirms: shown as
  // reported, never drawn on the calendar or counted as a schedule
  var REP = {}; (P.reported_dates || []).forEach(function (d) { REP[d.state] = d; });
  var rows = P.schedules.map(function (sc) {
    var m = { enum: null, draft: null, claims: null, claims_end: null, notice: null, final: null };
    sc.steps.forEach(function (st) { Object.keys(m).forEach(function (k) { if (st[k]) m[k] = st[k]; }); });
    var s = S[sc.state] || {};
    if (s.draft_date) m.draft = s.draft_date;
    // a final roll counts as published when its figures are held, even where
    // the day it came out was not found (Chandigarh)
    var pub = s.electors_final != null, pubDate = s.final_date || null;
    if (pubDate) m.final = pubDate;
    var claimsTo = m.claims ? m.claims[1] : m.claims_end;
    var st, cls;
    var rp = REP[sc.state] && (!m.final || REP[sc.state].final > m.final) ? REP[sc.state] : null;
    if (pub) { st = 'Final roll published'; cls = 'done'; }
    else if (rp && s.removed && rp.final >= asof) { st = 'Draft published, final roll reported for ' + SIR.date(rp.final); cls = 'now'; }
    else if (m.final && m.final < asof) { st = 'Final roll was due ' + SIR.date(m.final) + ', not yet found'; cls = 'late'; }
    // a draft date reported after the order's (Tripura) replaces it for a state with no draft
    else if (!s.removed && REP[sc.state] && REP[sc.state].draft && REP[sc.state].draft >= asof) { st = 'No draft roll yet, draft reported for ' + SIR.date(REP[sc.state].draft) + ' (press)'; cls = 'wait'; }
    else if (!s.removed && m.draft && m.draft < asof) { st = 'Draft roll was due ' + SIR.date(m.draft) + ', not yet found'; cls = 'late'; }
    // no draft yet: the order's own dates for such a state (Tripura) were not
    // kept, so no stage is read from them
    else if (!s.removed) { st = 'No draft roll yet'; cls = 'wait'; }
    else if (within(m.claims && m.claims[0], claimsTo)) { st = 'Claims and objections'; cls = 'now'; }
    else if (m.notice && within(m.notice[0], m.notice[1])) { st = 'Notices and hearings'; cls = 'now'; }
    else { st = 'Draft published, final roll due ' + (m.final ? SIR.date(m.final) : 'on a date not yet set'); cls = 'now'; }
    return { state: sc.state, phase: sc.phase, m: m, pub: pub, pubDate: pubDate, stage: st, cls: cls, rp: rp };
  });
  var ord = { I: 1, II: 2, III: 3 };
  rows.sort(function (a, b) { return ord[a.phase] - ord[b.phase] || (a.m.final || '9').localeCompare(b.m.final || '9') || a.state.localeCompare(b.state); });
  var n = function (c) { return rows.filter(function (x) { return x.cls === c; }).length; };
  var done = n('done'), late = rows.filter(function (x) { return x.cls === 'late' && /^Final/.test(x.stage); }), now = n('now'), wait = n('wait') + rows.filter(function (x) { return x.cls === 'late' && /^Draft/.test(x.stage); }).length;

  SIR.inShort([
    done + ' of the ' + rows.length + ' states and union territories in the revision had published a final roll by ' + SIR.date(asof) + '.',
    late.length ? late.length + ' had passed the date their latest schedule set for the final roll with no final roll found: ' + late.map(function (x) { return x.state; }).join(', ') + '.' : '',
    now ? now + ' had published a draft roll and were still taking claims, hearing notices or waiting for the final roll on a later date.' : '',
    wait ? wait + ' had not yet published a draft roll.' : '',
    'Assam had a different kind of revision, and Himachal Pradesh, Jammu and Kashmir and Ladakh have no schedule yet.'
  ], 'A stage follows the latest schedule on record and the rolls found published. A state may have published a roll that has not been found, so a late stage means only that the roll was not found, and says nothing about why.');

  document.getElementById('kpis').innerHTML = [
    [done, 'final rolls published'], [late.length, 'final rolls past their latest date'], [now, 'drafts out, final roll still to come'], [wait, 'no draft roll yet']
  ].map(function (k) { return '<div><b>' + k[0] + '</b><span>' + k[1] + '</span></div>'; }).join('');
  [].forEach.call(document.querySelectorAll('.asof'), function (e) { e.textContent = SIR.date(asof); });

  VIZ.gantt('vCal', { label: 'Every state on its latest schedule, with the date the stages describe', single: true, today: asof, todayLabel: 'As of ' + SIR.date(asof),
    rows: rows.map(function (x) { return { name: x.state, steps: [{ label: x.pub ? (x.pubDate ? 'Final roll published ' + SIR.date(x.pubDate) : 'Final roll published, day not found') : 'Latest schedule', enum: x.m.enum, draft: x.m.draft, claims: x.m.claims, claims_end: x.m.claims_end, final: x.m.final }] }; }) });
  document.getElementById('nCal').textContent = P.notes.p3later;
  // days from the first house visit to the final roll, published or due
  var days = function (a, b) { return Math.round((Date.parse(b) - Date.parse(a)) / 864e5); };
  var dur = rows.filter(function (x) { return S[x.state] && S[x.state].removed && x.m.enum && x.m.enum[0] && x.m.final; }).map(function (x) {
    return { name: x.state, v: days(x.m.enum[0], x.m.final), cls: x.cls, pub: x.pub };
  }).sort(function (a, b) { return b.v - a.v; });
  VIZ.lollipop('vDur', { label: 'Days from the first house visit to the final roll, every state', axis: 'Days from the first house visit to the final roll',
    rows: dur.map(function (d) { return { name: d.name, v: d.v, text: d.v + (d.pub ? ' days' : ' days, if on time'), tok: d.pub ? '--fill-navy' : d.cls === 'late' ? '--fill-red' : '--fill-amber', hi: !d.pub }; }) });
  var pubD = dur.filter(function (d) { return d.pub; }), med = function (a) { a = a.slice().sort(function (x, y) { return x - y; }); return a.length % 2 ? a[(a.length - 1) / 2] : Math.round((a[a.length / 2 - 1] + a[a.length / 2]) / 2); };
  var longest = dur[0];
  document.getElementById('fDur').innerHTML = '<b>The ' + pubD.length + ' revisions that have finished took ' + med(pubD.map(function (d) { return d.v; })) + ' days in the typical state, from ' + Math.min.apply(null, pubD.map(function (d) { return d.v; })) + ' to ' + Math.max.apply(null, pubD.map(function (d) { return d.v; })) + '.</b> ' +
    (longest.pub ? '' : longest.name + '\'s, if its final roll comes out on the date now set, will have taken ' + longest.v + ' days, the longest of all.');

  var link = function (s) { return '<a href="../../' + (PAGE[s] || 'india/process/#' + key(s)) + '">' + E(s) + '</a>'; };
  document.getElementById('tStage').innerHTML = '<thead><tr><th class="l">State or union territory</th><th>Phase</th><th>Draft roll</th><th>Final roll</th><th class="l">Stage</th></tr></thead><tbody>' +
    rows.map(function (x) {
      return '<tr><td class="l">' + link(x.state) + '</td><td>' + x.phase + '</td><td>' + (S[x.state] && S[x.state].removed ? SIR.date(x.m.draft) : 'not yet') + '</td><td>' +
        (x.pub ? (x.pubDate ? SIR.date(x.pubDate) : 'published, day not found') : x.rp ? 'reported for ' + SIR.date(x.rp.final) + ' (press)' : x.m.final ? 'due ' + SIR.date(x.m.final) : '') + '</td><td class="l"><span class="stage ' + x.cls + '">' + E(x.stage) + '</span></td></tr>';
    }).join('') + '</tbody>';
  var reps = rows.filter(function (x) { return x.rp && !x.pub; });
  document.getElementById('nOut').innerHTML = (reps.length ? 'The final roll dates for ' + reps.map(function (x) { return '<a href="' + E(x.rp.url) + '" rel="noopener" target="_blank">' + E(x.state) + '</a> (' + E(x.rp.outlet) + ', ' + SIR.date(x.rp.date) + ')'; }).reduce(function (a, t, i, all) { return a + (i === 0 ? '' : i === all.length - 1 ? ' and ' : ', ') + t; }, '') + ' are as the press reported them, and are marked press. No order or note confirms them, so the calendar keeps the last dates a document set. ' : '') + 'Assam, which was given a special revision in place of an intensive one, and Himachal Pradesh, Jammu and Kashmir and Ladakh, whose dates the Commission said it would announce later, are not in the table.';
  SIR.tools();
}).catch(SIR.fail);
