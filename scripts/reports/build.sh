#!/usr/bin/env bash
# Rebuilds the two reports into reports/: Word, then HTML printed to PDF.
# Run after any change to data/bihar or data/hyderabad. Needs python-docx,
# matplotlib, and playwright-core with a Chromium (PLAYWRIGHT_CORE, CHROME).
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 scripts/reports/bihar_report.py reports/bihar-sir-2025-report.docx
python3 scripts/reports/hyderabad_report.py reports/hyderabad-old-city-sir-2026-report.docx
node scripts/reports/pdf.mjs reports/bihar-sir-2025-report.html reports/hyderabad-old-city-sir-2026-report.html
rm reports/*.html
ls -la reports
