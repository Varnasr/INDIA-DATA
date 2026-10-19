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
    'https://thewire.in/business/the-link-between-tcs-sirs-digital-stack-and-the-noel-tata-n-chandrasekaran-tussle': 'Data and analysis',
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
    5: "Using the list of about 65 lakh Bihar electors left off the draft, which the Supreme Court made the Commission publish, shows women far outnumbered men among those marked 'permanently shifted', most of all below age 40.",
    6: "The Hindu's data team sets the gender gap among the names left off Bihar's draft against census migration records and the ages of those left off.",
    8: "Compares Bihar's January 2025 roll with the final SIR roll and finds women were close to 59% of the fall in the roll and the gender ratio of the roll fell in 230 of 243 seats.",
    9: 'Checks booth-level results in villages where many names were left off or deleted, the 28 close contests and late additions to the roll, and finds no anomaly that stands out. The NDA won exactly half the close contests.',
    10: "Sets the Commission's counts of names left off by reason and sex against state death records and finds about 7.6 lakh more women than men left off, including more women entered as dead, although more men die.",
    11: "Runs four tests of the names West Bengal left off or deleted against the 2026 margins and swings. The net count exceeded the BJP's margin in 82 seats but exceeded the swing in margin in only 12 flipped seats, and the names held for adjudication passed the two tests in 49 and 14 seats.",
    12: "From the Commission's lists, finds roughly three in five electors left off, deleted or held under adjudication on West Bengal's roll were women, most heavily in Muslim-majority, Scheduled Tribe and Matua seats.",
    13: "Using the Sabar Institute's data on names left off or deleted, reports that those names exceeded the margin in 102 of the BJP's 207 seats and, by its own summary, a regression in which they rose with how hard a seat was for the BJP to win.",
    14: "An economist's counterfactual. Even if every elector deleted after adjudication had voted for the runner-up, the BJP keeps a majority, and only under assumptions the data do not support do the wider counts of names left off or deleted overturn it.",
    15: 'An arithmetic test of sensitivity. The gross count of names left off or deleted exceeded the winning margin in 160 seats, and of two no-SIR scenarios one returns the TMC and the other leaves the BJP with a smaller majority. It does not model voter preference.',
    17: 'Finds 11 Bihar seats where the names left off or deleted exceeded the winning margin, separates the 47 lakh net fall from the 3.66 lakh deleted after the draft, and says the landslide made the numbers moot statewide.',
    18: 'Reports a Lokniti-CSDS survey across Delhi and five states. 52% of respondents had no birth certificate and 41% no domicile certificate, with sharp gaps between states.',
    20: 'Uses official records and interviews with election officials to argue that the West Bengal notices were produced in bulk by central software, and that registration officers did not review them one by one as the Commission told the Court.',
    21: "From booth-wise lists of names left off and ground reporting, finds 79.2 lakh of Delhi's 1.45 crore electors were left off the draft or sent a notice, with the heaviest losses among the poorest, including residents of demolished settlements.",
    25: "Draws on official figures for names left off and an RTI reply on West Bengal appeals. Delhi's draft excluded 32.78% of electors, 91.13% of the decided West Bengal appeals restored the elector, and the public still cannot check the rolls.",
    28: "Reading 91 lakh elector records, it finds women were 53.6% of the 58 lakh names left off the draft in December 2025 and that in Nandigram, where Muslims are about a quarter of the population, they were 95% of the names deleted from the supplementary lists.",
    29: "It finds the names left off or deleted in West Bengal's revision outnumbered the winning margin in 161 of 293 Assembly seats, and still did so in 124 seats once deaths are left out.",
    32: 'Of the 1,58,677 names left off the draft in Manipur, the 20 hill seats account for 66.4% and women for 55.96%, and women are the majority of those left off in all 60 seats.',
    39: "Finds that the 17 phase 3 states and territories with draft rolls left off 6.15 crore names, 17.1%, against 12.3% in the first two phases, with a larger share marked shifted or absent. It also finds that the full lists of names left off for Delhi, Maharashtra, Karnataka and Telangana mark no one as 'Others', though the Chief Electoral Officers' press notes put 9.73 lakh names left off in phase 3 under that reason.",
    40: "Finds that shifted or absent made up 75% to 96.5% of the names left off in 85 Maharashtra constituencies, and that neighbouring seats in Pune used the two reasons very differently. It estimates that the draft roll falls about 1.92 crore short of the projected adult population.",
    53: 'Sets Odisha\'s net fall of 17.67 lakh (about 5.3 per cent) from the pre-SIR roll to the final roll of 21 September against other states. It gives a 94 per cent return of enumeration forms, few duplicates and mostly seasonal migration as the reasons, and explains how an elector left off or deleted can appeal or reapply.',
}
# round 7 (15 October 2026), keyed by the URL
PLAIN_URL = {
    'https://www.youtube.com/shorts/YIUQjAucz1U': (
        "A BJP short on the 13 crore names left off the drafts. Its description splits them, citing the Commission's figures, into "
        "absent, shifted or other (9.5 crore, 71%), dead (2.7 crore, 20%) and duplicate (1 crore, 7.6%), argues that, given that split, "
        "the 13 crore cannot all be read as eligible voters deleted, and points to the Commission's drive to enrol eligible voters "
        "who were left out."),
}
EXTRA = [{
    'title': 'More SIR Deletions, Bigger BJP Swing? Prannoy Roy DeKodes the Data | DeKoder',
    'outlet': 'DeKoder', 'authors': 'Prannoy Roy', 'date': '2026-10-08',
    'url': 'https://www.youtube.com/watch?v=K5qUfsPBSvQ', 'type': 'video', 'duration': '7:37',
    'shows': ("Prannoy Roy sets the names West Bengal left off or deleted beside the 2026 swing against the TMC and argues "
              "that they enlarged it. The episode shows no allowance for other differences between seats, and the other analyses of "
              "the same question listed here reach different answers."),
}]


