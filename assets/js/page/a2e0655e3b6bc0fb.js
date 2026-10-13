SIR.json('data/tamilnadu/summary.json').then(function (s) {
  document.getElementById('mRem').textContent = SIR.n(s.removed);
  document.getElementById('mBefore').textContent = SIR.n(s.before);
  SIR.showFaq('tn', 'method');
}).catch(SIR.fail);
