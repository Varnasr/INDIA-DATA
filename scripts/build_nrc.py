"""The NRC page's facts, from the research and its independent check.

Reads data/india/raw/nrc_research/nrc.json (each fact with its quote and
document) and verified.json (a second reading of every fact against its
document), keeps only facts the check confirmed or corrected, applies the
corrections, and writes data/india/nrc.json for india/nrc/.

    python3 scripts/build_nrc.py           # write
    python3 scripts/build_nrc.py --check   # fail if the output is stale

Nothing here adds a fact. PLAIN rewords a few claims into the site's
writing rules without changing what they say; FIGURES are read from the
facts named beside them, and the build fails if those facts lose them.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'india', 'raw', 'nrc_research')
OUT = os.path.join(ROOT, 'data', 'india', 'nrc.json')
CHECK = '--check' in sys.argv

SECTIONS = [
    ('legal_basis', 'What the law provides'),
    ('assam', "Assam's NRC"),
    ('npr', 'The National Population Register'),
    ('nationwide', 'A nationwide NRC'),
    ('sir_vs_nrc', 'The SIR and citizenship'),
    ('assam_sr', "Assam's Special Revision of 2025-26"),
]

# claims reworded into plain sentences; the meaning is the checked claim's
PLAIN = {
    'assam-02': "Clause 5.8 of the Assam Accord of 15 August 1985 provides that foreigners who came to Assam on or after 25 March 1971 are to continue to be detected, deleted and expelled in accordance with law.",
    'legal_basis-08': "Rule 3(4) lets the Central Government decide a date for preparing the Population Register of everyone usually resident. Rule 3(5) says the local register of citizens is drawn from it after verification.",
    'legal_basis-10': "Under rule 4(4), people whose citizenship is doubtful are to be marked in the Population Register for further enquiry and told so. Rule 4(5) gives them a hearing before a decision.",
    'legal_basis-14': "In the Section 6A judgment, Chief Justice Chandrachud's opinion summarised the Schedule for Assam. The 1951 NRC and the electoral rolls up to midnight of 24 March 1971 are published, residents apply, and a consolidated list is made of those on those records and their descendants, leaving out anyone declared an illegal migrant or a foreigner.",
    'assam-03': "Section 6A, added in 1985, deems people of Indian origin who came to Assam from the territory now in Bangladesh before 1 January 1966, and have lived there ordinarily since, to be citizens from that date. Those who came between 1 January 1966 and 24 March 1971 and are detected to be foreigners must register, cannot be on an electoral roll for ten years from detection, and are deemed citizens after those ten years.",
    'sir_vs_nrc-06': "The SIR's list of documents for phase II, which it calls indicative and not exhaustive, has 13 items. The National Register of Citizens, 'wherever it exists', is item 9. Eleven items are kinds of document, one is the Aadhaar directions of 9 September 2025, and one is an extract of Bihar's SIR roll.",
    'assam_sr-04': "The Assam order cites the same rule on who may be enrolled as the SIR does, Article 326 with sections 16 and 19 of the Representation of the People Act.",
    'assam_sr-01': "Assam's revision was a Special Revision under section 21 of the Representation of the People Act, with 1 January 2026 as the qualifying date. It was ordered separately from the Special Intensive Revision.",
    'assam_sr-02': "In Assam, booth level officers checked a printed register of the electors already on the roll, house by house. The order names no enumeration form.",
    'sir_vs_nrc-02': "The order made each Electoral Registration Officer responsible for enrolling every eligible person, as Article 326 read with sections 16 and 19 of the Representation of the People Act requires, and for being satisfied of each person's eligibility.",
    'sir_vs_nrc-08': "Before the Court, counsel for the Commission argued that its exercise was an enquiry into eligibility for enrolment and did not determine anyone's citizenship.",
    'nationwide-06': "The Ministry said that rule 6 of the 2003 Rules, under which the national register is initialised, does not contradict rule 4.",
}

# document and place corrected by the check, where the claim was right
CITE = {
    'assam-02': ('In Re: Section 6A, judgment of 17 October 2024, opinion of J.B. Pardiwala J, para 73, the Memorandum of Settlement reproduced', 'PDF pages 311-313, para 73'),
    'sir_vs_nrc-08': ('ADR v ECI, W.P.(C) 640/2025, judgment of 27 May 2026 (2026 INSC 564), submissions for the Election Commission as recorded, para 14(r)', 'judgment pages 32-33, para 14(r)'),
}

# what the research could not settle, written for readers
UNSETTLED = [
    "The number who applied to Assam's NRC. The 3,30,27,661 in the press is the State Coordinator's figure as reported, and equals those found eligible and those left out added together. The Supreme Court's orders give only 3.29 crore.",
    "How many were left out of the complete draft of 30 July 2018. The Supreme Court's order of 31 July 2018 prints 40,70,707, but its own split, 37,59,630 rejected and 2,48,077 on hold, adds to 40,07,707. Only the second agrees with 3.29 crore applicants. This page gives the two parts and no total.",
    "The date of the final list. Every answer of the Ministry gives 31 August 2019. One opinion in the Supreme Court's judgment of 17 October 2024 gives 13 August 2019. This page uses 31 August 2019.",
    "Whether the Registrar General has notified the final NRC for Assam. No document found says it has. In March 2021 the Ministry said the final NRC had not been issued.",
    "Whether rejection orders have gone out since December 2021, when the Ministry said they had not.",
    "Any statement by the Government in Parliament on a nationwide NRC after 21 March 2023, or on updating the NPR after 29 July 2025. The Lok Sabha's answers were searched to October 2026, and the Rajya Sabha's were not searched in full.",
    "An order or press note in which the Election Commission says in its own words how the SIR relates to the NRC. Its position is known from its counsel's submissions as the Supreme Court recorded them.",
    "The Supreme Court's monitoring orders on the NRC of 2013 and 2014, and of 23 July and 13 August 2019, which could not be found.",
]

# figures for the chart, each tied to the fact that carries it
FIGURES = {
    'draft_included': ('assam-08', '2,89,83,677'),
    'draft_rejected': ('assam-09', '37,59,630'),
    'draft_on_hold': ('assam-09', '2,48,077'),
    'final_eligible': ('assam-12', '3,11,21,004'),
    'final_left_out': ('assam-12', '19,06,657'),
}


MONTHS = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')


def main():
    raw = json.load(open(os.path.join(RAW, 'nrc.json'), encoding='utf-8'))
    ver = {x['id']: x for x in json.load(open(os.path.join(RAW, 'verified.json'), encoding='utf-8'))['verified']}
    facts = {}
    for f in raw['facts']:
        v = ver.get(f['id'])
        if not v:
            raise SystemExit('FAIL - %s was not checked' % f['id'])
        if v['status'] not in ('confirmed', 'corrected'):
            continue
        claim = PLAIN.get(f['id']) or v.get('corrected_claim') or f['claim']
        # an ISO date in a claim is written out, as in the rest of the site's prose
        claim = re.sub(r'\b(\d{4})-(\d\d)-(\d\d)\b', lambda m: '%d %s %s' % (int(m.group(3)), MONTHS[int(m.group(2)) - 1], m.group(1)), claim)
        quote = v.get('corrected_quote') or f['quote']
        if re.search(r'\s[—–]\s|—', claim):
            raise SystemExit('FAIL - %s carries a dash' % f['id'])
        facts[f['id']] = {
            'id': f['id'], 'topic': f['topic'], 'claim': claim, 'quote': quote,
            'document': CITE.get(f['id'], (f['document'],))[0], 'issuer': f['issuer'], 'date': f['date'],
            'url': f['url'], 'where': CITE[f['id']][1] if f['id'] in CITE else (f.get('page_or_para') or ''),
        }
    missing = [k for k in PLAIN if k not in facts]
    if missing:
        raise SystemExit('FAIL - reworded facts not in the checked set: %s' % missing)
    figs = {}
    for k, (fid, s) in FIGURES.items():
        if fid not in facts or s not in facts[fid]['claim'] + facts[fid]['quote']:
            raise SystemExit('FAIL - %s no longer carries %s' % (fid, s))
        figs[k] = int(s.replace(',', ''))
    nat = sorted((f for f in facts.values() if f['topic'] == 'nationwide' and 'no decision' in f['claim']), key=lambda f: f['date'])
    out = {
        'sections': [{'id': t, 'title': title, 'facts': sorted((f for f in facts.values() if f['topic'] == t), key=lambda f: f['id'])}
                     for t, title in SECTIONS],
        'figures': figs,
        'nationwide': {'dates': sorted({f['date'] for f in nat}), 'latest': nat[-1]['date'], 'answers': len(nat)},
        'reported': [{'claim': r['claim'], 'outlet': r['outlet'], 'date': r['date'], 'url': r['url']} for r in raw['reported']],
        'unsettled': UNSETTLED,
        'checked': len(facts),
    }
    text = json.dumps(out, ensure_ascii=False, indent=1) + '\n'
    if CHECK:
        if not os.path.exists(OUT) or open(OUT, encoding='utf-8').read() != text:
            raise SystemExit('FAIL - data/india/nrc.json is stale; run scripts/build_nrc.py')
        print('OK: %d checked facts on the NRC page' % len(facts))
        return
    open(OUT, 'w', encoding='utf-8').write(text)
    print('wrote data/india/nrc.json, %d facts' % len(facts))


if __name__ == '__main__':
    main()
