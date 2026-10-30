"""Notices: electors kept on the draft roll but sent a notice, state by state.

Reads data/india/raw/notices/notices.csv (see SOURCES.md there) and
data/india/states.json, and writes data/india/notices.json and the
downloadable data/india/notices.csv.

    python3 scripts/build_notices.py           # write
    python3 scripts/build_notices.py --check   # fail if the output is stale

Two lists produced the notices. "No mapping" is an elector who could not be
linked to the roll of the last intensive revision (2002 to 2006). The "logical
discrepancy" list is the Commission's list of mismatches in names, ages and
family links. Most states published one total and some the two lists; a few
published one list only. The raw file keeps every figure found, with its
source, and several states have more than one. The rules for choosing, in
order:

- the total is a published total of notices, never a sum this build makes,
  except where a source gives the two lists and no total (marked `sum`);
- a total that equals the two lists from the same source is preferred, then a
  primary source, then the latest report, then an exact figure over a
  rounded one;
- the two lists are taken from one source, the total's own where it has them;
- a state with one list only gets no total and stays out of the chart.

Figures are per 100 electors on the draft roll, because a notice goes to an
elector who is on it.
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'india', 'raw', 'notices', 'notices.csv')
OUT = os.path.join(ROOT, 'data', 'india')
CHECK = '--check' in sys.argv

# reported as expected or as a target rather than as notices issued
NOT_ISSUED = {('Nagaland', 'all_notices'),
              # an early software flag on the enumeration forms, before any
              # notice was issued; the notices themselves were not reported
              ('Madhya Pradesh', 'discrepancy')}


def series(R):
    """The progress of the notice stage: one figure per category and date."""
    best = {}
    for r in R:
        if r['category'] not in ('all_notices', 'hearings_held', 'deleted_after_notice'):
            continue
        k = (r['date'], r['category'])
        rank = (r['kind'] == 'primary', r['rounded'] == 'no')
        if k not in best or rank > best[k][0]:
            best[k] = (rank, r)
    return [{'date': r['date'], 'category': r['category'], 'count': r['count'], 'rounded': r['rounded'] == 'yes',
             'kind': r['kind'], 'source_url': r['source_url']}
            for _rank, r in (best[k] for k in sorted(best))]


def main():
    rows = list(csv.DictReader(open(RAW, encoding='utf-8')))
    for r in rows:
        r['count'] = int(r['count'])
        assert r['kind'] in ('primary', 'press') and r['source_url'].startswith('http') and r['quote'].strip(), r
        assert r['category'] in ('discrepancy', 'no_mapping', 'all_notices', 'hearings_held', 'deleted_after_notice'), r
    S = {s['state']: s for s in json.load(open(os.path.join(OUT, 'states.json'), encoding='utf-8'))['states']}
    out = []
    for st in sorted({r['state'] for r in rows}):
        if st not in S:
            continue  # "All phase 2 states" and the like
        R = [r for r in rows if r['state'] == st and (st, r['category']) not in NOT_ISSUED]
        by = lambda c: [r for r in R if r['category'] == c]
        nm, dc, tot = by('no_mapping'), by('discrepancy'), by('all_notices')
        pairs = [(a, b) for a in nm for b in dc if a['source_url'] == b['source_url']]

        def score(t):
            same = any(a['count'] + b['count'] == t['count'] and a['source_url'] == t['source_url'] for a, b in pairs)
            return (same, t['kind'] == 'primary', t['date'], t['rounded'] == 'no')
        total = max(tot, key=score) if tot else None
        how = 'published' if total else None
        pair = None
        if pairs:
            own = [p for p in pairs if total and p[0]['source_url'] == total['source_url']]
            pair = (own or sorted(pairs, key=lambda p: p[0]['date']))[-1]
        if not total and pair:
            total = {'count': pair[0]['count'] + pair[1]['count'], 'kind': pair[0]['kind'], 'rounded': 'yes' if 'yes' in (pair[0]['rounded'], pair[1]['rounded']) else 'no',
                     'date': pair[0]['date'], 'source_url': pair[0]['source_url'], 'note': pair[0]['note']}
            how = 'sum'
        s = S[st]
        # no roll before the revision published (Chandigarh): no rate
        draft = s['electors_before'] - s['removed'] if s['electors_before'] and s['removed'] is not None else None
        rec = {'state': st, 'phase': s['phase'], 'draft': draft,
               'notices': total['count'] if total else None, 'how': how,
               'per_100': round(100 * total['count'] / draft, 1) if total and draft else None,
               'kind': total['kind'] if total else None, 'rounded': total['rounded'] == 'yes' if total else None,
               'date': total['date'] if total else None, 'source_url': total['source_url'] if total else None,
               'no_mapping': pair[0]['count'] if pair else (nm[0]['count'] if len(nm) == 1 else None),
               'discrepancy': pair[1]['count'] if pair else (dc[0]['count'] if len(dc) == 1 else None),
               'lists_same_source': bool(pair and total and pair[0]['source_url'] == total['source_url']),
               'lists_source': pair[0]['source_url'] if pair else ((nm or dc)[0]['source_url'] if len(nm) + len(dc) == 1 else None),
               'deleted_after_notice': max(by('deleted_after_notice'), key=lambda r: r['date'])['count'] if by('deleted_after_notice') else None,
               'deleted_kind': max(by('deleted_after_notice'), key=lambda r: r['date'])['kind'] if by('deleted_after_notice') else None,
               'other_figures': len(R) - (1 if total and how == 'published' else 0) - (2 if pair else 0),
               # every dated count of notices sent, hearings held and names
               # deleted after a notice, in date order, so a page can show
               # how the notice stage moved; one figure per category a day,
               # a primary source preferred, then an exact figure
               'series': series(R)}
        # the two lists can overlap, so together they may exceed the total,
        # but a total far above the two lists would mean a mismatched pair
        if pair and total and how == 'published' and pair[0]['source_url'] == total['source_url']:
            assert total['count'] <= 1.1 * (pair[0]['count'] + pair[1]['count']), st
        out.append(rec)
    out.sort(key=lambda r: -(r['per_100'] or -1))
    cov = [r for r in out if r['notices'] and r['draft']]
    summary = {'states': out, 'with_total': len(cov), 'primary': sum(r['kind'] == 'primary' for r in cov),
               'notices_total': sum(r['notices'] for r in cov), 'draft_total': sum(r['draft'] for r in cov)}
    summary['per_100'] = round(100 * summary['notices_total'] / summary['draft_total'], 1)
    j = json.dumps(summary, ensure_ascii=False, indent=1) + '\n'
    buf = io.StringIO()
    cols = ['state', 'phase', 'draft', 'notices', 'how', 'per_100', 'kind', 'rounded', 'date', 'no_mapping', 'discrepancy', 'deleted_after_notice', 'source_url', 'lists_source']
    w = csv.writer(buf, lineterminator='\n'); w.writerow(cols)
    for r in out:
        w.writerow(['' if r[c] is None else r[c] for c in cols])
    files = {os.path.join(OUT, 'notices.json'): j, os.path.join(OUT, 'notices.csv'): buf.getvalue()}
    if CHECK:
        stale = [p for p, t in files.items() if not os.path.exists(p) or open(p, encoding='utf-8').read() != t]
        assert not stale, 'stale: ' + ', '.join(stale)
        print('OK: data/india/notices matches its raw table')
        return
    for p, t in files.items():
        open(p, 'w', encoding='utf-8').write(t)
    print('wrote data/india/notices: %d states with a total, %d primary, %.1f per 100 on the draft' % (summary['with_total'], summary['primary'], summary['per_100']))


if __name__ == '__main__':
    main()
