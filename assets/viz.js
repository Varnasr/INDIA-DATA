/* Charts Chart.js does not draw: a sankey, a waterfall, a dot strip and a
   dumbbell. Plain SVG, sized by viewBox so it scales with its box, coloured
   with the site's CSS tokens (fill: var(--fill-navy)) so a theme change needs
   no redraw. Every chart is role="img" with a <title> naming what it shows;
   the page carries the finding in prose beside it. Text goes through L()
   before it arrives here. */
(function () {
  var NS = 'http://www.w3.org/2000/svg';
  function el(tag, attrs, parent, text) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) if (attrs[k] != null) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    if (parent) parent.appendChild(e);
    return e;
  }
  // a label of one or more lines, centred on y
  function label(parent, x, y, text, width, anchor, cls) {
    var lines = [].concat(SIR.wrap(text, width));
    var t = el('text', { x: x, y: y, 'text-anchor': anchor, 'dominant-baseline': 'middle', class: cls || 'vname' }, parent);
    lines.forEach(function (ln, j) { el('tspan', { x: x, dy: j ? '1.1em' : (-0.55 * (lines.length - 1)) + 'em' }, t, ln); });
    return t;
  }
  // about five round ticks between lo and hi
  function nice(lo, hi) {
    var span = Math.max(hi - lo, 1e-9), raw = span / 5, mag = Math.pow(10, Math.floor(Math.log10(raw))), f = raw / mag;
    var step = (f < 1.5 ? 1 : f < 3 ? 2 : f < 7 ? 5 : 10) * mag;
    return { step: step, lo: Math.floor(lo / step) * step, hi: Math.ceil(hi / step) * step };
  }
  function tickText(v, step) { return Math.abs(v) >= 1e5 ? SIR.lakh(v).replace(/\.0 /, ' ') : step < 1 ? (+v.toFixed(2)).toString() : SIR.n(v); }
  // a token ('--fill-navy') or a literal colour
  function paint(c) { return /^--/.test(c) ? 'fill:var(' + c + ')' : 'fill:' + c; }
  function stroke(c) { return /^--/.test(c) ? 'stroke:var(' + c + ')' : 'stroke:' + c; }
  function fill(tok) { return 'fill:var(' + tok + ')'; }
  function svgIn(box, w, h, label) {
    box = typeof box === 'string' ? document.getElementById(box) : box;
    box.innerHTML = '';
    var s = el('svg', { viewBox: '0 0 ' + w + ' ' + h, role: 'img', 'aria-label': label, class: 'viz', preserveAspectRatio: 'xMidYMid meet' }, box);
    el('title', {}, s, label);
    return s;
  }
  // Layout follows the box a chart is drawn in, not the window: a half-width
  // dashboard card gets the compact layout, and a wide box is drawn at its
  // own width so the text is the size the stylesheet says.
  var CUR = 900;
  function measure(box) { box = typeof box === 'string' ? document.getElementById(box) : box; CUR = (box && box.clientWidth) || innerWidth; }
  var phone = function () { return CUR < 600; };
  var WIDE = function () { return Math.max(600, Math.min(CUR, 1200)); };
  // counts in crore from a crore up, otherwise in lakh, as the pages write them
  var fmt = function (v) { return v >= 1e7 ? L('{x} crore', { x: (v / 1e7).toFixed(2) }) : SIR.lakh(v); };

  // ---- sankey: sources on the left, targets on the right, one flow per pair.
  // links: [{s: sourceIndex, t: targetIndex, v: value}]
  function sankey(box, o) {
    measure(box);
    var W = phone() ? Math.max(320, Math.min(CUR, 599)) : WIDE(), H = o.height || (phone() ? 440 : 400);
    var lw = phone() ? 92 : 200, nw = 12, gap = 10, top = 14, minH = phone() ? 34 : 30;
    var s = svgIn(box, W, H, o.label);
    var total = o.links.reduce(function (a, l) { return a + l.v; }, 0);
    function lay(nodes, key) {
      var sums = nodes.map(function (_, i) { return o.links.filter(function (l) { return l[key] === i; }).reduce(function (a, l) { return a + l.v; }, 0); });
      // a node is drawn to scale, but takes at least minH of room so its two
      // label lines never meet the next node's
      var room = function (h) { return Math.max(h, minH); };
      var k = (H - top * 2 - gap * (nodes.length - 1)) / total;
      for (var it = 0; it < 4; it++) {
        var used = sums.reduce(function (a, v) { return a + room(v * k); }, 0);
        k *= (H - top * 2 - gap * (nodes.length - 1)) / used;
      }
      var y = top;
      return sums.map(function (v) { var h = Math.max(v * k, 1.5), r = { y: y + (room(h) - h) / 2, h: h, v: v }; y += room(h) + gap; return r; });
    }
    var L = lay(o.sources, 's'), R = lay(o.targets, 't');
    var x0 = lw, x1 = W - lw - nw;
    var lo = L.map(function (n) { return n.y; }), ro = R.map(function (n) { return n.y; });
    var g = el('g', {}, s);
    o.links.forEach(function (l) {
      var a = L[l.s], b = R[l.t], h = l.v * (a.h / a.v);
      var ya = lo[l.s], yb = ro[l.t]; lo[l.s] += h; ro[l.t] += h;
      var xm = (x0 + nw + x1) / 2;
      var d = 'M' + (x0 + nw) + ',' + ya + ' C' + xm + ',' + ya + ' ' + xm + ',' + yb + ' ' + x1 + ',' + yb +
        ' L' + x1 + ',' + (yb + h) + ' C' + xm + ',' + (yb + h) + ' ' + xm + ',' + (ya + h) + ' ' + (x0 + nw) + ',' + (ya + h) + ' Z';
      var p = el('path', { d: d, style: fill(o.targets[l.t].tok) + ';opacity:.42', class: 'flow' }, g);
      el('title', {}, p, o.sources[l.s].name + ' → ' + o.targets[l.t].name + ': ' + fmt(l.v));
    });
    function nodes(list, lay, x, anchor, tx) {
      list.forEach(function (n, i) {
        var r = lay[i];
        el('rect', { x: x, y: r.y, width: nw, height: r.h, style: fill(n.tok) }, s);
        var lines = [].concat(SIR.wrap(n.name, phone() ? 12 : 30));
        var t = el('text', { x: tx, y: r.y + r.h / 2, 'text-anchor': anchor, 'dominant-baseline': 'middle', class: 'vlab' }, s);
        lines.forEach(function (ln, j) { el('tspan', { x: tx, dy: j ? '1.1em' : (-0.55 * lines.length) + 'em', class: 'vname' }, t, ln); });
        el('tspan', { x: tx, dy: '1.2em', class: 'vval' }, t, fmt(r.v));
      });
    }
    nodes(o.sources, L, x0, 'end', x0 - 6);
    nodes(o.targets, R, x1, 'start', x1 + nw + 6);
  }

  // ---- waterfall: steps [{name, v, kind: 'total'|'down'|'up'}]
  function waterfall(box, o) {
    measure(box);
    var n = o.steps.length, W = phone() ? Math.max(320, Math.min(CUR, 599)) : WIDE(), H = phone() ? 60 + n * 38 : 360;
    var s = svgIn(box, W, H, o.label);
    var run = 0, bars = o.steps.map(function (st) {
      var a, b;
      if (st.kind === 'total') { a = 0; b = st.v; run = st.v; }
      else if (st.kind === 'down') { a = run - st.v; b = run; run -= st.v; }
      else { a = run; b = run + st.v; run += st.v; }
      return { st: st, a: a, b: b };
    });
    var max = Math.max.apply(null, bars.map(function (x) { return x.b; }));
    var min = o.from != null ? o.from : 0;
    var tok = { total: '--fill-navy', down: '--fill-red', up: '--fill-teal' };
    if (phone()) {
      // horizontal on a phone: one row per step
      var lw = 136, rw = 66, x = function (v) { return lw + (W - lw - rw) * (v - min) / (max - min); };
      bars.forEach(function (b, i) {
        var y = 20 + i * 38;
        label(s, lw - 6, y + 12, b.st.name, 17, 'end');
        el('rect', { x: x(Math.max(b.a, min)), y: y, width: Math.max(x(b.b) - x(Math.max(b.a, min)), 1.5), height: 24, style: fill(tok[b.st.kind]) }, s);
        el('text', { x: W - rw + 6, y: y + 12, class: 'vval' }, s, (b.st.kind === 'down' ? '−' : b.st.kind === 'up' ? '+' : '') + fmt(b.st.v));
      });
      return;
    }
    var bw = (W - 60) / n, tight = bw < 100, wrapAt = Math.max(8, Math.floor(bw / (tight ? 7.2 : 8.2)));
    var names = bars.map(function (b) { return [].concat(SIR.wrap(b.st.name, Math.min(14, wrapAt))); });
    var lines = Math.max.apply(null, names.map(function (l) { return l.length; })), foot = 26 + lines * 15;
    s.setAttribute('viewBox', '0 0 ' + W + ' ' + (H + Math.max(0, foot - 80)));
    var y = function (v) { return 30 + (H - 110) * (1 - (v - min) / (max - min)); };
    bars.forEach(function (b, i) {
      var x0 = 40 + i * bw + bw * 0.15, w = bw * 0.7;
      el('rect', { x: x0, y: y(b.b), width: w, height: Math.max(y(Math.max(b.a, min)) - y(b.b), 1.5), style: fill(tok[b.st.kind]) }, s);
      if (i < n - 1) el('line', { x1: x0 + w, x2: x0 + bw, y1: y(b.st.kind === 'down' ? b.a : b.b), y2: y(b.st.kind === 'down' ? b.a : b.b), class: 'vlink' }, s);
      el('text', { x: x0 + w / 2, y: y(b.b) - 6, 'text-anchor': 'middle', class: 'vval' }, s, (b.st.kind === 'down' ? '−' : b.st.kind === 'up' ? '+' : '') + fmt(b.st.v));
      var t = el('text', { x: x0 + w / 2, y: H - 62, 'text-anchor': 'middle', class: tight ? 'vname small' : 'vname' }, s);
      names[i].forEach(function (line, j) { el('tspan', { x: x0 + w / 2, dy: j ? '1.15em' : 0 }, t, line); });
    });
  }

  // ---- dot strip (a beeswarm for a few dozen points): rows of dots on one axis
  // rows: [{name, tok, points: [{v, label}]}]
  function strip(box, o) {
    measure(box);
    var W = phone() ? Math.max(320, Math.min(CUR, 599)) : WIDE(), lw = phone() ? 0 : 150, top = (phone() ? 8 : 16) + (o.key ? 22 : 0), R = o.r || 5, D = R * 2 + 0.5;
    var all = [].concat.apply([], o.rows.map(function (r) { return r.points.map(function (p) { return p.v; }); }));
    var step = o.step || 5, max = Math.ceil(Math.max.apply(null, all) / step) * step, x = function (v) { return lw + 14 + (W - lw - 28) * v / max; };
    // lay each row out first: a swarm, each dot as close to the axis line as
    // it can go without touching another, so a row is as tall as it needs
    var rows = o.rows.map(function (r) {
      var placed = [];
      r.points.slice().sort(function (a, b) { return a.v - b.v; }).forEach(function (p) {
        var cx = x(p.v), k = 0, dy = 0;
        while (placed.some(function (q) { return (q.x - cx) * (q.x - cx) + (q.y - dy) * (q.y - dy) < D * D; })) { k++; dy = (k % 2 ? 1 : -1) * Math.ceil(k / 2) * (R + 0.5); }
        placed.push({ x: cx, y: dy, p: p });
      });
      var half = Math.max.apply(null, placed.map(function (q) { return Math.abs(q.y); }).concat([0])) + R + 4;
      return { r: r, placed: placed, half: Math.max(half, 22) };
    });
    var lab = phone() ? 18 : 0, H = top + rows.reduce(function (a, q) { return a + q.half * 2 + lab + (r_mark(q) ? 14 : 0); }, 0) + 34;
    function r_mark(q) { return (q.r.mark || []).length; }
    var s = svgIn(box, W, H, o.label);
    for (var t = 0; t <= max; t += step) {
      el('line', { x1: x(t), x2: x(t), y1: top - 6, y2: H - 28, class: 'vgrid' }, s);
      el('text', { x: x(t), y: H - 12, 'text-anchor': 'middle', class: 'vval' }, s, t);
    }
    var y0 = top;
    rows.forEach(function (q) {
      var r = q.r; y0 += lab + (r_mark(q) ? 14 : 0);
      var yc = y0 + q.half;
      if (phone()) el('text', { x: 4, y: y0 - (r_mark(q) ? 16 : 4), class: 'vname' }, s, r.name);
      else el('text', { x: lw, y: yc, 'text-anchor': 'end', 'dominant-baseline': 'middle', class: 'vname' }, s, r.name);
      q.placed.forEach(function (d) {
        var c = el('circle', { cx: d.x, cy: yc + d.y, r: R, style: fill(d.p.tok || r.tok), class: 'vdot' }, s);
        el('title', {}, c, d.p.label);
      });
      (r.mark || []).forEach(function (p) {
        el('text', { x: x(p.v), y: yc - q.half - 2, 'text-anchor': 'middle', class: 'vname small' }, s, p.label);
      });
      y0 += q.half * 2;
    });
    if (o.axis) el('text', { x: lw + (W - lw) / 2, y: H, 'text-anchor': 'middle', class: 'vval' }, s, o.axis);
    if (o.key) {
      // a key below the axis title, one entry per colour
      var kx = lw + 14;
      o.key.forEach(function (k) { el('circle', { cx: kx, cy: 6, r: R, style: fill(k[1]) }, s); var t = el('text', { x: kx + 9, y: 6, 'dominant-baseline': 'middle', class: 'vval' }, s, k[0]); kx += 34 + k[0].length * 7.5; });
    }
  }


  // ---- dumbbell: rows [{name, a, b}], a and b on one axis
  function dumbbell(box, o) {
    measure(box);
    var n = o.rows.length, W = phone() ? Math.max(320, Math.min(CUR, 599)) : WIDE(), lw = phone() ? 112 : 210, rh = phone() ? 30 : 24;
    var leg = phone() ? 44 : 24, H = leg + 16 + n * rh + 30;
    var s = svgIn(box, W, H, o.label);
    var st = o.step || 5, mn = o.min || 0, max = Math.ceil(Math.max.apply(null, o.rows.map(function (r) { return Math.max(r.a, r.b); }).concat([o.ref || 0])) / st) * st;
    var x = function (v) { return lw + 10 + (W - lw - 30) * Math.max(v - mn, 0) / (max - mn); };
    for (var t = mn; t <= max; t += st) {
      el('line', { x1: x(t), x2: x(t), y1: leg + 6, y2: H - 26, class: 'vgrid' }, s);
      el('text', { x: x(t), y: H - 10, 'text-anchor': 'middle', class: 'vval' }, s, t);
    }
    [[o.aName, o.aTok], [o.bName, o.bTok]].forEach(function (k, i) {
      // the key: side by side on a wide screen, one line each on a phone
      var lx = phone() ? 10 : lw + 10 + i * 300, ly = phone() ? 10 + i * 20 : 12;
      el('circle', { cx: lx, cy: ly, r: 5, style: fill(k[1]) }, s);
      el('text', { x: lx + 10, y: ly, 'dominant-baseline': 'middle', class: 'vval' }, s, k[0]);
    });
    if (o.ref != null) el('line', { x1: x(o.ref), x2: x(o.ref), y1: leg + 6, y2: H - 26, class: 'vzero' }, s);
    o.rows.forEach(function (r, i) {
      var y = leg + 16 + i * rh + rh / 2;
      label(s, lw - 4, y, SIR.short(r.name), phone() ? 16 : 28, 'end');
      el('line', { x1: x(r.a), x2: x(r.b), y1: y, y2: y, class: 'vlink thick' }, s);
      var ca = el('circle', { cx: x(r.a), cy: y, r: 6, style: fill(o.aTok) }, s); el('title', {}, ca, r.name + ': ' + r.a);
      var cb = el('circle', { cx: x(r.b), cy: y, r: 6, style: fill(o.bTok) }, s); el('title', {}, cb, r.name + ': ' + r.b);
    });
  }

  // ---- forest: rows [{name, est, lo, hi, main}], one estimate and its
  // interval per row, with the line at zero (no effect)
  function forest(box, o) {
    measure(box);
    var n = o.rows.length, W = phone() ? Math.max(320, Math.min(CUR, 599)) : WIDE(), lw = phone() ? 150 : 330, rw = phone() ? 0 : 150, rh = phone() ? 44 : 34, top = 10;
    var H = top + n * rh + (phone() ? 72 : 44);
    var s = svgIn(box, W, H, o.label);
    var lo = Math.min.apply(null, o.rows.map(function (r) { return r.lo != null ? r.lo : r.est; }).concat([0]));
    var hi = Math.max.apply(null, o.rows.map(function (r) { return r.hi != null ? r.hi : r.est; }).concat([0]));
    var pad = (hi - lo) * 0.08; lo -= pad; hi += pad;
    var x = function (v) { return lw + 10 + (W - lw - rw - 20) * (v - lo) / (hi - lo); };
    var tick = (hi - lo) > 3 ? 1 : 0.5;
    for (var t = Math.ceil(lo / tick) * tick; t <= hi; t += tick) {
      el('line', { x1: x(t), x2: x(t), y1: top, y2: top + n * rh, class: Math.abs(t) < 1e-9 ? 'vzero' : 'vgrid' }, s);
      el('text', { x: x(t), y: top + n * rh + 16, 'text-anchor': 'middle', class: 'vval' }, s, (t > 0 ? '+' : '') + (+t.toFixed(1)));
    }
    o.rows.forEach(function (r, i) {
      var y = top + i * rh + rh / 2;
      label(s, lw - 6, y, r.name, phone() ? 20 : 34, 'end', r.main ? 'vname' : 'vname light');
      if (r.lo != null) el('line', { x1: x(r.lo), x2: x(r.hi), y1: y, y2: y, class: 'vci' + (r.main ? ' main' : '') }, s);
      var d = el('rect', { x: x(r.est) - (r.main ? 7 : 5), y: y - (r.main ? 7 : 5), width: r.main ? 14 : 10, height: r.main ? 14 : 10, style: fill(r.main ? '--fill-red' : '--fill-navy') }, s);
      el('title', {}, d, r.name + ': ' + r.text);
      if (!phone()) el('text', { x: W - rw + 10, y: y, 'dominant-baseline': 'middle', class: 'vval' }, s, r.text);
    });
    if (o.axis) label(s, phone() ? W / 2 : lw + (W - lw - rw) / 2, H - 4, o.axis, phone() ? 44 : 90, 'middle', 'vval');
  }

  // ---- lollipop: ranked rows [{name, v, tok, text}], a stem and a dot each
  function lollipop(box, o) {
    measure(box);
    var n = o.rows.length, W = phone() ? Math.max(320, Math.min(CUR, 599)) : WIDE(), lw = phone() ? 112 : 210, rh = phone() ? 26 : 22, top = 6;
    var H = top + n * rh + 40, s = svgIn(box, W, H, o.label);
    var max = o.max || Math.max.apply(null, o.rows.map(function (r) { return r.v; }));
    var step = o.step || (max > 60 ? 20 : max > 25 ? 10 : 5); max = Math.ceil(max / step) * step;
    var x = function (v) { return lw + 8 + (W - lw - 60) * Math.max(v, 0) / max; };
    for (var t = 0; t <= max; t += step) {
      el('line', { x1: x(t), x2: x(t), y1: top, y2: top + n * rh, class: 'vgrid' }, s);
      el('text', { x: x(t), y: top + n * rh + 16, 'text-anchor': 'middle', class: 'vval' }, s, t);
    }
    if (o.ref != null) el('line', { x1: x(o.ref), x2: x(o.ref), y1: top, y2: top + n * rh, class: 'vzero' }, s);
    o.rows.forEach(function (r, i) {
      var y = top + i * rh + rh / 2;
      label(s, lw - 4, y, SIR.short(r.name), phone() ? 16 : 30, 'end', r.hi ? 'vname' : 'vname light');
      el('line', { x1: x(0), x2: x(r.v), y1: y, y2: y, class: 'vstem', style: 'stroke:var(' + (r.tok || o.tok || '--fill-navy') + ')' }, s);
      var c = el('circle', { cx: x(r.v), cy: y, r: phone() ? 5 : 6, style: fill(r.tok || o.tok || '--fill-navy') }, s);
      el('title', {}, c, r.name + ': ' + (r.text || r.v));
      el('text', { x: x(r.v) + 10, y: y, 'dominant-baseline': 'middle', class: 'vval' }, s, r.text || r.v);
    });
    if (o.axis) label(s, lw + (W - lw) / 2, H - 6, o.axis, phone() ? 40 : 90, 'middle', 'vval');
  }

  // ---- heatmap: rows x cols of shares, each cell shaded by its value and
  // written in an ink that clears contrast on its own shade
  function heat(box, o) {
    measure(box);
    var nr = o.rows.length, nc = o.cols.length, W = phone() ? Math.max(320, Math.min(CUR, 599)) : WIDE(), lw = phone() ? 104 : 210, top = phone() ? 58 : 44, rh = phone() ? 26 : 24;
    var H = top + nr * rh + 6, s = svgIn(box, W, H, o.label), cw = (W - lw - 4) / nc;
    o.cols.forEach(function (c, j) { label(s, lw + cw * j + cw / 2, top / 2, c, phone() ? 12 : 22, 'middle', 'vname'); });
    var max = o.max || 100;
    o.rows.forEach(function (r, i) {
      var y = top + i * rh;
      label(s, lw - 6, y + rh / 2, SIR.short(r.name), phone() ? 16 : 30, 'end', 'vname light');
      r.v.forEach(function (v, j) {
        if (v == null) { el('rect', { x: lw + cw * j + 1, y: y + 1, width: cw - 2, height: rh - 2, class: 'vnone' }, s); return; }
        // a tint from 6% to 45% of the colour: dark enough to read as a
        // heatmap, light enough that the theme's ink clears 5:1 on every cell
        // in both themes (checked against every token; at 50% amber falls to 4.6)
        var a = 0.06 + 0.39 * Math.max(0, Math.min(1, v / max));
        el('rect', { x: lw + cw * j + 1, y: y + 1, width: cw - 2, height: rh - 2, rx: 3, style: fill(o.tok[j]) + ';opacity:' + a.toFixed(2) }, s);
        var t = el('text', { x: lw + cw * j + cw / 2, y: y + rh / 2, 'text-anchor': 'middle', 'dominant-baseline': 'middle', class: 'vcell' }, s, (+v).toFixed(o.dp == null ? 0 : o.dp) + (o.unit || ''));
        el('title', {}, t, r.name + ', ' + o.cols[j] + ': ' + (+v).toFixed(1) + (o.unit || ''));
      });
    });
  }

  // ---- rank: a lollipop for any ranked list, negative values included.
  // rows [{name, v, col}], col a token or a literal colour
  function rank(box, o) {
    measure(box);
    var n = o.rows.length, W = phone() ? Math.max(320, Math.min(CUR, 599)) : WIDE(), lw = phone() ? 118 : 230, rh = phone() ? 28 : 24, top = 10;
    var H = top + n * rh + (o.axis ? 46 : 26), s = svgIn(box, W, H, o.label);
    var vs = o.rows.map(function (r) { return r.v; }), t = nice(Math.min(0, Math.min.apply(null, vs)), Math.max(0, Math.max.apply(null, vs)));
    var x = function (v) { return lw + 8 + (W - lw - 70) * (v - t.lo) / (t.hi - t.lo); };
    for (var g = t.lo; g <= t.hi + t.step / 2; g += t.step) {
      el('line', { x1: x(g), x2: x(g), y1: top, y2: top + n * rh, class: Math.abs(g) < t.step / 1e6 ? 'vzero' : 'vgrid' }, s);
      el('text', { x: x(g), y: top + n * rh + 16, 'text-anchor': 'middle', class: 'vval' }, s, tickText(g, t.step));
    }
    o.rows.forEach(function (r, i) {
      var y = top + i * rh + rh / 2, col = r.col || '--fill-navy';
      label(s, lw - 4, y, SIR.short(String(r.name)), phone() ? 17 : 32, 'end', 'vname light');
      el('line', { x1: x(0), x2: x(r.v), y1: y, y2: y, class: 'vstem', style: stroke(col) }, s);
      var c = el('circle', { cx: x(r.v), cy: y, r: phone() ? 5 : 6, style: paint(col) }, s);
      var txt = o.fmt ? o.fmt(r.v) : tickText(r.v, Math.abs(r.v) < 10 ? 0.1 : 1);
      el('title', {}, c, r.name + ': ' + txt);
      // a negative value's figure sits above its stem, clear of the names
      if (r.v < 0) el('text', { x: x(r.v) + 9, y: y - 8, 'text-anchor': 'start', class: 'vval' }, s, txt);
      else el('text', { x: x(r.v) + 10, y: y, 'dominant-baseline': 'middle', class: 'vval' }, s, txt);
    });
    if (o.axis) label(s, lw + (W - lw) / 2, H - 6, o.axis, phone() ? 40 : 90, 'middle', 'vval');
  }

  // ---- dots: several measures per category on one axis, joined by a line
  // from the lowest to the highest. series [{name, col, vals}]
  function dots(box, o) {
    measure(box);
    var n = o.cats.length, k = o.series.length, W = phone() ? Math.max(320, Math.min(CUR, 599)) : WIDE(), lw = phone() ? 118 : 230, rh = phone() ? 30 : 26;
    var leg = phone() ? 10 + k * 20 : 26, H = leg + 10 + n * rh + (o.axis ? 46 : 26), s = svgIn(box, W, H, o.label);
    var all = [].concat.apply([], o.series.map(function (z) { return z.vals; }));
    // a dot plot need not start at zero: where every value sits well away
    // from it, fit the axis to the values so the differences can be seen
    var mn = Math.min.apply(null, all), mx = Math.max.apply(null, all), pad = (mx - mn) * 0.15 || 1;
    var t = (mn > 0 && mx - mn < mx * 0.6) ? nice(Math.max(0, mn - pad), mx + pad) : nice(Math.min(0, mn), mx);
    var x = function (v) { return lw + 10 + (W - lw - 30) * (v - t.lo) / (t.hi - t.lo); }, y0 = leg + 10;
    for (var g = t.lo; g <= t.hi + t.step / 2; g += t.step) {
      el('line', { x1: x(g), x2: x(g), y1: y0 - 4, y2: y0 + n * rh, class: 'vgrid' }, s);
      el('text', { x: x(g), y: y0 + n * rh + 16, 'text-anchor': 'middle', class: 'vval' }, s, tickText(g, t.step));
    }
    var lx = phone() ? 10 : lw + 10;
    o.series.forEach(function (z, j) {
      var ly = phone() ? 10 + j * 20 : 12;
      el('circle', { cx: lx, cy: ly, r: 5, style: paint(z.col) }, s);
      var tt = el('text', { x: lx + 10, y: ly, 'dominant-baseline': 'middle', class: 'vval' }, s, z.name);
      if (!phone()) lx += 34 + String(z.name).length * 6.6;
    });
    o.cats.forEach(function (c, i) {
      var y = y0 + i * rh + rh / 2, vals = o.series.map(function (z) { return z.vals[i]; });
      label(s, lw - 4, y, SIR.short(String(c)), phone() ? 17 : 32, 'end', 'vname light');
      el('line', { x1: x(Math.min.apply(null, vals)), x2: x(Math.max.apply(null, vals)), y1: y, y2: y, class: 'vlink thick' }, s);
      o.series.forEach(function (z, j) {
        var d = el('circle', { cx: x(z.vals[i]), cy: y, r: phone() ? 5 : 6, style: paint(z.col) }, s);
        el('title', {}, d, c + ', ' + z.name + ': ' + tickText(z.vals[i], Math.abs(z.vals[i]) < 10 ? 0.1 : 1));
      });
    });
    if (o.axis) label(s, lw + (W - lw) / 2, H - 6, o.axis, phone() ? 40 : 90, 'middle', 'vval');
  }

  // ---- fromChart: read a Chart.js bar config and, when a better form fits,
  // draw it into box instead and return true. Two shapes are converted:
  //   one series of ranked categories (horizontal, or vertical and already
  //   in order) becomes a ranked lollipop;
  //   two or three series side by side, unstacked, becomes a dot plot.
  // Histograms, stacked bars, floating bars, lines and scatters are left to
  // Chart.js, where bars are the right form.
  function colOf(ds, i) {
    if (ds.$tokens) return ds.$tokens[i]; if (ds.$token) return ds.$token;
    var b = ds.backgroundColor; return Array.isArray(b) ? b[i % b.length] : (b || '--fill-navy');
  }
  function fromChart(box, cfg, label) {
    if (!cfg || cfg.type !== 'bar' || !cfg.data || !cfg.data.labels) return false;
    var o = cfg.options || {}, sc = o.scales || {}, ds = cfg.data.datasets || [], labels = cfg.data.labels;
    if (Object.keys(sc).some(function (k) { return sc[k] && sc[k].stacked; })) return false;
    if (ds.some(function (d) { return d.type && d.type !== 'bar'; })) return false;
    if (ds.some(function (d) { return d.data.some(function (v) { return typeof v !== 'number' || !isFinite(v); }); })) return false;
    var horiz = o.indexAxis === 'y', val = horiz ? 'x' : 'y';
    var axis = sc[val] && sc[val].title && sc[val].title.display !== false ? sc[val].title.text : (ds[0] && ds[0].label);
    if (Array.isArray(axis)) axis = axis.join(' ');
    var lab = label || axis || '';
    var tick = sc[val] && sc[val].ticks && sc[val].ticks.callback;
    var fmt = tick ? function (v) { try { var r = tick.call({ getLabelForValue: function (x) { return x; } }, v, 0, []); return Array.isArray(r) ? r.join(' ') : r; } catch (e) { return tickText(v, 1); } } : null;
    if (ds.length === 1 && labels.length >= 3) {
      var d = ds[0].data, sorted = d.every(function (v, i) { return !i || v <= d[i - 1]; }) || d.every(function (v, i) { return !i || v >= d[i - 1]; });
      if (!horiz && !(sorted && labels.length >= 5)) return false;
      rank(box, { label: lab, axis: axis, fmt: fmt, rows: labels.map(function (l, i) { return { name: Array.isArray(l) ? l.join(' ') : l, v: d[i], col: colOf(ds[0], i) }; }) });
      return true;
    }
    if (ds.length >= 2 && ds.length <= 3 && labels.length >= 2 && labels.length <= 40) {
      dots(box, { label: lab, axis: axis, cats: labels.map(function (l) { return Array.isArray(l) ? l.join(' ') : l; }),
        series: ds.map(function (z) { return { name: z.label, col: colOf(z, 0), vals: z.data }; }) });
      return true;
    }
    return false;
  }

  // ---- png: an SVG chart as a PNG, with the theme's colours written in
  function png(box, name) {
    var svg = box.querySelector('svg'); if (!svg) return;
    var c = svg.cloneNode(true), cs = getComputedStyle(document.body);
    c.querySelectorAll('[style]').forEach(function (e) { e.setAttribute('style', e.getAttribute('style').replace(/var\((--[\w-]+)\)/g, function (_, v) { return cs.getPropertyValue(v).trim(); })); });
    var src = svg.querySelectorAll('*'), dst = c.querySelectorAll('*');
    src.forEach(function (e, i) { var st = getComputedStyle(e); if (/text|tspan/.test(e.tagName)) { dst[i].setAttribute('fill', st.fill); dst[i].setAttribute('font-size', st.fontSize); dst[i].setAttribute('font-weight', st.fontWeight); dst[i].setAttribute('font-family', st.fontFamily); } else if (/line/.test(e.tagName)) { dst[i].setAttribute('stroke', st.stroke); dst[i].setAttribute('stroke-width', st.strokeWidth); } });
    var vb = svg.viewBox.baseVal, k = 2, img = new Image(), cv = document.createElement('canvas');
    cv.width = vb.width * k; cv.height = vb.height * k;
    img.onload = function () { var g = cv.getContext('2d'); g.fillStyle = cs.getPropertyValue('--card').trim() || '#fff'; g.fillRect(0, 0, cv.width, cv.height); g.drawImage(img, 0, 0, cv.width, cv.height); var a = document.createElement('a'); a.href = cv.toDataURL('image/png'); a.download = name + '.png'; a.click(); };
    img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(new XMLSerializer().serializeToString(c));
  }

  window.VIZ = { sankey: sankey, waterfall: waterfall, strip: strip, dumbbell: dumbbell, forest: forest, lollipop: lollipop, heat: heat, rank: rank, dots: dots, fromChart: fromChart, png: png };
})();
