"""The files build_site.py writes beside the pages for readers who follow the
revision from elsewhere: the What's new feed, the calendars of each state's
dates, the index of every published data file, and Netlify's _headers.

Each function returns text; build_site.py writes it with its own put(), so
`build_site.py --check` fails when any of them is stale. Nothing here reads
the clock: every date comes from the data, so two builds of the same data
write the same files.

  feed.xml               Atom, one entry per day of data/updates.json
  calendar.ics           all India: each state's draft and final roll, the
                         Supreme Court's dated orders in the process timeline,
                         and the events still to come in data/india/events.json
  calendar/<state>.ics   one state's own dates, from its latest schedule
  data/index.json        every published data file, with its columns or keys
  _headers               frame protection for every published path except
                         /embed/, which other sites may frame (see netlify.toml)
"""
import csv
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding='utf-8'))
MONTHS = 'January February March April May June July August September October November December'.split()


def long_date(iso):
    return '%d %s %s' % (int(iso[8:10]), MONTHS[int(iso[5:7]) - 1], iso[:4])


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def state_name(place):
    """The state a place's pages are about, as data/india/process.json names it."""
    if place['id'] == 'hyd':
        return 'Telangana'
    return re.sub(r' 20\d\d$', '', place['label'])


def latest_update():
    return max(e['date'] for e in J('data/updates.json')['entries'])


# ------------------------------------------------------------------- feed
def feed(cfg):
    U = J('data/updates.json')['entries']
    url = cfg['url']
    newest = max(e['date'] for e in U)
    out = ['<?xml version="1.0" encoding="utf-8"?>',
           '<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="en">',
           '  <title>Off the Roll: what\'s new</title>',
           '  <subtitle>What has been added, by date: states, constituency and district pages, sources and tables on the Special Intensive Revision of the electoral rolls.</subtitle>',
           '  <id>%supdates/</id>' % url,
           '  <link rel="self" type="application/atom+xml" href="%sfeed.xml"/>' % url,
           '  <link rel="alternate" type="text/html" href="%supdates/"/>' % url,
           '  <updated>%sT00:00:00Z</updated>' % newest,
           '  <author><name>%s</name><uri>%s</uri></author>' % (html.escape(cfg['credit']), html.escape(cfg['credit_url'])),
           '  <rights>CC BY 4.0</rights>']
    for e in sorted(U, key=lambda e: e['date'], reverse=True):
        items = ''.join('<li>%s</li>' % ('<a href="%s%s">%s</a>' % (url, html.escape(it[1]), html.escape(it[0])) if it[1] else html.escape(it[0]))
                        for it in e['items'])
        first = e['items'][0][0] if e['items'] else ''
        title = '%s: %d %s' % (long_date(e['date']), len(e['items']), 'addition' if len(e['items']) == 1 else 'additions')
        out += ['  <entry>',
                '    <title>%s</title>' % html.escape(title),
                '    <id>%supdates/#d-%s</id>' % (url, e['date']),
                '    <link rel="alternate" type="text/html" href="%supdates/#d-%s"/>' % (url, e['date']),
                '    <updated>%sT00:00:00Z</updated>' % e['date'],
                '    <summary>%s</summary>' % html.escape(first[:300]),
                '    <content type="html">%s</content>' % html.escape('<ul>%s</ul>' % items),
                '  </entry>']
    out.append('</feed>')
    return '\n'.join(out) + '\n'


# -------------------------------------------------------------- calendars
def _esc(s):
    return s.replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')


def _fold(line):
    """RFC 5545: lines of at most 75 octets, continued with a space."""
    b = line.encode('utf-8')
    if len(b) <= 75:
        return line
    parts, cur = [], b''
    for ch in line:
        c = ch.encode('utf-8')
        if len(cur) + len(c) > (75 if not parts else 74):
            parts.append(cur.decode('utf-8'))
            cur = b''
        cur += c
    parts.append(cur.decode('utf-8'))
    return '\r\n '.join(parts)


def _next_day(iso):
    import datetime
    return (datetime.date.fromisoformat(iso) + datetime.timedelta(days=1)).isoformat()


def _event(uid, start, end, summary, desc, url, stamp):
    """An all-day event from start to end inclusive (ISO dates)."""
    end = end or start
    lines = ['BEGIN:VEVENT', 'UID:%s@offtheroll.in' % uid, 'DTSTAMP:%sT000000Z' % stamp.replace('-', ''),
             'DTSTART;VALUE=DATE:%s' % start.replace('-', ''), 'DTEND;VALUE=DATE:%s' % _next_day(end).replace('-', ''),
             'SUMMARY:' + _esc(summary), 'DESCRIPTION:' + _esc(desc), 'TRANSP:TRANSPARENT']
    if url:
        lines.append('URL:' + url)
    lines.append('END:VEVENT')
    return lines


