#!/usr/bin/env python3
"""What Netlify publishes: an allowlist, copied into its own folder.

    python3 scripts/stage_site.py          # check only: every top-level entry is classified
    python3 scripts/stage_site.py _site    # copy the published files into _site

Netlify's file server answers paths without regard to case, and the 404 rules
in _redirects match case exactly, so /Scripts/... and /Data/bihar/RAW/...
were served while /scripts/... and /data/bihar/raw/... were not. Publishing
only a copy of what is meant to be public closes that for every spelling:
a file that is not in the copy does not exist on the site.

The copy holds the page folders (every folder in site/pages), assets, data,
downloads, fonts, reports and the calendars, and the root files in ROOT_FILES. Inside them it
leaves out every raw/ folder, notes and code (.md, .py, .mjs, .sh), and the
working files in DATA_PRIVATE. A top-level entry in neither PUBLIC nor PRIVATE
fails the check, so a new folder has to be named one or the other.
"""
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = sorted(d for d in os.listdir(os.path.join(ROOT, 'site', 'pages'))
               if os.path.isdir(os.path.join(ROOT, 'site', 'pages', d)))
PUBLIC_DIRS = set(PAGES) | {'assets', 'data', 'downloads', 'fonts', 'reports', 'calendar'}
# feed.xml, calendar.ics, calendar/ and _headers are written by build_site.py (build_feeds.py)
ROOT_FILES = {'index.html', '404.html', '_redirects', '_headers', 'manifest.webmanifest', 'robots.txt', 'sitemap.xml', 'sw.js',
              'feed.xml', 'calendar.ics'}
PRIVATE = {'archive', 'scripts', 'site', 'supabase', 'i18n', 'netlify', '_site', '.git', '.github', '.githooks', '.claude',
           'README.md', 'CLAUDE.md', 'CITATION.cff', 'LICENSE', 'netlify.toml', '.editorconfig', '.gitattributes',
           '.gitignore', '.gitmessage', '.netlify', '__pycache__', 'node_modules'}
SKIP_EXT = ('.md', '.py', '.mjs', '.sh', '.pyc')
# files under data/ that are working files, read by no page
DATA_PRIVATE = {'data/bihar/surname_classes.csv', 'data/ac_border_classification.csv',
                'data/district_border_classification.csv', 'data/district_demography_summary.csv',
                'data/district_gdp_profile.csv', 'data/district_population_profile.csv',
                'data/district_rural_urban_profile.csv'}


def unclassified():
    return sorted(e for e in os.listdir(ROOT)
                  if e not in PUBLIC_DIRS and e not in ROOT_FILES and e not in PRIVATE)


def published():
    for f in sorted(ROOT_FILES):
        if os.path.exists(os.path.join(ROOT, f)):
            yield f
    for d in sorted(PUBLIC_DIRS):
        for base, dirs, files in os.walk(os.path.join(ROOT, d)):
            dirs[:] = sorted(x for x in dirs if x != 'raw' and not x.startswith('.') and x != '__pycache__')
            for f in sorted(files):
                rel = os.path.relpath(os.path.join(base, f), ROOT).replace(os.sep, '/')
                if f.startswith('.') or f.endswith(SKIP_EXT) or rel in DATA_PRIVATE:
                    continue
                yield rel


def main():
    bad = unclassified()
    if bad:
        raise SystemExit('FAIL - top-level entries neither published nor kept back: %s. '
                         'Add each to PUBLIC_DIRS, ROOT_FILES or PRIVATE in scripts/stage_site.py.' % ', '.join(bad))
    files = list(published())
    for f in files:
        parts = f.lower().split('/')
        assert 'raw' not in parts and parts[0] not in {p.lower() for p in PRIVATE}, f
    if len(sys.argv) < 2:
        print('OK: %d files would be published; nothing unclassified at the top level' % len(files))
        return
    out = os.path.join(ROOT, sys.argv[1])
    if os.path.exists(out):
        shutil.rmtree(out)
    for f in files:
        dst = os.path.join(out, f)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(ROOT, f), dst)
    print('staged %d files in %s' % (len(files), sys.argv[1]))


if __name__ == '__main__':
    main()
