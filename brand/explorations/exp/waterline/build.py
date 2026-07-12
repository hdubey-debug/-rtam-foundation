#!/usr/bin/env python3
"""exp/waterline — Direction D (adventurous probe, timeboxed): the sanctum's
front view distilled to three strokes and a point —

    the drop (gold)  ·  the dome (arc)  ·  the lotus cup (arc)  ·  the waterline

No enclosure, no symmetry apparatus, maximum whitespace: modern-gallery
minimal. Includes the extreme reduction (drop + waterline as a divider glyph)
and a progressive-build learnability strip.

    python3 build.py    regenerates all SVGs + battery.html
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRAND = HERE.parents[2]
sys.path.insert(0, str(HERE.parents[0] / "_shared"))
from battery import emit_battery  # noqa: E402

INK, GOLD, IVORY = "#1A1A1A", "#C8A15A", "#F7F3E9"


def F(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def mark(size, line, accent, elements=("drop", "dome", "cup", "water")):
    """The waterline mark; `elements` allows the progressive build."""
    c = size / 2
    w = size * 0.018
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">']
    if "drop" in elements:
        p.append(f'<circle cx="{F(c)}" cy="{F(size * 0.285)}" r="{F(size * 0.036)}" fill="{accent}"/>')
    if "dome" in elements:
        r = size * 0.157
        p.append(f'<path d="M {F(c - r)} {F(size * 0.586)} A {F(r)} {F(r)} 0 0 1 {F(c + r)} {F(size * 0.586)}" '
                 f'fill="none" stroke="{line}" stroke-width="{F(w)}" stroke-linecap="round"/>')
    if "cup" in elements:
        p.append(f'<path d="M {F(size * 0.211)} {F(size * 0.563)} Q {F(c)} {F(size * 0.742)} '
                 f'{F(size * 0.789)} {F(size * 0.563)}" fill="none" stroke="{line}" '
                 f'stroke-width="{F(w)}" stroke-linecap="round"/>')
    if "water" in elements:
        p.append(f'<line x1="{F(size * 0.164)}" y1="{F(size * 0.695)}" x2="{F(size * 0.836)}" '
                 f'y2="{F(size * 0.695)}" stroke="{accent}" stroke-width="{F(w * 0.78)}" stroke-linecap="round"/>')
    p.append("</svg>")
    return "\n".join(p) + "\n"


def favicon(size, line, accent):
    """Three elements only: drop, dome, waterline."""
    c = size / 2
    w = size * 0.075
    r = size * 0.235
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">']
    p.append(f'<circle cx="{F(c)}" cy="{F(size * 0.20)}" r="{F(size * 0.105)}" fill="{accent}"/>')
    p.append(f'<path d="M {F(c - r)} {F(size * 0.62)} A {F(r)} {F(r)} 0 0 1 {F(c + r)} {F(size * 0.62)}" '
             f'fill="none" stroke="{line}" stroke-width="{F(w)}" stroke-linecap="round"/>')
    p.append(f'<line x1="{F(size * 0.14)}" y1="{F(size * 0.84)}" x2="{F(size * 0.86)}" y2="{F(size * 0.84)}" '
             f'stroke="{line}" stroke-width="{F(w * 0.85)}" stroke-linecap="round"/>')
    p.append("</svg>")
    return "\n".join(p) + "\n"


def divider(width=480, height=48):
    """Extreme reduction: the drop above the waterline — a section-rule glyph
    for web/print (the brand's <hr>)."""
    c = width / 2
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">']
    p.append(f'<circle cx="{F(c)}" cy="{F(height * 0.30)}" r="{F(height * 0.115)}" fill="{GOLD}"/>')
    p.append(f'<line x1="{F(width * 0.08)}" y1="{F(height * 0.72)}" x2="{F(width * 0.92)}" '
             f'y2="{F(height * 0.72)}" stroke="{GOLD}" stroke-width="1.6"/>')
    p.append("</svg>")
    return "\n".join(p) + "\n"


def learn_strip(size=200):
    """Progressive build: water -> +cup -> +dome -> +drop. The mark teaches itself."""
    steps = [("water",), ("water", "cup"), ("water", "cup", "dome"),
             ("water", "cup", "dome", "drop")]
    W = size * 4
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {size}">']
    for i, els in enumerate(steps):
        inner = mark(size, INK, GOLD, els)
        body = inner.split(">", 1)[1].rsplit("</svg>", 1)[0]
        p.append(f'<g transform="translate({i * size} 0)">{body}</g>')
        if i:
            p.append(f'<line x1="{i * size}" y1="{size * 0.2}" x2="{i * size}" y2="{size * 0.8}" '
                     f'stroke="#DDD5C6" stroke-width="1"/>')
    p.append("</svg>")
    return "\n".join(p) + "\n"


def main():
    out = {
        "waterline-mark.svg": mark(256, INK, GOLD),
        "waterline-dark.svg": mark(256, IVORY, GOLD),
        "waterline-mono.svg": mark(256, INK, INK),
        "waterline-favicon-light.svg": favicon(32, INK, GOLD),
        "waterline-favicon-dark.svg": favicon(32, IVORY, GOLD),
        "waterline-divider.svg": divider(),
        "learnability-strip.svg": learn_strip(),
    }
    for name, svg in out.items():
        (HERE / name).write_text(svg)
        print(f"  wrote {name}")
    emit_battery(HERE, {
        "name": "waterline",
        "claim": ("The adventurous probe: the sanctum's front view distilled to three strokes and a "
                  "point — drop, dome, lotus cup, waterline. No enclosure, no ornament; the holiest "
                  "possible mark that could still hang in a modern gallery. The extreme reduction "
                  "(drop over waterline) doubles as the brand's section divider."),
        "hero": "waterline-mark.svg",
        "ladder": [("learnability-strip.svg", "the mark teaches itself: water → cup → dome → drop"),
                   ("waterline-divider.svg", "extreme reduction — the brand's section rule")],
        "favicon_light": "waterline-favicon-light.svg",
        "favicon_dark": "waterline-favicon-dark.svg",
        "dark_indigo": "waterline-dark.svg",
        "dark_charcoal": "waterline-dark.svg",
        "avatar": "waterline-mark.svg",
        "cobrand": "waterline-mark.svg",
        "poster_mark": "waterline-dark.svg",
        "receipt_mark": "waterline-mark.svg",
        "mono": "waterline-mono.svg",
        "specimen": [(n, n.replace(".svg", "")) for n in out],
    })
    print("  wrote battery.html")


if __name__ == "__main__":
    main()
