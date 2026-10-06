# Notices to electors kept on the SIR draft roll: sources

Compiled 2026-10-03. Aggregates only. No list of individual electors, names or
EPIC numbers was opened, downloaded or counted. Several CEOs and district
offices publish the lists of persons issued notices (Karnataka, Delhi,
Telangana, West Bengal, and UP districts such as Sitapur, Amroha and
Maharajganj); those lists exist and were not opened.

`notices.csv` has one row per figure: state, phase, date of the figure,
category, count, whether the source gave it rounded (lakh or crore, "about",
"over"), primary or press, the URL that was read, the sentence the figure
comes from, and a note. Categories:

- `discrepancy`: electors flagged for "logical discrepancy" (also called
  "anomaly" or "mapping discrepancy"), that is, linked to the last intensive
  revision roll but with a mismatch the ECINET software flagged.
- `no_mapping`: electors who could not be linked to the last intensive
  revision roll ("unmapped", "no mapping").
- `all_notices`: notices issued or to be issued, both categories together.
- `hearings_held`: hearings or verifications completed.
- `deleted_after_notice`: electors marked ineligible or deleted after the
  notice process.

Several rows are interim figures from states where the notice phase was still
running on 2026-10-03 (all of phase 3 except Arunachal Pradesh, Manipur,
Sikkim, Odisha and Uttarakhand). The date column says when. Where two
sources disagree, both are rows and each note names the other. Do not sum
rows: the same quantity appears more than once.

## Primary sources (18 rows reach a primary document)

- **Goa**: CEO press note of 21/02/2026, https://ceogoa.nic.in/PDF/SIR2026/press-note-Final-publication.pdf.
  Unmapped 1,82,403; logical discrepancies 58,923 in five categories (progeny
  > 6, 3,348; father name mismatch, 41,116; parent age gap < 15, 7,197;
  > 50, 3,830; grandparent gap < 40, 3,432; they sum to 58,923); 35,780 marked
  ineligible after deciding those cases. The note does not give a count of
  notices issued.
- **Arunachal Pradesh**: CEO press note EN/OP/SIR-01/2026 of 22 September 2026,
  https://ceoarunachal.nic.in/componenthelper/getcomponentfile/68 (scanned,
  OCR'd). 85,175 + 1,33,413 = 2,18,588 notices; 28,899 found ineligible.
- **Manipur**: CEO press note of 6 September 2026,
  https://ceomanipur.nic.in/Documents/PressNote/2026-2027/PRESS%20NOTE%20SIR%20FINAL%20EROLL%202026.pdf.
  An image-only PDF; the figures were read off the page image (page 2,
  para 5). 91,178 + 11,30,655 = 12,21,833 notices; 26,362 marked ineligible,
  including those absent or found dead, shifted or repeated at the hearing.
  Logical discrepancy notices went to 58% of the draft roll.
- **Sikkim**: Sikkim government news release of 07-Sep-2026 on the CEO's
  briefing, https://www.sikkim.gov.in/media/news-announcement/news-info?name=Final+Electoral+Roll+under+SIR+2026+Published+in+Sikkim.
  72,135 + 52,384 = 1,24,519 notices; 16,485 found ineligible and deleted.
  Counted as primary because it is the state government's own release.
- **Haryana**: Haryana Public Relations Department release of 5 August 2026,
  https://prms.prharyana.gov.in/press-release/3846. 44,86,035 notices to be
  generated, 42,69,239 prepared. No split by category.
