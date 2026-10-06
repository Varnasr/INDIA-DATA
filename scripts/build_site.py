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
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'site', 'pages')
CHECK = '--check' in sys.argv
CFG = json.load(open(os.path.join(ROOT, 'site', 'places.json'), encoding='utf-8'))
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
DOWN = svg('<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>')
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


def shell(out, meta, content, scripts):
    """The whole page for site path `out` (e.g. 'bihar/results/')."""
    depth = out.count('/')
    root = '../' * depth
    place = PLACES[meta['place']]
    here = out
    # the places menu: every analysis, the current one marked
    items = []
    for p in CFG['places']:
        href = root + (p['pages'][0][0] if p['pages'] else '')
        cur = ' aria-current="true"' if p['id'] == place['id'] else ''
        items.append('<a href="%s"%s>%s</a>' % (href or './', cur, html.escape(p['label'])))
        # a page worth reaching from anywhere sits under its place
        for h, t in p.get('menu', []):
            sub = ' aria-current="page"' if h == here else ''
            items.append('<a class="sub" href="%s%s"%s>%s</a>' % (root, h, sub, html.escape(t)))
    current = place['label'] if place['id'] != 'home' else 'Places'
    places = ('<details class="dl places"><summary class="btn" aria-label="Places">%s <span class="lbl-place">%s</span></summary>'
              '<div class="menu" data-i18n-each>%s</div></details>' % (PIN, html.escape(current), ''.join(items)))
    dl = ''
    if place.get('downloads'):
        links = ''.join('<a href="%s%s"%s>%s</a>' % (root, h, ' download' if d else '', html.escape(t)) for h, t, d in place['downloads'])
        dl = ('<details class="dl"><summary class="btn">%s <span class="lbl">Downloads</span></summary>'
              '<div class="menu" data-i18n-each>%s</div></details>' % (DOWN, links))
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
        '    <a class="logo" href="%s"><span class="logo-icon">%s</span><%s class="titles"><span class="h-title">%s</span>'
        '<span class="subtitle">%s</span></%s></a>\n'
        '    <div class="controls" data-dyslexia-slot data-dyslexia-before=".theme">\n      %s\n      %s\n      %s\n'
        '      <button type="button" class="theme" aria-pressed="false">%s <span class="lbl">Dark</span></button>\n'
        '      %s\n'
        '    </div>\n  </div>\n</header>\n'
    ) % (place['band'], root or './', LOGO, tag, html.escape(CFG['title']), html.escape(place['subtitle']), tag, find, places, dl, MOON, prn)
    nav = ''
    if place['pages'] and not meta.get('own_tabs'):
        tabs = []
        for h, label, icon in place['pages']:
            cur = ' aria-current="page"' if h == here else ''
            tabs.append('<a class="nav-tab" href="%s%s"%s>%s %s</a>' % (root, h, cur, svg(ICONS[icon]), html.escape(label)))
        nav = '<nav class="nav-tabs" aria-label="%s">%s</nav>\n' % (place['nav_label'], ''.join(tabs))
    # data-i18n-each: the credit and the link are translated apart, so the
    # key does not change with the page's depth.
    footer = ('<footer data-i18n-each><span>Research by <a href="%s">%s</a>. Only totals are published, never names or EPIC numbers.</span>'
              ' · <a href="%s">About this site</a> · <a href="%sterms/">Terms and privacy</a>'
              ' · <a href="mailto:%s">%s</a></footer>' % (CFG['credit_url'], html.escape(CFG['credit']), root or './', root, CFG['email'], CFG['email']))
    # every page that loads sir.js gets viz.js after it: SIR.chart and the
    # dashboards hand ranked lists and side-by-side measures to it
    if 'assets/sir.js' in scripts and 'assets/viz.js' not in scripts:
        scripts = re.sub(r'(<script src="[^"]*assets/sir\.js"></script>)', lambda m: m.group(1) + '\n' + m.group(1).replace('sir.js', 'viz.js'), scripts, count=1)
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
    elif len(re.findall(r'<h2[\s>]', content)) >= 4 and 'class="report' not in content:
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
