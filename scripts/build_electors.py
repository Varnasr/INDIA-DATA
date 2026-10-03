"""Electors in every Lok Sabha general election from 1984-85, for the SIR in
numbers page.

Reads data/india/raw/lok_sabha_electors.csv, curated by hand from the Election
Commission of India's Atlas 2024, Graph 6.1 (printed page 19), and
data/india/raw/wpp2024_voting_age.csv, the population of voting age from the
UN World Population Prospects 2024 (written by scripts/fetch_wpp_voting_age.py:
21 and over for 1984-85, 18 and over after), and writes
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
WPP = os.path.join(ROOT, 'data', 'india', 'raw', 'wpp2024_voting_age.csv')
POP_SOURCE = 'UN World Population Prospects 2024, medium variant, single-year ages, 1 July of the election year'
POP_URL = 'https://population.un.org/wpp/downloads'


def build():
    with open(RAW, encoding='utf-8') as fh:
        rows = list(csv.DictReader(fh))
    with open(WPP, encoding='utf-8') as fh:
        pop = {r['election']: r for r in csv.DictReader(fh)}
    assert set(pop) == {r['election'] for r in rows}, 'the population file and the electors file list different elections'
    out = []
    for r in rows:
        w = pop[r['election']]
        age = int(w['voting_age'])
        # the voting age fell from 21 to 18 with the 61st Amendment, in force from 1989
        assert age == (21 if float(r['year']) < 1989 else 18), '%s: wrong voting age' % r['election']
        elig = int(w['pop_21plus'] if age == 21 else w['pop_18plus'])
        e = int(r['electors'])
        out.append({'election': r['election'], 'year': float(r['year']), 'electors': e, 'voting_age': age,
                    'pop_voting_age': elig, 'pop_18plus': int(w['pop_18plus']),
                    'electors_per_100': round(100 * e / elig, 1), 'note': r['note']})
    # the Atlas states 979.8 million for 2024; a mistyped row would move it
    assert out[-1]['election'] == '2024' and out[-1]['electors'] == 979751847, 'the 2024 row does not match the Atlas'
    assert [x['year'] for x in out] == sorted(x['year'] for x in out), 'rows out of order'
    # every row sits between 30 and 120 crore, so a dropped or doubled digit fails
    for x in out:
        assert 3e8 < x['electors'] < 1.2e9, '%s: %d looks mistyped' % (x['election'], x['electors'])
    data = {'source': SOURCE, 'url': URL, 'pop_source': POP_SOURCE, 'pop_url': POP_URL, 'rows': out}
    j = json.dumps(data, ensure_ascii=False, indent=1) + '\n'
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['election', 'electors', 'electors_crore', 'voting_age', 'pop_voting_age', 'pop_voting_age_crore', 'electors_per_100_of_voting_age', 'note', 'electors_source', 'population_source'])
    for x in out:
        w.writerow([x['election'], x['electors'], '%.2f' % (x['electors'] / 1e7), x['voting_age'], x['pop_voting_age'], '%.2f' % (x['pop_voting_age'] / 1e7), x['electors_per_100'], x['note'], SOURCE, POP_SOURCE])
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
