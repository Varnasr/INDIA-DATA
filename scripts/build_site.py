"""Builds every page from one shell and the page's own content.

The shell (head, folk-art band, header, places menu, tab row, footer) is
written here, once, from site/places.json. What differs from page to page is
in site/pages/<path>/index.html: a JSON line naming the page's title,
description and place, the page's content, and, after a <!--scripts--> line,
the scripts it loads. A new state or city is a new entry in places.json and a
folder of pages; nothing is copied from another page.

It also writes the tab and page lists the phone section bar reads into
assets/sir.js, between /*sites*/ markers, so those cannot drift from the
header either.

    python3 scripts/build_site.py           # write the pages
    python3 scripts/build_site.py --check   # fail if a page is stale

scripts/stamp.py runs after this and adds ?v= to every reference, so the
pages here are written without stamps and the check ignores them.
"""
import glob
import hashlib
import html
import urllib.parse
import json
import os
import re
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_feeds as BF  # noqa: E402  the feed, calendars, data index and _headers
import final_roll  # noqa: E402  when each state's final roll is due
import build_i18n  # noqa: E402  which translation files each page loads
import build_now  # noqa: E402  which states have a "What to do now" page

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'site', 'pages')
CHECK = '--check' in sys.argv
CFG = json.load(open(os.path.join(ROOT, 'site', 'places.json'), encoding='utf-8'))
# a page listed twice in one menu or tab row shows up twice in the header
for _pl in CFG['places']:
    for _key in ('menu', 'pages'):
        _seen = [x[0] for x in _pl.get(_key, [])]
        _dup = sorted({x for x in _seen if _seen.count(x) > 1})
        if _dup:
            raise SystemExit('FAIL - %s lists %s twice in %s' % (_pl['id'], ', '.join(_dup), _key))
PLACES = {p['id']: p for p in CFG['places']}
# places with a page for every constituency (scripts/make_seat_pages.py)
SEAT_PAGES = {'tn': 'tamilnadu', 'wb': 'westbengal', 'kl': 'kerala', 'dl': 'delhi', 'uk': 'uttarakhand', 'gj': 'gujarat', 'rj': 'rajasthan', 'mh': 'maharashtra', 'bihar': 'bihar', 'as': 'assam', 'ml': 'meghalaya', 'mn': 'manipur', 'od': 'odisha'}
# Every page's <body> carries its place's class. Delhi's was once "dl", which
# is also the class of the header menus, so the print stylesheet's .dl{display:
# none} hid the whole of every Delhi page on paper. A place class must not be a
# class the stylesheet styles on its own.
_STYLED = set(re.findall(r'(?:^|[\s,{}>+~(])\.([A-Za-z][\w-]*)', open(os.path.join(ROOT, 'assets', 'sir.css'), encoding='utf-8').read()))
_ALLOWED = {'home', 'hyd', 'wide', 'has-toc'}  # styled on purpose, as the page's place
for _p in CFG['places']:
    _c = _p.get('class', _p['id'])
    if _c in _STYLED and _c not in _ALLOWED:
        raise SystemExit('FAIL - place class %r is also a class sir.css styles; give the place a "class" of its own' % _c)
SIRJS = os.path.join(ROOT, 'assets', 'sir.js')
ICONS = json.loads(re.search(r'var ICONS = (\{.*?\});', open(SIRJS, encoding='utf-8').read()).group(1))
# stamp.py adds ?v= to every reference and the build's hash to the citation
# box, so a page is compared with both left out
STAMP = re.compile(r'\?v=[0-9a-f]{8}|(?<=<span class="cite-build">)[0-9a-f]*(?=</span>)')
stale = []


def svg(paths, cls='icon'):
    return ('<svg class="%s" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'aria-hidden="true">%s</svg>' % (cls, paths))


LOGO = svg('<rect x="2" y="3" width="20" height="18" rx="2"/><path d="M8 10l2 2 4-4"/>')
PIN = svg('<path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>')
STAR = svg('<circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>')
DOWN = svg('<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>')
DL_BOOK = {'india': 'india', 'bihar': 'bihar', 'hyd': 'hyd', 'tn': 'tn', 'wb': 'wb', 'kl': 'kl', 'ka': 'ka', 'rj': 'rj', 'up': 'up', 'dl': 'dl', 'mh': 'mh', 'gj': 'gj', 'uk': 'uk', 'as': 'as'}
APP = svg('<rect x="6" y="2" width="12" height="20" rx="2"/><path d="M12 6v8m-3-3 3 3 3-3"/>')
LENS = svg('<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>')
MOON = svg('<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>')
PRINT = svg('<polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/>')


_DL = None


def dl_book(book):
    """The downloads manifest's entry for one workbook (data/downloads.json,
    written by scripts/build_repository.py), or None."""
    global _DL
    if _DL is None:
        p = os.path.join(ROOT, 'data', 'downloads.json')
        _DL = {b['id']: b for b in json.load(open(p, encoding='utf-8'))['workbooks']} if os.path.exists(p) else {}
    return _DL.get(book)


def favicon(color):
    return ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>"
            "<rect width='32' height='32' rx='6' fill='%23" + color + "'/>"
            "<path d='M8 9h16M8 15h16M8 21h9' stroke='white' stroke-width='2.4' stroke-linecap='round'/></svg>")


def read_source(path):
    text = open(path, encoding='utf-8').read()
    first, rest = text.split('\n', 1)
    meta = json.loads(first[len('<!--page '):first.rindex(' -->')])
    content, _, scripts = rest.partition('\n<!--scripts-->\n')
    return meta, content.rstrip('\n'), scripts.rstrip('\n')


def heading_ids(content):
    """Give every h2 and h3 of a page an id from its English text, so a link
    can open on that section in any language (sir.js adds the copy button).
    Ids are made here, from the source, because the text is translated in the
    browser and an id made there would differ from language to language."""
    taken = set(re.findall(r'\sid="([^"]+)"', content))

    def one(m):
        tag, attrs, inner = m.group(1), m.group(2) or '', m.group(3)
        if re.search(r'\sid=', attrs):
            return m.group(0)
        text = html.unescape(re.sub(r'<[^>]+>', '', inner)).lower()
        base = re.sub(r'[^a-z0-9]+', '-', text).strip('-')[:60].rstrip('-') or tag
        key, n = base, 2
        while key in taken:
            key, n = '%s-%d' % (base, n), n + 1
        taken.add(key)
        return '<%s%s id="%s">%s</%s>' % (tag, attrs, key, inner, tag)
    return re.sub(r'<(h[23])(\s[^>]*)?>(.*?)</\1>', one, content, flags=re.S)


