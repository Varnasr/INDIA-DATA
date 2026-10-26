#!/usr/bin/env python3
"""Every string a reader can see has a translation, and no translation loses
a figure or a link.

Two sources of keys, merged in `i18n/catalogue.json`:
- sentences built by page scripts, `L('template {x}', {x: ...})`, read here
  straight from the source, so a new sentence cannot ship without a key;
- fixed text in the markup, which `assets/i18n.js` translates by matching an
  element's inner HTML. Those keys need a browser to read the way the browser
  serialises them, so `scripts/i18n_collect.mjs` writes them and this check
  only confirms the file is there and every key in it is translated.

For each of Hindi, Urdu, Telugu, Tamil and Bengali (`i18n/<lang>.json`) this
fails on a missing or empty translation, a placeholder that is dropped or
invented, an HTML tag or link that is dropped or changed, a key the catalogue
no longer has, and an em dash, which the house style does not use in any
language. It also fails if `L()` is ever called with anything but a string
literal, because a key that is not a literal cannot be found by this check.

Pages load the dictionaries in pieces (`scripts/build_i18n.py`): a core, a
file for each shared script with sentences, and a file for the page's group.
So this also fails if the pieces are stale, if a page's i18n.js tag does not
name the files build_i18n.py says it needs, if a piece is not stamped (the
loader asks only for stamped files), and, walking every built page, if any
string the page shows or its scripts build is in none of the files it loads.
"""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_i18n  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LANGS = ['hi', 'ur', 'te', 'ta', 'bn']
# the analyses are the first folder of every page each place lists
SECTIONS = sorted({x[0].split('/')[0] for p in json.loads((ROOT / 'site' / 'places.json').read_text(encoding='utf-8'))['places'] for x in p['pages']})
SOURCES = [ROOT / 'index.html', *[f for d in SECTIONS for f in sorted((ROOT / d).rglob('index.html'))],
           ROOT / 'assets' / 'sir.js', ROOT / 'assets' / 'viz.js', ROOT / 'assets' / 'dash.js', ROOT / 'assets' / 'i18n.js', *sorted((ROOT / 'assets' / 'faq').glob('*.js')),
           # page scripts, which build_site.py moves out of the HTML
           *sorted((ROOT / 'assets' / 'js' / 'page').glob('*.js'))]
LIT = re.compile(r"(?<![\w.$])L\(\s*'((?:[^'\\]|\\.)*)'")
NONLIT = re.compile(r"(?<![\w.$])L\(\s*(?!'|\))")
PH = re.compile(r'\{(\w+)\}')
TAG = re.compile(r'<(/?[a-zA-Z][a-zA-Z0-9]*)((?:\s+(?:href|lang|dir)="[^"]*")*)[^>]*>')


def unescape(s):
    return re.sub(r"\\(.)", lambda m: {'n': '\n', 't': '\t'}.get(m.group(1), m.group(1)), s)


def source_keys():
    keys, bad = {}, []
    for f in SOURCES:
        text = f.read_text(encoding='utf-8')
        rel = f.relative_to(ROOT).as_posix()
        for m in LIT.finditer(text):
            keys.setdefault(unescape(m.group(1)), set()).add(rel)
        for m in NONLIT.finditer(text):
            line = text.count('\n', 0, m.start()) + 1
            bad.append('%s:%d  L() called without a string literal' % (rel, line))
    return keys, bad


def load_dict(lang):
    f = ROOT / 'i18n' / (lang + '.json')
    if not f.exists():
        return None
    return json.loads(f.read_text(encoding='utf-8'))


