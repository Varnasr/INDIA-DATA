/* Shared helpers for the SIR pages. No framework; Chart.js is loaded by each
   page from cdnjs. Every page sets data-root on <body> ("../" or "../../") so
   the JSON under data/ resolves on Netlify and in a local server alike. */
(function () {
  'use strict';
  var root = document.body.getAttribute('data-root') || '';
  var nf = new Intl.NumberFormat('en-IN');

  var SIR = window.SIR = {
    root: root,
    n: function (x) { return x == null || isNaN(x) ? '–' : nf.format(Math.round(x)); },
    d: function (x, k) { return x == null || isNaN(x) ? '–' : Number(x).toFixed(k == null ? 1 : k); },
    pct: function (x, k) { return x == null || isNaN(x) ? '–' : Number(x).toFixed(k == null ? 1 : k) + '%'; },
    lakh: function (x) { return (x / 1e5).toFixed(1) + ' lakh'; },
    esc: function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); },
    json: function (path) {
      return fetch(root + path).then(function (r) {
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
      if (s) s.textContent = dark ? 'Light' : 'Dark'; else btn.textContent = dark ? 'Light' : 'Dark';
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

  // --------------------------------------------------------------- charts
  SIR.charts = [];
  SIR.chart = function (id, cfg) {
    if (typeof Chart === 'undefined') {
      var el = document.getElementById(id);
      if (el) el.parentNode.insertAdjacentHTML('beforeend', '<p class="pill">The chart library did not load; the table below carries the same figures.</p>');
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
    if (m) m.insertAdjacentHTML('afterbegin', '<p class="caveat">The data for this page did not load (' + SIR.esc(e.message) + '). If you opened the file directly, serve the folder instead: <code>python3 -m http.server</code>.</p>');
  };
})();