def contents(content):
    """The contents list under the head of a long page, in the markup the full
    reports use (nav.toc, a "Contents" heading, a list of links). A page asks
    for it with <!--contents--> where the list goes. It lists the page's fixed
    h2 sections by id, and sir.js (SIR.contents) keeps it in step with the
    sections a page's script adds or a filter hides, in the reader's language."""
    if '<!--contents-->' not in content:
        return content
    body = re.sub(r'<script\b.*?</script>', '', content, flags=re.S)
    items = []
    for m in re.finditer(r'<h2\b[^>]*?\sid="([^"]+)"[^>]*>(.*?)</h2>', body, flags=re.S):
        text = ' '.join(html.unescape(re.sub(r'<[^>]+>', '', m.group(2))).split())
        items.append('<li class="l2"><a href="#%s">%s</a></li>' % (m.group(1), html.escape(text, quote=False)))
    if not items:
        raise SystemExit('FAIL - a page asks for a contents list and has no h2 with an id')
    nav = ('<nav class="toc page-toc" aria-labelledby="contents" data-no-i18n><h2 id="contents">Contents</h2><ol>%s</ol></nav>'
           % ''.join(items))
    return content.replace('<!--contents-->', nav, 1)


# Which roll a state's figures come from, and when the next one is due, for
# the line under the kicker on every page of that state. The roll is read
# from data/india/states.json (a final roll only when its electors are held),
# the next date from the latest schedule step in data/india/process.json, and
# "today" is process.json's as_of, the day the schedules were last checked,
# so the build stays the same from one run to the next. The English sentence
# is in the markup, and sir.js swaps in its translation through L().
ASOF_LATER = {}   # a roll published after the draft and before the final, by state (Karnataka's of 9 October until its final roll)
ASOF_EXTRA = {'Assam': '2026-02-10'}       # the Special Revision's final roll; Assam is not in states.json


def asof(place):
    if place['id'] in ('home', 'india'):
        return None
    name = 'Telangana' if place['id'] == 'hyd' else re.sub(r' 20\d\d$', '', place['label'])
    S = {r['state']: r for r in json.load(open(os.path.join(ROOT, 'data', 'india', 'states.json'), encoding='utf-8'))['states']}
    P = json.load(open(os.path.join(ROOT, 'data', 'india', 'process.json'), encoding='utf-8'))
    today = P['as_of']
    if name in ASOF_EXTRA:
        return {'k': 'final', 'd': ASOF_EXTRA[name], 'c': today}
    r = S.get(name)
    if r is None:
        raise SystemExit('FAIL - no row in states.json for %s, so its pages cannot say which roll they use' % name)
    if r.get('electors_final') and r.get('final_date'):
        return {'k': 'final', 'd': r['final_date'], 'c': today}
    sched = next((x for x in P['schedules'] if x['state'] == name), None)
    # the latest step's date, or a date moved since the last order, as
    # reported (scripts/final_roll.py, which check_data.py also uses to fail
    # on a final roll that is overdue and not recorded)
    due = final_roll.due(name, P)
    if not r.get('draft_date'):
        slug = place.get('slug')
        summ = None
        for d in glob.glob(os.path.join(ROOT, 'data', '*', 'summary.json')):
            j = json.load(open(d, encoding='utf-8'))
            if isinstance(j, dict) and j.get('state') == name:
                summ = j
        n = (summ or {}).get('dates', {}).get('draft') or (sched['steps'][-1].get('draft') if sched else None)
        return {'k': 'nodraft', 'n': n, 'c': today}
    d, k = r['draft_date'], 'draft'
    if name in ASOF_LATER:
        d, k = ASOF_LATER[name], 'latest'
    if not due:
        return {'k': k, 'd': d, 'c': today}
    return {'k': k + ('-past' if due < today else '-due'), 'd': d, 'n': due, 'c': today}


ASOF_EN = {
    'final': 'Figures as of {d}, when the final roll was published.',
    'draft-due': 'Figures as of {d}, when the draft roll was published. The final roll is due on {n}.',
    'draft-past': 'Figures as of {d}, when the draft roll was published. The final roll was due on {n} and had not been found published when these figures were checked.',
    'latest-due': 'Figures as of {d}, a roll published after claims had closed, while notices were being heard. The final roll is due on {n}.',
    'latest-past': 'Figures as of {d}, a roll published after claims had closed, while notices were being heard. The final roll was due on {n} and had not been found published when these figures were checked.',
    'nodraft': 'No draft roll has been published yet. It is due on {n}.',
}


def asof_html(a):
    if not a:
        return ''
    fmt = lambda iso: '%d %s %s' % (int(iso[8:]), 'January February March April May June July August September October November December'.split()[int(iso[5:7]) - 1], iso[:4]) if iso else ''
    if a['k'] not in ASOF_EN:
        raise SystemExit('FAIL - no sentence for the roll stage %r' % a['k'])
    text = ASOF_EN[a['k']].format(d=fmt(a.get('d')), n=fmt(a.get('n')))
    attrs = ''.join(' data-%s="%s"' % (x, a[x]) for x in ('k', 'd', 'n') if a.get(x))
    return '<p class="asof" data-no-i18n%s>%s</p>' % (attrs, html.escape(text))


# ------------------------------------------------ feeds, alerts, citations
# The calendars (scripts/build_feeds.py), keyed by place id, and the date of
# the latest entry on What's new, which stands for the build's date wherever
# a page has to name one without a script: nothing here reads the clock.
CAL_FILES, CAL_STATE = BF.calendars(CFG)
LATEST = BF.latest_update()
_cff = open(os.path.join(ROOT, 'CITATION.cff'), encoding='utf-8').read()
_fam = re.search(r'family-names:\s*(.+)', _cff)
_giv = re.search(r'given-names:\s*(.+)', _cff)
CITE_AUTHOR = ('%s, %s' % (_fam.group(1).strip(), _giv.group(1).strip())) if _fam and _giv else CFG['credit']
# the states whose final roll is still to come, for the alert form
PENDING = []
for _p in CFG['places']:
    if _p.get('zone') and _p['pages']:
        _a = asof(_p)
        if _a and _a['k'] != 'final':
            PENDING.append((_p['id'], BF.state_name(_p)))
PENDING.sort(key=lambda x: x[1])
# charts another site may show in a frame (site/pages/embed, make_embed_pages.py)
EMBEDS = {'india': 'india'}
EMBEDS.update({pid: folder for pid, folder in SEAT_PAGES.items()})
EMBEDS = {k: v for k, v in EMBEDS.items() if os.path.exists(os.path.join(SRC, 'embed', v, 'index.html'))}


