"""Further reading and viewing (india/reading/): the research list, read twice.

Reads data/india/raw/reads_research/reads.json (each item opened by the
first researcher) and verified.json (a second, independent reading of every
item). Only items the second reading confirmed or corrected are kept, its
corrections are applied, and PLAIN rewords a summary into the site's writing
rules without changing what it says. EXTRA adds the items the second reading
checked that are not in the first list. Writes data/india/reads.json.

    python3 scripts/build_reads.py [--check]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / 'data' / 'india' / 'raw' / 'reads_research'
OUT = ROOT / 'data' / 'india' / 'reads.json'

# the groups the page shows, in order, and which group each item goes in
GROUPS = ['Investigations', "The Commission's account", 'Data and analysis', 'Research', 'Law and the courts', 'Videos']
TYPE = {
    'article (investigation)': 'Investigations',
    'report (official press note)': "The Commission's account",
    'analysis (data)': 'Data and analysis', 'article (data)': 'Data and analysis', 'report (analysis)': 'Data and analysis',
    'article (survey report)': 'Data and analysis',
    'academic (analysis)': 'Research', 'academic (working note)': 'Research',
    'legal': 'Law and the courts', 'video': 'Videos',
}
# an item whose type does not say where it belongs, by address
BY_URL = {
    'https://www.deccanherald.com/opinion/sir-redraws-bengals-margins-of-power-3995060': 'Data and analysis',
    'https://sabarinstitute.org/research-and-publications/citizens-handbook-for-filing-sir-voter-deletion-appeals': 'Law and the courts',
    'https://indianexpress.com/article/india/decisions-unanimous-election-commission-response-sir-vote-express-investigation-gyanesh-kumar-10890491/': "The Commission's account",
}
# the Hyderabad lists' compiler is never named or pointed to (CLAUDE.md), so
# a report on Hyderabad that names its co-author stays off the page
EXCLUDE = {'https://sabarinstitute.org/research-and-publications/hyderabad-sir-'}
OUTLET = {
    'Personal research note (debrajray.com)': 'Debraj Ray, research note',
    'Election Commission of India (copy hosted by the Government of Meghalaya)': 'Election Commission of India',
    "The Reporters' Collective (YouTube)": "The Reporters' Collective",
}
# summaries reworded into the site's rules (no colon hinges, no "X, not Y")
PLAIN = {
    2: "Reports the Election Commission's first response to the investigation. The Commission calls the 14 notes suggestions and says every decision was unanimous, and the paper sets out what the response does not address.",
    9: 'Checks booth-level results in high-deletion villages, the 28 close contests and late additions to the roll, and finds no anomaly that stands out. The NDA won exactly half the close contests.',
    11: "Runs four tests of West Bengal's deletions against the 2026 margins and swings. Net deletions exceeded the BJP's margin in 82 seats but exceeded the swing in margin in only 12 flipped seats, and the deletions under adjudication passed the two tests in 49 and 14 seats.",
    20: 'Uses official records and interviews with election officials to argue that the West Bengal notices were produced in bulk by central software, and that registration officers did not review them one by one as the Commission told the Court.',
    25: "Draws on official deletion figures and an RTI reply on West Bengal appeals. Delhi's draft excluded 32.78% of electors, 91.13% of the decided West Bengal appeals restored the elector, and the public still cannot check the rolls.",
}
EXTRA = [{
    'title': 'More SIR Deletions, Bigger BJP Swing? Prannoy Roy DeKodes the Data | DeKoder',
    'outlet': 'DeKoder', 'authors': 'Prannoy Roy', 'date': '2026-10-08',
    'url': 'https://www.youtube.com/watch?v=K5qUfsPBSvQ', 'type': 'video', 'duration': '7:37',
    'shows': ("Prannoy Roy sets West Bengal's deletions beside the 2026 swing against the TMC and argues that the deletions "
              "enlarged it. The episode shows no allowance for other differences between seats, and the other analyses of "
              "the same question listed here reach different answers."),
}]


def build():
    items = json.loads((RAW / 'reads.json').read_text(encoding='utf-8'))
    ver = {v['url']: v for v in json.loads((RAW / 'verified.json').read_text(encoding='utf-8'))}
    # the Sabar Institute's pieces, found and read twice in a second round
    sabar = [x for x in json.loads((RAW / 'sabar.json').read_text(encoding='utf-8')) if x['url'] not in EXCLUDE]
    ver.update({v['url']: v for v in json.loads((RAW / 'sabar_verified.json').read_text(encoding='utf-8'))})
    out, dropped = [], []
    for i, it in enumerate(items + EXTRA + sabar):
        v = ver.get(it['url'])
        if not v or v['status'] not in ('confirmed', 'corrected'):
            dropped.append({'title': it['title'], 'outlet': it['outlet'], 'why': (v or {}).get('note', 'not read a second time')})
            continue
        it = dict(it, **(v.get('fix') or {}))
        if isinstance(it.get('authors'), list):
            it['authors'] = ', '.join(it['authors'])
        if i in PLAIN:
            it['shows'] = PLAIN[i]
        g = BY_URL.get(it['url']) or TYPE.get(it['type'])
        if g not in GROUPS:
            sys.exit('FAIL - no group for %r (%s)' % (it['title'], it['type']))
        if '—' in it['shows']:
            sys.exit('FAIL - em dash in the summary of %r' % it['title'])
        out.append({'group': g, 'title': it['title'], 'outlet': OUTLET.get(it['outlet'], it['outlet']), 'authors': it.get('authors') or '',
                    'date': it['date'], 'url': it['url'], 'video': it['type'] == 'video', 'duration': it.get('duration') or '',
                    'shows': it['shows']})
    out.sort(key=lambda x: (GROUPS.index(x['group']), x['date']), reverse=False)
    return {'groups': GROUPS, 'items': out, 'dropped': dropped,
            'counts': {'items': len(out), 'outlets': len({x['outlet'] for x in out}), 'videos': sum(x['video'] for x in out)}}


def main():
    D = build()
    text = json.dumps(D, indent=1, ensure_ascii=False) + '\n'
    if '--check' in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding='utf-8') != text:
            sys.exit('FAIL - data/india/reads.json is stale: run scripts/build_reads.py')
        print('OK: %d reads current' % D['counts']['items'])
        return
    OUT.write_text(text, encoding='utf-8')
    print('wrote %d items, dropped %d' % (D['counts']['items'], len(D['dropped'])))


if __name__ == '__main__':
    main()
