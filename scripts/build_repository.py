#!/usr/bin/env python3
"""The downloads page: every table the site publishes, one workbook per place, and a manifest.

    python3 scripts/build_repository.py          # writes downloads/*.xlsx, downloads/all-tables.zip, data/downloads.json
    python3 scripts/build_repository.py --check  # fails if the manifest is stale or a column has no description

Each workbook carries the place's published tables, the Chief Electoral
Officer's own tables the pages are built from, a sheet saying what every
sheet is, and a sheet saying what every column is. Counts only: no table
here carries a name or an EPIC number, and the secondary compilations a
state's SOURCES.md records as unused stay out.

The workbooks and the zip are written with fixed timestamps, but openpyxl's
output is not byte-stable across versions, so --check compares the manifest
(files, sheets, rows, columns and descriptions) and not the binary files.
"""
import csv
import gzip
import io
import json
import os
import sys
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
P = lambda *p: os.path.join(ROOT, *p)
OUT = P('downloads')
FIXED = (2026, 10, 1, 0, 0, 0)

# Every published CSV: what it is and what it cannot show. The place's raw
# tables follow in EXTRA. Wording follows the site's rules.
PUBLISHED = {
    'data/india/states.csv': ('The names left off each state\'s draft roll, with the reasons each Chief Electoral Officer gave', 'state',
                              'Reasons are what the officers wrote down, and nobody checked them. Some states printed their figures in lakh, flagged in the figures column.'),
    'data/india/final_rolls.csv': ('Each final roll set against the draft, with names added and removed after it', 'state',
                                   'Several states gave only the net rise from draft to final. The rise counts new voters too, so it is the most that could have been restored.'),
    'data/india/women_removed.csv': ('Women\'s share of the names left off against their share of the roll', 'state',
                                     'Only states that published a split by sex. Each row carries its quality flag.'),
    'data/india/women.csv': ('Every count by sex the site holds, state and district', 'state and district',
                             'Each state is measured in its own way, named in the measure column. Rows from different measures are not comparable.'),
    'data/india/notices.csv': ('Electors kept on a draft roll but sent a notice, by state', 'state',
                               'Most figures are running counts reported by the press. The two lists overlap, so they can add up to more than the total.'),
    'data/india/process_timeline.csv': ('Every order, letter, court order and judgment that changed how the revision was run', 'event',
                                        'Primary documents only. Press reports are on the process page, apart.'),
    'data/india/process_schedules.csv': ('Each state\'s schedule as set and as moved', 'state and step', ''),
    'data/india/cities.csv': ('Large cities set against their suburbs and the rest of their state', 'city',
                              'A city is a set of districts, drawn differently from city to city. Kolkata and Kochi are measured by the fall in the roll.'),
    'data/india/urban.csv': ('Rural, mixed and urban districts inside each state', 'district (2011)',
                             'Urban shares are from the 2011 census. Each state is measured in its own way.'),
    'data/india/factors.csv': ('District circumstances from NFHS-5 beside the rate, inside each state', 'NFHS-5 district',
                               'Survey figures are for 2019-21, from a published compilation of the district fact sheets. Each state is measured in its own way.'),
    'data/india/reserved.csv': ('Seats reserved for Scheduled Castes and Scheduled Tribes against general seats', 'state and category',
                                'A reserved seat describes a place. It says nothing about the caste of the electors removed.'),
    'data/india/border.csv': ('Districts on the international border against the interior', 'state and part',
                              'The rate says nothing about citizenship.'),
    'data/india/margins_ls2024.csv': ('The names left off each Lok Sabha seat against its 2024 winning margin', 'Lok Sabha seat',
                                      'A count larger than the margin could have decided a seat. It does not show that it did.'),
    'data/india/lok_sabha_electors.csv': ('Electors in every Lok Sabha election since 1984-85, with the population of voting age', 'election',
                                          'The population counts residents who are not citizens.'),
    'data/india/ac_change.csv': ('Every constituency of Tamil Nadu, Kerala, West Bengal and Uttarakhand in one table', 'constituency',
                                 'Each state measures a different thing, named in the state\'s rows. Nothing is added across states. Only Uttarakhand has gross additions and deletions.'),
    'data/india/disputes.csv': ('Every court case, resolution, protest, Form 7 dispute and software change on the disputes page, with its source', 'item',
                                'Press items are what the outlet reported. Allegations are the party\'s. Nothing here says what anyone intended.'),
    'data/india/rti.csv': ('Every application under the Right to Information Act about the revision whose reply was published or reported, with what was asked and what came back', 'application',
                           'A list of the applications that were reported. No authority publishes how many were filed. Each answer is what the outlet reported.'),
    'data/bihar/constituencies.csv': ('Every Bihar constituency, with names removed by phase, reason and sex, and the 2020 to 2025 results', 'constituency',
                                      'Religion is guessed from names and given as a range. Reasons are what the officers wrote down.'),
    'data/bihar/districts.csv': ('Every Bihar district, with names removed by reason, women\'s share and the range for Muslim names', 'district', ''),
    'data/hyderabad/constituencies.csv': ('The five Old City constituencies, with names struck off and summoned to hearings', 'constituency',
                                          'Only these five seats were counted from the lists.'),
    'data/hyderabad/parts.csv': ('Every polling part of the five Old City constituencies', 'polling part',
                                 'Malakpet has no part numbers and is read by polling station.'),
    'data/tamilnadu/constituencies.csv': ('Every Tamil Nadu constituency, with names left off by reason and the 2021 and 2026 results', 'constituency',
                                          'No split by sex or age has been published.'),
    'data/tamilnadu/districts.csv': ('Every Tamil Nadu district', 'district', ''),
    'data/karnataka/districts.csv': ('Every Karnataka election district, with names left off by reason', 'district',
                                     'Published by district only. No split by sex.'),
    'data/westbengal/constituencies.csv': ('Every West Bengal constituency, with the fall in the roll from 2024 by sex', 'constituency',
                                           'The fall in the roll is a different count from the names struck off, which were published for the state only.'),
    'data/westbengal/districts.csv': ('Every West Bengal district', 'district', ''),
    'data/kerala/constituencies.csv': ('Every Kerala constituency, with the fall in the roll from January 2025 by sex', 'constituency',
                                       'No table of the names left off has been published. The rise after the draft counts new voters.'),
    'data/kerala/districts.csv': ('Every Kerala district', 'district', ''),
    'data/rajasthan/constituencies.csv': ('Every Rajasthan constituency, with the change in the roll from 2023', 'constituency',
                                          'The change spans more than two years and is a different count from the names left off.'),
    'data/rajasthan/districts.csv': ('Every Rajasthan district', 'district', ''),
    'data/uttarpradesh/districts.csv': ('Every Uttar Pradesh district, with names left off by reason', 'district',
                                        'The Chief Electoral Officer\'s table as published in the press.'),
    'data/uttarpradesh/seats.csv': ('Every Uttar Pradesh constituency, with its district\'s names left off spread by 2022 electors against the 2022 margin', 'constituency',
                                    'No count by constituency has been published. The spread is an estimate that gives how many seats, never which.'),
    'data/delhi/constituencies.csv': ('Every Delhi constituency, with forms not collected and the 2025 margin', 'constituency',
                                      'Reasons and sex are published for the state only.'),
    'data/delhi/districts.csv': ('Every Delhi district', 'district', ''),
    'data/maharashtra/districts.csv': ('Every Maharashtra district, with forms not collected', 'district',
                                       'No reasons, no split by sex of the names left off. By constituency only the 38 seats the CEO chose to list.'),
    'data/maharashtra/top38.csv': ('The 38 constituencies the CEO listed with a high share of forms not collected', 'constituency',
                                   'A selection the CEO made, which by its own title leaves out the seats a newspaper had called Muslim-heavy. It is 38 of 288 seats and cannot be ranked against the rest.'),
    'data/gujarat/constituencies.csv': ('Every Gujarat constituency, with names left off by reason and the 2022 margin', 'constituency',
                                        'The Chief Electoral Officer\'s tables as published in the press. No split by sex.'),
    'data/gujarat/districts.csv': ('Every Gujarat district, with the final roll', 'district', ''),
    'data/uttarakhand/constituencies.csv': ('Every Uttarakhand constituency, with names added and removed after the draft by sex', 'constituency',
                                            'The names left off the draft are a state total only.'),
    'data/uttarakhand/districts.csv': ('Every Uttarakhand district', 'district', ''),
    'data/assam/assam.csv': ('Assam\'s Special Revision of 2025-26, every figure with its source', 'state',
                             'Names were flagged for deletion. No figure says they were taken off the draft.'),
    'data/assam/constituencies.csv': ('Every Assam constituency, with the rolls of February 2024, the draft and the final roll', 'constituency',
                                      'Each change is net, names added less names removed. The tables do not give the two apart.'),
}