def alert_form(root, chosen=None):
    """The Netlify form asking for one email when a state's final roll is out.
    Netlify finds it in the built pages; nothing is sent automatically."""
    opts = ('' if chosen else '<option value="">Choose a state</option>') + ''.join(
        '<option data-no-i18n%s>%s</option>' % (' selected' if n == chosen else '', html.escape(n)) for _pid, n in PENDING)
    return ('<form class="shareform alertform" name="roll-alert" method="POST" action="/alerts/thanks/" data-netlify="true" netlify-honeypot="company_website">'
            '<h3>Get one email when the final roll is published</h3>'
            '<input type="hidden" name="form-name" value="roll-alert">'
            '<p class="hp" hidden data-no-i18n><label>Leave this empty <input name="company_website" tabindex="-1" autocomplete="off"></label></p>'
            '<p>Leave an email address and pick a state. One email is sent, by hand, on the day that state\'s final roll is published. '
            'The address is used for nothing else, and it is never published or shared.</p>'
            '<p><label for="raState">State</label><select id="raState" name="state" required>%s</select></p>'
            '<p><label for="raEmail">Email address</label><input id="raEmail" name="email" type="email" autocomplete="email" required></p>'
            '<p><button type="submit" class="btn send">Ask for the email</button></p>'
            '<p class="note" data-i18n-each><a href="%sterms/#privacy">How the address is kept, and how to have it deleted</a></p>'
            '</form>' % (opts, root))


def dates_block(out, place, root):
    """Calendars and the alert form: on each state's overview, and on the
    pages about the process and the events."""
    if out in ('india/process/', 'india/events/'):
        intro = ('<p>Every state\'s draft and final roll, the Supreme Court\'s dated orders and the events still to come can be added to any calendar app. '
                 'Each state has a calendar of its own as well.</p>')
        links = '<p class="rollcal-links" data-i18n-each><a class="btn" href="%scalendar.ics">Add the dates for all India to a calendar</a></p>' % root
        states = ''.join(' <a href="%s%s">%s</a>' % (root, CAL_STATE[p['id']], html.escape(BF.state_name(p)))
                         for p in sorted(CFG['places'], key=lambda q: BF.state_name(q)) if p['id'] in CAL_STATE)
        links += '<p class="calstates" data-no-i18n lang="en" dir="ltr">%s</p>' % states
        form = alert_form(root) if out == 'india/process/' and PENDING else ''
    elif place.get('zone') and place['pages'] and out == place['pages'][0][0] and place['id'] in CAL_STATE:
        intro = '<p>The dates of this state\'s revision, from the Election Commission\'s orders, can be added to any calendar app.</p>'
        links = ('<p class="rollcal-links" data-i18n-each><a class="btn" href="%s%s">Add this state\'s dates to a calendar</a> '
                 '<a class="btn" href="%scalendar.ics">Add the dates for all India to a calendar</a></p>' % (root, CAL_STATE[place['id']], root))
        name = BF.state_name(place)
        form = alert_form(root, name) if any(n == name for _p, n in PENDING) else ''
    else:
        return ''
    return '<section class="rollcal"><h2 class="dlh">Dates of the revision</h2>%s%s%s</section>' % (intro, links, form)


# Whether the revision still takes claims in a state, on the day the reader
# opens the page. sir.js (SIR.owin) works the stage out in the browser from
# data/india/process.json and states.json, so the box changes with the date
# and needs no rebuild. Every state's overview gets an empty box under its
# head, and the help page's box (#owinAll) is given the overview of every
# state, so its table can link to them.
# Each state's "What to do now" page (scripts/build_now.py) is linked from
# the box, so the box and the help page's picker are given the pages by state.
NOW_PAGES = {r['state']: r['path'] for r in build_now.PAGES if os.path.exists(os.path.join(SRC, r['path'], 'index.html'))}
NOW_ATTR = ' data-owin-now="%s"' % html.escape(json.dumps(NOW_PAGES, sort_keys=True, separators=(',', ':')))


# The front page's "What to do now in your state" card lists every state
# with a "What to do now" page, read from data/india/now.json
# (scripts/build_now.py), so a state added there appears with the next build.
# The links carry the state's place label ("Delhi 2026"), which the Places
# menu already translates.
def now_states(content, root):
    if '<!--now-states' not in content:
        return content
    with open(os.path.join(ROOT, 'data', 'india', 'now.json'), encoding='utf-8') as f:
        pages = json.load(f)['pages']
    rows = sorted((k, v) for k, v in pages.items() if os.path.exists(os.path.join(SRC, v['path'], 'index.html')))
    if not rows:
        raise SystemExit('FAIL - data/india/now.json names no state with a "What to do now" page')
    chips = ''.join('<a href="%s%s">%s</a>' % (root, v['path'], html.escape(v['label'])) for k, v in rows)
    return content.replace('<!--now-states-->', chips)


def open_window(out, place, content):
    if place.get('zone') and place['pages'] and out == place['pages'][0][0]:
        name = BF.state_name(place)
        box = ('<aside class="owin" data-owin="%s"%s aria-live="polite" hidden></aside>'
               % (html.escape(name), (' data-owin-now="%s"' % html.escape(json.dumps({name: NOW_PAGES[name]}, separators=(',', ':')))) if name in NOW_PAGES else ''))
        new, n = re.subn(r'(<div class="page-head"[^>]*>.*?</div>)', lambda m: m.group(1) + '\n' + box, content, count=1, flags=re.S)
        if not n:
            raise SystemExit('FAIL - %s has no page head to put the claims box under' % out)
        return new
    if 'id="owinAll"' in content:
        pages = {BF.state_name(p): p['pages'][0][0] for p in CFG['places'] if p.get('zone') and p['pages']}
        return content.replace('id="owinAll"', 'id="owinAll" data-owin-pages="%s"%s' % (html.escape(json.dumps(pages, sort_keys=True, separators=(',', ':'))), NOW_ATTR), 1)
    return content


def embed_block(out, place, root):
    """The code to show a place's chart on another site, on its overview."""
    folder = EMBEDS.get(place['id'])
    if not folder or not place['pages'] or out != place['pages'][0][0]:
        return ''
    src = CFG['url'] + 'embed/%s/' % folder
    code = ('<iframe src="%s" title="%s" width="100%%" height="620" style="border:0" loading="lazy"></iframe>'
            % (src, 'Off the Roll: ' + ('names left off per 100 electors, by state' if folder == 'india' else BF.state_name(place) + ', by district')))
    what = ('The chart of names left off per 100 electors, state by state, can be shown on another website with the code below. It names its source and links back here.'
            if folder == 'india' else
            'A chart of this state\'s districts, in its own measure, can be shown on another website with the code below. It names its source and links back here.')
    return ('<details class="embedbox"><summary class="btn">Embed this chart</summary><p>%s</p>'
            '<textarea class="embedcode" readonly rows="3" aria-label="Code to embed the chart" data-no-i18n>%s</textarea>'
            '<p class="embedacts" data-i18n-each><button type="button" class="btn embed-copy">Copy the code</button> '
            '<a href="%sembed/%s/">See the chart on its own</a></p></details>' % (what, html.escape(code), root, folder))


