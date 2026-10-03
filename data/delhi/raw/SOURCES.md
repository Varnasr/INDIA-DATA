# Delhi raw tables: sources

All files fetched 2026-10-03. Aggregates only: no list of individual electors
was opened, downloaded or counted. `check_raw.py` in this folder rebuilds the
four generated CSVs from `sources/` and asserts every check listed below
(36 checks, all passing): `python3 data/delhi/raw/check_raw.py`, or `--write`
to regenerate. It needs `pypdf` to read the two CEO PDFs.

## The CEO's site could not be reached

ceodelhi.gov.in refuses this sandbox: curl through the proxy is reset
(`ws_closed_mid_exchange`), `http://` answers 503, and Firecrawl fails with
`ERR_TUNNEL_CONNECTION_FAILED` on the default and stealth proxies with country
IN. The Wayback Machine holds no capture of `SIR2026.aspx` or of any SIR file
(its CDX index of ceodelhi.gov.in after 2026-08-01 holds only four manual
pages).

What the CEO published, as far as can be told from search results and from
reports that link it:

- `https://ceodelhi.gov.in/SIR2026.aspx`, the SIR page, listing "Distt/AC Wise
  Electors and Uncollectable Enumeration Forms-SIR 2026 Draft Publication".
- That table itself: `https://ceodelhi.gov.in/PDFFolders/2026/Uncollectable_Enumeration_FormsSIR31Aug2026.pdf`
  (linked as the source of both Business Standard charts). **Not read
  directly.** From what is quoted of it, it gives, by district and AC, the
  roll before, the draft and the uncollectable forms. Whether it splits the
  uncollectable forms by reason or by sex is not known.
- A press note of 31.08.2026 with the state figures (quoted in full by
  Business Standard and Hindustan Times; below).
- A daily bulletin of claims and objections (posted as images on the CEO's
  Facebook page, which Firecrawl does not read; figures below are as quoted by
  ANI and india.com).
- Booth-wise lists of absent, shifted, dead and duplicate electors and lists
  of electors issued notices, on the CEO and district sites
  (e.g. dmnewdelhi.delhi.gov.in/sample-page/sir-2026/). **Lists of named
  electors. Not opened.**
- The draft roll by part at voters.eci.gov.in/download-eroll. Named lists. Not
  opened.

## state.csv

The state figures from the CEO's press note of 31.08.2026, quoted in full and
to the elector by Business Standard
(https://www.business-standard.com/india-news/delhi-sir-2026-draft-13-constituencies-see-over-40-electors-left-out-126090100563_1.html,
1 Sept 2026) and Hindustan Times
(https://www.hindustantimes.com/cities/delhi-news/delhi-sir-narrows-gender-gap-as-voter-roll-shrinks-328-101788200888661.html,
1 Sept 2026). The two agree on every figure both give. Read from the articles'
text. The roll before is the roll "as of June 20" (HT); enumeration ran 30
June to 17 August 2026.

These replace the rounded figures in `data/india/raw/states.csv`:
1,45,10,299 before; 97,53,577 draft; 47,56,722 left off, of which
43,32,775 permanently shifted, absent or others, 2,82,412 dead and
1,41,535 enrolled at more than one place.

Checks: before minus draft equals left off exactly; the three reasons sum to
left off exactly; the draft by sex (49,88,993 men, 47,64,137 women, 447 third
gender) sums to the draft exactly. **The roll before by sex (77,11,132 men,
67,98,142 women, 1,024 third gender) sums to 1,45,10,298, one short of
1,45,10,299.** Copied as reported, not corrected. So women left off are
20,34,005 (matching `gender.csv`) and men 27,22,139; these are differences,
marked `derived`.

`notices_issued` (33,12,919) is the Commission's figure as a secondary
compilation quotes it (see below); Alt News gives 33.13 lakh. Marked
`reported`.

## ac.csv

Draft roll and uncollectable forms for all 70 ACs. **The CEO's AC table was
not read directly.** These numbers are the dataset behind Business Standard's
Datawrapper map (chart Gzg9R, "Source: Delhi SIR 2026 draft publication data",
linking the CEO PDF above), fetched as CSV from
https://datawrapper.dwcdn.net/Gzg9R/2/dataset.csv, saved unchanged as
`sources/bs_datawrapper_Gzg9R_ac_draft_uncollectable.csv`. Columns: AC name
as printed, draft, uncollectable, share.

