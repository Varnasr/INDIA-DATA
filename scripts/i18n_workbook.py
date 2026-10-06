#!/usr/bin/env python3
"""Writes the review workbook: every string on the site with its Hindi, Urdu,
Telugu, Tamil and Bengali translations side by side, for a native reader to check.

    python3 scripts/i18n_workbook.py out.xlsx

One sheet per language plus a combined sheet. Each row carries the pages the
string appears on and an empty column for the reviewer's correction, so the
corrections can be read back into assets/i18n/<lang>.js key by key. Needs
openpyxl.
"""
import json
import re
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

ROOT = Path(__file__).resolve().parent.parent
NAMES = {'hi': 'Hindi', 'ur': 'Urdu', 'te': 'Telugu', 'ta': 'Tamil', 'bn': 'Bengali'}


def load(lang):
    body = (ROOT / 'assets' / 'i18n' / (lang + '.js')).read_text(encoding='utf-8')
    return json.loads(re.search(r'window\.SIR_DICT\s*=\s*(\{.*\})\s*;\s*$', body, re.S).group(1))


def main(out):
    cat = json.loads((ROOT / 'i18n' / 'catalogue.json').read_text(encoding='utf-8'))
    dicts = {k: load(k) for k in NAMES}
    keys = sorted(cat, key=lambda k: (min(cat[k]['pages']), k.lower()))
    wb = Workbook()
    head = Font(bold=True, color='FFFFFF')
    fill = PatternFill('solid', fgColor='8B1E3F')
    wrap = Alignment(wrap_text=True, vertical='top')

    def sheet(ws, cols, rows, rtl_cols=()):
        ws.append(cols)
        for c in ws[1]:
            c.font, c.fill = head, fill
        for r in rows:
            ws.append(r)
        widths = {'No.': 6, 'Pages': 22, 'Kind': 9, 'English': 60}
        for i, name in enumerate(cols, start=1):
            letter = ws.cell(row=1, column=i).column_letter
            ws.column_dimensions[letter].width = widths.get(name, 60 if name in NAMES.values() else 40)
            for cell in ws[letter][1:]:
                cell.alignment = Alignment(wrap_text=True, vertical='top', horizontal='right' if name in rtl_cols else None,
                                           readingOrder=2 if name in rtl_cols else 0)
        ws.freeze_panes = 'D2'

    ws = wb.active
    ws.title = 'All languages'
    sheet(ws, ['No.', 'Pages', 'Kind', 'English', 'Hindi', 'Urdu', 'Telugu'],
          [[i + 1, ', '.join(cat[k]['pages']), cat[k]['kind'], k] + [dicts[l].get(k, '') for l in NAMES] for i, k in enumerate(keys)],
          rtl_cols=('Urdu',))
    for lang, name in NAMES.items():
        ws = wb.create_sheet(name)
        sheet(ws, ['No.', 'Pages', 'Kind', 'English', name, 'Correction', 'Reviewer note'],
              [[i + 1, ', '.join(cat[k]['pages']), cat[k]['kind'], k, dicts[lang].get(k, ''), '', ''] for i, k in enumerate(keys)],
              rtl_cols=(name, 'Correction') if lang == 'ur' else ())
    notes = wb.create_sheet('How to review', 0)
    for line in [
        'How to review these translations',
        '',
        'Each language has its own sheet. Read the English and the translation; if the translation is wrong, unclear or',
        'reads badly, write the corrected text in the Correction column and, if useful, a note. Leave Correction empty',
        'where the translation is right.',
        '',
        'Text in curly braces, such as {total} or {seat}, is filled in by the page with a figure or a name. Keep every',
        'one exactly as written, in Latin letters, but move it to wherever it belongs in the sentence.',
        'Tags such as <a href="...">...</a> or <b>...</b> are links and bold text. Keep them, with the text between',
        'them translated.',
        'Figures stay in Western digits with Indian grouping (6,62,063). Do not use an em dash.',
        'Names of places and parties that come from the data appear in charts and tables in Latin letters. That is',
        'expected.',
        '',
        '"Kind" says where a string comes from: markup is fixed text on a page, script is a sentence the page builds',
        'from the data. The Pages column says where it appears.',
    ]:
        notes.append([line])
    notes.column_dimensions['A'].width = 120
    notes['A1'].font = Font(bold=True, size=14)
    wb.save(out)
    print('wrote %s: %d strings x %d languages' % (out, len(keys), len(NAMES)))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'translations-for-review.xlsx')
