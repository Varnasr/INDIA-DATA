#!/usr/bin/env python3
"""Record a state's final roll in one command, check it, and rebuild what
depends on it.

    python3 scripts/add_final.py --json final.json --dry-run   # validate and show the diff, write nothing
    python3 scripts/add_final.py --json final.json             # write, rebuild, run the checks
    python3 scripts/add_final.py --state Haryana --final-date 2026-11-30 --electors-final 17500000 \\
        --added 300000 --deleted 71361 --figures exact --source "Chief Electoral Officer, Haryana, press note of 30 November 2026 on the final roll" \\
        --source-url https://ceoharyana.gov.in/... --dry-run

The input, as JSON (any key may also be given on the command line, with
dashes for underscores, and the command line wins):

    {"state": "Maharashtra",              # as in data/india/raw/states.csv
     "final_date": "2026-11-30",          # the day the final roll was published
     "electors_final": 81234567,          # general electors, the draft's footing
     "men": ..., "women": ..., "third": ...,   # if given, they must add to electors_final
     "service": ...,                      # service electors reported beside them, if any
     "added": ..., "deleted": ...,        # names added and deleted after the draft
     "withheld": ...,                     # names kept off the final roll while undecided, if any
     "electors_draft": ...,               # the draft as the final-roll source prints it
                                          # (default: the roll before less the names left off)
     "figures": "exact",                  # exact | rounded (lakh) | net (only the total or the net
                                          # change was published) | no (published, does not add up)
     "source": "Chief Electoral Officer, Maharashtra, press note of 30 November 2026 on the final roll",
     "source_url": "https://ceoelection.maharashtra.gov.in/...",
     "source_date": "2026-11-30",         # default: final_date
     "source_kind": "primary",            # primary | press (default: primary for an official
                                          # site or a Chief Electoral Officer's own account)
     "label": "...",                      # the schedule step's label (default from the source)
     "note": "..."}                       # the final.csv note; required unless figures is exact

What it writes, the way the earlier final rolls were written:

  * data/india/raw/final.csv, the state's row (appended; --replace to
    rewrite a row already there, in place);
  * for a state on the shared page, data/<slug>/raw/normal.json: the final
    date, the figures after the draft, the figures by sex, the source and a
    note sentence (scripts/state_schema.md);
  * for a state with its own analysis (Maharashtra, Delhi, Telangana,
    Karnataka), data/<folder>/raw/final.json (scripts/final_roll.py), which its
    builder reads and checks against final.csv;
  * data/india/process.json: a schedule step marked as published, and as_of
    moved up to the final date if it is earlier.

It never writes data/updates.json or the front page: it prints a drafted
What's New line and the other things left to do by hand. Then it runs the
data builders, the site build and every check, in the order CLAUDE.md gives,
and stops at the first builder that fails. --no-build stops after writing;
--no-site runs the data builders and data checks only.
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
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import final_roll  # noqa: E402

P = lambda *p: os.path.join(ROOT, *p)
FINAL_CSV = P('data', 'india', 'raw', 'final.csv')
STATES_CSV = P('data', 'india', 'raw', 'states.csv')
PROCESS = P('data', 'india', 'process.json')
# states with an analysis of their own: data folder, builder, page, place id
OWN = {
    'Maharashtra': ('maharashtra', 'build_maharashtra.py', 'maharashtra/', 'mh'),
    'Delhi': ('delhi', 'build_delhi.py', 'delhi/', 'dl'),
    'Telangana': ('hyderabad', 'build_telangana.py', 'hyderabad/telangana/', 'hyd'),
    'Karnataka': ('karnataka', 'build_karnataka.py', 'karnataka/', 'ka'),
}
FIGS = ('exact', 'rounded', 'net', 'no')
INT_KEYS = ('electors_final', 'men', 'women', 'third', 'service', 'added', 'deleted', 'withheld', 'electors_draft')
TEXT_KEYS = ('state', 'final_date', 'figures', 'source', 'source_url', 'source_date', 'source_kind', 'label', 'note')
# Chief Electoral Officers' own accounts on X, as the repository cites them
CEO_HANDLES = {'ceopuducherry', 'andaman_admin', 'ceoandhra', 'ceochandigarh', 'ceo_goa', 'ceodelhioffice', 'ceo_telangana', 'odishaceo'}
MONTHS = 'January February March April May June July August September October November December'.split()


def today_ist():
    return (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5, minutes=30)).date().isoformat()


def ind(n):
    """Indian digit grouping, as the site prints counts: 4,55,00,011."""
    s, neg = str(abs(int(n))), n < 0
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        s = ','.join(([head] if head else []) + parts) + ',' + tail
    return ('-' if neg else '') + s


def long_date(iso):
    return '%d %s %s' % (int(iso[8:]), MONTHS[int(iso[5:7]) - 1], iso[:4])


def official(url):
    """A Chief Electoral Officer's or the Commission's own site or account."""
    u = urlparse(url)
    host = u.netloc.lower().split(':')[0]
    if host.endswith(('.gov.in', '.nic.in')) or host in ('eci.gov.in', 'www.eci.gov.in'):
        return True
    if host in ('x.com', 'twitter.com', 'www.x.com', 'www.twitter.com'):
        handle = u.path.strip('/').split('/')[0].lower()
        return handle in CEO_HANDLES
    return False


def shared_states():
    """State name -> folder, for the states on the shared page."""
    import build_states
    out = {}
    for _pid, slug in build_states.STATES:
        p = P('data', slug, 'raw', 'normal.json')
        if os.path.exists(p):
            out[json.load(open(p, encoding='utf-8'))['state']] = slug
    return out


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
    rows = {r['state']: r for r in csv.DictReader(open(STATES_CSV, encoding='utf-8'))}
    st = x.get('state')
    if st not in rows:
        return ['%r is not a state in data/india/raw/states.csv' % st], warn, None
    r = rows[st]
    if not r['removed'] or not r['electors_before']:
        return ['%s has no draft roll recorded in data/india/raw/states.csv, so it has no final roll to add' % st], warn, None
    before, removed = int(r['electors_before']), int(r['removed'])
    draft_here = before - removed
    if x.get('electors_draft') is None:
        x['electors_draft'] = draft_here
    for k in INT_KEYS:
        if x.get(k) is not None and x[k] < 0:
            err.append('%s is below zero' % k)
    n = x.get('electors_final')
    if not n or n <= 0:
        err.append('electors_final is required and must be above zero')
    try:
        datetime.date.fromisoformat(x.get('final_date') or '')
    except ValueError:
        err.append('final_date must be YYYY-MM-DD')
    else:
        if x['final_date'] < r['draft_date']:
            err.append('final_date %s is before the draft of %s' % (x['final_date'], r['draft_date']))
        if x['final_date'] > today_ist():
            err.append('final_date %s is after today (%s)' % (x['final_date'], today_ist()))
    if x.get('source_date') is None:
        x['source_date'] = x.get('final_date')
    fig = x.get('figures')
    if fig not in FIGS:
        err.append('figures must be one of %s' % ', '.join(FIGS))
    if not x.get('source'):
        err.append('source (the title of the document or report) is required')
    url = x.get('source_url') or ''
    if not re.match(r'https?://', url):
        err.append('source_url must be an http or https address')
    elif not official(url):
        warn.append('the source is not a Chief Electoral Officer\'s or the Commission\'s site or account (%s). Prefer the CEO\'s own note, and mark it press' % urlparse(url).netloc)
    if x.get('source_kind') is None:
        x['source_kind'] = 'primary' if url and official(url) else 'press'
    if x['source_kind'] not in ('primary', 'press'):
        err.append('source_kind must be primary or press')
    if x['source_kind'] == 'primary' and url and not official(url):
        warn.append('source_kind is primary and the address is not an official one')
    if err:
        return err, warn, r
    sex = [x.get(k) for k in ('men', 'women', 'third')]
    if any(v is not None for v in sex):
        if any(v is None for v in sex):
            err.append('give men, women and third together, or none of them')
        elif sum(sex) != n:
            err.append('men, women and third add to %s, and electors_final is %s. electors_final is the general electors, and service electors go in service' % (ind(sum(sex)), ind(n)))
    d0 = x['electors_draft']
    # the draft the final-roll source gives must agree with the draft here, as build_india.py holds it
    if d0 != draft_here:
        if abs(d0 - draft_here) > 0.005 * draft_here and r['figures'] != 'rounded':
            err.append('the source puts the draft at %s and data/india/raw/states.csv at %s, more than half a per cent apart' % (ind(d0), ind(draft_here)))
        else:
            warn.append('the source puts the draft at %s and data/india/raw/states.csv at %s, %s apart. The fall in the roll is measured from the roll before' % (ind(d0), ind(draft_here), ind(abs(d0 - draft_here))))
    if fig in ('exact', 'rounded'):
        if x.get('added') is None or x.get('deleted') is None:
            err.append('figures %s needs added and deleted. Use net when only the total was published' % fig)
        else:
            gap = d0 + x['added'] - x['deleted'] - (x.get('withheld') or 0) - n
            tol = 0 if fig == 'exact' else final_roll.ROUNDED_TOLERANCE * n
            if abs(gap) > tol:
                err.append('the draft %s plus %s added less %s deleted%s is %s, and the final roll is %s, %s apart. %s'
                           % (ind(d0), ind(x['added']), ind(x['deleted']), (' less %s withheld' % ind(x['withheld'])) if x.get('withheld') else '',
                              ind(d0 + x['added'] - x['deleted'] - (x.get('withheld') or 0)), ind(n), ind(abs(gap)),
                              'Use figures no, with a note saying so, if the source prints it this way.' if fig == 'exact' else 'That is more than 0.1 per cent.'))
    elif not x.get('note'):
        err.append('figures %s needs a note saying what was and was not published' % fig)
    if n and n > before:
        warn.append('the final roll is larger than the roll before the revision')
    if fig == 'exact' and x.get('withheld') and st in shared_states():
        warn.append('the shared page has no field for names withheld, so normal.json gets the net change and the final roll only')
    existing = final_roll.india_row(st)
    if existing and not replace:
        err.append('%s already has a final roll in data/india/raw/final.csv. Pass --replace to rewrite it, and add a corrections entry if a figure changes' % st)
    x['_before'], x['_removed'], x['_draft_date'] = before, removed, r['draft_date']
    x['_existing'] = existing
    return err, warn, r


# ---------------------------------------------------------------- writers
def new_final_csv(x):
    text = open(FINAL_CSV, encoding='utf-8', newline='').read()
    rows = list(csv.reader(io.StringIO(text)))
    head = rows[0]
    reconciles = final_roll.FIGURES[x['figures']]
    val = {'state': x['state'], 'electors_draft': x['electors_draft'], 'added_after_draft': x.get('added'),
           'removed_after_draft': x.get('deleted'), 'withheld': x.get('withheld'), 'electors_final': x['electors_final'],
           'final_date': x['final_date'], 'reconciles': reconciles, 'source': x['source_kind'], 'source_url': x['source_url'],
           'note': x.get('note') or ''}
    assert set(val) == set(head), 'final.csv has columns this script does not know: %s' % sorted(set(head) ^ set(val))
    row = ['' if val[k] is None else str(val[k]) for k in head]
    at = [i for i, r in enumerate(rows) if r and r[0] == x['state']]
    if at:
        rows[at[0]] = row
    else:
        rows.append(row)
    b = io.StringIO()
    csv.writer(b, lineterminator='\n').writerows(rows)
    return b.getvalue()


def new_normal(x, slug):
    p = P('data', slug, 'raw', 'normal.json')
    text = open(p, encoding='utf-8').read()
    N = json.loads(text)
    F = N['figures']
    primary = x['source_kind'] == 'primary'
    src = next((s for s in N['sources'] if s['url'] == x['source_url']), None)
    if src is None:
        ids = [int(s['id'][1:]) for s in N['sources'] if re.match(r's\d+$', s['id'])]
        src = {'id': 's%d' % (max(ids or [0]) + 1), 'title': x['source'], 'url': x['source_url'], 'date': x['source_date'], 'primary': primary}
        N['sources'].append(src)
    n = x['electors_final']
    draft = F['draft']['v'] if 'draft' in F else x['electors_draft']
    new = {}
    if x['figures'] == 'exact' and not x.get('withheld'):
        if 'draft' in F and F['draft']['v'] + x['added'] - x['deleted'] != n:
            raise SystemExit('normal.json puts the draft at %s, and with it the figures do not add to the final roll. Use figures no, or check the draft' % ind(F['draft']['v']))
        new.update(added_after=x['added'], removed_after=x['deleted'], net_after=x['added'] - x['deleted'], final=n)
    else:
        new.update(net_after=n - draft, final=n)
    if x.get('men') is not None:
        new.update(men_final=x['men'], women_final=x['women'], third_final=x['third'])
    # keys this run replaces: everything after the draft, so a figures flag
    # that changes on --replace leaves nothing stale behind
    for k in ('added_after', 'removed_after', 'net_after', 'final', 'men_final', 'women_final', 'third_final'):
        if k not in new:
            F.pop(k, None)
    out = {}
    tail = [k for k in F if k == 'notices']
    for k, v in F.items():
        if k in tail:
            continue
        out[k] = v
    for k, v in new.items():
        fig = {'v': v, 'src': src['id']}
        if not primary:
            fig['press'] = True
        out[k] = fig if k not in F else dict(F[k], **fig)
        if k in F and primary:
            out[k].pop('press', None)
    for k in tail:
        out[k] = F[k]
    N['figures'] = out
    N['dates']['final'] = x['final_date']
    # the method page's note, in the words the earlier final rolls used
    sex = (', %s men, %s women and %s third gender' % (ind(x['men']), ind(x['women']), ind(x['third']))) if x.get('men') is not None else ''
    net = n - draft
    rel = ('%s more than the draft' % ind(net)) if net > 0 else ('%s fewer than the draft' % ind(-net)) if net < 0 else 'the same as the draft'
    note = 'The final roll was published on %s with %s electors%s. That is %s and %s fewer than the roll before the revision.' % (
        long_date(x['final_date']), ind(n), sex, rel, ind(x['_before'] - n))
    # a note already giving this final roll (written by hand, as Meghalaya's) is left as it is
    if not any('with %s electors' % ind(n) in s for s in N.get('notes', []) if not s.startswith('The final roll was published on ')):
        N['notes'] = [s for s in N.get('notes', []) if not s.startswith('The final roll was published on ')] + [note]
    return p, json.dumps(N, ensure_ascii=False, indent=1) + ('\n' if text.endswith('\n') else ''), note


def new_own(x, folder):
    p = P('data', folder, 'raw', 'final.json')
    F = {'state': x['state'], 'date': x['final_date'], 'electors': x['electors_final'],
         'men': x.get('men'), 'women': x.get('women'), 'third': x.get('third'), 'service': x.get('service'),
         'added': x.get('added'), 'deleted': x.get('deleted'), 'withheld': x.get('withheld'), 'draft': x['electors_draft'],
         'figures': x['figures'],
         'source': {'title': x['source'], 'url': x['source_url'], 'date': x['source_date'], 'primary': x['source_kind'] == 'primary'},
         'note': x.get('note') or ''}
    return p, json.dumps(F, ensure_ascii=False, indent=1) + '\n'


def _close(text, i):
    """Index of the bracket closing the one at text[i], skipping strings."""
    depth, j, ins = 0, i, False
    while j < len(text):
        c = text[j]
        if ins:
            if c == '\\':
                j += 1
            elif c == '"':
                ins = False
        elif c == '"':
            ins = True
        elif c in '[{':
            depth += 1
        elif c in ']}':
            depth -= 1
            if depth == 0:
                return j
        j += 1
    raise SystemExit('process.json: unbalanced brackets')


def new_process(x):
    """A schedule step marked as published, inserted as text so the rest of
    process.json keeps its hand-kept layout, and as_of moved up to the final
    date. The result is parsed back and compared with the intended data."""
    text = open(PROCESS, encoding='utf-8').read()
    D = json.loads(text)
    sched = next((s for s in D['schedules'] if s['state'] == x['state']), None)
    if sched is None:
        return text, None
    if any(s.get('kind') == 'published' and s.get('final') == x['final_date'] for s in sched['steps']):
        step = None
    else:
        # the draft and the claims period as the latest schedule that gives them
        steps = [s for s in sched['steps'] if s.get('kind') != 'published']
        draft = next((s['draft'] for s in reversed(steps) if s.get('draft')), None)
        claims = next((s['claims'] for s in reversed(steps) if s.get('claims')), None)
        label = x.get('label') or ('As published, ' + ('' if x['source_kind'] == 'primary' else 'reported in ') + x['source'])
        step = {'enum': None, 'draft': draft, 'claims': claims, 'notice': None, 'final': x['final_date'],
                'label': label, 'src': x['source_url'], 'kind': 'published'}
        i = text.index('"schedules": [')
        m = re.compile(r'"state": %s,' % re.escape(json.dumps(x['state'], ensure_ascii=False))).search(text, i)
        j = text.index('"steps": [', m.end()) + len('"steps": ')
        k = _close(text, j)
        ls = text.rindex('\n', 0, k)
        indent = text[ls + 1:k] + ' '
        body = '\n'.join(indent + ln for ln in json.dumps(step, ensure_ascii=False, indent=1).split('\n'))
        text = text[:ls] + ',\n' + body + text[ls:]
        sched['steps'].append(step)
    if x['final_date'] > D['as_of']:
        text = re.sub(r'^ "as_of": "\d{4}-\d\d-\d\d",$', ' "as_of": "%s",' % x['final_date'], text, count=1, flags=re.M)
        D['as_of'] = x['final_date']
    assert json.loads(text) == D, 'process.json: the edit did not give the intended data'
    return text, step


# ---------------------------------------------------------------- running
def run(cmd, env=None):
    print('\n$ ' + ' '.join(cmd), flush=True)
    r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
    lines = (r.stdout + r.stderr).strip().splitlines()
    tail = lines[-12:]
    # a failure reported early in a long run (check_data.py) is printed too
    early = [ln for ln in lines[:-12] if re.search(r'\bFAIL\b|Error|Traceback', ln)]
    print('\n'.join(early + (['...'] if early else []) + tail) if lines else '(no output)')
    return r.returncode == 0


def pipeline(x, kind, folder, no_site):
    py = sys.executable
    S = lambda name, *a: [py, os.path.join('scripts', name)] + list(a)
    data = [S('build_india.py')]
    data.append(S(OWN[x['state']][1]) if kind == 'own' else S('build_states.py', folder) if kind == 'shared' else None)
    data += [S('build_women.py'), S('build_margins.py'), S('build_notices.py'), S('build_downloads.py'),
             S('make_seat_pages.py'), S('make_district_pages.py'), S('make_embed_pages.py'), S('build_repository.py')]
    for c in [c for c in data if c]:
        if not run(c):
            print('\nSTOPPED: %s failed. Fix the input or the builder, then run this again with --replace.' % c[1])
            return False
    env = dict(os.environ)
    site = [S('build_site.py')]
    if os.environ.get('PLAYWRIGHT_CORE'):
        site.append(['node', os.path.join('scripts', 'i18n_collect.mjs')])
    else:
        print('\nPLAYWRIGHT_CORE is not set, so node scripts/i18n_collect.mjs is skipped. Set it and run it before build_i18n.py if a page string changed.')
    site += [S('build_i18n.py'), S('stamp.py'), S('build_site.py'), S('build_i18n.py'), S('stamp.py')]
    checks = [S('check_data.py')]
    if not no_site:
        for c in site:
            if not run(c, env):
                print('\nSTOPPED: %s failed.' % ' '.join(c[1:]))
                return False
        checks += [S('build_site.py', '--check'), S('stamp.py', '--check'), S('build_i18n.py', '--check'), S('check_i18n.py'),
                   S('check_writing.py'), S('check_contrast.py'), S('verify_bihar.py'), S('stage_site.py')]
    bad = [c for c in checks if not run(c, env)]
    print('\nCHECKS: %s' % ('all passed' if not bad else 'failed: ' + ', '.join(' '.join(c[1:]) for c in bad)))
    return not bad


def todo(x, kind, folder, page, note, step):
    st, n, d = x['state'], x['electors_final'], x['final_date']
    net = n - x['electors_draft']
    fall = x['_before'] - n
    rel = ('It stands %s above the draft' % ind(net)) if net >= 0 else ('It stands %s below the draft' % ind(-net))
    parts = []
    if x.get('added') is not None and x.get('deleted') is not None:
        a, de = (('%.2f lakh' % (x['added'] / 1e5), '%.2f lakh' % (x['deleted'] / 1e5)) if x['figures'] == 'rounded' else (ind(x['added']), ind(x['deleted'])))
        parts.append('%s names were added and %s deleted after the draft' % (a, de))
    else:
        parts.append('no count of names added or deleted after the draft was published')
    sex = ' It holds %s men, %s women and %s third gender electors.' % (ind(x['men']), ind(x['women']), ind(x['third'])) if x.get('men') is not None else ''
    line = '%s: the final roll of %s, %s electors, a fall in the roll of %s since the roll before the revision. %s, and %s.%s' % (
        st, long_date(d), ind(n), ind(fall), rel, parts[0], sex)
    print('\n' + '=' * 72 + '\nLEFT TO DO BY HAND for %s\n' % st)
    print('1. What\'s New. data/updates.json is not written by this script. A drafted entry for %s:' % d)
    print('   ' + json.dumps([line, page], ensure_ascii=False))
    print('   Then add the "How the revision was run" line Karnataka\'s entry carried, if the schedule step is new.')
    srcmd = P('data', folder, 'raw', 'SOURCES.md') if folder else None
    if srcmd and os.path.exists(srcmd):
        print('2. %s: add a section for the final roll naming %s (%s), what it gives and what it does not.' % (os.path.relpath(srcmd, ROOT), x['source'], x['source_url']))
    else:
        print('2. Sources: the state has no SOURCES.md. The source is recorded in final.csv%s.' % (' and normal.json' if kind == 'shared' else ''))
    if kind == 'own' and st != 'Karnataka':
        print('3. The page (%s) switches from "due on" to "published on" by itself from summary.json. Read it at 390 wide.' % page)
    elif kind == 'own':
        print('3. Karnataka\'s page text about the final roll is written by hand in site/pages/karnataka/index.html. Read it against the new figures.')
    elif kind == 'shared':
        print('3. normal.json now carries the note "%s" Add to cannot_show what the final roll was not published for (by district or constituency, by sex), as Meghalaya\'s does.' % note)
    else:
        print('3. This state has no page of its own beyond the All India tables.')
    if x.get('_existing'):
        print('4. A final roll was already recorded. If any figure changed, add an entry to site/pages/corrections/index.html saying what the pages said and what they say now.')
    else:
        print('4. Corrections: nothing to add, since no figure was there before.')
    print('5. The front page card in site/pages/index.html (the <a class="hub st" href="%s"> line): say the final roll is in if the card names what the page holds.' % (page.split('/')[0] + '/'))
    P_ = json.load(open(PROCESS, encoding='utf-8'))
    due = [t['title'] for t in P_['timeline'] if st in (t.get('text') or '') and re.search(r'\bfinal roll (is|was) due\b|\bdue on\b', t.get('text') or '')]
    rep = [t['topic'] for t in P_.get('reported', []) if t.get('state') == st and 'due' in (t.get('response') or '')]
    if due or rep:
        print('6. data/india/process.json says the final roll is due in: %s. Say it was published.' % '; '.join(due + rep))
    if step:
        print('   A schedule step "%s" was added to process.json.' % step['label'])
    print('   The reading page panels quote national figures that move with every final roll. If check_data.py fails on them, change the figure and its sentence in data/india/raw/panels_research/plain.json (the failure names both), then run scripts/build_panels.py.')
    rep = {'mh': 'node scripts/reports/page_pack.mjs http://localhost:8000 mh', 'dl': 'node scripts/reports/page_pack.mjs http://localhost:8000 dl',
           'hyd': 'scripts/reports/build.sh (the Hyderabad report)', 'ka': 'scripts/reports/build.sh (the Karnataka report and deck)'}
    cmd = rep.get(OWN[st][3]) if kind == 'own' else 'node scripts/reports/page_pack.mjs http://localhost:8000 other' if kind == 'shared' else 'scripts/reports/build.sh (the India report)'
    print('7. With the site served (python3 -m http.server 8000), the report and deck: %s. Then the link cards: node scripts/og_cards.mjs.' % cmd)
    print('8. Commit only the sources (scripts/, site/pages/, data/ sources, i18n/), then open the pull request. To publish before 20:00 IST, the owner says "publish".')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--json')
    for k in INT_KEYS:
        ap.add_argument('--' + k.replace('_', '-'), dest=k)
    for k in TEXT_KEYS:
        ap.add_argument('--' + k.replace('_', '-'), dest=k)
    ap.add_argument('--dry-run', action='store_true', help='validate and show the diff, and write nothing')
    ap.add_argument('--replace', action='store_true', help='rewrite a final roll already recorded')
    ap.add_argument('--no-build', action='store_true', help='write the sources and stop')
    ap.add_argument('--no-site', action='store_true', help='run the data builders and data checks only')
    ap.add_argument('--due', action='store_true', help='list every state whose final roll is not recorded, with the date it is due, and stop')
    a = ap.parse_args()
    if a.due:
        S = json.load(open(P('data', 'india', 'states.json'), encoding='utf-8'))['states']
        Pr = json.load(open(PROCESS, encoding='utf-8'))
        t = today_ist()
        for r in sorted((r for r in S if r.get('electors_final') is None), key=lambda r: (final_roll.due(r['state'], Pr) or '9', r['state'])):
            d = final_roll.due(r['state'], Pr)
            what = 'no draft yet' if r.get('removed') is None else ('OVERDUE' if d and d < t else 'due today' if d == t else 'due')
            print('%-12s %-10s %s%s' % (d or 'no date', what, r['state'], ' (own analysis)' if r['state'] in OWN else ''))
        return
    x = read_input(a)
    err, warn, _r = validate(x, a.replace)
    for w in warn:
        print('WARNING: ' + w)
    if err:
        for e in err:
            print('REFUSED: ' + e)
        sys.exit(1)
    st = x['state']
    shared = shared_states()
    if st in OWN:
        kind, folder, page = 'own', OWN[st][0], OWN[st][2]
    elif st in shared:
        kind, folder, page = 'shared', shared[st], shared[st] + '/'
    else:
        kind, folder, page = 'none', None, 'india/'
    files = {FINAL_CSV: new_final_csv(x)}
    note = None
    if kind == 'shared':
        p, t, note = new_normal(x, folder)
        files[p] = t
    elif kind == 'own':
        p, t = new_own(x, folder)
        files[p] = t
    ptext, step = new_process(x)
    files[PROCESS] = ptext
    changed = 0
    for p, t in files.items():
        old = open(p, encoding='utf-8', newline='').read() if os.path.exists(p) else ''
        if old == t:
            print('unchanged: %s' % os.path.relpath(p, ROOT))
            continue
        changed += 1
        rel = os.path.relpath(p, ROOT)
        print(''.join(difflib.unified_diff(old.splitlines(True), t.splitlines(True), 'a/' + rel, 'b/' + rel, n=1)))
    print('%s: the final roll of %s, %s electors (%s), %s, source %s. %d file(s) %s.' % (
        st, x['final_date'], ind(x['electors_final']), x['figures'], kind, x['source_kind'], changed, 'would change' if a.dry_run else 'changed'))
    if a.dry_run:
        print('DRY RUN: nothing written.')
        todo(x, kind, folder, page, note, step)
        return
    for p, t in files.items():
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8', newline='').write(t)
    ok = True
    if not a.no_build:
        ok = pipeline(x, kind, folder, a.no_site)
    todo(x, kind, folder, page, note, step)
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
