// the footer's link carries the page the reader came from, so they need not type it
(function () {
  var m = /[?&]from=([^&]*)/.exec(location.search), f = document.getElementById('fbPage');
  if (m && f && !f.value) {
    try { f.value = decodeURIComponent(m[1]).replace(/[^\w\/\-\.]/g, '').slice(0, 200) || ''; } catch (e) { f.value = ''; }
  }
})();
