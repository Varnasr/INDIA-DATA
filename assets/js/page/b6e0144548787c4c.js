Promise.all([SIR.json('data/uttarakhand/summary.json'), SIR.json('data/uttarakhand/districts.json'), SIR.json('data/uttarakhand/constituencies.json'), SIR.json('data/india/notices.json')]).then(function (r) {
  var S = r[0], D = r[1], A = r[2], NT = r[3].states.filter(function (x) { return x.state === 'Uttarakhand'; })[0], n = SIR.n, d1 = function (v) { return SIR.d(v, 1); };
  var lk = function (x) { return SIR.lk(x, 2); };
  var PL = function (x) { return x.plains ? '--fill-red' : '--fill-navy'; };

  VIZ.waterfall('vWater', { label: 'Uttarakhand: the roll before the revision, the draft of 14 July and the final roll of 3 October 2026', from: Math.floor(S.draft * 0.85 / 1e6) * 1e6, steps: [
    { name: 'Roll before the revision', v: S.roll_before, kind: 'total' }, { name: 'Left off the draft', v: S.left_off, kind: 'down' }, { name: 'Draft roll', v: S.draft, kind: 'total' },
    { name: 'Added after the draft', v: S.claims, kind: 'up' }, { name: 'Deleted after the draft', v: S.objections, kind: 'down' }, { name: 'Final roll', v: S.final, kind: 'total' }] });
  document.getElementById('fWater').innerHTML = '<b>The draft roll left off ' + lk(S.left_off) + ' names, ' + d1(S.per_100) + ' of every 100 electors, and the final roll is ' + lk(-S.final_vs_before) + ' smaller than the roll before the revision.</b> After the draft, ' + lk(S.claims) + ' names were added and ' + lk(S.objections) + ' deleted. The net rise of ' + n(S.net) + ' is ' + d1(S.made_up_pct) + ' for every 100 left off, and it counts people enrolling for the first time, so fewer than that were put back.';

  VIZ.lollipop('vReason', { label: 'Names left off the draft, by the reason entered', axis: 'Lakh',
    rows: [['Absent or shifted', S.reasons.absent_or_shifted], ['Dead', S.reasons.dead], ['Enrolled at more than one place', S.reasons.duplicate], ['Other', S.reasons.other]].map(function (x) { return { name: x[0], v: x[1] / 1e5, text: lk(x[1]), tok: '--fill-navy', hi: true }; }) });
  document.getElementById('fReason').innerHTML = '<b>' + SIR.pct(S.shares.absent_or_shifted) + ' were entered as absent or shifted, ' + SIR.pct(S.shares.dead) + ' as dead and ' + SIR.pct(S.shares.duplicate) + ' as enrolled at more than one place.</b> The Chief Electoral Officer did not separate absent from shifted, and published no split of the reasons by district or by sex.';

  VIZ.strip('vLeft', { label: 'Names left off the draft per 100 on the roll before, every constituency, by district', axis: 'Left off the draft, per 100 on the roll before', r: 4.5,
    key: [['Plains districts', '--fill-red'], ['Hill districts', '--fill-navy']],
    rows: D.slice().sort(function (a, b) { return b.left_off_per_100 - a.left_off_per_100; }).map(function (d) { return { name: d.district, tok: PL(d),
      points: A.filter(function (a) { return a.district === d.district; }).map(function (a) { return { v: a.left_off_per_100, label: a.name + ': ' + n(a.left_off) + ' left off, ' + d1(a.left_off_per_100) + ' per 100' }; }) }; }) });
  document.getElementById('fLeft').innerHTML = '<b>' + S.lo_max + ' lost ' + d1(S.lo_max_v) + ' of every 100 names on its roll before the revision, and ' + S.lo_max2 + ' ' + d1(S.lo_max2_v) + '. ' + S.lo_min + ' lost ' + d1(S.lo_min_v) + ', the fewest.</b> ' + S.acs_lo_over_state + ' of the 70 constituencies lost more than the state\'s ' + d1(S.per_100) + '. By district, ' + S.dist_lo_max + ' lost the most, ' + d1(S.dist_lo_max_v) + ' per 100, and ' + S.dist_lo_min + ' the fewest, ' + d1(S.dist_lo_min_v) + '. The plains districts lost ' + d1(S.plains.left_off_per_100) + ' per 100 and the hill districts ' + d1(S.hills.left_off_per_100) + '. The table gives no reason or sex below the state.';

  VIZ.scatter('vAfter', { label: 'Names added and deleted after the draft, per 1,000 on each constituency\'s draft roll', diag: true, xMin: 0, yMin: 0,
    xAxis: 'Added after the draft, per 1,000 on the draft', yAxis: 'Deleted after the draft, per 1,000', diagLabel: 'deleted = added',
    key: [['Plains districts', '--fill-red'], ['Hill districts', '--fill-navy']],
    points: A.map(function (a) { return { x: a.claims_per_1000, y: a.objections_per_1000, tok: PL(a), label: a.name + ' (' + a.district + '): ' + n(a.claims) + ' added, ' + n(a.objections) + ' deleted' }; }) });
  var lost = A.filter(function (a) { return a.net < 0; }), lostPl = lost.filter(function (a) { return a.plains; }).length;
  document.getElementById('fAfter').innerHTML = '<b>In ' + S.acs_lost + ' of the 70 constituencies more names were deleted after the draft than added, and ' + (lostPl === lost.length ? 'all of them are' : lostPl + ' of them are') + ' in the plains districts.</b> ' + S.obj_max + ' deleted the most, ' + d1(S.obj_max_v) + ' for every 1,000 on its draft, and ' + S.obj_min + ' the fewest, ' + d1(S.obj_min_v) + '. Across the state, ' + d1(S.claims_per_1000) + ' were added and ' + d1(S.objections_per_1000) + ' deleted for every 1,000 on the draft.';

  VIZ.lollipop('vPlains', { label: 'The plains districts\' share of the roll before, of the names left off, of the notices, of the draft roll and of the names added and deleted after it', axis: 'Per cent', max: 100, step: 20, ref: S.plains.draft_pct,
    rows: [['Roll before the revision', S.plains.roll_before_pct, '--fill-navy'], ['Left off the draft', S.plains.left_off_pct, '--fill-red'], ['Notices', S.plains.notices_pct, '--fill-red'], ['Draft roll', S.plains.draft_pct, '--fill-navy'], ['Added after the draft', S.plains.claims_pct, '--fill-teal'], ['Deleted after the draft', S.plains.objections_pct, '--fill-red']].map(function (x) { return { name: x[0], v: x[1], text: SIR.pct(x[1]), tok: x[2], hi: true }; }) });
  document.getElementById('fPlains').innerHTML = '<b>The plains districts held ' + SIR.pct(S.plains.roll_before_pct) + ' of the roll before the revision, and account for ' + SIR.pct(S.plains.left_off_pct) + ' of the names left off the draft, ' + SIR.pct(S.plains.notices_pct) + ' of the notices and ' + SIR.pct(S.plains.objections_pct) + ' of the names deleted after it.</b> Their share grows at every step. They deleted ' + d1(S.plains.objections_per_1000) + ' for every 1,000 on the draft and added ' + d1(S.plains.claims_per_1000) + ', so their rolls ' + (S.plains.net_per_1000 < 0 ? 'shrank' : 'grew') + ' by ' + d1(Math.abs(S.plains.net_per_1000)) + ' per 1,000. The hill districts deleted ' + d1(S.hills.objections_per_1000) + ' and added ' + d1(S.hills.claims_per_1000) + ', and their rolls grew by ' + d1(S.hills.net_per_1000) + ' per 1,000.';

  VIZ.strip('vDist', { label: 'Names deleted after the draft per 1,000 on the draft roll, every constituency, by district', axis: 'Deleted after the draft, per 1,000 on the draft roll', r: 4.5,
    key: [['Plains districts', '--fill-red'], ['Hill districts', '--fill-navy']],
    rows: D.map(function (d) { return { name: d.district, tok: PL(d),
      points: A.filter(function (a) { return a.district === d.district; }).map(function (a) { return { v: a.objections_per_1000, label: a.name + ': ' + d1(a.objections_per_1000) + ' per 1,000' }; }) }; }) });
  document.getElementById('fDist').innerHTML = '<b>' + D[0].district + ' deleted ' + d1(D[0].objections_per_1000) + ' for every 1,000 on its draft, the most of the 13 districts.</b> ' + D[1].district + ' and ' + D[2].district + ' come next, at ' + d1(D[1].objections_per_1000) + ' and ' + d1(D[2].objections_per_1000) + '. ' + D[D.length - 1].district + ' deleted the fewest, ' + d1(D[D.length - 1].objections_per_1000) + '.';

  VIZ.scatter('vWomen', { label: 'Women\'s share of each constituency\'s draft roll and of the names deleted from it after the draft', diag: true,
    xAxis: 'Women, per cent of the draft roll', yAxis: 'Women, per cent of those deleted after the draft', diagLabel: 'same share',
    key: [['Plains districts', '--fill-red'], ['Hill districts', '--fill-navy']],
    points: A.map(function (a) { return { x: a.women_draft_pct, y: a.women_objections_pct, tok: PL(a), label: a.name + ': women ' + SIR.pct(a.women_draft_pct) + ' of the draft, ' + SIR.pct(a.women_objections_pct) + ' of the ' + n(a.objections) + ' deleted' }; }) });
  var big = A.filter(function (a) { return a.women_objections_gap >= 10; }).sort(function (a, b) { return b.women_objections_gap - a.women_objections_gap; });
  document.getElementById('fWomen').innerHTML = '<b>Women were ' + SIR.pct(S.women_draft_pct) + ' of the draft roll and ' + SIR.pct(S.women_objections_pct) + ' of the names deleted after it, more than their share in ' + S.acs_women_over + ' of the 70 constituencies.</b> In ' + big.length + ' the gap is 10 points or more, among them ' + (function (a) { return a.length < 2 ? a.join('') : a.slice(0, -1).join(', ') + ' and ' + a[a.length - 1]; })(big.slice(0, 4).map(function (a) { return a.name + ' (' + SIR.pct(a.women_objections_pct) + ' of ' + n(a.objections) + ')'; })) + '. Women were also ' + SIR.pct(S.women_claims_pct) + ' of the names added, and ' + SIR.pct(S.women_final_pct) + ' of the final roll.';

  VIZ.scatter('vNotice', { label: 'Notices per 100 on the draft and names deleted after the draft per 1,000, by constituency', xMin: 0, yMin: 0,
    xAxis: 'Notices, per 100 on the draft roll', yAxis: 'Deleted after the draft, per 1,000',
    key: [['Plains districts', '--fill-red'], ['Hill districts', '--fill-navy']],
    points: A.map(function (a) { return { x: a.notices_per_100, y: a.objections_per_1000, tok: PL(a), label: a.name + ': ' + n(a.notices) + ' notices, ' + n(a.objections) + ' deleted after the draft' }; }) });
  document.getElementById('fNotice').innerHTML = '<b>' + lk(S.notices) + ' electors on the draft, ' + d1(S.notices_per_100) + ' of every 100, were in line for a notice: ' + lk(S.no_mapping) + ' with no mapping to the 2003 roll and ' + lk(S.anomalies) + ' with an anomaly.</b> The constituencies with more notices deleted more names after the draft (rank correlation ' + SIR.d(S.rho_notices_objections, 2) + '), and the notices tie the two counts together more closely than the names left off do (' + SIR.d(S.rho_lo_objections, 2) + '). The plains districts had ' + d1(S.plains.notices_per_100) + ' notices per 100 on the draft and the hills ' + d1(S.hills.notices_per_100) + '. The table does not say how many notices were served or heard in each constituency. The Indian Express reported on 3 October, from the Chief Electoral Officer\'s presentation, that 97,186 of the 1,04,708 names deleted after the draft were electors found ineligible after a notice, and that would explain the link. The presentation itself has not been found.';

  document.getElementById('fNext').innerHTML = 'With the final roll, the Chief Electoral Officer told booth officers to compare it with the roll from before the revision, visit the people missing from it, help those still eligible fill in Form 6, and share the lists with the parties\' booth agents. The steps are on <a href="../india/process/#t-2026-10-03">How the revision was run</a>.';

  SIR.table(document.getElementById('tDist'), [
    { k: 'district', label: 'District', left: true }, { k: 'acs', label: 'Seats' }, { k: 'roll_before', label: 'Roll before', fmt: n }, { k: 'left_off', label: 'Left off', fmt: n }, { k: 'left_off_per_100', label: 'Left off per 100', fmt: d1 }, { k: 'notices_per_100', label: 'Notices per 100 on draft', fmt: d1 }, { k: 'draft', label: 'Draft roll', fmt: n },
    { k: 'claims', label: 'Added', fmt: n }, { k: 'objections', label: 'Deleted', fmt: n }, { k: 'final', label: 'Final roll', fmt: n },
    { k: 'objections_per_1000', label: 'Deleted per 1,000', fmt: d1 }, { k: 'women_objections_pct', label: 'Women, % of deleted', fmt: d1 }], D, { sort: 'left_off_per_100' });
  SIR.table(document.getElementById('tAc'), [
    { k: 'ac', label: 'No.' }, { k: 'name', label: 'Constituency', left: true }, { k: 'district', label: 'District', left: true },
    { k: 'roll_before', label: 'Roll before', fmt: n }, { k: 'left_off', label: 'Left off', fmt: n }, { k: 'left_off_per_100', label: 'Left off per 100', fmt: d1 }, { k: 'notices_per_100', label: 'Notices per 100 on draft', fmt: d1 },
    { k: 'draft', label: 'Draft roll', fmt: n }, { k: 'claims', label: 'Added', fmt: n }, { k: 'objections', label: 'Deleted', fmt: n }, { k: 'final', label: 'Final roll', fmt: n },
    { k: 'net_per_1000', label: 'Change per 1,000', fmt: d1 }, { k: 'objections_per_1000', label: 'Deleted per 1,000', fmt: d1 },
    { k: 'women_objections_pct', label: 'Women, % of deleted', fmt: d1 }], A, { sort: 'left_off_per_100' });

  var seatsOf = function (d) { return A.filter(function (a) { return a.district === d.district; }); };
  var DSET = { rows: D, key: function (d) { return SIR.slug(d.district); }, label: function (d) { return d.district + ' district'; },
    card: function (d) { return SIR.facts([['Roll before the revision', n(d.roll_before)], ['Left off the draft', n(d.left_off)], ['Left off per 100', d1(d.left_off_per_100)], ['Notices', n(d.notices)], ['Draft roll', n(d.draft)], ['Added after the draft', n(d.claims)], ['Deleted after the draft', n(d.objections)], ['Final roll', n(d.final)], ['Deleted per 1,000 on the draft', d1(d.objections_per_1000)], ['Women, share of those deleted', SIR.pct(d.women_objections_pct)], ['Constituencies', n(d.acs)]]) + '<p class="note">Its constituencies</p>' + SIR.goList(seatsOf(d), function (a) { return 'ac-' + a.ac; }, function (a) { return a.ac + '. ' + a.name; }); },
    pick: function (d) { var b = document.getElementById('vMap'); if (b.__select) b.__select(seatsOf(d).map(function (a) { return a.ac; })); },
    share: function (d) { return d.district + ' district, Uttarakhand. The SIR draft roll left off ' + n(d.left_off) + ' names, ' + d1(d.left_off_per_100) + ' of every 100 on the roll before. After the draft, ' + n(d.claims) + ' names were added and ' + n(d.objections) + ' deleted, and the final roll holds ' + n(d.final) + '. These are counts from the Chief Electoral Officer\'s tables of the draft and the final roll.'; } };
  var F = SIR.finder('finder', { seatPages: true, districtPages: true, rows: A, more: [DSET], prompt: 'Find a constituency or district', placeholder: 'Type a name, a number or a district', key: function (a) { return 'ac-' + a.ac; }, label: function (a) { return a.ac + '. ' + a.name + ' (' + a.district + ')'; },
    pick: function (a) { var b = document.getElementById('vMap'); if (b.__select) b.__select(a.ac); },
    card: function (a) { return SIR.facts([['Roll before the revision', n(a.roll_before)], ['Left off the draft', n(a.left_off)], ['Left off per 100', d1(a.left_off_per_100)], ['Notices', n(a.notices)], ['Draft roll', n(a.draft)], ['Added after the draft', n(a.claims)], ['Deleted after the draft', n(a.objections)], ['Final roll', n(a.final)],
      ['Deleted per 1,000 on the draft', d1(a.objections_per_1000)], ['Women, share of the draft', SIR.pct(a.women_draft_pct)], ['Women, share of those deleted', SIR.pct(a.women_objections_pct)]]); },
    share: function (a) { return a.name + ', Uttarakhand. The SIR draft roll left off ' + n(a.left_off) + ' names, ' + d1(a.left_off_per_100) + ' of every 100 on the roll before. After the draft, ' + n(a.claims) + ' names were added and ' + n(a.objections) + ' deleted, and the final roll holds ' + n(a.final) + '. Women were ' + SIR.pct(a.women_objections_pct) + ' of those deleted. These are counts from the Chief Electoral Officer\'s tables of the draft and the final roll.'; } });
  SIR.json('data/geo/uttarakhand.json').then(function (geo) {
    var byAc = {}; A.forEach(function (a) { byAc[a.ac] = a; });
    VIZ.map('vMap', { geo: geo, label: 'Map of names left off the draft per 100 on the roll before, by constituency', title: 'Left off per 100',
      v: function (ac) { return byAc[ac] ? byAc[ac].left_off_per_100 : null; }, name: function (ac) { return byAc[ac] ? byAc[ac].name : ''; },
      pick: function (ac) { if (byAc[ac]) F.select(byAc[ac]); } });
    var it = F.item[SIR.hashId()]; if (it && it.s.pick) it.s.pick(it.r);
    SIR.tools();
  });
  SIR.showFaq('uk', 'main');
}).catch(SIR.fail);
