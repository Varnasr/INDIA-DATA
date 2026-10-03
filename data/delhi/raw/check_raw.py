#!/usr/bin/env python3
"""Delhi raw tables: build them from sources/ and assert every check in SOURCES.md.

    python3 data/delhi/raw/check_raw.py           # check the CSVs against sources/
    python3 data/delhi/raw/check_raw.py --write   # rewrite the CSVs, then check

Aggregates only. Nothing here reads a list of individual electors.
"""
import csv, collections, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'sources')
fails = []


def check(cond, msg):
    print(('ok    ' if cond else 'FAIL  ') + msg)
    if not cond:
        fails.append(msg)


def num(s):
    s = (s or '').replace(',', '').strip()
    return int(s) if s else None


def norm(s):
    s = re.sub(r'\(SC\)', '', s, flags=re.I)
    return re.sub(r'[^a-z]', '', s.lower())


# ---------------------------------------------------------------- state figures
# CEO Delhi press note of 31.08.2026, as quoted in full by Business Standard and
# Hindustan Times (see SOURCES.md). The press note itself could not be fetched.
STATE = dict(roll_before=14510299, draft=9753577, left_off=4756722,
             shifted_absent_other=4332775, dead=282412, duplicate=141535,
             before_men=7711132, before_women=6798142, before_tg=1024,
             draft_men=4988993, draft_women=4764137, draft_tg=447)

# ---------------------------------------------------------------- roll of 6.1.2025
jan = []
dist = None
dist_tot = {}
for r in csv.reader(open(os.path.join(SRC, 'ceo_ac_electors_20250106_opencity.csv'), encoding='utf-8-sig')):
    if r[0] == 'District No.':
        continue
    if r[1]:
        dist = r[1]
    if r[2]:
        jan.append(dict(ac=int(r[2]), ac_name=r[3], district_2025=dist, men=int(r[4]),
                        women=int(r[5]), third_gender=int(r[6]), total=int(r[7])))
    else:
        dist_tot[r[3]] = [int(x) for x in r[4:8]]
jan.sort(key=lambda x: x['ac'])
check(len(jan) == 70 and [x['ac'] for x in jan] == list(range(1, 71)), 'roll 6.1.2025: 70 ACs, numbered 1 to 70')
check(all(x['men'] + x['women'] + x['third_gender'] == x['total'] for x in jan), 'roll 6.1.2025: men + women + third gender = total in every AC')
by_d = collections.defaultdict(lambda: [0, 0, 0, 0])
for x in jan:
    for i, k in enumerate(['men', 'women', 'third_gender', 'total']):
        by_d[x['district_2025']][i] += x[k]
gt = dist_tot.pop('Grand Total')
check(len(dist_tot) == 11, 'roll 6.1.2025: 11 district total rows')
printed = {norm(k.replace(' Total', '')): v for k, v in dist_tot.items()}
check(sorted(printed) == sorted(norm(d) for d in by_d) and all(by_d[d] == printed[norm(d)] for d in by_d),
      'roll 6.1.2025: ACs sum to each printed district total')
check([sum(x[k] for x in jan) for k in ['men', 'women', 'third_gender', 'total']] == gt == [8349645, 7173952, 1261, 15524858],
      'roll 6.1.2025: ACs sum to printed grand total 1,55,24,858')
# The CSV is OpenCity's transcription of the CEO PDF kept beside it; compare every row with the PDF text.
try:
    txt = subprocess.run(['python3', '-c', "import pypdf,sys;r=pypdf.PdfReader(sys.argv[1]);print('\\n'.join(p.extract_text() for p in r.pages))",
                          os.path.join(SRC, 'ceo_ac_electors_20250106.pdf')], capture_output=True, text=True).stdout
    pdf = {int(m[0]): [int(v) for v in m[2:]] for m in re.findall(r'^(\d+) ([A-Z .]+?) (\d+) (\d+) (\d+) (\d+)$', txt, re.M)}
    check(len(pdf) == 70 and all(pdf[x['ac']] == [x['men'], x['women'], x['third_gender'], x['total']] for x in jan),
          'roll 6.1.2025: OpenCity CSV equals the CEO PDF in all 70 rows')
