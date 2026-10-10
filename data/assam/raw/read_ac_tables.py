"""Reads the Chief Electoral Officer's three constituency tables in sources/
and writes ac_rolls.csv. Needs pypdf; not run by CI. --check compares.

    python3 data/assam/raw/read_ac_tables.py [--check]

Each row must satisfy men + women + third gender = total, every one of the
126 constituencies must appear once in each table, and the columns must add
to the state totals printed at the foot of each table.
"""
import csv, io, os, re, sys
import pypdf

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'sources')
TABLES = [('r2024', 'ceo_final_electors_20240208.pdf', False, 24301960),
          ('draft', 'ceo_draft_electors_20251227.pdf', True, 25201624),
          ('final', 'ceo_final_electors_20260210.pdf', True, 24958139)]


def lines(path):
    text = '\n'.join(p.extract_text() or '' for p in pypdf.PdfReader(path).pages)
    out = []
    for l in (x.strip() for x in text.splitlines()):
        # a name wrapped onto the next line, or a number alone on its own line
        if out and (re.match(r'^\((SC|ST)\)', l) or re.match(r'^[A-Za-z]', l) and re.fullmatch(r'\d{1,3}', out[-1])) and not re.search(r'\d\s*$', out[-1] if not re.fullmatch(r'\d{1,3}', out[-1]) else 'x'):
            out[-1] += ' ' + l
        else:
            out.append(l)
    return out


def parse(path, has_ps):
    n = 5 if has_ps else 4
    pat = re.compile(r'(\d{1,3})\s+([A-Za-z][A-Za-z .\-()]*?)\s+' + r'\s+'.join([r'(\d+)'] * n) + r'\s*$')
    rows, district = {}, ''
    for l in lines(path):
        m = pat.search(l)
        if not m:
            continue
        pre = l[:m.start()].strip()
        d = re.sub(r'^\d+\s*-?\s*', '', pre).strip()
        if d:
            # West Karbi Anglong wraps over two lines in the draft and final tables
            district = {'West Karbi': 'West Karbi Anglong', 'Anglong': 'West Karbi Anglong'}.get(d, d)
        nums = [int(x) for x in m.groups()[2:]]
        ps = nums.pop(0) if has_ps else None
        men, women, tg, total = nums
        assert men + women + tg == total, (path, l)
        ac = int(m.group(1))
        assert ac not in rows, (path, ac)
        name = re.sub(r'\s+', ' ', m.group(2)).strip()
        rows[ac] = dict(name=name, district=district, ps=ps, men=men, women=women, tg=tg, total=total)
    return rows


def build():
    T = {}
    for key, f, has_ps, printed in TABLES:
        R = parse(os.path.join(SRC, f), has_ps)
        assert sorted(R) == list(range(1, 127)), (f, sorted(set(range(1, 127)) - set(R)))
        assert sum(r['total'] for r in R.values()) == printed, (f, sum(r['total'] for r in R.values()), printed)
        T[key] = R
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['ac', 'ac_name', 'reserved', 'district', 'men_2024', 'women_2024', 'third_2024', 'total_2024',
                'polling_stations', 'men_draft', 'women_draft', 'third_draft', 'total_draft',
                'men_final', 'women_final', 'third_final', 'total_final'])
    for ac in range(1, 127):
        a, d, f = T['r2024'][ac], T['draft'][ac], T['final'][ac]
        assert d['ps'] == f['ps'], ac
        m = re.match(r'(.*?)\s*\((SC|ST)\)$', d['name'])
        name, res = (m.group(1), m.group(2)) if m else (d['name'], '')
        w.writerow([ac, name, res, d['district'], a['men'], a['women'], a['tg'], a['total'], d['ps'],
                    d['men'], d['women'], d['tg'], d['total'], f['men'], f['women'], f['tg'], f['total']])
    return buf.getvalue()


if __name__ == '__main__':
    out, p = build(), os.path.join(HERE, 'ac_rolls.csv')
    if '--check' in sys.argv:
        sys.exit(0 if open(p, encoding='utf-8').read() == out else 'FAIL - ac_rolls.csv differs from the PDFs')
    open(p, 'w', encoding='utf-8').write(out)
    print('wrote', p)
