#!/usr/bin/env python3
"""Record a state's draft roll in a special summary revision, check it, and
keep it in data/india/raw/ssr_draft.csv.

    python3 scripts/add_draft.py --due                          # every state with a summary-revision draft, and whether it is in
    python3 scripts/add_draft.py --json draft.json --dry-run    # validate and show the diff, write nothing
    python3 scripts/add_draft.py --json draft.json              # write the row and run check_data.py

The summary revisions are the ones data/india/process.json carries in a
timeline step's "ssr" block (the 17 states of 15 October 2026, West Bengal's
later dates of 28 October, the six of 4 November). A later block naming a
state replaces an earlier one, so West Bengal's draft is due on 23 November.

The input, as JSON (any key may also be given on the command line, with
dashes for underscores, and the command line wins):

    {"state": "Uttar Pradesh",            # as in data/india/raw/states.csv
     "draft_date": "2026-11-12",          # the day the draft roll was published
     "electors": 133000000,               # general electors on the draft
     "men": ..., "women": ..., "third": ...,   # if given, they must add to electors
     "service": ...,                      # service electors reported beside them, if any
     "added": ..., "deleted": ...,        # names added and deleted since the last final roll, if the source gives them
     "figures": "exact",                  # exact | rounded (lakh) | total (only the total was published)
     "source": "Chief Electoral Officer, Uttar Pradesh, press note of 12 November 2026 on the draft roll",
     "source_url": "https://ceouttarpradesh.nic.in/...",
     "source_kind": "primary",            # primary | press (default: primary for an official site or a CEO's own account)
     "note": "..."}                       # required unless figures is exact

The row records, beside the draft, the roll it follows: the final roll of
the intensive revision from data/india/raw/final.csv, where there is one.
The change between the two is printed, never added to any figure the pages
show. Nothing on the site reads the file yet: the pages that will show the
summary revision are to be written once the first drafts are in hand.
"""
import argparse
import csv
import datetime
import difflib
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from add_final import official, ind, long_date, today_ist  # noqa: E402

P = lambda *p: os.path.join(ROOT, *p)
DRAFT_CSV = P('data', 'india', 'raw', 'ssr_draft.csv')
FINAL_CSV = P('data', 'india', 'raw', 'final.csv')
STATES_CSV = P('data', 'india', 'raw', 'states.csv')
PROCESS = P('data', 'india', 'process.json')
HEAD = ['state', 'order_date', 'qualifying', 'draft_date', 'electors', 'men', 'women', 'third', 'service',
        'added', 'deleted', 'base', 'base_date', 'figures', 'source', 'source_url', 'note']
FIGS = ('exact', 'rounded', 'total')
INT_KEYS = ('electors', 'men', 'women', 'third', 'service', 'added', 'deleted')
TEXT_KEYS = ('state', 'draft_date', 'figures', 'source', 'source_url', 'source_kind', 'note')
# a draft this far from the final roll before it is printed as a warning, to be read against the source
WARN_SHARE = 0.03


def schedules(process=None):
    """State -> the summary-revision schedule that governs it: the ssr block
    of the latest timeline step naming it, with the step's date as the order."""
    D = process or json.load(open(PROCESS, encoding='utf-8'))
    out = {}
    for t in sorted(D['timeline'], key=lambda t: t['date']):
        s = t.get('ssr')
        if not s:
            continue
        for st in s['states']:
            out[st] = dict(s, order_date=t['date'], title=t['title'])
    return out


def rows(path):
    if not os.path.exists(path):
        return []
    return list(csv.DictReader(open(path, encoding='utf-8')))


def base_roll(st):
    """The roll a summary-revision draft follows: the intensive revision's
    final roll where final.csv has one, else None."""
    r = next((r for r in rows(FINAL_CSV) if r['state'] == st), None)
    if r and r['electors_final']:
        return int(r['electors_final']), r['final_date']
    return None, None


def read_input(a):
    x = {}
    if a.json:
        x.update(json.load(open(a.json, encoding='utf-8')))
    for k in INT_KEYS + TEXT_KEYS:
        v = getattr(a, k)
        if v is not None:
            x[k] = v
    for k in INT_KEYS:
        if x.get(k) in ('', None):
            x[k] = None
        elif not isinstance(x[k], int):
            try:
                x[k] = int(str(x[k]).replace(',', ''))
            except ValueError:
                raise SystemExit('%s must be a whole number, got %r' % (k, x[k]))
    unknown = set(x) - set(INT_KEYS) - set(TEXT_KEYS)
    if unknown:
        raise SystemExit('unknown fields in the input: %s' % ', '.join(sorted(unknown)))
    return x


