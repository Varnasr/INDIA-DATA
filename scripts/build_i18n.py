#!/usr/bin/env python3
"""Splits each language's dictionary into the files a page loads.

    python3 scripts/build_i18n.py           # write assets/i18n/<lang>/*.js
    python3 scripts/build_i18n.py --check   # fail if any of them is stale

Every translation is kept in i18n/<lang>.json, one file per language, which is
what a correction is written into and what check_i18n.py checks. Pages do not
load it. A page in Hindi loads three kinds of file from assets/i18n/hi/, named
in the data-i18n attribute that build_site.py writes on the page's i18n.js tag:

  * core.js, on every page: the strings in the scripts every page loads
    (CORE_SCRIPTS) and the strings a third or more of the page groups use,
    which is the header, the menus, the footer and the common labels;
  * one file per shared script with sentences of its own, such as
    faq-india.js for assets/faq/india.js, on the pages that load that script;
  * one file for the page's group (group_of), holding everything else the
    pages in that group show or build.

A page's strings are its fixed text, as i18n_collect.mjs read it into
i18n/catalogue.json, and every L('...') in the scripts it loads, so a sentence a
script builds after the page has loaded is in a file the page has already
loaded. check_i18n.py walks every built page and fails if any of its strings is
in none of the files it loads.

Run it after i18n_collect.mjs, after build_site.py, and after any change to
i18n/<lang>.json; then stamp.py, which gives each file its ?v= address. The
loader in assets/i18n.js asks only for files that stamp.py has stamped, so a
group with no strings of its own (the constituency and district pages) has no
file and costs no request.
"""
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stage_site  # noqa: E402  the page folders

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS = ['hi', 'ur', 'te', 'ta', 'bn']
SRC = os.path.join(ROOT, 'i18n')
OUT = os.path.join(ROOT, 'assets', 'i18n')
# loaded on every page, so their strings go in the core
CORE_SCRIPTS = ('assets/i18n.js', 'assets/sir.js', 'assets/viz.js')
# places whose pages are each a group of their own, because each is a
# different analysis; every other place's pages share one group
SPLIT = ('india', 'bihar', 'hyderabad')
# a string used by this share of the groups or more goes in the core
CORE_SHARE = 1 / 3
LIT = re.compile(r"(?<![\w.$])L\(\s*'((?:[^'\\]|\\.)*)'")
SCRIPT = re.compile(r'<script\b[^>]*\bsrc="([^"?#]+)')
I18N_TAG = re.compile(r'<script src="[^"]*assets/i18n\.js(?:\?v=[0-9a-f]+)?"(?: data-i18n="([^"]*)")?></script>')
HEAD = 'Object.assign(window.SIR_DICT = window.SIR_DICT || {}, '


def unescape(s):
    return re.sub(r"\\(.)", lambda m: {'n': '\n', 't': '\t'}.get(m.group(1), m.group(1)), s)


def group_of(out):
    """The group of the page at site path `out` ('' is the front page,
    'bihar/results/' a page). None for the 404 page, which loads the core
    alone."""
    if out == '404.html':
        return None
    parts = [p for p in out.split('/') if p]
    if not parts:
        return 'home'
    # the constituency and district pages of a place share one group: their
    # own text stays English, and only their shell is translated
    if local_folder(out):
        return parts[0] + '-local'
    if parts[0] in SPLIT and len(parts) > 1:
        return parts[0] + '-' + parts[1]
    return parts[0]


LOCAL = re.compile(r'^(.*/(?:seat|district)/)[^/]+/$')


def local_folder(out):
    """'bihar/seat/' for 'bihar/seat/12/'; None for any other page. Every
    page in such a folder carries the same shell, so i18n_collect.mjs reads
    only the first of them, and the others are given its strings."""
    m = LOCAL.match(out)
    return m.group(1) if m else None


def bundle_of(rel):
    """'assets/faq/india.js' -> 'faq-india'."""
    return rel[len('assets/'):-len('.js')].replace('/', '-')


_keys = {}


def script_keys(rel):
    """The L('...') keys in a script, by its path from the repository root."""
    if rel not in _keys:
        with open(os.path.join(ROOT, rel), encoding='utf-8') as fh:
            _keys[rel] = {unescape(m.group(1)) for m in LIT.finditer(fh.read())}
    return _keys[rel]


def local_scripts(out, html):
    """The scripts on this site that a page loads, by their path from the
    repository root. `out` is the page's site path."""
    here = os.path.dirname(out) if out == '404.html' else out.rstrip('/')
    got = []
    for src in SCRIPT.findall(html):
        if '://' in src or src.startswith('//'):
            continue
        rel = os.path.normpath(src.lstrip('/') if src.startswith('/') else os.path.join(here, src)).replace(os.sep, '/')
        if os.path.isfile(os.path.join(ROOT, rel)) and rel not in got:
            got.append(rel)
    return got


def is_bundle(rel):
    return rel not in CORE_SCRIPTS and not rel.startswith('assets/js/page/') and bool(script_keys(rel))


def manifest(out, html):
    """What build_site.py writes in the page's data-i18n attribute: the
    page's group, then a bundle for each shared script with strings."""
    g = group_of(out)
    return ' '.join(([g] if g else []) + [bundle_of(r) for r in local_scripts(out, html) if is_bundle(r)])


