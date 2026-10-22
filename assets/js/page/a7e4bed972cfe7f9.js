SIR.json('data/india/rti.json').then(function (D) {
  var n = SIR.n, esc = SIR.esc, C = D.counts, O = D.by_outcome;
  var NAME = {
    'no record held': 'Said it held no record', 'not supplied': 'Sent something other than what was asked', 'refused': 'Refused', 'transferred': 'Passed to another office',
    'partly supplied': 'Answered in part', 'supplied': 'Answered', 'appeal': 'Decided on appeal or in court',
    'no reply in time': 'No reply within 30 days', 'pending': 'Still waiting for a reply'
  };
  var none = O['no record held'] || 0, sent = O['transferred'] || 0, ref = O['refused'] || 0, full = O['supplied'] || 0;
  var dated = D.items.filter(function (i) { return i.days != null; }), late = dated.filter(function (i) { return i.days > 30; });
  SIR.inShort([
    n(C.items) + ' applications about the revision whose reply, refusal or appeal was reported between ' + SIR.date(C.first) + ' and ' + SIR.date(C.last) + '.',
    none ? 'In ' + n(none) + ' of them the authority said it held no record of what was asked.' : '',
    O['not supplied'] ? 'In ' + n(O['not supplied']) + ' it sent something other than what was asked, such as a link to a different document.' : '',
    sent || ref ? (sent ? n(sent) + ' were passed to another office' : '') + (sent && ref ? ' and ' : '') + (ref ? n(ref) + (ref === 1 ? ' was' : ' were') + ' refused' : '') + '.' : '',
    'In ' + n(full) + ' of the ' + n(C.items) + ' the authority supplied what was asked in full.',
    dated.length ? n(late.length) + ' of the ' + n(dated.length) + ' replies with both dates reported came after the 30 days the Act allows.' : ''
  ], 'These are the applications that were reported. No authority publishes how many were filed. Each item is what the outlet reported about the reply. Nothing here says what anyone intended.');

  document.getElementById('kpis').innerHTML = [
    [n(C.items), 'applications reported'], [n(none), 'answered that no record was held'],
    [n(sent + ref), 'refused or passed on'], [n(full), 'answered in full']
  ].map(function (x) { return '<div><b>' + x[0] + '</b><span>' + x[1] + '</span></div>'; }).join('');

  VIZ.lollipop('vOut', { label: 'Applications by what became of them', axis: 'Applications',
    rows: Object.keys(O).map(function (o) { return { name: NAME[o], v: O[o], text: n(O[o]), tok: o === 'supplied' ? '--fill-navy' : '--fill-red', hi: true }; }) });
  if (dated.length) {
    VIZ.lollipop('vDays', { label: 'Days from application to reply', axis: 'Days',
      rows: dated.slice().sort(function (a, b) { return b.days - a.days; }).map(function (i) {
        return { name: i.authority.replace('Election Commission of India', 'Commission') + ', ' + SIR.date(i.replied), v: i.days, text: n(i.days) + ' days', tok: i.days > 30 ? '--fill-red' : '--fill-grey', hi: i.days > 30 };
      }) });
  } else document.getElementById('pDays').hidden = true;

  var li = function (i) {
    var when = [i.filed ? 'filed ' + SIR.date(i.filed) : '', i.replied ? 'answered ' + SIR.date(i.replied) : ''].filter(Boolean).join(', ');
    var src = '<a href="' + esc(i.url) + '" rel="noopener">' + esc(i.outlet) + '</a>, ' + SIR.date(i.published) + '.' +
      (i.doc_url ? ' <a href="' + esc(i.doc_url) + '" rel="noopener">The reply</a>.' : '') +
      (i.kind === 'primary' ? ' <span class="tag primary">document</span>' : ' <span class="tag press">report</span>');
    return '<li id="r-' + esc(i.id) + '"><p><b>' + esc(i.authority) + '</b>, ' + esc(i.state) + '. Asked by ' + esc(i.applicant) + (when ? ', ' + when : '') + '.</p>' +
      '<p>' + esc(i.asked) + '</p><p class="nresp">' + esc(i.answer) + (i.section ? ' The refusal cited ' + esc(i.section) + '.' : '') +
      (i.days > 30 ? ' The reply came ' + n(i.days) + ' days after the application, ' + n(i.days - 30) + ' days past the 30 the Act allows.' : '') + '</p>' +
      '<p class="nsrc">' + src + '</p>' +
      (i.quote ? '<details><summary>The words of the source</summary><blockquote>' + esc(i.quote) + '</blockquote></details>' : '') + '</li>';
  };
  var html = '', k = 0;
  Object.keys(O).forEach(function (o) {
    var its = D.items.filter(function (i) { return i.outcome === o; });
    html += '<h3 class="dsec">' + NAME[o] + '</h3><ol class="nfacts dsec" start="' + (k + 1) + '">' + its.map(li).join('') + '</ol>';
    k += its.length;
  });
  document.getElementById('secEnd').insertAdjacentHTML('beforebegin', html);

  var other = D.other || [];
  document.getElementById('otherList').innerHTML = other.length ? other.map(li).join('') : '<li>None published yet.</li>';
  document.getElementById('unconfirmed').innerHTML = D.unconfirmed.length ? D.unconfirmed.map(function (u) {
    return '<li>' + esc(u.outlet || '') + (u.date ? ', ' + SIR.date(u.date) : '') + ', "' + esc(u.headline || '') + '". ' + esc(u.reason) + '</li>';
  }).join('') : '<li>Every report we found was matched to its source.</li>';

  SIR.anchors && SIR.anchors();
  SIR.toc && SIR.toc();
  SIR.showFaq('india', 'rti');
  SIR.jump && SIR.jump();
}).catch(SIR.fail);
