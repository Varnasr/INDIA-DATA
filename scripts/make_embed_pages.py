#!/usr/bin/env python3
"""One page for each chart another site may show in a frame, at /embed/.

    python3 scripts/make_embed_pages.py          # write site/pages/embed/<place>/
    python3 scripts/make_embed_pages.py --check  # fail if a page is missing or stale

A page's source holds no figure. assets/embed.js draws the chart from the
same data the pages read: the all-India chart from data/india/states.json,
and each state's chart, its districts in the state's own measure, from the
constituency table its seat pages read (data/<state>/constituencies.json,
with the measure named in assets/seat.js). Run build_site.py after this;
its shell writes these pages with no header, menu or footer, and
build_feeds.headers() leaves /embed/ out of the rule that forbids framing.
English only, like the seat pages.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_seat_pages import STATES  # noqa: E402  the states with constituency tables

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGE = '''<!--page {meta} -->
<main id="main" class="embedmain" lang="en" dir="ltr" data-no-i18n>
<h1 class="emh" id="emH">{title}</h1>
<p class="emsub" id="emSub"></p>
<div class="vizbox" id="vEmbed"></div>
<p class="emsrc" id="emSrc"></p>
</main>
<!--scripts-->
<script src="../../assets/sir.js"></script>
<script src="../../assets/viz.js"></script>
{seat}<script src="../../assets/embed.js"></script>
<script>SIR.embedChart();</script>
'''


def pages():
    out = {}
    meta = {'title': 'Names left off per 100 electors, by state: Off the Roll', 'embed': True, 'place': 'india',
            'description': 'A chart of the names left off each state\'s draft roll for every 100 electors on its roll before the revision, for showing on another website.',
            'body': {}}
    out[os.path.join('site', 'pages', 'embed', 'india', 'index.html')] = PAGE.format(
        meta=json.dumps(meta, ensure_ascii=False), title='Names left off per 100 electors, by state', seat='')
    for folder, pid, label in STATES:
        name = label.rsplit(' ', 1)[0]
        meta = {'title': '%s, by district: Off the Roll' % name, 'embed': True, 'place': pid,
                'description': 'A chart of the districts of %s in the state\'s own measure of the revision, for showing on another website.' % name}
        out[os.path.join('site', 'pages', 'embed', folder, 'index.html')] = PAGE.format(
            meta=json.dumps(meta, ensure_ascii=False), title='%s, by district' % name,
            seat='<script src="../../assets/seat.js"></script>\n')
    return out


def main():
    P = pages()
    stale = [f for f, t in P.items() if not os.path.exists(os.path.join(ROOT, f)) or open(os.path.join(ROOT, f), encoding='utf-8').read() != t]
    if '--check' in sys.argv:
        if stale:
            raise SystemExit('FAIL - %d embed pages missing or stale; run scripts/make_embed_pages.py' % len(stale))
        print('OK: %d embed pages' % len(P))
        return
    for f in stale:
        os.makedirs(os.path.dirname(os.path.join(ROOT, f)), exist_ok=True)
        open(os.path.join(ROOT, f), 'w', encoding='utf-8').write(P[f])
    print('wrote %d of %d embed pages' % (len(stale), len(P)))


if __name__ == '__main__':
    main()
