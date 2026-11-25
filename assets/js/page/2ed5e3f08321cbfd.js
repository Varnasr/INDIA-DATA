Promise.all([SIR.json('data/uttarpradesh/summary.json'), SIR.json('data/uttarpradesh/analysis.json')]).then(function (r) {
  var s = r[0], MM = r[1].margins.measured;
  document.getElementById('mS1dDraft').textContent = SIR.n(MM.draft);
  document.getElementById('mS1dGap').textContent = SIR.n(MM.draft_ceo_gap);
  document.getElementById('mS1dDist').textContent = SIR.n(MM.draft_district_gap_max);
  document.getElementById('mBefore').textContent = SIR.n(s.roll_before);
  document.getElementById('mDraft').textContent = SIR.n(s.draft);
  document.getElementById('mLeft').textContent = SIR.n(s.left_off);
  document.getElementById('mAfter').textContent = SIR.n(s.removed_after);
  SIR.showFaq('up', 'method');
}).catch(SIR.fail);
