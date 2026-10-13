#!/usr/bin/env python3
"""One page per district, for the states whose revision was published by
district only: Uttar Pradesh, Maharashtra and Karnataka.

    python3 scripts/make_district_pages.py          # write site/pages/<state>/district/<slug>/
    python3 scripts/make_district_pages.py --check  # fail if a page is missing or stale

Like make_seat_pages.py, a page's source holds no figure; assets/district.js
draws it from data/<state>/districts.json and data/india/factors.json. The
slug is SIR.slug's, so the state pages' #d-<slug> and these addresses agree.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATES = [('uttarpradesh', 'up', 'Uttar Pradesh 2026'), ('maharashtra', 'mh', 'Maharashtra 2026'), ('karnataka', 'ka', 'Karnataka 2026')]


def slug(s):
    return re.sub(r'^-|-$', '', re.sub(r'[^a-z0-9]+', '-', s.lower()))


PAGE = '''<!--page {meta} -->
<main id="main">
<div class="page-head"><h1 data-no-i18n>{name}</h1><ol class="summary" id="short"></ol></div>
<p class="report-lang">This page is in English only for now. Every figure on it comes from the Election Commission or the Chief Electoral Officer, and where it reached us through the press, the page says so.</p>

<article class="state seat" lang="en" dir="ltr" data-no-i18n>
  <p class="sub" id="dSub"></p>
  <p class="seatlinks" id="dLinks"></p>

  <h2>Against every district of the state</h2>
  <div class="grid"><div class="panel wide"><div class="vizbox" id="vCompare"></div></div></div>
  <p class="finding" id="fCompare"></p>

  <section id="sReasons"><h2>The reasons</h2>
  <div class="grid"><div class="panel wide"><div class="vizbox" id="vReasons"></div></div></div>
  <p class="finding" id="fReasons"></p></section>

  <section id="sWomen"><h2>Women</h2>
  <p class="finding" id="fWomen"></p></section>

  <section id="sAfter"><h2>After the draft</h2>
  <p class="finding" id="fAfter"></p></section>

  <section id="sFactors"><h2>The district's circumstances</h2>
  <div class="twrap scroll" tabindex="0" role="region" aria-label="The district's circumstances"><table id="tFactors"></table></div>
  <p class="note" id="fFactors"></p></section>

  <h2>Every other district</h2>
  <p class="golist" id="others"></p>
</article>
  <p class="note" data-no-i18n>This site publishes counts only, never a name.</p>
  <p class="note limits" id="shortNote" hidden></p>
  <section class="page-faq" aria-labelledby="faqH"><h2 id="faqH">Questions about this page</h2><div id="pageFaq"></div></section>
</main>
<!--scripts-->
<script src="../../../assets/sir.js"></script>
<script src="../../../assets/viz.js"></script>
<script src="../../../assets/district.js"></script>
<script>SIR.districtPage();</script>
'''


def pages():
    out = {}
    for folder, pid, label in STATES:
        for d in json.load(open(os.path.join(ROOT, 'data', folder, 'districts.json'), encoding='utf-8')):
            name = d['district'] + (' (now %s)' % d['now'] if d.get('now') else '')
            meta = {'title': '%s district, %s' % (name, label),
                    'description': 'The SIR in %s district of %s: how many names it lost, the reasons where published, and its circumstances from the National Family Health Survey, set against the state\'s other districts.' % (name, label.rsplit(' ', 1)[0]),
                    'place': pid, 'body': {'data-district-state': folder, 'data-district': slug(d['district'])}}
            out[os.path.join('site', 'pages', folder, 'district', slug(d['district']), 'index.html')] = PAGE.format(meta=json.dumps(meta, ensure_ascii=False), name=name)
    return out


def main():
    P = pages()
    stale = [f for f, t in P.items() if not os.path.exists(os.path.join(ROOT, f)) or open(os.path.join(ROOT, f), encoding='utf-8').read() != t]
    if '--check' in sys.argv:
        if stale:
            raise SystemExit('FAIL - %d district pages missing or stale; run scripts/make_district_pages.py' % len(stale))
        print('OK: %d district pages' % len(P))
        return
    for f in stale:
        os.makedirs(os.path.dirname(os.path.join(ROOT, f)), exist_ok=True)
        open(os.path.join(ROOT, f), 'w', encoding='utf-8').write(P[f])
    print('wrote %d of %d district pages' % (len(stale), len(P)))


if __name__ == '__main__':
    main()