# The Chief Electoral Officer's own tables, as transcribed. Raw files are not
# served on their own; they reach readers only inside a workbook.
EXTRA = {
    'bihar': [('data/bihar/raw/final_roll_format4b.csv', 'Final roll by seat (Format 4B)',
               'The Election Commission\'s Format 4B return for the final roll, seat by seat and by sex, with names added and removed after the draft.'),
              ('data/bihar/raw/reasons_by_ac.csv.gz', 'Reasons by seat, sex, age',
               'Phase 1 names removed, counted by seat, reason, sex and age band. Reasons are what the officers wrote down.')],
    'hyd': [('data/hyderabad/raw/telangana_districts.csv', 'Telangana districts',
             'The draft-roll totals for all 33 districts of Telangana.'),
            ('data/hyderabad/raw/hyderabad_district_acs.csv', 'Hyderabad seats',
             'The draft-roll totals for the 15 seats of Hyderabad district.')],
    'tn': [('data/tamilnadu/raw/asd_ac.csv', 'Names left off by seat (ASD)',
            'The Chief Electoral Officer\'s list of absent, shifted, dead and duplicate electors, counted by constituency.'),
           ('data/tamilnadu/raw/draft_roll_ac.csv', 'Draft roll by seat and sex', 'The draft roll of 19 December 2025.'),
           ('data/tamilnadu/raw/final_roll_ac.csv', 'Final roll by seat and sex', 'The final roll of 23 February 2026.'),
           ('data/tamilnadu/raw/election_roll_20260406_ac.csv', 'Election roll by seat and sex', 'The roll of 6 April 2026, on which the 2026 election was held.'),
           ('data/tamilnadu/raw/roll_20250106_ac.csv', 'January 2025 roll by seat and sex', 'The final roll of 6 January 2025, the last roll before the revision published by sex.')],
    'kl': [('data/kerala/raw/roll_before_ac.csv', 'January 2025 roll by seat and sex', 'The final roll of the summary revision, published 6 January 2025.'),
           ('data/kerala/raw/draft_roll_ac.csv', 'Draft roll by seat and sex', 'The draft roll of 23 December 2025.'),
           ('data/kerala/raw/final_roll_ac.csv', 'Final roll by seat and sex', 'The final roll of 21 February 2026.'),
           ('data/kerala/raw/election_roll_ac.csv', 'Election roll by seat and sex', 'The roll of 23 March 2026.')],
    'wb': [('data/westbengal/raw/roll_2024_ls_ac.csv', '2024 roll by seat and sex', 'Electors at the 2024 Lok Sabha nominations, by assembly segment. About 18 months older than the roll the revision started from.'),
           ('data/westbengal/raw/draft_roll_ac.csv', 'Draft roll by seat and sex', 'The draft roll of 16 December 2025.'),
           ('data/westbengal/raw/electors_nomination_2026_ac.csv', '2026 election roll by seat', 'Electors on the last date of nomination for the 2026 Assembly election, by constituency and sex.'),
           ('data/westbengal/raw/electors_phase1_district.csv', 'Phase 1 electors by district', 'Electors in the districts voting in the first phase.'),
           ('data/westbengal/raw/adjudication_state.csv', 'Adjudication, as reported',
            'The outcomes of adjudication for the state, as the press reported them. Every row is flagged.')],
    'uk': [('data/uttarakhand/raw/ac.csv', 'Claims and objections by seat', 'Pages 3 and 4 of PN 63/2026, transcribed from a scan.'),
           ('data/uttarakhand/raw/district_printed.csv', 'District totals as printed', 'The district totals the note prints.'),
           ('data/uttarakhand/raw/state.csv', 'State figures', 'The state figures of PN 36/2026 and PN 63/2026.'),
           ('data/uttarakhand/raw/ac_draft_asdd.csv', 'Draft, left off, notices by seat', 'The CEO\'s table of the draft of 14.07.2026, read from the PDF\'s text: names marked ASDD and left off, anomalies and no mapping, by seat, district and state.')],
    'dl': [('data/delhi/raw/ac.csv', 'Draft and forms not collected by seat', 'The Chief Electoral Officer\'s table of 31 August 2026.'),
           ('data/delhi/raw/roll_20250106_ac.csv', 'January 2025 roll by seat', 'The roll of 6 January 2025, by constituency and sex.'),
           ('data/delhi/raw/claims_objections.csv', 'Claims and objections', 'Forms received after the draft.'),
           ('data/delhi/raw/state.csv', 'State figures', 'The state figures with their source.')],
    'gj': [('data/gujarat/raw/ac.csv', 'Names left off by seat', 'The draft of 19 December 2025, by constituency and reason.'),
           ('data/gujarat/raw/district.csv', 'Names left off by district', 'The same table by district.'),
           ('data/gujarat/raw/final_district.csv', 'Final roll by district', 'The final roll by district, with additions and deletions as printed.'),
           ('data/gujarat/raw/eci2022_ac.csv', '2022 result by seat', 'The Election Commission\'s statistical report for the 2022 assembly election: winner, runner-up, margin, electors by sex and votes polled.')],
    'rj': [('data/rajasthan/raw/electors_2023_ac.csv', '2023 roll by seat', 'Electors at the 2023 election, from the Election Commission\'s statistical report.'),
           ('data/rajasthan/raw/final_roll_ac.csv', 'Final roll by seat and sex', 'The final roll of 12 March 2026.'),
           ('data/rajasthan/raw/final_roll_district.csv', 'Final roll by district', 'The same roll by district.'),
           ('data/rajasthan/raw/sir_state_summary.csv', 'State figures', 'The state figures of the press note and the fact sheet.')],
    'up': [('data/uttarpradesh/raw/asd_district.csv', 'Names left off by district', 'The district table of 6 January 2026, by reason.'),
           ('data/uttarpradesh/raw/sir_state_summary.csv', 'State figures', 'The state figures with their source.')],
    'mh': [('data/maharashtra/raw/district_draft.csv', 'Draft roll by district and sex', 'Annexure-1 of the press note of 31 August 2026.'),
           ('data/maharashtra/raw/district_uncollectable.csv', 'Forms not collected by district', 'Annexure-2 of the same note.'),
           ('data/maharashtra/raw/state.csv', 'State figures', 'The state figures with their source.')],
    'ka': [('data/karnataka/raw/asd_district.csv', 'Names left off by district', 'The Chief Electoral Officer\'s table by election district and reason.'),
           ('data/karnataka/raw/draft_roll_district.csv', 'Draft roll by district and sex', 'The draft roll of 24 August 2026, general and service electors.'),
           ('data/karnataka/raw/roll_20260925_district.csv', 'Roll of 25 September 2026', 'The roll of 25 September 2026, by district and sex.'),
           ('data/karnataka/raw/roll_20261009_district.csv', 'Roll of 9 October 2026', 'The roll of 9 October 2026, by district and sex.'),
           ('data/karnataka/raw/notices_20261009_district.csv', 'Notices to 9 October 2026', 'Notices generated, delivered and heard by 9 October 2026, by district.'),
           ('data/karnataka/raw/forms_20260616_20261008_district.csv', 'Forms 6, 6A, 7 and 8 to 8 October 2026', 'Forms received from 16 June to 8 October 2026, by district.')],
    'as': [('data/assam/raw/ac_rolls.csv', 'Rolls by seat and sex', 'The Chief Electoral Officer\'s tables of the final roll of 8 February 2024, the draft and the final roll, every constituency by sex.'),
           ('data/assam/raw/state.csv', 'State figures', 'Every roll figure, as quoted by the press.'),
           ('data/assam/raw/rules.csv', 'Rules beside the SIR\'s', 'Each rule of the Special Revision set against the SIR\'s.'),
           ('data/assam/raw/schedule.csv', 'Schedule', 'The order\'s schedule.'),
           ('data/assam/raw/nrc_2019.csv', 'NRC lists of 2019', 'The figures of the lists published on 31 August 2019.'),
           ('data/assam/raw/d_voters.csv', 'D-voters', 'Answers in Parliament on D-voters.'),
           ('data/assam/raw/foreigners_tribunals.csv', 'Foreigners Tribunals', 'Answers in Parliament on the Foreigners Tribunals.'),
           ('data/assam/raw/detention_state.csv', 'Detention, state', 'Answers in Parliament on detention.'),
           ('data/assam/raw/detention_centres.csv', 'Detention centres', 'Capacity and inmates by centre.')],
}