- `roll_before` is draft plus uncollectable, **derived**: the dataset does
  not carry the roll before. The identity is the CEO's own (forms not
  collected are exactly the names left off).
- `ac` and `district_2025` come from matching names to the CEO's roll of
  6.1.2025 (below). Seven names needed a hand match: Nerela, Mangol Puri,
  Seelam Pur, Seemapuri, R.K. Puram, Sultan Pur Majra, Delhi Cantt.
- `district_2025` is the **old 11-district** set of the 2025 roll. Delhi was
  re-districted into 13 districts after that election (a compilation shows
  "Old Delhi", "Central North" and "Outer North"), and the CEO's SIR table is
  probably on the new set. The new AC-to-district map was not found in a
  primary source and is not recorded here.

Checks (all pass): 70 rows, each matched to one AC number; the drafts sum to
97,53,577, the uncollectable forms to 47,56,722 and their sum to 1,45,10,299,
each exactly the state figure; the printed share equals uncollectable over
draft plus uncollectable in every AC to 0.05 point; and ten single-AC figures
quoted elsewhere from the same table agree (HT: Burari 167,885, Okhla
163,829, Badarpur 146,673 and Vikaspuri 146,225 left off, Matiala 333,057 and
Delhi Cantt 41,654 in the draft; BS: Tughlakabad 100,386 and 92,033; Alt News:
Sangam Vihar 114,412 and New Delhi 52,368 in the draft).

**No split by reason or by sex at AC level from a primary source.**

## secondary_reasons_ac.csv (secondary, not primary)

By AC: polling parts, permanently shifted, untraceable or absent, death,
already enrolled elsewhere, their total, and notices issued. From
https://macinsights.in/delhi/sir2026 ("data as of 21 September 2026"), a
consultancy's page that says it **tallied these from the ASDD deleted-list
PDFs and notice PDFs, which are lists of named electors**. The tally is
theirs; this collection did not open or count any list. The table was
transcribed from the rendered page into
`sources/secondary_asdd_reasons_ac_transcribed.txt`; the site's API needs a
token and was not used.

Checks: every row's four reasons sum to its total; the columns sum to the
page's own printed totals (31,59,213; 11,73,547; 2,82,412; 1,41,533;
47,56,705; 33,11,746), so the transcription is exact. Against the CEO: deaths
equal 2,82,412 exactly; shifted plus absent is 15 short of 43,32,775;
duplicates 2 short of 1,41,535; and the AC totals are 17 short of the CEO AC
totals in ac.csv, in 11 ACs (27, 31, 38, 52, 63, 67 by 1; 28, 34, 35, 37 by
2; 57 by 3), never over. It separates "shifted" from "absent", which the CEO's
state figure does not, and it is the only AC-level split by reason found.
**Decide before using it on a page**: it is a third party's count of named
lists. Its page also gives women as 20,33,995 of 47,56,705 deleted (42.76%)
and age bands for the state; these are not recorded here.

## roll_20250106_ac.csv

