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
  // A step wide enough that the tick labels do not run into each other: on a
  // phone a lakh-sized axis at the caller's step wrote "020,0040,000...".
  // Steps go 1, 2, 5, 10 and so on, and the axis is extended to a whole step.
  function roomy(step, lo, hi, px, label) {
    var gap = function (st) { return px * st / Math.max(hi - lo, 1e-9); };
    var need = function (st) { return Math.max(phone() ? 44 : 52, (label ? String(tickText(Math.max(Math.abs(hi), Math.abs(lo)), st)).length : 4) * 7 + 10); };
    var seq = [1, 2, 5], k = 0;
    while (gap(step) < need(step) && (hi - lo) / step > 1) {
      var mag = Math.pow(10, Math.floor(Math.log10(step) + 1e-9)), f = step / mag;
      step = (f < 2 ? 2 : f < 5 ? 5 : 10) * mag;
      if (++k > 20) break;
    }
    return { step: step, hi: Math.ceil(hi / step - 1e-9) * step };
  }
  // the same for an axis from nice(): widen its step until the labels fit px
  function fitT(t, px) {
    var r = roomy(t.step, t.lo, t.hi, px, true);
    return { step: r.step, lo: Math.floor(t.lo / r.step + 1e-9) * r.step, hi: Math.ceil(t.hi / r.step - 1e-9) * r.step };
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
    var lw = o.lw || (phone() ? 92 : 200), nw = 12, gap = 10, top = 14, minH = o.minH || (phone() ? 34 : 30);
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
    var W = phone() ? Math.max(320, Math.min(CUR, 599)) : WIDE(), lw = phone() ? 0 : Math.max(150, 12 + 7.4 * Math.max.apply(null, o.rows.map(function (r) { return String(r.name).length; }))), top = (phone() ? 8 : 16) + (o.key ? 22 : 0), R = o.r || 5, D = R * 2 + 0.5;
    var all = [].concat.apply([], o.rows.map(function (r) { return r.points.map(function (p) { return p.v; }); }));
    // the axis starts at zero unless a value falls below it (a roll that grew)
    var step = o.step || 5, max = Math.ceil(Math.max.apply(null, all) / step) * step, min = Math.min(0, Math.min.apply(null, all));
    var rm = roomy(step, min, max, W - lw - 28, true); step = rm.step; max = rm.hi; min = Math.floor(min / step + 1e-9) * step;
    var x = function (v) { return lw + 14 + (W - lw - 28) * (v - min) / (max - min); };
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
    for (var t = min; t <= max + 1e-9; t += step) {
      el('line', { x1: x(t), x2: x(t), y1: top - 6, y2: H - 28, class: Math.abs(t) < 1e-9 && min < 0 ? 'vzero' : 'vgrid' }, s);
      el('text', { x: x(t), y: H - 12, 'text-anchor': 'middle', class: 'vval' }, s, tickText(t, step));
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
    var rm = roomy(st, mn, max, W - lw - 30, true); st = rm.step; max = rm.hi;
    var x = function (v) { return lw + 10 + (W - lw - 30) * Math.max(v - mn, 0) / (max - mn); };
    for (var t = mn; t <= max + 1e-9; t += st) {
      el('line', { x1: x(t), x2: x(t), y1: leg + 6, y2: H - 26, class: 'vgrid' }, s);
      el('text', { x: x(t), y: H - 10, 'text-anchor': 'middle', class: 'vval' }, s, tickText(t, st));
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

  // ---- gantt: one row per state, one thin line per schedule that applied to
  // it (the first order at the top, each later change below it). On each line
  // a bar for enumeration, a bar for claims and objections, a dot for the
  // draft and a diamond for the final roll. o.rows [{name, steps:[{label,
  // enum:[a,b], draft, claims:[a,b], claims_end, final}], note}], dates ISO.
  // English only, like the page it serves (india/process/), whose legal
  // detail is not machine translated.
  function gantt(box, o) {
    measure(box);
    box = typeof box === 'string' ? document.getElementById(box) : box;
    var D = function (iso) { return iso ? Date.parse(iso + 'T00:00:00Z') : null; };
    var all = [];
    o.rows.forEach(function (r) { r.steps.forEach(function (st) { [st.draft, st.final, st.claims_end].concat(st.enum || [], st.claims || []).forEach(function (d) { if (d) all.push(D(d)); }); }); });
    var t0 = Math.min.apply(null, all), t1 = Math.max.apply(null, all);
    var m0 = new Date(t0); m0 = Date.UTC(m0.getUTCFullYear(), m0.getUTCMonth(), 1);
    var m1 = new Date(t1); m1 = Date.UTC(m1.getUTCFullYear(), m1.getUTCMonth() + 1, 1);
    var ph = phone(), W = ph ? Math.max(320, Math.min(CUR, 599)) : WIDE(), lw = ph ? 104 : 230, lh = 9, gap = ph ? 10 : 8, leg = ph ? 62 : 34;
    var heights = o.rows.map(function (r) { return Math.max(1, r.steps.length) * lh + gap * 2; });
    var H = leg + heights.reduce(function (a, b) { return a + b; }, 0) + 30;
    var s = svgIn(box, W, H, o.label);
    var x = function (t) { return lw + 8 + (W - lw - 20) * (t - m0) / (m1 - m0); };
    var mon = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    var span = (m1 - m0) / 864e5, every = span > 400 ? 3 : span > 200 ? 2 : 1;
    for (var m = new Date(m0), i = 0; m.getTime() <= m1; m = new Date(Date.UTC(m.getUTCFullYear(), m.getUTCMonth() + 1, 1)), i++) {
      el('line', { x1: x(m.getTime()), x2: x(m.getTime()), y1: leg, y2: H - 24, class: 'vgrid' }, s);
      if (i % every === 0 && m.getTime() < m1) el('text', { x: x(m.getTime()) + 2, y: H - 8, class: 'vval' }, s, mon[m.getUTCMonth()] + (m.getUTCMonth() === 0 || i === 0 ? ' ' + m.getUTCFullYear() : ''));
    }
    // the key
    var keys = [['bar', '--fill-navy', 'Enumeration'], ['bar', '--fill-amber', 'Claims and objections'], ['dot', '--fill-navy', 'Draft roll'], ['dia', '--fill-red', 'Final roll']];
    keys.forEach(function (k, j) {
      var kx = ph ? 10 + (j % 2) * 150 : lw + 8 + j * 170, ky = ph ? 12 + Math.floor(j / 2) * 20 : 14;
      if (k[0] === 'bar') el('rect', { x: kx - 6, y: ky - 3, width: 14, height: 6, rx: 2, style: fill(k[1]) }, s);
      if (k[0] === 'dot') el('circle', { cx: kx, cy: ky, r: 4.5, style: fill(k[1]) }, s);
      if (k[0] === 'dia') el('path', { d: 'M' + kx + ' ' + (ky - 5) + 'l5 5-5 5-5-5z', style: fill(k[1]) }, s);
      el('text', { x: kx + 12, y: ky, 'dominant-baseline': 'middle', class: 'vval' }, s, k[2]);
    });
    if (!ph) el('text', { x: W - 10, y: 14, 'text-anchor': 'end', 'dominant-baseline': 'middle', class: 'vval' }, s, 'Faint lines are schedules later replaced');
    var y = leg;
    o.rows.forEach(function (r, ri) {
      var h = heights[ri];
      if (ri % 2) el('rect', { x: 0, y: y, width: W, height: h, class: 'vband' }, s);
      // o.mark: one state picked out (a link from that state's page)
      if (o.mark && r.name === o.mark) el('rect', { x: 1, y: y + 1, width: W - 2, height: h - 2, rx: 4, class: 'vmark' }, s);
      label(s, lw - 6, y + h / 2, ph ? SIR.short(r.name) : r.name, ph ? 15 : 24, 'end');
      r.steps.forEach(function (st, k) {
        var yy = y + gap + k * lh + lh / 2, last = k === r.steps.length - 1, g = el('g', { opacity: last ? 1 : 0.38 }, s);
        var tip = r.name + ', ' + st.label + ': ' + [st.enum && st.enum[0] ? 'enumeration ' + SIR.date(st.enum[0]) + ' to ' + SIR.date(st.enum[1]) : st.enum ? 'enumeration to ' + SIR.date(st.enum[1]) : '',
          st.draft ? 'draft ' + SIR.date(st.draft) : '', st.claims ? 'claims ' + SIR.date(st.claims[0]) + ' to ' + SIR.date(st.claims[1]) : st.claims_end ? 'claims to ' + SIR.date(st.claims_end) : '',
          st.final ? 'final roll ' + SIR.date(st.final) : ''].filter(Boolean).join(', ');
        el('title', {}, g, tip);
        if (st.enum && st.enum[0]) el('rect', { x: x(D(st.enum[0])), y: yy - 3, width: Math.max(2, x(D(st.enum[1])) - x(D(st.enum[0]))), height: 6, rx: 2, style: fill('--fill-navy') + ';fill-opacity:.45' }, g);
        if (st.claims) el('rect', { x: x(D(st.claims[0])), y: yy - 3, width: Math.max(2, x(D(st.claims[1])) - x(D(st.claims[0]))), height: 6, rx: 2, style: fill('--fill-amber') }, g);
        if (st.claims_end) el('path', { d: 'M' + x(D(st.claims_end)) + ' ' + (yy - 4) + 'v8', class: 'vlink thick', style: 'stroke:var(--fill-amber)' }, g);
        if (st.draft) el('circle', { cx: x(D(st.draft)), cy: yy, r: 4, style: fill('--fill-navy') }, g);
        if (st.final) { var fx = x(D(st.final)); el('path', { d: 'M' + fx + ' ' + (yy - 5) + 'l5 5-5 5-5-5z', style: fill('--fill-red') }, g); }
      });
      y += h;
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
    var rm = roomy(step, 0, max, W - lw - 60, true); step = rm.step; max = rm.hi;
    var x = function (v) { return lw + 8 + (W - lw - 60) * Math.max(v, 0) / max; };
    for (var t = 0; t <= max + 1e-9; t += step) {
      el('line', { x1: x(t), x2: x(t), y1: top, y2: top + n * rh, class: 'vgrid' }, s);
      el('text', { x: x(t), y: top + n * rh + 16, 'text-anchor': 'middle', class: 'vval' }, s, tickText(t, step));
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
    t = fitT(t, W - lw - 70);
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
    t = fitT(t, W - lw - 30);
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
  // ---- small multiples: one little line chart per panel, all on one scale,
  // so a reader can compare the shape of each path at a glance.
  // panels [{name, v: [..], hi}], steps: labels for the points, ref: a level
  // drawn in every panel (100 for an index), fmtv: label for a value
  function multiples(box, o) {
    measure(box);
    var W = phone() ? Math.max(320, Math.min(CUR, 599)) : WIDE(), cols = phone() ? 2 : Math.max(3, Math.min(5, Math.floor(W / 220)));
    var n = o.panels.length, rows = Math.ceil(n / cols), pw = W / cols, ph = phone() ? 112 : 124, foot = 34;
    var H = rows * ph + foot, s = svgIn(box, W, H, o.label);
    var all = [].concat.apply([], o.panels.map(function (p) { return p.v; })).concat(o.ref != null ? [o.ref] : []);
    var mn = Math.min.apply(null, all), mx = Math.max.apply(null, all), pad = (mx - mn) * 0.08;
    mn -= pad; mx += pad;
    var k = o.steps.length, fv = o.fmtv || function (v) { return SIR.d(v, 1); };
    o.panels.forEach(function (p, i) {
      var c = i % cols, r = Math.floor(i / cols), x0 = c * pw + 10, y0 = r * ph, iw = pw - 56, top = y0 + 26, bot = y0 + ph - 12;
      var x = function (j) { return x0 + 4 + iw * j / (k - 1); }, y = function (v) { return top + (bot - top) * (mx - v) / (mx - mn); };
      el('text', { x: x0, y: y0 + 13, class: p.hi ? 'vname' : 'vname light' }, s, SIR.short(p.name));
      el('rect', { x: x0, y: top - 4, width: iw + 8, height: bot - top + 8, rx: 6, class: 'vpanel' }, s);
      if (o.ref != null) el('line', { x1: x0, x2: x0 + iw + 8, y1: y(o.ref), y2: y(o.ref), class: 'vlink' }, s);
      var col = p.hi ? '--fill-red' : (o.tok || '--fill-navy');
      el('path', { d: p.v.map(function (v, j) { return (j ? 'L' : 'M') + x(j) + ',' + y(v); }).join(' '), class: 'vline', style: stroke(col) }, s);
      p.v.forEach(function (v, j) {
        var d = el('circle', { cx: x(j), cy: y(v), r: j === k - 1 || j === 0 ? 3.5 : 2.5, style: paint(col) }, s);
        el('title', {}, d, p.name + ', ' + o.steps[j] + ': ' + fv(v));
      });
      el('text', { x: x(k - 1) + 7, y: y(p.v[k - 1]), 'dominant-baseline': 'middle', class: 'vval' }, s, fv(p.v[k - 1]));
      // the lowest point named where it sits, so the dip can be read off
      var lowJ = p.v.indexOf(Math.min.apply(null, p.v));
      if (lowJ > 0 && lowJ < k - 1) el('text', { x: x(lowJ), y: y(p.v[lowJ]) + 14, 'text-anchor': 'middle', class: 'vval small' }, s, fv(p.v[lowJ]));
    });
    // the steps, once, under the grid
    var t = el('text', { x: 10, y: H - 10, class: 'vval' }, s);
    t.textContent = o.steps.join('  ›  ');
  }

  // ---- slope: each row a line from its value on the left to its value on
  // the right. rows [{name, a, b, tok, hi}]; only highlighted rows are named
  // on the chart, every line names itself on hover
  function slope(box, o) {
    measure(box);
    var W = phone() ? Math.max(320, Math.min(CUR, 599)) : Math.min(WIDE(), 820), H = phone() ? 420 : 460, top = 40, bot = H - 22;
    var s = svgIn(box, W, H, o.label);
    var all = [].concat.apply([], o.rows.map(function (r) { return [r.a, r.b]; })), t = nice(Math.min(0, Math.min.apply(null, all)), Math.max.apply(null, all));
    var xa = phone() ? 40 : 200, xb = W - (phone() ? 150 : 220), y = function (v) { return top + (bot - top) * (t.hi - v) / (t.hi - t.lo); };
    for (var g = t.lo; g <= t.hi + t.step / 2; g += t.step) {
      el('line', { x1: xa, x2: xb, y1: y(g), y2: y(g), class: Math.abs(g) < 1e-9 ? 'vzero' : 'vgrid' }, s);
      el('text', { x: xa - 10, y: y(g), 'text-anchor': 'end', 'dominant-baseline': 'middle', class: 'vval' }, s, tickText(g, t.step));
    }
    [[xa, o.aName], [xb, o.bName]].forEach(function (c, i) { label(s, phone() && !i ? c[0] + 20 : c[0], 14, c[1], phone() ? 14 : 30, 'middle', 'vname'); });
    var rows = o.rows.slice().sort(function (p, q) { return (p.hi ? 1 : 0) - (q.hi ? 1 : 0); });
    rows.forEach(function (r) {
      var col = r.tok || (r.hi ? '--fill-red' : '--fill-grey');
      var g = el('g', { class: r.hi ? 'vslope hi' : 'vslope' }, s);
      el('line', { x1: xa, x2: xb, y1: y(r.a), y2: y(r.b), style: stroke(col) }, g);
      el('circle', { cx: xa, cy: y(r.a), r: 4, style: paint(col) }, g);
      el('circle', { cx: xb, cy: y(r.b), r: 4, style: paint(col) }, g);
      el('title', {}, g, r.name + ': ' + SIR.d(r.a, 1) + ' → ' + SIR.d(r.b, 1));
    });
    // names for the highlighted rows on the right, nudged apart so none touch
    var lab = o.rows.filter(function (r) { return r.hi || r.lab; }).map(function (r) { return { r: r, y: y(r.b) }; }).sort(function (p, q) { return p.y - q.y; });
    for (var i = 1; i < lab.length; i++) if (lab[i].y - lab[i - 1].y < 15) lab[i].y = lab[i - 1].y + 15;
    lab.forEach(function (q) { el('text', { x: xb + 10, y: q.y, 'dominant-baseline': 'middle', class: q.r.hi ? 'vname' : 'vname light' }, s, SIR.short(q.r.name) + ' ' + SIR.d(q.r.b, 1)); });
  }

  // ---- scatter: points [{x, y, tok, label, r}], with an optional diagonal
  // (y = x) and reference lines, and a key of colours
  function scatter(box, o) {
    measure(box);
    var W = phone() ? Math.max(320, Math.min(CUR, 599)) : Math.min(WIDE(), 900), H = phone() ? 360 : 440, l = phone() ? 46 : 60, b = 52, top = o.key ? 30 : 12, rgt = 16;
    var s = svgIn(box, W, H, o.label);
    var xs = o.points.map(function (p) { return p.x; }), ys = o.points.map(function (p) { return p.y; });
    var tx = nice(o.xMin != null ? o.xMin : Math.min.apply(null, xs), Math.max.apply(null, xs)), ty = nice(o.yMin != null ? o.yMin : Math.min.apply(null, ys), Math.max.apply(null, ys));
    tx = fitT(tx, W - l - rgt);
    var x = function (v) { return l + (W - l - rgt) * (v - tx.lo) / (tx.hi - tx.lo); }, y = function (v) { return top + (H - top - b) * (ty.hi - v) / (ty.hi - ty.lo); };
    var g;
    for (g = tx.lo; g <= tx.hi + tx.step / 2; g += tx.step) { el('line', { x1: x(g), x2: x(g), y1: top, y2: H - b, class: 'vgrid' }, s); el('text', { x: x(g), y: H - b + 16, 'text-anchor': 'middle', class: 'vval' }, s, tickText(g, tx.step)); }
    for (g = ty.lo; g <= ty.hi + ty.step / 2; g += ty.step) { el('line', { x1: l, x2: W - rgt, y1: y(g), y2: y(g), class: 'vgrid' }, s); el('text', { x: l - 6, y: y(g), 'text-anchor': 'end', 'dominant-baseline': 'middle', class: 'vval' }, s, tickText(g, ty.step)); }
    // y = x, drawn only over the range both axes share
    var d0 = Math.max(tx.lo, ty.lo), d1 = Math.min(tx.hi, ty.hi);
    if (o.diag && d1 > d0) el('line', { x1: x(d0), y1: y(d0), x2: x(d1), y2: y(d1), class: 'vlink' }, s);
    if (o.refY != null) el('line', { x1: l, x2: W - rgt, y1: y(o.refY), y2: y(o.refY), class: 'vzero' }, s);
    if (o.diag && o.diagLabel && d1 > d0) el('text', { x: x(d1) + 4, y: y(d1) - 6, 'text-anchor': x(d1) > W - 90 ? 'end' : 'start', class: 'vval' }, s, o.diagLabel);
    o.points.forEach(function (p) {
      var c = el('circle', { cx: x(p.x), cy: y(p.y), r: p.r || (phone() ? 3.5 : 4.5), style: paint(p.tok || '--fill-navy') + ';opacity:.85', class: 'vdot' }, s);
      el('title', {}, c, p.label);
    });
    label(s, l + (W - l) / 2, H - 10, o.xAxis, phone() ? 44 : 90, 'middle', 'vval');
    var ya = el('text', { x: 12, y: top + (H - top - b) / 2, 'text-anchor': 'middle', class: 'vval', transform: 'rotate(-90 12 ' + (top + (H - top - b) / 2) + ')' }, s, o.yAxis);
    if (o.key) { var kx = l; o.key.forEach(function (k) { el('circle', { cx: kx + 5, cy: 10, r: 5, style: paint(k[1]) }, s); el('text', { x: kx + 14, y: 10, 'dominant-baseline': 'middle', class: 'vval' }, s, k[0]); kx += 30 + k[0].length * 7; }); }
  }

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

  // ---- map: a choropleth of constituencies from a GeoJSON of polygons with
  // an `ac` property. v(ac) gives the value (null for none), name(ac) the
  // label; five bins of one colour, the lightest still visible on the card.
  // pick(ac) is called on a click, and select(ac) outlines a seat.
  function map(box, o) {
    measure(box);
    box = typeof box === 'string' ? document.getElementById(box) : box;
    var feats = o.geo.features, xs = [], ys = [];
    feats.forEach(function (f) { eachPt(f.geometry, function (p) { xs.push(p[0]); ys.push(p[1]); }); });
    var x0 = Math.min.apply(null, xs), x1 = Math.max.apply(null, xs), y0 = Math.min.apply(null, ys), y1 = Math.max.apply(null, ys);
    var kx = Math.cos((y0 + y1) / 2 * Math.PI / 180), gw = (x1 - x0) * kx, gh = y1 - y0;
    var W = phone() ? Math.max(320, Math.min(CUR, 599)) : Math.min(WIDE(), 900), leg = 46;
    var H = Math.min(Math.round(W * gh / gw), phone() ? 640 : 760) + leg, sc = Math.min((W - 16) / gw, (H - leg - 16) / gh);
    var ox = (W - gw * sc) / 2, oy = leg + 8;
    var P = function (p) { return (ox + (p[0] - x0) * kx * sc).toFixed(1) + ',' + (oy + (y1 - p[1]) * sc).toFixed(1); };
    var s = svgIn(box, W, H, o.label);
    var vals = feats.map(function (f) { return o.v(f.properties.ac); }).filter(function (v) { return v != null && isFinite(v); }).sort(function (a, b) { return a - b; });
    var q = [0.2, 0.4, 0.6, 0.8].map(function (t) { return vals[Math.floor(t * (vals.length - 1))]; });
    if (o.breaks) q = o.breaks;
    var bin = function (v) { var i = 0; while (i < q.length && v > q[i]) i++; return i; };
    var op = [0.14, 0.3, 0.48, 0.68, 0.9], tok = o.tok || '--fill-red', fv = o.fmt || function (v) { return SIR.d(v, 1); };
    var g = el('g', { class: 'vmap' }, s), paths = {};
    feats.forEach(function (f) {
      var ac = f.properties.ac, v = o.v(ac), d = geomPath(f.geometry, P);
      var pth = el('path', { d: d, 'data-ac': ac, style: v == null ? 'fill:var(--line)' : fill(tok) + ';fill-opacity:' + op[bin(v)] }, g);
      el('title', {}, pth, o.name(ac) + ': ' + (v == null ? L('no figure') : fv(v)));
      paths[ac] = pth;
    });
    // an inset: a city's seats drawn again, enlarged, in a corner where the
    // state's outline leaves room, so seats too small to tap can be reached
    var extra = {};
    if (o.inset) {
      var inF = feats.filter(function (f) { return o.inset.acs.indexOf(f.properties.ac) >= 0; }), ix = [], iy = [];
      inF.forEach(function (f) { eachPt(f.geometry, function (p) { ix.push(p[0]); iy.push(p[1]); }); });
      var a0 = Math.min.apply(null, ix), a1 = Math.max.apply(null, ix), b0 = Math.min.apply(null, iy), b1 = Math.max.apply(null, iy);
      var bw = Math.min(phone() ? 150 : 230, W * 0.36), iw = (a1 - a0) * kx, ih = b1 - b0, k2 = Math.min((bw - 12) / iw, (bw - 12) / ih);
      var bh = ih * k2 + 30, bx = o.inset.left ? 8 : W - bw - 8, by = o.inset.bottom ? H - bh - 8 : leg + 4;
      var ig = el('g', { class: 'vmap vinset' }, s);
      el('rect', { x: bx, y: by, width: bw, height: bh, rx: 8, class: 'vpanel' }, ig);
      el('text', { x: bx + 8, y: by + 15, class: 'vval' }, ig, o.inset.name);
      var P2 = function (p) { return (bx + 6 + (bw - 12 - iw * k2) / 2 + (p[0] - a0) * kx * k2).toFixed(1) + ',' + (by + 24 + (b1 - p[1]) * k2).toFixed(1); };
      inF.forEach(function (f) {
        var ac = f.properties.ac, v = o.v(ac);
        var pth = el('path', { d: geomPath(f.geometry, P2), 'data-ac': ac, style: v == null ? 'fill:var(--line)' : fill(tok) + ';fill-opacity:' + op[bin(v)] }, ig);
        el('title', {}, pth, o.name(ac) + ': ' + (v == null ? L('no figure') : fv(v)));
        extra[ac] = pth;
      });
      if (o.pick) ig.addEventListener('click', function (e) { var t = e.target.closest('path'); if (t) o.pick(+t.getAttribute('data-ac')); });
    }
    if (o.pick) g.addEventListener('click', function (e) { var t = e.target.closest('path'); if (t) o.pick(+t.getAttribute('data-ac')); });
    // the key: five swatches with the range each covers
    var lo = vals[0], hi = vals[vals.length - 1], edges = [lo].concat(q, [hi]), kw = Math.min(110, (W - 20) / 5);
    if (o.title) el('text', { x: 10, y: 12, class: 'vval' }, s, o.title);
    op.forEach(function (a, i) {
      el('rect', { x: 10 + i * kw, y: 20, width: kw - 4, height: 10, rx: 2, style: fill(tok) + ';fill-opacity:' + a }, s);
      el('text', { x: 10 + i * kw, y: 42, class: 'vval small' }, s, fv(edges[i]) + '–' + fv(edges[i + 1]));
    });
    // one seat, or several (a district's seats) outlined together
    box.__select = function (ac) {
      var on = [].concat(ac).map(Number);
      [paths, extra].forEach(function (set) {
        Object.keys(set).forEach(function (k) { set[k].classList.toggle('on', on.indexOf(+k) >= 0); });
        on.forEach(function (a) { if (set[a]) set[a].parentNode.appendChild(set[a]); });
      });
    };
  }
  function eachPt(gm, f) { (gm.type === 'Polygon' ? [gm.coordinates] : gm.coordinates).forEach(function (poly) { poly.forEach(function (ring) { ring.forEach(f); }); }); }
  function geomPath(gm, P) { return (gm.type === 'Polygon' ? [gm.coordinates] : gm.coordinates).map(function (poly) { return poly.map(function (ring) { return 'M' + ring.map(P).join('L') + 'Z'; }).join(''); }).join(''); }

  // ---- what each chart's CSV holds: the numbers it was drawn from
  var CSV = {
    sankey: function (o) { return [['from', 'to', 'count']].concat(o.links.map(function (l) { return [o.sources[l.s].name, o.targets[l.t].name, l.v]; })); },
    waterfall: function (o) { return [['step', 'count', 'kind']].concat(o.steps.map(function (s) { return [s.name, s.v, s.kind]; })); },
    strip: function (o) { return [['group', 'point', 'value']].concat([].concat.apply([], o.rows.map(function (r) { return r.points.map(function (p) { return [r.name, p.label, p.v]; }); }))); },
    dumbbell: function (o) { return [['name', o.aName, o.bName]].concat(o.rows.map(function (r) { return [r.name, r.a, r.b]; })); },
    slope: function (o) { return [['name', o.aName, o.bName]].concat(o.rows.map(function (r) { return [r.name, r.a, r.b]; })); },
    forest: function (o) { return [['estimate', 'value', 'low', 'high']].concat(o.rows.map(function (r) { return [r.name, r.est, r.lo, r.hi]; })); },
    lollipop: function (o) { return [['name', o.axis || 'value']].concat(o.rows.map(function (r) { return [r.name, r.v]; })); },
    rank: function (o) { return [['name', o.axis || 'value']].concat(o.rows.map(function (r) { return [r.name, r.v]; })); },
    heat: function (o) { return [['name'].concat(o.cols)].concat(o.rows.map(function (r) { return [r.name].concat(r.v); })); },
    dots: function (o) { return [['category'].concat(o.series.map(function (z) { return z.name; }))].concat(o.cats.map(function (c, i) { return [c].concat(o.series.map(function (z) { return z.vals[i]; })); })); },
    multiples: function (o) { return [['name'].concat(o.steps)].concat(o.panels.map(function (p) { return [p.name].concat(p.v); })); },
    scatter: function (o) { return [['point', o.xAxis, o.yAxis]].concat(o.points.map(function (p) { return [p.label, p.x, p.y]; })); },
    gantt: function (o) { var out = [['state', 'schedule', 'enumeration from', 'enumeration to', 'draft', 'claims from', 'claims to', 'final']]; o.rows.forEach(function (r) { r.steps.forEach(function (st) { out.push([r.name, st.label, st.enum ? st.enum[0] || '' : '', st.enum ? st.enum[1] : '', st.draft || '', st.claims ? st.claims[0] : '', st.claims ? st.claims[1] : st.claims_end || '', st.final || '']); }); }); return out; },
    map: function (o) { return [['ac', 'name', o.title || 'value']].concat(o.geo.features.map(function (f) { var a = f.properties.ac; return [a, o.name(a), o.v(a)]; })); }
  };
  function keep(name, f) {
    return function (box, o) {
      var r = f.apply(this, arguments);
      try { var b = typeof box === 'string' ? document.getElementById(box) : box; if (b) b.__csv = name === 'fromChart' ? chartCsv(o) : CSV[name](o); } catch (e) {}
      return r;
    };
  }
  function chartCsv(cfg) {
    var ds = cfg.data.datasets, labels = cfg.data.labels;
    return [['label'].concat(ds.map(function (d) { return d.label || ''; }))].concat(labels.map(function (l, i) { return [Array.isArray(l) ? l.join(' ') : l].concat(ds.map(function (d) { return d.data[i]; })); }));
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

  var K = {};
  var F = { gantt: gantt, multiples: multiples, slope: slope, scatter: scatter, sankey: sankey, waterfall: waterfall, strip: strip, dumbbell: dumbbell, forest: forest, lollipop: lollipop, heat: heat, rank: rank, dots: dots, map: map };
  Object.keys(F).forEach(function (k) { K[k] = keep(k, F[k]); });
  K.fromChart = function (box, cfg, label) { var ok = fromChart(box, cfg, label); if (ok) try { (typeof box === 'string' ? document.getElementById(box) : box).__csv = chartCsv(cfg); } catch (e) {} return ok; };
  K.png = png;
  window.VIZ = K;
})();
