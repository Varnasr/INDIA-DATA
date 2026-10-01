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
    lakh: function (x) { return L('{x} lakh', { x: (x / 1e5).toFixed(1) }); },
    esc: function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); },
    json: function (path) {
      var v = (window.SIR_V || {})[path];
      return fetch(root + path + (v ? '?v=' + v : '')).then(function (r) {
        if (!r.ok) throw new Error(path + ' answered ' + r.status);
        return r.json();
      });
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
  var SITES = /*sites*/{"india": {"tabs": [], "dash": "", "pages": [["india/", "All India", "i0"], ["india/method/", "Sources and method", "i10"], ["india/faq/", "FAQ", "i12"], ["india/report/", "Full report", "i13"]]}, "bihar": {"tabs": [["overview", "Overview", "i0"], ["deletions", "Deletions", "i1"], ["reasons", "Reasons", "i16"], ["phases", "Phases", "i2"], ["gender", "Gender", "i3"], ["caste", "Caste", "i4"], ["religion", "Religion", "i5"], ["electoral", "Electoral", "i6"], ["geographic", "Geographic", "i7"], ["economic", "Economic", "i8"], ["research", "Research", "i9"], ["methodology", "Methods", "i10"]], "dash": "bihar/", "pages": [["bihar/explorer/", "Booth explorer", "i9"], ["bihar/results/", "Elections", "i6"], ["bihar/people/", "Women, religion, caste", "i3"], ["bihar/border/", "Border", "i7"], ["bihar/districts/", "Districts", "i11"], ["bihar/faq/", "FAQ", "i12"], ["bihar/method/", "Method", "i10"], ["bihar/report/", "Full report", "i13"]]}, "hyd": {"tabs": [["overview", "Overview", "i0"], ["deletions", "Deletions", "i1"], ["age", "Age and sex", "i3"], ["religion", "Religion", "i5"], ["link", "2002 link", "i14"], ["hearings", "Hearings", "i15"], ["parts", "Polling parts", "i11"], ["electoral", "Electoral", "i6"], ["research", "Research", "i9"], ["methodology", "Methods", "i10"]], "dash": "hyderabad/", "pages": [["hyderabad/explorer/", "Part explorer", "i9"], ["hyderabad/people/", "Age, sex, religion, 2002", "i3"], ["hyderabad/parts/", "Polling parts", "i11"], ["hyderabad/hearings/", "Hearings", "i15"], ["hyderabad/telangana/", "Hyderabad and Telangana", "i7"], ["hyderabad/faq/", "FAQ", "i12"], ["hyderabad/method/", "Method", "i10"], ["hyderabad/report/", "Full report", "i13"]]}, "tn": {"tabs": [], "dash": "", "pages": [["tamilnadu/", "Overview", "i0"], ["tamilnadu/elections/", "Elections", "i6"], ["tamilnadu/faq/", "FAQ", "i12"], ["tamilnadu/method/", "Method", "i10"]]}}/*sites*/;
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
  SIR.chart = function (id, cfg) {
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
  // The FAQ tab shows every question; a page shows the ones tagged with its
  // key. Answers are written for the FAQ tab, so their relative links are
  // resolved against it wherever they appear.
  var FAQ = {};
  SIR.faq = function (site, base, loader) { FAQ[site] = { base: base, load: loader }; };
  SIR.showFaq = function (site, page) {
    var f = FAQ[site], el = document.getElementById(page ? 'pageFaq' : 'qas');
    if (!f) return Promise.resolve();
    return f.load().then(function (out) {
      // A loader returns {qa, short}: short maps a page key to its "In short"
      // points ([points, note]); the FAQ tab itself uses the key 'faq'.
      var QA = out.qa || out, sh = out.short && out.short[page || 'faq'];
      if (sh) SIR.inShort(sh[0], sh[1]);
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
