# NRC explainer sources

Gathered on 2026-10-07 for a page on the National Register of Citizens.
`nrc.json` holds the rows: `facts` (primary documents only, each with a
verbatim quote, page or paragraph, and the local copy), `reported` (press,
attributed, reopened) and `could_not_verify`. Every PDF below is in
`sources/` unless it is already in `data/assam/raw/sources/`. All are
aggregate or legal documents; none carries a list of electors.

## Acts and rules

| file | document | used for |
|---|---|---|
| mizoram_gazette_20040603_citizenship_amendment_act_2003.pdf | Citizenship (Amendment) Act, 2003 (6 of 2004), republished in the Mizoram Gazette Extraordinary No. 178, 3.6.2004. https://mizoramassembly.in/storage/Assembly/Gazette/EO/GZEO33_ISS178.pdf | text of s.14A (scan with OCR noise; quoted words are clear) |
| mha_citizenship_rules_2003.pdf | Citizenship (Registration of Citizens and Issue of National Identity Cards) Rules, 2003, G.S.R. 937(E), 10.12.2003, MHA copy. https://www.mha.gov.in/sites/default/files/2022-09/citizenship_rules2003_0%5B1%5D.pdf | rules 2(k), 2(l), 3, 4, 6. This copy predates rule 4A (2009) |
| orgi_npr_notification_20190731.pdf | S.O. 2753(E), 31.7.2019, Registrar General of Citizen Registration (NPR update with Census 2021 phase 1). https://censusindia.gov.in/nada/index.php/catalog/42544/download/46170/GAZ_NOTIFICATION_04.pdf | NPR 2020 schedule, "except Assam" |

India Code (403 and timeouts) and egazette.gov.in were not reachable.
censusindia.gov.in serves an incomplete certificate chain; it was fetched with
the issuer's own intermediate (emSign SSL CA - G1, from the certificate's AIA
address) added to the CA bundle, verification on.

## Supreme Court

| file | document | used for |
|---|---|---|
| sc_section6a_judgment_20241017.pdf | In Re: Section 6A of the Citizenship Act 1955, W.P.(C) 274/2009, judgment 17.10.2024, 2024 INSC 789 (407 pp.). https://api.sci.gov.in/supremecourt/2009/16113/16113_2009_1_1501_56604_Judgement_17-Oct-2024.pdf | NRC 1951; rule 4A and the Schedule (reproduced); s.6A text; Assam Accord clause 5; history of the NRC monitoring |
| sc_section6a_order_20241017.pdf | Record of proceedings of the same date. https://api.sci.gov.in/supremecourt/2009/16113/16113_2009_1_1501_56604_Order_17-Oct-2024.pdf | majority outcome, para 391 |
| sc_apw_order_02-Jul-2018.pdf, sc_apw_order_31-Jul-2018.pdf | Assam Public Works v Union of India, W.P.(C) 274/2009, orders. https://api.sci.gov.in/supremecourt/2009/16113/16113_2009_Order_<date>.pdf | part draft (31.12.2017), complete draft counts (30.7.2018) |
| sc_apw_order_08-May-2018.pdf, 19-Sep-2018, 01-Nov-2018, 12-Dec-2018, 08-May-2019 | same case, other orders | downloaded and skimmed, not cited |
| sc_adr_order_20250908.pdf | ADR v ECI, W.P.(C) 640/2025, order 8.9.2025. https://api.sci.gov.in/supremecourt/2025/35785/35785_2025_2_26_63969_Order_08-Sep-2025.pdf | Aadhaar as 12th document, not proof of citizenship |
| sc_adr_judgment_20260527.pdf | ADR v ECI, judgment 27.5.2026, 2026 INSC 564. https://api.sci.gov.in/supremecourt/2025/35785/35785_2025_1_1501_71617_Judgement_27-May-2026.pdf | ECI's power and its limits on citizenship (paras 13(r), 171-178, 186) |

The NRC orders of 2013-2014 and of 23 July and 13 August 2019 were not found:
the old-style file names return empty files for those dates.

## Election Commission

| file | document | used for |
|---|---|---|
| eci_sir_orders_ceokerala.pdf | ECI No.23/2025-ERS (Vol.II) of 27.10.2025 (SIR phase II) with Annexure I, the 24.06.2025 letter and Order No. 23/ERS/2025 for Bihar, and Annexures III-IV. Copy hosted by CEO Kerala: https://www.ceo.kerala.gov.in/ceokerala/pdf/SIR/sir-12-states.pdf | legal basis (Art. 324, s.21; Art. 326, ss.16, 19); 2003 roll and presumption of citizenship; no documents at enumeration (phase II); document list incl. "National Register of Citizens (wherever it exists)". The 24.06.2025 pages are scans and were read by eye |
| data/assam/raw/sources/eci_23-2025-ERS_17.11.2025_assam_special_revision.pdf | ECI letter of 17.11.2025 to CEO Assam (Special Revision), from Scribd page images, see data/assam/raw/SOURCES.md | all 18 letter pages read by eye: no mention of the NRC; D-voters para 4(d); Aadhaar voluntary para 10(e) |

## Lok Sabha answers (Lok Sabha digital library, elibrary.sansad.in)

Item pages are https://elibrary.sansad.in/items/<id>. MHA unless stated.

