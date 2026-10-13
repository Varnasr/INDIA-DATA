var DL = function (iso) { var p = iso.split('-'); return +p[2] + ' ' + ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][+p[1] - 1] + ' ' + p[0]; };
SIR.json('data/maharashtra/summary.json').then(function (s) {
  document.getElementById('mBefore').textContent = SIR.n(s.before);
  document.getElementById('mBefore2').textContent = SIR.n(s.before);
  document.getElementById('mDraft').textContent = SIR.n(s.draft);
  document.getElementById('mLeft').textContent = SIR.n(s.left_off);
  document.getElementById('mClaims').textContent = DL(s.claims_to);
  document.getElementById('mFinal').textContent = DL(s.final_due);
  SIR.showFaq('mh', 'method');
}).catch(SIR.fail);
