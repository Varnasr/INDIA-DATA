/* The tabbed dashboards (Bihar at /, Hyderabad at /hyderabad/). Builds the
   summary cards, banners and chart cards, draws a tab's charts when it is
   first opened, and handles PNG export, printing, theme and resize.
   Loads after sir.js, which owns the theme button and SIR.isDark(). */
(function () {
  'use strict';
  var nf = new Intl.NumberFormat('en-IN');
  var D = window.DASH = {};
  D.n = function (x) { return x == null || isNaN(x) ? '–' : nf.format(Math.round(x)); };
  D.d = function (x, k) { return x == null || isNaN(x) ? '–' : Number(x).toFixed(k == null ? 1 : k); };
  D.pct = function (x, k) { return D.d(x, k) + '%'; };
  D.lakh = function (x) { return SIR.lakh(x); };
  D.esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  D.sum = function (a, f) { return a.reduce(function (s, x) { return s + (typeof f === 'function' ? f(x) : x[f]); }, 0); };
  D.mean = function (a) { return a.length ? D.sum(a, function (x) { return x; }) / a.length : NaN; };
  D.median = function (a) { var s = a.slice().sort(function (x, y) { return x - y; }), m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };
  function corr(x, y) { var mx = D.mean(x), my = D.mean(y), sxy = 0, sx = 0, sy = 0; x.forEach(function (v, i) { sxy += (v - mx) * (y[i] - my); sx += (v - mx) * (v - mx); sy += (y[i] - my) * (y[i] - my); }); return sxy / Math.sqrt(sx * sy); }
  function rank(a) { var o = a.map(function (v, i) { return [v, i]; }).sort(function (p, q) { return p[0] - q[0]; }), r = new Array(a.length); for (var i = 0; i < o.length;) { var j = i; while (j + 1 < o.length && o[j + 1][0] === o[i][0]) j++; for (var k = i; k <= j; k++) r[o[k][1]] = (i + j) / 2 + 1; i = j + 1; } return r; }
  D.rho = function (x, y) { return corr(rank(x), rank(y)); };
  D.groupBy = function (a, k) { var o = {}; a.forEach(function (r) { var g = typeof k === 'function' ? k(r) : r[k]; (o[g] = o[g] || []).push(r); }); return o; };
  D.tag = function (al) { return al ? '<span class="tag ' + al + '">' + al + '</span>' : '–'; };
  D.C = { red: '#C0392B', orange: '#E67E22', green: '#27AE60', dblue: '#1F618D', purple: '#8E44AD', yellow: '#D4AC0D', teal: '#17A589', grey: '#95A5A6', pink: '#AF3B6E', nda: '#E67E22', india: '#1E8449', other: '#8E7CC3', maroon: '#8B1E3F', gold: '#E0A526', ikat: '#0E5E6F' };
  D.AL = { NDA: D.C.nda, INDIA: D.C.india, Other: D.C.other };
  var ICON = D.ICON = '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 2v10"/><circle cx="12" cy="17" r="4"/></svg>';

  // ---------------------------------------------------------------- markup
  D.kpis = function (list) { var cls = ['', 'y', 'b', 'g', 'o', 'p']; return '<div class="summary-grid">' + list.map(function (k, i) { return '<div class="summary-card ' + cls[i % 6] + '"><div class="summary-value">' + k[0] + '</div><div class="summary-label">' + k[1] + '</div></div>'; }).join('') + '</div>'; };
  // Each tab opens with one plain paragraph; the tab name is its heading.
  D.banner = function (title, text) { return '<p class="tab-lead">' + text + '</p>'; };
  D.card = function (num, id, title, insight, opts) {
    opts = opts || {};
    return '<div class="card' + (opts.wide ? ' wide' : '') + '"><div class="card-title"><span>' + num + '. ' + title + '</span><div class="card-actions"><button type="button" data-png="' + id + '" aria-label="' + L('Download this chart as PNG') + '">PNG</button></div></div>' +
      '<div class="chart-container ' + (opts.size || '') + '"><canvas id="' + id + '" role="img" aria-label="' + D.esc(title) + '"></canvas></div>' +
      '<div class="chart-takeaway">' + ICON + ' <strong>' + L('Key insight:') + '</strong> ' + insight + '</div></div>';
  };
  D.section = function (id, html) { return '<section class="tab-content" id="tab-' + id + '" role="tabpanel" aria-labelledby="tabbtn-' + id + '">' + html + '</section>'; };
  D.grid = function (html) { return '<div class="charts-grid">' + html + '</div>'; };
  D.qa = function (list) { return list.map(function (q) { return '<div class="research-section"><div class="research-q">' + q[0] + '</div><div class="research-a">' + q[1] + '</div></div>'; }).join(''); };

  // ---------------------------------------------------------------- charts
  D.barOpts = function (x, y, extra) { return Object.assign({ plugins: { legend: { display: false } }, scales: { x: { title: { display: !!x, text: x } }, y: { beginAtZero: true, title: { display: !!y, text: y } } } }, extra || {}); };
  D.hbar = function (labels, data, colors, xt) { return { type: 'bar', data: { labels: labels, datasets: [{ label: xt, data: data, backgroundColor: colors }] }, options: { indexAxis: 'y', plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true, title: { display: true, text: xt } } } } }; };
  D.scatter = function (pts, xt, yt, color, labelFn) { return { type: 'scatter', data: { datasets: [{ label: yt, data: pts, backgroundColor: color, pointRadius: 3.5 }] }, options: { plugins: { legend: { display: false }, tooltip: { callbacks: { label: labelFn } } }, scales: { x: { title: { display: true, text: xt } }, y: { title: { display: true, text: yt } } } } }; };
  var charts = {}, specs = {};
  D.chart = function (id, cfg) { specs[id] = cfg; };
  function draw(id) {
    var el = document.getElementById(id); if (!el || !specs[id]) return;
    // a ranked list or measures side by side are drawn in SVG (assets/viz.js)
    if (window.SIR && SIR.viz) { var v = SIR.viz(id, specs[id]); if (v) { charts[id] = v; return; } }
    if (typeof Chart === 'undefined') return;
    if (charts[id]) charts[id].destroy();
    var dark = window.SIR && SIR.isDark();
    Chart.defaults.color = dark ? '#D5DBE1' : '#34495E';
    Chart.defaults.borderColor = dark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.08)';
    Chart.defaults.font.family = "'Segoe UI', system-ui, sans-serif";
    Chart.defaults.font.size = window.innerWidth < 600 ? 11 : 12;
    Chart.defaults.maintainAspectRatio = false;
    if (Chart.defaults.plugins.colors) Chart.defaults.plugins.colors.enabled = false;
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) Chart.defaults.animation = false;
    // A fresh copy each draw: Chart.js mutates the config it is given.
    // Functions (tick and tooltip callbacks) are carried across by reference.
    var cfg = (function clone(v) { if (Array.isArray(v)) return v.map(clone); if (v && typeof v === 'object') { var o = {}; Object.keys(v).forEach(function (k) { o[k] = clone(v[k]); }); return o; } return v; })(specs[id]);
    cfg.options = cfg.options || {};
    if (cfg.options.indexAxis === 'y') { cfg.options.scales = cfg.options.scales || {}; cfg.options.scales.y = cfg.options.scales.y || {}; cfg.options.scales.y.ticks = Object.assign({ autoSkip: false }, cfg.options.scales.y.ticks || {}); }
    if (window.innerWidth < 600) { cfg.options.plugins = cfg.options.plugins || {}; cfg.options.plugins.legend = Object.assign({}, cfg.options.plugins.legend || {}); cfg.options.plugins.legend.labels = { boxWidth: 10, boxHeight: 10, padding: 6 }; if (window.SIR && SIR.fitPhone) SIR.fitPhone(cfg); }
    if (window.SIR && SIR.polish) SIR.polish(cfg);
    charts[id] = new Chart(el, cfg);
  }

  // ------------------------------------------------------------ tabs, etc.
  D.start = function (main, prefix) {
    var tabs = document.querySelectorAll('.nav-tab[data-tab]'), drawn = {};
    function drawTab(tab) { document.querySelectorAll('#tab-' + tab + ' canvas').forEach(function (c) { draw(c.id); }); }
    function show(tab, push) {
      tabs.forEach(function (b) { var on = b.getAttribute('data-tab') === tab; b.setAttribute('aria-selected', on ? 'true' : 'false'); b.id = 'tabbtn-' + b.getAttribute('data-tab'); b.tabIndex = on ? 0 : -1; });
      document.querySelectorAll('.tab-content').forEach(function (s) { s.classList.toggle('active', s.id === 'tab-' + tab); });
      if (!drawn[tab]) { drawTab(tab); drawn[tab] = true; }
      if (push) {
        history.replaceState(null, '', '#' + tab);
        // A tab opened from far down the page starts at its own top, just
        // under the sticky tab bar, rather than halfway through.
        var sb = document.querySelector('.secbar'), bar = sb && sb.offsetHeight ? sb : document.querySelector('.nav-tabs'), m = document.getElementById('content') || document.querySelector('main');
        var top = m.getBoundingClientRect().top + window.scrollY - bar.offsetHeight - (parseFloat(getComputedStyle(bar).top) || 0);
        if (window.scrollY > top) window.scrollTo(0, top);
      }
      if (SIR.tabIntoView) SIR.tabIntoView(document.querySelector('.nav-tab[data-tab="' + tab + '"]'));
    }
    tabs.forEach(function (b, i) {
      b.addEventListener('click', function () { show(b.getAttribute('data-tab'), true); });
      b.addEventListener('keydown', function (e) { var j = e.key === 'ArrowRight' ? i + 1 : e.key === 'ArrowLeft' ? i - 1 : null; if (j == null) return; var nb = tabs[(j + tabs.length) % tabs.length]; nb.focus(); nb.click(); });
    });
    var first = tabs[0].getAttribute('data-tab'), start = (location.hash || '#' + first).slice(1);
    show(document.getElementById('tab-' + start) ? start : first);
    document.addEventListener('sir-theme', function () { Object.keys(charts).forEach(draw); });
    main.addEventListener('click', function (e) {
      var b = e.target.closest('[data-png]'); if (!b || !charts[b.getAttribute('data-png')]) return;
      if (charts[b.getAttribute('data-png')].viz) { VIZ.png(charts[b.getAttribute('data-png')].box, prefix + '-' + b.getAttribute('data-png')); return; }
      var a = document.createElement('a'); a.href = charts[b.getAttribute('data-png')].toBase64Image('image/png', 1); a.download = prefix + '-' + b.getAttribute('data-png') + '.png'; a.click();
    });
    if (window.SIR) SIR.beforePrint = function () {
      document.querySelectorAll('.tab-content').forEach(function (s) { s.classList.add('active'); });
      Object.keys(specs).forEach(function (id) { if (!charts[id]) draw(id); });
      window.addEventListener('afterprint', function () { show(document.querySelector('.nav-tab[aria-selected="true"]').getAttribute('data-tab')); }, { once: true });
    };
    var rt; window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(function () { Object.keys(charts).forEach(draw); }, 250); });
  };
})();