def cite_block(out, meta):
    """How to cite the page: built here in English, with the build's hash
    (scripts/stamp.py) and a date; sir.js puts today's date in its place."""
    title = re.sub(r':\s*%s$' % re.escape(CFG['title']), '', meta['title'])
    when = BF.long_date(LATEST)
    ref = ('%s. "%s." <i>Off the Roll: %s</i>, %s. %s%s. Build <span class="cite-build"></span>, %s. Accessed <span class="cite-acc">%s</span>.'
           % (html.escape(CITE_AUTHOR), html.escape(title), html.escape(CFG['title']), html.escape(CFG['credit']), CFG['url'],
              html.escape(out if out != '404.html' else ''), when, when))
    return ('<details class="cite"><summary>Cite this page</summary>'
            '<p class="citetext" data-no-i18n lang="en" dir="ltr">%s</p>'
            '<p><button type="button" class="btn cite-copy">Copy the reference</button></p></details>' % ref)


def embed_shell(out, meta, content, scripts, place, root):
    """A chart alone, for another site's frame: no header, menus or footer,
    only the chart, its source and a link back (site/pages/embed)."""
    back = CFG['url'] + (place['pages'][0][0] if place['pages'] else '')
    page = (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<meta name="robots" content="noindex">\n'
        '<script src="%sassets/i18n.js"></script>\n<title>%s</title>\n<meta name="description" content="%s">\n'
        '<link rel="canonical" href="%s">\n<link rel="stylesheet" href="%sassets/sir.css">\n</head>\n'
        '<body class="embed %s" data-place="%s" data-root="%s" data-back="%s">\n%s\n%s\n</body>\n</html>\n'
    ) % (root, html.escape(meta['title'], quote=False), html.escape(meta['description']), back, root,
         place.get('class', place['id']), place['id'], root, back, content, scripts)
    return i18n_files(out, page)


