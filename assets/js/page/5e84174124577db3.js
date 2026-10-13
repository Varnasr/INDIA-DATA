SIR.json('data/kerala/summary.json').then(function (s) {
  document.getElementById('mFall').textContent = SIR.n(s.fall_draft);
  document.getElementById('mFrozen').textContent = SIR.n(s.frozen);
  document.getElementById('mPress').textContent = SIR.n(s.press_removed);
  SIR.showFaq('kl', 'method');
}).catch(SIR.fail);
