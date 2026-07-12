#!/usr/bin/env python3
"""exp/chakra-seal — Direction A: the plan-view rta-chakra as the Foundation's
seal/crest, with its reduction ladder. Every radius/angle comes from
iconography/geometry/grid.json; petals from brandlib.petal_path. Fine-line
"modern engraving" discipline: stroke-led, two weights, gold reserved for the
god-points (bindu, medallions, water ring).

    python3 build.py    regenerates all SVGs + battery.html
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRAND = HERE.parents[2]
sys.path.insert(0, str(BRAND / "tools"))
sys.path.insert(0, str(HERE.parents[0] / "_shared"))
import brandlib as bl  # noqa: E402
from battery import emit_battery  # noqa: E402

G = json.loads((BRAND / "iconography" / "geometry" / "grid.json").read_text())
RG, NA = G["rings"], G["nali"]
SPOKE, OFF = G["anglesDeg"]["spoke"], G["anglesDeg"]["tierOffset"]

INK, GOLD, IVORY = "#1A1A1A", "#C8A15A", "#F7F3E9"


def F(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def circle(cx, cy, r, stroke=None, sw=0, fill="none"):
    s = f' stroke="{stroke}" stroke-width="{F(sw)}"' if stroke else ""
    return f'<circle cx="{F(cx)}" cy="{F(cy)}" r="{F(r)}" fill="{fill}"{s}/>'


def seal_full(size, line, accent, nali=False, mono=False):
    """The full yantra. line = structural colour, accent = god-point colour."""
    c = size / 2
    R = size / 2 - size * 0.04
    w_main, w_fine = size * 0.0055, size * 0.0032
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">']
    # rim band
    p.append(circle(c, c, R, line, w_main))
    p.append(circle(c, c, RG["waterOuter"] * R, line, w_fine))
    # water ring accent (dotted gold — the held offering)
    wr = (RG["waterOuter"] + RG["tier2PetalTip"]) / 2 * R
    p.append(f'<circle cx="{F(c)}" cy="{F(c)}" r="{F(wr)}" fill="none" stroke="{accent}" '
             f'stroke-width="{F(w_fine)}" stroke-dasharray="0.1 {F(size * 0.02)}" stroke-linecap="round"/>')
    # lotus tiers
    for k in range(12):
        d = bl.petal_path(c, c, RG["tier2PetalTip"] * R, RG["jaladhari"] * R * 0.94,
                          k * SPOKE + OFF, SPOKE / 2 * 0.92)
        p.append(f'<path d="{d}" fill="none" stroke="{line}" stroke-width="{F(w_fine)}"/>')
    for k in range(12):
        d = bl.petal_path(c, c, RG["tier1PetalTip"] * R, RG["jaladhari"] * R * 0.9,
                          k * SPOKE, SPOKE / 2 * 0.98)
        p.append(f'<path d="{d}" fill="none" stroke="{line}" stroke-width="{F(w_main)}"/>')
    # jaladhari + hub (the linga from above = the bindu)
    p.append(circle(c, c, RG["jaladhari"] * R, line, w_fine))
    p.append(circle(c, c, RG["linga"] * R, line, w_main))
    p.append(circle(c, c, RG["linga"] * R * 0.5, fill=(line if mono else accent)))
    # medallions — the 12 Adityas
    for k in range(12):
        mx, my = bl.polar(c, c, RG["medallionCenter"] * R, k * SPOKE)
        col = line if mono else accent
        p.append(circle(mx, my, RG["medallionRadius"] * R, col, w_fine))
        p.append(circle(mx, my, RG["medallionRadius"] * R * 0.35, fill=col))
    if nali:
        import math
        a0 = NA["orientationDeg"]
        aw = NA["widthOverR"] * R / 2
        for s in (-1, 1):
            x1, y1 = bl.polar(c, c, RG["waterOuter"] * R, a0 + s * math.degrees(aw / (RG["waterOuter"] * R)))
            x2, y2 = bl.polar(c, c, R * (1 + NA["lengthBeyondRimOverR"] * 0.75), a0 + s * math.degrees(aw / R) * 0.55)
            p.append(f'<line x1="{F(x1)}" y1="{F(y1)}" x2="{F(x2)}" y2="{F(y2)}" stroke="{line}" stroke-width="{F(w_main)}"/>')
        lx, ly = bl.polar(c, c, R * (1 + NA["lengthBeyondRimOverR"] * 0.75), a0)
        p.append(f'<line x1="{F(lx - aw * 0.55)}" y1="{F(ly)}" x2="{F(lx + aw * 0.55)}" y2="{F(ly)}" stroke="{line}" stroke-width="{F(w_main)}"/>')
        p.append(circle(lx, ly + size * 0.028, size * 0.011, fill=(line if mono else accent)))
    p.append("</svg>")
    return "\n".join(p) + "\n"


def wheel(size, line, accent):
    """Avatar rung: ring + single 12-petal tier + hub bindu. Bolder weights."""
    c = size / 2
    R = size / 2 - size * 0.055
    w = size * 0.011
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">']
    p.append(circle(c, c, R, line, w))
    for k in range(12):
        d = bl.petal_path(c, c, 0.66 * R, 0.3 * R, k * SPOKE, SPOKE / 2 * 0.86)
        p.append(f'<path d="{d}" fill="none" stroke="{line}" stroke-width="{F(w * 0.82)}"/>')
        m0 = bl.polar(c, c, 0.36 * R, k * SPOKE)
        m1 = bl.polar(c, c, 0.55 * R, k * SPOKE)
        p.append(f'<line x1="{F(m0[0])}" y1="{F(m0[1])}" x2="{F(m1[0])}" y2="{F(m1[1])}" '
                 f'stroke="{line}" stroke-width="{F(w * 0.4)}" opacity="0.75"/>')
    p.append(circle(c, c, 0.3 * R, line, w * 0.82))
    p.append(circle(c, c, 0.16 * R, fill=accent))
    p.append("</svg>")
    return "\n".join(p) + "\n"


def bindu_ring(size, line, accent):
    """Favicon rung: ring + gold bindu. The 16px answer: a circled point."""
    c = size / 2
    R = size / 2 - size * 0.09
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">']
    p.append(circle(c, c, R, line, size * 0.075))
    p.append(circle(c, c, R * 0.34, fill=accent))
    p.append("</svg>")
    return "\n".join(p) + "\n"


def main():
    out = {
        "seal-full-ivory.svg": seal_full(512, INK, GOLD),
        "seal-full-ivory-nali.svg": seal_full(512, INK, GOLD, nali=True),
        "seal-full-indigo.svg": seal_full(512, GOLD, GOLD),
        "seal-full-mono.svg": seal_full(512, INK, INK, mono=True),
        "wheel-ivory.svg": wheel(256, INK, GOLD),
        "wheel-dark.svg": wheel(256, IVORY, GOLD),
        "bindu-ring-light.svg": bindu_ring(32, INK, GOLD),
        "bindu-ring-dark.svg": bindu_ring(32, IVORY, GOLD),
    }
    for name, svg in out.items():
        (HERE / name).write_text(svg)
        print(f"  wrote {name}")
    emit_battery(HERE, {
        "name": "chakra-seal",
        "claim": ("The plan-view of the sanctum — the rta-chakra — is the Foundation's crest: "
                  "12 Aditya medallions, the 24-petal lotus, the linga as hub-bindu. One constructed "
                  "yantra replaces the bare typographic mark, and its reduction ladder ends in a "
                  "bindu-in-ring favicon that finally survives 16 px."),
        "hero": "seal-full-ivory.svg",
        "ladder": [("seal-full-ivory.svg", "full yantra — certificate / seal"),
                   ("wheel-ivory.svg", "wheel — avatar / operational"),
                   ("bindu-ring-light.svg", "bindu-in-ring — favicon")],
        "favicon_light": "bindu-ring-light.svg",
        "favicon_dark": "bindu-ring-dark.svg",
        "dark_indigo": "seal-full-indigo.svg",
        "dark_charcoal": "wheel-dark.svg",
        "avatar": "wheel-ivory.svg",
        "cobrand": "wheel-ivory.svg",
        "poster_mark": "seal-full-indigo.svg",
        "receipt_mark": "wheel-ivory.svg",
        "mono": "seal-full-mono.svg",
        "specimen": [(n, n.replace(".svg", "")) for n in out],
    })
    print("  wrote battery.html")


if __name__ == "__main__":
    main()