def shell(out, meta, content, scripts):
    """The whole page for site path `out` (e.g. 'bihar/results/')."""
    depth = out.count('/')
    root = '../' * depth
    place = PLACES[meta['place']]
    here = out
    # the places menu: every analysis, the current one marked. A place's own
    # pages and the run of 2026 states each fold under a heading, opened when
    # the reader is inside it, so the menu stays short as places are added.
    # every state and territory sits in one fold, grouped by the Ministry of
    # Home Affairs' zonal councils (`zone` in places.json) and A to Z inside
    # each, so a place is always where the reader found it last time. The 13
    # with a full analysis of their own are in bold; the 20 on the shared page
    # are not. Telangana carries the Old City study beneath it.
    FULL = {'bihar', 'hyd', 'tn', 'ka', 'wb', 'kl', 'rj', 'up', 'dl', 'mh', 'gj', 'uk', 'as', 'od', 'ap', 'cg', 'mn', 'ml'}
    ZONES = ['Northern', 'Central', 'Eastern', 'Western', 'Southern', 'North-East']

    def link(p, href=None, label=None, cls=''):
        href = root + (href if href is not None else (p['pages'][0][0] if p['pages'] else ''))
        cur = ' aria-current="true"' if p['id'] == place['id'] and not cls else ''
        c = ' '.join(x for x in (cls, 'full' if p['id'] in FULL and not cls else '') if x)
        return '<a href="%s"%s%s>%s</a>' % (href or './', ' class="%s"' % c if c else '', cur, html.escape(label or p['label']))

    def fold(title, links, opened, cls=''):
        return ('<details class="grp%s"%s><summary>%s</summary><div class="sub" data-i18n-each>%s</div></details>'
                % (cls, ' open' if opened else '', html.escape(title), ''.join(links)))
    items, zoned = [], {z: [] for z in ZONES}
    for p in CFG['places']:
        if p.get('zone'):
            if p['zone'] not in zoned:
                raise SystemExit('unknown zone %r for %s' % (p['zone'], p['id']))
            zoned[p['zone']].append(p)
            continue
        if p.get('group'):
            raise SystemExit('%s has a group but no zone' % p['id'])
        if p.get('menu'):
            # a place with its own pages is one fold: its overview, then each page
            home = p['pages'][0][0]
            subs = ['<a href="%s%s"%s>%s</a>' % (root, h, ' aria-current="page"' if h == here else '', html.escape(t)) for h, t in [[home, 'Overview']] + p['menu']]
            items.append(fold(p['label'], subs, p['id'] == place['id']))
        else:
            # the front page's place is About this site, which opens on why the
            # revision matters, so the link does not reload the page a reader is on.
            # The 404 page is built as the front page's place and needs a real link.
            items.append(link(p, '#why-this-site-exists' if p['id'] == 'home' and here != '404.html' else None))
    subs = ['<p class="lg">Names in bold have a full analysis of their own. The others share one summary page.</p>']
    # each zone is its own block, so a wide screen can set the zones in columns
    for z in ZONES:
        zl = ['<span class="rg">%s</span>' % z]
        for p in sorted(zoned[z], key=lambda q: q['label']):
            if p['id'] == 'hyd':
                zl.append(link(p, 'hyderabad/telangana/'))
                zl.append(link(p, 'hyderabad/', 'Old City of Hyderabad', 'in'))
            else:
                zl.append(link(p))
        subs.append('<div class="zn" data-i18n-each>%s</div>' % ''.join(zl))
    items.append(fold('All states and union territories', subs, bool(place.get('zone')), ' states'))
    # the front page closes the menu, under a rule, rather than sitting
    # between the pages most readers come for and the places
    about = [i for i in items if i.startswith('<a ')]
    items = [i for i in items if not i.startswith('<a ')] + ['<div class="about" data-i18n-each>%s</div>' % ''.join(about)]
    # the pages most readers come for, at the top of the menu whatever the place
    quick = '<div class="ql" data-i18n-each>%s</div>' % ''.join(
        '<a href="%s%s"%s>%s</a>' % (root, h, ' aria-current="page"' if h == here else '', html.escape(t)) for h, t in
        (('guide/', 'How to use this site'), ('about-the-data/', 'About the data'), ('india/brief/', 'The SIR in brief'), ('india/constituencies/', 'Find a constituency'), ('help/', 'Left off the roll? What to do'), ('help/#owinAll', 'What to do now in your state'), ('india/disputes/', 'Protests and disputes'), ('india/events/', 'Events'), ('india/rti/', 'RTI replies'), ('india/cases/', 'Case studies'), ('india/reading/', 'Further reading and viewing'),
         ('india/women/', 'Women'), ('india/numbers/', 'The SIR in numbers'), ('support/', 'Support our work')))
    # "Start here" is its own menu beside Places, so Places holds only places
    about = ''.join(i for i in items if i.startswith('<div class="about"'))
    items = [i for i in items if not i.startswith('<div class="about"')]
    start = ('<details class="dl start"><summary class="btn" aria-label="Start here">%s <span class="lbl">Start here</span></summary>'
             '<div class="menu"><div data-i18n-each>%s%s</div></div></details>' % (STAR, quick, about))
    current = place['label'] if place['id'] != 'home' else 'Places'
    places = ('<details class="dl places"><summary class="btn">%s <span class="vh">Places, </span><span class="lbl-place">%s</span></summary>'
              '<div class="menu"><div data-i18n-each>%s</div></div></details>' % (PIN, html.escape(current), ''.join(items)))
    # Downloads is one button to the downloads page, opened at this place's
    # own workbook, which lists its tables, report and slides with what each
    # holds. A menu of every file grew to twenty links on All India.
    book = DL_BOOK.get(place['id'], 'other' if place.get('zone') else '')
    dl = ('<a class="btn dlink" href="%sdownloads/%s"%s>%s <span class="lbl">Downloads</span></a>'
          % (root, '#w-' + book if book else '', ' aria-current="page"' if here == 'downloads/' else '', DOWN))
    # the sitewide search (sir.js): a button, and Ctrl or Command and K
    # installing the site as an app: hidden until the browser offers it (sir.js)
    find = ('<button type="button" class="btn install" hidden>%s <span class="lbl">Install app</span></button>\n      ' % APP) + ('<button type="button" class="btn find" aria-haspopup="dialog" aria-keyshortcuts="Control+K Meta+K">%s '
            '<span class="lbl">Search</span> <kbd class="kbd" aria-hidden="true">Ctrl K</kbd></button>' % LENS)
    # Print belongs on an analysis, where it prints the charts; the front page
    # is an introduction and carries no print button.
    prn = ('' if place['id'] == 'home' else
           '<button type="button" class="btn-primary print">%s <span class="lbl">Export PDF</span></button>' % PRINT)
    # A dashboard's only heading is the site title in its header.
    tag = 'h1' if meta.get('own_tabs') and '<h1' not in content else 'span'
    header = (
        '<a class="skip" href="#main">Skip to content</a>\n'
        '<div class="band %s" aria-hidden="true"></div>\n'
        '<header class="top">\n  <div class="header-content">\n'
        '    <a class="logo" href="%s"><span class="logo-icon">%s</span><%s class="titles"><span class="wm" aria-hidden="true" data-no-i18n>Off the <s>Roll</s></span>'
        '<span class="h-title">%s</span><span class="subtitle">%s</span></%s></a>\n'
        '    <div class="controls" data-dyslexia-slot data-dyslexia-before=".theme">\n      %s\n      %s\n      %s\n      %s\n'
        '      <button type="button" class="theme" aria-pressed="false">%s <span class="lbl">Dark</span></button>\n'
        '      %s\n'
        '    </div>\n  </div>\n</header>\n'
    ) % (place['band'], root or './', LOGO, tag, html.escape(CFG['title']), html.escape(place['subtitle']), tag, find, start, places, dl, MOON, prn)
    nav = ''
    if place['pages'] and not meta.get('own_tabs'):
        tabs = []
        for h, label, icon in place['pages']:
            cur = ' aria-current="page"' if h == here else ''
            tabs.append('<a class="nav-tab" href="%s%s"%s>%s %s</a>' % (root, h, cur, svg(ICONS[icon]), html.escape(label)))
        nav = '<nav class="nav-tabs" aria-label="%s">%s</nav>\n' % (place['nav_label'], ''.join(tabs))
    # data-i18n-each: the credit and the link are translated apart, so the
    # key does not change with the page's depth.
    # the constituency finder floats at the bottom of the screen, with its
    # label, on every page but its own: a seat is what most readers come for
    fab = '' if here == 'india/constituencies/' else (
        '<a class="fab" href="%sindia/constituencies/#find-a-constituency">%s<span>Find your constituency</span></a>' % (root, svg(ICONS['i23'])))
    # and a second, quieter one asking for lists the site does not have,
    # on every screen, except on the share pages themselves
    if not here.startswith(('share/', 'support/', 'feedback/')):
        fab = ('<a class="fab fab-share" href="%sshare/">%s<span>Share a list</span></a>' % (root, svg(ICONS['i24']))) + fab
    fab = '<div class="fabs">%s</div>' % fab if fab else ''
    footer = ('<footer data-i18n-each><span>Research by <a href="%s">%s</a>. Only totals are published, never names or EPIC numbers.</span>'
              ' · <a href="%s#why-this-site-exists">About this site</a> · <a href="%shelp/">Left off the roll? What to do</a> · <a href="%sdownloads/%s">Downloads</a> · <a href="%sshare/">Share a list</a> · <a href="%ssupport/">Support our work</a> · <a href="%sterms/">Terms and privacy</a> · <a href="%supdates/">What\'s new</a> · <a href="%sfeed.xml">Follow by feed</a> · <a href="%scorrections/">Corrections</a> · <a href="%sfeedback/?from=%s">Feedback</a>'
              ' · <a href="mailto:%s">%s</a></footer>' % (CFG['credit_url'], html.escape(CFG['credit']), root or './', root, root, '#w-' + book if book else '', root, root, root, root, root, root, root, urllib.parse.quote(here or 'home', safe=''), CFG['email'], CFG['email']))
    # On a phone the header's Downloads button is inside the menu, and the
    # footer link opened the downloads page at its top, where the first button
    # is the zip of every table. So every page of a place with a workbook
    # carries its own files at the foot of the page: the workbook and the
    # CSVs the pages draw, each one tap away.
    # (a state's "What to do now" page is about the steps open to an elector,
    # like the help page, so it carries no table downloads either)
    wb = dl_book(book) if book and not here.startswith(('downloads/', 'share/', 'terms/', 'corrections/', 'updates/', 'help/')) and not here.endswith('/now/') and place['id'] != 'home' else None
    if wb:
        # the shared workbook of the twenty smaller places: only this place's own table
        own = 'data/%s/' % out.split('/')[0]
        csvs = ''.join(' <a href="%s%s" download>%s</a>' % (root, s['path'], html.escape(s['path'].rsplit('/', 1)[-1])) for s in wb['sheets']
                       if s['kind'] == 'published' and (book != 'other' or s['path'].startswith(own)))
        strip = ('<section class="dlstrip" lang="en" dir="ltr" data-no-i18n aria-label="Download the figures"><h2 class="dlh">Download the figures for %s</h2>'
                 '<p><a class="btn" href="%s%s" download>%s</a> <a class="btn" href="%sdownloads/#w-%s">What each sheet holds</a></p>'
                 '%s</section>' % (html.escape(place['label']), root, wb['file'],
                                   'Excel workbook, this place and the other smaller states' if book == 'other' else 'Excel workbook, every table', root, book,
                                   ('<p class="csvs">CSV:%s</p>' % csvs) if csvs else ''))
        content = content.replace('</main>', strip + '\n</main>', 1) if '</main>' in content else content + strip
    footer += ('\n' + fab) if fab else ''
    # every page that loads sir.js gets viz.js after it: SIR.chart and the
    # dashboards hand ranked lists and side-by-side measures to it
    if 'assets/sir.js' in scripts and 'assets/viz.js' not in scripts:
        scripts = re.sub(r'(<script src="[^"]*assets/sir\.js"></script>)', lambda m: m.group(1) + '\n' + m.group(1).replace('sir.js', 'viz.js'), scripts, count=1)
    if meta.get('embed'):
        return embed_shell(out, meta, content, scripts, place, root)
    if place['id'] != 'home':
        content = re.sub(r'(<div class="page-head"[^>]*>)', lambda m: m.group(1) + '<p class="kicker">%s</p>' % html.escape(place['label']) + asof_html(asof(place)), content, count=1)
    content = open_window(out, place, content)
    content = now_states(content, root)
    head_extra = ('\n' + meta['head']) if meta.get('head') else ''
    # link previews: a shared page shows its title, description and its
    # place's card (assets/og, written by scripts/og_cards.mjs). Previews
    # need absolute addresses, so this is the one place the head carries
    # the site's own; no visible text does.
    og = CFG['url'] + 'assets/og/%s.png' % place['id']
    t, d = html.escape(meta['title']), html.escape(meta['description'])
    head_extra = ('\n<meta property="og:type" content="website">\n<meta property="og:site_name" content="%s">\n'
                  '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n'
                  '<meta property="og:url" content="%s%s">\n<meta property="og:image" content="%s">\n'
                  '<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
                  '<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:image" content="%s">\n'
                  '<meta name="twitter:title" content="%s">\n<meta name="twitter:description" content="%s">\n'
                  '<meta property="og:locale" content="en_IN">\n<link rel="canonical" href="%s%s">\n%s%s'
                  % (html.escape(CFG['title']), t, d, CFG['url'], out, og, og, t, d, CFG['url'], out, ldjson(out, meta, place),
                     '\n<meta name="robots" content="noindex">' if out in NOINDEX else '')) + head_extra
    # the What's new feed, for a reader's feed reader to find (build_feeds.py)
    head_extra += '\n<link rel="alternate" type="application/atom+xml" title="Off the Roll: what\'s new" href="%sfeed.xml">' % root
    cls = place.get('class', place['id'])
    # dashboards and explorers get the wider column (sir.css, body.wide)
    if meta.get('own_tabs') or out.endswith('explorer/'):
        cls += ' wide'
    # a long reading page gets the "On this page" rail in its left margin
    # (sir.js builds it from the h2s; sir.css keeps the margin for it)
    elif len(re.findall(r'<h2[\s>]', content)) >= 4 and 'class="report' not in content and place['id'] != 'home':
        cls += ' has-toc'
    # added after the column is chosen, so they do not change it: the dates and
    # alert form, and the code to embed the place's chart, before the page's
    # questions or its download strip
    extra = dates_block(out, place, root) + embed_block(out, place, root)
    if extra:
        for mark in ('<section class="page-faq"', '<section class="dlstrip"', '</main>'):
            if mark in content:
                content = content.replace(mark, extra + '\n' + mark, 1)
                break
        else:
            content += extra
    footer = cite_block(out, meta) + '\n' + footer
    page = (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<script src="%sassets/i18n.js"></script>\n<title>%s</title>\n<meta name="description" content="%s">\n'
        '<link rel="icon" href="%s">\n<link rel="manifest" href="%smanifest.webmanifest">\n<meta name="theme-color" content="#1f4e79">\n'
        '<link rel="apple-touch-icon" href="%sassets/app/apple-touch-icon.png">\n<link rel="stylesheet" href="%sassets/sir.css">%s\n</head>\n'
        '<body class="%s" data-place="%s" data-root="%s"%s>\n%s%s%s\n%s\n%s\n'
        '<script src="%sassets/dyslexia-font.js" data-accent="var(--fill-red)" data-radius="10px" defer></script>\n</body>\n</html>\n'
    ) % (root, html.escape(meta['title'], quote=False), html.escape(meta['description']), favicon(place['color']), root, root, root, head_extra,
         cls, place['id'], root, ''.join(' %s="%s"' % (k, html.escape(v)) for k, v in sorted(meta.get('body', {}).items())),
         header, nav, content, footer, scripts, root)
    return i18n_files(out, page)