def _calendar(name, desc, events):
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Off the Roll//SIR dates//EN', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
             'X-WR-CALNAME:' + _esc(name), 'X-WR-CALDESC:' + _esc(desc), 'X-WR-TIMEZONE:Asia/Kolkata']
    for e in events:
        lines += e
    lines.append('END:VCALENDAR')
    return '\r\n'.join(_fold(x) for x in lines) + '\r\n'


def schedule(state):
    """One state's dates as they now stand: a draft or final roll already
    published on the day it was published; otherwise, for each step, the
    latest order that sets it, or a date moved since in the press (as the
    pages' own line under the kicker does). Returns [(kind, start, end, src, note)]."""
    P = J('data/india/process.json')
    sched = next((s for s in P['schedules'] if s['state'] == state), None)
    if not sched:
        return []
    got = {}
    for st in sched['steps']:
        for k in ('enum', 'draft', 'claims', 'notice', 'final'):
            if st.get(k):
                got[k] = (st[k], st.get('src'), st.get('label'))
    moved = sorted((x for x in P.get('reported_dates', []) if x['state'] == state), key=lambda x: x['date'])
    # a roll already published is dated by its publication (data/india/states.json)
    S = next((r for r in J('data/india/states.json')['states'] if r['state'] == state), {})
    done = {}
    if S.get('draft_date'):
        done['draft'] = (S['draft_date'], S.get('source_url'), 'published')
    if S.get('electors_final') and S.get('final_date'):
        done['final'] = (S['final_date'], (S.get('final_source') or {}).get('url'), 'published')
    out = []
    for k in ('enum', 'draft', 'claims', 'notice', 'final'):
        rep = [x for x in moved if x.get(k)]
        if k in done:
            out.append((k, done[k][0], done[k][0], done[k][1], done[k][2]))
        elif rep:
            r = rep[-1]
            out.append((k, r[k], r[k], r['url'], 'Moved, as %s reported on %s. No order confirming the new date has been found.' % (r['outlet'], long_date(r['date']))))
        elif k in got:
            v, src, label = got[k]
            a, b = (v[0], v[1]) if isinstance(v, list) else (v, v)
            out.append((k, a, b, src, 'Set in: %s.' % label if label else ''))
    return out


KIND = {'enum': ('enumeration', 'house visits and enumeration forms'), 'draft': ('draft', 'draft roll'),
        'claims': ('claims', 'claims and objections'), 'notice': ('notices', 'notices heard and decided'),
        'final': ('final', 'final roll')}


def calendars(cfg):
    P = J('data/india/process.json')
    stamp = P['as_of']
    url = cfg['url']
    files, per_state = {}, {}
    india = []
    for place in cfg['places']:
        if not place.get('zone') or not place['pages']:
            continue
        name = state_name(place)
        dates = schedule(name)
        if not dates:
            continue
        page = url + place['pages'][0][0]
        ev = []
        for k, a, b, src, note in dates:
            what = KIND[k][1]
            if k in ('draft', 'final'):
                what += ' published' if note == 'published' else ' due'
            summary = '%s: %s' % (name, what)
            desc = ' '.join(x for x in ('%s.' % (what[0].upper() + what[1:]), '' if note == 'published' else note,
                                        'Source: %s.' % src if src else '', 'More: ' + page) if x)
            e = _event('%s-%s' % (slug(name), KIND[k][0]), a, b, summary, desc, page, stamp)
            ev.append(e)
            if k in ('draft', 'final'):
                india.append((a, e))
        path = 'calendar/%s.ics' % slug(name)
        files[path] = _calendar('Off the Roll: %s' % name, 'The dates of the Special Intensive Revision in %s, from the Election Commission\'s orders, and dates moved since as the press reported them.' % name, ev)
        per_state[place['id']] = path
    # the Supreme Court's dated orders and hearings, as the process timeline holds them
    seen = {}
    for t in P['timeline']:
        if t['who'] != 'sc':
            continue
        n = seen.get(t['date'], 0)
        seen[t['date']] = n + 1
        uid = 'sc-%s%s' % (t['date'], '-%d' % (n + 1) if n else '')
        src = t['src'][0]['url'] if isinstance(t.get('src'), list) and t['src'] and isinstance(t['src'][0], dict) else (t.get('src') if isinstance(t.get('src'), str) else '')
        india.append((t['date'], _event(uid, t['date'], t['date'], 'Supreme Court: ' + t['title'], t['text'] + (' Source: ' + src if src else '') + ' More: ' + url + 'india/process/', url + 'india/process/', stamp)))
    # events still to come or under way on the day the schedules were checked
    for e in J('data/india/events.json')['events']:
        end = e.get('end') or e['start']
        if end < stamp:
            continue
        desc = '%s Organised by %s%s. Place: %s. Source: %s' % (e['what'], e['organiser'], ' (a political party)' if e.get('party') else '', e['place'], e['url'])
        india.append((e['start'], _event(e['id'], e['start'], end, e['title'], desc, url + 'india/events/', stamp)))
    india.sort(key=lambda x: x[0])
    files['calendar.ics'] = _calendar('Off the Roll: the revision across India',
                                      'Each state\'s draft and final roll, the Supreme Court\'s dated orders, and events still to come on the Special Intensive Revision.',
                                      [e for _, e in india])
    return files, per_state


