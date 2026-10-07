"""Write the three page sources (overview, questions, method) and the places
entry for every state in build_states.STATES that has a summary.json.

    python3 scripts/make_state_pages.py

Run it once when a state is added. The pages hold no figures and no prose of
their own: assets/statepage.js draws everything from data/<slug>/summary.json,
so a page source only says which state it is. An entry already in
site/places.json is left as it is.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_states import STATES  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(ROOT, 'site', 'pages')
PLACES = os.path.join(ROOT, 'site', 'places.json')

HEAD = '<p class="report-lang">This page is in English only for now. Every figure on it comes from the Election Commission or the Chief Electoral Officer, and where it reached us through the press, the page says so.</p>'

MAIN = '''<!--page {meta} -->
<main id="main">
<div class="page-head"><h1>Overview</h1><ol class="summary" id="short"></ol></div>
{head}

<article class="state" lang="en" dir="ltr" data-no-i18n>
  <div id="sp"></div>
  <p class="note limits" id="shortNote" hidden></p>
  <section class="page-faq" aria-labelledby="faqH"><h2 id="faqH">Questions about this page</h2><div id="pageFaq"></div></section>
</article>
</main>
<!--scripts-->
<script src="../assets/sir.js"></script>
<script>window.STATE = {{ id: '{pid}', slug: '{slug}' }};</script>
<script src="../assets/statepage.js"></script>
<script>SIR.statePage('main');</script>
'''

SUB = '''<!--page {meta} -->
<main id="main">
<div class="page-head"><h1>{h1}</h1><ol class="summary" id="short"></ol></div>
{head}

<article class="state" lang="en" dir="ltr" data-no-i18n>
  <div id="{box}"></div>
  <p class="note limits" id="shortNote" hidden></p>
  {foot}
</article>
</main>
<!--scripts-->
<script src="../../assets/sir.js"></script>
<script>window.STATE = {{ id: '{pid}', slug: '{slug}' }};</script>
<script src="../../assets/statepage.js"></script>
<script>SIR.statePage('{page}');</script>
'''


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path) or open(path, encoding='utf-8').read() != text:
        open(path, 'w', encoding='utf-8').write(text)
        print('wrote', os.path.relpath(path, ROOT))


def main():
    places = open(PLACES, encoding='utf-8').read()
    have = set(re.findall(r'"id": "([a-z]+)"', places))
    entries = []
    for pid, slug in STATES:
        sp = os.path.join(ROOT, 'data', slug, 'summary.json')
        if not os.path.exists(sp):
            continue
        d = json.load(open(sp, encoding='utf-8'))
        st, label = d['state'], d['state'] + ' 2026'
        meta = lambda title, desc: json.dumps({'title': title, 'description': desc, 'place': pid}, ensure_ascii=False)
        write(os.path.join(PAGES, slug, 'index.html'), MAIN.format(
            meta=meta(label, 'How many names %s\'s draft roll left off, the reasons entered, and what changed by the final roll, from the Chief Electoral Officer\'s published figures.' % st),
            head=HEAD, pid=pid, slug=slug))
        write(os.path.join(PAGES, slug, 'faq', 'index.html'), SUB.format(
            meta=meta('Questions, ' + label, 'Questions and answers on the Special Intensive Revision in %s.' % st), h1='Questions', head=HEAD,
            box='qas', foot='<p class="note">Every figure on this page is computed from the published data when the page loads. <a href="../method/">Sources and method</a>.</p>',
            pid=pid, slug=slug, page='faq'))
        write(os.path.join(PAGES, slug, 'method', 'index.html'), SUB.format(
            meta=meta('Method, ' + label, 'Where the %s figures come from, how they were checked, and what they cannot show.' % st), h1='Method', head=HEAD,
            box='sp', foot='<section class="page-faq" aria-labelledby="faqH"><h2 id="faqH">Questions about this page</h2><div id="pageFaq"></div></section>',
            pid=pid, slug=slug, page='method'))
        if pid not in have:
            entries.append('''    {
      "id": "%s", "group": "%s",
      "label": "%s",
      "subtitle": "%s · the Special Intensive Revision of the roll",
      "band": "motifs",
      "color": "1f4e79",
      "class": "%s",
      "nav_label": "%s pages",
      "pages": [
        ["%s/", "Overview", "i0"],
        ["%s/faq/", "Questions", "i12"],
        ["%s/method/", "Method", "i10"]
      ],
      "downloads": [
        ["data/%s/tables.csv", "Every %s figure with its source, CSV", true]
      ]
    }''' % (pid, 'uts' if d.get('ut') else 'states', label, label, pid, st, slug, slug, slug, slug, st))
    if entries:
        i = places.rstrip().rindex(']')
        places = places[:i].rstrip() + ',\n' + ',\n'.join(entries) + '\n  ' + places[i:]
        open(PLACES, 'w', encoding='utf-8').write(places)
        print('added %d places' % len(entries))


if __name__ == '__main__':
    main()