def i18n_files(out, page):
    """Names on the page's i18n.js tag the translation files it loads besides
    the core: its group and one for each shared script with sentences of its
    own (scripts/build_i18n.py)."""
    names = build_i18n.manifest(out, page)
    if not names:
        return page
    return page.replace('assets/i18n.js"></script>', 'assets/i18n.js" data-i18n="%s"></script>' % names, 1)


# Every inline script on a page is written to a file of its own, named by a
# hash of its contents, so the Content-Security-Policy in netlify.toml can
# leave 'unsafe-inline' out of script-src: an injected <script> then does not
# run. JSON-LD and other data blocks stay inline, because a browser never runs
# them. The same script on 1,721 seat pages is one file.
PAGE_JS = os.path.join(ROOT, 'assets', 'js', 'page')
INLINE = re.compile(r'<script(?P<attrs>(?:(?!\bsrc=)[^>])*)>(?P<body>.*?)</script>', re.S)
page_js = {}


def externalise(text, rel):
    root = '../' * rel.count('/')

    def out(m):
        attrs, body = m.group('attrs'), m.group('body')
        t = re.search(r'\btype\s*=\s*["\']?([^"\'\s>]+)', attrs)
        if t and t.group(1).lower() not in ('text/javascript', 'module') or not body.strip():
            return m.group(0)
        h = hashlib.sha256(body.encode('utf-8')).hexdigest()[:16]
        page_js[h] = body
        return '<script src="%sassets/js/page/%s.js"%s></script>' % (root, h, attrs)
    return INLINE.sub(out, text)