# Columns the raw tables share. A column a sheet carries that is in neither
# this nor columns.json fails --check.
COMMON = {
    'ac': 'Assembly constituency number.', 'ac_number': 'Assembly constituency number.',
    'ac_name': 'Assembly constituency name, as the source spells it.', 'name': 'Name, as the source spells it.',
    'district': 'District.', 'sno': 'Serial number in the source table.', 'sr': 'Serial number in the source table.',
    'men': 'Men on the roll.', 'women': 'Women on the roll.', 'third': 'Third-gender electors on the roll.',
    'third_gender': 'Third-gender electors on the roll.', 'total': 'Total.', 'polling_stations': 'Polling stations.',
    'source': 'The document the figure comes from.', 'source_url': 'Address of the source document.',
    'measure': 'What the row measures.', 'value': 'The figure.', 'item': 'What the row measures.', 'note': 'Note on the row.',
    'date': 'Date of the figure.', 'quote': 'The words of the source.', 'scope': 'What the figure covers.',
    'kind': 'Primary document or press report.', 'source_type': 'Primary document or press report.',
    'figures': 'Exact, or rounded in the source.', 'primary': 'Yes if the source is a primary document.',
    'page_or_para': 'Page or paragraph of the source.', 'as_of': 'Date the figure refers to.', 'phase': 'Polling phase.',
    'reason': 'Reason entered for the removal.', 'sex': 'Sex, F or M (T for third gender).', 'age_band': 'Age band.',
    'count': 'Count.', 'dead': 'Entered as dead.', 'shifted': 'Entered as shifted.', 'absent': 'Entered as absent.',
    'shifted_absent': 'Entered as shifted or absent.', 'multiple': 'Entered as enrolled more than once.',
    'duplicate': 'Entered as enrolled more than once.', 'other': 'Any other reason.', 'others': 'Any other reason.',
    'death': 'Entered as dead.', 'untraceable_absent': 'Entered as untraceable or absent.',
    'already_enrolled': 'Entered as already enrolled elsewhere.', 'before': 'Roll before the revision.',
    'roll_before': 'Roll before the revision.', 'draft': 'Draft roll.', 'final': 'Final roll.',
    'electors_pre': 'Roll before the revision.', 'electors_draft': 'Draft roll.', 'removed': 'Names left off the draft.',
    'electors_before': 'Roll before the revision.', 'uncollectable': 'Enumeration forms not collected, the names left off.',
    'digitised': 'Forms digitised.', 'general': 'General electors.', 'service': 'Service electors.',
    'all_electors': 'General and service electors.', 'general_total': 'General electors.',
    'service_men': 'Service electors, men.', 'service_women': 'Service electors, women.', 'service_total': 'Service electors.',
    'addition': 'Names added after the draft.', 'deletion': 'Names removed after the draft.', 'net': 'Additions less deletions.',
    'pct': 'Per cent change, as printed.', 'left_off': 'Names left off the draft.', 'name_as_published': 'Name as the table prints it.',
    'district_2025': 'District on the 2025 roll.', 'printed_name': 'Name as the table prints it.', 'draft_men': 'Draft roll, men.', 'draft_women': 'Draft roll, women.',
    'draft_tg': 'Draft roll, third gender.', 'period': 'Period of the count.', 'area': 'Area covered.', 'form': 'Form number.',
    'applications': 'Applications received.', 'step': 'Step of the schedule.', 'activity': 'What happens at the step.',
    'from': 'Start date.', 'to': 'End date.', 'para': 'Paragraph of the order.', 'aspect': 'Rule compared.',
    'assam_special_revision': 'The rule in Assam\'s Special Revision.', 'assam_source': 'Document for the Assam rule.',
    'assam_para': 'Paragraph for the Assam rule.', 'assam_quote': 'Words of the Assam order.',
    'sir_phase2': 'The rule in the SIR order of 27 October 2025.', 'sir_source': 'Document for the SIR rule.',
    'd_voters': 'D-voters (doubtful voters).', 'd_voters_women': 'D-voters who are women.', 'centre': 'Detention centre.',
    'capacity_2020': 'Capacity in 2020.', 'inmates_men_20191128': 'Inmates, men, 28 November 2019.',
    'inmates_women_20191128': 'Inmates, women, 28 November 2019.', 'inmates_total_20191128': 'Inmates, 28 November 2019.',
    'added_after_draft': 'Names added after the draft.', 'removed_after_draft': 'Names removed after the draft.',
    'electors_final': 'Final roll.', 'men_final': 'Final roll, men.', 'women_final': 'Final roll, women.',
    'third_gender_final': 'Final roll, third gender.', 'added_men': 'Added after the draft, men.', 'added_women': 'Added after the draft, women.',
    'added_third_gender': 'Added after the draft, third gender.', 'removed_men': 'Removed after the draft, men.',
    'removed_women': 'Removed after the draft, women.', 'removed_third_gender': 'Removed after the draft, third gender.',
    'removed_expired': 'Removed after the draft as dead.', 'removed_shifted': 'Removed after the draft as shifted.',
    'removed_repeated': 'Removed after the draft as enrolled more than once.', 'removed_reason_unstated': 'Removed after the draft, reason not given.',
    'draft_third_gender': 'Draft roll, third gender.',
    'notices_generated': 'Notices generated.', 'notices_delivered': 'Notices delivered.', 'notices_undelivered': 'Notices not delivered.',
    'hearings_held': 'Hearings held.', 'hearings_pending': 'Hearings pending.', 'form6': 'Form 6 received (to add a name).',
    'form6a': 'Form 6A received (overseas electors).', 'form7': 'Form 7 received (objection to a name).',
    'form8': 'Form 8 received (correction or shift).', 'all_forms': 'All four forms received.',
}
for p in ('claims', 'objections'):
    for s, w in (('men', 'men'), ('women', 'women'), ('tg', 'third gender'), ('total', 'all')):
        COMMON['%s_%s' % (p, s)] = '%s admitted after the draft, %s.' % ('Claims' if p == 'claims' else 'Objections', w)
