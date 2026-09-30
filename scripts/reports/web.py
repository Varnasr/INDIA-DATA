"""The full reports as pages on the site: india/report/, bihar/report/ and hyderabad/report/.

Each report builder writes report.fragment.html and its figures into the page
folder (Report.save_web). This script puts that fragment into the site's page
shell, taken from the analysis's method page so the header, the tab row and
the scripts are the same as everywhere else, and deletes the fragment.

The report is in English: the article carries lang="en" and data-no-i18n, and
a translated page shows a one-line note saying so above it.

    python3 scripts/reports/web.py bihar hyderabad
"""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
META = {
    'india': ('All India SIR: full report',
              'The overall report on the Special Intensive Revision: the reasons recorded for every removal in each state and union territory, with the list-level findings for Bihar and Hyderabad Old City, and what the Election Commission should do.',
              'sir-india-report.pdf'),
    'bihar': ('Bihar SIR 2025: full report',
              'The full report on the Bihar Special Intensive Revision of 2025: Bihar as a whole, a chapter for each of the 38 districts, what the lists show and do not, and what the Election Commission should do.',
              'bihar-sir-2025-report.pdf'),
    'hyderabad': ('Hyderabad Old City SIR 2026: full report',
                  'The full report on the 2026 Special Intensive Revision in five Old City constituencies of Hyderabad: the five together, a chapter for each constituency, and what the Election Commission should do before the final roll.',
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
    tpl = open(os.path.join(ROOT, site, 'method', 'index.html'), encoding='utf-8').read()
    head = tpl[:tpl.index('<main id="main">')]
    title, desc, pdf = META[site]
    head = re.sub(r'<title>.*?</title>', '<title>%s</title>' % title, head, count=1)
    head = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % desc, head, count=1)
    head = head.replace(' aria-current="page"', '')
    head = head.replace('href="../../%s/report/">' % site, 'href="../../%s/report/" aria-current="page">' % site)
    foot = tpl[tpl.index('<footer>'):tpl.index('</footer>') + len('</footer>')]
    page = (head +
            '<main id="main" class="report-page">\n'
            '<p class="report-lang">The full report is published in English. The same text is in the PDF.</p>\n'
            '<p class="report-actions" data-i18n-each><a class="btn" href="../../reports/' + pdf + '" download>Download the PDF</a></p>\n'
            '<article class="report" lang="en" dir="ltr" data-no-i18n>' + frag + '</article>\n'
            '</main>\n' + foot + '\n<script src="../../assets/sir.js"></script>\n</body>\n</html>\n')
    open(os.path.join(folder, 'index.html'), 'w', encoding='utf-8').write(page)
    os.remove(frag_path)
    print('wrote', os.path.relpath(os.path.join(folder, 'index.html'), ROOT))


if __name__ == '__main__':
    for s in sys.argv[1:] or ['india', 'bihar', 'hyderabad']:
        build(s)
