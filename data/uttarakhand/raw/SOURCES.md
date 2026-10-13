# Uttarakhand sources

Both documents are press notes of the Chief Electoral Officer, Uttarakhand,
hosted on the state's S3WaaS site and downloaded with plain HTTPS on
2026-10-06.

- **PN 36/2026, 14 July 2026, the draft roll.**
  https://cdnbbsr.s3waas.gov.in/s3cbf8710b43df3f2c1553e649403426df/uploads/2026/07/20260801442066944.pdf
  Six pages, Hindi and English. Electors on 8 June 2026, 79,60,762; the draft,
  71,33,785 (men 37,23,614, women 34,09,954, third gender 217). The names left
  off under four reasons are read from the chart on page 3: absent or shifted
  6,33,573, deceased 1,24,173, enrolled at more than one place 61,454, other
  7,777, which add to 8,26,977. Nothing below the state.
- **PN 63/2026, 3 October 2026, the final roll.**
  https://cdnbbsr.s3waas.gov.in/s3cbf8710b43df3f2c1553e649403426df/uploads/2026/10/202610031173939115.pdf
  Four pages. Pages 1 and 2 give the final roll, 71,58,949 (men 37,37,701,
  women 34,21,036, third gender 212), 1,29,872 claims and 1,04,708 objections
  admitted, 72,656 electors aged 18 or 19, 1,22,892 aged 80 or more and 12,543
  polling stations. Pages 3 and 4 are a scanned table of all 70 assembly
  constituencies by district: the draft, claims admitted (Form 6, 6A and
  Form 8 transfers), objections admitted (Form 7 and Form 8 transfers) and the
  final roll, each for men, women and third gender.

- **The CEO's table of the draft by constituency, 14 July 2026.** No press-note
  number; linked from the ceo.uk.gov.in home page.
  https://cdnbbsr.s3waas.gov.in/s3cbf8710b43df3f2c1553e649403426df/uploads/2026/07/202607152058741775.pdf
  Two A3 pages (copy in `sources/ceo_ac_draft_asdd_20260714.pdf`). For each of
  the 70 constituencies, with district and state totals: polling stations, the
  draft, electors with anomalies and the nine anomaly categories (each with its
  share), no mapping, "Electors Marked as ASDD during SIR (Deleted)" and service
  electors. Downloaded 2026-10-13.

## Files

- `ac.csv`: the table, one row per constituency, transcribed by hand from the
  scan. `name` is the Election Commission's spelling; `printed_name` records
  the table's own where it differs in more than case. The table prints 35 as
  Haridwar (it is Haridwar Rural) and leaves the SC mark off Bhagwanpur (28),
  Gangolihat (45), Bageshwar (47) and Someshwar (51).
- `district_printed.csv`: the 13 district totals and the state total as the
  table prints them.
- `state.csv`: the state figures from both notes, and the 24,30,608 notices.
- `ac_draft_asdd.csv`: the table of the draft, read from the PDF's text layer by
  `parse_ac_draft_asdd.py` (`python3 parse_ac_draft_asdd.py <pdf> <csv>`, needs
  pdftotext), not typed. Rows for constituencies, districts and the state; the
  district is printed as `U.S.Nagar` there, and constituency names keep the
  table's spelling (the build joins on the number).
- `sources/pn63_table_transcription.txt`: the transcription as first typed,
  kept for the record.

## Checks (`check_raw.py`, run by `check_data.py`)

In every constituency, for men, women and third gender separately, draft plus
claims less objections equals the final roll; claims and objections add to
their printed totals; the constituencies add to the printed district totals,
and the districts to the state total; the state totals equal both press notes;
and the four reasons add to the names left off. A misread digit breaks at
least one, and the transcription passed all of them.

The table of the draft is checked too: the constituencies add to every
printed district total and the districts to the state total in all 14
columns; its draft equals PN 63's draft in all 70 constituencies; its ASDD
total equals PN 36's names left off, so the draft plus the names left off is
the roll of 8 June; and anomalies plus no mapping equal the 24,30,608 notices.
The nine anomaly categories overlap and are never added.

## Not used

The 2024 Lok Sabha roll by assembly segment (`data/india/raw/ls2024_ac_pc.csv`)
adds to 84,31,101, the Election Commission's electorate including service
voters. The SIR rolls are of general electors, and Uttarakhand's service
voters are many and concentrated in the hill seats, so the two are not set
side by side below the state.