except Exception as e:  # pypdf missing
    check(False, 'roll 6.1.2025: could not read the CEO PDF (%s)' % e)
JAN = {x['ac']: x for x in jan}
NAME2AC = {norm(x['ac_name']): x['ac'] for x in jan}
NAME2AC.update({'nerela': 1, 'mangolpuri': 12, 'seelampur': 65, 'seemapuri': 63, 'rkpuram': 44,
                'sultanpurmajra': 10, 'delhicantt': 38})

# ---------------------------------------------------------------- draft by AC
dw = list(csv.reader(open(os.path.join(SRC, 'bs_datawrapper_Gzg9R_ac_draft_uncollectable.csv'), encoding='utf-8-sig')))[1:]
ac = []
for name, draft, unc, share in dw:
    a = NAME2AC.get(norm(name))
    ac.append(dict(ac=a, ac_name=JAN[a]['ac_name'] if a else name, name_as_published=name,
                   district_2025=JAN[a]['district_2025'] if a else '', draft=num(draft),
                   left_off=num(unc), share_printed=share))
check(all(x['ac'] for x in ac) and len({x['ac'] for x in ac}) == 70, 'draft by AC: 70 rows, each matched to one AC number')
for x in ac:
    x['roll_before'] = x['draft'] + x['left_off']
check(sum(x['draft'] for x in ac) == STATE['draft'], 'draft by AC: sums to the state draft 97,53,577')
check(sum(x['left_off'] for x in ac) == STATE['left_off'], 'draft by AC: uncollectable forms sum to the state 47,56,722')
check(sum(x['roll_before'] for x in ac) == STATE['roll_before'], 'draft by AC: draft + uncollectable sums to the state roll before 1,45,10,299')
off = [x['name_as_published'] for x in ac
       if abs(100 * x['left_off'] / x['roll_before'] - float(x['share_printed'].rstrip('%'))) >= 0.06]
check(off == [], 'draft by AC: printed share = uncollectable / (draft + uncollectable) in every AC (to 0.05 point)')
A = {x['ac']: x for x in ac}
# figures for single ACs quoted in other reports of the same table
quoted = [(2, 'left_off', 167885, 'HT'), (54, 'left_off', 163829, 'HT'), (53, 'left_off', 146673, 'HT'),
          (31, 'left_off', 146225, 'HT'), (34, 'draft', 333057, 'HT'), (38, 'draft', 41654, 'HT'),
          (52, 'draft', 100386, 'BS'), (52, 'left_off', 92033, 'BS'), (49, 'draft', 114412, 'Alt News'),
          (40, 'draft', 52368, 'Alt News')]
check(all(A[a][k] == v for a, k, v, _ in quoted), 'draft by AC: agrees with the 10 AC figures quoted by HT, BS and Alt News')

# ---------------------------------------------------------------- state figures by sex and reason
check(STATE['roll_before'] - STATE['draft'] == STATE['left_off'], 'state: roll before - draft = left off (exact)')
check(STATE['shifted_absent_other'] + STATE['dead'] + STATE['duplicate'] == STATE['left_off'], 'state: three reasons sum to left off (exact)')
check(STATE['draft_men'] + STATE['draft_women'] + STATE['draft_tg'] == STATE['draft'], 'state: draft by sex sums to the draft (exact)')
check(STATE['before_men'] + STATE['before_women'] + STATE['before_tg'] == STATE['roll_before'] - 1,
      'state: roll before by sex sums to 1,45,10,298, ONE SHORT of 1,45,10,299 (as reported; not corrected)')

