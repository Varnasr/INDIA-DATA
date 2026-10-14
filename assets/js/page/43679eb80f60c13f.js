SIR.json('data/india/factors.json').then(function (d) {
  var S = d.states, C = d.census, X = d.summary, p2 = function (x) { return SIR.d(x, 2); };
  var list = function (a) { return a.length ? a.join(', ').replace(/, ([^,]*)$/, ' and $1') : ''; };
  var FL = {}; d.factors.forEach(function (f) { FL[f.key] = f.label; });
  var clear = function (k, sign) { return S.filter(function (s) { var v = s.survey[k]; return v && v.clear && (sign > 0 ? v.rho > 0 : v.rho < 0); }).map(function (s) { return s.state; }); };
  var cl = function (k, sign) { return C.filter(function (s) { var v = s.census[k]; return v && v.clear && (sign > 0 ? v.rho > 0 : v.rho < 0); }).map(function (s) { return s.state; }); };
  var schUp = clear('women_10yr', 1), schDn = clear('women_10yr', -1), litDn = clear('women_literate', -1), marUp = clear('married_18', 1), marDn = clear('married_18', -1);
  var fuelUp = clear('clean_fuel', 1), deathUp = clear('death_reg', 1), deathDn = clear('death_reg', -1);
  var urbUp = cl('urban_pct', 1), denUp = cl('density', 1);
  var none = S.filter(function (s) { return !Object.keys(s.survey).some(function (k) { return k !== 'sex_ratio' && s.survey[k] && s.survey[k].clear; }); }).map(function (s) { return s.state; });
  var big = S.filter(function (s) { return s.units >= 20; }), cols = big.map(function (s) { return s.school_fuel; }), lo = Math.min.apply(null, cols), hi = Math.max.apply(null, cols);
  var MEAS = { left_off: 'names left off per 100 on the roll before', roll_2025: 'names left off or deleted per 100 on the 2025 roll', fall: 'fall in the roll per 100', change_2023: 'fall in the roll from 2023 per 100', after_draft: 'names deleted after the draft per 100 on the draft', fall_after_draft: 'fall in the roll after the draft per 100 on the draft', rise_after_draft: 'rise in the roll after the draft per 100 on the draft' };
  var I = d.income, incUp = I.filter(function (s) { return s.income.clear && s.income.rho > 0; }).map(function (s) { return s.state; }),
    incDn = I.filter(function (s) { return s.income.rho < 0; }).map(function (s) { return s.state; });

  SIR.inShort([
    'In ' + list(urbUp) + ', the districts with more of their people in towns lost clearly more names for their size, out of the ' + C.length + ' states with district figures.',
    'Districts where women had more years of school lost clearly more names in ' + list(schUp) + ', and districts where more homes cooked with gas or electricity did so in ' + list(fuelUp) + '. In most states these are also the more urban districts.',
    litDn.length ? list(litDn) + ' ran the other way. There the districts with fewer women who can read' + (marUp.length ? ' and more early marriage' : '') + ' lost more names.' : '',
    'In ' + list(deathUp) + ', districts that register more of their deaths lost more names.' + (deathDn.length ? ' In ' + list(deathDn) + ' they lost fewer.' : ' In no state did they clearly lose fewer.'),
    'Districts with higher income per head lost clearly more names in ' + list(incUp) + (incDn.length ? ', and fewer, though not clearly, in ' + list(incDn) : '') + '.',
    none.length ? 'In ' + list(none) + ' no survey circumstance goes clearly with the rate.' : ''
  ].filter(Boolean), 'Survey figures are for 2019-21, census figures for 2011, and income for the year of each state\'s table. A correlation inside a state says which districts lost more and nothing about why, and the circumstances move together, so no one of them can be singled out. Rajasthan and Delhi have no census figures here, and only five states have a district income table.');

  document.getElementById('kpis').innerHTML = [
    [urbUp.length + ' of ' + C.length, 'states where more urban districts clearly lost more names'],
    [schUp.length + ' of ' + S.length, 'states where districts with more schooled women clearly lost more'],
    [deathUp.length + ' of ' + S.length, 'states where districts registering more deaths clearly lost more'],
    [incUp.length + ' of ' + I.length, 'states where richer districts clearly lost more'],
    [X.survey_units, 'survey districts in ' + X.survey_states + ' states']
  ].map(function (k) { return '<div><b>' + k[0] + '</b><span>' + k[1] + '</span></div>'; }).join('');

  var cats = S.map(function (s) { return s.state + ' (' + s.units + ')'; });
  var rv = function (k) { return S.map(function (s) { return s.survey[k] ? s.survey[k].rho : null; }); };
  VIZ.dots('vSchool', { label: 'Rank correlation between the rate and three district circumstances, state by state', axis: 'Rank correlation',
    cats: cats, series: [{ name: FL.women_10yr, col: '--fill-navy', vals: rv('women_10yr') }, { name: FL.clean_fuel, col: '--fill-amber', vals: rv('clean_fuel') }, { name: FL.married_18, col: '--fill-red', vals: rv('married_18') }] });
  document.getElementById('nSchool').textContent = 'The number after each state is its count of survey districts. ' + S.map(function (s) { return s.state + ' needs ' + p2(s.chance); }).join(', ').replace(/, ([^,]*)$/, ' and $1') + ' before a correlation is clear of chance.';
  document.getElementById('fSchool').innerHTML = '<b>Districts where women had more years of school lost clearly more names in ' + list(schUp) + '.</b> ' +
    (marDn.length ? 'Early marriage runs the other way there, and its correlation is clearly below zero in ' + list(marDn) + '. ' : '') +
    (marUp.length ? 'In ' + list(marUp) + ' the districts with more early marriage lost more' + (litDn.length ? ', and the districts with fewer women who can read lost more too' : '') + '. ' : '') +
    (none.length ? 'In ' + list(none) + ' none of the survey circumstances is clear of chance.' : '');

  VIZ.dots('vDeath', { label: 'Rank correlation between the rate and the share of deaths registered', axis: 'Rank correlation',
    cats: cats, series: [{ name: FL.death_reg, col: '--fill-purple', vals: rv('death_reg') }] });
  VIZ.dots('vInc', { label: 'Rank correlation between the rate and income per head', axis: 'Rank correlation',
    cats: I.map(function (s) { return s.state + ' (' + s.units + ')'; }),
    series: [{ name: 'Income per head', col: '--fill-amber', vals: I.map(function (s) { return s.income.rho; }) }] });
  document.getElementById('nInc').textContent = 'The number after each state is its count of districts in its income table. ' +
    I.map(function (s) { return s.state + ' ' + p2(s.income.rho) + ' (' + s.year + ')'; }).join('; ') + '. ' +
    'Clear of chance in ' + list(I.filter(function (s) { return s.income.clear; }).map(function (s) { return s.state; })) + '. The richest districts are mostly the cities and their suburbs, which the cities page shows lost the most.';
  var dr = S.map(function (s) { return s.state + ' ' + p2(s.survey.death_reg.rho); }).join(', ').replace(/, ([^,]*)$/, ' and $1');
  document.getElementById('nDeath').textContent = 'The correlations are ' + dr + '. Clear of chance in ' + list(deathUp.concat(deathDn)) + '. The figures cannot say whether registered deaths made dead names easier to find, or whether the same districts differ in other ways. In West Bengal and Kerala the rate is the fall in the roll, which takes in ordinary deaths as well.';

  VIZ.dots('vTown', { label: 'Rank correlation between the rate and urban share and density, 2011', axis: 'Rank correlation',
    cats: C.map(function (s) { return s.state + ' (' + s.units + ')'; }),
    series: [{ name: FL.urban_pct, col: '--fill-navy', vals: C.map(function (s) { return s.census.urban_pct.rho; }) }, { name: FL.density, col: '--fill-teal', vals: C.map(function (s) { return s.census.density.rho; }) }] });
  var bi = C.filter(function (s) { return s.state === 'Bihar'; })[0];
  document.getElementById('nTown').textContent = 'The number after each state is its count of 2011 districts. More urban districts lost clearly more names in ' + list(urbUp) + ', and more crowded ones in ' + list(denUp) + '. ' +
    (bi.census.urban_pct.rho < 0 ? 'Bihar runs the other way on urban share, at ' + p2(bi.census.urban_pct.rho) + (bi.census.urban_pct.clear ? '' : ', short of the ' + p2(bi.chance) + ' needed to be clear of chance') + ', while its correlation with density is ' + p2(bi.census.density.rho) + '. Bihar has few towns, and its crowded districts are mostly villages.' : '');

  document.getElementById('tCol').textContent = 'Across the districts of each state with 20 or more of them, women\'s schooling and clean cooking fuel have a rank correlation of ' + p2(lo) + ' to ' + p2(hi) + ' with each other, and both are highest in the towns. A district with more schooled women is, in most states, a district with more homes on gas and more people in towns, and a district figure cannot say which of these, if any, made the difference. Separating them would take a count of whose names were left off, household by household, which no state has published. So this page shows which kinds of districts lost more names, and it stops there.';

  var keys = d.factors.filter(function (f) { return f.source === 'nfhs'; }).map(function (f) { return f.key; });
  var fmt = function (v) { return v ? p2(v.rho) + (v.clear ? ' *' : '') : '–'; };
  SIR.table('tAll', [{ h: 'State' }, { h: 'Districts', num: true }].concat(keys.map(function (k) { return { h: FL[k], num: true }; })).concat([{ h: 'Measure' }]),
    S.map(function (s) { return [SIR.esc(s.state), s.units].concat(keys.map(function (k) { return fmt(s.survey[k]); })).concat([MEAS[s.measure]]); }));
  document.getElementById('mChecked').textContent = 'A star in the table marks a correlation clear of chance.';
  SIR.showFaq('india', 'factors');
}).catch(SIR.fail);
