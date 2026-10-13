#!/usr/bin/env python3
"""Merge printed pages into one PDF with a title (page_pack.mjs calls this).

    python3 scripts/reports/merge_pdf.py OUT.pdf "Title" part1.pdf part2.pdf ...
"""
import sys

from pypdf import PdfWriter

out, title, parts = sys.argv[1], sys.argv[2], sys.argv[3:]
w = PdfWriter()
for p in parts:
    w.append(p)
w.add_metadata({'/Title': title, '/Author': 'ImpactMojo'})
with open(out, 'wb') as fh:
    w.write(fh)