def validate(x, replace):
    """Errors stop the run; warnings are printed and the run goes on."""
    err, warn = [], []
    st = x.get('state')
    known = {r['state'] for r in rows(STATES_CSV)}
    S = schedules()
    if st not in known:
        return ['%r is not a state in data/india/raw/states.csv' % st], warn
    if st not in S:
        return ['%s is in no summary revision that data/india/process.json records. Add the Commission\'s order as a timeline step with an ssr block first' % st], warn
    s = S[st]
    x['_order'], x['_qualifying'], x['_due'] = s['order_date'], s['qualifying'], s['draft']
    for k in INT_KEYS:
        if x.get(k) is not None and x[k] < 0:
            err.append('%s is below zero' % k)
    n = x.get('electors')
    if not n or n <= 0:
        err.append('electors is required and must be above zero')
    try:
        datetime.date.fromisoformat(x.get('draft_date') or '')
    except ValueError:
        err.append('draft_date must be YYYY-MM-DD')
    else:
        if x['draft_date'] < s['order_date']:
            err.append('draft_date %s is before the order of %s' % (x['draft_date'], s['order_date']))
        if x['draft_date'] > today_ist():
            err.append('draft_date %s is after today (%s)' % (x['draft_date'], today_ist()))
        if x['draft_date'] != s['draft']:
            warn.append('the schedule (%s) puts the draft on %s and the input on %s. If the date moved, record the move in process.json as well'
                        % (s['title'], s['draft'], x['draft_date']))
    fig = x.get('figures')
    if fig not in FIGS:
        err.append('figures must be one of %s' % ', '.join(FIGS))
    if not x.get('source'):
        err.append('source (the title of the document or report) is required')
    url = x.get('source_url') or ''
    if not re.match(r'https?://', url):
        err.append('source_url must be an http or https address')
    elif not official(url):
        warn.append('the source is not a Chief Electoral Officer\'s or the Commission\'s site or account. Prefer the CEO\'s own note, and mark it press')
    if x.get('source_kind') is None:
        x['source_kind'] = 'primary' if url and official(url) else 'press'
    if x['source_kind'] not in ('primary', 'press'):
        err.append('source_kind must be primary or press')
    if x['source_kind'] == 'primary' and url and not official(url):
        warn.append('source_kind is primary and the address is not an official one')
    if fig in ('rounded', 'total') and not x.get('note'):
        err.append('figures %s needs a note saying what was and was not published' % fig)
    if err:
        return err, warn
    sex = [x.get(k) for k in ('men', 'women', 'third')]
    if any(v is not None for v in sex):
        if any(v is None for v in sex):
            err.append('give men, women and third together, or none of them')
        elif fig == 'exact' and sum(sex) != n:
            err.append('men, women and third add to %s, and electors is %s. electors is the general electors, and service electors go in service' % (ind(sum(sex)), ind(n)))
        elif fig == 'rounded' and abs(sum(sex) - n) > 0.001 * n:
            err.append('men, women and third add to %s, more than 0.1 per cent from electors (%s)' % (ind(sum(sex)), ind(n)))
    base, base_date = base_roll(st)
    x['_base'], x['_base_date'] = base, base_date
    if base is None:
        warn.append('%s has no final roll of the intensive revision in final.csv, so the draft is recorded with nothing to set it against' % st)
    else:
        if x['draft_date'] < base_date:
            err.append('draft_date %s is before the final roll of %s it follows' % (x['draft_date'], base_date))
        if abs(n - base) > WARN_SHARE * base:
            warn.append('the draft (%s) is %.1f per cent %s the final roll of %s (%s). Read the figure against the source again'
                        % (ind(n), abs(100.0 * (n - base) / base), 'above' if n > base else 'below', long_date(base_date), ind(base)))
        if x.get('added') is not None and x.get('deleted') is not None:
            gap = base + x['added'] - x['deleted'] - n
            tol = 0 if fig == 'exact' else 0.001 * n
            if abs(gap) > tol:
                warn.append('the final roll %s plus %s added less %s deleted is %s, and the draft is %s, %s apart. The source may count from another roll; say so in the note'
                            % (ind(base), ind(x['added']), ind(x['deleted']), ind(base + x['added'] - x['deleted']), ind(n), ind(abs(gap))))
    if any(r['state'] == st and r['order_date'] == s['order_date'] for r in rows(DRAFT_CSV)) and not replace:
        err.append('%s already has a draft for this summary revision in ssr_draft.csv. Pass --replace to rewrite it, and add a corrections entry if a figure changes' % st)
    return err, warn


