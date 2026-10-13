SIR.json('data/rajasthan/summary.json').then(function (s) {
  document.getElementById('mBefore').textContent = SIR.n(s.before);
  document.getElementById('mLeft').textContent = SIR.n(s.left_off);
  document.getElementById('mLeft2').textContent = SIR.n(s.left_off);
  document.getElementById('mSum').textContent = s.reasons_lakh_sum.toFixed(2);
  document.getElementById('mFall').textContent = SIR.n(s.fall);
  document.getElementById('mCov').textContent = SIR.n(s.press.left_off_covered) + ' (' + SIR.pct(s.press.covered_pct) + ')';
  SIR.showFaq('rj', 'method');
}).catch(SIR.fail);
