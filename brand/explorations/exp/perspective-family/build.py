#!/usr/bin/env python3
"""exp/perspective-family — Direction B: the system architecture. One murti,
three projections, three entities:

  plan wheel      -> the Foundation   (the rta-chakra: order administered)
  front elevation -> the Temple       (the axis: order worshipped)
  anahata compact -> the community    (the heart lotus: order carried within)

All from grid.json; petals from brandlib. The falling-drop bindu appears in
every projection (hub / above the dome / at the lotus centre) — one god-point,
three vantages.

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
RG = G["rings"]
SPOKE = G["anglesDeg"]["spoke"]

INK, GOLD, IVORY = "#1A1A1A", "#C8A15A", "#F7F3E9"


def F(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def circle(cx, cy, r, stroke=None, sw=0, fill="none"):
    s = f' stroke="{stroke}" stroke-width="{F(sw)}"' if stroke else ""
    return f'<circle cx="{F(cx)}" cy="{F(cy)}" r="{F(r)}" fill="{fill}"{s}/>'


def foundation(size, line, accent):
    """Plan wheel with the Aditya ring: ring + 12 medallion dots + 12 petals + hub bindu."""
    c = size / 2
    R = size / 2 - size * 0.055
    w = size * 0.009
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">']
    p.append(circle(c, c, R, line, w))
    p.append(circle(c, c, 0.755 * R, line, w * 0.55))  # rim band containing the Adityas
    for k in range(12):
        mx, my = bl.polar(c, c, 0.877 * R, k * SPOKE)
        p.append(circle(mx, my, 0.038 * R, fill=accent))
    for k in range(12):
        a = k * SPOKE + 15
        d = bl.petal_path(c, c, 0.68 * R, 0.3 * R, a, SPOKE / 2 * 0.84)
        p.append(f'<path d="{d}" fill="none" stroke="{line}" stroke-width="{F(w * 0.8)}"/>')
        m0 = bl.polar(c, c, 0.36 * R, a)
        m1 = bl.polar(c, c, 0.56 * R, a)
        p.append(f'<line x1="{F(m0[0])}" y1="{F(m0[1])}" x2="{F(m1[0])}" y2="{F(m1[1])}" '
                 f'stroke="{line}" stroke-width="{F(w * 0.38)}" opacity="0.75"/>')
    p.append(circle(c, c, 0.3 * R, line, w * 0.8))
    p.append(circle(c, c, 0.15 * R, fill=accent))
    p.append("</svg>")
    return "\n".join(p) + "\n"


def temple(size, line, accent):
    """Front elevation: the falling drop over the dome, lotus tiers, waterline."""
    c = size / 2
    w = size * 0.011
    lr = size * 0.155            # linga half-width
    dome_top = size * 0.28
    seat = size * 0.60           # lotus seat (linga base)
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">']
    # the drop (grace descending)
    p.append(circle(c, size * 0.135, size * 0.032, fill=accent))
    # linga: dome + short shaft
    p.append(f'<path d="M {F(c - lr)} {F(seat)} L {F(c - lr)} {F(dome_top + lr)} '
             f'A {F(lr)} {F(lr)} 0 0 1 {F(c + lr)} {F(dome_top + lr)} L {F(c + lr)} {F(seat)}" '
             f'fill="none" stroke="{line}" stroke-width="{F(w)}"/>')
    # lotus: two scallop rows widening downward
    def scallops(y, half, n, rise, sw):
        seg = 2 * half / n
        d = [f"M {F(c - half)} {F(y)}"]
        for i in range(n):
            x0 = c - half + i * seg
            d.append(f"Q {F(x0 + seg / 2)} {F(y - rise)} {F(x0 + seg)} {F(y)}")
        p.append(f'<path d="{" ".join(d)}" fill="none" stroke="{line}" stroke-width="{F(sw)}"/>')
    scallops(seat + size * 0.075, size * 0.26, 5, size * 0.055, w * 0.8)
    scallops(seat + size * 0.145, size * 0.315, 6, size * 0.05, w * 0.7)
    # waterline (gold) + basin lip (ink)
    p.append(f'<line x1="{F(c - size * 0.36)}" y1="{F(seat + size * 0.21)}" x2="{F(c + size * 0.36)}" '
             f'y2="{F(seat + size * 0.21)}" stroke="{accent}" stroke-width="{F(w * 0.75)}"/>')
    p.append(f'<line x1="{F(c - size * 0.395)}" y1="{F(seat + size * 0.265)}" x2="{F(c + size * 0.395)}" '
             f'y2="{F(seat + size * 0.265)}" stroke="{line}" stroke-width="{F(w)}"/>')
    p.append("</svg>")
    return "\n".join(p) + "\n"


def anahata(size, line, accent):
    """The heart lotus: 12 petals around the bindu, unringed (the open heart)."""
    c = size / 2
    R = size / 2 - size * 0.07
    w = size * 0.0095
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">']
    for k in range(12):
        d = bl.petal_path(c, c, R, 0.34 * R, k * SPOKE - 90, SPOKE / 2 * 0.9)
        p.append(f'<path d="{d}" fill="none" stroke="{line}" stroke-width="{F(w)}"/>')
    p.append(circle(c, c, 0.34 * R, line, w * 0.8))
    p.append(circle(c, c, 0.17 * R, fill=accent))
    p.append("</svg>")
    return "\n".join(p) + "\n"


def favicon_drop(size, line, accent):
    """Ultra-reduction of the temple elevation: the drop over the dome."""
    c = size / 2
    w = size * 0.075
    lr = size * 0.30
    dome_top = size * 0.42
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">']
    p.append(circle(c, size * 0.19, size * 0.105, fill=accent))
    p.append(f'<path d="M {F(c - lr)} {F(size * 0.88)} L {F(c - lr)} {F(dome_top + lr)} '
             f'A {F(lr)} {F(lr)} 0 0 1 {F(c + lr)} {F(dome_top + lr)} L {F(c + lr)} {F(size * 0.88)}" '
             f'fill="none" stroke="{line}" stroke-width="{F(w)}"/>')
    p.append("</svg>")
    return "\n".join(p) + "\n"


def main():
    out = {
        "family-foundation.svg": foundation(256, INK, GOLD),
        "family-foundation-dark.svg": foundation(256, IVORY, GOLD),
        "family-temple.svg": temple(256, INK, GOLD),
        "family-temple-dark.svg": temple(256, IVORY, GOLD),
        "family-anahata.svg": anahata(256, INK, GOLD),
        "family-anahata-dark.svg": anahata(256, IVORY, GOLD),
        "family-temple-mono.svg": temple(256, INK, INK),
        "favicon-drop-light.svg": favicon_drop(32, INK, GOLD),
        "favicon-drop-dark.svg": favicon_drop(32, IVORY, GOLD),
    }
    for name, svg in out.items():
        (HERE / name).write_text(svg)
        print(f"  wrote {name}")
    emit_battery(HERE, {
        "name": "perspective-family",
        "claim": ("One murti, three projections, three entities: the plan wheel is the Foundation "
                  "(order administered), the front elevation is the Temple (order worshipped), the "
                  "unringed anahata lotus is the community (order carried in the heart). The gold "
                  "god-point recurs in every projection — hub, falling drop, lotus centre — and the "
                  "favicon is the axis at its smallest: the drop over the dome."),
        "hero": "family-foundation.svg",
        "ladder": [("family-foundation.svg", "plan wheel — FOUNDATION"),
                   ("family-temple.svg", "front elevation — TEMPLE"),
                   ("family-anahata.svg", "anahata — COMMUNITY / devotee")],
        "favicon_light": "favicon-drop-light.svg",
        "favicon_dark": "favicon-drop-dark.svg",
        "dark_indigo": "family-temple-dark.svg",
        "dark_charcoal": "family-anahata-dark.svg",
        "avatar": "family-anahata.svg",
        "cobrand": "family-foundation.svg",
        "poster_mark": "family-temple-dark.svg",
        "receipt_mark": "family-foundation.svg",
        "mono": "family-temple-mono.svg",
        "specimen": [(n, n.replace(".svg", "")) for n in out],
    })
    print("  wrote battery.html")


if __name__ == "__main__":
    main()
