#!/usr/bin/env python3
"""Write the source of every state's "What to do now" page from one template.

    python3 scripts/make_now_pages.py           # write site/pages/<place>/now/index.html
    python3 scripts/make_now_pages.py --check   # fail if a source differs from the template

The states are the rows of PAGES in scripts/build_now.py. A page source holds
no steps and no figures: assets/now.js draws them in the browser from the
state's stage and data/india/now.json, so a source only names its state, its
title and the overview it links back to. Run scripts/build_site.py after it.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_now import PAGES, places  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'site', 'pages')

TEMPLATE = '''<!--page {meta} -->
<main id="main" class="now" data-now="{state}">
<div class="page-head"><h1 id="nowH" data-no-i18n>What to do now in {state}</h1><ol class="summary" id="short"></ol></div>
<aside class="owin" id="nowBox" aria-live="polite" hidden></aside>
<article class="helpart nowart" id="nowBody"></article>
<p class="note limits" id="shortNote" hidden></p>
<section class="page-faq" aria-labelledby="faqH"><h2 id="faqH">Questions about this page</h2><div id="qas"></div></section>
<p class="nowback"><a href="{back}">Back to the {label} overview</a></p>
</main>
<!--scripts-->
<script src="{up}assets/sir.js"></script>
<script src="{up}assets/now.js"></script>
<script>SIR.showFaq('now');</script>
'''


def render(row, place):
    depth = row['path'].count('/')
    overview = place['pages'][0][0]
    back = os.path.relpath(overview, row['path']).replace(os.sep, '/') + '/'
    meta = {'title': 'What to do now, %s' % place['label'],
            'description': 'What an elector in %s can do at the stage the revision has reached, from the draft roll and the forms '
                           'to the notices, the hearings and the appeals, with the order or law each step rests on.' % row['state'],
            'place': row['place']}
    return TEMPLATE.format(meta=json.dumps(meta, ensure_ascii=False), state=row['state'], back=back,
                           label=place['label'], up='../' * depth)


def main():
    check = '--check' in sys.argv
    PL = places()
    stale = []
    for row in PAGES:
        path = os.path.join(SRC, row['path'], 'index.html')
        text = render(row, PL[row['place']])
        old = open(path, encoding='utf-8').read() if os.path.exists(path) else None
        if old != text:
            stale.append(row['path'])
            if not check:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                open(path, 'w', encoding='utf-8').write(text)
    if check:
        if stale:
            sys.exit('STALE: %s, run python3 scripts/make_now_pages.py' % ', '.join(stale))
        print('OK: %d "What to do now" pages match the template' % len(PAGES))
    else:
        print('wrote %s' % ', '.join(stale) if stale else 'nothing to write')


if __name__ == '__main__':
    main()