def put(path, text, compare_unstamped=True):
    # newline='' keeps a calendar's CRLF line ends as they are, both ways
    old = open(path, encoding='utf-8', newline='').read() if os.path.exists(path) else None
    same = old is not None and (STAMP.sub('', old) == STAMP.sub('', text) if compare_unstamped else old == text)
    if same:
        return
    stale.append(os.path.relpath(path, ROOT))
    if not CHECK:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, 'w', encoding='utf-8', newline='').write(text)


# pages kept out of search: the form's thank-you page
NOINDEX = {'share/thanks/', 'support/thanks/', 'feedback/thanks/', 'alerts/thanks/'}


def ldjson(out, meta, place):
    """schema.org markup: the site on the front page, every other page as a
    page of it, and each place's overview as a dataset with its CSVs."""
    pub = {'@type': 'Organization', 'name': CFG['credit'], 'url': CFG['credit_url']}
    site = {'@type': 'WebSite', 'name': CFG['title'], 'url': CFG['url'], 'inLanguage': 'en-IN', 'publisher': pub}
    url = CFG['url'] + out
    if out == '':
        d = dict(site, **{'@context': 'https://schema.org', 'description': meta['description']})
    else:
        d = {'@context': 'https://schema.org', '@type': 'WebPage', 'name': meta['title'], 'description': meta['description'],
             'url': url, 'inLanguage': 'en-IN', 'isPartOf': site, 'publisher': pub}
        csvs = [x for x in place.get('downloads', []) if x[0].endswith('.csv')]
        first = (place.get('pages') or [[None]])[0][0]
        if csvs and out == first:
            d = {'@context': 'https://schema.org', '@type': 'Dataset', 'name': meta['title'], 'description': meta['description'],
                 'url': url, 'inLanguage': 'en-IN', 'isAccessibleForFree': True, 'creator': pub, 'publisher': pub,
                 'license': 'https://creativecommons.org/licenses/by/4.0/', 'spatialCoverage': 'India',
                 'distribution': [{'@type': 'DataDownload', 'encodingFormat': 'text/csv', 'name': x[1],
                                   'contentUrl': CFG['url'] + x[0]} for x in csvs]}
    return '<script type="application/ld+json">%s</script>' % json.dumps(d, ensure_ascii=False).replace('</', '<\\/')


