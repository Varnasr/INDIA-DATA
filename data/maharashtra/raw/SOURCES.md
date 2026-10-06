# Maharashtra raw tables: sources

All files written 2026-10-06. Aggregates only: no list of individual electors
was opened, downloaded or stored. `check_raw.py` in this folder asserts every
check listed below (19 checks, all passing; each prints ok or FAIL and the
script exits 1 on any FAIL).

## The source

CEO Maharashtra, "Press Note on Draft Publication of Electoral Roll in SIR –
2026", dated 31 August 2026, 4 pages:
https://ceoelection.maharashtra.gov.in/Downloads/PDF/Notification/Press%20Note%20English_31.08.2026%20Draft%20Roll.pdf
(fetched 2026-10-06, 1,106,900 bytes, sha256 fd9843ccbe0487ce..., PDF producer
iLovePDF, modified 2026-08-31). Pages 1 and 2 are the note's text; page 3 is
Annexure-1, page 4 Annexure-2.

How it was read. The site serves its certificate without the intermediate, so
curl fails verification. The missing intermediate, GlobalSign RSA OV SSL CA
2018, was fetched from the address the certificate itself names
(http://secure.globalsign.com/cacert/gsrsaovsslca2018.crt) and added to the CA
bundle, so the chain was verified in full; verification was never switched off.
The PDF has a clean text layer. Both annexures were extracted from it with
pypdf, then pages 3 and 4 were rendered to images and compared with the
extraction row by row by eye: every row, name and figure agrees. (An earlier
automatic extraction of this note, made elsewhere, had misaligned the rows from
Thane to Pune and from Sindhudurg to Kolhapur. These files do not come from it.)

## What the note does not give

- **No reasons below or at the state.** The note names the five reasons a form
  was not collected, without a single count: absent or not found; shifted;
  dead; enrolled elsewhere or duplicate; other reasons, including refusal to
  fill and submit the form. Any reason counts for Maharashtra elsewhere in the
  repository come from the press, not from this note.
- **No split by sex of the names left off**, at any level. Only the draft is
  given by sex.
- **No roll before the revision by district or by sex.** The note gives the
  roll before as a state total only (9,78,54,049). By district it is derived as
  draft plus uncollectable, which sums exactly to the state total.
- **No AC-level table.** Both annexures are by district.
- **No count of BLOs** and no count of notices issued. The note says notices go
  to electors unmapped with the 2002-2004 rolls and to those with logical
  discrepancies, without numbers.
- The text says the district-wise ASDDO figures are "enclosed as Annexure-1";
  they are in fact Annexure-2. Annexure-1 is the draft by sex.

## district_draft.csv

Electors in the draft roll of 31.08.2026, by district and sex.

- Source: the note's Annexure-1, "Electors in Draft Electoral Roll SIR- 2026
  (as on 31-08-2026)", page 3.
- Columns: sr (the CEO's serial number), district (spelt as in the note), men,
  women, third_gender, total. Rows in the CEO's order, 1 Nandurbar to 36
  Palghar. Names keep the note's spellings: Amaravati, Aurangabad (now
  Chhatrapati Sambhajinagar), Ahmednagar (now Ahilyanagar), Osmanabad (now
  Dharashiv), Beed, Buldhana, Gondia, Raigad, Mumbai City, Mumbai Suburban.
- Checks: 36 districts, each once, serials 1 to 36; men + women + third gender
  = total in every row; the columns sum to the printed Total row and to the
  text of page 1: 3,95,89,905 men, 3,75,72,570 women, 3,087 third gender,
  7,71,65,562 in all.
- Whether the draft counts service electors is not said.

## district_uncollectable.csv

Electors on the roll before the revision whose enumeration form was not
collected, so who are not in the draft, by district. Total only.

- Source: the note's Annexure-2, "Uncollectable EF - The electors not included
  in Draft Eroll of SIR-2026", page 4, column "Total Uncollectable EF count".
- Columns: sr, district, uncollectable. Same 36 districts in the same order
  and spelling as Annexure-1.
- Checks: 36 districts, the same names in the same order as Annexure-1; the
  column sums to the printed total and page 1's 2,06,88,487; draft plus
  uncollectable sums to the roll before, 9,78,54,049, exactly. The roll before
  by district can therefore be taken as draft plus uncollectable.
- For the record (not a check): the share left off runs from 38.4% in Thane,
  37.2% in Mumbai City and 34.0% in Mumbai Suburban down to 8.8% in Hingoli.

## state.csv

State figures and dates, one per row: measure, value, source (page of the
note) and the note's own words in `quote`.

- Counts: roll before 9,78,54,049; draft 7,71,65,562 (78.86%) with 3,95,89,905
  men, 3,75,72,570 women and 3,087 third gender; left off 2,06,88,487 (21.14%);
  288 ACs, 288 EROs, "more than 7,000" AEROs; polling stations 1,00,253 before
  rationalisation, 394 added, 431 deleted, 1,00,216 after, and 1,403 moved to
  new premises.
- Dates: draft published 31.08.2026; claims and objections 31.08.2026 to
  30.09.2026; qualifying date 01.10.2026; notices and disposal 31.08.2026 to
  29.10.2026; final roll due 04.11.2026 (as the note sets it; a later revision
  of the date, if any, is not in this file).
- The five reasons are listed as text, with no values. `blos` is blank because
  the note does not state it.
- Quotes are the note's text with the stray spaces of the PDF text layer
  closed up ("com mencement", "re fusal").
- Checks: the counts as printed; men + women + third gender = draft; draft +
  left off = before; the printed 78.86% and 21.14% follow from the counts;
  1,00,253 + 394 - 431 = 1,00,216.

## ac_district.csv

The district, among today's 36, of each of the 288 assembly constituencies
(2008 delimitation), for dissolving DataMeet's AC map into a district map.

- Source: the Election Commission's voter portal lookup, retrieved 2026-10-06,
  the same service used for Karnataka:
  `https://gateway-voters.eci.gov.in/api/v1/common/districts/S13` lists 36
  districts, and `.../common/acs/<district code>` (S1301 to S1336) each
  district's constituencies. ECI's district names and numbers are identical to
  the press note's, in the same order (ECI's district number is the note's
  serial number), so no name had to be mapped. Across the 36 the lookup returns
  ACs 1 to 288, each once, all active. (The service resets requests without a
  browser's Origin and Referer headers; with them it answers 200.)
- Columns: ac, ac_name (ECI's spelling, with ECI's own typos kept, e.g.
  "Vekramgrth (ST)" for Vikramgad and "Aurangbad (East)"), district (= the
  press note's spelling), district_code (ECI), ac_name_datameet and
  district_datameet (from the DataMeet shapefile `India_AC.shp`, field AC_NAME
  and DIST_NAME, for joining to the map), note.
- Compared with DataMeet's DIST_NAME, the districts agree for 281 ACs apart
  from spelling (AHMADNAGAR, BID, BULDANA, GONDIYA, RAIGARH, MUMBAI for Mumbai
  City, and so on). Seven differ:
  - ACs 128 to 133 (Dahanu, Vikramgad, Palghar, Boisar, Nalasopara, Vasai):
    DataMeet has Thane; ECI has Palghar, the district formed from Thane on
    1 August 2014. Thane keeps 18 ACs.
  - AC 75 Warora: DataMeet has Yavatmal; ECI has Chandrapur. Warora and
    Bhadravati, the tehsils the seat is made of, are in Chandrapur district,
    so DataMeet's field is wrong here. ECI's is used.
- The names of 26 ACs differ in spelling between the two sources (Sindhkheda
  and Sindkheda, Dhaisar and Dahisar, Varsova and Versova, Ahmednagar City and
  Ahmednagar, and so on); the AC number is the key, not the name.
- Note for the map: the shapefile also holds 14 Maharashtra polygons with
  AC_NO 0 and no name (DIST_NAME THANE 4, MUMBAI (SUBURBAN) 6, MUMBAI 1,
  RAIGARH 3), probably creeks and islands. They are in no AC and so not in this
  file; a dissolve by district either drops them or assigns them by
  DIST_NAME, where THANE is ambiguous between Thane and Palghar.
- Checks: ACs 1 to 288 each once; every AC's district is one of the 36 names in
  the note, spelt the same; every district has at least one AC (fewest 3, most
  26, Mumbai Suburban); Palghar has 6 and Thane 18.

## Not done

- The final roll (due 04.11.2026) and any roll during claims and objections
  were not looked for.
- No list of individual electors, and no ASDDO list, was opened.
- Nothing in the repository outside data/maharashtra/raw/ was changed.
