"""Cache busting: give every file a page loads an address that changes when
the file does.

A browser, a phone above all, can keep a script or a data file it fetched
earlier and pair it with a page from a newer deploy. Each reference is
stamped with a short hash of the file's content (`sir.js?v=3f9a01c2`), so a
changed file has a new address and cannot be served from a cache, while an
unchanged one keeps its address and stays cached.

It also writes the build's hash into `assets/i18n.js` (`window.SIR_BUILD`)
and into every page's "Cite this page" box.

Three kinds of reference:

  * `src` and `href` in every page, to a local script, stylesheet, image,
    download or data file;
  * the data files the pages fetch through `SIR.json`, and every piece of
    the translation dictionaries under assets/i18n/<lang>/ that
    `assets/i18n.js` loads (scripts/build_i18n.py writes them): their hashes
    are written into `assets/i18n.js` as `window.SIR_V`, which loads first on
    every page, and the loader asks only for a piece listed there;
  * the stamps in a page are taken after that, so the page's own reference
    to `i18n.js` changes when any data file does.

Netlify runs this as its build command and the Pages workflow runs it before
staging, so a deploy is always stamped and nobody has to remember. Run it by
hand to see the result locally; `--check` fails if anything is stale.
"""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECK = '--check' in sys.argv
SKIP_DIRS = {'.git', '.github', 'archive', 'scripts', 'node_modules', 'raw'}
EXT = ('.js', '.css', '.json', '.csv', '.pdf', '.pptx', '.png', '.svg', '.webp', '.jpg')
I18N = os.path.join(ROOT, 'assets', 'i18n.js')
MARK = re.compile(r'/\*stamp\*/.*?/\*stamp\*/', re.S)
REF = re.compile(r'''((?:src|href)=")([^"#?]+?\.(?:js|css|json|csv|pdf|pptx|png|svg|webp|jpg))(?:\?v=[0-9a-f]+)?(")''')
changed = []


def h(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()[:8]


def walk(top, exts):
    for d, dirs, files in os.walk(top):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        for f in sorted(files):
            if f.endswith(exts):
                yield os.path.join(d, f)


def put(path, text):
    if open(path, encoding='utf-8').read() == text:
        return
    changed.append(os.path.relpath(path, ROOT))
    if not CHECK:
        open(path, 'w', encoding='utf-8').write(text)


# 1. what the scripts fetch: every data file and every piece of every
# dictionary, assets/i18n/<lang>/<name>.js, at any depth
fetched = list(walk(os.path.join(ROOT, 'data'), ('.json',))) + list(walk(os.path.join(ROOT, 'assets', 'i18n'), ('.js',)))
V = {os.path.relpath(p, ROOT).replace(os.sep, '/'): h(p) for p in fetched}
src = open(I18N, encoding='utf-8').read()
if not MARK.search(src):
    sys.exit('assets/i18n.js has no /*stamp*/ marker')
# the build's hash, for the citation box on every page: one hash over every
# data file, dictionary, script and stylesheet, so it changes with any of them
ASSETS = {os.path.relpath(p, ROOT).replace(os.sep, '/'): h(p) for p in walk(os.path.join(ROOT, 'assets'), ('.js', '.css'))
          if not p.endswith(os.sep + 'i18n.js')}
BUILD = hashlib.sha256(json.dumps([V, ASSETS], sort_keys=True).encode('utf-8')).hexdigest()[:12]
BMARK = re.compile(r'/\*build\*/.*?/\*build\*/', re.S)
if not BMARK.search(src):
    sys.exit('assets/i18n.js has no /*build*/ marker')
src = BMARK.sub(lambda m: '/*build*/' + json.dumps(BUILD) + '/*build*/', src)
CITE = re.compile(r'(<span class="cite-build">)[0-9a-f]*(</span>)')
put(I18N, MARK.sub(lambda m: '/*stamp*/' + json.dumps(V, separators=(',', ':'), sort_keys=True) + '/*stamp*/', src))
# 2. every page's own references, resolved against the page's folder
for page in walk(ROOT, ('.html',)):
    here = os.path.dirname(page)
    text = open(page, encoding='utf-8').read()

    def stamp(m):
        ref = m.group(2)
        if '://' in ref or ref.startswith('//'):
            return m.group(0)
        f = os.path.normpath(os.path.join(ROOT, ref.lstrip('/')) if ref.startswith('/') else os.path.join(here, ref))
        if not os.path.isfile(f):
            return m.group(0)
        return m.group(1) + ref + '?v=' + h(f) + m.group(3)
    put(page, CITE.sub(lambda m: m.group(1) + BUILD + m.group(2), REF.sub(stamp, text)))

if CHECK:
    if changed:
        print('STALE stamps in:', ', '.join(changed), '\nRun python3 scripts/stamp.py')
        sys.exit(1)
    print('OK: every reference carries its file\'s current stamp')
else:
    print('stamped %d files' % len(changed) if changed else 'nothing to stamp')
