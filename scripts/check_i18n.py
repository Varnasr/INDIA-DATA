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

For each of Hindi, Urdu and Telugu (`assets/i18n/<lang>.js`) this fails on a
missing or empty translation, a placeholder that is dropped or invented, an
HTML tag or link that is dropped or changed, a key the catalogue no longer
has, and an em dash, which the house style does not use in any language.
It also fails if `L()` is ever called with anything but a string literal,
because a key that is not a literal cannot be found by this check.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGS = ['hi', 'ur', 'te']
SOURCES = [ROOT / 'index.html', *sorted((ROOT / 'india').rglob('index.html')), *sorted((ROOT / 'bihar').rglob('index.html')), *sorted((ROOT / 'hyderabad').rglob('index.html')),
           ROOT / 'assets' / 'sir.js', ROOT / 'assets' / 'dash.js', ROOT / 'assets' / 'i18n.js', *sorted((ROOT / 'assets' / 'faq').glob('*.js'))]
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
    f = ROOT / 'assets' / 'i18n' / (lang + '.js')
    if not f.exists():
        return None
    body = f.read_text(encoding='utf-8')
    m = re.search(r'window\.SIR_DICT\s*=\s*(\{.*\})\s*;\s*$', body, re.S)
    if not m:
        sys.exit('FAIL - %s does not have the form window.SIR_DICT = {...};' % f.name)
    return json.loads(m.group(1))


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
            fails.append('assets/i18n/%s.js is missing' % lang)
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
    if fails:
        print('FAIL: %d problem(s)' % len(fails))
        for f in fails[:80]:
            print('  ' + f)
        if len(fails) > 80:
            print('  ... and %d more' % (len(fails) - 80))
        sys.exit(1)
    print('PASS: %d strings (%d built by scripts), translated into %s, placeholders and links intact'
          % (len(cat), len(keys), ', '.join(LANGS)))


if __name__ == '__main__':
    main()
