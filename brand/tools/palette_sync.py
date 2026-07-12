#!/usr/bin/env python3
"""Palette canon gate: brand/palette/colors.json is the ONLY place a brand
colour value is defined. Every other copy is derived or verified against it:

  palette/colors.css        GENERATED here (palette_sync.py --write)
  spec/brand.json tokens    verified: each token hex must equal the canon hex
  render_md_to_pdf.py       builds its :root block via css_root_vars()

  palette_sync.py            check mode (build.sh gate): colors.css on disk
                             matches regenerated CSS byte-for-byte AND every
                             brand.json token matches canon. Exit 1 on drift.
  palette_sync.py --write    (re)generate palette/colors.css, then check tokens.

One colour, three namespaces (historical; renames deferred to brand.json v2):
  brand.json token · colors.json name · CSS custom property — see NAMES below.
"""
import argparse
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
BRAND = TOOLS.parent
PALETTE_JSON = BRAND / "palette" / "colors.json"
PALETTE_CSS = BRAND / "palette" / "colors.css"
SPEC = BRAND / "spec" / "brand.json"

# (css var suffix, colors.json name, brand.json token or None if spec-unused)
NAMES = [
    ("gold",      "antiqueGold",   "gold"),
    ("ivory",     "warmIvory",     "ivory"),
    ("charcoal",  "charcoalBlack", "ink"),
    ("sandstone", "sandstone",     "sandstone"),
    ("indigo",    "deepIndigo",    "indigo"),
    ("bronze",    "bronze",        None),
    ("stone",     "stoneGray",     "stone"),
    # v0.2.0 substance palette (2026-07-12); spec tokens for the three the
    # constructed marks consume, None for the rest until they ship in spec.
    ("mahakala",     "mahakala",    "mahakala"),
    ("bhasma-light", "bhasmaLight", "bhasma"),
    ("bhasma-deep",  "bhasmaDeep",  None),
    ("tamra",        "tamraCopper", None),
    ("chandra",      "chandraMoon", "chandra"),
]


def load_canon() -> dict:
    """colors.json flattened to {name: hex}."""
    data = json.loads(PALETTE_JSON.read_text())
    hexes = {}
    for group in ("primary", "secondary", "substances"):
        for name, t in data.get(group, {}).items():
            hexes[name] = t["hex"]
    return hexes


def css_root_vars(indent: str = "  ") -> str:
    """The --rtam-* custom-property lines, for embedding in a :root block
    (used by render_md_to_pdf.py so it carries no hardcoded copy)."""
    canon = load_canon()
    lines = []
    for css, jname, tok in NAMES:
        spec = f" · brand.json: {tok}" if tok else ""
        lines.append(f"{indent}--rtam-{css}: {canon[jname]};  /* colors.json: {jname}{spec} */")
    return "\n".join(lines)


def css_text() -> str:
    """Full colors.css content (deterministic)."""
    return f"""/* RTAM Foundation — color tokens
 * GENERATED from brand/palette/colors.json by tools/palette_sync.py --write.
 * Do not edit by hand: change colors.json and regenerate (build.sh gates drift).
 * Name mapping per line: CSS var · colors.json name · brand.json spec token.
 */

:root {{
{css_root_vars()}

  /* Semantic aliases */
  --rtam-bg:       var(--rtam-ivory);
  --rtam-fg:       var(--rtam-charcoal);
  --rtam-accent:   var(--rtam-gold);
  --rtam-muted:    var(--rtam-stone);
}}

/* Dark scheme — charcoal working dark (docs, UI) */
.rtam-dark {{
  --rtam-bg:     var(--rtam-charcoal);
  --rtam-fg:     var(--rtam-ivory);
  --rtam-accent: var(--rtam-gold);
  --rtam-muted:  var(--rtam-stone);
}}

/* Night scheme — LEGACY (retired 2026-07-12: indigo is retired from brand
 * surfaces; night now means mahakala). Kept only for committed legacy
 * assets; new work uses .rtam-garbhagriha. */
.rtam-night {{
  --rtam-bg:     var(--rtam-indigo);
  --rtam-fg:     var(--rtam-ivory);
  --rtam-accent: var(--rtam-gold);
  --rtam-muted:  var(--rtam-stone);
}}

/* Garbhagriha — the lead register (founder-locked 2026-07-12): the sanctum
 * at aarti. Ground is the linga dark; display type is the dipa flame
 * (gold, 7.63:1 AAA); reading text is vibhuti ash (10.42:1 AAA). All dark
 * surfaces, city print, video. */
.rtam-garbhagriha {{
  --rtam-bg:     var(--rtam-mahakala);
  --rtam-fg:     var(--rtam-bhasma-light);
  --rtam-accent: var(--rtam-gold);
  --rtam-muted:  var(--rtam-bhasma-deep);
}}

/* Bhasma-day — the reading register: chandra moon-paper (de-yellowed),
 * charcoal ink, tamra copper as the functional accent (5.65:1 AA). Website
 * body, documents. */
.rtam-day {{
  --rtam-bg:     var(--rtam-chandra);
  --rtam-fg:     var(--rtam-charcoal);
  --rtam-accent: var(--rtam-tamra);
  --rtam-muted:  var(--rtam-bhasma-deep);
}}
"""


def check_spec_tokens() -> list[str]:
    """Every brand.json token must equal the canon hex for its mapped name."""
    canon = load_canon()
    tokens = json.loads(SPEC.read_text())["tokens"]
    by_token = {tok: jname for _, jname, tok in NAMES if tok}
    errs = []
    for tok, hexval in tokens.items():
        jname = by_token.get(tok)
        if jname is None:
            errs.append(f"brand.json token '{tok}' has no canon mapping in palette_sync.NAMES")
        elif hexval.upper() != canon[jname].upper():
            errs.append(f"brand.json token '{tok}' = {hexval} but canon {jname} = {canon[jname]}")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="regenerate colors.css")
    args = ap.parse_args()
    errs = []
    want = css_text()
    if args.write:
        PALETTE_CSS.write_text(want)
        print(f"  wrote {PALETTE_CSS.relative_to(BRAND.parent)}")
    else:
        have = PALETTE_CSS.read_text() if PALETTE_CSS.exists() else ""
        if have != want:
            errs.append("colors.css is stale or hand-edited (rerun palette_sync.py --write)")
    errs += check_spec_tokens()
    if errs:
        print("PALETTE GATE FAILED:")
        for e in errs:
            print("  -", e)
        return 1
    print("  palette canon OK (colors.css in sync; brand.json tokens match colors.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
