Promise.all([SIR.json('data/india/reserved.json'), SIR.json('data/india/states.json'), SIR.json('data/india/border.json')]).then(function (r) {
  var R = r[0].states, S = r[1].states, F = r[1].final, B = r[2];
  var p1 = function (x) { return x == null ? null : SIR.d(x, 1); };
  var sign = function (x) { return x == null ? '–' : (x > 0 ? '+' : '') + SIR.d(x, 1); };
  var list = function (a) { return a.join(', ').replace(/, ([^,]*)$/, ' and $1'); };
  var MEAS = { left_off: 'names left off', fall: 'fall in the roll' };

  // reserved seats
  VIZ.dots('vRes', { label: 'General, SC and ST seats, names lost per 100 electors in each state\'s own measure', axis: 'Per 100 electors, in each state\'s own measure',
    cats: R.map(function (s) { return s.state; }),
    series: [{ name: 'General seats', col: '--fill-grey', vals: R.map(function (s) { return s.GEN.rate; }) },
             { name: 'SC seats', col: '--fill-red', vals: R.map(function (s) { return s.SC ? s.SC.rate : null; }) },
             { name: 'ST seats', col: '--fill-navy', vals: R.map(function (s) { return s.ST ? s.ST.rate : null; }) }] });
  document.getElementById('nRes').textContent = 'Bihar, Tamil Nadu, Gujarat and Delhi are measured by the names left off the draft. West Bengal and Kerala published no names left off below the state, so they are measured by the fall in the roll to the draft. Read each state as its own row. Delhi has no ST seats.';
  VIZ.strip('vResGap', { label: 'Each reserved seat against the general seats of its own district', axis: 'Names per 100 above or below the general seats of the same district', step: 2, r: 4.5,
    key: [['SC seat', '--fill-red'], ['ST seat', '--fill-navy']],
    rows: R.map(function (s) {
      var pts = [];
      ['SC', 'ST'].forEach(function (c) { if (s[c]) s[c].each.forEach(function (e) { pts.push({ v: e.gap, tok: c === 'SC' ? '--fill-red' : '--fill-navy', label: e.name + ' (' + c + '), ' + e.district + ': ' + sign(e.gap) + ' per 100' }); }); });
      return { name: s.state, points: pts };
    }) });
  var lower = function (c) { return R.filter(function (s) { return s[c] && s[c].rate < s.GEN.rate; }).length; };
  var withC = function (c) { return R.filter(function (s) { return s[c]; }).length; };
  var dist = function (c) { return R.filter(function (s) { return s[c] && s[c].gap_vs_district != null && s[c].gap_vs_district < 0; }).length; };
  var distN = function (c) { return R.filter(function (s) { return s[c] && s[c].gap_vs_district != null; }).length; };
  var above = R.reduce(function (a, s) { return a + ['SC', 'ST'].reduce(function (b, c) { return b + (s[c] ? s[c].above_district : 0); }, 0); }, 0);
  var compared = R.reduce(function (a, s) { return a + ['SC', 'ST'].reduce(function (b, c) { return b + (s[c] ? s[c].compared : 0); }, 0); }, 0);
  document.getElementById('nResGap').textContent = 'Each dot is one reserved seat. A dot to the right of zero lost more names than the general seats of its own district. ' + above + ' of the ' + compared + ' reserved seats did.';
  document.getElementById('fRes').innerHTML = '<b>Seats reserved for Scheduled Castes lost a smaller share of their roll than general seats in ' + lower('SC') + ' of ' + withC('SC') + ' states, and seats reserved for Scheduled Tribes in ' + lower('ST') + ' of ' + withC('ST') + '.</b> Part of that comes from where reserved seats are. Set against the general seats of their own district, SC seats were still lower on average in ' + dist('SC') + ' of ' + distN('SC') + ' states, by a smaller margin, and in every state some reserved seats lost more than the general seats around them.';
  SIR.table('tRes', [{ h: 'State' }, { h: 'General seats', num: true }, { h: 'SC seats', num: true }, { h: 'ST seats', num: true }, { h: 'SC seats higher than their district', num: true }, { h: 'ST seats higher than their district', num: true }],
    R.map(function (s) {
      return [s.state + '<small>' + s.unit + '</small>', p1(s.GEN.rate) + ' <small>' + s.GEN.seats + ' seats</small>',
        s.SC ? p1(s.SC.rate) + ' <small>' + s.SC.seats + ' seats</small>' : null, s.ST ? p1(s.ST.rate) + ' <small>' + s.ST.seats + ' seats</small>' : null,
        s.SC && s.SC.compared ? s.SC.above_district + ' of ' + s.SC.compared : null, s.ST && s.ST.compared ? s.ST.above_district + ' of ' + s.ST.compared : null];
    }));

  // how much came back
  var fin = S.filter(function (s) { return s.made_up_pct != null; }).sort(function (a, b) { return b.made_up_pct - a.made_up_pct; });
  var flag = function (s) { return s.reconciles === 'net only' ? 'net figure only' : s.reconciles === 'no' ? 'figures do not add up' : s.reconciles === 'rounded' ? 'rounded' : ''; };
  VIZ.rank('vBack', { label: 'The rise from the draft to the final roll as a share of the names the draft left off', axis: 'Per cent of the names left off at the draft', fmt: function (v) { return SIR.d(v, 1) + '%'; },
    rows: fin.map(function (s) { return { name: s.state, v: s.made_up_pct, col: s.made_up_pct < 0 ? '--fill-grey' : '--fill-red' }; }) });
  var flagged = fin.filter(function (s) { return flag(s); });
  document.getElementById('nBack').textContent = 'Grey stems are states whose roll shrank again after the draft. Some figures carry a caution. ' + flagged.map(function (s) { return s.state + ' (' + flag(s) + ')'; }).join(', ') + '.';
  var neg = fin.filter(function (s) { return s.made_up_pct < 0; });
  var under25 = fin.filter(function (s) { return s.made_up_pct < 25; }).length;
  var pooled = 'Taken together, the ' + F.states + ' final rolls made up at most ' + SIR.pct(F.made_up_pct) + ' of the names the drafts left off, or ' + SIR.pct(F.made_up_pct_ex_withheld) + ' leaving out West Bengal\'s ' + SIR.lk(F.withheld, 0) + ' names held for adjudication.';
  document.getElementById('fBack').innerHTML = '<b>' + pooled + '</b> By state the share runs from ' + SIR.pct(fin[0].made_up_pct) + ' in ' + fin[0].state + ' to below zero in ' + neg.length + ' (' + list(neg.map(function (s) { return s.state; })) + '), where the roll shrank again after the draft. In ' + under25 + ' of the ' + fin.length + ' it was under a quarter, those ' + neg.length + ' included. West Bengal\'s further fall is mostly the names held back for adjudication.';
  SIR.table('tBack', [{ h: 'State' }, { h: 'Share made up', num: true }, { h: 'Caution' }],
    fin.map(function (s) { return [SIR.esc(s.state), SIR.pct(s.made_up_pct), flag(s) || null]; }));

  // borders
  var bs = B.states, pct = function (a, b) { return 100 * (a / b - 1); };
  var near = function (s) { return Math.abs(s.ratio - 1) < 0.02; };
  var up = bs.filter(function (s) { return s.ratio >= 1.02; }), even = bs.filter(near), down = bs.filter(function (s) { return s.ratio <= 0.98; });
  VIZ.rank('vBorder', { label: 'The border districts\' rate against the rest of the state', axis: 'Per cent higher or lower than the rest of the state', fmt: function (v) { return (v > 0 ? '+' : '') + SIR.d(v, 1) + '%'; },
    rows: bs.slice().sort(function (a, b) { return b.ratio - a.ratio; }).map(function (s) { return { name: s.state, v: pct(s.border.rate, s.interior.rate), col: s.ratio > 1 ? '--fill-red' : '--fill-grey' }; }) });
  var wb = bs.filter(function (s) { return s.state === 'West Bengal'; })[0];
  document.getElementById('nBorder').innerHTML = 'Each state is measured as its own page measures it. Uttar Pradesh, Gujarat and Uttarakhand by the names left off, Bihar by the names left off or deleted in both phases, and West Bengal by the fall in the roll. The large cities lost the most names and none of them is on the border. Leave Kolkata out and West Bengal\'s border districts fell by ' + p1(wb.border.rate) + ' per 100, against ' + p1(wb.interior_without_city.rate) + ' in the rest of the state.';
  VIZ.strip('vBorderD', { label: 'Each border district against the rest of its state', axis: 'Per cent higher or lower than the rest of the state', step: 20,
    rows: bs.map(function (s) { return { name: s.state, points: s.districts.map(function (x) { var v = pct(x.rate, s.interior.rate); return { v: v, tok: v > 0 ? '--fill-red' : '--fill-grey', label: x.district + ', ' + s.state + ': ' + (v > 0 ? '+' : '') + SIR.d(v, 0) + '%' }; }) }; }) });
  document.getElementById('nBorderD').textContent = 'Each dot is one border district. The number that lost more than the rest of their state was ' + list(bs.map(function (s) { return s.above + ' of ' + s.districts.length + ' in ' + s.state; })) + '.';
  var why = bs.filter(function (s) { return s.border.elsewhere_share != null; });
  VIZ.dots('vBorderWhy', { label: 'Names entered as enrolled elsewhere, border districts and the rest', axis: 'Per cent of the names left off',
    cats: why.map(function (s) { return s.state; }),
    series: [{ name: 'Rest of the state', col: '--fill-grey', vals: why.map(function (s) { return s.interior.elsewhere_share; }) }, { name: 'Border districts', col: '--fill-red', vals: why.map(function (s) { return s.border.elsewhere_share; }) }] });
  document.getElementById('nBorderWhy').textContent = 'Uttar Pradesh and Gujarat are the two states that published reasons by district. In both, a larger share of the border districts\' names were entered as enrolled somewhere else. A reason is what the officer wrote down, and nobody checked it. Enrolled elsewhere means on another roll in India, and it says nothing about anyone\'s citizenship.';
  document.getElementById('fBorder').innerHTML = '<b>The border districts show no single pattern.</b> They lost more than the rest of their state in ' + list(up.map(function (s) { return s.state; })) + ', about the same in ' + list(even.map(function (s) { return s.state; })) + ', and fewer in ' + list(down.map(function (s) { return s.state; })) + '. Bihar\'s seven border districts are the same seven Nepal-border districts the <a href="../../bihar/border/">Bihar border page</a> studies in more detail. Rajasthan is left out, because its district figure is the change in the roll over more than two years, and Barmer, one of its four border districts, was split in 2023.';
  SIR.table('tBorder', [{ h: 'State' }, { h: 'Border districts', num: true }, { h: 'Rest of the state', num: true }, { h: 'Rest, without the city', num: true }, { h: 'Border districts higher', num: true }],
    bs.map(function (s) {
      return ['<a href="../../' + s.page + '">' + SIR.esc(s.state) + '</a><small>' + s.unit + '</small>', p1(s.border.rate) + ' <small>' + s.border.districts + ' districts</small>', p1(s.interior.rate),
        s.interior_without_city ? p1(s.interior_without_city.rate) + ' <small>without ' + list(s.city_districts) + '</small>' : null, s.above + ' of ' + s.districts.length];
    }));

  SIR.inShort([
    'Seats reserved for Scheduled Castes lost a smaller share of their roll than general seats in ' + lower('SC') + ' of ' + withC('SC') + ' states, and seats reserved for Scheduled Tribes in ' + lower('ST') + ' of ' + withC('ST') + '.',
    'Part of the gap comes from where the seats are. Against the general seats of their own district, SC seats were lower on average in ' + dist('SC') + ' of ' + distN('SC') + ' states, by a smaller margin.',
    pooled + ' By state the share runs from ' + SIR.pct(fin[0].made_up_pct) + ' in ' + fin[0].state + ' to below zero in ' + neg.length + ', where the roll shrank again.',
    'On the Government of India\'s own list of border districts, the border lost more names than the rest of its state in ' + list(up.map(function (s) { return s.state; })) + ', about the same in ' + list(even.map(function (s) { return s.state; })) + ' and fewer in ' + list(down.map(function (s) { return s.state; })) + '.'
  ], 'A reserved seat describes a place, and says nothing about which electors there were left off or deleted. The rise to the final roll includes new voters, so the share made up is a ceiling. A border district\'s rate says nothing about any elector\'s citizenship.');
  SIR.showFaq('india', 'compare');
}).catch(SIR.fail);