# --------------------------------------------------------- data file index
LICENCE = {'name': 'CC BY 4.0', 'url': 'https://creativecommons.org/licenses/by/4.0/'}
# what the files with no table of their own hold, by name
NAMED = {
    'data/india/ac_finder.json': 'Every constituency the constituency finder opens, with its state and page',
    'data/india/brief.json': 'The SIR in brief: the rules and rights, each with its source',
    'data/india/cases.json': 'The case studies of single constituencies and places, with their sources',
    'data/india/disputes_counts.json': 'Counts of the protests and disputes by state and month',
    'data/india/events.json': 'Jan Sunwais, marches, protests and press conferences about the revision, with dates and sources',
    'data/india/help.json': 'What to do when a name is left off the roll: remedies, forms and organisations, with sources',
    'data/india/help_counts.json': 'Counts behind the page on what to do when a name is left off',
    'data/india/margins.json': 'Names left off against the 2024 Lok Sabha winning margins, constituency by constituency',
    'data/india/nrc.json': 'The National Register of Citizens, as set beside the revision, with sources',
    'data/india/panels.json': 'Panels quoted on the reading page, with their figures',
    'data/india/process.json': 'How the revision was run: the rules as they changed, and each state\'s dates',
    'data/india/reads.json': 'Further reading and viewing on the revision, with outlets, dates and summaries',
    'data/bihar/final.json': 'Bihar: the final roll against the draft, by constituency',
    'data/bihar/identity.json': 'Bihar: the names left off by caste and religion group, as estimated from the lists',
    'data/bihar/impact.json': 'Bihar: estimates of how the names left off bear on the 2025 election',
    'data/bihar/reasons.json': 'Bihar: the names left off by the reason entered',
    'data/bihar/robust.json': 'Bihar: the robustness checks behind the findings',
    'data/bihar/swing.json': 'Bihar: the swing from 2020 to 2025 against the names left off',
    'data/bihar/tests.json': 'Bihar: the deaths and marriage tests against the census',
    'data/gujarat/final.json': 'Gujarat: the final roll by district',
    'data/hyderabad/impact.json': 'The Old City of Hyderabad: estimates of how the names left off bear on its seats',
    'data/hyderabad/telangana.json': 'Telangana: the draft roll by district, against the Old City of Hyderabad',
    'data/uttarpradesh/analysis.json': 'Uttar Pradesh: the figures its analysis pages draw',
}


