"""The owner's writing rules, checked over everything a reader sees that the
site wrote itself.

    python3 scripts/check_writing.py

Reads the text of every page source in site/pages (outside scripts and
styles), the strings in every page script and in assets/*.js and
assets/faq/*.js, and the string values of the published JSON under data/
(raw/ folders excluded). Fails on an em dash, an en dash between words,
"rather than", "not only", ", not a/an/the", a semicolon between words in the
pages' own prose, and the owner's banned words.

It also fails on the owner's stock phrases, hedges, vague attributions and
crutch openers, on the site talking about itself outside the pages whose
subject is the site (SELF_EXEMPT), and on a reading-list summary that opens
on a fragment.

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
          r'spearhead\w*|realm|myriad|plethora|genuine\w*|honestly|truly|arguably|quietly|deeply|fundamentally|navigat\w*|'
          r'arena|sphere')
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
    # the owner's rule of 14 October 2026: a name not carried into the draft was
    # left off it, and only an order after the draft deletes one, so the site's
    # own words never call either "removed" or "struck off" (quotations aside)
    ('a word for names that blurs left off and deleted', r'\b(struck off|removals|names? (?:were |was |are |is )?removed|removed (?:from|after) the (?:draft|roll))\b'),
    # the owner's list of stock phrases, hedges and crutches (24 October 2026)
    ('a stock phrase', r"\b(plays? an? (?:key|vital|crucial|central) role|stark reminder|deeply rooted|it'?s important to note|"
     r"it is important to note|when it comes to|in an era of|at the intersection of|sheds? light on|paves? the way|"
     r"navigate the complexities)\b"),
    ('a hedge', r'\b(to some extent|in many ways)\b'),
    ('a vague attribution', r'\b(experts (?:say|said|believe|warn)|studies (?:show|have shown|suggest)|observers (?:note|say|said))\b'),
    ('authority with no one behind it', r'\bha(?:s|ve) been (?:described|called|characterised|characterized|hailed|seen) as\b'),
    ('a sentence opened on a crutch', r'(?:^|[.!?]\s+)(Moreover|Furthermore|Additionally|Importantly|That said|Consequently|'
     r'Ultimately|In essence|In conclusion),? '),
]
# The site never talks about itself: a fact is stated, not what "this site"
# holds, found or could read. Pages whose subject is the site itself (terms and
# privacy, the forms, how to use it, what changed, the method of counting) are
# exempt, and so are quotations.
SELF = ('the site talking about itself', r"\b(this site|this site's|the site's own|the site's figures|reached us|send us|"
        r"we could not|we have not found|that we (?:could )?find|that we found|how sure are we|tells us nothing|on this site)\b")
SELF_EXEMPT = {'site/pages/terms/index.html', 'site/pages/share/index.html', 'site/pages/feedback/index.html',
               'site/pages/support/index.html', 'site/pages/guide/index.html', 'site/pages/about-the-data/index.html',
               'site/pages/corrections/index.html', 'site/pages/downloads/index.html', 'site/pages/updates/index.html',
               'data/updates.json'}
# A reading-list summary opens on a full sentence ("It reports ...", never "Reports ...").
READS_FRAGMENT = re.compile(r'^(Argues|Checks|Compares|Describes|Draws|Examines|Finds|Follows|Gives|Reads|Records|Reports|Runs|'
                            r'Sets|Tabulates|Tallies|Traces|Uses|Walks|Shows|Counts|Explains|Lists|Maps|Documents|Tracks|'
                            r'Analyses|Estimates|Covers|Looks|Reviews|Companion piece)\b')
QUOTES = re.compile(r'"[^"]*"|\u201c[^\u201d]*\u201d|\u2018[^\u2019]*\u2019')
SEMI = ('a semicolon between words', r'[a-z]; [a-z]')
QUOTED = {'quote', 'quotes', 'title', 'title_en', 'headline', 'url', 'source', 'src', 'outlet', 'evidence', 'law',
          'contact', 'state', 'place', 'places', 'activity', 'para', 'name', 'href', 'issue', 'verbatim', 'text_quote', 'translation'}
# a banned word used as a term of art, allowed by its whole phrase
ALLOWED = {
    'specially empowered Executive Magistrate': 'the words of BNSS section 163, quoted in a legal point',
    'How to use this site': 'the name of the guide page, used as the label of a link to it',
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
        rel = os.path.relpath(p.split(' (')[0], ROOT)
        checks = PATTERNS + ([SEMI] if prose else []) + ([] if rel in SELF_EXEMPT else [SELF])
        for what, rx in checks:
            if what.startswith('a word for names') and '/corrections/' in p:
                continue  # the corrections page records what pages used to say
            tt = QUOTES.sub(' ', t) if what.startswith(('a word for names', 'the site talking')) else t
            for m in re.finditer(rx, tt, flags=re.I if what != 'an em dash' else 0):
                ctx = ' '.join(tt[max(0, m.start() - 50):m.end() + 50].split())
                bad.append('%s: %s in "...%s..."' % (os.path.relpath(p.split(' (')[0], ROOT), what, ctx))
    for it in json.load(open(os.path.join(ROOT, 'data', 'india', 'reads.json'), encoding='utf-8'))['items']:
        if READS_FRAGMENT.match(it['shows']):
            bad.append('data/india/reads.json: a summary that opens on a fragment in "%s..."' % it['shows'][:80])
    if bad:
        print('\n'.join(bad[:60]))
        sys.exit('FAIL: %d place(s) break the writing rules' % len(bad))
    print('OK: no dash, banned word or "X, not Y" turn in the site\'s own words')


if __name__ == '__main__':
    main()
