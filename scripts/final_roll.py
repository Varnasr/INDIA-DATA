"""The final roll: when each state's is due, and the record of one that has
been published, for the states with an analysis of their own.

Used by scripts/add_final.py (which writes the record), by the builders of
the states with their own analysis (build_maharashtra.py, build_delhi.py,
build_telangana.py, build_karnataka.py), by build_site.py (the line saying
which roll a page's figures come from) and by check_data.py (a final roll
that is overdue and not recorded fails CI).

A state with its own analysis keeps its final roll in data/<folder>/raw/final.json:

    {"state": "Karnataka", "date": "2026-10-27", "electors": 45455689,
     "men": 22540493, "women": 22912355, "third": 2841, "service": 44322,
     "added": 1008000, "deleted": 188000, "withheld": null, "draft": 44635975,
     "figures": "rounded",
     "source": {"title": "...", "url": "https://...", "date": "2026-10-28", "primary": false},
     "note": "..."}

`electors` is the final roll of general electors, on the same footing as the
draft, and `service` the service electors reported beside it. `figures` is
`exact` (the draft plus those added less those deleted and withheld is the
final roll exactly), `rounded` (printed in lakh, within 0.1 per cent),
`net` (only the final roll, or the net change, was published) or `no` (the
published figures do not add up, and the note says how). Until a state's
final roll is published the file does not exist, and the builder writes its
summary with `final` set to null.
"""
import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYS = {'state', 'date', 'electors', 'men', 'women', 'third', 'service', 'added', 'deleted', 'withheld', 'draft',
        'figures', 'source', 'note'}
FIGURES = {'exact': 'exact', 'rounded': 'rounded', 'net': 'net only', 'no': 'no'}   # final.json -> final.csv `reconciles`
ROUNDED_TOLERANCE = 0.001   # as build_india.py allows a rounded final roll


def due(name, process=None):
    """The date a state's final roll is due, as build_site.py states it under
    every page: the final date of the state's latest schedule step in
    data/india/process.json, replaced by a later date reported in the press
    (reported_dates), the most recently reported one winning. None when no
    date is set."""
    P = process or json.load(open(os.path.join(ROOT, 'data', 'india', 'process.json'), encoding='utf-8'))
    sched = next((x for x in P['schedules'] if x['state'] == name), None)
    d = sched['steps'][-1].get('final') if sched else None
    moved = sorted((x for x in P.get('reported_dates', []) if x['state'] == name and x.get('final')), key=lambda x: x['date'])
    if moved:
        d = moved[-1]['final']
    return d


def read(folder):
    """data/<folder>/raw/final.json, or None while no final roll is recorded."""
    p = os.path.join(ROOT, 'data', folder, 'raw', 'final.json')
    if not os.path.exists(p):
        return None
    F = json.load(open(p, encoding='utf-8'))
    extra = set(F) - KEYS
    assert not extra, '%s: unknown fields %s' % (p, sorted(extra))
    return F


def draft_date(name):
    """The draft's date in data/india/raw/states.csv."""
    with open(os.path.join(ROOT, 'data', 'india', 'raw', 'states.csv'), encoding='utf-8') as fh:
        return next(r['draft_date'] for r in csv.DictReader(fh) if r['state'] == name)


def india_row(name):
    """The state's row in data/india/raw/final.csv, or None."""
    with open(os.path.join(ROOT, 'data', 'india', 'raw', 'final.csv'), encoding='utf-8') as fh:
        return next((r for r in csv.DictReader(fh) if r['state'] == name), None)


def block(F, name, before, draft, removed, draft_date):
    """The summary block a state page draws its final roll from, with every
    identity asserted. `before`, `draft`, `removed` and `draft_date` are the
    page's own figures for the roll before the revision, the draft and the
    names left off. Returns None while no final roll is recorded."""
    if F is None:
        # nothing recorded here, so nothing may be recorded in the All India table either
        assert india_row(name) is None, '%s has a final roll in data/india/raw/final.csv and none in its own raw/final.json' % name
        return None
    n = F['electors']
    assert F['state'] == name, 'final.json names %s' % F['state']
    assert isinstance(n, int) and n > 0, 'the final roll must be a count above zero'
    assert F['date'] >= draft_date, 'the final roll of %s is dated before the draft of %s' % (F['date'], draft_date)
    assert F['figures'] in FIGURES, 'figures must be one of %s' % sorted(FIGURES)
    for k in ('men', 'women', 'third', 'service', 'added', 'deleted', 'withheld', 'draft'):
        assert F.get(k) is None or (isinstance(F[k], int) and F[k] >= 0), '%s must be a count' % k
    sex = [F.get(k) for k in ('men', 'women', 'third')]
    if all(x is not None for x in sex):
        assert sum(sex) == n, 'men, women and third gender add to %d, and the final roll is %d' % (sum(sex), n)
    # The draft the final-roll source gives, where it gives one, must be the
    # page's draft within half a per cent, as build_india.py holds it.
    d0 = F.get('draft') if F.get('draft') is not None else draft
    assert abs(d0 - draft) <= 0.005 * draft, 'the final-roll source puts the draft at %d, the page at %d' % (d0, draft)
    if F['figures'] in ('exact', 'rounded'):
        assert F.get('added') is not None and F.get('deleted') is not None, 'an exact or rounded final roll needs the names added and deleted'
        gap = d0 + F['added'] - F['deleted'] - (F.get('withheld') or 0) - n
        tol = 0 if F['figures'] == 'exact' else ROUNDED_TOLERANCE * n
        assert abs(gap) <= tol, 'the draft plus those added less those deleted misses the final roll by %d' % gap
    else:
        assert F.get('note'), 'a final roll that does not reconcile needs a note saying why'
    s = F.get('source') or {}
    assert s.get('title') and str(s.get('url', '')).startswith('http') and isinstance(s.get('primary'), bool), 'the final roll needs a source'
    # the All India table carries the same final roll
    r = india_row(name)
    assert r is not None, '%s has a final roll in its raw/final.json and none in data/india/raw/final.csv (run scripts/add_final.py)' % name
    num = lambda v: int(v) if v not in ('', None) else None
    assert num(r['electors_final']) == n and r['final_date'] == F['date'], 'final.json and data/india/raw/final.csv disagree on the final roll'
    assert num(r['added_after_draft']) == F.get('added') and num(r['removed_after_draft']) == F.get('deleted'), \
        'final.json and data/india/raw/final.csv disagree on the names added or deleted'
    assert r['reconciles'] == FIGURES[F['figures']], 'final.json and data/india/raw/final.csv disagree on whether the figures add up'
    net = n - draft
    out = {
        'date': F['date'], 'electors': n, 'men': F.get('men'), 'women': F.get('women'), 'third': F.get('third'),
        'service': F.get('service'), 'with_service': n + F['service'] if F.get('service') is not None else None,
        'added': F.get('added'), 'deleted': F.get('deleted'), 'withheld': F.get('withheld'), 'figures': F['figures'],
        'net_after': net,
        'made_up_pct': round(100 * net / removed, 4) if removed else None,
        'net_fall': before - n,
        'net_per_100': round(100 * (before - n) / before, 4),
        'women_pct': round(100 * F['women'] / n, 4) if all(x is not None for x in sex) else None,
        'source': {'title': s['title'], 'url': s['url'], 'date': s.get('date'), 'primary': s['primary']},
    }
    return out
