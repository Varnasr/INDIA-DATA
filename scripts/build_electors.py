"""Electors in every Lok Sabha general election from 1984-85, for the SIR in
numbers page.

Reads data/india/raw/lok_sabha_electors.csv, curated by hand from the Election
Commission of India's Atlas 2024, Graph 6.1 (printed page 19), and writes
data/india/lok_sabha_electors.json for the page and
data/india/lok_sabha_electors.csv for download. --check fails if either is
stale.
"""
import csv, io, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'india', 'raw', 'lok_sabha_electors.csv')
OUT_JSON = os.path.join(ROOT, 'data', 'india', 'lok_sabha_electors.json')
OUT_CSV = os.path.join(ROOT, 'data', 'india', 'lok_sabha_electors.csv')
SOURCE = 'Election Commission of India, Atlas 2024, Graph 6.1 (printed page 19)'
URL = 'https://www.eci.gov.in/EBooks/atlas-2024/files/basic-html/page43.html'


def build():
    with open(RAW, encoding='utf-8') as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for r in rows:
        out.append({'election': r['election'], 'year': float(r['year']), 'electors': int(r['electors']), 'note': r['note']})
    # the Atlas states 979.8 million for 2024; a mistyped row would move it
    assert out[-1]['election'] == '2024' and out[-1]['electors'] == 979751847, 'the 2024 row does not match the Atlas'
    assert [x['year'] for x in out] == sorted(x['year'] for x in out), 'rows out of order'
    # every row sits between 30 and 120 crore, so a dropped or doubled digit fails
    for x in out:
        assert 3e8 < x['electors'] < 1.2e9, '%s: %d looks mistyped' % (x['election'], x['electors'])
    data = {'source': SOURCE, 'url': URL, 'rows': out}
    j = json.dumps(data, ensure_ascii=False, indent=1) + '\n'
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['election', 'electors', 'electors_crore', 'note', 'source'])
    for x in out:
        w.writerow([x['election'], x['electors'], '%.2f' % (x['electors'] / 1e7), x['note'], SOURCE])
    return j, buf.getvalue()


def main():
    j, c = build()
    if '--check' in sys.argv:
        for path, text in ((OUT_JSON, j), (OUT_CSV, c)):
            if not os.path.exists(path) or open(path, encoding='utf-8').read() != text:
                sys.exit('%s is stale: run scripts/build_electors.py' % os.path.relpath(path, ROOT))
        print('OK: Lok Sabha electors current')
        return
    open(OUT_JSON, 'w', encoding='utf-8').write(j)
    open(OUT_CSV, 'w', encoding='utf-8').write(c)
    print('wrote', os.path.relpath(OUT_JSON, ROOT), os.path.relpath(OUT_CSV, ROOT))


if __name__ == '__main__':
    main()
