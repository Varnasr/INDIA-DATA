"""Census 2011 table A-01 (number of villages, towns, households, population
and area), district by district, from the Registrar General's own file.

Reads data/india/raw/sources/census2011_A-01_villages_towns_households_population_area.xlsx
(censusindia.gov.in, catalogue PC11_A01) and writes
data/india/raw/census2011_a01_districts.csv: state, district, census code,
population, rural, urban, urban share, area in sq km and density, for all 640
districts.

    python3 scripts/census_a01.py           # write
    python3 scripts/census_a01.py --check   # fail if the output is stale

The build fails unless rural plus urban equals the total in every row and the
districts add to India's published totals.
"""
import csv
import io
import os
import sys

import re

import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'data', 'india', 'raw', 'sources', 'census2011_A-01_villages_towns_households_population_area.xlsx')
OUT = os.path.join(ROOT, 'data', 'india', 'raw', 'census2011_a01_districts.csv')
CHECK = '--check' in sys.argv
INDIA = (1210854977, 833748852, 377106125)


def read():
    ws = openpyxl.load_workbook(SRC, read_only=True).active
    states, rows = {}, {}
    for r in ws.iter_rows(min_row=5, values_only=True):
        if not r or r[3] not in ('STATE', 'DISTRICT'):
            continue
        # footnote markers (^, ###, @&, $) concern area only; runs of spaces collapse
        name = re.sub(r'\s+', ' ', re.sub(r'\s*[#@$^*]+[&]?\s*$', '', str(r[4]))).strip()
        if r[3] == 'STATE':
            states[r[0]] = name.replace(' (', '(').split('(')[0].strip().title()
            continue
        key = (r[0], r[1])
        d = rows.setdefault(key, {'state_code': r[0], 'census_code': r[0] + r[1], 'district': name})
        d[r[5].strip().lower()] = int(r[10])
        if r[5].strip() == 'Total':
            d['area'] = float(r[13])
            d['density'] = int(r[14])
    out = []
    for key, d in sorted(rows.items()):
        if d['rural'] + d['urban'] != d['total']:
            raise SystemExit('FAIL - %s: rural plus urban is not the total' % d['district'])
        out.append(dict(state=states[d['state_code']], district=d['district'], census_code=d['census_code'],
                        population=d['total'], rural=d['rural'], urban=d['urban'],
                        urban_pct=round(100 * d['urban'] / d['total'], 2), area_km2=d['area'], density=d['density']))
    tot = (sum(x['population'] for x in out), sum(x['rural'] for x in out), sum(x['urban'] for x in out))
    if len(out) != 640 or tot != INDIA:
        raise SystemExit('FAIL - %d districts, totals %s, expected 640 and %s' % (len(out), tot, INDIA))
    return out


def main():
    rows = read()
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0]), lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
    text = buf.getvalue()
    if CHECK:
        if not os.path.exists(OUT) or open(OUT, encoding='utf-8').read() != text:
            raise SystemExit('FAIL - stale: data/india/raw/census2011_a01_districts.csv')
        print('OK: census A-01 districts current')
        return
    open(OUT, 'w', encoding='utf-8').write(text)
    print('wrote %d districts' % len(rows))


if __name__ == '__main__':
    main()