def pages():
    """Every built page, as (site path, file)."""
    yield '', os.path.join(ROOT, 'index.html')
    yield '404.html', os.path.join(ROOT, '404.html')
    for d in stage_site.PAGES:
        for base, dirs, files in os.walk(os.path.join(ROOT, d)):
            dirs.sort()
            if 'index.html' in files:
                yield os.path.relpath(base, ROOT).replace(os.sep, '/') + '/', os.path.join(base, 'index.html')


def catalogue():
    with open(os.path.join(ROOT, 'i18n', 'catalogue.json'), encoding='utf-8') as fh:
        return json.load(fh)


def page_needs(cat):
    """For every built page: (site path, the data-i18n names it carries, the
    bundles it loads, its own keys, every key it shows). A constituency or
    district page's own keys are those of the page i18n_collect.mjs read in
    its folder."""
    markup, folders = {}, {}
    for k, e in cat.items():
        for p in e['pages']:
            markup.setdefault(p, set()).add(k)
            f = local_folder(p[1:])
            if f:
                folders.setdefault(f, set()).add(k)
    for out, path in pages():
        with open(path, encoding='utf-8') as fh:
            html = fh.read()
        m = I18N_TAG.search(html)
        names = (m.group(1) or '').split() if m else None
        f = local_folder(out)
        own, bundles, every = set(folders.get(f, ()) if f else markup.get('/' + out, ())), [], set()
        for rel in local_scripts(out, html):
            ks = script_keys(rel) & cat.keys()
            every |= ks
            if rel.startswith('assets/js/page/'):
                own |= ks
            elif is_bundle(rel):
                bundles.append(rel)
        own &= cat.keys()
        yield out, names, bundles, own, own | every


def plan(cat):
    """{file name: set of keys}, for the core, every bundle and every group."""
    needs = list(page_needs(cat))
    core = set()
    for rel in CORE_SCRIPTS:
        core |= script_keys(rel) & cat.keys()
    groups_of_key, groups = {}, set()
    for out, _n, _b, own, _e in needs:
        g = group_of(out)
        if g is None:
            continue
        groups.add(g)
        for k in own:
            groups_of_key.setdefault(k, set()).add(g)
    floor = math.ceil(len(groups) * CORE_SHARE)
    core |= {k for k, gs in groups_of_key.items() if len(gs) >= floor}
    files = {'core': core}
    for _o, _n, bundles, _own, _e in needs:
        for rel in bundles:
            files.setdefault(bundle_of(rel), (script_keys(rel) & cat.keys()) - core)
    for out, _n, bundles, own, _e in needs:
        g = group_of(out)
        if g is None:
            continue
        if g in files and g not in groups:
            sys.exit('FAIL - group %r has the name of a bundle; rename one' % g)
        have = set()
        for rel in bundles:
            have |= files[bundle_of(rel)]
        files.setdefault(g, set()).update(own - core - have)
    return {k: v for k, v in files.items() if v}, needs


def load_source(lang):
    with open(os.path.join(SRC, lang + '.json'), encoding='utf-8') as fh:
        return json.load(fh)


def render(d, keys):
    return HEAD + json.dumps({k: d[k] for k in sorted(keys) if k in d}, ensure_ascii=False, separators=(',', ':')) + ');\n'


def read_split(path):
    """The dictionary in one written file."""
    with open(path, encoding='utf-8') as fh:
        body = fh.read()
    if not body.startswith(HEAD) or not body.endswith(');\n'):
        raise ValueError('%s does not have the form %s{...});' % (os.path.relpath(path, ROOT), HEAD))
    return json.loads(body[len(HEAD):-3])


def build(check):
    cat = catalogue()
    files, _ = plan(cat)
    stale = []
    for lang in LANGS:
        d = load_source(lang)
        folder = os.path.join(OUT, lang)
        want = {name + '.js': render(d, keys) for name, keys in files.items()}
        have = set(os.listdir(folder)) if os.path.isdir(folder) else set()
        for f, text in sorted(want.items()):
            path = os.path.join(folder, f)
            old = open(path, encoding='utf-8').read() if f in have else None
            if old != text:
                stale.append('assets/i18n/%s/%s' % (lang, f))
                if not check:
                    os.makedirs(folder, exist_ok=True)
                    open(path, 'w', encoding='utf-8').write(text)
        for f in sorted(have - set(want)):
            stale.append('assets/i18n/%s/%s (no longer used)' % (lang, f))
            if not check:
                os.remove(os.path.join(folder, f))
    # the dictionaries are no longer loaded whole
    for f in sorted(os.listdir(OUT)):
        if f.endswith('.js'):
            stale.append('assets/i18n/%s (the whole dictionary; it is i18n/%s.json now)' % (f, f[:-3]))
            if not check:
                os.remove(os.path.join(OUT, f))
    return files, stale


if __name__ == '__main__':
    CHECK = '--check' in sys.argv
    files, stale = build(CHECK)
    if CHECK:
        if stale:
            print('STALE: %d file(s): %s\nRun python3 scripts/build_i18n.py' % (len(stale), ', '.join(stale[:10])))
            sys.exit(1)
        print('OK: the split dictionaries match i18n/<lang>.json and the pages')
    else:
        print('%d files per language (core, %d bundles and groups); %s' % (
            len(files), len(files) - 1, '%d written or removed' % len(stale) if stale else 'nothing changed'))
