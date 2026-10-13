Promise.all([SIR.json('data/bihar/constituencies.json'), SIR.json('data/bihar/districts.json')]).then(function (r0) {
  var A = r0[0], D = r0[1];
  SIR.json('data/geo/bihar.json').then(function (geo) {
    var byAc = {}; A.forEach(function (a) { byAc[a.ac] = a; });
    var seatsOf = function (d) { return A.filter(function (a) { return a.district === d.district; }); };
    var sum = function (d, k) { return seatsOf(d).reduce(function (t, a) { return t + a[k]; }, 0); };
    var DSET = { rows: D, key: function (d) { return SIR.slug(d.district); }, label: function (d) { return L('{d} district', { d: d.district }); },
      card: function (d) { return SIR.facts([
        [L('Names removed'), SIR.n(sum(d, 'total'))], [L('Per 100 electors'), SIR.d(d.per_100, 1)], [L('Women among them'), SIR.pct(100 * sum(d, 't_f') / sum(d, 'total'))],
        [L('Entered as dead'), SIR.n(sum(d, 'r_dead'))], [L('Shifted'), SIR.n(sum(d, 'r_shifted'))], [L('Absent'), SIR.n(sum(d, 'r_absent'))], [L('Already enrolled'), SIR.n(sum(d, 'r_enrolled'))],
        [L('Seats where more were removed than the margin'), L('{k} of {n}', { k: seatsOf(d).filter(function (a) { return a.total > a.margin2025; }).length, n: d.acs })]]) + '<p class="note">' + L('Its constituencies') + '</p>' + SIR.goList(seatsOf(d), function (a) { return 'ac-' + a.ac; }, function (a) { return a.ac + '. ' + a.name; }); },
      share: function (d) { return L('{d} district, Bihar. {r} names were removed from the roll here in the revision, {p} of every 100 electors, across {n} constituencies, and women were {w} of them. These are counts from the Election Commission\'s published lists. A reason on the list is what the officer wrote down, and nobody checked it.', { d: d.district, r: SIR.n(sum(d, 'total')), p: SIR.d(d.per_100, 1), n: d.acs, w: SIR.pct(100 * sum(d, 't_f') / sum(d, 'total')) }); },
      pick: function (d) { var b = document.getElementById('vMap'); if (b.__select) b.__select(seatsOf(d).map(function (a) { return a.ac; })); } };
    var F = SIR.finder('finder', { seatPages: '../seat/', districtPages: '../district/', rows: A, more: [DSET], prompt: L('Find a constituency or district'), placeholder: L('Type a name, a number or a district'), key: function (a) { return 'ac-' + a.ac; }, label: function (a) { return a.ac + '. ' + a.name + ' (' + a.district + ')'; },
      card: function (a) { return SIR.facts([
        [L('Names removed'), SIR.n(a.total)], [L('Per 100 electors'), SIR.d(a.per_100, 1)], [L('Women among them'), SIR.pct(100 * a.t_f / a.total)],
        [L('Entered as dead'), SIR.n(a.r_dead)], [L('Shifted'), SIR.n(a.r_shifted)], [L('Absent'), SIR.n(a.r_absent)], [L('Already enrolled'), SIR.n(a.r_enrolled)],
        [L('Won in 2025'), a.win2025 + ' · ' + L('margin {m}', { m: SIR.n(a.margin2025) })], [L('Removed more than the margin'), a.total > a.margin2025 ? L('Yes') : L('No')]]); },
      share: function (a) { return L('{n}, Bihar. {r} names were removed from the roll here in the revision, {p} of every 100 electors, and women were {w} of them. The seat was won in 2025 by {m} votes. These are counts from the Election Commission\'s published lists. A reason on the list is what the officer wrote down, and nobody checked it.', { n: a.name, r: SIR.n(a.total), p: SIR.d(a.per_100, 1), w: SIR.pct(100 * a.t_f / a.total), m: SIR.n(a.margin2025) }); },
      pick: function (a) { var b = document.getElementById('vMap'); if (b.__select) b.__select(a.ac); } });
    VIZ.map('vMap', { geo: geo, label: L('Map of names removed per 100 electors, by constituency'), title: L('Removed per 100 electors'), 
      v: function (ac) { return byAc[ac] ? byAc[ac].per_100 : null; }, name: function (ac) { return byAc[ac] ? byAc[ac].name : ''; },
      pick: function (ac) { if (byAc[ac]) F.select(byAc[ac]); } });
    var it = F.item[SIR.hashId()]; if (it && it.s.pick) it.s.pick(it.r);
    SIR.tools();
  });
}).catch(SIR.fail);
