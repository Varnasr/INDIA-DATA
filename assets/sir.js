/* Shared helpers for the SIR pages. No framework; Chart.js is loaded by each
   page from cdnjs. Every page sets data-root on <body> ("../" or "../../") so
   the JSON under data/ resolves on Netlify and in a local server alike. */
(function () {
  'use strict';
  // No i18n.js on the page: every string stays as written.
  if (!window.L) { window.L = function (k, v) { return v ? k.replace(/\{(\w+)\}/g, function (m, x) { return v[x] != null ? v[x] : m; }) : k; }; window.L.apply = function () {}; window.L.lang = 'en'; }
  L.apply(document.body);
  // the line under the kicker saying which roll a state's figures come from;
  // build_site.py writes it in English and the stage and dates as data
  [].forEach.call(document.querySelectorAll('p.asof[data-k]'), function (p) {
    var f = function (iso) { if (!iso) return ''; var q = iso.split('-'); return +q[2] + ' ' + ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][+q[1] - 1] + ' ' + q[0]; };
    var v = { d: f(p.getAttribute('data-d')), n: f(p.getAttribute('data-n')) }, t = {
      'final': L('Figures as of {d}, when the final roll was published.', v),
      'draft-due': L('Figures as of {d}, when the draft roll was published. The final roll is due on {n}.', v),
      'draft-past': L('Figures as of {d}, when the draft roll was published. The final roll was due on {n}, and we have not found it published.', v),
      'latest-due': L('Figures as of {d}, a roll published after claims had closed, while notices were being heard. The final roll is due on {n}.', v),
      'nodraft': L('No draft roll has been published yet. It is due on {n}.', v)
    }[p.getAttribute('data-k')];
    if (t) p.textContent = t;
  });
  var root = document.body.getAttribute('data-root') || '';
  var nf = new Intl.NumberFormat('en-IN');

  var SIR = window.SIR = {
    root: root,
    n: function (x) { return x == null || isNaN(x) ? '–' : nf.format(Math.round(x)); },
    // a half rounds away from zero, whatever its binary form (8.65 is 8.7 and 1.15 is 1.2)
    d: function (x, k) { if (x == null || isNaN(x)) return '–'; k = k == null ? 1 : k; x = Number(x); return (x + (x < 0 ? -1e-9 : 1e-9)).toFixed(k); },
    pct: function (x, k) { return x == null || isNaN(x) ? '–' : SIR.d(x, k) + '%'; },
    // a multiple such as removals over a margin: one decimal, except that just
    // under 1 is cut to two (0.99×), so a seat below its margin never reads 1.0×
    times: function (x) { return x == null || isNaN(x) ? '' : (x < 1 && x >= 0.95 ? (Math.floor(x * 100) / 100).toFixed(2) : Number(x).toFixed(1)) + '×'; },
    date: function (iso) { if (!iso) return ''; var p = iso.split('-'); return +p[2] + ' ' + ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][+p[1] - 1] + ' ' + p[0]; },
    // a count of a crore or more is written in crore, anything smaller in lakh
    lakh: function (x) { return Math.abs(x) >= 1e7 ? L('{x} crore', { x: (x / 1e7).toFixed(2) }) : L('{x} lakh', { x: (x / 1e5).toFixed(1) }); },
    // the same in plain English, for pages that are English only
    lk: function (x, k) { return Math.abs(x) >= 1e7 ? (x / 1e7).toFixed(2) + ' crore' : (x / 1e5).toFixed(k == null ? 1 : k) + ' lakh'; },
    esc: function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); },
    // one request per file per page: several scripts on a page read the
    // same file, so the text is kept (and dropped again if the request
    // fails), and each caller gets its own parsed copy, which it may sort
    json: function (path) {
      var J = SIR._json || (SIR._json = {});
      if (!J[path]) {
        var v = (window.SIR_V || {})[path];
        J[path] = fetch(root + path + (v ? '?v=' + v : '')).then(function (r) {
          if (!r.ok) throw new Error(path + ' answered ' + r.status);
          return r.text();
        }).catch(function (e) { delete J[path]; throw e; });
      }
      return J[path].then(JSON.parse);
    },
    css: function (name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); },
    alliance: { NDA: '--fill-nda', INDIA: '--fill-india', Other: '--fill-other' },
    mean: function (a) { return a.length ? a.reduce(function (s, x) { return s + x; }, 0) / a.length : NaN; },
    median: function (a) { var s = a.slice().sort(function (x, y) { return x - y; }); var m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; },
    corr: function (x, y) {
      var mx = SIR.mean(x), my = SIR.mean(y), sxy = 0, sx = 0, sy = 0;
      for (var i = 0; i < x.length; i++) { sxy += (x[i] - mx) * (y[i] - my); sx += (x[i] - mx) * (x[i] - mx); sy += (y[i] - my) * (y[i] - my); }
      return sxy / Math.sqrt(sx * sy);
    },
    // Spearman: Pearson on ranks. Used alongside Pearson because 38 districts
    // and a few Seemanchal outliers make the linear coefficient fragile.
    spearman: function (x, y) {
      function ranks(a) { var idx = a.map(function (v, i) { return [v, i]; }).sort(function (p, q) { return p[0] - q[0]; }); var r = new Array(a.length); for (var i = 0; i < idx.length;) { var j = i; while (j + 1 < idx.length && idx[j + 1][0] === idx[i][0]) j++; for (var k = i; k <= j; k++) r[idx[k][1]] = (i + j) / 2 + 1; i = j + 1; } return r; }
      return SIR.corr(ranks(x), ranks(y));
    },
    groupBy: function (rows, key) { var o = {}; rows.forEach(function (r) { var k = typeof key === 'function' ? key(r) : r[key]; (o[k] = o[k] || []).push(r); }); return o; },
    sum: function (rows, k) { return rows.reduce(function (s, r) { return s + (typeof k === 'function' ? k(r) : r[k]); }, 0); }
  };

  // ---------------------------------------------------------------- theme
  var saved = null;
  try { saved = localStorage.getItem('sir-theme'); } catch (e) {}
  if (saved) document.documentElement.setAttribute('data-theme', saved);
  var btn = document.querySelector('.theme');
  SIR.isDark = function () {
    var t = document.documentElement.getAttribute('data-theme');
    return t === 'dark' || (!t && matchMedia('(prefers-color-scheme: dark)').matches);
  };
  function label() {
    var dark = SIR.isDark();
    if (btn) {
      var s = btn.querySelector('span');
      if (s) s.textContent = dark ? L('Light') : L('Dark'); else btn.textContent = dark ? L('Light') : L('Dark');
      btn.setAttribute('aria-pressed', dark ? 'true' : 'false');
    }
    return dark;
  }
  if (btn) btn.addEventListener('click', function () {
    var next = label() ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try { localStorage.setItem('sir-theme', next); } catch (e) {}
    label();
    SIR.charts.forEach(function (c) { SIR.recolour(c); });
    document.dispatchEvent(new Event('sir-theme'));
  });
  label();
  // Export PDF prints the page; the print stylesheet drops the header and
  // shows every tab. A dashboard can set SIR.beforePrint to draw its charts.
  var pr = document.querySelector('.print');
  if (pr) pr.addEventListener('click', function () { if (SIR.beforePrint) SIR.beforePrint(); setTimeout(function () { window.print(); }, 300); });

  // On a phone the header is one row: the title, Search, and this button,
  // which opens the other controls on a row beneath (sir.css hides them
  // until then). On a wide screen the stylesheet hides the button.
  var ctl = document.querySelector('header.top .controls');
  if (ctl && !ctl.querySelector('.more')) {
    var more = document.createElement('button');
    more.type = 'button'; more.className = 'more';
    more.setAttribute('aria-expanded', 'false');
    more.setAttribute('aria-label', L('More options'));
    more.innerHTML = '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/></svg>';
    ctl.appendChild(more);
    more.addEventListener('click', function () {
      var open = document.querySelector('header.top').classList.toggle('open');
      more.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // ----------------------------------------------------- header and tabs
  // On a wide screen the header is sticky and the tab bar sticks beneath it,
  // so the bar needs the header's height; on a phone the header scrolls away
  // and the bar sticks at the top on its own (the stylesheet zeroes --hh).
  var head = document.querySelector('header.top'), nav = document.querySelector('.nav-tabs');
  function measure() {
    if (head) document.documentElement.style.setProperty('--hh', (getComputedStyle(head).position === 'sticky' ? head.offsetHeight : 0) + 'px');
    if (nav) {
      var over = nav.scrollWidth - nav.clientWidth, x = Math.abs(nav.scrollLeft), rtl = getComputedStyle(nav).direction === 'rtl';
      var before = x > 4, after = x < over - 4;
      nav.classList.toggle(rtl ? 'more-end' : 'more-start', over > 4 && before);
      nav.classList.toggle(rtl ? 'more-start' : 'more-end', over > 4 && after);
    }
  }
  SIR.tabIntoView = function (t) {
    if (!nav || !t) return;
    var n = nav.getBoundingClientRect(), r = t.getBoundingClientRect();
    nav.scrollBy({ left: (r.left + r.width / 2) - (n.left + n.width / 2), behavior: 'smooth' });
  };
  if (nav) {
    nav.addEventListener('scroll', measure, { passive: true });
    SIR.tabIntoView(nav.querySelector('[aria-current="page"]'));
  }
  window.addEventListener('resize', measure);
  measure();
  // ------------------------------------------------------- section bar
  // On a phone the row of tabs is replaced by one line: where you are
  // ("Bihar 2025 › Overview", 1 of 11), arrows to the previous and next
  // section, and a menu behind a tap listing the dashboard's tabs and the
  // analysis's other pages under separate headings. The arrows and the count
  // run over whichever list the reader is in: the tabs on a dashboard, the
  // pages elsewhere. A page without JavaScript keeps the scrolling row.
  // The map below is the dashboards' tabs and each analysis's pages, with
  // their icons; labels are the English keys the dictionaries already hold.
  var ICONS = {"i0": "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"1.5\" d=\"M21 21H3.8a.8.8 0 0 1-.8-.8V3m3 11 4-4 4 4 7-7\"/>", "i1": "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-miterlimit=\"10\" stroke-width=\"1.5\" d=\"M8 12h8m6 0c0 5.523-4.477 10-10 10S2 17.523 2 12 6.477 2 12 2s10 4.477 10 10\"/>", "i2": "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-miterlimit=\"10\" stroke-width=\"1.5\" d=\"m12 12 3.136-2.391C16.318 8.7 17 7.265 17 5.735V2H7v3.735c0 1.53.682 2.965 1.864 3.874zm0 0-3.136 2.391C7.682 15.3 7 16.735 7 18.265V22h10v-3.735c0-1.53-.682-2.965-1.864-3.874zm-5 6 5-1 5 1M5 2h14M5 22h14\"/>", "i3": "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"1.5\" d=\"M21 22c0-4.418-3.626-8-8.1-8h-1.8C6.626 14 3 17.582 3 22m9-11a4 4 0 0 1-4-4V6a4 4 0 1 1 8 0v1a4 4 0 0 1-4 4\"/>", "i4": "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-miterlimit=\"10\" stroke-width=\"1.5\" d=\"m3 12 9 5 9-5M3 16l9 5 9-5M3 8l9-5 9 5-9 5z\"/>", "i5": "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-miterlimit=\"10\" stroke-width=\"1.5\" d=\"M18 8V2.8a.8.8 0 0 0-.8-.8h-2.4a.8.8 0 0 0-.8.8V6h-4V2.8a.8.8 0 0 0-.8-.8H6.8a.8.8 0 0 0-.8.8V8m12 0v11.6a2.4 2.4 0 0 1-2.4 2.4M18 8h4m-6.4 14H14m1.6 0h4a2.4 2.4 0 0 0 2.4-2.4V8m-8 14h-4m4 0v-3.2a.8.8 0 0 0-.8-.8h-2.4a.8.8 0 0 0-.8.8V22m0 0H8.4m0 0A2.4 2.4 0 0 1 6 19.6V8m2.4 14H4.5C3.175 22 2 20.878 2 19.553V8m4 0H2m20 0h1M2 8H1m10 2h2m-3 4h4\"/>", "i6": "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-miterlimit=\"10\" stroke-width=\"1.5\" d=\"M12 15h5m-5-6h5M5.4 3h13.2A2.4 2.4 0 0 1 21 5.4v13.2a2.4 2.4 0 0 1-2.4 2.4H5.4A2.4 2.4 0 0 1 3 18.6V5.4A2.4 2.4 0 0 1 5.4 3M9 15a1 1 0 1 1-2 0 1 1 0 0 1 2 0m0-6a1 1 0 1 1-2 0 1 1 0 0 1 2 0\"/>", "i7": "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-miterlimit=\"10\" stroke-width=\"1.5\" d=\"M9 3v16M9 3 2 5v16l7-2M9 3l6 2M9 19l6 2m0-16v16m0-16 7-2v16l-7 2\"/>", "i8": "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-miterlimit=\"10\" stroke-width=\"1.5\" d=\"M7 4h3.75c1.393 0 2.728.474 3.713 1.318S16 7.307 16 8.5s-.553 2.338-1.537 3.182c-.985.844-2.32 1.318-3.712 1.318H7l8.2 7M7 8.5h11M11 4h7\"/>", "i9": "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-miterlimit=\"10\" stroke-width=\"1.5\" d=\"m21 21-4-4m2-6a8 8 0 1 1-16 0 8 8 0 0 1 16 0\"/>", "i10": "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-miterlimit=\"10\" stroke-width=\"1.5\" d=\"M12 7.333C12 5.5 10.5 4 8.667 4H2v12h6.708C12 16 12 19.334 12 19.334m0-12C12 5.5 13.5 4 15.333 4H22v12h-6.667C12 16 12 19.334 12 19.334m0-12v12m1.875 1.124A2.58 2.58 0 0 1 16.167 19H21m-10.875 1.458A2.54 2.54 0 0 0 7.833 19H3\"/>", "i11": "<path stroke-linejoin=\"round\" stroke-miterlimit=\"10\" stroke-width=\"1.5\" d=\"M8.4 4H5.6A1.6 1.6 0 0 0 4 5.6v2.8A1.6 1.6 0 0 0 5.6 10h2.8A1.6 1.6 0 0 0 10 8.4V5.6A1.6 1.6 0 0 0 8.4 4ZM8.4 14H5.6A1.6 1.6 0 0 0 4 15.6v2.8A1.6 1.6 0 0 0 5.6 20h2.8a1.6 1.6 0 0 0 1.6-1.6v-2.8A1.6 1.6 0 0 0 8.4 14ZM18.4 4h-2.8A1.6 1.6 0 0 0 14 5.6v2.8a1.6 1.6 0 0 0 1.6 1.6h2.8A1.6 1.6 0 0 0 20 8.4V5.6A1.6 1.6 0 0 0 18.4 4ZM18.4 14h-2.8a1.6 1.6 0 0 0-1.6 1.6v2.8a1.6 1.6 0 0 0 1.6 1.6h2.8a1.6 1.6 0 0 0 1.6-1.6v-2.8a1.6 1.6 0 0 0-1.6-1.6Z\"/>", "i12": "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-miterlimit=\"10\" stroke-width=\"1.5\" d=\"M11.83 14v-.621a2.33 2.33 0 0 1 1.164-2.02c1.126-.66 1.514-2.057.854-3.183s-2.057-1.514-3.183-.854C9.965 7.75 9.5 8.487 9.5 9.341M12 17h-.008M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12s4.477 10 10 10 10-4.477 10-10\"/>", "i13": "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-miterlimit=\"10\" stroke-width=\"1.5\" d=\"M8 12h8m-8 3h4M8 9h8M4.4 4h15.2A2.4 2.4 0 0 1 22 6.4v11.2a2.4 2.4 0 0 1-2.4 2.4H4.4A2.4 2.4 0 0 1 2 17.6V6.4A2.4 2.4 0 0 1 4.4 4\"/>", "i14": "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-miterlimit=\"10\" stroke-width=\"1.5\" d=\"M10.372 13.127a3.78 3.78 0 0 1 .317-4.91l4.05-4.124a3.62 3.62 0 0 1 5.187 0 3.78 3.78 0 0 1 0 5.278l-2.709 2.93m-4.043-1.65a3.78 3.78 0 0 1 0 5.261L9.26 19.907a3.62 3.62 0 0 1-5.186 0 3.78 3.78 0 0 1 0-5.278l2.607-2.739\"/>", "i15": "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-miterlimit=\"10\" stroke-width=\"1.5\" d=\"m18.657 6.657-1.414-1.414m-3.536 6.364-8.061 9.475a1.6 1.6 0 0 1-2.263 0l-.565-.566a1.6 1.6 0 0 1 0-2.262l9.475-8.062m3.535 3.536 3.536-3.536m-9.192-2.12 3.535-3.536m-5.091.848L11.02 2.98a.8.8 0 0 1 1.131 0l8.769 8.768a.8.8 0 0 1 0 1.131l-2.405 2.405a.8.8 0 0 1-1.131 0L8.616 6.515a.8.8 0 0 1 0-1.13\"/>", "i16": "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-miterlimit=\"10\" stroke-width=\"1.5\" d=\"m2 8 2 2 4-4m4 2h10M2 16l2 2 4-4m4 2h10\"/>", "i17": "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-miterlimit=\"10\" stroke-width=\"1.5\" d=\"M2 2v17.6A2.4 2.4 0 0 0 4.4 22h2.2A2.4 2.4 0 0 0 9 19.6V2H1m15 3v14.6a2.4 2.4 0 0 1-2.4 2.4H6.4m7 0h7.2a2.4 2.4 0 0 0 2.4-2.4V5h-8m-6 6h7M5 6h1M5 9h1m-1 3h1m-1 3h1m-1 3h1m13-6h1m-1-3h1m-1 6h1m-1 3h1m-8 0h1m-1-3h1\"/>", "i18": "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"1.5\" d=\"M12.707 15.293 18 10m1.806 10a9.77 9.77 0 0 0 2.13-5.037 9.7 9.7 0 0 0-.922-5.38 9.9 9.9 0 0 0-3.69-4.071A10.1 10.1 0 0 0 12 4c-1.884 0-3.73.524-5.324 1.512a9.9 9.9 0 0 0-3.69 4.07 9.7 9.7 0 0 0-.921 5.38A9.77 9.77 0 0 0 4.194 20zM13 16a1 1 0 1 1-2 0 1 1 0 0 1 2 0\"/>", "i19": "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-miterlimit=\"10\" stroke-width=\"1.5\" d=\"m21 21-4-4m-9-6h6m-3 3V8m8 3a8 8 0 1 1-16 0 8 8 0 0 1 16 0\"/>", "i20": "<path fill=\"currentColor\" d=\"M12 12h-.75c0 .414.336.75.75.75zm4.971-8.432a.75.75 0 1 0-1.06-1.06l.53.53zm-5.501 3.38a.75.75 0 0 0 1.06 1.06l-.53-.53zm10.066 1.23a.75.75 0 0 0-1.061-1.062l.53.53zm-5.414 3.292a.75.75 0 0 0 1.06 1.06l-.53-.53zM22 12h.75c0-5.937-4.813-10.75-10.75-10.75v1.5A9.25 9.25 0 0 1 21.25 12zM12 2v-.75C6.063 1.25 1.25 6.063 1.25 12h1.5A9.25 9.25 0 0 1 12 2.75zM2 12h-.75c0 5.937 4.813 10.75 10.75 10.75v-1.5A9.25 9.25 0 0 1 2.75 12zm10 10v.75c5.937 0 10.75-4.813 10.75-10.75h-1.5A9.25 9.25 0 0 1 12 21.25zm-7.071-2.929.53.53L19.601 5.46l-.53-.53-.53-.53L4.399 18.54zM12 12v.75h10v-1.5H12zm0 0h.75V2h-1.5v10zm4.44-8.962-.53-.53-4.44 4.44.53.53.53.53 4.441-4.44zm4.565 4.609-.53-.53-4.353 4.353.53.53.53.53 4.354-4.353z\"/>", "i21": "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-miterlimit=\"10\" stroke-width=\"1.5\" d=\"M3 11.851C3 12.483 3.54 13 4.2 13h14.4c1.32 0 2.4-1.034 2.4-2.298V5.15C21 4.517 20.46 4 19.8 4H5.4C4.08 4 3 5.034 3 6.298zm0 0V20\"/>", "i22": "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-miterlimit=\"10\" stroke-width=\"1.5\" d=\"M7 11 3 7m0 0 4-4M3 7h18m-4 14 4-4m0 0-4-4m4 4H3\"/>", "i23": "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"1.5\" d=\"M12 21c-2.6-2.3-6-6.1-6-10a6 6 0 0 1 12 0c0 .8-.1 1.6-.4 2.4M12 12.8a1.8 1.8 0 1 0 0-3.6 1.8 1.8 0 0 0 0 3.6m7.4 6.6 1.8 1.8m-1.2-4.2a2.7 2.7 0 1 1-5.4 0 2.7 2.7 0 0 1 5.4 0\"/>", "i24": "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"1.5\" d=\"M12 15V4m0 0-4 4m4-4 4 4M5 14v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-4\"/>"};
  var SITES = /*sites*/{"india": {"tabs": [], "dash": "", "pages": [["india/", "Overview", "i0"], ["india/constituencies/", "Constituencies", "i23"], ["india/disputes/", "Disputes", "i15"], ["india/rti/", "RTI Replies", "i13"], ["india/women/", "Women", "i3"], ["india/cities/", "Cities", "i17"], ["india/numbers/", "Numbers", "i11"], ["india/compare/", "Comparisons", "i22"], ["india/cases/", "Case Studies", "i23"], ["india/urban/", "Urban", "i7"], ["india/factors/", "District Factors", "i22"], ["india/uts/", "Territories", "i21"], ["india/process/", "Rules", "i15"], ["india/progress/", "Progress", "i18"], ["india/nrc/", "The NRC", "i16"], ["india/method/", "Method", "i10"], ["india/faq/", "Questions", "i12"], ["india/report/", "Report", "i13"]]}, "bihar": {"tabs": [["overview", "Overview", "i0"], ["deletions", "Left Off or Deleted", "i1"], ["reasons", "Reasons", "i16"], ["phases", "Phases", "i2"], ["gender", "Women", "i3"], ["caste", "Caste", "i4"], ["religion", "Religion", "i5"], ["electoral", "Elections", "i6"], ["geographic", "Geography", "i7"], ["economic", "District Factors", "i8"], ["research", "Research", "i9"], ["methodology", "Method", "i10"]], "dash": "bihar/", "pages": [["bihar/explorer/", "Explorer", "i19"], ["bihar/results/", "Elections", "i6"], ["bihar/people/", "People", "i20"], ["bihar/border/", "Border", "i21"], ["bihar/districts/", "Districts", "i11"], ["bihar/faq/", "Questions", "i12"], ["bihar/method/", "Method", "i10"], ["bihar/report/", "Report", "i13"]]}, "hyd": {"tabs": [["overview", "Overview", "i0"], ["deletions", "Exclusions", "i1"], ["age", "Age", "i3"], ["religion", "Religion", "i5"], ["link", "Linkage", "i14"], ["hearings", "Hearings", "i15"], ["parts", "Parts", "i11"], ["electoral", "Elections", "i6"], ["research", "Research", "i9"], ["methodology", "Method", "i10"]], "dash": "hyderabad/", "pages": [["hyderabad/explorer/", "Explorer", "i19"], ["hyderabad/people/", "People", "i20"], ["hyderabad/parts/", "Parts", "i11"], ["hyderabad/hearings/", "Hearings", "i15"], ["hyderabad/telangana/", "Statewide", "i7"], ["hyderabad/faq/", "Questions", "i12"], ["hyderabad/method/", "Method", "i10"], ["hyderabad/report/", "Report", "i13"]]}, "tn": {"tabs": [], "dash": "", "pages": [["tamilnadu/", "Overview", "i0"], ["tamilnadu/elections/", "Elections", "i6"], ["tamilnadu/faq/", "Questions", "i12"], ["tamilnadu/method/", "Method", "i10"]]}, "ka": {"tabs": [], "dash": "", "pages": [["karnataka/", "Overview", "i0"], ["karnataka/faq/", "Questions", "i12"], ["karnataka/method/", "Method", "i10"]]}, "wb": {"tabs": [], "dash": "", "pages": [["westbengal/", "Overview", "i0"], ["westbengal/elections/", "Elections", "i6"], ["westbengal/faq/", "Questions", "i12"], ["westbengal/method/", "Method", "i10"]]}, "kl": {"tabs": [], "dash": "", "pages": [["kerala/", "Overview", "i0"], ["kerala/elections/", "Elections", "i6"], ["kerala/faq/", "Questions", "i12"], ["kerala/method/", "Method", "i10"]]}, "rj": {"tabs": [], "dash": "", "pages": [["rajasthan/", "Overview", "i0"], ["rajasthan/faq/", "Questions", "i12"], ["rajasthan/method/", "Method", "i10"]]}, "up": {"tabs": [], "dash": "", "pages": [["uttarpradesh/", "Overview", "i0"], ["uttarpradesh/faq/", "Questions", "i12"], ["uttarpradesh/method/", "Method", "i10"]]}, "dl": {"tabs": [], "dash": "", "pages": [["delhi/", "Overview", "i0"], ["delhi/faq/", "Questions", "i12"], ["delhi/method/", "Method", "i10"]]}, "mh": {"tabs": [], "dash": "", "pages": [["maharashtra/", "Overview", "i0"], ["maharashtra/faq/", "Questions", "i12"], ["maharashtra/method/", "Method", "i10"]]}, "gj": {"tabs": [], "dash": "", "pages": [["gujarat/", "Overview", "i0"], ["gujarat/elections/", "Elections", "i6"], ["gujarat/faq/", "Questions", "i12"], ["gujarat/method/", "Method", "i10"]]}, "uk": {"tabs": [], "dash": "", "pages": [["uttarakhand/", "Overview", "i0"], ["uttarakhand/faq/", "Questions", "i12"], ["uttarakhand/method/", "Method", "i10"]]}, "as": {"tabs": [], "dash": "", "pages": [["assam/", "Overview", "i0"], ["assam/faq/", "Questions", "i12"], ["assam/method/", "Method", "i10"]]}, "cg": {"tabs": [], "dash": "", "pages": [["chhattisgarh/", "Overview", "i0"], ["chhattisgarh/faq/", "Questions", "i12"], ["chhattisgarh/method/", "Method", "i10"]]}, "mp": {"tabs": [], "dash": "", "pages": [["madhyapradesh/", "Overview", "i0"], ["madhyapradesh/faq/", "Questions", "i12"], ["madhyapradesh/method/", "Method", "i10"]]}, "ap": {"tabs": [], "dash": "", "pages": [["andhrapradesh/", "Overview", "i0"], ["andhrapradesh/faq/", "Questions", "i12"], ["andhrapradesh/method/", "Method", "i10"]]}, "od": {"tabs": [], "dash": "", "pages": [["odisha/", "Overview", "i0"], ["odisha/faq/", "Questions", "i12"], ["odisha/method/", "Method", "i10"]]}, "jh": {"tabs": [], "dash": "", "pages": [["jharkhand/", "Overview", "i0"], ["jharkhand/faq/", "Questions", "i12"], ["jharkhand/method/", "Method", "i10"]]}, "hr": {"tabs": [], "dash": "", "pages": [["haryana/", "Overview", "i0"], ["haryana/faq/", "Questions", "i12"], ["haryana/method/", "Method", "i10"]]}, "pb": {"tabs": [], "dash": "", "pages": [["punjab/", "Overview", "i0"], ["punjab/faq/", "Questions", "i12"], ["punjab/method/", "Method", "i10"]]}, "ga": {"tabs": [], "dash": "", "pages": [["goa/", "Overview", "i0"], ["goa/faq/", "Questions", "i12"], ["goa/method/", "Method", "i10"]]}, "mn": {"tabs": [], "dash": "", "pages": [["manipur/", "Overview", "i0"], ["manipur/faq/", "Questions", "i12"], ["manipur/method/", "Method", "i10"]]}, "ml": {"tabs": [], "dash": "", "pages": [["meghalaya/", "Overview", "i0"], ["meghalaya/faq/", "Questions", "i12"], ["meghalaya/method/", "Method", "i10"]]}, "mz": {"tabs": [], "dash": "", "pages": [["mizoram/", "Overview", "i0"], ["mizoram/faq/", "Questions", "i12"], ["mizoram/method/", "Method", "i10"]]}, "nl": {"tabs": [], "dash": "", "pages": [["nagaland/", "Overview", "i0"], ["nagaland/faq/", "Questions", "i12"], ["nagaland/method/", "Method", "i10"]]}, "sk": {"tabs": [], "dash": "", "pages": [["sikkim/", "Overview", "i0"], ["sikkim/faq/", "Questions", "i12"], ["sikkim/method/", "Method", "i10"]]}, "ar": {"tabs": [], "dash": "", "pages": [["arunachal/", "Overview", "i0"], ["arunachal/faq/", "Questions", "i12"], ["arunachal/method/", "Method", "i10"]]}, "tr": {"tabs": [], "dash": "", "pages": [["tripura/", "Overview", "i0"], ["tripura/faq/", "Questions", "i12"], ["tripura/method/", "Method", "i10"]]}, "py": {"tabs": [], "dash": "", "pages": [["puducherry/", "Overview", "i0"], ["puducherry/faq/", "Questions", "i12"], ["puducherry/method/", "Method", "i10"]]}, "ch": {"tabs": [], "dash": "", "pages": [["chandigarh/", "Overview", "i0"], ["chandigarh/faq/", "Questions", "i12"], ["chandigarh/method/", "Method", "i10"]]}, "ld": {"tabs": [], "dash": "", "pages": [["lakshadweep/", "Overview", "i0"], ["lakshadweep/faq/", "Questions", "i12"], ["lakshadweep/method/", "Method", "i10"]]}, "an": {"tabs": [], "dash": "", "pages": [["andaman/", "Overview", "i0"], ["andaman/faq/", "Questions", "i12"], ["andaman/method/", "Method", "i10"]]}, "dd": {"tabs": [], "dash": "", "pages": [["dnhdd/", "Overview", "i0"], ["dnhdd/faq/", "Questions", "i12"], ["dnhdd/method/", "Method", "i10"]]}}/*sites*/;
  if (nav) (function () {
    // SITES is written from site/places.json by scripts/build_site.py.
    var body = document.body, site = body.getAttribute('data-place'), map = SITES[site];
    if (!map) return;
    var root = body.getAttribute('data-root') || '', dash = root + map.dash;
    var tabs = [].slice.call(nav.querySelectorAll('.nav-tab[data-tab]')), onDash = tabs.length > 0;
    function tr(k) { return (L.lang !== 'en' && window.SIR_DICT && window.SIR_DICT[k]) || k; }
    function ico(n) { return '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">' + ICONS[n] + '</svg>'; }
    var here = location.pathname.replace(/index\.html$/, '');
    function path(h) { return new URL(h, location.href).pathname.replace(/index\.html$/, ''); }
    // Each entry: label, icon, and either a tab to click or an address.
    var A = map.tabs.map(function (t) { return { key: t[0], label: tr(t[1]), icon: t[2], tab: onDash ? nav.querySelector('[data-tab="' + t[0] + '"]') : null, href: onDash ? null : dash + '#' + t[0] }; });
    var B = map.pages.map(function (p) { return { label: tr(p[1]), icon: p[2], href: root + p[0] }; });
    var seq = onDash ? A : B;
    if (seq.length < 2) return;
    var cur = document.querySelector('header.top .places .lbl-place');
    var place = cur ? cur.textContent.trim() : '';
    function index() {
      for (var i = 0; i < seq.length; i++) {
        if (onDash ? seq[i].tab && seq[i].tab.getAttribute('aria-selected') === 'true' : path(seq[i].href) === here) return i;
      }
      return -1;
    }
    function go(e) { if (!e) return; if (e.tab) e.tab.click(); else location.href = e.href; }
    function item(e, g, i) {
      var inner = ico(e.icon) + '<span>' + e.label + '</span>';
      return e.tab ? '<button type="button" data-g="' + g + '" data-i="' + i + '">' + inner + '</button>' : '<a href="' + e.href + '" data-g="' + g + '" data-i="' + i + '">' + inner + '</a>';
    }
    var arrowPrev = '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><polyline points="15 18 9 12 15 6"/></svg>';
    var arrowNext = '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><polyline points="9 18 15 12 9 6"/></svg>';
    var caret = '<svg class="icon caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg>';
    var bar = document.createElement('div');
    bar.className = 'secbar';
    bar.innerHTML = '<button type="button" class="sec-step sec-prev" aria-label="' + L('Previous section') + '">' + arrowPrev + '</button>' +
      '<button type="button" class="sec-now" aria-expanded="false" aria-controls="secmenu"><span class="sec-where"></span><span class="sec-count"></span>' + caret + '</button>' +
      '<button type="button" class="sec-step sec-next" aria-label="' + L('Next section') + '">' + arrowNext + '</button>' +
      '<div class="secmenu" id="secmenu" hidden>' +
        (A.length ? '<p class="sechead">' + L('Dashboard') + '</p><div class="secgrid">' + A.map(function (e, i) { return item(e, 'a', i); }).join('') + '</div>' : '') +
        (A.length ? '<p class="sechead">' + L('More pages') + '</p>' : '') + '<div class="secgrid">' + B.map(function (e, i) { return item(e, 'b', i); }).join('') + '</div>' +
      '</div>';
    nav.parentNode.insertBefore(bar, nav);
    document.documentElement.classList.add('has-secbar');
    var now = bar.querySelector('.sec-now'), menu = bar.querySelector('.secmenu');
    function paint() {
      var i = index(), e = seq[i];
      var name = e ? e.label : (document.querySelector('.page-head h1') || {}).textContent || '';
      bar.querySelector('.sec-where').innerHTML = (place && name !== place ? '<span class="sec-crumb">' + place + ' <span aria-hidden="true">›</span></span> ' : '') + '<b>' + name + '</b>';
      bar.querySelector('.sec-count').textContent = i < 0 ? '' : L('{i} of {n}', { i: i + 1, n: seq.length });
      bar.querySelector('.sec-prev').disabled = i <= 0;
      bar.querySelector('.sec-next').disabled = i < 0 || i === seq.length - 1;
      var g = onDash ? 'a' : 'b';
      menu.querySelectorAll('[data-i]').forEach(function (b) {
        var on = b.getAttribute('data-g') === g && +b.getAttribute('data-i') === i;
        b.classList.toggle('on', on);
        if (on) b.setAttribute('aria-current', onDash ? 'true' : 'page'); else b.removeAttribute('aria-current');
      });
    }
    function open(v) { menu.hidden = !v; now.setAttribute('aria-expanded', v ? 'true' : 'false'); if (v) { var o = menu.querySelector('.on'); (o || menu.querySelector('[data-i]')).focus(); } }
    now.addEventListener('click', function () { open(menu.hidden); });
    bar.querySelector('.sec-prev').addEventListener('click', function () { open(false); go(seq[index() - 1]); });
    bar.querySelector('.sec-next').addEventListener('click', function () { open(false); go(seq[index() + 1]); });
    menu.addEventListener('click', function (e) {
      var b = e.target.closest('button[data-i]'); if (!b) return; // links navigate on their own
      open(false); go(A[+b.getAttribute('data-i')]); now.focus();
    });
    document.addEventListener('click', function (e) { if (!menu.hidden && !bar.contains(e.target)) open(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !menu.hidden) { open(false); now.focus(); } });
    // A dashboard switches tabs without loading a page; follow it.
    new MutationObserver(paint).observe(nav, { attributes: true, subtree: true, attributeFilter: ['aria-selected'] });
    paint();
  })();

  // On a wide screen the places menu sets every state and territory out in
  // columns beside the rest (sir.css), so that list is open whenever the
  // menu is; on a phone it stays a fold.
  var placesMenu = document.querySelector('header.top details.places');
  if (placesMenu) placesMenu.addEventListener('toggle', function () {
    if (placesMenu.open && window.matchMedia('(min-width:1000px)').matches) placesMenu.querySelectorAll('details.grp').forEach(function (g) { g.open = true; });
  });
  // The header menus close on a click elsewhere and on Escape.
  document.addEventListener('click', function (e) {
    document.querySelectorAll('details.dl[open]').forEach(function (d) { if (!d.contains(e.target)) d.removeAttribute('open'); });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    document.querySelectorAll('details.dl[open]').forEach(function (d) { d.removeAttribute('open'); d.querySelector('summary').focus(); });
  });

  // --------------------------------------------------------------- charts
  // A long string as lines of at most n characters, broken at spaces.
  SIR.wrap = function (s, n) {
    if (typeof s !== 'string' || s.length <= n) return s;
    // a long hyphenated name (Manendragarh-Chirmiri-Bharatpur) may break
    // after a hyphen, which keeps it inside a phone's label column
    var out = [], cur = '', words = [];
    s.split(' ').forEach(function (w) { if (w.length > n && w.indexOf('-') > 0) words = words.concat(w.split(/(?<=-)/)); else words.push(w); });
    words.forEach(function (w) {
      var sep = !cur || /-$/.test(cur) ? '' : ' ';
      if (cur && (cur + sep + w).length > n) { out.push(cur); cur = w; } else cur = cur + sep + w;
    });
    if (cur) out.push(cur);
    return out;
  };
  // On a phone a chart is about 320px wide. Chart.js squeezes a long axis
  // title into that width rather than wrapping it, cuts long category labels
  // at the edge, tilts short ones and lets big tick numbers run together.
  // Wrap titles and category labels, keep labels level where they fit, and
  // thin the value ticks. A chart's own tick callback is left alone.
  var SHORT = { 'Dadra and Nagar Haveli and Daman and Diu': 'DNH and Daman and Diu', 'Andaman and Nicobar Islands': 'Andaman and Nicobar' };
  SIR.short = function (x) { return SHORT[x] || x; };
  SIR.fitPhone = function (cfg) {
    if (window.innerWidth >= 600 || !/^(bar|line|scatter|bubble)$/.test(cfg.type)) return cfg;
    var o = cfg.options = cfg.options || {}, sc = o.scales = o.scales || {};
    var horiz = o.indexAxis === 'y', catAxis = cfg.type === 'bar' || cfg.type === 'line' ? (horiz ? 'y' : 'x') : null;
    var nLabels = ((cfg.data || {}).labels || []).length;
    ['x', 'y'].forEach(function (k) { sc[k] = sc[k] || {}; });
    Object.keys(sc).forEach(function (k) {
      var a = sc[k], t = a.ticks = a.ticks || {}, isX = k === 'x' || a.axis === 'x';
      if (a.title && typeof a.title.text === 'string') a.title.text = SIR.wrap(a.title.text, isX ? 34 : 40);
      if (k === catAxis) {
        var lab = function (x) { return SIR.wrap(SHORT[x] || x, horiz ? 20 : 12); };
        if (!t.callback) t.callback = function (v) { return lab(this.getLabelForValue(v)); };
        // Level only if the longest line fits its slot (about 6.5px a character).
        var widest = Math.max.apply(null, cfg.data.labels.map(function (x) { return [].concat(lab(String(x))).reduce(function (m, l) { return Math.max(m, l.length); }, 0); }).concat([0]));
        if (!horiz && nLabels && widest * 6.5 <= 300 / nLabels - 4 && t.maxRotation == null) { t.maxRotation = 0; t.autoSkip = false; }
      } else if (a.type !== 'logarithmic' && a.type !== 'time' && a.type !== 'category') {
        if (t.maxTicksLimit == null) t.maxTicksLimit = isX ? 5 : 7;
        // 8,000,000 takes a third of a phone's width; 80 lakh does not.
        if (!t.callback) t.callback = function (v, i, ts) {
          return Math.abs(v) >= 1e7 ? L('{x} crore', { x: String(+(v / 1e7).toFixed(2)) }) : Math.abs(v) >= 1e5 ? L('{x} lakh', { x: String(+(v / 1e5).toFixed(1)) }) : Chart.Ticks.formatters.numeric.call(this, v, i, ts);
        };
        if (isX && t.maxRotation == null) { t.maxRotation = 0; t.autoSkipPadding = 14; }
      } else if (isX && t.maxRotation == null && a.type === 'logarithmic') { t.maxRotation = 0; t.autoSkipPadding = 8; }
    });
    return cfg;
  };
  SIR.charts = [];
  // One look for every Chart.js chart on the site, set here so the 110-odd
  // bar charts across the pages and both dashboards share it: rounded bars
  // of a sensible thickness, no grid along the category axis, no axis rules,
  // rounded legend keys and a dark, padded tooltip.
  SIR.polish = function (cfg) {
    if (typeof Chart === 'undefined') return cfg;
    var D = Chart.defaults;
    D.elements.bar.borderRadius = 4;
    D.elements.bar.borderSkipped = 'start';
    D.datasets.bar.maxBarThickness = 26;
    D.datasets.bar.categoryPercentage = 0.78;
    D.datasets.bar.barPercentage = 0.9;
    D.elements.line.tension = 0.3;
    D.elements.line.borderWidth = 2.5;
    D.elements.point.radius = 3;
    D.elements.point.hoverRadius = 6;
    D.scale.border = D.scale.border || {}; D.scale.border.display = false;
    D.scale.ticks.padding = 6;
    D.plugins.legend.labels.usePointStyle = true;
    D.plugins.legend.labels.pointStyle = 'rectRounded';
    var t = D.plugins.tooltip;
    t.backgroundColor = 'rgba(20,28,38,0.94)'; t.padding = 10; t.cornerRadius = 8; t.boxPadding = 4;
    t.titleFont = { weight: '600' }; t.displayColors = true; t.usePointStyle = true;
    // a stacked bar needs no rounding between its segments
    var stacked = false, sc = (cfg.options && cfg.options.scales) || {};
    Object.keys(sc).forEach(function (k) { if (sc[k] && sc[k].stacked) stacked = true; });
    if (cfg.type === 'bar') {
      cfg.options = cfg.options || {}; cfg.options.scales = cfg.options.scales || {};
      var cat = cfg.options.indexAxis === 'y' ? 'y' : 'x', a = cfg.options.scales[cat] = cfg.options.scales[cat] || {};
      a.grid = a.grid || {}; if (a.grid.display == null) a.grid.display = false;
      if (stacked) (cfg.data.datasets || []).forEach(function (ds) { if (ds.borderRadius == null) ds.borderRadius = 0; });
    }
    return cfg;
  };
  // Where a better form fits (a ranked list, measures side by side),
  // assets/viz.js draws it in SVG in place of the canvas. Returns a stub with
  // the destroy() the pages call before a redraw, or null to use Chart.js.
  SIR.viz = function (id, cfg) {
    if (!window.VIZ || cfg.$chartjs) return null;
    var el = document.getElementById(id); if (!el) return null;
    var box = el;
    // put the box in the page first, so the chart can measure its width
    if (el.tagName === 'CANVAS') { box = document.createElement('div'); box.className = 'vizbox'; el.parentNode.classList.add('has-viz'); el.parentNode.replaceChild(box, el); }
    if (!VIZ.fromChart(box, cfg, el.getAttribute('aria-label'))) {
      if (box !== el) { box.parentNode.classList.remove('has-viz'); box.parentNode.replaceChild(el, box); }
      return null;
    }
    if (box !== el) box.id = id;
    return { viz: true, box: box, destroy: function () {}, update: function () {} };
  };
  SIR.chart = function (id, cfg) {
    var v = SIR.viz(id, cfg); if (v) return v;
    if (typeof Chart === 'undefined') {
      var el = document.getElementById(id);
      if (el) el.parentNode.insertAdjacentHTML('beforeend', '<p class="pill">' + L('The chart library did not load, so use the table below, which has the same figures.') + '</p>');
      return null;
    }
    Chart.defaults.font.family = '"Helvetica Neue", Arial, sans-serif';
    Chart.defaults.font.size = 12;
    Chart.defaults.maintainAspectRatio = false;
    // Set a field, never replace the object: the defaults carry the easing
    // function, and a fresh object without it breaks every animated chart.
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) Chart.defaults.animation = false;
    else Chart.defaults.animation.duration = 300;
    // Resolve token colours before construction, and turn off Chart.js's own
    // palette plugin: left on, it paints its defaults over colours set later.
    Chart.defaults.plugins.colors = Chart.defaults.plugins.colors || {};
    Chart.defaults.plugins.colors.enabled = false;
    (cfg.data.datasets || []).forEach(function (ds) {
      if (ds.$token) { var v = SIR.css(ds.$token); ds.backgroundColor = v; ds.borderColor = v; }
      if (ds.$tokens) { var vs = ds.$tokens.map(SIR.css); ds.backgroundColor = vs; ds.borderColor = vs; }
    });
    // Horizontal bars carry their categories as tick labels: never skip one.
    cfg.options = cfg.options || {};
    if (cfg.options.indexAxis === 'y') { cfg.options.scales = cfg.options.scales || {}; var ys = cfg.options.scales.y = cfg.options.scales.y || {}; ys.ticks = ys.ticks || {}; if (ys.ticks.autoSkip == null) ys.ticks.autoSkip = false; }
    // On a phone, smaller type and compact legend keys leave room for the data.
    if (window.innerWidth < 600) {
      Chart.defaults.font.size = 11;
      cfg.options.plugins = cfg.options.plugins || {};
      var lg = cfg.options.plugins.legend = cfg.options.plugins.legend || {};
      lg.labels = lg.labels || {}; lg.labels.boxWidth = 10; lg.labels.boxHeight = 10; lg.labels.padding = 6;
      SIR.fitPhone(cfg);
    }
    SIR.polish(cfg);
    var c = new Chart(document.getElementById(id), cfg);
    c.$tokens = cfg.$tokens || null;
    SIR.recolour(c);
    SIR.charts.push(c);
    return c;
  };
  // For pages that redraw on selection: drop the chart on this canvas first,
  // or Chart.js refuses to reuse it.
  SIR.redraw = function (id, cfg) {
    if (typeof Chart !== 'undefined') {
      var old = Chart.getChart(document.getElementById(id));
      if (old) { SIR.charts = SIR.charts.filter(function (c) { return c !== old; }); old.destroy(); }
    }
    return SIR.chart(id, cfg);
  };
  SIR.recolour = function (c) {
    var ink = SIR.css('--ink'), muted = SIR.css('--muted'), line = SIR.css('--line');
    // Set fields on Chart.js's option proxies; replacing an options object
    // detaches the functions it resolves through (legend label generation).
    Object.values(c.options.scales || {}).forEach(function (s) {
      if (s.ticks) s.ticks.color = muted;
      if (s.grid) s.grid.color = line;
      if (s.title) s.title.color = muted;
    });
    if (c.options.plugins && c.options.plugins.legend && c.options.plugins.legend.labels) c.options.plugins.legend.labels.color = ink;
    c.data.datasets.forEach(function (ds) {
      if (ds.$token) { var v = SIR.css(ds.$token); ds.backgroundColor = v; ds.borderColor = v; }
      if (ds.$tokens) { var vs = ds.$tokens.map(SIR.css); ds.backgroundColor = vs; ds.borderColor = vs; }
    });
    c.update('none');
  };

  // --------------------------------------------------------------- tables
  // cols: [{k, label, fmt, left}], rows: objects. Sorting is by button in the
  // header cell so it is reachable by keyboard; aria-sort says which.
  SIR.table = function (el, cols, rows, opts) {
    opts = opts || {};
    var key = opts.sort || cols[0].k, dir = opts.dir || -1;
    function render() {
      var sorted = rows.slice().sort(function (a, b) {
        var x = a[key], y = b[key];
        if (typeof x === 'string' || typeof y === 'string') return dir * String(x).localeCompare(String(y));
        return dir * ((x == null ? -Infinity : x) - (y == null ? -Infinity : y));
      });
      var h = '<thead><tr>' + cols.map(function (c) {
        var s = c.k === key ? (dir < 0 ? 'descending' : 'ascending') : 'none';
        return '<th scope="col" class="' + (c.left ? 'l' : '') + '" aria-sort="' + s + '"><button type="button" data-k="' + c.k + '">' + c.label + '</button></th>';
      }).join('') + '</tr></thead><tbody>' + sorted.slice(0, opts.limit || sorted.length).map(function (r) {
        return '<tr' + (opts.onRow ? ' class="link"' : '') + '>' + cols.map(function (c, i) {
          var v = c.fmt ? c.fmt(r[c.k], r) : SIR.esc(r[c.k]);
          if (i === 0 && opts.onRow) v = '<button type="button" class="open" data-id="' + SIR.esc(r[opts.id || c.k]) + '">' + v + '</button>';
          return '<td class="' + (c.left ? 'l' : '') + '" data-label="' + SIR.esc(String(c.label).replace(/<[^>]+>/g, '')) + '">' + v + '</td>';
        }).join('') + '</tr>';
      }).join('') + '</tbody>';
      el.innerHTML = h;
      // on a phone each row becomes a card with every figure named, and the
      // header stays as a row of sort buttons (sir.css)
      el.classList.add('stack', 'sortable');
      el.querySelectorAll('th button').forEach(function (b) {
        b.addEventListener('click', function () { var k = b.getAttribute('data-k'); dir = k === key ? -dir : -1; key = k; render(); });
      });
      if (opts.onRow) {
        el.querySelectorAll('button.open').forEach(function (b) { b.addEventListener('click', function () { opts.onRow(b.getAttribute('data-id')); }); });
        el.querySelectorAll('tr.link').forEach(function (tr) { tr.addEventListener('click', function (e) { if (e.target.tagName !== 'BUTTON') tr.querySelector('button.open').click(); }); });
      }
    }
    render();
  };

  SIR.fail = function (e) {
    if (window.console) console.error(e && e.stack);
    var m = document.querySelector('main');
    if (m) m.insertAdjacentHTML('afterbegin', '<p class="caveat">' + L('The data for this page did not load ({msg}). Reload the page and try again.', { msg: SIR.esc(e.message) }) + '</p>');
  };

  // ---- "In short" box: numbered plain sentences at the top of a page.
  SIR.inShort = function (points, note) {
    var ol = document.getElementById('short');
    if (ol) ol.innerHTML = points.filter(Boolean).map(function (t) { return '<li>' + t + '</li>'; }).join('');
    var n = document.getElementById('shortNote');
    if (n) { n.innerHTML = note || ''; n.hidden = !note; }
    // the page's own share row, under its findings: WhatsApp opens with the
    // page's title and its first finding already written
    if (ol && ol.children.length && !document.querySelector('.pageshare')) {
      var first = ol.children[0].innerText.replace(/\s+/g, ' ').trim(),
        h = document.querySelector('main h1'), k = document.querySelector('main .kicker'),
        title = (k ? k.textContent.trim() + ', ' : '') + (h ? h.textContent.trim() : document.title),
        text = title + '. ' + first, bar = document.createElement('div');
      bar.className = 'tools pageshare';
      bar.innerHTML = '<a class="btn" target="_blank" rel="noopener" href="' + SIR.esc(SIR.wa(text)) + '">' + L('Share on WhatsApp') + '</a><button type="button">' + L('Copy link') + '</button>';
      bar.querySelector('button').addEventListener('click', function (e) { copy(SIR.pageUrl(), e.target); });
      ol.parentNode.insertBefore(bar, ol.nextSibling);
    }
  };

  // ---- Questions and answers. Each analysis registers one loader
  // (assets/faq/<site>.js) returning [[question, answer, [page keys]], ...].
  // ---- sharing. WhatsApp opens with the text already written; on a phone
  // that is the app, on a computer WhatsApp Web.
  // a link shared from a translated page opens in the same language
  SIR.pageUrl = function (hash) {
    var m = /[?&]lang=([a-z]{2})/.exec(location.search);
    return location.origin + location.pathname + (m && m[1] !== 'en' ? '?lang=' + m[1] : '') + (hash ? '#' + hash : '');
  };
  SIR.wa = function (text, hash) { return 'https://wa.me/?text=' + encodeURIComponent(text + '\n' + SIR.pageUrl(hash)); };
  function copy(text, btn) {
    var done = function () { var t = btn.textContent; btn.textContent = L('Copied'); setTimeout(function () { btn.textContent = t; }, 1500); };
    if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, function () {}); else { prompt('', text); }
  }
  function csvText(rows) {
    return '﻿' + rows.map(function (r) { return r.map(function (c) { c = c == null ? '' : String(c); return /[",\n]/.test(c) ? '"' + c.replace(/"/g, '""') + '"' : c; }).join(','); }).join('\n');
  }
  function save(href, name) { var a = document.createElement('a'); a.href = href; a.download = name; document.body.appendChild(a); a.click(); a.remove(); }
  var slug = function () { return (location.pathname.replace(/^\/|\/$/g, '').replace(/\//g, '-') || 'sir'); };

  // A link button on every section heading with an id (build_site.py gives
  // each h2 and h3 one): it copies the page's address with #section, so a
  // shared link opens on that section, in whatever language the reader uses.
  var LINKICON = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/></svg>';
  SIR.anchors = function (root) {
    (root || document).querySelectorAll('main h2[id], main h3[id]').forEach(function (h) {
      if (h.id === 'faqH' || h.querySelector('.anchor') || h.closest('.card, .qa, .tab-content, nav, .how')) return;
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'anchor'; b.setAttribute('data-no-i18n', '');
      b.setAttribute('aria-label', L('Copy a link to this section')); b.innerHTML = LINKICON;
      b.addEventListener('click', function () {
        var url = SIR.pageUrl(h.id);
        try { history.replaceState(null, '', '#' + h.id); } catch (e) {}
        var ok = function () { b.setAttribute('data-msg', L('Copied')); setTimeout(function () { b.removeAttribute('data-msg'); }, 1500); };
        if (navigator.clipboard) navigator.clipboard.writeText(url).then(ok, function () { prompt('', url); }); else prompt('', url);
      });
      h.appendChild(b);
    });
  };
  // A link to a section opens on it. Charts draw after the page loads and move
  // what is below them, so the jump is made again each time charts are added,
  // until the reader scrolls for themselves.
  // The part of the address after #, decoded. A malformed one (a stray %)
  // makes decodeURIComponent throw, which stopped the rest of a page's script;
  // it now reads as no hash at all.
  SIR.hashId = function () {
    try { return decodeURIComponent(location.hash.slice(1)); } catch (e) { return ''; }
  };
  var moved = false;
  ['wheel', 'touchstart', 'keydown'].forEach(function (ev) { addEventListener(ev, function () { moved = true; }, { once: true, passive: true }); });
  SIR.jump = function () {
    if (moved || !location.hash) return;
    var t = document.getElementById(SIR.hashId());
    if (t && t.closest('main')) t.scrollIntoView({ block: 'start' });
  };
  setTimeout(function () { SIR.anchors(); SIR.jump(); }, 0);

  // "On this page": on a long reading page (build_site.py marks it
  // has-toc), the sections listed in the left margin of a wide screen, the
  // one being read marked. It appears once the opening band has scrolled
  // away, and sir.css keeps the margin for it so no chart runs under it.
  SIR.toc = function () {
    if (!document.body.classList.contains('has-toc') || document.querySelector('nav.toc')) return;
    var hs = [].slice.call(document.querySelectorAll('main h2[id]')).filter(function (h) {
      return h.id !== 'faqH' && !h.closest('.card, .qa, .panel, .methodology, nav, .page-faq');
    });
    if (!hs.length) return;
    var nav = document.createElement('nav');
    nav.className = 'toc'; nav.setAttribute('aria-label', L('On this page'));
    nav.innerHTML = '<p class="toc-h">' + SIR.esc(L('On this page')) + '</p><ol>' + hs.map(function (h) {
      var c = h.cloneNode(true);
      c.querySelectorAll('.anchor').forEach(function (b) { b.remove(); });
      return '<li><a href="#' + h.id + '">' + SIR.esc(c.textContent.trim()) + '</a></li>';
    }).join('') + '</ol>';
    document.body.appendChild(nav);
    var links = nav.querySelectorAll('a'), head = document.querySelector('.page-head');
    var mark = function () {
      var cur = -1;
      hs.forEach(function (h, i) { if (h.getBoundingClientRect().top < 160) cur = i; });
      links.forEach(function (a, i) { if (i === cur) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current'); });
      nav.classList.toggle('on', !head || head.getBoundingClientRect().bottom < 120);
    };
    addEventListener('scroll', mark, { passive: true });
    mark();
  };
  setTimeout(SIR.toc, 0);

  // A row of buttons under every chart on a page: the picture, the numbers
  // behind it, and the finding written beside it, to send on.
  SIR.tools = function () {
    document.querySelectorAll('main .panel').forEach(function (panel) {
      if (panel.querySelector('.tools') || panel.closest('.card')) return;
      var box = panel.querySelector('.vizbox, canvas');
      if (!box || !box.id || !(box.querySelector && box.querySelector('svg') || box.tagName === 'CANVAS')) return;
      var id = box.id, name = slug() + '-' + id;
      // the finding is the first .finding after this chart, before the next heading
      var n = panel.closest('.grid') || panel, fin = null;
      while ((n = n.nextElementSibling)) { if (/^H[23]$/.test(n.tagName)) break; if (n.classList.contains('finding')) { fin = n; break; } }
      var bar = document.createElement('div'); bar.className = 'tools';
      bar.innerHTML = '<button type="button" data-t="png">' + L('PNG') + '</button><button type="button" data-t="csv">' + L('CSV') + '</button>' +
        '<a class="btn" data-t="wa" target="_blank" rel="noopener">' + L('WhatsApp') + '</a><button type="button" data-t="link">' + L('Copy link') + '</button>';
      var wa = bar.querySelector('[data-t=wa]');
      var text = function () { return (fin ? fin.innerText : (box.getAttribute('aria-label') || document.title)).replace(/\s+/g, ' ').trim(); };
      wa.href = SIR.wa(text(), id); wa.setAttribute('aria-label', L('Share this chart on WhatsApp'));
      wa.addEventListener('mouseenter', function () { wa.href = SIR.wa(text(), id); });
      bar.addEventListener('click', function (e) {
        var b = e.target.closest('[data-t]'); if (!b) return;
        var t = b.getAttribute('data-t');
        if (t === 'png') {
          if (box.tagName === 'CANVAS') {
            var ch = window.Chart && Chart.getChart(box); if (!ch) return;
            var c = document.createElement('canvas'); c.width = box.width; c.height = box.height;
            var g = c.getContext('2d'); g.fillStyle = getComputedStyle(document.body).getPropertyValue('--card').trim() || '#fff'; g.fillRect(0, 0, c.width, c.height); g.drawImage(box, 0, 0);
            save(c.toDataURL('image/png'), name + '.png');
          } else VIZ.png(box, name);
        } else if (t === 'csv') {
          var rows = box.__csv;
          if (!rows && box.tagName === 'CANVAS' && window.Chart && Chart.getChart(box)) {
            var d = Chart.getChart(box).data;
            rows = d.labels ? [['label'].concat(d.datasets.map(function (z) { return z.label || ''; }))].concat(d.labels.map(function (l, i) { return [Array.isArray(l) ? l.join(' ') : l].concat(d.datasets.map(function (z) { var v = z.data[i]; return v && typeof v === 'object' ? JSON.stringify(v) : v; })); }))
              : [['series', 'x', 'y', 'name']].concat([].concat.apply([], d.datasets.map(function (z) { return z.data.map(function (p) { return [z.label, p.x, p.y, p.n || '']; }); })));
          }
          if (rows) save(URL.createObjectURL(new Blob([csvText(rows)], { type: 'text/csv' })), name + '.csv');
        } else if (t === 'link') copy(SIR.pageUrl(id), b);
        else if (t === 'wa') wa.href = SIR.wa(text(), id);
      });
      panel.appendChild(bar);
    });
    SIR.anchors(); SIR.jump();
  };

  // ---- the finder: type a constituency, get its card, share it. A card has
  // its own address (#ac-12), so a shared link opens on that seat.
  // o: {rows, key(r) -> 'ac-12', label(r), card(r) -> html, share(r) -> text, pick(r)}
  // o is a set of rows (constituencies); o.more adds further sets (districts)
  // with their own key, label, card, share and pick. Every set's labels go
  // in the one list, and a link to any row opens on it.
  SIR.finder = function (el, o) {
    el = typeof el === 'string' ? document.getElementById(el) : el;
    var uid = el.id || 'finder', list = uid + '-list', sets = [o].concat(o.more || []), items = [];
    sets.forEach(function (st) { st.rows.forEach(function (r) { items.push({ s: st, r: r, l: st.label(r), k: st.key(r) }); }); });
    el.innerHTML = '<label for="' + uid + '-q">' + (o.prompt || L('Find a constituency')) + '</label>' +
      '<input id="' + uid + '-q" type="search" list="' + list + '" autocomplete="off" placeholder="' + (o.placeholder || L('Type a name or number')) + '">' +
      '<datalist id="' + list + '">' + items.map(function (it) { return '<option value="' + SIR.esc(it.l) + '">'; }).join('') + '</datalist>' +
      '<div class="fcard" aria-live="polite"></div>';
    var input = el.querySelector('input'), out = el.querySelector('.fcard');
    var byLabel = {}, byKey = {}, item = {};
    items.forEach(function (it) { byLabel[it.l.toLowerCase()] = it; item[it.k] = it; if (it.s === o) byKey[it.k] = it.r; });
    function find(v) {
      v = v.trim().toLowerCase(); if (!v) return null;
      if (byLabel[v]) return byLabel[v];
      var hit = items.filter(function (it) { var l = it.l.toLowerCase(); return l.indexOf(v) === 0 || l.indexOf(' ' + v) >= 0 || String(it.r.ac) === v; });
      return hit.length === 1 ? hit[0] : null;
    }
    function select(it, scroll) {
      if (!it) return;
      var st = it.s, r = it.r, k = it.k;
      input.value = it.l;
      out.innerHTML = '<h3>' + SIR.esc(st.title ? st.title(r) : it.l) + '</h3>' + st.card(r) +
        '<div class="tools">' + (o.seatPages && /^ac-\d+$/.test(k) ? '<a class="btn" href="' + (o.seatPages === true ? 'seat/' : o.seatPages) + k.slice(3) + '/">' + L('Open this constituency\'s own page') + '</a>' : '') +
        (o.districtPages && /^d-/.test(k) ? '<a class="btn" href="' + (o.districtPages === true ? 'district/' : o.districtPages) + k.slice(2) + '/">' + L('Open this district\'s own page') + '</a>' : '') +
        '<a class="btn" target="_blank" rel="noopener" href="' + SIR.wa(st.share(r), k) + '">' + L('Share on WhatsApp') + '</a>' +
        '<button type="button" data-t="link">' + L('Copy link') + '</button><button type="button" data-t="text">' + L('Copy text') + '</button></div>';
      out.querySelector('[data-t=link]').onclick = function () { copy(SIR.pageUrl(k), this); };
      out.querySelector('[data-t=text]').onclick = function () { copy(st.share(r) + '\n' + SIR.pageUrl(k), this); };
      // a card can carry buttons that open another row (a district's seats)
      out.querySelectorAll('[data-go]').forEach(function (b) { b.onclick = function () { select(item[b.getAttribute('data-go')], false); }; });
      if (history.replaceState) history.replaceState(null, '', '#' + k);
      if (st.pick) st.pick(r);
      if (scroll) el.scrollIntoView({ block: 'start' });
    }
    input.addEventListener('change', function () { select(find(input.value)); });
    input.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); select(find(input.value)); } });
    function fromHash(scroll) { var h = SIR.hashId(); if (item[h]) select(item[h], scroll); }
    fromHash(true);
    window.addEventListener('hashchange', function () { fromHash(true); });
    return { select: function (r) { var it = items.filter(function (x) { return x.r === r; })[0]; select(it, false); }, byKey: byKey, item: item };
  };
  // buttons for a list of rows, each opening that row's card
  SIR.goList = function (rows, key, label) {
    return '<p class="golist">' + rows.map(function (r) { return '<button type="button" class="chip" data-go="' + SIR.esc(key(r)) + '">' + SIR.esc(label(r)) + '</button>'; }).join(' ') + '</p>';
  };
  SIR.slug = function (s) { return 'd-' + String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''); };
  // SIR.table(id, cols, rows): a table that reads at a desktop width and
  // turns each row into a card on a phone. cols [{h, num}], rows arrays of
  // cell HTML; each cell carries its column's heading as data-label, which
  // the phone layout writes beside the value.
  // two shapes share the name: (element, [{k, label}], rows, opts) is the
  // sortable table above, and (id, [{h, num}], rows of cells) this one
  var sortable = SIR.table;
  SIR.table = function (id, cols, rows) {
    if (typeof id !== 'string' || (cols[0] && cols[0].k !== undefined)) return sortable.apply(this, arguments);
    var t = document.getElementById(id); if (!t) return;
    t.classList.add('stack');
    t.innerHTML = '<thead><tr>' + cols.map(function (c) { return '<th' + (c.num ? ' class="num"' : '') + ' scope="col">' + c.h + '</th>'; }).join('') + '</tr></thead><tbody>' +
      rows.map(function (r) {
        return '<tr>' + r.map(function (v, i) { var c = cols[i] || {}; return '<td' + (c.num ? ' class="num"' : '') + ' data-label="' + SIR.esc(String(c.h).replace(/<[^>]+>/g, '')) + '">' + (v == null ? '–' : v) + '</td>'; }).join('') + '</tr>';
      }).join('') + '</tbody>';
  };
  // the day, counted in India, so the front page's daily order changes at
  // midnight IST and every visitor sees the same one on the same day
  SIR.day = function () { return Math.floor((Date.now() + 5.5 * 36e5) / 864e5); };
  SIR.esc = function (x) { return String(x).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  // a card's figures as label and value pairs
  SIR.facts = function (pairs) {
    return '<dl class="facts">' + pairs.filter(Boolean).map(function (p) { return '<div><dt>' + p[0] + '</dt><dd>' + p[1] + '</dd></div>'; }).join('') + '</dl>';
  };

  // The FAQ tab shows every question; a page shows the ones tagged with its
  // key. Answers are written for the FAQ tab, so their relative links are
  // resolved against it wherever they appear.
  var FAQ = {};
  SIR.faq = function (site, base, loader) { FAQ[site] = { base: base, load: loader }; };
  SIR.showFaq = function (site, page) {
    try { SIR.tools(); } catch (e) {}
    var f = FAQ[site], el = document.getElementById(page ? 'pageFaq' : 'qas');
    if (!f) return Promise.resolve();
    return f.load().then(function (out) {
      // A loader returns {qa, short}: short maps a page key to its "In short"
      // points ([points, note]); the FAQ tab itself uses the key 'faq'.
      var QA = out.qa || out, sh = out.short && out.short[page || 'faq'];
      if (sh) SIR.inShort(sh[0], sh[1]);
      setTimeout(SIR.jump, 0);
      if (!el) return;
      var rows = QA.filter(function (q) { return !page || (q[2] || []).indexOf(page) >= 0; });
      el.innerHTML = rows.map(function (q) { return '<div class="qa"><h3>' + q[0] + '</h3><p>' + q[1] + '</p></div>'; }).join('') +
        (page ? '<p class="note"><a href="' + root + f.base + '">' + L('All questions and answers') + '</a></p>' : '');
      if (page) {
        var faqUrl = new URL(root + f.base, location.href);
        el.querySelectorAll('.qa a[href]').forEach(function (a) {
          var h = a.getAttribute('href');
          if (!/^(https?:|#|\/)/.test(h)) a.setAttribute('href', new URL(h, faqUrl).href);
        });
      }
    }).catch(SIR.fail);
  };
})();

// ---------------------------------------------------------------- search
// One box for the whole site, opened by the header button, Ctrl or Command
// and K, or "/". It looks through data/search.json, which build_site.py
// writes: every page, and every constituency and district a finder opens.
(function () {
  var btn = document.querySelector('.find');
  if (!btn) return;
  var kbd = btn.querySelector('.kbd');
  if (kbd && /Mac|iPhone|iPad/.test(navigator.platform || '')) kbd.textContent = '⌘ K';
  var tr = function (k) { return (L.lang !== 'en' && window.SIR_DICT && window.SIR_DICT[k]) || k; };
  var root = document.body.getAttribute('data-root') || '';
  var dlg, input, list, status, data, items = [], hits = [], cur = -1;
  function norm(x) { return String(x).toLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim(); }
  function load() {
    if (data) return Promise.resolve(data);
    return SIR.json('data/search.json').then(function (d) {
      data = d;
      var place = function (id) { return tr(d.places[id] || ''); };
      // a page's fourth field is words a reader might type for it ("check my name" for the help page)
      d.pages.forEach(function (p) { items.push({ l: tr(p[1]), m: L('Page') + ' · ' + place(p[0]), u: p[2], k: 0, h: norm(tr(p[1]) + ' ' + p[1] + ' ' + place(p[0]) + ' ' + d.places[p[0]] + ' ' + (p[3] || '')) }); });
      d.rows.forEach(function (r) {
        // the disputes page: an item, or a filter on it (a court, a party, a place or an issue)
        if (r[1] === 'x') { items.push({ l: r[2], m: L('Protests and disputes') + ' · ' + r[3], u: r[4], k: 4, h: norm(r[2] + ' ' + r[3] + ' ' + (r[5] || '')) }); return; }
        if (r[1] === 'f') { items.push({ l: r[2], m: L('Protests and disputes') + ' · ' + (r[3] === 1 ? L('One item') : L('{n} items', { n: r[3] })), u: r[4], k: 3, h: norm(r[2]) }); return; }
        var dist = r[1] === 'd', l = dist ? L('{d} district', { d: r[2] }) : r[2];
        var m = (dist ? L('District') : L('Constituency')) + ' · ' + (r[3] ? r[3] + ' · ' : '') + place(r[0]);
        items.push({ l: l, m: m, u: r[4], k: dist ? 1 : 2, h: norm(l + ' ' + r[2] + ' ' + r[3] + ' ' + place(r[0]) + ' ' + d.places[r[0]] + ' ' + (r[5] || '')) + ' ' + norm(r[2]).replace(/ /g, '') });
      });
      return d;
    });
  }
  function build() {
    dlg = document.createElement('dialog');
    dlg.className = 'search';
    dlg.setAttribute('aria-label', L('Search'));
    dlg.innerHTML = '<div class="search-in"><label for="sq" class="sr">' + L('Search') + '</label>' +
      '<input id="sq" type="search" role="combobox" aria-expanded="false" aria-controls="sres" aria-autocomplete="list" autocomplete="off" placeholder="' + SIR.esc(L('Search places, pages, constituencies and districts')) + '">' +
      '<button type="button" class="sclose">' + L('Close') + '</button></div>' +
      '<ul id="sres" role="listbox" aria-label="' + SIR.esc(L('Results')) + '"></ul><p class="sstatus" aria-live="polite"></p>';
    document.body.appendChild(dlg);
    input = dlg.querySelector('input'); list = dlg.querySelector('ul'); status = dlg.querySelector('.sstatus');
    dlg.querySelector('.sclose').onclick = function () { dlg.close(); };
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
    input.addEventListener('input', run);
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); move(e.key === 'ArrowDown' ? 1 : -1); }
      else if (e.key === 'Enter') { e.preventDefault(); go(hits[cur < 0 ? 0 : cur]); }
    });
    list.addEventListener('click', function (e) { var li = e.target.closest('li'); if (li) go(hits[+li.getAttribute('data-i')]); });
  }
  function run() {
    var q = norm(input.value), toks = q ? q.split(' ') : [];
    cur = -1;
    if (!toks.length) { hits = []; list.innerHTML = ''; status.textContent = ''; input.setAttribute('aria-expanded', 'false'); return; }
    hits = items.filter(function (it) { return toks.every(function (t) { return it.h.indexOf(t) >= 0; }); });
    var score = function (it) { var l = norm(it.l); return (l.indexOf(q) === 0 ? 0 : (' ' + l).indexOf(' ' + toks[0]) >= 0 ? 1 : 2) * 10 + it.k; };
    hits.sort(function (a, b) { return score(a) - score(b) || a.l.localeCompare(b.l); });
    var n = hits.length; hits = hits.slice(0, 20);
    // nothing matched: offer the pages that answer most questions, never a bare dead end
    if (!n) hits = ['help/', 'india/constituencies/', 'india/'].map(function (u) { return items.filter(function (it) { return it.u === u && it.k === 0; })[0]; }).filter(Boolean);
    list.innerHTML = hits.map(function (it, i) {
      return '<li role="option" id="so' + i + '" data-i="' + i + '" aria-selected="false"><span class="sl">' + SIR.esc(it.l) + '</span><span class="sm">' + SIR.esc(it.m) + '</span></li>';
    }).join('');
    input.setAttribute('aria-expanded', hits.length ? 'true' : 'false');
    status.textContent = n ? (n > 20 ? L('{n} matches, the first 20 shown', { n: n }) : n === 1 ? L('One match') : L('{n} matches', { n: n })) : L('No match');
    if (hits.length) move(1);
  }
  function move(d) {
    if (!hits.length) return;
    cur = (cur + d + hits.length) % hits.length;
    list.querySelectorAll('li').forEach(function (li, i) { li.setAttribute('aria-selected', i === cur ? 'true' : 'false'); });
    input.setAttribute('aria-activedescendant', 'so' + cur);
    var li = list.children[cur]; if (li && li.scrollIntoView) li.scrollIntoView({ block: 'nearest' });
  }
  function go(it) {
    if (!it) return;
    var u = new URL(root + it.u, location.href), lang = new URLSearchParams(location.search).get('lang');
    if (lang) u.searchParams.set('lang', lang);
    if (SIR.count) SIR.count('search', ('/' + it.u).replace(/[^a-zA-Z0-9\/_.#-]/g, '').slice(0, 120));
    dlg.close();
    if (u.pathname === location.pathname && u.hash) { location.hash = u.hash; } else { location.href = u.href; }
  }
  function open() {
    if (!dlg) build();
    if (!dlg.open) dlg.showModal();
    input.select();
    load().then(run).catch(function () { status.textContent = L('The search could not load. Reload the page and try again.'); });
  }
  btn.addEventListener('click', open);
  // Escape closes the search at once, even with text typed in the box (a
  // search field's own Escape only clears it, so it took two presses)
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && dlg && dlg.open && e.target === input && input.value) { e.preventDefault(); dlg.close(); } }, true);
  document.addEventListener('keydown', function (e) {
    var t = e.target, typing = t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName));
    if ((e.key === 'k' || e.key === 'K') && (e.metaKey || e.ctrlKey)) { e.preventDefault(); open(); }
    else if (e.key === '/' && !typing && !e.metaKey && !e.ctrlKey && !e.altKey) { e.preventDefault(); open(); }
  });
})();

// ---------------------------------------------------------------- install
// The site installs as an app (manifest.webmanifest, sw.js). The Install
// button stays hidden until the browser says it can install, which on an
// Android phone is Chrome, Edge or Samsung Internet; elsewhere the browser's
// own menu still offers "Add to Home screen".
(function () {
  var root = document.body.getAttribute('data-root') || '';
  if ('serviceWorker' in navigator && location.protocol !== 'file:') {
    window.addEventListener('load', function () { navigator.serviceWorker.register(root + 'sw.js').catch(function () {}); });
  }
  var btn = document.querySelector('.install'), ask = null;
  if (!btn) return;
  window.addEventListener('beforeinstallprompt', function (e) { e.preventDefault(); ask = e; btn.hidden = false; });
  btn.addEventListener('click', function () {
    if (!ask) return;
    ask.prompt();
    ask.userChoice.then(function () { ask = null; btn.hidden = true; });
  });
  window.addEventListener('appinstalled', function () { ask = null; btn.hidden = true; });
})();

// ---------------------------------------------------------------- counts
// Anonymous daily tallies, the same design as Democracy by Design's: one row
// per day, kind and page path, added to through one function. No cookie, no
// IP address, no device id and no search words are sent. Nothing is counted
// on a local server or a deploy preview, or when the browser asks not to be
// tracked (Do Not Track, Global Privacy Control). The table and function are
// in supabase/migrations; the key is the public anon key, which can only call
// offtheroll_track().
// The front page shows the totals: offtheroll_public_stats() returns sums
// only, never a page or a day. A card with nothing in it is left out.
(function () {
  var box = document.getElementById('tally');
  if (!box) return;
  var K = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJpdmNjcHNuenpvbHh1cWR2aGZ1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ5OTA0NDYsImV4cCI6MjEwMDU2NjQ0Nn0.-LpzZ4KUHLHNPndPwOKz6lz0TDDrW7niRmwOKz-afRo';
  fetch('https://bivccpsnzzolxuqdvhfu.supabase.co/rest/v1/rpc/offtheroll_public_stats', { method: 'POST',
    headers: { apikey: K, Authorization: 'Bearer ' + K, 'Content-Type': 'application/json' }, body: '{}' })
    .then(function (r) { return r.ok ? r.json() : null; }).then(function (t) {
      if (!t || !t.views) return;
      var cards = [[t.views, L('Page views')], [t.shares, L('Shares')], [t.downloads, L('Downloads')], [t.searches, L('Searches')]].filter(function (c) { return c[0] > 0; });
      box.querySelector('.kpis').innerHTML = cards.map(function (c) { return '<div><b>' + SIR.n(c[0]) + '</b><span>' + c[1] + '</span></div>'; }).join('');
      box.querySelector('.note').textContent = L('Counted from {d}, without cookies or anything that identifies a visitor. Visits with Do Not Track or Global Privacy Control switched on are not counted, so these are the least the site has had.', { d: SIR.date(t.since) });
      box.hidden = false;
    }).catch(function () {});
})();
(function () {
  var URL_ = 'https://bivccpsnzzolxuqdvhfu.supabase.co/rest/v1/rpc/offtheroll_track';
  var KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJpdmNjcHNuenpvbHh1cWR2aGZ1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ5OTA0NDYsImV4cCI6MjEwMDU2NjQ0Nn0.-LpzZ4KUHLHNPndPwOKz6lz0TDDrW7niRmwOKz-afRo';
  var h = location.hostname;
  if (!h || /^(localhost|127\.|0\.0\.0\.0)/.test(h) || /^deploy-preview-/.test(h)) return;
  if (navigator.globalPrivacyControl || navigator.doNotTrack === '1' || window.doNotTrack === '1') return;
  var root = document.body.getAttribute('data-root') || '';
  var base = new URL(root || './', location.href).pathname;
  var clean = function (p) { return ('/' + p).replace(/\/+/g, '/').replace(/[^a-zA-Z0-9\/_.#-]/g, '').slice(0, 120); };
  var here = function () { return clean(location.pathname.slice(base.length)); };
  function count(kind, item) {
    try {
      fetch(URL_, { method: 'POST', keepalive: true, headers: { apikey: KEY, Authorization: 'Bearer ' + KEY, 'Content-Type': 'application/json' },
        body: JSON.stringify({ p_kind: kind, p_item: item }) }).catch(function () {});
    } catch (e) { /* a count must never break the page */ }
  }
  SIR.count = count;
  count('view', here());
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a,button');
    if (!a) return;
    var href = a.getAttribute('href') || '', t = a.getAttribute('data-t');
    if (t === 'png' || t === 'csv') count('download', here());
    else if (t === 'wa' || t === 'link' || t === 'text' || /^https:\/\/wa\.me\//.test(href)) count('share', here());
    else if (a.hasAttribute('download')) count('download', clean(href.replace(/^(\.\.\/)+/, '').split('?')[0]));
  }, true);
  window.addEventListener('appinstalled', function () { count('install', '/'); });
})();

// ------------------------------------------------ header tooltips and the tour
// A short line under each header control on hover or keyboard focus, for a
// mouse or a keyboard (a touch screen has no hover, and the controls carry
// their own labels for a screen reader). Escape hides it. The tour walks a
// first-time visitor of the front page through the same controls, once: the
// choice is kept in this browser, and "Take the tour" on the front page runs it
// again. Nothing is sent anywhere.
(function () {
  var TIPS = [
    ['.controls .find', L('Search every page, constituency, district and dispute. Ctrl or Command and K opens it from anywhere.')],
    ['.fab:not(.fab-share)', L('Find any constituency with a figure on this site.')],
    ['.controls .start > summary', L('The pages most readers come for, from finding a constituency to what to do if a name was left off.')],
    ['.controls .places > summary', L('Every analysis, from All India to each state and union territory.')],
    ['.controls .dlink', L('The tables, reports and slides behind this page, and every download explained.')],
    ['.controls #lang', L('Read the site in English, Hindi, Urdu, Telugu, Tamil or Bengali.')],
    ['.controls #dys-font-btn', L('Switch to a font some readers with dyslexia find easier.')],
    ['.controls .theme', L('Switch between light and dark.')],
    ['.controls .print', L('Save this page as a PDF, with its charts.')]
  ];
  var tip = null, cur = null;
  function hide() { if (tip) tip.hidden = true; if (cur) cur.removeAttribute('aria-describedby'); cur = null; }
  function show(el, text) {
    if (window.matchMedia && !window.matchMedia('(hover: hover)').matches && !el.matches(':focus-visible')) return;
    if (el.closest('details[open]') || el.hasAttribute('aria-current')) return;
    if (!tip) { tip = document.createElement('div'); tip.className = 'htip'; tip.id = 'htip'; tip.setAttribute('role', 'tooltip'); tip.hidden = true; document.body.appendChild(tip); }
    tip.textContent = text; tip.hidden = false; cur = el; el.setAttribute('aria-describedby', 'htip');
    var r = el.getBoundingClientRect(), w = tip.offsetWidth;
    tip.style.top = (r.bottom + 8) + 'px';
    tip.style.left = Math.max(8, Math.min(window.innerWidth - w - 8, r.left + r.width / 2 - w / 2)) + 'px';
  }
  function wire() {
    TIPS.forEach(function (t) {
      var el = document.querySelector(t[0]);
      if (!el || el.__tip) return;
      el.__tip = 1;
      el.addEventListener('mouseenter', function () { show(el, t[1]); });
      el.addEventListener('mouseleave', hide);
      el.addEventListener('focus', function () { show(el, t[1]); });
      el.addEventListener('blur', hide);
      el.addEventListener('click', hide);
    });
  }
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { hide(); if (SIR.tourStop) SIR.tourStop(); } });
  window.addEventListener('scroll', hide, { passive: true });
  // the language menu and the reading-font button are added by other scripts
  wire(); setTimeout(wire, 600); window.addEventListener('load', wire);

  // the floating buttons stay out of the way while a page's own row of
  // buttons is on the screen or still below it (the front page's hero), and
  // come in once the reader has scrolled past the whole row
  (function () {
    var fabs = document.querySelector('.fabs'), own = document.querySelector('main .btn-ink[href*="constituencies"]');
    own = own && (own.closest('.btns') || own);
    if (!fabs || !own || !('IntersectionObserver' in window)) return;
    fabs.classList.add('fabs-off');
    new IntersectionObserver(function (e) {
      fabs.classList.toggle('fabs-off', e[0].isIntersecting || e[0].boundingClientRect.top > 0);
    }, { rootMargin: '0px 0px -96px 0px' }).observe(own);
  })();

  // The floating buttons must never sit on what the reader is reading. On a
  // phone they hide while the page scrolls down and come back on the way up,
  // and they stay away while a finder or its result card is on the screen.
  // A page with its own finder points "Find your constituency" at it, so the
  // button no longer takes the reader away to the All India finder.
  (function () {
    var fabs = document.querySelector('.fabs'); if (!fabs) return;
    var own = document.querySelector('main .finder, main #finder'), fab = fabs.querySelector('.fab:not(.fab-share)');
    if (own && fab) {
      if (!own.id) own.id = 'finder';
      fab.setAttribute('href', '#' + own.id);
      fab.addEventListener('click', function (e) { e.preventDefault(); own.scrollIntoView({ behavior: 'smooth', block: 'start' });
        var inp = own.querySelector('input'); if (inp) setTimeout(function () { inp.focus({ preventScroll: true }); }, 400); });
    }
    var last = scrollY, busy = false, near = false;
    if (own && 'IntersectionObserver' in window) new IntersectionObserver(function (e) { near = e[0].isIntersecting; fabs.classList.toggle('fabs-hide', near); }).observe(own);
    addEventListener('scroll', function () {
      if (busy) return; busy = true;
      requestAnimationFrame(function () {
        var y = scrollY, down = y > last + 4, up = y < last - 4;
        if (innerWidth < 700 && !near) { if (down && y > 120) fabs.classList.add('fabs-hide'); else if (up) fabs.classList.remove('fabs-hide'); }
        last = y; busy = false;
      });
    }, { passive: true });
  })();

  // the tour, on the front page
  var STEPS = [
    ['.controls .find', L('Search finds any page, constituency, district or dispute. Press Ctrl or Command and K from anywhere on the site.')],
    ['main .btn-ink[href*="constituencies"]', L('Constituencies opens a finder over every constituency with a figure on this site, each in its own state\'s measure.')],
    ['.controls .start > summary', L('Start here lists the pages most readers come for, from finding a constituency to what to do if a name was left off.')],
    ['.controls .places > summary', L('Places lists every analysis, from All India to each state and union territory.')],
    ['#vIndia', L('The map shows the names left off per 100 electors in each state. Tap a state to open its own page.')],
    ['.hubs .hub.pin', L('The pinned cards lead to the pages most readers look for, among them the disputes, every constituency and women.')],
    ['.controls .dlink', L('Every table behind the site can be downloaded, with what each column means.')],
    ['.controls #lang', L('The site reads in English, Hindi, Urdu, Telugu, Tamil and Bengali.')]
  ];
  var KEY = 'otr-tour', box = null, on = null, i = 0, head = document.querySelector('header.top');
  var seen = function () { try { return localStorage.getItem(KEY); } catch (e) { return '1'; } };
  var mark = function () { try { localStorage.setItem(KEY, '1'); } catch (e) {} };
  function stop() {
    if (on) on.classList.remove('tour-on');
    if (box) box.remove();
    box = on = null;
    if (head && head.__tourOpened) { head.classList.remove('open'); head.__tourOpened = 0; }
    mark();
  }
  SIR.tourStop = function () { if (box) stop(); };
  function step(n) {
    var steps = STEPS.filter(function (s) { return document.querySelector(s[0]); });
    if (n < 0 || n >= steps.length) { stop(); return; }
    i = n;
    var s = steps[n], el = document.querySelector(s[0]);
    // on a phone the header's controls sit behind the menu button
    // (a control can be hidden by its own box or by the menu around it, so
    // the test is whether it has any box on screen at all)
    if (head && el.closest('header.top') && !head.classList.contains('open') && !el.getClientRects().length) { head.classList.add('open'); head.__tourOpened = 1; }
    if (on) on.classList.remove('tour-on');
    on = el; el.classList.add('tour-on');
    // on a phone the tour's box sits at the foot of the screen, so a target
    // further down the page is brought to the top, above the box
    if (innerWidth < 700 && !el.closest('header.top')) window.scrollTo({ top: el.getBoundingClientRect().top + scrollY - 12, behavior: 'smooth' });
    else el.scrollIntoView({ block: 'center', behavior: 'smooth' });
    box.querySelector('.tour-t').textContent = s[1];
    box.querySelector('.tour-n').textContent = L('{a} of {b}', { a: n + 1, b: steps.length });
    box.querySelector('.tour-back').disabled = n === 0;
    box.querySelector('.tour-next').textContent = n === steps.length - 1 ? L('Done') : L('Next');
    box.querySelector('.tour-next').focus();
  }
  function start() {
    hide();
    if (box) stop();
    box = document.createElement('div');
    box.className = 'tour'; box.setAttribute('role', 'dialog'); box.setAttribute('aria-label', L('A tour of the site'));
    box.innerHTML = '<p class="tour-n"></p><p class="tour-t" aria-live="polite"></p><div class="tour-b">' +
      '<button type="button" class="tour-back">' + L('Back') + '</button><button type="button" class="tour-next btn-ink"></button>' +
      '<button type="button" class="tour-x">' + L('Close the tour') + '</button></div>';
    document.body.appendChild(box);
    box.querySelector('.tour-back').onclick = function () { step(i - 1); };
    box.querySelector('.tour-next').onclick = function () { step(i + 1); };
    box.querySelector('.tour-x').onclick = stop;
    step(0);
  }
  SIR.tour = start;
  var front = document.querySelector('.hubs') && document.getElementById('vIndia');
  document.addEventListener('click', function (e) { var b = e.target.closest('.take-tour'); if (b) { e.preventDefault(); start(); } });
  // a first visit to the front page is offered the tour once
  if (front && !seen()) {
    var ask = document.createElement('div');
    ask.className = 'tour tour-ask'; ask.setAttribute('role', 'dialog'); ask.setAttribute('aria-label', L('A tour of the site'));
    ask.innerHTML = '<p class="tour-t">' + L('New here? A one-minute tour shows where everything is.') + '</p><div class="tour-b">' +
      '<button type="button" class="tour-go btn-ink">' + L('Take the tour') + '</button><button type="button" class="tour-no">' + L('No, thanks') + '</button></div>';
    setTimeout(function () {
      if (seen()) return;
      document.body.appendChild(ask);
      ask.querySelector('.tour-go').onclick = function () { ask.remove(); start(); };
      ask.querySelector('.tour-no').onclick = function () { ask.remove(); mark(); };
      // the offer does not follow the reader down the page: the first real
      // scroll takes it away, as a no thanks, and Take the tour stays in the hero
      var y0 = scrollY, gone = function () { if (Math.abs(scrollY - y0) > 160 && ask.parentNode) { ask.remove(); mark(); removeEventListener('scroll', gone); } };
      addEventListener('scroll', gone, { passive: true });
    }, 1500);
  }
})();
