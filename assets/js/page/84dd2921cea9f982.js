SIR.json('data/delhi/summary.json').then(function (s) {
  document.getElementById('mBefore').textContent = SIR.n(s.roll_before);
  document.getElementById('mDraft').textContent = SIR.n(s.draft);
  // s.final is null until scripts/add_final.py records the final roll
  var today = new Date().toISOString().slice(0, 10);
  document.getElementById('mClaims').textContent = s.final ? 'Claims and objections ran to ' + SIR.date(s.claims_to) + ', and the final roll was published on ' + SIR.date(s.final.date) + '.'
    : 'Claims and objections ' + (s.claims_to < today ? 'ran' : 'run') + ' to ' + SIR.date(s.claims_to) + ', and the final roll ' + (s.final_due < today ? 'was' : 'is') + ' due on ' + SIR.date(s.final_due) + '.';
  if (s.final) document.getElementById('mPutBack').textContent = 'How many of those left off were put back. The names added after the draft count new voters with them, and no published count separates the two.';
  SIR.showFaq('dl', 'method');
}).catch(SIR.fail);
