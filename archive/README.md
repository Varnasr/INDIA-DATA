# Archive

Working files from earlier stages of the Bihar analysis, kept for the record.
Nothing on the site reads them and this folder is not served: Netlify answers
404 for `/archive/*` (see `_redirects`) and the GitHub Pages workflow leaves it
out of the artifact it deploys.

- `context-reports-2025/`: Word reports from September 2025. The current
  versions are in `reports/`.
- `working-files-2025/`: intermediate tables from the first extract.
- `data-notes.md`: notes on how those tables were reconciled with the booth
  files.

The published figures are built by `scripts/build_bihar.py` from
`data/bihar/raw/`.
