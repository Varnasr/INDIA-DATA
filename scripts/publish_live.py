"""Publish the newest finished production build of offtheroll.in.

Auto-publishing on the Netlify site is locked to save credits: every merge to
main builds, and nothing goes live until a build is published. The daily
publish for every locked site on the team runs from the private
Democracy-by-Design repository (tools/publish-locked.py). Actions minutes for a
private repository are billed, and on 20 and 21 October 2026 GitHub refused to
start three of its runs because of the account's billing. This repository is
public, so its Actions minutes are free, and this script is the fallback for
this one site.

It publishes only a build newer than the live one, so running it after the main
publish has already gone through changes nothing.

    python3 scripts/publish_live.py            # publish if there is a newer build
    python3 scripts/publish_live.py --dry-run  # say what it would publish

Needs NETLIFY_TOKEN.
"""
import argparse
import json
import os
import sys
import urllib.request

API = 'https://api.netlify.com/api/v1'
SITE = '01c6fa76-a649-452e-a599-392f3cabfe51'  # forindia, served at offtheroll.in


def call(path, method='GET'):
    req = urllib.request.Request(API + path, method=method,
                                 data=b'{}' if method == 'POST' else None,
                                 headers={'Authorization': 'Bearer ' + os.environ['NETLIFY_TOKEN'],
                                          'Content-Type': 'application/json',
                                          'User-Agent': 'offtheroll-publish'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    if not os.environ.get('NETLIFY_TOKEN'):
        sys.exit('NETLIFY_TOKEN is not set. Add it as an Actions secret of this repository.')
    live = call('/sites/%s' % SITE).get('published_deploy') or {}
    deploys = call('/sites/%s/deploys?per_page=20&production=true' % SITE)
    ready = [d for d in deploys if d.get('state') == 'ready' and d.get('context') == 'production'
             and d['created_at'] > live.get('created_at', '')]
    if not ready:
        print('Nothing newer than the live build of %s (%s).'
              % (live.get('created_at', '?')[:16], (live.get('commit_ref') or '?')[:7]))
        return
    new = max(ready, key=lambda d: d['created_at'])
    print('Publishing %s, built %s from %s.' % (new['id'], new['created_at'][:16], (new.get('commit_ref') or '?')[:7]))
    if a.dry_run:
        return
    call('/sites/%s/deploys/%s/restore' % (SITE, new['id']), 'POST')
    # Locking the new live deploy keeps auto-publishing off.
    call('/deploys/%s/lock' % new['id'], 'POST')
    now = call('/sites/%s' % SITE).get('published_deploy') or {}
    if now.get('id') != new['id']:
        sys.exit('Netlify still serves %s after the restore.' % now.get('id'))
    print('Live: %s, locked: %s.' % (now['id'], now.get('locked')))


if __name__ == '__main__':
    main()
