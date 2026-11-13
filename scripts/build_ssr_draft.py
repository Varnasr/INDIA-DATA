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

The special campaign days, on which booth level officers sit at the polling
stations to take claims, come from data/india/raw/ssr_campaign.json, two
readings each. The Commission left them to each Chief Electoral Officer, so a
state has them only where a source gives them, and a source that speaks for
one district is kept to that district. The build stops on a day outside the
state's claims window or a state no summary revision covers.
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
CAMPAIGN = os.path.join(ROOT, 'data', 'india', 'raw', 'ssr_campaign.json')


def campaign(sched):
    with open(CAMPAIGN, encoding='utf-8') as fh:
        rows = json.load(fh)['days']
    out = {}
    for c in rows:
        st = c['state']
        if st not in sched:
            raise SystemExit('FAIL - ssr_campaign.json: %s is in no summary revision' % st)
        if st in out:
            raise SystemExit('FAIL - ssr_campaign.json: %s is there twice' % st)
        s = sched[st]
        days = sorted(c['days'])
        if not days or days != sorted(set(days)):
            raise SystemExit('FAIL - ssr_campaign.json: %s has no days, or a day twice' % st)
        for d in days:
            if not (s['draft'] <= d <= s['claims_end']):
                raise SystemExit('FAIL - ssr_campaign.json: %s day %s is outside the claims window %s to %s' % (st, d, s['draft'], s['claims_end']))
        if c['scope'] not in ('state', 'district') or (c['scope'] == 'district') != bool(c.get('district')):
            raise SystemExit('FAIL - ssr_campaign.json: %s scope %r and district %r do not agree' % (st, c['scope'], c.get('district')))
        if c['kind'] not in ('primary', 'press') or (c['kind'] == 'press') != bool(c.get('by')):
            raise SystemExit('FAIL - ssr_campaign.json: %s kind %r needs an outlet in "by" exactly when it is press' % (st, c['kind']))
        if not c['url'].startswith('https://') or not c.get('quote'):
            raise SystemExit('FAIL - ssr_campaign.json: %s needs an https source and the quotation that gives the days' % st)
        out[st] = {'days': days, 'scope': c['scope'], 'district': c.get('district'), 'press': c['kind'] == 'press', 'by': c.get('by'), 'source': c['source'], 'url': c['url']}
    return out


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
    camp = campaign(sched)
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
        if st in camp:
            e['campaign'] = camp[st]
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
