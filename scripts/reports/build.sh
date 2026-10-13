#!/usr/bin/env bash
# Rebuilds the reports: a PDF in reports/, and a page on the site at
# india/report/, bihar/report/ and hyderabad/report/. The four 2026 state
# reports (Tamil Nadu, Karnataka, West Bengal, Kerala) are PDFs only. Rajasthan,
# Uttar Pradesh, Delhi, Maharashtra, Gujarat, Uttarakhand, Assam and the twenty
# states on the shared page get a PDF and a deck printed from their own pages
# by page_pack.mjs. The
# builders also write a Word file on the way; it is deleted, because the site
# publishes the PDF and the page.
# Run after any change to data/bihar or data/hyderabad. Needs python-docx,
# matplotlib, Pillow, playwright-core with a Chromium (PLAYWRIGHT_CORE,
# CHROME), and pptxgenjs for the two slide decks (set NODE_PATH if it is not
# installed here).
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 scripts/reports/india_report.py reports/sir-india-report.docx india/report
python3 scripts/reports/bihar_report.py reports/bihar-sir-2025-report.docx bihar/report
python3 scripts/reports/hyderabad_report.py reports/hyderabad-old-city-sir-2026-report.docx hyderabad/report
python3 scripts/reports/state_report.py tamilnadu reports/tamil-nadu-sir-2026-report.docx
python3 scripts/reports/state_report.py karnataka reports/karnataka-sir-2026-report.docx
python3 scripts/reports/state_report.py westbengal reports/west-bengal-sir-2026-report.docx
python3 scripts/reports/state_report.py kerala reports/kerala-sir-2026-report.docx
node scripts/reports/pdf.mjs reports/sir-india-report.html reports/bihar-sir-2025-report.html reports/hyderabad-old-city-sir-2026-report.html \
  reports/tamil-nadu-sir-2026-report.html reports/karnataka-sir-2026-report.html reports/west-bengal-sir-2026-report.html reports/kerala-sir-2026-report.html
rm -f reports/*.html reports/*.docx
python3 scripts/reports/web.py india bihar hyderabad
node scripts/reports/decks.js reports
node scripts/reports/state_decks.js reports
# Every other analysis: its PDF and deck are made from its own pages, so the
# site must be served while this runs (python3 -m http.server 8000).
node scripts/reports/page_pack.mjs http://localhost:8000
ls -la reports india/report bihar/report hyderabad/report