| file | question | id | used for |
|---|---|---|---|
| ls_usq2476_20191203_updation_npr.pdf | USQ 2476, 3.12.2019 | 2e48f16d-e5b8-4b10-bfb9-66f67bbe5dfc | s.14A in force 3.12.2004; NPR 2010, 2015; NPR 2020 plan and cost |
| ls_sq22_20200204_nrc.pdf | SQ 22, 4.2.2020 | 22145c47-7061-4185-a6cf-306c745ad70d | no decision on nationwide NRIC |
| ls_usq376_20200204_preparation_npr.pdf | USQ 376, 4.2.2020 | 5490ea78-6d3b-46d5-8817-96305c08e6d1 | no citizenship verification in NPR; rule 6 |
| ls_usq387_20200204_updation_npr.pdf | USQ 387, 4.2.2020 | 81380cbd-3fdf-4dd6-8ac9-df0931dcb432 | no documents in NPR; Aadhaar voluntary |
| ls_usq425_20200204_npr_hold.pdf | USQ 425, 4.2.2020 | 7dc04ead-0a13-4619-889d-2d20d23acb2c | no decision on nationwide NRIC |
| ls_usq1932_20200303_review_nrc.pdf | USQ 1932, 3.3.2020 | a565c71f-98ea-4474-bb53-9ed5048f8e64 | re-verification prayer declined 23.7.2019 |
| ls_sq14_20210202_nrc.pdf | SQ 14, 2.2.2021 | 2e974ea3-1b15-483b-94c8-8e4aaa74a235 | security regime before lists are shared |
| ls_sq111_20210727_nrc_assam.pdf | SQ 111, 27.7.2021 | 94da780b-002c-4577-adc0-01274b1a0d67 | rejection slips postponed; nine gazette notifications |
| ls_usq3451_20210810_excluded_nrc.pdf | USQ 3451, 10.8.2021 | bfe60a7a-02a9-4eeb-855d-e7979a1ac439 | remedies not exhausted |
| ls_usq3455_20210810_caa_nrc_npr.pdf | USQ 3455, 10.8.2021 | 6f2bdac8-5989-47d0-9453-19d4e0255b6b | no decision on nationwide NRIC |
| ls_usq1016_20220208_npr.pdf | USQ 1016, 8.2.2022 | 30945b08-fd9c-490c-abb2-91021addb5e4 | NPR and census postponed |
| ls_usq350_20220719_nrc.pdf | USQ 350, 19.7.2022 | a5616391-33fc-4c4a-b6f5-926fa09756df | read; repeats security regime and appeal rule |
| ls_usq2072_20230314_updation_nrc.pdf | USQ 2072, 14.3.2023 | 513c7031-8a5c-493a-957f-124a99b9bda9 | update under rule 4A(4) Schedule; cost |
| ls_usq3389_20230321_nrc_caa_npr.pdf | USQ 3389, 21.3.2023 | 3fdecccc-3859-4aee-9280-ff48ea25e44a | latest "no decision" on nationwide NRIC found |
| ls_usq441_20250722_census2027.pdf | USQ 441, 22.7.2025 | d101f446-c34f-4863-821d-3050e1304425 | read; census preparations |
| ls_usq1382_20250729_census2027.pdf | USQ 1382, 29.7.2025 | 47e9623a-6706-40ff-8b0a-05e3d6522bf6 | census intent 16.6.2025; "No decision has been taken to update the National Population Register." |
| ls_usq258_20251202_census_resumption.pdf | USQ 258, 2.12.2025 | b4a9f6e6-d9d1-4832-b7d0-e425f7801fa3 | census 2027 phases |
| ls_usq262_20251202_census_proforma.pdf, ls_usq420_20251202_census_timeline.pdf | USQ 262 and 420, 2.12.2025 | a5631f4e-..., c93f8e52-... | read; no NPR mention |
| ls_usq5278_20260324_census2027_safeguards.pdf | USQ 5278, 24.3.2026 | 3d6a7b68-b268-40c5-8f64-dff2cc4eac1b | census data confidential |
| ls_usq990_20260724_sir.pdf | USQ 990, 24.7.2026, Ministry of Law and Justice | ae284c05-04a6-4e9b-af83-a9ecf7a9209a | SIR phases; Court's holding |
| ls_usq2274_20161129_nrc_assam.pdf, ls_usq1267_20181218_nrc_assam.pdf | USQ 2274 (2016), 1267 (2018) | 0cae374e-..., fbacb61b-... | read; background |

Reused from `data/assam/raw/sources/`: ls_20210209_nrc_assam.pdf (USQ 1264,
item 5a55334c-29c7-4094-a608-411dc9ab70c7), ls_20210316_nrc_assam.pdf (USQ
3448, 05a2e507-9d89-4cdd-9d83-d1d4ff8e750f), ls_20210323_ft_appeals.pdf (USQ
4425, f496396c-5bfa-44e3-85ba-078fdbacf02f), ls_20211214_nrc_list.pdf (USQ
2624, d43fb455-804d-4402-ba7d-832000a74487), ls_20211214_ft_appeal.pdf (USQ
2627, 61ad252f-ec8b-4988-b506-e36de9c2453f).

The library was searched by title (NRC, NPR, National Register, National
Population Register, Census, Citizens) to October 2026. No answer on a
nationwide NRC after 21.3.2023, on rejection orders after 14.12.2021, or on
the NPR after 29.7.2025 was found. Rajya Sabha was not searched
systematically.

## Press (reported list only)

- The Tribune (PTI), 31.8.2019, https://www.tribuneindia.com/news/archive/nation/final-national-register-of-citizens-released-in-assam-825782
  : the State Coordinator's statement with 3,30,27,661 applicants. Reopened
  2026-10-07.

## Not reachable

nrcassam.nic.in (reset; Firecrawl failed), indiacode.nic.in (403/timeout),
egazette.gov.in, eci.gov.in downloads (406, per earlier work).
