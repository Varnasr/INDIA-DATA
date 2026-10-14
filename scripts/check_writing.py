"""The owner's writing rules, checked over everything a reader sees that the
site wrote itself.

    python3 scripts/check_writing.py

Reads the text of every page source in site/pages (outside scripts and
styles), the strings in every page script and in assets/*.js and
assets/faq/*.js, and the string values of the published JSON under data/
(raw/ folders excluded). Fails on an em dash, an en dash between words,
"rather than", "not only", ", not a/an/the", a semicolon between words in the
pages' own prose, and the owner's banned words.

What it cannot see is left to the reader: a fragment, a flourish, an
epigram ending, a sentence hinged on a colon. Labels such as chart titles
("Kerala: the roll ...") are allowed, which is why colons are not checked.

Quotations are the source's words and are left alone. In the JSON that means
every value under a key in QUOTED (headlines, titles, quotes, laws, contacts,
lists of places). A banned word that is a term of art is allowed by its
whole phrase in ALLOWED, with the reason.
"""
import glob
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANNED = (r'delv\w*|certainly|utilis\w*|utiliz\w*|leverag\w*|robust|streamlin\w*|harness\w*|foster\w*|underscor\w*|'
          r'enhanc\w*|testament|pivotal|intricat\w*|crucial|transformative|groundbreaking|tapestry|landscape|paradigm|'
          r'synergy|liminal|palpable|showcas\w*|meticulous\w*|notabl[ey]|noteworthy|commendable|versatil\w*|seamless\w*|'
          r'multifaceted|nuanced|holistic|invaluable|unparalleled|garner\w*|bolster\w*|elucidat\w*|interplay|underpin\w*|'
          r'solidif\w*|vibrant|bustling|nestled|breathtaking|stunning|boasts|renowned|indelible|poignant|captivat\w*|'
          r'evocative|embark\w*|unlock\w*|unleash\w*|empower\w*|elevat\w*|amplif\w*|resonat\w*|evok\w*|facilitat\w*|'
          r'spearhead\w*|realm|myriad|plethora|genuine\w*|honestly|truly|arguably|quietly|deeply|fundamentally|navigat\w*')
PATTERNS = [
    ('an em dash', r'—'),
    ('an en dash between words', r'[A-Za-z]\s?–\s?[A-Za-z]'),
    ('"rather than"', r'\brather than\b'),
    ('"not only"', r'\bnot only\b'),
    ('an "X, not Y" turn', r',\s+not (a|an|the)\b'),
    ('a banned word', r'\b(' + BANNED + r')\b'),
    # the owner's rule: a page is about the revision, never about how the site
    # was made, so no reader is told how pages are built or how sources were read
    ('talk about how the site works', r"\b(read twice|opened and read|a second reader|second reading|two readers|one researcher|"
     r"when (?:the|this) page loads|the build|the site is not built|auto-captions|YouTube's (?:English|Hindi) captions)\b"),
]
SEMI = ('a semicolon between words', r'[a-z]; [a-z]')
QUOTED = {'quote', 'quotes', 'title', 'title_en', 'headline', 'url', 'source', 'src', 'outlet', 'evidence', 'law',
          'contact', 'state', 'place', 'places', 'activity', 'para', 'name', 'href', 'issue', 'verbatim', 'text_quote'}
# a banned word used as a term of art, allowed by its whole phrase
ALLOWED = {
    'specially empowered Executive Magistrate': 'the words of BNSS section 163, quoted in a legal point',
}


def page_text(s):
    s = re.sub(r'<(script|style)\b.*?</\1>', ' ', s, flags=re.S)
    s = re.sub(r'<!--.*?-->', ' ', s, flags=re.S)
    return html.unescape(re.sub(r'<[^>]+>', ' ', s))


def js_strings(s):
    for m in re.finditer(r"'((?:[^'\\\n]|\\.)*)'|\"((?:[^\"\\\n]|\\.)*)\"", s):
        t = (m.group(1) if m.group(1) is not None else m.group(2) or '').replace("\\'", "'")
        if len(t.split()) >= 4:
            yield re.sub(r'<[^>]+>', ' ', t)


def walk(o, key=''):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, k)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v, key)
    elif isinstance(o, str) and key not in QUOTED and len(o.split()) >= 4 and not o.startswith('http'):
        yield o


def units():
    for p in sorted(glob.glob(os.path.join(ROOT, 'site', 'pages', '**', 'index.html'), recursive=True)):
        s = open(p, encoding='utf-8').read()
        yield p, page_text(s), True
        for sc in re.findall(r'<script>(.*?)</script>', s, flags=re.S):
            for t in js_strings(sc):
                yield p + ' (script)', t, False
    for p in sorted(glob.glob(os.path.join(ROOT, 'assets', '*.js')) + glob.glob(os.path.join(ROOT, 'assets', 'faq', '*.js'))):
        if os.path.basename(p) in ('i18n.js',):
            continue
        for t in js_strings(open(p, encoding='utf-8').read()):
            yield p, t, False
    for p in sorted(glob.glob(os.path.join(ROOT, 'data', '**', '*.json'), recursive=True)):
        rel = os.path.relpath(p, ROOT)
        if '/raw/' in rel or '/geo/' in rel or rel in ('data/search.json', 'data/downloads.json'):
            continue
        try:
            d = json.load(open(p, encoding='utf-8'))
        except ValueError:
            continue
        for t in walk(d):
            yield p, t, False


def main():
    bad = []
    for p, t, prose in units():
        for phrase in ALLOWED:
            t = t.replace(phrase, '')
        checks = PATTERNS + ([SEMI] if prose else [])
        for what, rx in checks:
            for m in re.finditer(rx, t, flags=re.I if what == 'a banned word' else 0):
                ctx = ' '.join(t[max(0, m.start() - 50):m.end() + 50].split())
                bad.append('%s: %s in "...%s..."' % (os.path.relpath(p.split(' (')[0], ROOT), what, ctx))
    if bad:
        print('\n'.join(bad[:60]))
        sys.exit('FAIL: %d place(s) break the writing rules' % len(bad))
    print('OK: no dash, banned word or "X, not Y" turn in the site\'s own words')


if __name__ == '__main__':
    main()
