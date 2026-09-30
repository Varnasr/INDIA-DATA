"""Counts, by reason, from the row-level Bihar phase 1 deletion list.

The row-level list carries every removed elector's name, relative's name and
EPIC number, so it is never stored here. This script reads it as a stream on
standard input and writes counts only:

    data/bihar/raw/reasons_by_ac.csv.gz    ac, reason, sex, age band, count
    data/bihar/raw/reasons_by_booth.csv.gz ac, January part, reason, sex, count

    <stream of the list> | python3 scripts/aggregate_bihar_reasons.py

Reasons are recorded in Hindi and mapped to four codes (dead, shifted, absent,
already_enrolled); anything else is counted as 'other' and printed, so nothing
is dropped without notice. Only the reason is kept: a cell's text after a line
break, which in a few rows is part of a name, never reaches the counts.
"""
import collections
import csv
import gzip
import io
import os
import sys

RAW = os.path.join(os.path.dirname(__file__), '..', 'data', 'bihar', 'raw')
BANDS = [(18, 24), (25, 29), (30, 39), (40, 49), (50, 59), (60, 69), (70, 79), (80, 200)]


def band(a):
    try:
        a = int(float(a))
    except (TypeError, ValueError):
        return 'unknown'
    for lo, hi in BANDS:
        if lo <= a <= hi:
            return '80+' if lo == 80 else '%d-%d' % (lo, hi)
    return 'under 18' if a < 18 else 'unknown'


# The list records the reason in Hindi, and a few cells carry a line break
# followed by stray text (a surname fragment). Only the reason itself is
# kept: the first word decides it, and nothing after a line break survives.
REASONS = [('मृत', 'dead'), ('स्', 'shifted'), ('अनुप', 'absent'), ('पहले', 'already_enrolled')]


def reason_code(v):
    v = v.split('\n')[0].replace('\u200d', '').strip()
    for prefix, code in REASONS:
        if v.startswith(prefix):
            return code
    return 'other'


def sex_code(v):
    v = v.strip().upper()
    return v if v in ('F', 'M', 'T') else 'unknown'


def renormalise():
    """Rewrite the two count files with the codes above (no stream needed)."""
    for name, rkey in (('reasons_by_ac.csv.gz', 1), ('reasons_by_booth.csv.gz', 2)):
        path = os.path.join(RAW, name)
        with gzip.open(path, 'rt', encoding='utf-8') as f:
            rows = list(csv.reader(f))
        head, cnt = rows[0], collections.Counter()
        si = head.index('sex')
        for r in rows[1:]:
            r[rkey] = reason_code(r[rkey])
            r[si] = sex_code(r[si])
            cnt[tuple(r[:-1])] += int(r[-1])
        with gzip.open(path, 'wt', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(head)
            for k in sorted(cnt):
                w.writerow(list(k) + [cnt[k]])


def main():
    csv.field_size_limit(10 ** 7)
    rd = csv.reader(io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8-sig', errors='replace', newline=''))
    head = next(rd)
    col = {h.strip(): i for i, h in enumerate(head)}
    def find(*keys):
        for h, i in col.items():
            if any(k in h for k in keys):
                return i
        raise SystemExit('column not found: %s in %s' % (keys, list(col)))
    i_age, i_sex, i_reason = find('आयु'), find('लिंग'), find('कारण')
    i_ac, i_old = col['ac_number'], find('पुराना भाग')
    by_ac, by_booth = collections.Counter(), collections.Counter()
    values = collections.Counter()
    n = 0
    for r in rd:
        if len(r) <= max(i_age, i_sex, i_reason, i_ac, i_old):
            values[('short row', len(r))] += 1
            continue
        reason, sex = reason_code(r[i_reason]), sex_code(r[i_sex])
        values[('reason', reason)] += 1
        values[('sex', sex)] += 1
        ac = r[i_ac].strip()
        by_ac[(ac, reason, sex, band(r[i_age]))] += 1
        by_booth[(ac, r[i_old].strip(), reason, sex)] += 1
        n += 1
        if n % 500000 == 0:
            print('rows', n, file=sys.stderr, flush=True)
    for name, cnt, cols in (('reasons_by_ac.csv.gz', by_ac, ['ac', 'reason', 'sex', 'age_band', 'count']),
                            ('reasons_by_booth.csv.gz', by_booth, ['ac', 'jan_part', 'reason', 'sex', 'count'])):
        with gzip.open(os.path.join(RAW, name), 'wt', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(cols)
            for k in sorted(cnt):
                w.writerow(list(k) + [cnt[k]])
    print('rows', n, file=sys.stderr)
    for k, v in sorted(values.items(), key=lambda kv: -kv[1])[:40]:
        print(k, v, file=sys.stderr)


if __name__ == '__main__':
    renormalise() if '--renormalise' in sys.argv else main()
