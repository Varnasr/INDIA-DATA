SIR.json('data/india/nrc.json').then(function (D) {
  var F = {}, num = {}, k = 0, n = SIR.n, esc = SIR.esc;
  D.sections.forEach(function (s) { s.facts.forEach(function (f) { F[f.id] = f; num[f.id] = ++k; }); });
  var ref = function (ids) { return ' <span class="nref">' + ids.map(function (id) { return '<a href="#f-' + id + '">' + num[id] + '</a>'; }).join(', ') + '</span>'; };
  var G = D.figures, NW = D.nationwide;

  SIR.inShort([
    'The lists published on 31 August 2019 found ' + n(G.final_eligible) + ' people eligible for Assam\'s NRC and left ' + n(G.final_left_out) + ' out.',
    'In March 2021 the Ministry of Home Affairs told Parliament that the final NRC for Assam had not been issued. In December 2021 it said no rejection orders had gone out, so no one left out had yet appealed. No later statement was found.',
    'In answers to the Lok Sabha from ' + SIR.date(NW.dates[0]) + ' to ' + SIR.date(NW.latest) + ', the Government said it had taken no decision to prepare an NRC for the whole country.',
    'The SIR was ordered under the law on electoral rolls. The Supreme Court held on 27 May 2026 that declining to enrol someone does not declare that person not to be a citizen, and that deciding citizenship belongs to the authority under the Citizenship Act.',
    'The order for Assam\'s Special Revision of 2025-26 does not mention the NRC.'
  ], 'Every statement here comes from a primary document and links to it. Nothing on this page says whether any person is a citizen.');

  document.getElementById('kpis').innerHTML = [
    [n(G.final_left_out), 'left out of the lists for Assam, 31 August 2019'],
    [n(G.final_eligible), 'found eligible'],
    [SIR.date(NW.latest), 'the latest answer found: no decision on a nationwide NRC'],
    ['27 May 2026', 'the Supreme Court\'s judgment on the SIR']
  ].map(function (x) { return '<div><b>' + x[0] + '</b><span>' + x[1] + '</span></div>'; }).join('');

  var rows = [
    ['The law', 'Section 14A of the Citizenship Act, 1955, and the Rules of 2003' + ref(['legal_basis-01', 'legal_basis-04']), 'Article 324 of the Constitution and section 21 of the Representation of the People Act, 1950' + ref(['sir_vs_nrc-01', 'sir_vs_nrc-09'])],
    ['Who keeps it', 'The Registrar General of Citizen Registration' + ref(['legal_basis-07']), 'The Election Commission, through each constituency\'s Electoral Registration Officer' + ref(['sir_vs_nrc-02'])],
    ['What it records', 'Indian citizens, living in India or abroad' + ref(['legal_basis-05']), 'Electors, who under Article 326 must be citizens' + ref(['sir_vs_nrc-03'])],
    ['Where it has been done', 'Assam, under rules made for Assam alone. The Government has said it has taken no decision to prepare one for the whole country' + ref(['legal_basis-12', 'nationwide-05']), 'Bihar in 2025, then further states in phases from a second order of 27 October 2025' + ref(['sir_vs_nrc-01', 'sir_vs_nrc-05'])],
    ['What a person had to show', 'In Assam, that they or an ancestor lived in India on or before the cut-off date, through a listed document' + ref(['assam-13']), 'A form. In Bihar, those not on the 2003 roll had to give documents. The NRC is one item on the list of documents accepted' + ref(['sir_vs_nrc-04', 'sir_vs_nrc-06'])],
    ['What being left out means', 'A person left out may appeal to a Foreigners Tribunal within 120 days. No rejection orders had been issued by December 2021' + ref(['assam-19', 'assam-18']), 'A name off the roll. The Supreme Court held that this does not declare anyone not to be a citizen, and that doubtful cases go to the authority under the Citizenship Act' + ref(['sir_vs_nrc-12', 'sir_vs_nrc-13'])]
  ];
  SIR.table('tCompare', [{ h: '' }, { h: 'The NRC' }, { h: 'The SIR' }], rows);

  D.sections.forEach(function (s) {
    var box = document.getElementById('s-' + s.id);
    box.setAttribute('start', num[s.facts[0].id]);
    box.innerHTML = s.facts.map(function (f) {
      return '<li id="f-' + f.id + '"><p>' + esc(f.claim) + '</p><p class="nsrc"><a href="' + esc(f.url) + '" rel="noopener">' + esc(f.document) + '</a>, ' + esc(f.issuer) + ', ' + SIR.date(f.date) + (f.where ? ', ' + esc(f.where) : '') + '.</p>' +
        (f.quote ? '<details><summary>The words of the document</summary><blockquote>' + esc(f.quote) + '</blockquote></details>' : '') + '</li>';
    }).join('');
  });

  var nat = D.sections.filter(function (s) { return s.id === 'nationwide'; })[0].facts.filter(function (f) { return /no decision/.test(f.claim); });
  SIR.table('tNational', [{ h: 'Answered' }, { h: 'Answer' }, { h: 'Statement' }], nat.map(function (f) {
    return [SIR.date(f.date), '<a href="' + esc(f.url) + '" rel="noopener">' + esc(f.document) + '</a>', '<a href="#f-' + f.id + '">' + num[f.id] + '</a>'];
  }));

  VIZ.lollipop('vAssam', { label: 'Assam\'s NRC, the complete draft of 30 July 2018 and the lists of 31 August 2019', axis: 'Lakh',
    rows: [['Included in the complete draft, 2018', G.draft_included, '--fill-grey'], ['Rejected from the draft', G.draft_rejected, '--fill-red'], ['Kept on hold in the draft', G.draft_on_hold, '--fill-red'],
           ['Found eligible, 2019', G.final_eligible, '--fill-grey'], ['Left out, 2019', G.final_left_out, '--fill-red']]
      .map(function (r) { return { name: r[0], v: r[1] / 1e5, text: n(r[1]), tok: r[2], hi: true }; }) });
  document.getElementById('nAssam').textContent = 'The Supreme Court\'s order of 31 July 2018 gives the draft\'s exclusions in two parts, ' + n(G.draft_rejected) + ' rejected and ' + n(G.draft_on_hold) + ' kept on hold. The total it prints does not equal their sum, so no total is shown. The lists of 31 August 2019 are the supplementary list of inclusions and the list of exclusions. The Ministry said in 2021 that the final NRC had not been issued.';

  document.getElementById('reported').innerHTML = D.reported.map(function (r) {
    return '<li><p>' + esc(r.claim) + '</p><p class="nsrc"><a href="' + esc(r.url) + '" rel="noopener">' + esc(r.outlet) + '</a>, ' + SIR.date(r.date) + '.</p></li>';
  }).join('');
  document.getElementById('unsettled').innerHTML = D.unsettled.map(function (u) { return '<li>' + esc(u) + '</li>'; }).join('');

  SIR.showFaq('india', 'nrc');
  SIR.jump && SIR.jump();
}).catch(SIR.fail);