def data_index(cfg, published, sizes):
    """Every published file under data/ and downloads/, with what it holds."""
    folders = {}
    for p in cfg['places']:
        for h, _label, _icon in p.get('pages', []):
            folders.setdefault(h.split('/')[0], state_name(p) if p.get('zone') else p['label'])
    folders['hyderabad'] = 'Telangana and the Old City of Hyderabad'
    D = J('data/downloads.json')
    what = {}
    for b in D['workbooks']:
        what[b['file']] = b['title'] + ', Excel workbook'
        for s in b['sheets']:
            what.setdefault(s['path'], s.get('what') or s['sheet'])
    if D.get('zip'):
        what[D['zip'].get('file', 'downloads/all-tables.zip')] = 'Every table as CSV in one zip file'
    rows = []
    for f in published:
        if not f.startswith(('data/', 'downloads/')) or f in ('data/index.json',) or f.endswith('.html'):
            continue
        ext = f.rsplit('.', 1)[-1].lower()
        parts = f.split('/')
        place = folders.get(parts[1], parts[1]) if parts[0] == 'data' and len(parts) > 2 else ''
        stem = parts[-1].rsplit('.', 1)[0]
        d = what.get(f) or NAMED.get(f)
        if not d and ext == 'json':
            twin = f[:-5] + '.csv'
            if twin in what:
                d = what[twin] + '. The same table as ' + twin + ', as JSON'
            elif parts[1] == 'geo':
                d = '%s for the maps of %s, from DataMeet' % ('Assembly constituency boundaries' if stem.endswith('_ac') else 'Boundaries',
                                                            'India' if stem == 'india' else folders.get(stem.replace('_ac', ''), stem))
            elif '/booths/' in f:
                d = 'Bihar: the polling booths of assembly constituency %d' % int(stem.split('_')[1])
            elif stem == 'summary':
                d = '%s: the figures its pages draw' % place
            elif stem == 'constituencies':
                d = '%s: one row for each assembly constituency' % place
            elif stem == 'districts':
                d = '%s: one row for each district' % place
            elif f == 'data/search.json':
                d = 'Every page, constituency and district the search box finds'
            elif f == 'data/updates.json':
                d = "What has been added, by date, as on the What's new page"
            elif f == 'data/downloads.json':
                d = 'The downloads manifest: every workbook, sheet and column, with what each holds'
            elif parts[1] == 'india' and parts[2] == 'factors' and len(parts) > 3:
                d = 'District circumstances from NFHS-5 beside the rate, for %s' % stem.replace('-', ' ').title().replace(' And ', ' and ')
            else:
                d = '%s: %s' % (place or 'All India', stem.replace('_', ' '))
        row = {'path': f, 'description': d or stem.replace('_', ' '), 'format': {'json': 'JSON', 'csv': 'CSV', 'xlsx': 'Excel', 'zip': 'ZIP', 'pdf': 'PDF', 'pptx': 'PowerPoint'}.get(ext, ext.upper()),
               'bytes': sizes[f]}
        full = os.path.join(ROOT, f)
        if ext == 'csv':
            with open(full, encoding='utf-8-sig', newline='') as fh:
                row['columns'] = next(csv.reader(fh), [])
        elif ext == 'json':
            try:
                o = json.load(open(full, encoding='utf-8'))
            except ValueError:
                o = None
            if isinstance(o, dict):
                row['keys'] = list(o.keys())
            elif isinstance(o, list):
                row['rows'] = len(o)
                if o and isinstance(o[0], dict):
                    row['row_keys'] = list(o[0].keys())
        # the maps are DataMeet's, under DataMeet's licences, which terms/ names
        row['licence'] = "DataMeet's licence, as the terms page gives it" if parts[1] == 'geo' else LICENCE['name']
        rows.append(row)
    out = {'title': 'Off the Roll: index of the published data files',
           'url': cfg['url'] + 'data/index.json',
           'built': latest_update(),
           'licence': LICENCE,
           'licence_note': 'The tables and the analysis may be reused under CC BY 4.0. Credit "SIR analysis for India, ImpactMojo" and link to the page used. Official data keeps the terms of whoever published it, and each file\'s source is named in its workbook and on its method page.',
           'publisher': {'name': cfg['credit'], 'url': cfg['credit_url']},
           'counts': {'files': len(rows), 'bytes': sum(r['bytes'] for r in rows)},
           'files': rows}
    return json.dumps(out, ensure_ascii=False, indent=1) + '\n'


# ----------------------------------------------------------------- headers
def headers(top_dirs, root_files):
    """Frame protection for every published path except /embed/.

    netlify.toml's [[headers]] for "/*" would also match /embed/*, and Netlify
    joins the values of a header set by two matching rules, so a browser would
    enforce frame-ancestors 'none' and X-Frame-Options DENY there too. The
    sitewide rule therefore carries no frame rule, and this file adds one for
    every other published path, from the same list stage_site.py publishes,
    so a new folder is covered by existing."""
    rule = ("  Content-Security-Policy: frame-ancestors 'none'\n  X-Frame-Options: DENY\n")
    paths = ['/'] + ['/' + f for f in sorted(root_files) if f.endswith('.html')] + ['/%s/*' % d for d in sorted(top_dirs) if d != 'embed']
    return ('# Written by scripts/build_site.py (build_feeds.headers). Every published\n'
            '# path but /embed/ may not be shown inside another site\'s frame.\n'
            + ''.join('%s\n%s' % (p, rule) for p in paths))
