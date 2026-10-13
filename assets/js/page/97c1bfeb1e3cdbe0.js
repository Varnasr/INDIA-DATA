SIR.json('data/assam/summary.json').then(function (d) {
  var S = d.state, n = SIR.n, set = function (id, v) { document.getElementById(id).textContent = v; };
  set('mFlag', n(S.flagged)); set('mFlag2', n(S.flagged)); set('mJan', n(S.draft_vs_jan));
  set('mD1', n(S.draft)); set('mD2', n(S.draft_as_stated_with_final)); set('mGap', n(S.draft_gap)); set('mFall', n(S.net_fall));
  SIR.showFaq('as', 'method');
}).catch(SIR.fail);
