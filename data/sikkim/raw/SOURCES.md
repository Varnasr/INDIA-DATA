# Sikkim sources

Searched on 2026-10-06: the CEO's SIR page (ceo.sikkim.gov.in/SIRElectoral/SIRElectoralGeneral),
its press releases, its statistical reports list, the Government of Sikkim news
releases, and one web search for district figures. **The CEO has published no
table of the roll, the draft, the names left off or the final roll below the
state.** The only sub-state table is the count of appeals by district. The SIR
page offers polling-station lists of ASDD electors and of deletions (named lists,
not opened, not linked here) and the statutory Form 9/10/11 lists (also named).
The draft-day press note linked from the SIR page
("SIR Press Note 5th July 2026.pdf") answers 404 on the CEO's site.

## Documents

- **CEO Sikkim, press note on the final roll.**
  https://ceo.sikkim.gov.in/UploadedFiles/NewsTender/PRESS%20NOTE.pdf
  Five pages, generated 5 September 2026, for the final roll of 6 September 2026.
  Downloaded with curl on 2026-10-06 and read as PDF text (pymupdf); the appeals
  table on page 4 checked against a rendering of the page. Primary.
  The PDF itself is not kept, because it carries links and QR codes to
  downloadable lists of named electors; `sources/ceo_press_note_final_roll_20260906.txt`
  is its text with those links removed.
- **Government of Sikkim news release, 7 September 2026**, "Final Electoral
  Roll under SIR 2026 Published in Sikkim", reporting the CEO's press briefing.
  https://www.sikkim.gov.in/media/news-announcement/news-info?name=Final+Electoral+Roll+under+SIR+2026+Published+in+Sikkim
  Fetched with curl; text in `sources/sikkim_gov_news_final_roll_20260907.txt`.
  Same figures as the press note. State government, not the CEO.

## Files

- `state.csv`: every state figure in the press note (roll before, reasons,
  draft, mapping, notices, claims and objections, final, polling stations,
  appeals).
- `appeals_deo_district.csv`: appeals at the District Election Officer (first
  appellate authority) as on 6 September 2026, six districts, online and offline.
  The printed Total row is in `state.csv`, not in this file.

## Checks

Passed:
- Roll before by sex: 2,35,572 + 2,35,444 + 2 = 4,71,018.
- Draft by sex: 2,18,507 + 2,14,785 + 2 = 4,33,294.
- Final by sex: 2,12,534 + 2,05,931 + 2 = 4,18,467.
- Reasons: 10,837 + 8,648 + 14,603 + 2,396 + 1,253 = 37,737, the printed total.
- Mapped plus unmapped: 3,61,159 + 72,135 = 4,33,294, the draft.
- Notices: 72,135 + 52,384 = 1,24,519.
- Deleted after the draft: 16,485 + 324 = 16,809.
- Draft + 1,982 added - 16,809 removed = 4,18,467, the final roll; net -14,827.
- 37,724 + 16,485 = 54,209, as printed.
- Polling stations: 572 + 53 = 625.
- Appeals: online columns sum to the printed totals (111, 91, 20); in every
  district row received = responded + pending, online and offline; CEO level
  6 + 36 = 42.

Failed, recorded and not corrected:
- **Roll before less draft is 37,724, not the 37,737 printed as left off.**
  The note itself uses 37,724 on page 2 ("54,209 (37,724 ASDD + 16,485
  ineligible)") and 37,737 on page 1. Both are kept (`left_off`, `left_off_alt`).
- **Forms received (4,33,242) plus forms not received (37,737) = 4,70,979**,
  39 short of the roll before; and forms received is 52 fewer than the draft
  (4,33,294).
- **Offline appeals at DEO level: the district rows add to 297 received, 32
  pending and 265 responded; the printed Total row says 103, 7 and 96.** Each
  row and the Total row are internally consistent (received = pending +
  responded); the rows and the total disagree. Gangtok alone prints 194.
- Form 6 claims received (2,052) and electors added (1,982) are different
  counts; no check implied.