# ---------------------------------------------------------------- 2025 results and electors at the poll
cand = list(csv.DictReader(open(os.path.join(SRC, 'results_2025_candidates_opencity.csv'), encoding='utf-8-sig')))
check(all(int(c['EVM Votes']) + int(c['Postal Votes']) == int(c['Total Votes']) for c in cand), 'results 2025: EVM + postal = total for every candidate')
ABBR = {'Bharatiya Janata Party': 'BJP', 'Aam Aadmi Party': 'AAP', 'Indian National Congress': 'INC',
        'Janata Dal  (United)': 'JD(U)', 'Lok Janshakti Party(Ram Vilas)': 'LJP(RV)', 'None of the Above': 'NOTA'}
byac = collections.defaultdict(list)
for c in cand:
    byac[int(c['AC No'])].append(c)
check(sorted(byac) == list(range(1, 71)), 'results 2025: all 70 ACs present')
txt = subprocess.run(['python3', '-c', "import pypdf,sys;r=pypdf.PdfReader(sys.argv[1]);print('\\n'.join(p.extract_text() for p in r.pages))",
                      os.path.join(SRC, 'ceo_ac_turnout_2025.pdf')], capture_output=True, text=True).stdout
turn = {}
for m in re.findall(r'^(\d+) ([A-Z .]+?) ' + r' '.join([r'(\d+)'] * 8) + r' ([\d.]+)$', txt, re.M):
    turn[int(m[0])] = [int(v) for v in m[2:10]] + [float(m[10])]
check(sorted(turn) == list(range(1, 71)), 'turnout 2025 (CEO PDF): 70 ACs read')
check(all(t[0] + t[1] + t[2] == t[3] and t[4] + t[5] + t[6] == t[7] for t in turn.values()), 'turnout 2025: electors and votes by sex add up in every AC')
check(sum(t[3] for t in turn.values()) == 15614000 and sum(t[7] for t in turn.values()) == 9451997,
      'turnout 2025: electors sum to 1,56,14,000 and polling-station votes to the printed 94,51,997')
check(all(abs(100 * t[7] / t[3] - t[8]) < 0.01 for t in turn.values()), 'turnout 2025: printed percentage = votes / electors in every AC')
res = []
for a in range(1, 71):
    cs = sorted(byac[a], key=lambda c: -int(c['Total Votes']))
    w, r = cs[0], cs[1]
    check(r['Party'] != 'None of the Above', 'results 2025: runner-up in AC %d is a candidate, not NOTA' % a) if r['Party'] == 'None of the Above' else None
    t = turn[a]
    res.append(dict(ac=a, ac_name=JAN[a]['ac_name'], district_2025=JAN[a]['district_2025'],
                    winner=w['Candidate'].strip(), winner_party=ABBR.get(w['Party'], w['Party']),
                    winner_votes=int(w['Total Votes']), runner_up=r['Candidate'].strip(),
                    runner_up_party=ABBR.get(r['Party'], r['Party']), runner_up_votes=int(r['Total Votes']),
                    margin=int(w['Total Votes']) - int(r['Total Votes']),
                    votes_total=sum(int(c['Total Votes']) for c in cs), postal_total=sum(int(c['Postal Votes']) for c in cs),
                    electors=t[3], electors_men=t[0], electors_women=t[1], electors_tg=t[2],
                    votes_polled_ps=t[7]))
check(all(int(cs['Total Votes']) >= 0 for cs in cand) and all(x['margin'] > 0 for x in res), 'results 2025: no ties; every margin positive')
check(collections.Counter(x['winner_party'] for x in res) == {'BJP': 48, 'AAP': 22}, 'results 2025: BJP 48, AAP 22, as declared')
evm_gap = {x['ac']: sum(int(c['EVM Votes']) for c in byac[x['ac']]) - x['votes_polled_ps'] for x in res}
evm_gap = {k: v for k, v in evm_gap.items() if v}
check(evm_gap == {1: -40, 7: -2, 11: 1, 28: -787, 31: -1514, 32: -1, 37: -2, 47: -1, 53: 3, 57: -1, 60: 24, 68: -2},
      'results 2025: EVM votes counted equal CEO polling-station votes in 58 ACs; the 12 known differences net -2,322 (Hari Nagar -787, Vikaspuri -1,514)')
