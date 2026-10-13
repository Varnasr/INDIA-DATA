SIR.json('data/uttarakhand/summary.json').then(function (s) {
  document.getElementById('mBefore').textContent = SIR.n(s.roll_before);
  document.getElementById('mDraft').textContent = SIR.n(s.draft);
  document.getElementById('mFinal').textContent = SIR.n(s.final);
  SIR.showFaq('uk', 'method');
}).catch(SIR.fail);
