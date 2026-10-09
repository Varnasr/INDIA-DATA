"""The SIR in brief (india/brief/): the rights section, read twice.

The page gathers what the site already holds (the burdens on electors, the
disputes, the RTI replies, the Indian Express account, women, margins) from
the published JSON when it loads. The one thing it adds is a section on the
rights of anyone who protests, which rests on the bare acts, the
Constitution, the Supreme Court's judgments and NALSA's own site.

data/india/raw/brief_research/rights.json holds each point with its law, a
verbatim quote and the address it was read at; verified.json is a second,
independent reading of every item. Only items it confirmed or corrected are
kept and its corrections are applied. Writes data/india/brief.json.

    python3 scripts/build_brief.py [--check]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / 'data' / 'india' / 'raw' / 'brief_research'
OUT = ROOT / 'data' / 'india' / 'brief.json'

# the order the groups appear in on the page
GROUPS = {'1': 'The right to protest', '2': 'Prohibitory orders', '3': 'Unlawful assembly and dispersal',
          '4': 'Where a protest may be held', '5': 'If you are arrested', '8': 'Offences often charged at protests',
          '6': 'Women', '9': 'Children', '10': 'Complaining about force used by police', '7': 'Free legal aid'}
# the second reading's own words where a point still needed plainer wording
PLAIN = {
    10: 'An Executive Magistrate, the officer in charge of the police station or, in his absence, a police officer of at least sub-inspector rank can order an unlawful assembly, or a gathering of five or more likely to disturb the peace, to disperse. Its members then have a duty to leave, and if they do not, force may be used.',
    5: "Knowingly disobeying a lawful prohibitory order is an offence if it obstructs, annoys or injures, or risks injuring, anyone lawfully employed. The punishment is up to six months' simple imprisonment or a fine of up to Rs 2,500. If the disobedience causes or tends to cause danger to life, health or safety, or a riot or affray, it is up to one year or a fine of up to Rs 5,000. It is enough to know of the order, and no intent to cause harm is needed.",
    8: 'A gathering of five or more people is an unlawful assembly only if they share one of a few aims the law lists. These are intimidating the government, a legislature or a public servant by criminal force or a show of it, resisting a law or legal process, committing mischief, criminal trespass or another offence, and using criminal force to take property or make someone act against their rights. A gathering that starts lawful can become unlawful later.',
    9: 'Knowingly joining or staying in an unlawful assembly is punishable, and staying after it has been lawfully ordered to disperse carries a higher punishment. Staying in any gathering of five or more likely to disturb the peace after a lawful order to disperse is also an offence.',
    25: 'If you have a case to bring or defend, you are entitled to free legal services if you belong to one of the groups the law lists. These include anyone in custody, women and children, members of Scheduled Castes and Scheduled Tribes, persons with disabilities, victims of trafficking or of a disaster, ethnic violence or caste atrocity, industrial workers, and anyone earning below the income limit their state sets. The legal services authority must be satisfied that you have a prima facie case, and a sworn statement of your income is normally enough.',
    13: 'Whether a protest needs police permission, and where it may be held, is set by local orders and differs from place to place. Ask at the local police station or a lawyer before the day.',
}


def build():
    R = json.loads((RAW / 'rights.json').read_text(encoding='utf-8'))
    V = {v['id']: v for v in json.loads((RAW / 'verified.json').read_text(encoding='utf-8'))}
    # the second round (October 2026), from the checked points of a legal note
    # for protesters, read twice in the same way; its ids follow the first's
    R2 = json.loads((RAW / 'rights2.json').read_text(encoding='utf-8'))
    n1 = len(R['items'])
    for v in json.loads((RAW / 'verified2.json').read_text(encoding='utf-8')):
        V[n1 + v['id']] = v
    items, dropped = [], []
    for i, it in enumerate(R['items'] + R2['items']):
        v = V.get(i)
        if not v or v['status'] not in ('confirmed', 'corrected'):
            dropped.append(it['topic'])
            continue
        it = dict(it, **(v.get('fix') or {}))
        if i in PLAIN:
            it['point'] = PLAIN[i]
        m = re.match(r'(\d+)\.\s*(.*)', it['topic'])
        if not m or m.group(1) not in GROUPS:
            sys.exit('FAIL - no group for %r' % it['topic'])
        for f in ('point', 'law', 'quote', 'url'):
            if not it.get(f):
                sys.exit('FAIL - item %d has no %s' % (i, f))
        if re.search('[\u2013\u2014;]', it['point']) or re.search(r'[a-z]: ', it['point']):
            sys.exit('FAIL - point %d breaks the writing rules' % i)
        items.append({'group': GROUPS[m.group(1)], 'title': m.group(2), 'point': it['point'], 'law': it['law'],
                      'quote': it['quote'], 'url': it['url'], 'checked': it.get('checked_on', R['as_of'])})
    if not any('15100' in x['point'] for x in items):
        sys.exit('FAIL - the legal aid helpline is missing')
    order = list(GROUPS.values())
    items.sort(key=lambda x: order.index(x['group']))
    return {'as_of': R['as_of'], 'groups': order, 'rights': items, 'dropped': dropped}


def main():
    D = build()
    text = json.dumps(D, indent=1, ensure_ascii=False) + '\n'
    if '--check' in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding='utf-8') != text:
            sys.exit('FAIL - data/india/brief.json is stale: run scripts/build_brief.py')
        print('OK: %d rights current' % len(D['rights']))
        return
    OUT.write_text(text, encoding='utf-8')
    print('wrote %d rights, dropped %d' % (len(D['rights']), len(D['dropped'])))


if __name__ == '__main__':
    main()
