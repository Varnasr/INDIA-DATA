if (/[?&]other=1/.test(location.search)) {
  document.getElementById('upiBlock').hidden = true;
  document.getElementById('otherBlock').hidden = false;
}
