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
import html
import json
import os
import re
import sys
from urllib.parse import quote

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
SIRJS = os.path.join(ROOT, 'assets', 'sir.js')
ICONS = json.loads(re.search(r'var ICONS = (\{.*?\});', open(SIRJS, encoding='utf-8').read()).group(1))
STAMP = re.compile(r'\?v=[0-9a-f]{8}')
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


# Which roll a state's figures come from, and when the next one is due, for
# the line under the kicker on every page of that state. The roll is read
# from data/india/states.json (a final roll only when its electors are held),
# the next date from the latest schedule step in data/india/process.json, and
# "today" is process.json's as_of, the day the schedules were last checked,
# so the build stays the same from one run to the next. The English sentence
# is in the markup, and sir.js swaps in its translation through L().
ASOF_LATER = {'Karnataka': '2026-10-09'}   # a roll published after the draft and before the final
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
    due = sched['steps'][-1].get('final') if sched else None
    # a date moved since the last order, as reported, replaces the order's
    moved = sorted((x for x in P.get('reported_dates', []) if x['state'] == name and x.get('final')), key=lambda x: x['date'])
    if moved:
        due = moved[-1]['final']
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
    'draft-past': 'Figures as of {d}, when the draft roll was published. The final roll was due on {n}, and we have not found it published.',
    'latest-due': 'Figures as of {d}, a roll published while claims and notices were being heard. The final roll is due on {n}.',
    'nodraft': 'No draft roll has been published yet. It is due on {n}.',
}


def asof_html(a):
    if not a:
        return ''
    fmt = lambda iso: '%d %s %s' % (int(iso[8:]), 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()[int(iso[5:7]) - 1], iso[:4]) if iso else ''
    if a['k'] not in ASOF_EN:
        raise SystemExit('FAIL - no sentence for the roll stage %r' % a['k'])
    text = ASOF_EN[a['k']].format(d=fmt(a.get('d')), n=fmt(a.get('n')))
    attrs = ''.join(' data-%s="%s"' % (x, a[x]) for x in ('k', 'd', 'n') if a.get(x))
    return '<p class="asof" data-no-i18n%s>%s</p>' % (attrs, html.escape(text))


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
    FULL = {'bihar', 'hyd', 'tn', 'ka', 'wb', 'kl', 'rj', 'up', 'dl', 'mh', 'gj', 'uk', 'as'}
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
            # site exists rather than reloading the page a reader is on
            items.append(link(p, '#why-this-site-exists' if p['id'] == 'home' else None))
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
    items.append(fold('All States and Union Territories', subs, bool(place.get('zone')), ' states'))
    # the front page closes the menu, under a rule, rather than sitting
    # between the pages most readers come for and the places
    about = [i for i in items if i.startswith('<a ')]
    items = [i for i in items if not i.startswith('<a ')] + ['<div class="about" data-i18n-each>%s</div>' % ''.join(about)]
    # the pages most readers come for, at the top of the menu whatever the place
    quick = '<div class="ql" data-i18n-each>%s</div>' % ''.join(
        '<a href="%s%s"%s>%s</a>' % (root, h, ' aria-current="page"' if h == here else '', html.escape(t)) for h, t in
        (('india/brief/', 'The SIR in brief'), ('india/constituencies/', 'Find a constituency'), ('help/', 'If your name was left off'), ('india/disputes/', 'Protests and disputes'), ('india/rti/', 'RTI replies'), ('india/reading/', 'Further reading and viewing'),
         ('india/women/', 'Women'), ('india/numbers/', 'The SIR in numbers')))
    # "Start here" is its own menu beside Places, so Places holds only places
    about = ''.join(i for i in items if i.startswith('<div class="about"'))
    items = [i for i in items if not i.startswith('<div class="about"')]
    start = ('<details class="dl start"><summary class="btn" aria-label="Start here">%s <span class="lbl">Start here</span></summary>'
             '<div class="menu"><div data-i18n-each>%s%s</div></div></details>' % (STAR, quick, about))
    current = place['label'] if place['id'] != 'home' else 'Places'
    places = ('<details class="dl places"><summary class="btn" aria-label="Places">%s <span class="lbl-place">%s</span></summary>'
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
    if not here.startswith('share/'):
        fab = ('<a class="fab fab-share" href="%sshare/">%s<span>Share a list</span></a>' % (root, svg(ICONS['i24']))) + fab
    fab = '<div class="fabs">%s</div>' % fab if fab else ''
    footer = ('<footer data-i18n-each><span>Research by <a href="%s">%s</a>. Only totals are published, never names or EPIC numbers.</span>'
              ' · <a href="%s#why-this-site-exists">About this site</a> · <a href="%shelp/">If your name was left off</a> · <a href="%sdownloads/">Downloads</a> · <a href="%sshare/">Share a list with us</a> · <a href="%sterms/">Terms and privacy</a>'
              ' · <a href="mailto:%s">%s</a></footer>' % (CFG['credit_url'], html.escape(CFG['credit']), root or './', root, root, root, root, CFG['email'], CFG['email']))
    footer += ('\n' + fab) if fab else ''
    # every page that loads sir.js gets viz.js after it: SIR.chart and the
    # dashboards hand ranked lists and side-by-side measures to it
    if 'assets/sir.js' in scripts and 'assets/viz.js' not in scripts:
        scripts = re.sub(r'(<script src="[^"]*assets/sir\.js"></script>)', lambda m: m.group(1) + '\n' + m.group(1).replace('sir.js', 'viz.js'), scripts, count=1)
    if place['id'] != 'home':
        content = re.sub(r'(<div class="page-head"[^>]*>)', lambda m: m.group(1) + '<p class="kicker">%s</p>' % html.escape(place['label']) + asof_html(asof(place)), content, count=1)
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
                  '<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:image" content="%s">'
                  % (html.escape(CFG['title']), t, d, CFG['url'], out, og, og)) + head_extra
    cls = place.get('class', place['id'])
    # dashboards and explorers get the wider column (sir.css, body.wide)
    if meta.get('own_tabs') or out.endswith('explorer/'):
        cls += ' wide'
    # a long reading page gets the "On this page" rail in its left margin
    # (sir.js builds it from the h2s; sir.css keeps the margin for it)
    elif len(re.findall(r'<h2[\s>]', content)) >= 4 and 'class="report' not in content and place['id'] != 'home':
        cls += ' has-toc'
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<script src="%sassets/i18n.js"></script>\n<title>%s</title>\n<meta name="description" content="%s">\n'
        '<link rel="icon" href="%s">\n<link rel="manifest" href="%smanifest.webmanifest">\n<meta name="theme-color" content="#1f4e79">\n'
        '<link rel="apple-touch-icon" href="%sassets/app/apple-touch-icon.png">\n<link rel="stylesheet" href="%sassets/sir.css">%s\n</head>\n'
        '<body class="%s" data-place="%s" data-root="%s">\n%s%s%s\n%s\n%s\n'
        '<script src="%sassets/dyslexia-font.js" data-accent="var(--fill-red)" data-radius="10px" defer></script>\n</body>\n</html>\n'
    ) % (root, html.escape(meta['title'], quote=False), html.escape(meta['description']), favicon(place['color']), root, root, root, head_extra,
         cls, place['id'], root, header, nav, content, footer, scripts, root)