for p, w in (('final', 'Final roll'), ('draft', 'Draft roll')):
    for s, x in (('men', 'men'), ('women', 'women'), ('tg', 'third gender'), ('total', 'all')):
        COMMON.setdefault('%s_%s' % (p, s), '%s, %s.' % (w, x))

GROUPS = [
    ('india', 'All India', 'india-all-states'),
    ('bihar', 'Bihar 2025', 'bihar'),
    ('hyd', 'Telangana 2026 and the Old City of Hyderabad', 'telangana-hyderabad'),
    ('tn', 'Tamil Nadu', 'tamil-nadu'), ('wb', 'West Bengal', 'west-bengal'), ('kl', 'Kerala', 'kerala'),
    ('ka', 'Karnataka', 'karnataka'), ('rj', 'Rajasthan', 'rajasthan'), ('up', 'Uttar Pradesh', 'uttar-pradesh'),
    ('dl', 'Delhi', 'delhi'), ('mh', 'Maharashtra', 'maharashtra'), ('gj', 'Gujarat', 'gujarat'),
    ('uk', 'Uttarakhand', 'uttarakhand'), ('as', 'Assam', 'assam'),
]
SHARED = 'other'


def read(path):
    raw = gzip.open(P(path), 'rt', encoding='utf-8') if path.endswith('.gz') else open(P(path), encoding='utf-8', newline='')
    with raw as f:
        rows = list(csv.reader(f))
    return rows[0], rows[1:]