# margins as published by a results compilation (BOOM), for the record: two differ from the CSV's own vote counts
BOOM = {40: 4199, 57: 28702}
check(all(next(x for x in res if x['ac'] == a)['margin'] != v for a, v in BOOM.items()),
      'results 2025: New Delhi 4,089 and Patparganj 28,072 from the votes (compilations print 4,199 and 28,702)')

# ---------------------------------------------------------------- secondary reasons by AC
sec = []
for l in open(os.path.join(SRC, 'secondary_asdd_reasons_ac_transcribed.txt')).read().split('\n'):
    if l.strip():
        f = l.split('|')
        sec.append(dict(ac=int(f[0]), ac_name=JAN[int(f[0])]['ac_name'], parts=num(f[2]), shifted=num(f[3]), absent=num(f[4]),
                        dead=num(f[5]), duplicate=num(f[6]), total=num(f[7]), notices=num(f[8])))
sec.sort(key=lambda x: x['ac'])
check(len(sec) == 70 and [x['ac'] for x in sec] == list(range(1, 71)), 'secondary reasons: 70 ACs')
check(all(x['shifted'] + x['absent'] + x['dead'] + x['duplicate'] == x['total'] for x in sec), 'secondary reasons: four reasons sum to the row total in every AC')
check([sum(x[k] for x in sec) for k in ['shifted', 'absent', 'dead', 'duplicate', 'total', 'notices']] ==
      [3159213, 1173547, 282412, 141533, 4756705, 3311746], 'secondary reasons: columns sum to the compiler\'s own printed totals (transcription check)')
check(sum(x['dead'] for x in sec) == STATE['dead'], 'secondary reasons: dead equals the CEO state figure 2,82,412 exactly')
check(STATE['shifted_absent_other'] - sum(x['shifted'] + x['absent'] for x in sec) == 15 and
      STATE['duplicate'] - sum(x['duplicate'] for x in sec) == 2, 'secondary reasons: shifted+absent 15 short and duplicate 2 short of the CEO state figures')
diff = {x['ac']: A[x['ac']]['left_off'] - x['total'] for x in sec if A[x['ac']]['left_off'] != x['total']}
check(sum(diff.values()) == 17 and all(v > 0 for v in diff.values()),
      'secondary reasons: 17 short of the CEO AC totals, in %d ACs (%s)' % (len(diff), ', '.join('%d:%d' % kv for kv in sorted(diff.items()))))

# ---------------------------------------------------------------- write / compare
OUT = {
    'ac.csv': (['ac', 'ac_name', 'name_as_published', 'district_2025', 'roll_before', 'draft', 'left_off'], ac),
    'roll_20250106_ac.csv': (['ac', 'ac_name', 'district_2025', 'men', 'women', 'third_gender', 'total'], jan),
    'results_2025.csv': (['ac', 'ac_name', 'district_2025', 'winner', 'winner_party', 'winner_votes', 'runner_up',
                          'runner_up_party', 'runner_up_votes', 'margin', 'votes_total', 'postal_total', 'electors',
                          'electors_men', 'electors_women', 'electors_tg', 'votes_polled_ps'], res),
    'secondary_reasons_ac.csv': (['ac', 'ac_name', 'parts', 'shifted', 'absent', 'dead', 'duplicate', 'total', 'notices'], sec),
}
for fn, (cols, rows) in OUT.items():
    rows = sorted(rows, key=lambda x: x['ac'])
    path = os.path.join(HERE, fn)
    if '--write' in sys.argv:
        with open(path, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(cols)
            for x in rows:
                w.writerow([x[c] for c in cols])
    have = list(csv.reader(open(path))) if os.path.exists(path) else []
    check(have == [cols] + [[str(x[c]) for c in cols] for x in rows], '%s matches what sources/ produce' % fn)

print('\n%d failed' % len(fails) if fails else '\nall checks pass')
sys.exit(1 if fails else 0)
