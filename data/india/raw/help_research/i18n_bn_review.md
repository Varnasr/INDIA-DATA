# Bengali translation, second reading (help page)

File: `i18n_bn.json`, 105 strings. Every pair read against the English for
meaning, numbers, time limits, may/shall, caveats, legal terms, placeholders
({o} {s} {k} {p} {d}), digits and dashes. Placeholders all kept, Western
digits throughout, no em or en dashes.

## Changed (3)

1. **"Shown by"** (label before the link to the source report):
   `যেখানে দেখা যায়` -> `সূত্র`.
2. **"Held camps in Muslim-majority areas ... about 500 a day by its own count."**
   The translation said about 500 *people* a day (`দিনে প্রায় 500 জনের জন্য`).
   The 500 is camps a day: now `... তাদের নিজেদের হিসেবে দিনে প্রায় 500টি।`
3. **"Put together a team of lawyers and peer counsellors ..."**
   `সমমনস্ক পরামর্শদাতা` means like-minded counsellors; a peer counsellor is one
   from the same community. Now `নিজেদের সম্প্রদায়েরই পরামর্শদাতাদের (পিয়ার কাউন্সেলর)`.

## Checked and left as they are

All other 102 pairs carry the English meaning: time limits (15 days from the
ERO's decision, 30 days from the District Magistrate's order, ten days before
the last date for nominations), "may" kept as `যেতে পারে` for the special
camps and legal help, the Aadhaar identity/citizenship caveat, the West Bengal
pending-appeal sentence, and the 11 November 2025 request's scope. Legal terms
are consistent with the glossary.

## Still doubtful (not changed)

- **"One organisation in {p}." / "{k} organisations in {p}." / "Last reported active {d}."**
  are rendered with a colon (`{p}: একটি সংগঠন।`, `সর্বশেষ সক্রিয় থাকার খবর: {d}।`).
  The meaning is right, and the colon avoids attaching a case ending to a
  placeholder that may be a state name or `একাধিক রাজ্য`. It does sit against
  the site's no-colon writing rule; a native reader may prefer a form such as
  `{p}-এ একটি সংগঠন।` if every value of {p} takes `-এ` cleanly.
- **"Form 6 asks for it ... until ten days before the last date for nominations"**
  is translated faithfully. Whether the English itself is right (the statutory
  bar in section 23(3) is the last date for nominations; the ten days is the
  Commission's practice) is a question for the English page, not the translation.
- `ইলেক্টোরাল রেজিস্ট্রেশন অফিসার` carries `(ERO)` in most strings and not in
  the 15-day appeal step. Same term either way, so not changed.
