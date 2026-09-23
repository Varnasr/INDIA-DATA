#!/usr/bin/env python3
"""Every ink token clears AA on every surface it is painted on, in both themes.

The palette is declared twice in `index.html`: `:root` for the light theme and
`[data-theme="dark"]` for the dark one. The dark block redefines the *surfaces*
and, until 2026-09-23, almost none of the inks painted on them. So the same
`--dblue` that is 6.3:1 on a white card was 2.9:1 on the #0f3460 one, and the
same `--red` that is the active tab in the light theme was 2.3:1 in the dark.
Nothing errored. The tab you are on simply became hard to read.

This measures the pairs the page actually paints, named in PAIRS below, rather
than every combination, because most combinations never occur and a check that
reports them is a check nobody runs.
"""
import re
import sys
from pathlib import Path

PAGE = Path(__file__).resolve().parent.parent / "index.html"

# (ink token, surface token, what it is) — each pair is a real rule in the page.
PAIRS = [
    ("--text",         "--bg",    "body text"),
    ("--text",         "--card",  "text on a card"),
    ("--text",         "--bg2",   "text on the tab strip and buttons"),
    ("--text-light",   "--card",  "the subtitle under the wordmark"),
    ("--text-light",   "--bg",    "muted prose"),
    ("--tab-inactive", "--bg2",   "the ten inactive tab labels"),
    ("--tab-active",   "--card",  "the active tab label"),
    ("--tab-text",     "--bg2",   "a tab label on hover"),
    ("--dblue",        "--card",  "every takeaway lead-in and section heading"),
    ("--dblue",        "--bg",    "the research-question headings"),
    ("--warn-ink",     "--bg2",   "the 'Not robust' caveat on the alliance chart"),
    ("--warn-ink",     "--card",  "the same caveat on a card"),
]

MIN = 4.5


def parse_block(src: str, selector: str) -> dict:
    m = re.search(re.escape(selector) + r"\s*\{(.*?)\}", src, re.S)
    if not m:
        sys.exit(f"FAIL - could not find the `{selector}` block in index.html")
    out = {}
    for name, value in re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;}]+)", m.group(1)):
        out[name] = value.strip()
    return out


def resolve(token: str, theme: dict, base: dict, seen=()) -> str:
    """Follow `var(--x)` chains, falling back to the light block for anything
    the dark block does not redeclare — which is exactly what the browser does,
    and exactly how the inks came to be wrong."""
    if token in seen:
        sys.exit(f"FAIL - `{token}` resolves in a cycle")
    value = theme.get(token, base.get(token))
    if value is None:
        sys.exit(f"FAIL - `{token}` is used by this check and declared nowhere")
    m = re.fullmatch(r"var\(\s*(--[a-z0-9-]+)\s*\)", value)
    if m:
        return resolve(m.group(1), theme, base, seen + (token,))
    return value


def luminance(hex_colour: str) -> float:
    h = hex_colour.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        sys.exit(f"FAIL - `{hex_colour}` is not a plain hex colour; this check "
                 f"cannot measure it and must not pretend otherwise")
    parts = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        parts.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = parts
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def main() -> int:
    src = PAGE.read_text(encoding="utf-8")
    light = parse_block(src, ":root")
    dark = parse_block(src, '[data-theme="dark"]')

    failures = []
    checked = 0
    for theme_name, block in (("light", {}), ("dark", dark)):
        for ink, surface, what in PAIRS:
            fg = resolve(ink, block, light)
            bg = resolve(surface, block, light)
            r = ratio(fg, bg)
            checked += 1
            if r < MIN:
                failures.append(
                    f"  {theme_name:5s}  {ink} on {surface}: {fg} on {bg} = {r:.2f}:1  ({what})")

    if failures:
        print(f"FAIL - {len(failures)} of {checked} token pairs are under {MIN}:1\n")
        print("\n".join(failures))
        return 1
    print(f"PASS - all {checked} token pairs clear {MIN}:1 in both themes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
