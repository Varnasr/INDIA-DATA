SIR.json('data/india/cities.json').then(function (d) {
  var C = d.cities, S = d.summary;
  var p1 = function (x) { return SIR.d(x, 1); };
  var by = {}; C.forEach(function (c) { by[c.city] = c; });
  var ranked = C.filter(function (c) { return c.measure === 'left_off' && !c.roll_2025; }).sort(function (a, b) { return b.core.per_100 - a.core.per_100; });
  var vsState = ranked.filter(function (c) { return c.state !== 'Delhi'; });
  var rings = ranked.filter(function (c) { return c.ring; });
  var ringUp = rings.filter(function (c) { return c.ring.per_100 >= c.core.per_100; });
  var why = ranked.filter(function (c) { return c.core.shifted_absent_share != null; });
  var shMin = Math.min.apply(null, why.map(function (c) { return c.core.shifted_absent_share; })), shMax = Math.max.apply(null, why.map(function (c) { return c.core.shifted_absent_share; }));
  var top = ranked[0], pat = by.Patna, kol = by.Kolkata, koc = by.Kochi;
  var name = function (c) { return c.city + (c.reported ? ' (as reported)' : ''); };

  SIR.inShort([
    (S.above_state === S.compared ? 'In all ' + S.compared + ' large cities measured by the names left off that can be set against a state (Delhi is a city and a state at once), the city lost a larger share of its roll than its state did, between ' : 'In ' + S.above_state + ' of ' + S.compared + ' large cities measured by the names left off, the city lost a larger share of its roll than its state did. The city\'s rate ran from ') + p1(S.times_min) + (S.above_state === S.compared ? ' and ' : ' to ') + p1(S.times_max) + ' times the state\'s rate.',
    top.city + ' lost ' + p1(top.core.per_100) + ' of every 100 electors, the most of any city, against ' + p1(top.state_per_100) + ' in ' + top.state + '. Its districts held ' + p1(top.share_of_roll) + '% of the state\'s roll and ' + p1(top.share_of_removed) + '% of the names left off.',
    'The suburbs lost fewer names than the city itself in ' + (rings.length - ringUp.length) + ' of ' + rings.length + ' cities. ' + (ringUp.length ? ringUp.map(function (c) { return c.city; }).join(' and ') + (ringUp.length > 1 ? ' are' : ' is') + ' the exception. ' + ringUp.map(function (c) { return c.ring.districts.join(' and ') + ' lost ' + p1(c.ring.per_100) + ' per 100, against ' + p1(c.core.per_100) + ' in ' + c.city + ' itself.'; }).join(' ') : ''),
    'Where the reasons were published, ' + Math.round(shMin) + ' to ' + Math.round(shMax) + ' of every 100 names left off in a city were entered as shifted or absent.',
    'Patna lost ' + p1(pat.core.per_100) + ' per 100 against ' + p1(pat.state_per_100) + ' for Bihar, the one city that lost fewer names than its state.'
  ], 'A city here is its districts, drawn differently from city to city, and Kolkata and Kochi are measured by the fall in the roll. A reason is what the officer wrote down, and nobody checked it.');

  document.getElementById('kpis').innerHTML = [
    [vsState.filter(function (c) { return c.core.per_100 > c.state_per_100; }).length + ' of ' + vsState.length, 'cities that lost more than their state'],
    [p1(S.times_min) + ' to ' + p1(S.times_max), 'times the state\'s rate'],
    [p1(top.core.per_100), 'per 100 in ' + top.city + ', the most'],
    [(rings.length - ringUp.length) + ' of ' + rings.length, 'suburbs that lost less than the city']
  ].map(function (k) { return '<div><b>' + k[0] + '</b><span>' + k[1] + '</span></div>'; }).join('');

  // the city against its state
  VIZ.dumbbell('vCity', { label: 'Names left off per 100 electors in each city and in its state', min: 0, step: 10,
    aName: 'The state, per 100', aTok: '--fill-grey', bName: 'The city, per 100', bTok: '--fill-red',
    rows: ranked.map(function (c) { return { name: name(c) + (c.state === 'Delhi' ? '' : ', ' + c.state), a: c.state_per_100, b: c.core.per_100 }; }) });
  document.getElementById('nCity').textContent = 'Delhi is a city and a state at once, so its grey dot and its red dot are the same figure.';

  var link = function (c) { return '<a href="../../' + c.page + '">' + name(c) + '</a>'; };
  var vs = ranked.filter(function (c) { return c.state !== 'Delhi'; });

  VIZ.dots('vWeight', { label: "Each city's share of its state's roll and of its names left off", axis: 'Per cent of the state',
    cats: vs.map(function (c) { return name(c); }),
    series: [{ name: "Share of the state's roll", col: '--fill-grey', vals: vs.map(function (c) { return c.share_of_roll; }) },
             { name: "Share of the state's names left off", col: '--fill-red', vals: vs.map(function (c) { return c.share_of_removed; }) }] });
  var mostW = vs.slice().sort(function (a, b) { return (b.share_of_removed - b.share_of_roll) - (a.share_of_removed - a.share_of_roll); })[0];
  document.getElementById('nWeight').textContent = mostW.city + ' held ' + p1(mostW.share_of_roll) + '% of ' + mostW.state + '\'s roll and ' + p1(mostW.share_of_removed) + '% of its names left off, the widest gap of any city. Delhi is left out of this chart because it is a city and a state at once.';

  VIZ.dots('vRing', { label: 'Names left off per 100 electors in the city, its suburbs and the rest of the state', axis: 'Names left off per 100 electors',
    cats: ranked.map(function (c) { return name(c); }),
    series: [{ name: 'Rest of the state', col: '--fill-grey', vals: ranked.map(function (c) { return c.rest ? c.rest.per_100 : null; }) },
             { name: 'Suburbs', col: '--fill-navy', vals: ranked.map(function (c) { return c.ring ? c.ring.per_100 : null; }) },
             { name: 'The city', col: '--fill-red', vals: ranked.map(function (c) { return c.core.per_100; }) }] });
  document.getElementById('nRing').textContent = 'Pune and Surat have no suburbs drawn, and Delhi has no rest of the state. Delhi\'s suburbs are measured on Uttar Pradesh\'s revision.';
  var and = function (a) { return a.join(', ').replace(/, ([^,]*)$/, ' and $1'); };
  var withRest = rings.filter(function (c) { return c.rest; });
  var noRest = rings.filter(function (c) { return !c.rest; });
  var both = withRest.filter(function (c) { return c.ring.per_100 < c.core.per_100 && c.rest.per_100 < c.ring.per_100; });
  var restUp = withRest.filter(function (c) { return c.ring.per_100 < c.core.per_100 && c.rest.per_100 >= c.ring.per_100; });
  document.getElementById('fRing').innerHTML = '<b>In ' + (rings.length - ringUp.length) + ' of ' + rings.length + ' cities with suburbs, the suburbs lost fewer names than the city.</b> ' +
    (ringUp.length ? ringUp.map(function (c) { return 'In ' + c.city + ' they lost more, because ' + c.ring.districts.join(' and ') + ' lost ' + p1(c.ring.per_100) + ' per 100, against ' + p1(c.core.per_100) + ' in the city\'s own districts.'; }).join(' ') + ' ' : '') +
    'The rate falls at both steps, from the city to its suburbs and again to the rest of the state, in ' + both.length + ' of ' + withRest.length + ' cities, ' + and(both.map(function (c) { return c.city; })) + '.' +
    (restUp.length ? ' In ' + and(restUp.map(function (c) { return c.city; })) + ' the rest of the state lost more than the suburbs.' : '') +
    (noRest.length ? ' ' + and(noRest.map(function (c) { return c.city; })) + ' is left out of that count because it is a city and a state at once, so it has no rest of the state.' : '');
  SIR.table('tRing', [{ h: 'City' }, { h: 'City', num: true }, { h: 'Suburbs', num: true }, { h: 'Rest of the state', num: true }, { h: 'Times the state', num: true }, { h: 'Share of the roll', num: true }, { h: 'Share left off', num: true }],
    ranked.map(function (c) {
      return [link(c) + '<small>' + c.state + ', per 100</small>', p1(c.core.per_100), c.ring ? p1(c.ring.per_100) + (c.ring.state !== c.state ? ' <small>' + c.ring.state + '</small>' : '') : null, c.rest ? p1(c.rest.per_100) : null,
        c.state === 'Delhi' ? null : p1(c.times_state), c.share_of_roll != null ? p1(c.share_of_roll) + '%' : null, c.share_of_removed != null ? p1(c.share_of_removed) + '%' : null];
    }));

  VIZ.dots('vWhy', { label: "Shares of each city's names left off entered as shifted or absent, and as dead", axis: 'Per cent of the city\'s names left off',
    cats: why.map(function (c) { return name(c); }),
    series: [{ name: 'Entered as dead', col: '--fill-grey', vals: why.map(function (c) { return c.core.dead_share; }) },
             { name: 'Entered as shifted or absent', col: '--fill-red', vals: why.map(function (c) { return c.core.shifted_absent_share; }) }] });
  var noWhy = ranked.filter(function (c) { return c.core.shifted_absent_share == null; }).map(function (c) { return c.city; });
  document.getElementById('nWhy').textContent = noWhy.length ? noWhy.join(', ').replace(/, ([^,]*)$/, ' and $1') + ' are left out because ' + (noWhy.length > 1 ? 'their states' : 'its state') + ' published no reasons by district.' : '';

  VIZ.dots('vFall', { label: 'The fall in the roll per 100 electors in Kolkata and Kochi, their suburbs and the rest of their states', axis: 'Fall in the roll per 100 electors',
    cats: [kol, koc].map(function (c) { return c.city; }),
    series: [{ name: 'Rest of the state', col: '--fill-grey', vals: [kol, koc].map(function (c) { return c.rest ? c.rest.per_100 : null; }) },
             { name: 'Suburbs', col: '--fill-navy', vals: [kol, koc].map(function (c) { return c.ring ? c.ring.per_100 : null; }) },
             { name: 'The city', col: '--fill-red', vals: [kol, koc].map(function (c) { return c.core.per_100; }) }] });
  document.getElementById('nFall').textContent = 'Kolkata\'s roll fell by ' + p1(kol.core.per_100) + ' of every 100 electors to the draft, ' + p1(kol.times_state) + ' times West Bengal\'s ' + p1(kol.state_per_100) + '. Kochi\'s fell by ' + p1(koc.core.per_100) + ', against ' + p1(koc.state_per_100) + ' for Kerala. Both follow the pattern of the other cities, on a different count. Kochi has no suburbs drawn.';

  document.getElementById('nPatna').textContent = 'Bihar published its roll before the revision for the state only, so its pages count the names removed in both phases against the 2025 roll, and so does this one. On that count Patna lost ' + p1(pat.core.per_100) + ' of every 100 electors, against ' + p1(pat.state_per_100) + ' for Bihar as a whole. It is the one city here that lost fewer names than its state. Its base differs from the other cities\' bases, so it is not ranked with them.';

  SIR.table('tDraw', [{ h: 'City' }, { h: 'Its districts' }, { h: 'Its suburbs' }],
    C.map(function (c) { return [link(c), c.core.districts.join(', '), c.ring ? c.ring.districts.join(', ') + (c.ring.state !== c.state ? ' (' + c.ring.state + ')' : '') : 'None drawn']; }));
  SIR.showFaq('india', 'cities');
}).catch(SIR.fail);
