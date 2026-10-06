/* Shared helpers for the SIR pages. No framework; Chart.js is loaded by each
   page from cdnjs. Every page sets data-root on <body> ("../" or "../../") so
   the JSON under data/ resolves on Netlify and in a local server alike. */
(function () {
  'use strict';
  // No i18n.js on the page: every string stays as written.
  if (!window.L) { window.L = function (k, v) { return v ? k.replace(/\{(\w+)\}/g, function (m, x) { return v[x] != null ? v[x] : m; }) : k; }; window.L.apply = function () {}; window.L.lang = 'en'; }
  L.apply(document.body);
  var root = document.body.getAttribute('data-root') || '';
  var nf = new Intl.NumberFormat('en-IN');

  var SIR = window.SIR = {
    root: root,
    n: function (x) { return x == null || isNaN(x) ? '–' : nf.format(Math.round(x)); },
    d: function (x, k) { return x == null || isNaN(x) ? '–' : Number(x).toFixed(k == null ? 1 : k); },
    pct: function (x, k) { return x == null || isNaN(x) ? '–' : Number(x).toFixed(k == null ? 1 : k) + '%'; },
    date: function (iso) { if (!iso) return ''; var p = iso.split('-'); return +p[2] + ' ' + ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][+p[1] - 1] + ' ' + p[0]; },
    lakh: function (x) { return L('{x} lakh', { x: (x / 1e5).toFixed(1) }); },
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
  var ICONS = {"i0": "<path d=\"M3 3v18h18\"/><path d=\"M18 17V9\"/><path d=\"M13 17V5\"/><path d=\"M8 17v-3\"/>", "i1": "<polyline points=\"23 6 13.5 15.5 8.5 10.5 1 18\"/><polyline points=\"17 6 23 6 23 12\"/>", "i2": "<circle cx=\"12\" cy=\"12\" r=\"10\"/><path d=\"M12 6v6l4 2\"/>", "i3": "<path d=\"M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2\"/><circle cx=\"9\" cy=\"7\" r=\"4\"/><path d=\"M23 21v-2a4 4 0 0 0-3-3.87\"/><path d=\"M16 3.13a4 4 0 0 1 0 7.75\"/>", "i4": "<polygon points=\"12 2 2 7 12 12 22 7 12 2\"/><polyline points=\"2 17 12 22 22 17\"/><polyline points=\"2 12 12 17 22 12\"/>", "i5": "<path d=\"M12 2L2 8v2h20V8L12 2z\"/><path d=\"M4 10v10h16V10\"/><path d=\"M10 20v-6h4v6\"/>", "i6": "<path d=\"M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z\"/><line x1=\"4\" y1=\"22\" x2=\"4\" y2=\"15\"/>", "i7": "<path d=\"M1 6v16l7-4 8 4 7-4V2l-7 4-8-4-7 4z\"/><path d=\"M8 2v16\"/><path d=\"M16 6v16\"/>", "i8": "<path d=\"M6 3h12\"/><path d=\"M6 8h12\"/><path d=\"M6 13l6 8\"/><path d=\"M18 13c-3 0-6-3-6-8\"/>", "i9": "<circle cx=\"11\" cy=\"11\" r=\"8\"/><path d=\"M21 21l-4.35-4.35\"/>", "i10": "<path d=\"M4 19.5A2.5 2.5 0 0 1 6.5 17H20\"/><path d=\"M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z\"/>", "i11": "<rect x=\"3\" y=\"3\" width=\"7\" height=\"7\"/><rect x=\"14\" y=\"3\" width=\"7\" height=\"7\"/><rect x=\"3\" y=\"14\" width=\"7\" height=\"7\"/><rect x=\"14\" y=\"14\" width=\"7\" height=\"7\"/>", "i12": "<circle cx=\"12\" cy=\"12\" r=\"10\"/><path d=\"M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3\"/><line x1=\"12\" y1=\"17\" x2=\"12.01\" y2=\"17\"/>", "i13": "<path d=\"M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z\"/><polyline points=\"14 2 14 8 20 8\"/><line x1=\"8\" y1=\"13\" x2=\"16\" y2=\"13\"/><line x1=\"8\" y1=\"17\" x2=\"13\" y2=\"17\"/>", "i14": "<path d=\"M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71\"/><path d=\"M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71\"/>", "i15": "<path d=\"M14 13l-7.5 7.5a2.1 2.1 0 0 1-3-3L11 10\"/><path d=\"M16 16l6-6\"/><path d=\"M8 8l6-6\"/><path d=\"M9 7l8 8\"/>", "i16": "<path d=\"M9 11l3 3L22 4\"/><path d=\"M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11\"/>"};
  var SITES = /*sites*/{"india": {"tabs": [], "dash": "", "pages": [["india/", "All India", "i0"], ["india/numbers/", "In numbers", "i11"], ["india/process/", "How it was run", "i15"], ["india/progress/", "Where it stands", "i15"], ["india/method/", "Sources and method", "i10"], ["india/faq/", "FAQ", "i12"], ["india/report/", "Full report", "i13"]]}, "bihar": {"tabs": [["overview", "Overview", "i0"], ["deletions", "Deletions", "i1"], ["reasons", "Reasons", "i16"], ["phases", "Phases", "i2"], ["gender", "Gender", "i3"], ["caste", "Caste", "i4"], ["religion", "Religion", "i5"], ["electoral", "Electoral", "i6"], ["geographic", "Geographic", "i7"], ["economic", "Economic", "i8"], ["research", "Research", "i9"], ["methodology", "Methods", "i10"]], "dash": "bihar/", "pages": [["bihar/explorer/", "Booth explorer", "i9"], ["bihar/results/", "Elections", "i6"], ["bihar/people/", "Women, religion, caste", "i3"], ["bihar/border/", "Border", "i7"], ["bihar/districts/", "Districts", "i11"], ["bihar/faq/", "FAQ", "i12"], ["bihar/method/", "Method", "i10"], ["bihar/report/", "Full report", "i13"]]}, "hyd": {"tabs": [["overview", "Overview", "i0"], ["deletions", "Deletions", "i1"], ["age", "Age and sex", "i3"], ["religion", "Religion", "i5"], ["link", "2002 link", "i14"], ["hearings", "Hearings", "i15"], ["parts", "Polling parts", "i11"], ["electoral", "Electoral", "i6"], ["research", "Research", "i9"], ["methodology", "Methods", "i10"]], "dash": "hyderabad/", "pages": [["hyderabad/explorer/", "Part explorer", "i9"], ["hyderabad/people/", "Age, sex, religion, 2002", "i3"], ["hyderabad/parts/", "Polling parts", "i11"], ["hyderabad/hearings/", "Hearings", "i15"], ["hyderabad/telangana/", "Hyderabad and Telangana", "i7"], ["hyderabad/faq/", "FAQ", "i12"], ["hyderabad/method/", "Method", "i10"], ["hyderabad/report/", "Full report", "i13"]]}, "tn": {"tabs": [], "dash": "", "pages": [["tamilnadu/", "Overview", "i0"], ["tamilnadu/elections/", "Elections", "i6"], ["tamilnadu/faq/", "FAQ", "i12"], ["tamilnadu/method/", "Method", "i10"]]}, "ka": {"tabs": [], "dash": "", "pages": [["karnataka/", "Overview", "i0"], ["karnataka/faq/", "FAQ", "i12"], ["karnataka/method/", "Method", "i10"]]}, "wb": {"tabs": [], "dash": "", "pages": [["westbengal/", "Overview", "i0"], ["westbengal/elections/", "Elections", "i6"], ["westbengal/faq/", "FAQ", "i12"], ["westbengal/method/", "Method", "i10"]]}, "kl": {"tabs": [], "dash": "", "pages": [["kerala/", "Overview", "i0"], ["kerala/elections/", "Elections", "i6"], ["kerala/faq/", "FAQ", "i12"], ["kerala/method/", "Method", "i10"]]}, "rj": {"tabs": [], "dash": "", "pages": [["rajasthan/", "Overview", "i0"], ["rajasthan/faq/", "FAQ", "i12"], ["rajasthan/method/", "Method", "i10"]]}, "up": {"tabs": [], "dash": "", "pages": [["uttarpradesh/", "Overview", "i0"], ["uttarpradesh/faq/", "FAQ", "i12"], ["uttarpradesh/method/", "Method", "i10"]]}, "dl": {"tabs": [], "dash": "", "pages": [["delhi/", "Overview", "i0"], ["delhi/faq/", "FAQ", "i12"], ["delhi/method/", "Method", "i10"]]}, "mh": {"tabs": [], "dash": "", "pages": [["maharashtra/", "Overview", "i0"], ["maharashtra/faq/", "FAQ", "i12"], ["maharashtra/method/", "Method", "i10"]]}, "gj": {"tabs": [], "dash": "", "pages": [["gujarat/", "Overview", "i0"], ["gujarat/elections/", "Elections", "i6"], ["gujarat/faq/", "FAQ", "i12"], ["gujarat/method/", "Method", "i10"]]}}/*sites*/;
  if (nav) (function () {
    // SITES is written from site/places.json by scripts/build_site.py.
    var body = document.body, site = body.getAttribute('data-place'), map = SITES[site];
    if (!map) return;
    var root = body.getAttribute('data-root') || '', dash = root + map.dash;
    var tabs = [].slice.call(nav.querySelectorAll('.nav-tab[data-tab]')), onDash = tabs.length > 0;
    function tr(k) { return (L.lang !== 'en' && window.SIR_DICT && window.SIR_DICT[k]) || k; }
    function ico(n) { return '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">' + ICONS[n] + '</svg>'; }
    var here = location.pathname.replace(/index\.html$/, '');
    function path(h) { return new URL(h, location.href).pathname.replace(/index\.html$/, ''); }
    // Each entry: label, icon, and either a tab to click or an address.
    var A = map.tabs.map(function (t) { return { key: t[0], label: tr(t[1]), icon: t[2], tab: onDash ? nav.querySelector('[data-tab="' + t[0] + '"]') : null, href: onDash ? null : dash + '#' + t[0] }; });
    var B = map.pages.map(function (p) { return { label: tr(p[1]), icon: p[2], href: root + p[0] }; });
    var seq = onDash ? A : B;
    if (seq.length < 2) return;
    var cur = document.querySelector('header.top .places [aria-current]');
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

  // The downloads menu closes on a click elsewhere and on Escape.
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
    var out = [], cur = '';
    s.split(' ').forEach(function (w) {
      if (cur && (cur + ' ' + w).length > n) { out.push(cur); cur = w; } else cur = cur ? cur + ' ' + w : w;
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
          return Math.abs(v) >= 1e5 ? L('{x} lakh', { x: String(+(v / 1e5).toFixed(1)) }) : Chart.Ticks.formatters.numeric.call(this, v, i, ts);
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
          return '<td class="' + (c.left ? 'l' : '') + '">' + v + '</td>';
        }).join('') + '</tr>';
      }).join('') + '</tbody>';
      el.innerHTML = h;
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
    if (m) m.insertAdjacentHTML('afterbegin', '<p class="caveat">' + L('The data for this page did not load ({msg}). If you opened the file directly, serve the folder with <code>python3 -m http.server</code> and open it from there.', { msg: SIR.esc(e.message) }) + '</p>');
  };

  // ---- "In short" box: numbered plain sentences at the top of a page.
  SIR.inShort = function (points, note) {
    var ol = document.getElementById('short');
    if (ol) ol.innerHTML = points.filter(Boolean).map(function (t) { return '<li>' + t + '</li>'; }).join('');
    var n = document.getElementById('shortNote');
    if (n) { n.innerHTML = note || ''; n.hidden = !note; }
  };

  // ---- Questions and answers. Each analysis registers one loader
  // (assets/faq/<site>.js) returning [[question, answer, [page keys]], ...].
  // ---- sharing. WhatsApp opens with the text already written; on a phone
  // that is the app, on a computer WhatsApp Web.
  SIR.pageUrl = function (hash) { return location.origin + location.pathname + (hash ? '#' + hash : ''); };
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
      if (h.id === 'faqH' || h.querySelector('.anchor') || h.closest('.card, .qa, .tab-content, nav')) return;
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
  var moved = false;
  ['wheel', 'touchstart', 'keydown'].forEach(function (ev) { addEventListener(ev, function () { moved = true; }, { once: true, passive: true }); });
  SIR.jump = function () {
    if (moved || !location.hash) return;
    var t = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (t && t.closest('main')) t.scrollIntoView({ block: 'start' });
  };
  setTimeout(function () { SIR.anchors(); SIR.jump(); }, 0);

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
        '<div class="tools"><a class="btn" target="_blank" rel="noopener" href="' + SIR.wa(st.share(r), k) + '">' + L('Share on WhatsApp') + '</a>' +
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
    function fromHash(scroll) { var h = decodeURIComponent(location.hash.slice(1)); if (item[h]) select(item[h], scroll); }
    fromHash(true);
    window.addEventListener('hashchange', function () { fromHash(true); });
    return { select: function (r) { var it = items.filter(function (x) { return x.r === r; })[0]; select(it, false); }, byKey: byKey, item: item };
  };
  // buttons for a list of rows, each opening that row's card
  SIR.goList = function (rows, key, label) {
    return '<p class="golist">' + rows.map(function (r) { return '<button type="button" class="chip" data-go="' + SIR.esc(key(r)) + '">' + SIR.esc(label(r)) + '</button>'; }).join(' ') + '</p>';
  };
  SIR.slug = function (s) { return 'd-' + String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''); };
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
      d.pages.forEach(function (p) { items.push({ l: tr(p[1]), m: L('Page') + ' · ' + place(p[0]), u: p[2], k: 0, h: norm(tr(p[1]) + ' ' + p[1] + ' ' + place(p[0]) + ' ' + d.places[p[0]]) }); });
      d.rows.forEach(function (r) {
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
    list.innerHTML = hits.map(function (it, i) {
      return '<li role="option" id="so' + i + '" data-i="' + i + '" aria-selected="false"><span class="sl">' + SIR.esc(it.l) + '</span><span class="sm">' + SIR.esc(it.m) + '</span></li>';
    }).join('');
    input.setAttribute('aria-expanded', n ? 'true' : 'false');
    status.textContent = n ? (n > 20 ? L('{n} matches, the first 20 shown', { n: n }) : n === 1 ? L('One match') : L('{n} matches', { n: n })) : L('No match');
    if (n) move(1);
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