def build():
    items = json.loads((RAW / 'reads.json').read_text(encoding='utf-8'))
    ver = {v['url']: v for v in json.loads((RAW / 'verified.json').read_text(encoding='utf-8'))}
    # the Sabar Institute's pieces, found and read twice in a second round
    sabar = [x for x in json.loads((RAW / 'sabar.json').read_text(encoding='utf-8')) if x['url'] not in EXCLUDE]
    ver.update({v['url']: v for v in json.loads((RAW / 'sabar_verified.json').read_text(encoding='utf-8'))})
    # a third round, 15 September to 10 October 2026, found and read twice
    third = json.loads((RAW / 'round3.json').read_text(encoding='utf-8'))
    ver.update({v['url']: v for v in json.loads((RAW / 'round3_verified.json').read_text(encoding='utf-8'))})
    # later rounds (fourth to 14 October 2026, fifth The Wire's RTI piece, eighth to 19 October), each found and read twice
    fourth = []
    for n in (4, 5, 6, 7, 8):
        if (RAW / ('round%d.json' % n)).exists():
            fourth += json.loads((RAW / ('round%d.json' % n)).read_text(encoding='utf-8'))
            ver.update({v['url']: v for v in json.loads((RAW / ('round%d_verified.json' % n)).read_text(encoding='utf-8'))})
    out, dropped = [], []
    for i, it in enumerate(items + EXTRA + sabar + third + fourth):
        v = ver.get(it['url'])
        if not v or v['status'] not in ('confirmed', 'corrected'):
            dropped.append({'title': it['title'], 'outlet': it['outlet'], 'why': (v or {}).get('note', 'not read a second time')})
            continue
        it = dict(it, **(v.get('fix') or {}))
        if isinstance(it.get('authors'), list):
            it['authors'] = ', '.join(it['authors'])
        if i in PLAIN:
            it['shows'] = PLAIN[i]
        if it['url'] in PLAIN_URL:
            it['shows'] = PLAIN_URL[it['url']]
        g = BY_URL.get(it['url']) or it.get('group') or TYPE.get(it['type'])
        if g not in GROUPS:
            sys.exit('FAIL - no group for %r (%s)' % (it['title'], it['type']))
        if '—' in it['shows']:
            sys.exit('FAIL - em dash in the summary of %r' % it['title'])
        out.append({'group': g, 'title': it['title'], 'outlet': OUTLET.get(it['outlet'], it['outlet']), 'authors': it.get('authors') or '',
                    'date': it['date'], 'url': it['url'], 'video': it['type'].startswith('video'), 'duration': it.get('duration') or '', 'subscription': bool(it.get('subscription')),
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
