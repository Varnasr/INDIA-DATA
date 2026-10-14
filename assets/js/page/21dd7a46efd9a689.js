SIR.json('data/india/ac_finder.json').then(function (F) {
  var root = document.body.getAttribute('data-root') || '';
  SIR.table('tMeasures', [{ h: 'State' }, { h: 'What is counted' }, { h: 'Per' }, { h: 'Constituencies', num: true }],
    F.places.map(function (p) {
      return ['<a href="' + root + SIR.esc(p.page) + '">' + SIR.esc(p.state) + '</a>', SIR.esc(p.what.charAt(0).toUpperCase() + p.what.slice(1)), (p.per === 1000 ? '1,000' : '100') + ' on ' + SIR.esc(p.of), String(p.acs)];
    }));
}).catch(SIR.fail);
