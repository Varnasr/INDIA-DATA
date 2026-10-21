# Security Policy

## Reporting a Vulnerability

**Email:** care@pinpointventures.in

Please do NOT open a public issue for security vulnerabilities.

### What to include
- Description of the vulnerability
- Steps to reproduce
- Potential impact

### Response Timeline
- **Acknowledgement:** Within 48 hours
- **Resolution:** Within 7 days for critical issues

## Scope

In scope: XSS, data injection, credential exposure, content manipulation.
Out of scope: DDoS, social engineering, third-party service vulnerabilities.

## Licence, forks and takedowns

See [LICENSE](../LICENSE). The code is MIT. The analysis, charts, maps and
tables are CC BY 4.0, which allows reuse with credit. Third-party data keeps its
publishers' terms.

A fork must keep the credit to "SIR analysis for India, ImpactMojo" and the
credit to the official sources. A fork must not present these figures as its own
research, remove the notes on what a count cannot show, or add voter-level lists
(names or EPIC numbers) to the repository. This project publishes aggregate
counts only.

If you find a copy that removes the credit, or a copy that adds voter-level
lists with this project's name on it:

1. Note the URL and the files concerned.
2. File a notice with GitHub at https://github.com/contact, following its DMCA
   policy where the credit has been removed.
3. Tell care@pinpointventures.in so it is tracked.

## The public key in the code

The Supabase key in `assets/` is the project's public anon key. It can only call
one function, which adds one to a daily tally; the table is closed to it. If you
fork the project, use your own Supabase project and key.