The final roll of the summary revision 2025 (qualifying date 1.1.2025),
published 6.1.2025: CEO Delhi, "District And Assembly Constituency wise No.
of Electors as on 6.1.2025", by district and AC, men, women, third gender.
Primary URL `https://ceodelhi.gov.in/PDFFolders/District_ACWise%20_Final%20Electors2025.pdf`
(unreachable here). Taken from OpenCity's copy of the CEO PDF
(https://data.opencity.in/dataset/delhi-assembly-elections-2025-voter-rolls),
saved as `sources/ceo_ac_electors_20250106.pdf`, and OpenCity's CSV of it,
`sources/ceo_ac_electors_20250106_opencity.csv`.

Checks: the CSV equals the PDF in all 70 rows (read from the PDF's text
layer); men + women + third gender = total in every AC; ACs sum to each of the
11 printed district totals and to the printed grand total 1,55,24,858.

This is **not** the roll the SIR started from. The SIR started from the roll
of 20 June 2026 (1,45,10,299), about 10 lakh smaller; the roll at the
February 2025 poll was 1,56,14,000. No AC table of the June 2026 roll was
found other than the "before" column implied by ac.csv.

## results_2025.csv

The Delhi assembly election of 5 February 2025, by AC.

- Votes: OpenCity "Delhi Assembly Elections 2025 - Results"
  (https://data.opencity.in/dataset/delhi-assembly-elections-2025-results),
  all 769 candidates and NOTA with EVM, postal and total votes, a copy of the
  ECI results site (results.eci.gov.in/ResultAcGenFeb2025, which now answers
  404). Saved as `sources/results_2025_candidates_opencity.csv`. Winner and
  runner-up are the top two by total votes; margin is their difference.
  Party names shortened for BJP, AAP, INC, JD(U), LJP(RV).
- Electors and polling-station votes: CEO Delhi, "Details of Assembly wise
  votes polled on polling stations during DLAE-2025", by AC and sex, from
  OpenCity (https://data.opencity.in/dataset/delhi-assembly-elections-2025-turnout),
  saved as `sources/ceo_ac_turnout_2025.pdf`, read from its text layer.
  `electors` is the roll at the poll, general electors (service voters are
  not in this table). `votes_polled_ps` excludes postal ballots.
- The ECI statistical reports (https://www.eci.gov.in/statistical-report/ae/2025/10,
  tables 10, 11 and 12) exist but could not be downloaded: the page lists
  them, and the backend API and every guessed file path answer 406 (AppTrana)
  to curl and to Firecrawl, including with a stealth proxy.

Checks: EVM + postal = total for every candidate; all 70 ACs; electors and
votes by sex add up in every AC; electors sum to 1,56,14,000 and polling
station votes to the printed 94,51,997; the printed turnout equals votes over
electors in every AC; every margin positive and no runner-up is NOTA; BJP 48,
AAP 22 as declared. **EVM votes counted equal the CEO's polling-station votes
in 58 ACs; 12 differ** (net 2,322 fewer counted, mostly Vikaspuri -1,514 and
Hari Nagar -787; the rest under 41). Recorded, not reconciled; the usual
reasons are mock-poll votes not cleared and machines not counted.

Margins come from the votes. Two published compilations (Wikipedia and BOOM)
print New Delhi as 4,199 and Patparganj as 28,702; the votes give **4,089**
and **28,072**, which Alt News also uses. Wikipedia also prints Ambedkar
Nagar's runner-up as 46,055; the votes give 42,055 (margin 4,230 either way).

## claims_objections.csv

As reported, not primary: the CEO's daily bulletin as quoted by ANI in the
Economic Times
(https://m.economictimes.com/news/india/delhi-sir-ceo-says-notices-to-electors-do-not-mean-deletion-84263-form-6-applications-received-since-aug-31/articleshow/134369503.cms,
20 Sept 2026), and "official data" quoted by india.com
(https://www.india.com/news/india/delhi-sir-minority-heavy-south-east-district-sees-most-form-7-applications-seeking-deletion-of-names-8531733/,
2 Oct 2026). The india.com district figures are only the five districts it
names for each form, so they do not sum to Delhi and must not be made to.
Its totals include applications filed before the draft (from 30 June). The
two sources agree in shape: 2,12,400 Form 6 to 30 August plus 84,263 to 19
September is 2,96,663; 3,72,729 to 29 September.

No primary count of Form 6, 7 or 8 by AC, of notices by AC, or of hearings or
decisions was found. ECI press note ECI/PN/120/2026 of 26.09.2026
(`sources/eci_pn_120_2026_20260926.pdf`, from
https://www.eci.gov.in/eci/public/api/document?id=17536, curl with browser
headers) extends Delhi's claims and objections to 30 October 2026 and
disposal to 30 November 2026, at the CEO's request; india.com reports the
final roll moved to 4 December 2026.

## Not used

- `sources/bs_datawrapper_fNWAl_district.csv`, Business Standard's district
  chart (https://datawrapper.dwcdn.net/fNWAl/2/dataset.csv). It sets the 2025
  poll roll on the old districts against the SIR draft on a different set:
  only South East matches the ACs (16,54,222 and 8,78,208); the Shahdara row
  is broken (131,461 before, draft blank) and the header is missing. Kept for
  the record only.
- Business Standard's text calls the 2025 roll "156.14 million" and the draft
  "97.54 million"; these are 1.5614 crore and 97.54 lakh.
- The Wire's figure of 7,90,766 removed between January 2025 and June 2026
  and Alt News's 11.16 lakh between the 2025 poll roll and the SIR base: not
  recorded, because they depend on which 2025 roll is taken.

## What is missing

- The CEO's AC/district table itself (only its draft and uncollectable
  columns, through a newspaper's chart data).
- Any primary split of the names left off by reason or by sex below the state.
- The new 13-district map of ACs.
- Claims, objections and notices by AC or district from a primary source.
- The ECI statistical report tables for 2025 (electors including service
  voters, and Form 21 detailed results).
