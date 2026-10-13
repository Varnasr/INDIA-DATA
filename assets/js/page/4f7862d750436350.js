SIR.json('data/uttarpradesh/summary.json').then(function (s) {
  document.getElementById('mBefore').textContent = SIR.n(s.roll_before);
  document.getElementById('mDraft').textContent = SIR.n(s.draft);
  document.getElementById('mLeft').textContent = SIR.n(s.left_off);
  document.getElementById('mAfter').textContent = SIR.n(s.removed_after);
  SIR.showFaq('up', 'method');
}).catch(SIR.fail);