- **West Bengal**: Supreme Court order of 19 January 2026, W.P.(C) 1089/2025,
  https://api.sci.gov.in/supremecourt/2025/64235/64235_2025_1_30_67603_Order_19-Jan-2026.pdf,
  para 2: "approximately 1.40 crore individuals have been issued notices" and
  logical discrepancy "accounting for approximately 1.36 crore voters". The
  Court's words are "It appears that", so this is the Court's reading of the
  record, not a count it made. The CEO's final press note PN-05-2026
  (https://ceowestbengal.wb.gov.in/Downloads/News/Final%20Press%20Note%20CEO-PN-05-2026.pdf)
  was read and carries no notice counts; its 60,06,675 "under adjudication"
  are the notice cases still undecided on 28 February 2026, not a count of
  notices, so they are not a row here (they are in
  `data/westbengal/raw/adjudication_state.csv`).

## Press, by state

Every press row quotes the reporter's sentence. Most attribute the figure to
the CEO or the CEO's office; the note on each row says when they do not.

- **Uttar Pradesh**: The Hindu (PTI), 7 March 2026, CEO Navdeep Rinwa:
  notices 3.26 crore, of which 1.4 crore unmapped and 2.02 crore
  discrepancies. Those two add to 3.42 crore, not 3.26; the article does not
  explain it. The same article says 3.60 crore notices (93.8%) were served,
  which cannot be right against 3.26 crore and is treated as a misprint.
  Hearings around 2.80 crore by 7 March. The Times of India of 19 February
  2026, also reporting the CEO, gives the same 3.26 crore as 1.04 crore for no
  mapping and 2.22 crore for logical discrepancies, which adds up exactly, and
  ThePrint of 10 April 2026 repeats those two figures. The build prefers a
  total whose own report gives lists that add up to it, so the Times of India
  split is the one used. Deleted for not responding to notices:
  3,50,026 (New Indian Express, 11 April 2026).
- **West Bengal**: ECI breakdown of 91.46 lakh logical discrepancy cases and 30
  lakh unmapped (National Herald, 3 January 2026) against the Supreme Court's
  1.36 crore of 19 January; The Reporters' Collective's 1.31 crore initial flag
  and 95 lakh by 2 January (already in `process_research`). Hearings 9.3 lakh by
  14 January (Times of India). After adjudication 27,16,393 of 60,06,675 stood
  deleted (Indian Express, 7 April 2026).
- **Tamil Nadu**: CEO Archana Patnaik at the final roll (New Indian Express, 24
  February 2026): around 13 lakh mapping notices, roughly 1.58 crore logical
  discrepancies, around 2,000 of the mapping cases left out. A DMK application
  to the Supreme Court claimed 1.7 crore logical discrepancy forms (The Hindu,
  28 January 2026); recorded as a party's claim.
- **Kerala**: 36,88,948 notices, all heard (The Hindu, 14 February 2026, CEO
  Rathan U. Kelkar); 19.32 lakh no mapping and 17.56 lakh logical
  discrepancies (Indian Express, 21 February 2026). Ineligible after hearings:
  28,158 by 9 February, "close to 40,000" by 14 February. No final count found.
- **Madhya Pradesh**: 8,46,184 unmapped at the draft (NDTV, 23 December 2025;
  the same article also says "more than 8.35 lakh"); 2.35 crore initial
  logical discrepancy flag from ECI internal records (Reporters' Collective, 4
  February 2026). No count of notices issued was found.
- **Rajasthan**: about 11 lakh unmapped at the draft (New Indian Express and ETV
  Bharat, 16 December 2025) against more than 8.29 lakh in an ECI status report
  of 25 December (Amar Ujala). No logical discrepancy count found.
- **Gujarat**: about 44 lakh notices to be issued (Times of India, 7 January
  2026, an unnamed senior officer in the CEO's office). No split, no outcome.
- **Andaman and Nicobar Islands**: 25,407 unmapped to receive notices (Nicobar
  Times, 23 December 2025).
- **Phase 2 together**: around 5 crore hearing notices (NDTV, 10 April 2026,
  EC sources).
- **Delhi**: 13,79,785 no mapping and 19,33,134 logical discrepancies, 33,12,919
  in all (Hindustan Times, 21 September 2026; the same figures are in the writ
  petition reported by LiveLaw, The Hindu and Business Standard). Conflicts:
  32,27,443 notices "so far" and 13,40,213 not mapped (ETV Bharat, 21 September,
  from an analysis of EC data by Mandate Analytics), and "more than 31 lakh"
  (Newslaundry, 26 September, citing the CEO). Hearings 4,01,670 by 29 September
  (ThePrint/PTI); more than 350 marked ineligible by 27 September (The Hindu).
- **Karnataka**: 20.35 lakh logical discrepancies and 23.45 lakh no mapping,
  43.80 lakh in all (The Hindu, 20 August 2026); 43,81,141 notices generated
  (Hindustan Times, 5 September). HT's own split, 43,81,335 anomaly and
  23,45,500 unmapped, cannot both be right and its first figure is probably the
  total; not used as a split. Hearings 28.81 lakh by 25 September (Deccan
  Herald).
- **Telangana**: 92.88 lakh notices generated, 60.5 lakh logical discrepancies,
  32.3 lakh unmapped, hearings in 61.87 lakh cases, 46.88 lakh found eligible
  (Times of India, 29 September 2026, from the CEO's status). Frontline (26
  September) gives the same 60.5 lakh and "over 32 lakh".
- **Maharashtra**: 1,22,24,007 flagged, 62,48,281 logical discrepancies,
  59,75,726 unmapped (Times of India, 17 September 2026). Indian Express (2
  October) gives the same in lakh.
- **Jharkhand**: 63,24,116 notices: 14,03,205 no mapping, 45,55,227 logical
  discrepancies and 3,65,684 "demographic similar entries", a third category
  seen only here (Times of India, 6 August; ETV Bharat, 7 August 2026).
- **Odisha**: 12,98,779 unmapped + 45,37,613 logical discrepancies = 58,36,392
  notices; 24,070 found ineligible (New Indian Express, 22 September 2026).
- **Andhra Pradesh**: 44,28,444 notices; verification done for 44,00,225; 1,53,600
  declared ineligible by 24 September (ETV Bharat). No split found.
- **Uttarakhand**: 24.30 lakh notices targeted, 20.27 lakh served, 19,04,380
  logical discrepancies (New Indian Express, 6 August 2026); 97,186 marked
  "ineligible for final" at the final roll (Indian Express, 3 October 2026).
  The CEO said the ineligible were all logical discrepancy cases (Hindustan
  Times, 25 September).
- **Punjab**: 22.69 lakh logical discrepancies, 98.77% cleared by 23 September
  (Hindustan Times). No unmapped count found.
- **Chandigarh**: 1,37,814 notices proposed: 69,461 no linkage and 68,353
  logical discrepancies (The Tribune, 28 July 2026, from the district review
  meeting).
- **Meghalaya**: 6,51,735 notices: 2,22,786 no mapping and 4,28,949 mapping
  discrepancies; 6,06,939 completed and 1,194 found ineligible by 1 October
  (Syllad, CEO BDR Tiwari).
- **Nagaland**: "about five lakh" expected (New Indian Express, 21 September
  2026). The Additional CEO gave only shares (9.33% no mapping, 27.31%
  anomalies); against the draft of 11.99 lakh those come to about 4.4 lakh,
  below "about five lakh". Flagged, not resolved; no counts recorded from the
  shares.

## Not found

- **Bihar** (phase 1): no row. The "logical discrepancy" category did not exist
  in the Bihar SIR; Frontline (26 September 2026,
  https://frontline.thehindu.com/the-nation/telangana-special-intensive-revision-voter-deletions-sir/article71498928.ece):
  "The logical discrepancies notice did not exist in the SIR's pilot project in
  Bihar. It was, in fact, instituted by the Election Commission of India (ECI)
  during the SIR's phase II". No comparable state count of notices for Bihar
  was found.
- **Chhattisgarh, Puducherry, Lakshadweep, Mizoram, Dadra and Nagar Haveli and
  Daman and Diu**: no state count of unmapped, discrepancy or notices found.
  Chhattisgarh: only a Raipur district release (dprcg.gov.in, not read) and
  press on district figures. Mizoram: the DIPR release of the CEO's final-roll
  briefing (dipr.mizoram.gov.in) answers 403 to curl and Firecrawl; The Hindu's
  report of it (7 September 2026) gives no notice figures. Puducherry: the
  CEO's final-roll post on X was not readable.
- **Tripura**: the SIR has not reached notices. The schedule starts on 27
  October 2026 with a draft on 12 December 2026 (tripurainfo.com, 2 October).
- **Unreachable primary sites**: ceodelhi.gov.in and ceo.karnataka.gov.in reset
  the connection from this sandbox (curl and Firecrawl), so the Delhi CEO press
  notes and the Karnataka daily notes (latest 2 October 2026,
  https://ceo.karnataka.gov.in/uploads/Press%20Note%20-%2002_1790928798.pdf)
  were not read; ceouttarpradesh.nic.in likewise (see
  `data/uttarpradesh/raw/SOURCES.md`). eci.gov.in was not tried for notice
  counts; no ECI or PIB release with state-wise notice counts was found by
  search. The PIB release of 26 September 2026 (PRID 2315309) concerns
  procedure and gives no counts.
- **Read and not used**: Dainik Bhaskar (Rajasthan, before the draft, 16.46
  lakh "must submit documents", an estimate not a notice count); Naidunia and
  Jagran district figures for Indore and Bhopal; HT's Mumbai district figures;
  a Sikkim Chronicle post (via Instagram) on 92,079 cases heard by 10 August,
  not readable; an Instagram post giving 92 to 93.7 lakh notices for Andhra
  Pradesh, which matches Telangana's figures and appears to be a mix-up; the
  Pioneer e-paper's "68,700" for Chandigarh; a PTI story on Haryana (44.91 lakh
  notices, 4.35 lakh hearings pending, about 1 October 2026) whose text could
  not be read.

## Second pass

Every source URL in `notices.csv` was fetched again on 2026-10-03 (curl into a
fresh folder; Firecrawl with `maxAge: 0` for NDTV, Syllad and Deccan Herald,
which block curl), and each quote's figures and wording were checked against
the page. The Manipur PDF was downloaded again (same MD5) and paragraph 5 was
read off the page image again. All 84 rows were confirmed. One correction came
out of it: the Deccan Herald Karnataka hearings story is dated 25 September
2026 on the page, not the 26th of its metadata.

### Could not confirm

None dropped.