def put(path, text, compare_unstamped=True):
    old = open(path, encoding='utf-8').read() if os.path.exists(path) else None
    same = old is not None and (STAMP.sub('', old) == STAMP.sub('', text) if compare_unstamped else old == text)
    if same:
        return
    stale.append(os.path.relpath(path, ROOT))
    if not CHECK:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, 'w', encoding='utf-8').write(text)


def build():
    for d, _, files in os.walk(SRC):
        for f in files:
            if f != 'index.html':
                continue
            src = os.path.join(d, f)
            rel = os.path.relpath(src, SRC).replace(os.sep, '/')
            out = rel[:-len('index.html')]
            meta, content, scripts = read_source(src)
            put(os.path.join(ROOT, rel), shell(out, meta, heading_ids(content), scripts))
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
    # the front page's own pages, which no tab row lists
    pages += [['home', 'If your name was left off', 'help/'], ['home', 'All downloads, explained', 'downloads/'], ['home', 'Share a list with us', 'share/'], ['home', 'Terms and privacy', 'terms/']]
    rows = []
    for pid, folder, page in (('bihar', 'bihar', 'bihar/results/'), ('tn', 'tamilnadu', 'tamilnadu/'),
                              ('wb', 'westbengal', 'westbengal/'), ('kl', 'kerala', 'kerala/'), ('rj', 'rajasthan', 'rajasthan/'), ('dl', 'delhi', 'delhi/'),
                              ('gj', 'gujarat', 'gujarat/'), ('uk', 'uttarakhand', 'uttarakhand/')):
        for a in J(folder + '/constituencies.json'):
            rows.append([pid, 'ac', '%d. %s' % (a['ac'], a['name']), a['district'], page + '#ac-%d' % a['ac']])
        for d in J(folder + '/districts.json'):
            rows.append([pid, 'd', d['district'], '', page + '#' + slug(d['district'])])
    for d in J('uttarpradesh/districts.json'):
        rows.append(['up', 'd', d['district'], '', 'uttarpradesh/#' + slug(d['district'])])
    for d in J('maharashtra/districts.json'):
        # the press note keeps three old names; a reader may type the new one,
        # and Bombay for Mumbai
        alias = ' '.join(x for x in (d['now'], 'Bombay' if d['district'].startswith('Mumbai') else '') if x)
        rows.append(['mh', 'd', d['district'], '', 'maharashtra/#' + slug(d['district'])] + ([alias] if alias else []))
    for d in J('karnataka/districts.json'):
        # Bengaluru is four election districts; a reader types the city
        city = 'Bengaluru Bangalore' if d['bengaluru'] else ''
        rows.append(['ka', 'd', d['district'], '', 'karnataka/#' + slug(d['district'])] + ([city] if city else []))
    for a in J('hyderabad/summary.json')['acs']:
        rows.append(['hyd', 'ac', a['name'], '', 'hyderabad/explorer/#' + a['name']])
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
