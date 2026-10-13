SIR.json('data/westbengal/summary.json').then(function (s) {
  document.getElementById('mRem').textContent = SIR.n(s.pn05.removed);
  document.getElementById('mAdj').textContent = SIR.n(s.pn05.adjudication);
  document.getElementById('mGrow').textContent = SIR.n(s.growth_2024_to_oct2025);
  document.getElementById('mGrow2').textContent = SIR.lakh(s.growth_2024_to_oct2025);
  SIR.showFaq('wb', 'method');
}).catch(SIR.fail);
