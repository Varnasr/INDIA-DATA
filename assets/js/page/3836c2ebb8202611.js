SIR.json('data/karnataka/summary.json').then(function (s) {
  document.getElementById('mRem').textContent = SIR.n(s.removed);
  document.getElementById('mBefore').textContent = SIR.n(s.before);
  document.getElementById('mGap').textContent = SIR.n(s.final - s.final_by_sex);
  SIR.showFaq('ka', 'method');
}).catch(SIR.fail);
