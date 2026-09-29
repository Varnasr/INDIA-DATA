#!/usr/bin/env python3
"""Every ink clears AA on every surface it is painted on, in both themes.

The palette lives in `assets/sir.css`: a light `:root` block and a dark block
that redeclares the inks as well as the surfaces. The earlier dashboard's dark
block redefined the surfaces and almost none of the inks, so the same blue that
read at 6.3:1 on a white card was 2.9:1 on the dark one. This measures the
pairs the pages actually paint, in both themes, following `var()` chains and
falling back to the light block for anything the dark block leaves out, which
is what the browser does.
"""
import re
import sys
from pathlib import Path

CSS = (Path(__file__).resolve().parent.parent / 'assets' / 'sir.css').read_text()

# (ink, surface, what) — text painted on a surface somewhere in the pages.
PAIRS = [(ink, surf, '%s on %s' % (ink, surf))
         for ink in ['--ink', '--muted', '--navy', '--red', '--amber', '--female', '--male']
         for surf in ['--bg', '--soft', '--card']]
PAIRS += [('--bg', '--navy', 'the current tab and pressed buttons')]
# Fills that carry text: the alliance tags.
LITERAL = [('#1c1c1c', '--fill-nda', 'NDA tag'), ('#ffffff', '#1f6f43', 'INDIA tag'), ('#16112a', '--fill-other', 'Other tag')]
MIN = 4.5


def block(selector):
    m = re.search(re.escape(selector) + r'\s*\{(.*?)\}', CSS, re.S)
    if not m:
        sys.exit('FAIL - no `%s` block in assets/sir.css' % selector)
    return dict(re.findall(r'(--[a-z0-9-]+)\s*:\s*([^;}]+)', m.group(1)))


LIGHT = block(':root')
DARK = block(':root[data-theme="dark"]')
MEDIA = re.search(r'prefers-color-scheme:dark\)\{:root:not\(\[data-theme="light"\]\)\{(.*?)\}\}', CSS, re.S)
if not MEDIA or dict(re.findall(r'(--[a-z0-9-]+)\s*:\s*([^;}]+)', MEDIA.group(1))) != DARK:
    sys.exit('FAIL - the prefers-color-scheme dark block and the [data-theme="dark"] block have drifted apart')


def resolve(v, theme):
    v = v.strip()
    if v.startswith('--'):
        v = theme.get(v, LIGHT.get(v))
        if v is None:
            sys.exit('FAIL - token used by this check and declared nowhere')
    m = re.fullmatch(r'var\(\s*(--[a-z0-9-]+)\s*\)', v)
    return resolve(m.group(1), theme) if m else v


def lum(hexv):
    h = hexv.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    rgb = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


fails, n = [], 0
for name, theme in [('light', LIGHT), ('dark', DARK)]:
    for ink, surf, what in PAIRS + LITERAL:
        a, b = resolve(ink, theme), resolve(surf, theme)
        r = ratio(a, b)
        n += 1
        if r < MIN:
            fails.append('%s theme: %s = %s on %s = %s is %.2f:1' % (name, ink, a, surf, b, r))
if fails:
    print('FAIL: %d of %d pairs under %.1f:1' % (len(fails), n, MIN))
    for f in fails:
        print('  ' + f)
    sys.exit(1)
print('PASS: %d ink-on-surface pairs clear %.1f:1 in both themes' % (n, MIN))