def build():
    pages = []
    for d, _, files in os.walk(SRC):
        for f in files:
            if f != 'index.html':
                continue
            src = os.path.join(d, f)
            rel = os.path.relpath(src, SRC).replace(os.sep, '/')
            out = rel[:-len('index.html')]
            meta, content, scripts = read_source(src)
            put(os.path.join(ROOT, rel), externalise(shell(out, meta, contents(heading_ids(content)), scripts), rel))
            # a chart for another site's frame is not a page to search for
            if out not in NOINDEX and not out.startswith('embed/'):
                pages.append(out)
    # the 404 page is served at whatever address was asked for, so every link
    # and file in it is made absolute, and it is kept out of search engines
    meta, content, scripts = read_source(os.path.join(ROOT, 'site', '404.html'))
    page = externalise(shell('404.html', meta, contents(heading_ids(content)), scripts), '404.html')
    page = re.sub(r'(\s(?:href|src)=")(?!https?:|/|#|mailto:|data:|upi:|tel:)', r'\1/', page)
    page = page.replace('data-root=""', 'data-root="/"')
    page = re.sub(r'<link rel="canonical"[^>]*>\n?', '', page)
    if 'name="robots"' not in page:
        page = page.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">\n<meta name="robots" content="noindex">', 1)
    put(os.path.join(ROOT, '404.html'), page)
    # every page for search engines, and where to find the list
    put(os.path.join(ROOT, 'sitemap.xml'), '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join('<url><loc>%s%s</loc></url>\n' % (CFG['url'], html.escape(o)) for o in sorted(pages)) + '</urlset>\n', compare_unstamped=False)
    put(os.path.join(ROOT, 'robots.txt'), 'User-agent: *\nAllow: /\nDisallow: /data/india/raw/\nDisallow: /scripts/\n\nSitemap: %ssitemap.xml\n' % CFG['url'],
        compare_unstamped=False)
    # the phone section bar's lists, from the same config
    sites = {}
    for p in CFG['places']:
        if not p['pages']:
            continue
        sites[p['id']] = {'tabs': p.get('tabs', []), 'dash': p.get('dash', ''),
                          'pages': [x for x in p['pages'] if x[0] != p.get('dash')]}
    js = open(SIRJS, encoding='utf-8').read()
    js2 = re.sub(r'/\*sites\*/.*?/\*sites\*/', lambda m: '/*sites*/' + json.dumps(sites, ensure_ascii=False) + '/*sites*/', js, flags=re.S)
    if '/*sites*/' not in js:
        sys.exit('assets/sir.js has no /*sites*/ marker')
    put(SIRJS, js2, compare_unstamped=False)
    put(os.path.join(ROOT, 'data', 'search.json'), search_index(), compare_unstamped=False)
    # the What's new feed, the calendars, the data index and the frame rules
    put(os.path.join(ROOT, 'feed.xml'), BF.feed(CFG), compare_unstamped=False)
    for path, text in sorted(CAL_FILES.items()):
        put(os.path.join(ROOT, path), text, compare_unstamped=False)
    caldir = os.path.join(ROOT, 'calendar')
    for f in sorted(os.listdir(caldir)) if os.path.isdir(caldir) else []:
        if 'calendar/' + f not in CAL_FILES:
            stale.append('calendar/' + f)
            if not CHECK:
                os.remove(os.path.join(caldir, f))
    import stage_site
    pub = [f for f in stage_site.published() if f != 'data/index.json']
    put(os.path.join(ROOT, 'data', 'index.json'), BF.data_index(CFG, pub, {f: os.path.getsize(os.path.join(ROOT, f)) for f in pub}), compare_unstamped=False)
    put(os.path.join(ROOT, '_headers'), BF.headers(stage_site.PUBLIC_DIRS, stage_site.ROOT_FILES), compare_unstamped=False)
    for h, body in sorted(page_js.items()):
        put(os.path.join(PAGE_JS, h + '.js'), body.strip('\n') + '\n', compare_unstamped=False)
    # a script no page uses any more is removed, and --check reports it
    for f in sorted(os.listdir(PAGE_JS)) if os.path.isdir(PAGE_JS) else []:
        if f.endswith('.js') and f[:-3] not in page_js:
            stale.append(os.path.relpath(os.path.join(PAGE_JS, f), ROOT))
            if not CHECK:
                os.remove(os.path.join(PAGE_JS, f))


def search_index():
    """What the sitewide search looks through: every page, every
    constituency and district a finder can open, and the five Hyderabad
    seats in the part explorer. Names stay as the data spells them."""
    J = lambda p: json.load(open(os.path.join(ROOT, 'data', p), encoding='utf-8'))
    slug = lambda s: 'd-' + re.sub(r'^-|-$', '', re.sub(r'[^a-z0-9]+', '-', s.lower()))
    pages = []
    for p in CFG['places']:
        for h, label, _ in p['pages']:
            pages.append([p['id'], label, h])
        # pages reached only from the places menu, such as the reading page
        seen = {x[2] for x in pages}
        for h, label in p.get('menu', []):
            if h not in seen:
                pages.append([p['id'], label, h])
    # the front page's own pages, which no tab row lists
    pages += [['home', 'Left off the roll? What to do', 'help/', 'check my name removed deleted excluded left off struck off missing name voter list appeal helpline legal aid form 6 add back नाम हटाया मदद নাম বাদ সাহায্য'], ['home', 'All downloads, explained', 'downloads/'], ['home', 'About the data', 'about-the-data/', 'definitions glossary what counts mean names left off fall in the roll net change notices no-mapping discrepancy reasons per 100 margin lakh crore'], ['home', 'Share a list', 'share/'], ['home', 'Support our work', 'support/', 'donate contribute upi support fund'], ['home', 'How to use this site', 'guide/', 'help guide how to use navigate tour start'], ['home', 'Terms and privacy', 'terms/'], ['home', 'Corrections', 'corrections/'], ['home', 'Feedback and corrections', 'feedback/', 'feedback suggestion error mistake wrong figure report correction contact'], ['home', "What's new", 'updates/', 'new latest added changelog timeline updates']]
    rows = []
    for pid, folder, page in (('bihar', 'bihar', 'bihar/results/'), ('tn', 'tamilnadu', 'tamilnadu/'),
                              ('wb', 'westbengal', 'westbengal/'), ('kl', 'kerala', 'kerala/'), ('rj', 'rajasthan', 'rajasthan/'), ('dl', 'delhi', 'delhi/'),
                              ('gj', 'gujarat', 'gujarat/'), ('uk', 'uttarakhand', 'uttarakhand/'), ('as', 'assam', 'assam/'), ('ml', 'meghalaya', 'meghalaya/'), ('mn', 'manipur', 'manipur/'), ('od', 'odisha', 'odisha/')):
        for a in J(folder + '/constituencies.json'):
            # a state with constituency pages (make_seat_pages.py) links to the seat's own page
            href = '%s/seat/%d/' % (SEAT_PAGES[pid], a['ac']) if pid in SEAT_PAGES else page + '#ac-%d' % a['ac']
            rows.append([pid, 'ac', '%d. %s' % (a['ac'], a['name']), a['district'], href])
        for d in J(folder + '/districts.json'):
            # every district of these states has a page of its own (make_district_pages.py)
            rows.append([pid, 'd', d['district'], '', folder + '/district/' + slug(d['district'])[2:] + '/'])
    for pid, folder in (('ap', 'andhrapradesh'), ('cg', 'chhattisgarh'), ('mz', 'mizoram')):
        for d in J(folder + '/districts.json'):
            rows.append([pid, 'd', d['district'], '', folder + '/district/' + slug(d['district'])[2:] + '/'])
    for d in J('hyderabad/telangana.json')['districts']:
        rows.append(['hyd', 'd', d['district'], '', 'hyderabad/telangana/district/' + slug(d['district'])[2:] + '/'])
    for d in J('uttarpradesh/districts.json'):
        rows.append(['up', 'd', d['district'], '', 'uttarpradesh/district/' + slug(d['district'])[2:] + '/'])
    # Maharashtra's constituencies, each with its own page (its districts follow)
    for a in J('maharashtra/constituencies.json'):
        rows.append(['mh', 'ac', '%d. %s' % (a['ac'], a['name']), a['district'], 'maharashtra/seat/%d/' % a['ac']])
    for d in J('maharashtra/districts.json'):
        # the press note keeps three old names; a reader may type the new one,
        # and Bombay for Mumbai
        alias = ' '.join(x for x in (d['now'], 'Bombay' if d['district'].startswith('Mumbai') else '') if x)
        rows.append(['mh', 'd', d['district'], '', 'maharashtra/district/' + slug(d['district'])[2:] + '/'] + ([alias] if alias else []))
    for d in J('karnataka/districts.json'):
        # Bengaluru is four election districts; a reader types the city
        city = 'Bengaluru Bangalore' if d['bengaluru'] else ''
        rows.append(['ka', 'd', d['district'], '', 'karnataka/district/' + slug(d['district'])[2:] + '/'] + ([city] if city else []))
    for a in J('hyderabad/summary.json')['acs']:
        rows.append(['hyd', 'ac', a['name'], '', 'hyderabad/explorer/#' + a['name']])
    # the reading page: every piece, by title, outlet and author
    for it in J('india/reads.json')['items']:
        rows.append(['india', 'x', it['title'], '%s, %s' % (it['outlet'], it['date']), 'india/reading/', ' '.join(x for x in (it.get('authors') or '', it['shows']) if x)])
    # the disputes page: every item, and every court, party or body, place and
    # issue, which opens the page filtered to it
    D = J('india/disputes.json')
    facets = {}
    for sec in D['sections']:
        for it in sec['items']:
            rows.append(['india', 'x', it['headline'] or it['claim'][:100], '%s, %s' % (it['outlet'], it['date']),
                         'india/disputes/#d-' + it['id'], ' '.join([it['claim'], it['state'], it['court']] + it['places'] + it['actors'] + it['issues'])])
            for k, vals in (('court', [it['court']] if it['court'] else []), ('actor', it['actors']), ('place', it['places']), ('issue', it['issues'])):
                for v in vals:
                    facets[(k, v)] = facets.get((k, v), 0) + 1
    for (k, v), n in sorted(facets.items()):
        rows.append(['india', 'f', v, n, 'india/disputes/?%s=%s' % (k, quote(v))])
    # the RTI page: every application, by what was asked
    for it in J('india/rti.json')['items']:
        rows.append(['india', 'x', it['asked'][:100], '%s, %s' % (it['outlet'], it['published']),
                     'india/rti/#r-' + it['id'], ' '.join(['RTI', it['authority'], it['state'], it['answer']])])
    places = {p['id']: p['label'] for p in CFG['places']}
    return json.dumps({'places': places, 'pages': pages, 'rows': rows}, ensure_ascii=False, separators=(',', ':')) + '\n'


if __name__ == '__main__':
    build()
    if CHECK:
        if stale:
            print('STALE, run python3 scripts/build_site.py:', ', '.join(stale))
            sys.exit(1)
        print('OK: every page matches its source and the shell')
    else:
        print('wrote %d files' % len(stale) if stale else 'nothing to write')
