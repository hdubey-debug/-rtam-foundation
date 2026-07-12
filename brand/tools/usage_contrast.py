#!/usr/bin/env python3
"""Usage-level contrast gate: every brand.json output declares the grounds it
ships on (`grounds`: token names); this tool checks each output's resolved
fills against every declared ground.

Floors (why they differ): WCAG 1.4.3 exempts logotype text, so glyph runs that
ARE the brand name get a reported 3.0:1 advisory only (ceremonial variants like
all-gold-on-ivory are legal by design and eye-gated instead). Informative text
baked into an asset (role `support`, and any future tagline/url roles) is NOT
the logo — it must clear the 4.5:1 body floor on every declared ground, or the
build fails. This is the gate that would have caught the stone-on-ivory
donation-lockup support line (1.92:1).

Shapes (bindu/ring/rule) are decorative: reported, never gated.

  usage_contrast.py          gate (build.sh runs this)
  usage_contrast.py -v       also print every passing pair
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import brandlib as bl  # noqa: E402
from contrast import ratio  # noqa: E402

INFO_ROLES = {"support", "tagline", "url"}   # informative text -> hard 4.5 floor
INFO_MIN = 4.5
LOGO_ADVISORY = 3.0                          # logotype runs -> reported only


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    brand = bl.load_brand()
    fails, warns, n_pairs = [], [], 0
    for asset, output in bl.all_outputs(brand):
        grounds = output.get("grounds")
        if not grounds:
            fails.append(f"{output['path']}: no declared grounds (add \"grounds\" to the output)")
            continue
        model = bl.resolve(brand, asset, output)
        for g in grounds:
            bg = bl.color(brand, g)
            for r in model["runs"]:
                n_pairs += 1
                rr = ratio(r["fill"], bg)
                info = r["role"] in INFO_ROLES
                if info and rr < INFO_MIN:
                    fails.append(f"{output['path']}: {r['role']} text {r['fill']} on {g} = {rr:.2f}:1 < {INFO_MIN}")
                elif not info and rr < LOGO_ADVISORY:
                    warns.append(f"{output['path']}: logotype {r['role']} {r['fill']} on {g} = {rr:.2f}:1 (<3.0 advisory; eye-gated)")
                elif args.verbose:
                    print(f"  ok {output['path']}: {r['role']} on {g} = {rr:.2f}:1")
    for w in warns:
        print(f"  WARN {w}")
    if fails:
        print("USAGE-CONTRAST GATE FAILED:")
        for f in fails:
            print("  -", f)
        return 1
    print(f"  usage contrast OK ({n_pairs} run x ground pairs; "
          f"{len(warns)} logotype advisories, 0 informative-text failures)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
