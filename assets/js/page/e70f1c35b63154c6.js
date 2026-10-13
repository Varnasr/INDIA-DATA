// a supporter who is not an Indian citizen is sent to a thank-you page with no
// UPI code: contributions are taken only from Indian citizens
(function () {
  var f = document.querySelector('form[name="support"]'), c = document.getElementById('spCit');
  f.addEventListener('submit', function () { f.setAttribute('action', c.value === 'no' ? '/support/thanks/?other=1' : '/support/thanks/'); });
})();
