SIR.json('data/delhi/summary.json').then(function (s) {
  document.getElementById('mBefore').textContent = SIR.n(s.roll_before);
  document.getElementById('mDraft').textContent = SIR.n(s.draft);
  SIR.showFaq('dl', 'method');
}).catch(SIR.fail);