def num(v):
    if v == '' or v is None:
        return None
    try:
        f = float(v)
    except ValueError:
        return v
    if f != f:
        return v
    return int(f) if f == int(f) and 'e' not in v.lower() and len(v) < 16 else f


def columns_text():
    try:
        return json.load(open(P('data', 'india', 'raw', 'columns.json'), encoding='utf-8'))
    except FileNotFoundError:
        return {}


def describe(path, col, G):
    return (G.get(path) or {}).get(col) or COMMON.get(col)


def places():
    C = json.load(open(P('site', 'places.json'), encoding='utf-8'))
    return {p['id']: p for p in C['places']}


def plan():
    """Every workbook and its sheets, in order."""
    PL = places()
    books = []
    for pid, title, slug in GROUPS:
        sheets = []
        for h, t, _ in PL[pid].get('downloads', []):
            if h.endswith('.csv'):
                what, level, cannot = PUBLISHED[h]
                sheets.append({'path': h, 'sheet': t.replace(', CSV', ''), 'what': what, 'level': level, 'cannot': cannot, 'kind': 'published'})
        for h, t, what in EXTRA.get(pid, []):
            sheets.append({'path': h, 'sheet': t, 'what': what, 'level': '', 'cannot': '', 'kind': 'source'})
        books.append({'id': pid, 'title': title, 'file': 'downloads/%s.xlsx' % slug, 'sheets': sheets})
    shared = [p for p in PL.values() if p.get('group') in ('states', 'uts') and any(d[0].endswith('/tables.csv') for d in p.get('downloads', []))]
    sheets = []
    for p in sorted(shared, key=lambda p: p['label']):
        h = [d[0] for d in p['downloads'] if d[0].endswith('/tables.csv')][0]
        S = json.load(open(P(os.path.dirname(h), 'summary.json'), encoding='utf-8'))
        sheets.append({'path': h, 'sheet': S['state'][:31], 'what': 'Every %s figure with its source.' % S['state'], 'level': 'state and district', 'kind': 'published',
                       'cannot': ' '.join(S.get('cannot_show') or [])})
    books.append({'id': SHARED, 'title': 'Every other state and union territory', 'file': 'downloads/other-states.xlsx', 'sheets': sheets})
    return books


