#!/usr/bin/env python3
"""One page per assembly constituency, for the states whose constituency
tables are the Chief Electoral Officer's own.

    python3 scripts/make_seat_pages.py          # write site/pages/<state>/seat/<n>/
    python3 scripts/make_seat_pages.py --check  # fail if a page is missing or stale

A page's source holds no figure: its title and description name the seat, and
assets/seat.js draws every number and sentence from
data/<state>/constituencies.json when the page loads. Run build_site.py after
this. A new state is a line in STATES and an entry in CFG in assets/seat.js.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# state folder, place id, label
STATES = [('tamilnadu', 'tn', 'Tamil Nadu 2026'), ('westbengal', 'wb', 'West Bengal 2026'), ('kerala', 'kl', 'Kerala 2026'),
          ('delhi', 'dl', 'Delhi 2026'), ('uttarakhand', 'uk', 'Uttarakhand 2026'), ('gujarat', 'gj', 'Gujarat 2026'),
          ('rajasthan', 'rj', 'Rajasthan 2026'), ('maharashtra', 'mh', 'Maharashtra 2026'), ('bihar', 'bihar', 'Bihar 2025'), ('assam', 'as', 'Assam 2026'), ('meghalaya', 'ml', 'Meghalaya 2026'), ('manipur', 'mn', 'Manipur 2026'), ('odisha', 'od', 'Odisha 2026')]

PAGE = '''<!--page {meta} -->
<main id="main">
<div class="page-head"><h1 data-no-i18n>{name}</h1><ol class="summary" id="short"></ol></div>
<p class="report-lang">This page is in English only for now. Every figure on it comes from the Election Commission or the Chief Electoral Officer, and where it reached us through the press, the page says so.</p>

<article class="state seat" lang="en" dir="ltr" data-no-i18n>
  <p class="sub" id="seatSub"></p>
  <p class="seatlinks" id="seatLinks"></p>

  <h2>Against its district and the state</h2>
  <div class="grid"><div class="panel wide"><div class="vizbox" id="vCompare"></div></div></div>
  <p class="finding" id="fCompare"></p>

  <h2>Every constituency of the district</h2>
  <div class="grid"><div class="panel wide"><div class="vizbox" id="vDistrict"></div></div></div>
  <div id="dLinks"></div>

  <section id="sPress" hidden><h2>Names left off, as the press printed them</h2>
  <div class="grid"><div class="panel wide"><div class="vizbox" id="vPress"></div></div></div>
  <p class="finding" id="fPress"></p></section>

  <section id="sReasons"><h2>The reasons</h2>
  <div class="grid"><div class="panel wide"><div class="vizbox" id="vReasons"></div></div></div>
  <p class="finding" id="fReasons"></p></section>

  <section id="sWomen"><h2>Women</h2>
  <div class="grid"><div class="panel wide"><div class="vizbox" id="vWomen"></div></div></div>
  <p class="finding" id="fWomen"></p></section>

  <section id="sAfter"><h2>After the draft</h2>
  <div class="grid"><div class="panel wide"><div class="vizbox" id="vAfter"></div></div></div>
  <p class="finding" id="fAfter"></p></section>

  <section id="sElection"><h2>Against the winning margin</h2>
  <div class="grid"><div class="panel wide"><div class="vizbox" id="vElection"></div></div></div>
  <p class="finding" id="fElection"></p></section>
</article>
  <p class="note" data-no-i18n>This site publishes counts only, never a name.</p>
  <p class="note limits" id="shortNote" hidden></p>
  <section class="page-faq" aria-labelledby="faqH"><h2 id="faqH">Questions about this page</h2><div id="pageFaq"></div></section>
</main>
<!--scripts-->
<script src="../../../assets/sir.js"></script>
<script src="../../../assets/viz.js"></script>
<script src="../../../assets/seat.js"></script>
<script>SIR.seatPage();</script>
'''


def pages():
    out = {}
    for folder, pid, label in STATES:
        A = json.load(open(os.path.join(ROOT, 'data', folder, 'constituencies.json'), encoding='utf-8'))
        for a in A:
            meta = {'title': '%s (%d), %s' % (a['name'], a['ac'], label),
                    'description': 'The SIR in %s, assembly constituency %d of %s, in %s district: how many names it lost, set against its district and the state, from the published tables.' % (a['name'], a['ac'], label.rsplit(' ', 1)[0], a['district']),
                    'place': pid, 'body': {'data-seat-state': folder, 'data-seat-ac': str(a['ac'])}}
            out[os.path.join('site', 'pages', folder, 'seat', str(a['ac']), 'index.html')] = PAGE.format(
                meta=json.dumps(meta, ensure_ascii=False), name='%s (%d)' % (a['name'], a['ac']))
    return out


def main():
    P = pages()
    stale = [f for f, t in P.items() if not os.path.exists(os.path.join(ROOT, f)) or open(os.path.join(ROOT, f), encoding='utf-8').read() != t]
    if '--check' in sys.argv:
        if stale:
            raise SystemExit('FAIL - %d seat pages missing or stale; run scripts/make_seat_pages.py' % len(stale))
        print('OK: %d seat pages' % len(P))
        return
    for f in stale:
        os.makedirs(os.path.dirname(os.path.join(ROOT, f)), exist_ok=True)
        open(os.path.join(ROOT, f), 'w', encoding='utf-8').write(P[f])
    print('wrote %d of %d seat pages' % (len(stale), len(P)))


if __name__ == '__main__':
    main()
