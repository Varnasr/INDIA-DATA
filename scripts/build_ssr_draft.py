#!/usr/bin/env python3
"""Write data/india/ssr_draft.json, which the pages read to show the draft
rolls of the special summary revisions.

    python3 scripts/build_ssr_draft.py           # write it
    python3 scripts/build_ssr_draft.py --check   # fail if it is stale

One entry for every state and union territory a summary revision covers, from
the "ssr" blocks of data/india/process.json (scripts/add_draft.py, schedules()),
with the draft the order set. A state whose draft is recorded in
data/india/raw/ssr_draft.csv carries its figures, its source and the note
written beside it. The change from the final roll of the intensive revision is
the draft less the roll the row records as its base, and is left out where the
row has no base. Whether a draft is late is decided in the browser from the
date, so the file does not change with the day.
"""
import csv
import json
import os
import sys
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import add_draft  # noqa: E402

OUT = os.path.join(ROOT, 'data', 'india', 'ssr_draft.json')


def num(v):
    return int(v) if v not in (None, '') else None


def build():
    sched = add_draft.schedules()
    rec = {}
    for r in add_draft.rows(add_draft.DRAFT_CSV):
        s = sched.get(r['state'])
        # only the draft of the revision that now governs the state is shown
        if s and r['order_date'] == s['order_date']:
            rec[r['state']] = r
    out = []
    for st in sorted(sched):
        s = sched[st]
        e = {'state': st, 'order_date': s['order_date'], 'due': s['draft'], 'claims_end': s['claims_end'], 'final_due': s['final']}
        r = rec.get(st)
        if r:
            n, base = int(r['electors']), num(r['base'])
            host = urlparse(r['source_url']).hostname or ''
            e['draft'] = {
                'date': r['draft_date'], 'electors': n,
                'men': num(r['men']), 'women': num(r['women']), 'third': num(r['third']), 'service': num(r['service']),
                'added': num(r['added']), 'deleted': num(r['deleted']),
                'base': base, 'base_date': r['base_date'] or None,
                'change': n - base if base is not None else None,
                'figures': r['figures'], 'press': r['source'] != 'primary',
                'url': r['source_url'], 'site': host[4:] if host.startswith('www.') else host,
                'note': r['note'] or None}
        out.append(e)
    return {'about': 'The draft rolls of the special summary revisions with 1 January 2027 as the qualifying date, from data/india/raw/ssr_draft.csv. Written by scripts/build_ssr_draft.py.',
            'states': out}


def text():
    return json.dumps(build(), ensure_ascii=False, indent=1, sort_keys=True) + '\n'


if __name__ == '__main__':
    new = text()
    old = open(OUT, encoding='utf-8').read() if os.path.exists(OUT) else None
    if '--check' in sys.argv:
        if old != new:
            sys.exit('STALE: data/india/ssr_draft.json, run python3 scripts/build_ssr_draft.py')
        print('OK: data/india/ssr_draft.json is current')
    else:
        if old != new:
            open(OUT, 'w', encoding='utf-8').write(new)
        print('wrote data/india/ssr_draft.json' if old != new else 'data/india/ssr_draft.json unchanged')