def sheet_name(s, used):
    bad = '[]:*?/\\'
    n = ''.join('-' if c in bad else c for c in s)[:31]
    k, i = n, 2
    while k in used:
        k = (n[:28] + ' %d' % i)
        i += 1
    used.add(k)
    return k


def manifest(books, G):
    missing = []
    for b in books:
        for s in b['sheets']:
            head, rows = read(s['path'])
            s['rows'], s['cols'] = len(rows), len(head)
            if not s['level']:
                s['level'] = 'constituency' if {'ac', 'ac_number'} & set(head) else 'district' if 'district' in head else 'state'
            s['columns'] = []
            for c in head:
                d = describe(s['path'], c, G)
                if not d:
                    missing.append('%s: %s' % (s['path'], c))
                s['columns'].append([c, d or ''])
    return missing


def write_book(b):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment
    from openpyxl.utils import get_column_letter
    import datetime
    wb = Workbook()
    wb.properties.creator = 'Off the Roll'
    wb.properties.created = wb.properties.modified = datetime.datetime(*FIXED)
    about = wb.active
    about.title = 'About'
    bold = Font(bold=True)
    about.append([b['title']])
    about['A1'].font = Font(bold=True, size=14)
    about.append(['Counts only. No table here carries a name or an EPIC number. Published tables are the ones the site draws; source tables are the Chief Electoral Officer\'s own, as transcribed.'])
    about.append(['Analysis CC BY 4.0. Every sheet names its source in its own rows or on the site\'s method page.'])
    about.append([])
    about.append(['Sheet', 'Kind', 'Level', 'Rows', 'What it is', 'What it cannot show', 'File on the site'])
    for c in about[5]:
        c.font = bold
    used = {'About', 'Columns'}
    names = []
    for s in b['sheets']:
        n = sheet_name(s['sheet'], used)
        names.append(n)
        about.append([n, 'Published table' if s['kind'] == 'published' else 'Source table', s['level'], s['rows'], s['what'], s['cannot'],
                      s['path'] if s['kind'] == 'published' else 'in this workbook only'])
    for col, w in zip('ABCDEFG', (34, 16, 18, 8, 70, 70, 40)):
        about.column_dimensions[col].width = w
    for row in about.iter_rows(min_row=6):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical='top')
    for s, n in zip(b['sheets'], names):
        ws = wb.create_sheet(n)
        head, rows = read(s['path'])
        ws.append(head)
        for c in ws[1]:
            c.font = bold
        for r in rows:
            ws.append([num(v) for v in r])
        ws.freeze_panes = 'A2'
        for i, h in enumerate(head, 1):
            longest = max([len(h)] + [len(r[i - 1]) for r in rows[:300] if len(r) >= i])
            ws.column_dimensions[get_column_letter(i)].width = min(48, max(8, longest + 2))
    cw = wb.create_sheet('Columns')
    cw.append(['Sheet', 'Column', 'What it holds'])
    for c in cw[1]:
        c.font = bold
    for s, n in zip(b['sheets'], names):
        for c, d in s['columns']:
            cw.append([n, c, d])
    cw.column_dimensions['A'].width, cw.column_dimensions['B'].width, cw.column_dimensions['C'].width = 30, 32, 90
    os.makedirs(OUT, exist_ok=True)
    wb.save(P(b['file']))


