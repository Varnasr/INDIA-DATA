"""The 2024 Lok Sabha results by constituency and the assembly segments of
each constituency, for the comparison of removals with winning margins.

Run by hand; not part of CI. Reads a published compilation of the Election
Commission's 2024 results (results.eci.gov.in) and of its statistical report
34, "Details of Assembly Segment of PC", and writes
  data/india/raw/ls2024_pc_results.csv  one row per constituency
  data/india/raw/ls2024_ac_pc.csv       one row per assembly segment
The margin is the winner's votes less the runner-up candidate's. NOTA is not a
candidate: in Indore it came second, and the runner-up is the candidate behind
it. Surat was won unopposed and has no margin.
"""
import csv, io, os, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'india', 'raw')
BASE = 'https://data.opencity.in/dataset/85a345c6-78c0-4f57-adfc-236c726c5456/resource/'
RESULTS = BASE + 'd164b73a-b855-4b68-be0c-0f3450e7ab9f/download/1b837c18-4f7a-4acb-aad0-918c51186a54.csv'
WINNERS = BASE + '3e96ed32-9b97-4c5b-9201-7807d90b20e5/download/2a4e0925-0903-4857-902b-9a57cfb78094.csv'
SEGMENTS = BASE + '881d1489-a8fc-46b1-b00d-d4824e08e797/download/142dc4e5-49e3-4412-a751-d712970b0dd5.csv'
# the state names the rest of the site uses
NAMES = {'NCT OF Delhi': 'Delhi', 'Andaman & Nicobar Islands': 'Andaman and Nicobar Islands',
         'Dadra & Nagar Haveli and Daman & Diu': 'Dadra and Nagar Haveli and Daman and Diu'}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8-sig')


def num(x):
    try:
        return int(x)
    except ValueError:
        return None


def main():
    cands = {}
    for r in csv.DictReader(io.StringIO(get(RESULTS))):
        t = num(r['Total Votes'])
        if t is None or r['Party'].strip().upper() == 'NONE OF THE ABOVE' or r['Candidate'].strip().upper() == 'NOTA':
            continue
        cands.setdefault((r['State'].strip(), int(r['PC No'])), []).append((t, r['Candidate'].strip(), r['Party'].strip(), r['PC Name'].strip()))
    pub = {(r['State'].strip(), int(r['PC No'])): num(r['Margin Votes']) for r in csv.DictReader(io.StringIO(get(WINNERS)))}
    seg, pce, pcname = [], {}, {}
    for r in csv.reader(io.StringIO(get(SEGMENTS))):
        if len(r) < 7 or not r[4].strip().isdigit():
            continue
        key = (r[0].strip(), int(r[1]), int(r[4]))
        pce[(r[0].strip(), int(r[1]))] = int(r[3])
        pcname[(r[0].strip(), int(r[1]))] = r[2].strip()
        seg.append(key + (r[5].strip(), r[2].strip(), int(r[6])))
    seen = set()
    with open(os.path.join(RAW, 'ls2024_ac_pc.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh, lineterminator='\n')
        w.writerow(['state', 'ac', 'ac_name', 'pc', 'pc_name', 'electors_ac'])
        for st, pc, ac, acn, pcn, el in sorted(set(seg)):
            if (st, ac) in seen:
                continue
            seen.add((st, ac))
            w.writerow([NAMES.get(st, st), ac, acn, pc, pcn, el])
    with open(os.path.join(RAW, 'ls2024_pc_results.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh, lineterminator='\n')
        w.writerow(['state', 'pc', 'pc_name', 'electors', 'winner', 'winner_party', 'winner_votes', 'runner_up', 'runner_up_party', 'runner_up_votes', 'margin', 'margin_published', 'note'])
        for k in sorted(pub):
            v = sorted(cands.get(k, []), reverse=True)
            note = ''
            if len(v) < 2:
                note = 'won unopposed'
                row = [k[1], pcname.get(k, 'Surat' if k == ('Gujarat', 24) else ''), pce.get(k, ''), v[0][1] if v else '', v[0][2] if v else '', v[0][0] if v else '', '', '', '', '', pub[k]]
            else:
                m = v[0][0] - v[1][0]
                if pub[k] != m:
                    note = 'published margin is against NOTA' if pub[k] and pub[k] > m else 'published margin differs'
                row = [k[1], v[0][3], pce.get(k, ''), v[0][1], v[0][2], v[0][0], v[1][1], v[1][2], v[1][0], m, pub[k]]
            w.writerow([NAMES.get(k[0], k[0])] + row + [note])
    print('wrote ls2024_pc_results.csv and ls2024_ac_pc.csv')


if __name__ == '__main__':
    main()
