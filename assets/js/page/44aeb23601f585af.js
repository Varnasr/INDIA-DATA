Promise.all([SIR.json('data/gujarat/summary.json'), SIR.json('data/gujarat/final.json')]).then(function (r) {
  var s = r[0], G = r[1].filter(function (f) { return f.gap; });
  var NAME = { BJP: 'BJP', INC: 'Congress', AAP: 'AAP', IND: 'independents', SP: 'Samajwadi Party' };
  document.getElementById('mGaps').textContent = G.slice(0, -1).map(function (f) { return f.district + ' by ' + SIR.n(f.gap); }).join(', ') + ' and ' + G[G.length - 1].district + ' by ' + SIR.n(G[G.length - 1].gap);
  document.getElementById('mGapN').textContent = G.length;
  document.getElementById('mGap2').textContent = SIR.n(s.final_gap);
  document.getElementById('mSeats').textContent = Object.keys(s.seats_2022).sort(function (a, b) { return s.seats_2022[b] - s.seats_2022[a]; }).map(function (p) { return (NAME[p] || p) + ' ' + s.seats_2022[p]; }).join(', ').replace(/, ([^,]*)$/, ' and $1');
  document.getElementById('mBefore').textContent = SIR.n(s.before);
  document.getElementById('mRem').textContent = SIR.n(s.removed);
  document.getElementById('mDraft').textContent = SIR.n(s.draft);
  document.getElementById('mGap').textContent = SIR.n(s.final_gap);
  SIR.showFaq('gj', 'method');
}).catch(SIR.fail);