def write_zip(books):
    seen = []
    for b in books:
        for s in b['sheets']:
            if s['kind'] == 'published' and s['path'] not in seen:
                seen.append(s['path'])
    for h in PUBLISHED:
        if h not in seen:
            seen.append(h)
    readme = ['Every table published on the site, as CSV, and the source tables behind them.', '',
              'Counts only. No file carries a name or an EPIC number.',
              'columns.csv says what every column holds. The workbooks on the downloads page carry the same tables, the Chief Electoral Officers\' own tables, and these notes.', '']
    cols = io.StringIO()
    w = csv.writer(cols, lineterminator='\n')
    w.writerow(['file', 'column', 'what_it_holds'])
    G = columns_text()
    with zipfile.ZipFile(P('downloads', 'all-tables.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
        for h in seen:
            info = zipfile.ZipInfo(h[len('data/'):], FIXED)
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, open(P(h), 'rb').read())
            what = PUBLISHED.get(h, (None,))[0] or next(s['what'] for b in books for s in b['sheets'] if s['path'] == h)
            readme.append('%s  %s' % (h[len('data/'):], what))
            for c in read(h)[0]:
                w.writerow([h[len('data/'):], c, describe(h, c, G) or ''])
        readme += ['', 'Source tables, the Chief Electoral Officers\' own, as transcribed and checked:', '']
        for b in books:
            for t in b['sheets']:
                if t['kind'] != 'source':
                    continue
                h = t['path']
                name = 'sources/' + h[len('data/'):].replace('/raw/', '/').replace('.csv.gz', '.csv')
                head, rows = read(h)
                buf = io.StringIO()
                csv.writer(buf, lineterminator='\n').writerows([head] + rows)
                info = zipfile.ZipInfo(name, FIXED)
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, buf.getvalue())
                readme.append('%s  %s' % (name, t['what']))
                for c in head:
                    w.writerow([name, c, describe(h, c, G) or ''])
        for name, body in (('README.txt', '\n'.join(readme) + '\n'), ('columns.csv', cols.getvalue())):
            info = zipfile.ZipInfo(name, FIXED)
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, body)
    return len(seen)


