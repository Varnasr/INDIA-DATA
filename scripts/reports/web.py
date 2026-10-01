"""The full reports as pages on the site: india/report/, bihar/report/ and hyderabad/report/.

Each report builder writes report.fragment.html and its figures into the page
folder (Report.save_web). This script puts that fragment into the site's page
shell, taken from the analysis's method page so the header, the tab row and
the scripts are the same as everywhere else, and deletes the fragment.

The report is in English: the article carries lang="en" and data-no-i18n, and
a translated page shows a one-line note saying so above it.

    python3 scripts/reports/web.py bihar hyderabad
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
META = {
    'india': ('All India SIR: full report',
              'The All India report on the Special Intensive Revision. It covers the reasons recorded for removals in each state and union territory, women among the removed, what goes with the removal rate, and what the Election Commission should do.',
              'sir-india-report.pdf'),
    'bihar': ('Bihar SIR 2025: full report',
              'The full report on the Bihar Special Intensive Revision of 2025. It covers Bihar as a whole, gives each of the 38 districts a chapter, sets out what the lists show and what they cannot, and ends with what the Election Commission should do.',
              'bihar-sir-2025-report.pdf'),
    'hyderabad': ('Hyderabad Old City SIR 2026: full report',
                  'The full report on the 2026 Special Intensive Revision in five Old City constituencies of Hyderabad. It covers the five together, gives each constituency a chapter, and ends with what the Election Commission should do before the final roll.',
                  'hyderabad-old-city-sir-2026-report.pdf'),
}


def build(site):
    folder = os.path.join(ROOT, site, 'report')
    frag_path = os.path.join(folder, 'report.fragment.html')
    frag = open(frag_path, encoding='utf-8').read()
    # One h1 on the page, the report's title; the chapters step down a level.
    for lvl in (3, 2, 1):
        frag = re.sub(r'<h%d(?![^>]*class="title")' % lvl, '<h%d' % (lvl + 1), frag)
        frag = frag.replace('</h%d>' % lvl, '</h%d>' % (lvl + 1))
    frag = re.sub(r'(<h1 class="title">.*?)</h2>', r'\1</h1>', frag, count=1)
    frag = frag.replace('<h3 id="toc-h">Contents</h3>', '<h2 id="toc-h">Contents</h2>')
    # Print sizes (7.5pt tables) are for the PDF; the page sizes its own.
    frag = re.sub(r'<table style="[^"]*"', '<table', frag)
    title, desc, pdf = META[site]
    place = {'india': 'india', 'bihar': 'bihar', 'hyderabad': 'hyd'}[site]
    meta = {'title': title, 'description': desc, 'place': place, 'report': True}
    content = ('<main id="main" class="report-page">\n'
               '<p class="report-lang">The full report is published in English. The same text is in the PDF.</p>\n'
               '<p class="report-actions" data-i18n-each><a class="btn" href="../../reports/' + pdf + '" download>Download the PDF</a></p>\n'
               '<article class="report" lang="en" dir="ltr" data-no-i18n>' + frag + '</article>\n'
               '</main>')
    # The page's own content goes to site/pages; scripts/build_site.py puts
    # the shared shell round it.
    src = os.path.join(ROOT, 'site', 'pages', site, 'report', 'index.html')
    with open(src, 'w', encoding='utf-8') as fh:
        fh.write('<!--page ' + json.dumps(meta, ensure_ascii=False) + ' -->\n' + content + '\n<!--scripts-->\n<script src="../../assets/sir.js"></script>\n')
    os.remove(frag_path)
    print('wrote', os.path.relpath(src, ROOT))


if __name__ == '__main__':
    for s in sys.argv[1:] or ['india', 'bihar', 'hyderabad']:
        build(s)
    subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_site.py')], check=True)
