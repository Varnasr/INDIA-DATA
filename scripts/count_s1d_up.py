"""Count Uttar Pradesh's digitised rolls by assembly constituency, and by sex and
age, from s1d labs' hashed Parquet release. Writes two aggregate tables:

    data/uttarpradesh/raw/s1d_ac.csv       one row per constituency
    data/uttarpradesh/raw/s1d_age_sex.csv  one row per sex and age band

    python3 scripts/count_s1d_up.py /path/to/s1d/data

The folder holds the three tar files as extracted, 2024-ge-final/,
2026-sir-draft/ and 2026-sir-final/, each with ac=<n>/data.parquet. The tar
files are version 2 of 25 November 2026 (https://data.s1d.me/eci-rolls/up/),
and SHA256 below is what SHA256SUMS.txt gives for them. Needs duckdb, which the
build does not: these tables are counted once, by hand, and committed.

Only counts leave this script. No token, part number, serial number or any
other field of a single entry is written out.

What is counted, in s1d labs' own terms (README of version 2):
- an entry of the 2024 roll or the final roll is one with no letter in
  status_code. A letter (E, M, Q, R, S) marks a box stamped DELETED, which
  stays printed in the roll. '#' and digit codes are kept as entries, as the
  README says.
- an entry of the 2024 roll is "not found on the draft" when its epic_token
  occurs nowhere on the SIR draft of the state. A token comes from an OCR
  reading, so a misread EPIC on either roll also counts as not found. The
  entries whose 2024 EPIC is not a valid format are counted apart.
- sex and age are as printed on the 2024 roll, which gives age on 1 January
  2024.
"""
import csv
import os
import sys

import duckdb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'uttarpradesh', 'raw')
SHA256 = {'up-electoral-roll-2024-ge-final-hashed-parquet.tar': 'dc959549c4573646148c30389a4d3edded9a973a475ce0d4716d79c373841659',
          'up-electoral-roll-2026-sir-draft-hashed-parquet.tar': '1f2872028e65cccb404c8fd130d8bf8c463390337434af0e927f7bde5de1242e',
          'up-electoral-roll-2026-sir-final-hashed-parquet.tar': '179ef95cbb9877b495418c2213794e199655ac55f398900a9391fda73028243a'}
# the README's own row counts, version 2
ROWS = {'2024-ge-final': 156925128, '2026-sir-draft': 125556003, '2026-sir-final': 134800792}
BANDS = [('18 to 24', 18, 24), ('25 to 29', 25, 29), ('30 to 34', 30, 34), ('35 to 44', 35, 44), ('45 to 54', 45, 54),
         ('55 to 64', 55, 64), ('65 to 79', 65, 79), ('80 and over', 80, 200)]
SEX = {'F': 'women', 'M': 'men', 'T': 'third gender'}


def main(base):
    c = duckdb.connect()
    tmp = os.path.join(os.path.dirname(base.rstrip('/')), 'tmp')
    os.makedirs(tmp, exist_ok=True)
    c.execute("SET threads=4; SET memory_limit='10GB'; SET preserve_insertion_order=false; SET temp_directory='%s'" % tmp)
    P = lambda roll: "read_parquet('%s/%s/ac=*/data.parquet', hive_partitioning=false)" % (base, roll)
    for roll, n in ROWS.items():
        got = c.execute('SELECT count(*) FROM %s' % P(roll)).fetchone()[0]
        assert got == n, '%s holds %d rows, the README says %d' % (roll, got, n)
    band = 'CASE ' + ' '.join("WHEN age BETWEEN %d AND %d THEN '%s'" % (lo, hi, b) for b, lo, hi in BANDS) + " ELSE 'not read' END"
    deleted = "coalesce(regexp_matches(status_code, '^[EMQRS]'), false)"
    c.execute('CREATE TABLE dk AS SELECT DISTINCT epic_token FROM %s' % P('2026-sir-draft'))
    c.execute('CREATE TABLE g AS SELECT ac, epic_token, epic_format, gender, age, %s AS del FROM %s' % (deleted, P('2024-ge-final')))
    c.execute('CREATE TABLE gn AS SELECT g.*, dk.epic_token IS NULL AS nf FROM g LEFT JOIN dk USING (epic_token)')
    c.execute('DROP TABLE g')
    ge = {r[0]: r[1:] for r in c.execute("""SELECT ac, sum((NOT del)::INT), sum(del::INT), sum((NOT del AND nf)::INT),
        sum((NOT del AND nf AND epic_format = 'other')::INT) FROM gn GROUP BY ac""").fetchall()}
    sexage = c.execute("""SELECT coalesce(gender, '') g, %s b, count(*), sum(nf::INT) FROM gn WHERE NOT del GROUP BY ALL""" % band).fetchall()
    c.execute('DROP TABLE gn')
    dr = {r[0]: r[1:] for r in c.execute('SELECT ac, count(*), sum(coalesce(extra_part, false)::INT) FROM %s GROUP BY ac' % P('2026-sir-draft')).fetchall()}
    fi = {r[0]: r[1:] for r in c.execute('SELECT ac, sum((NOT %s)::INT), sum(%s::INT) FROM %s GROUP BY ac' % (deleted, deleted, P('2026-sir-final'))).fetchall()}
    assert sorted(ge) == sorted(dr) == sorted(fi) == list(range(1, 404)), 'all 403 constituencies in each roll'
    rows = []
    for ac in range(1, 404):
        rows.append([ac, ge[ac][0], ge[ac][1], dr[ac][0], dr[ac][1], fi[ac][0], fi[ac][1], ge[ac][2], ge[ac][3]])
    with open(os.path.join(OUT, 's1d_ac.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['ac', 'ge2024_entries', 'ge2024_stamped_deleted', 'draft_entries', 'draft_entries_in_added_parts', 'final_entries',
                    'final_stamped_deleted', 'ge2024_not_on_draft', 'ge2024_not_on_draft_invalid_epic'])
        w.writerows(rows)
    order = {b: i for i, (b, _, _) in enumerate(BANDS)}
    out = {}
    for g, b, n, nf in sexage:
        k = (SEX.get(g, 'not read'), b)
        out[k] = [a + x for a, x in zip(out.get(k, [0, 0]), (n, nf))]
    so = {'women': 0, 'men': 1, 'third gender': 2, 'not read': 3}
    with open(os.path.join(OUT, 's1d_age_sex.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['sex', 'age_band', 'ge2024_entries', 'ge2024_not_on_draft'])
        for k in sorted(out, key=lambda k: (so[k[0]], order.get(k[1], 99))):
            w.writerow([k[0], k[1]] + out[k])
    print('2024 entries', sum(r[1] for r in rows), 'not on draft', sum(r[7] for r in rows), 'draft', sum(r[3] for r in rows), 'final', sum(r[5] for r in rows))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