def other_files():
    """Reports and decks, listed with the workbooks on the page."""
    PL = places()
    out = []
    for pid in ['india', 'bihar', 'hyd', 'tn', 'wb', 'kl', 'ka', 'rj', 'up', 'dl', 'mh', 'gj', 'uk', 'as']:
        for h, t, _ in PL[pid].get('downloads', []):
            if h.endswith('.pdf') or h.endswith('.pptx'):
                out.append({'place': PL[pid]['label'], 'book': pid, 'file': h, 'label': t})
    # the twenty states on the shared page share one report and one deck
    for f, t in (('reports/other-states-sir-2026-report.pdf', 'Full report, PDF'), ('reports/other-states-sir-2026-deck.pptx', 'Slides, PowerPoint')):
        out.append({'place': 'Every other state and union territory', 'book': 'other', 'file': f, 'label': t})
    return out


def build(write):
    G = columns_text()
    books = plan()
    missing = manifest(books, G)
    if missing:
        sys.exit('No description for %d columns:\n  ' % len(missing) + '\n  '.join(missing))
    n = 0
    if write:
        for b in books:
            write_book(b)
        n = write_zip(books)
    size = lambda f: os.path.getsize(P(f)) if os.path.exists(P(f)) else None
    files = []
    for b in books:
        files.append({'id': b['id'], 'title': b['title'], 'file': b['file'], 'bytes': size(b['file']),
                      'sheets': [{k: s[k] for k in ('sheet', 'path', 'kind', 'level', 'rows', 'cols', 'what', 'cannot', 'columns')} for s in b['sheets']]})
    docs = other_files()
    for d in docs:
        d['bytes'] = size(d['file'])
    M = {'workbooks': files, 'zip': {'file': 'downloads/all-tables.zip', 'bytes': size('downloads/all-tables.zip')}, 'documents': docs,
         'counts': {'workbooks': len(files), 'tables': sum(len(b['sheets']) for b in files),
                    'published': len({s['path'] for b in files for s in b['sheets'] if s['kind'] == 'published'}),
                    'rows': sum(s['rows'] for b in files for s in b['sheets'])}}
    path = P('data', 'downloads.json')
    if write:
        open(path, 'w', encoding='utf-8').write(json.dumps(M, ensure_ascii=False, separators=(',', ':')) + '\n')
        print('%d workbooks, %d tables, %d rows; zip of %d CSVs' % (len(files), M['counts']['tables'], M['counts']['rows'], n))
        return
    # Sizes move with the zip and openpyxl's output, so they are left out of the comparison.
    def bare(x):
        if isinstance(x, dict):
            return {k: bare(v) for k, v in x.items() if k != 'bytes'}
        return [bare(v) for v in x] if isinstance(x, list) else x
    old = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {}
    if bare(old) != bare(M):
        sys.exit('data/downloads.json is stale: run scripts/build_repository.py')
    gone = [f for f in [b['file'] for b in files] + [M['zip']['file']] + [d['file'] for d in docs] if not os.path.exists(P(f))]
    if gone:
        sys.exit('Missing: ' + ', '.join(gone))
    print('downloads.json current; %d workbooks, %d tables' % (len(files), M['counts']['tables']))

if __name__ == '__main__':
    build('--check' not in sys.argv)
