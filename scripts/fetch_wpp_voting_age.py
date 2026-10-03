"""India's population of voting age in each Lok Sabha election year, from the
UN World Population Prospects 2024 (medium variant, single-year ages, 1 July).

Run by hand; it downloads about 130 MB and is not part of CI. Writes
data/india/raw/wpp2024_voting_age.csv, which scripts/build_electors.py reads.
The voting age was 21 until the 61st Amendment came into force in 1989, so
the eligible population is 21 and over for 1984-85 and 18 and over after.
"""
import csv, gzip, io, os, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'india', 'raw', 'wpp2024_voting_age.csv')
BASE = 'https://population.un.org/wpp/assets/Excel%20Files/1_Indicator%20(Standard)/CSV_FILES/'
FILES = ['WPP2024_PopulationBySingleAgeSex_Medium_1950-2023.csv.gz', 'WPP2024_PopulationBySingleAgeSex_Medium_2024-2100.csv.gz']
# the WPP year read for each election: the calendar year it was held in
YEARS = {'1984-85': 1984, '1989': 1989, '1991-92': 1991, '1996': 1996, '1998': 1998, '1999': 1999,
         '2004': 2004, '2009': 2009, '2014': 2014, '2019': 2019, '2024': 2024}


def main():
    want = set(YEARS.values()); res = {}
    for f in FILES:
        raw = urllib.request.urlopen(BASE + f).read()
        with gzip.open(io.BytesIO(raw), 'rt', encoding='utf-8-sig') as fh:
            for r in csv.DictReader(fh):
                if r['LocID'] != '356' or r['Variant'] != 'Medium' or int(r['Time']) not in want:
                    continue
                t, a, p = int(r['Time']), int(r['AgeGrpStart']), float(r['PopTotal']) * 1000
                d = res.setdefault(t, {'18': 0.0, '21': 0.0})
                if a >= 18: d['18'] += p
                if a >= 21: d['21'] += p
    with open(OUT, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh, lineterminator='\n')
        w.writerow(['election', 'wpp_year', 'pop_18plus', 'pop_21plus', 'voting_age'])
        for e, t in YEARS.items():
            w.writerow([e, t, round(res[t]['18']), round(res[t]['21']), 21 if t < 1989 else 18])
    print('wrote', os.path.relpath(OUT, ROOT))


if __name__ == '__main__':
    main()
