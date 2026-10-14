Promise.all([SIR.json('data/india/states.json'), SIR.json('data/bihar/reasons.json')]).then(function (r) {
  var d = r[0], RS = r[1], T = d.total, b = d.states.filter(function (s) { return s.state === 'Bihar'; })[0];
  document.getElementById('bihar').innerHTML = L('{n} names, of which {dead} dead, {shifted} shifted and {absent} absent (combined here as {sao}), and {dup} already enrolled.', { n: SIR.n(RS.total), dead: SIR.n(RS.totals.dead), shifted: SIR.n(RS.totals.shifted), absent: SIR.n(RS.totals.absent), sao: SIR.n(b.shifted_absent_other), dup: SIR.n(RS.totals.already_enrolled) });
  document.getElementById('recon').innerHTML = L('The national totals reported on 30 September 2026 were about 13.3 crore left off, 2.7 crore dead, 9.5 crore absent, shifted or other, and 1.01 crore enrolled more than once. The state rows here add up to {total}, {dead}, {sao} and {dup}. The small differences come from rounding in the national figures and in the states that published in lakh. The table is built up from the states. <a href="https://www.thehindu.com/news/national/of-those-deleted-in-sir-so-far-over-71-in-absent-shifted-or-others-category/article71524969.ece">Report of 30 September 2026</a>.', { total: L('{x} crore', { x: (T.removed / 1e7).toFixed(2) }), dead: L('{x} crore', { x: (T.dead / 1e7).toFixed(2) }), sao: L('{x} crore', { x: (T.shifted_absent_other / 1e7).toFixed(2) }), dup: L('{x} crore', { x: (T.duplicate / 1e7).toFixed(2) }) });
  document.getElementById('gN').textContent = L('{n} states have a split by sex.', { n: d.gender.length });
  // states whose reasons fall short of their total, add to more than it, or are missing
  var withR = d.states.filter(function (s) { return s.removed != null; }), rsum = function (s) { return (s.dead || 0) + (s.shifted_absent_other || 0) + (s.duplicate || 0); };
  document.getElementById('splitN').textContent = L('In {short} states the reasons leave some names unexplained, in {over} they add up to slightly more than the total, and in {none} no split by reason was published.', {
    short: withR.filter(function (s) { return s.shares && rsum(s) < s.removed; }).length, over: withR.filter(function (s) { return s.shares && rsum(s) > s.removed; }).length, none: withR.filter(function (s) { return !s.shares; }).length });
  document.getElementById('asof').textContent = SIR.date(d.as_of);
  var SK = { primary: L('Press note'), press: L('Press report'), lists: L('Lists') };
  SIR.table(document.getElementById('tSrc'), [
    { k: 'state', label: L('State or union territory'), left: true, fmt: function (v) { return SIR.esc(v); } },
    { k: 'draft_date', label: L('Draft roll'), left: true, fmt: function (v) { return v || '–'; } },
    { k: 'source', label: L('Source'), left: true, fmt: function (v, s) { var t = SK[v] || '–'; return s.source_url ? '<a href="' + SIR.esc(s.source_url) + '" rel="noopener">' + t + '</a>' : t; } },
    { k: 'note', label: L('Note'), left: true, fmt: function (v) { return v ? SIR.esc(v) : '–'; } }
  ], d.states, { sort: 'state', dir: 1 });
  var RL = { urban_pct: L('Urban share'), literacy: L('Literacy'), female_literacy: L('Women\'s literacy'), muslim_pct: L('Muslim share'), sc_pct: L('SC share'), st_pct: L('ST share'), sex_ratio: L('Sex ratio') };
  var changed = d.robustness_2011.filter(function (x) { return x.rho_recent != null && x.rho_2011 != null && ((Math.abs(x.rho_recent) >= 0.2) !== (Math.abs(x.rho_2011) >= 0.2) || (Math.abs(x.rho_recent) >= 0.2 && (x.rho_recent > 0) !== (x.rho_2011 > 0))); });
  document.getElementById('robust').innerHTML = L('Run on the 2011 census values instead, the rank correlations with the rate of exclusion across all states come out as follows. {list} The reading changes for {n} of them ({changed}).', {
    list: d.robustness_2011.map(function (x) { return L('{c} is {a} with the recent figure and {b} with 2011.', { c: RL[x.key], a: SIR.d(x.rho_recent, 2), b: SIR.d(x.rho_2011, 2) }); }).join(' '),
    n: changed.length, changed: changed.length ? changed.map(function (x) { return RL[x.key]; }).join(', ') : L('none') });
  var FQ = { exact: L('Adds up'), rounded: L('Rounded'), 'net only': L('Net only'), no: L('Does not add up') };
  SIR.table(document.getElementById('tFsrc'), [
    { k: 'state', label: L('State or union territory'), left: true, fmt: function (v) { return SIR.esc(v); } },
    { k: 'final_date', label: L('Final roll'), left: true, fmt: function (v) { return v || '–'; } },
    { k: 'reconciles', label: L('Figures'), left: true, fmt: function (v, s) { var t = FQ[v] || '–'; return '<a href="' + SIR.esc(s.final_source.url) + '" rel="noopener">' + t + '</a> · ' + (s.final_source.source === 'primary' ? L('Press note') : L('Press report')); } },
    { k: 'note', label: L('Note'), left: true, fmt: function (v, s) { return s.final_source.note ? SIR.esc(s.final_source.note) : '–'; } }
  ], d.states.filter(function (s) { return s.final_source; }), { sort: 'state', dir: 1 });
  var GQ = { exact: L('Exact'), rounded: L('Rounded'), proxy: L('Earlier roll'), unverified: L('Unverified'), lists: L('Lists') };
  SIR.table(document.getElementById('tGsrc'), [
    { k: 'state', label: L('State or union territory'), left: true, fmt: function (v) { return SIR.esc(v); } },
    { k: 'quality', label: L('Figures'), left: true, fmt: function (v, g) { var t = GQ[v] || v; return g.source_url ? '<a href="' + SIR.esc(g.source_url) + '" rel="noopener">' + t + '</a>' : t; } },
    { k: 'note', label: L('Note'), left: true, fmt: function (v) { return SIR.esc(v); } }
  ], d.gender, { sort: 'state', dir: 1 });
}).catch(SIR.fail);
