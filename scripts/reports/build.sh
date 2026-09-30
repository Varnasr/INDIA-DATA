#!/usr/bin/env bash
# Rebuilds the two reports: a PDF in reports/, and a page on the site at
# bihar/report/ and hyderabad/report/. The builders also write a Word file on
# the way; it is deleted, because the site publishes the PDF and the page.
# Run after any change to data/bihar or data/hyderabad. Needs python-docx,
# matplotlib, Pillow, playwright-core with a Chromium (PLAYWRIGHT_CORE,
# CHROME), and pptxgenjs for the two slide decks (set NODE_PATH if it is not
# installed here).
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 scripts/reports/bihar_report.py reports/bihar-sir-2025-report.docx bihar/report
python3 scripts/reports/hyderabad_report.py reports/hyderabad-old-city-sir-2026-report.docx hyderabad/report
node scripts/reports/pdf.mjs reports/bihar-sir-2025-report.html reports/hyderabad-old-city-sir-2026-report.html
rm -f reports/*.html reports/*.docx
python3 scripts/reports/web.py bihar hyderabad
node scripts/reports/decks.js reports
ls -la reports bihar/report hyderabad/report