def reachable(cat):
    """Every built page against the files it loads. Returns failures."""
    fails = []
    _files, stale = build_i18n.build(check=True)
    for f in stale:
        fails.append('stale (run scripts/build_i18n.py): %s' % f)
    stamped = json.loads(re.search(r'/\*stamp\*/(.*?)/\*stamp\*/', (ROOT / 'assets' / 'i18n.js').read_text(encoding='utf-8'), re.S).group(1))
    split = {}
    for lang in LANGS:
        folder = ROOT / 'assets' / 'i18n' / lang
        split[lang] = {}
        for f in sorted(folder.glob('*.js')) if folder.is_dir() else []:
            rel = f.relative_to(ROOT).as_posix()
            if rel not in stamped:
                fails.append('%s is not stamped, so no page loads it (run scripts/stamp.py)' % rel)
            try:
                split[lang][f.stem] = build_i18n.read_split(f)
            except ValueError as e:
                fails.append(str(e))
        if 'core' not in split[lang]:
            fails.append('assets/i18n/%s/core.js is missing' % lang)
    n = 0
    collected = {build_i18n.local_folder(p[1:]) for e in cat.values() for p in e['pages']}
    for out, names, bundles, _own, every in build_i18n.page_needs(cat):
        n += 1
        page = '/' + out
        folder = build_i18n.local_folder(out)
        if folder and folder not in collected:
            fails.append('%s: no page in %s was collected, so its shell has no strings (re-run scripts/i18n_collect.mjs)' % (page, folder))
        if names is None:
            fails.append('%s: no i18n.js tag' % page)
            continue
        want = build_i18n.manifest(out, (ROOT / (out if out == '404.html' else out + 'index.html')).read_text(encoding='utf-8'))
        if ' '.join(names) != want:
            fails.append('%s: its i18n.js tag names %r where build_i18n.py gives %r (run scripts/build_site.py)' % (page, ' '.join(names), want))
        for lang in LANGS:
            have = set(split[lang].get('core', ()))
            for name in names:
                have |= split[lang].get(name, {}).keys()
            lost = sorted(k for k in every if k not in have)
            for k in lost[:3]:
                fails.append('%s in %s: %r is in none of the files the page loads' % (page, lang, k[:70]))
            if len(lost) > 3:
                fails.append('%s in %s: and %d more strings in none of its files' % (page, lang, len(lost) - 3))
    return fails, n


def tags(s):
    return sorted((t.lower(), a) for t, a in TAG.findall(s))


def main():
    fails = []
    keys, bad = source_keys()
    fails += bad
    cat_path = ROOT / 'i18n' / 'catalogue.json'
    if not cat_path.exists():
        sys.exit('FAIL - i18n/catalogue.json is missing: run scripts/i18n_collect.mjs')
    cat = json.loads(cat_path.read_text(encoding='utf-8'))
    missing = [k for k in keys if k not in cat]
    for k in missing:
        fails.append('not in the catalogue (re-run scripts/i18n_collect.mjs): %r' % k[:90])
    for lang in LANGS:
        d = load_dict(lang)
        if d is None:
            fails.append('i18n/%s.json is missing' % lang)
            continue
        for k in cat:
            v = d.get(k)
            if not v or not v.strip():
                fails.append('%s: no translation for %r' % (lang, k[:90]))
                continue
            if set(PH.findall(k)) != set(PH.findall(v)):
                fails.append('%s: placeholders differ for %r: %s vs %s' % (lang, k[:60], sorted(set(PH.findall(k))), sorted(set(PH.findall(v)))))
            if tags(k) != tags(v):
                fails.append('%s: tags or links differ for %r' % (lang, k[:60]))
            if '—' in v:
                fails.append('%s: em dash in the translation of %r' % (lang, k[:60]))
        for k in d:
            if k not in cat:
                fails.append('%s: %r is translated but no longer on any page' % (lang, k[:60]))
    more, pages = reachable(cat)
    fails += more
    if fails:
        print('FAIL: %d problem(s)' % len(fails))
        for f in fails[:80]:
            print('  ' + f)
        if len(fails) > 80:
            print('  ... and %d more' % (len(fails) - 80))
        sys.exit(1)
    print('PASS: %d strings (%d built by scripts), translated into %s, placeholders and links intact; '
          'every string on each of %d pages is in a file the page loads' % (len(cat), len(keys), ', '.join(LANGS), pages))


if __name__ == '__main__':
    main()