def new_csv(x):
    text = open(DRAFT_CSV, encoding='utf-8', newline='').read() if os.path.exists(DRAFT_CSV) else ','.join(HEAD) + '\n'
    rs = list(csv.reader(io.StringIO(text)))
    assert rs[0] == HEAD, 'ssr_draft.csv has columns this script does not know: %s' % rs[0]
    val = {'state': x['state'], 'order_date': x['_order'], 'qualifying': x['_qualifying'], 'draft_date': x['draft_date'],
           'electors': x['electors'], 'men': x.get('men'), 'women': x.get('women'), 'third': x.get('third'),
           'service': x.get('service'), 'added': x.get('added'), 'deleted': x.get('deleted'),
           'base': x['_base'], 'base_date': x['_base_date'], 'figures': x['figures'],
           'source': x['source_kind'], 'source_url': x['source_url'], 'note': x.get('note') or ''}
    row = ['' if val[k] is None else str(val[k]) for k in HEAD]
    at = [i for i, r in enumerate(rs) if i and r and r[0] == x['state'] and r[1] == x['_order']]
    if at:
        rs[at[0]] = row
    else:
        rs.append(row)
    b = io.StringIO()
    csv.writer(b, lineterminator='\n').writerows(rs)
    return b.getvalue()


def due():
    t = today_ist()
    have = {(r['state'], r['order_date']) for r in rows(DRAFT_CSV)}
    out = []
    for st, s in schedules().items():
        got = (st, s['order_date']) in have
        what = 'recorded' if got else 'OVERDUE' if s['draft'] < t else 'due today' if s['draft'] == t else 'due'
        out.append((s['draft'], what, st))
    for d, what, st in sorted(out):
        print('%-12s %-10s %s' % (d, what, st))


def todo(x):
    st, n, d = x['state'], x['electors'], x['draft_date']
    print('\n' + '=' * 72 + '\nLEFT TO DO BY HAND for %s\n' % st)
    rel = ''
    if x['_base'] is not None:
        ch = n - x['_base']
        rel = ' That is %s %s the final roll of the intensive revision on %s.' % (ind(abs(ch)), 'more than' if ch >= 0 else 'fewer than', long_date(x['_base_date']))
    sex = ' It holds %s men, %s women and %s third gender electors.' % (ind(x['men']), ind(x['women']), ind(x['third'])) if x.get('men') is not None else ''
    line = '%s: the draft roll of the summary revision, published on %s, has %s electors.%s%s' % (st, long_date(d), ind(n), rel, sex)
    print('1. What\'s New. data/updates.json is not written by this script. A drafted line, to be read against the source:')
    print('   ' + line)
    print('2. Have an independent second reader open %s and check every figure in the row.' % x['source_url'])
    print('3. The state\'s "what to do now" page changes stage by itself from the schedule. Read it at 390 wide on the day.')
    print('4. Commit the row, open the pull request, merge once CI is green. It goes live at the 20:00 IST publish unless the owner says "publish".')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--json')
    for k in INT_KEYS + TEXT_KEYS:
        ap.add_argument('--' + k.replace('_', '-'), dest=k)
    ap.add_argument('--dry-run', action='store_true', help='validate and show the diff, and write nothing')
    ap.add_argument('--replace', action='store_true', help='rewrite a draft already recorded')
    ap.add_argument('--no-check', action='store_true', help='write the row and skip check_data.py')
    ap.add_argument('--due', action='store_true', help='list every summary-revision draft, with its date and whether it is recorded')
    a = ap.parse_args()
    if a.due:
        due()
        return
    x = read_input(a)
    err, warn = validate(x, a.replace)
    for w in warn:
        print('WARNING: ' + w)
    if err:
        for e in err:
            print('REFUSED: ' + e)
        sys.exit(1)
    old = open(DRAFT_CSV, encoding='utf-8', newline='').read() if os.path.exists(DRAFT_CSV) else ''
    new = new_csv(x)
    rel = os.path.relpath(DRAFT_CSV, ROOT)
    print(''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), 'a/' + rel, 'b/' + rel, n=1)))
    print('%s: the summary-revision draft of %s, %s electors (%s), source %s. %s.' % (
        x['state'], x['draft_date'], ind(x['electors']), x['figures'], x['source_kind'], 'Would write' if a.dry_run else 'Written'))
    if a.dry_run:
        print('DRY RUN: nothing written.')
        todo(x)
        return
    open(DRAFT_CSV, 'w', encoding='utf-8', newline='').write(new)
    ok = True
    if not a.no_check:
        r = subprocess.run([sys.executable, os.path.join('scripts', 'check_data.py')], cwd=ROOT, capture_output=True, text=True)
        lines = (r.stdout + r.stderr).strip().splitlines()
        print('\n'.join([ln for ln in lines if 'FAIL' in ln] + lines[-2:]))
        ok = r.returncode == 0
    todo(x)
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
