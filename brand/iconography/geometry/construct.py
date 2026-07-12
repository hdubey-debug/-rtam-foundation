#!/usr/bin/env python3
"""Generate the murti construction drawings from grid.json.

Outputs (same directory):
  plan-view-pure.svg   the rta-chakra, pure rotational symmetry
  plan-view-nali.svg   same, with the nali index notch breaking the rim
  front-elevation.svg  the sanctum axis: light shaft, drop, linga, lotus,
                       waterline, rim, nali stream, floor pool

Engraving discipline: stroke-led fine linework (no flat clip-art fills),
charcoal ink on ivory, gold reserved for the god-points (bindu, drop,
medallions, waterline). Construction guides (spoke rays, ring circles) are
dashed stone-gray and live in their own layer group so consumers can drop
them. These drawings are the single geometric source for every Phase-2 mark.

    python3 construct.py        # writes the three SVGs
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
G = json.loads((HERE / "grid.json").read_text())

INK = "#1A1A1A"
GOLD = "#C8A15A"
STONE = "#B8B1A4"
IVORY = "#F7F3E9"

R = 500.0  # rim outer radius in drawing units
CX = CY = 600.0
VB = 1200


def P(r, deg, cx=None, cy=None):
    cx = CX if cx is None else cx
    cy = CY if cy is None else cy
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def fmt(x):
    return f"{x:.2f}".rstrip("0").rstrip(".")


def petal(tip_r, base_r, center_deg, half_w_deg, belly=1.35):
    """Pointed lotus petal, stroke path: base->belly->tip->belly->base.
    `belly` pushes the side control points outward for the ogive curve."""
    tx, ty = P(tip_r, center_deg)
    b1x, b1y = P(base_r, center_deg - half_w_deg)
    b2x, b2y = P(base_r, center_deg + half_w_deg)
    mid_r = base_r + (tip_r - base_r) * 0.55
    c1x, c1y = P(mid_r, center_deg - half_w_deg * belly)
    c2x, c2y = P(tip_r * 0.97, center_deg - half_w_deg * 0.35)
    c3x, c3y = P(tip_r * 0.97, center_deg + half_w_deg * 0.35)
    c4x, c4y = P(mid_r, center_deg + half_w_deg * belly)
    d = (f"M {fmt(b1x)} {fmt(b1y)} C {fmt(c1x)} {fmt(c1y)} {fmt(c2x)} {fmt(c2y)} {fmt(tx)} {fmt(ty)} "
         f"C {fmt(c3x)} {fmt(c3y)} {fmt(c4x)} {fmt(c4y)} {fmt(b2x)} {fmt(b2y)}")
    # midrib: from base-centre 15% out to 70% of the petal length
    r0 = base_r + (tip_r - base_r) * 0.15
    r1 = base_r + (tip_r - base_r) * 0.70
    m0, m1 = P(r0, center_deg), P(r1, center_deg)
    rib = f"M {fmt(m0[0])} {fmt(m0[1])} L {fmt(m1[0])} {fmt(m1[1])}"
    return d, rib


def circle(r, stroke, sw, dash=None, fill="none", cx=None, cy=None):
    cx = CX if cx is None else cx
    cy = CY if cy is None else cy
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r)}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>')


def plan_view(with_nali: bool) -> str:
    rg = G["rings"]
    spokes = G["anglesDeg"]["spoke"]
    off = G["anglesDeg"]["tierOffset"]
    n = G["counts"]["petalsPerTier"]
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VB} {VB}">')
    parts.append(f'<rect width="{VB}" height="{VB}" fill="{IVORY}"/>')

    # construction guides (droppable layer)
    parts.append('<g id="construction" opacity="0.55">')
    for key in ("jaladhari", "tier1PetalTip", "tier2PetalTip", "waterOuter", "medallionCenter"):
        parts.append(circle(rg[key] * R, STONE, 1, dash="6 7"))
    for k in range(n):
        a = k * spokes
        x1, y1 = P(rg["linga"] * R, a)
        x2, y2 = P(R * 1.04, a)
        parts.append(f'<line x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" y2="{fmt(y2)}" '
                     f'stroke="{STONE}" stroke-width="1" stroke-dasharray="2 9"/>')
    parts.append("</g>")

    # rim (two lines: outer + inner edge of the band)
    parts.append(circle(R, INK, 3))
    parts.append(circle(rg["waterOuter"] * R, INK, 1.5))
    # water annulus accent
    parts.append(circle((rg["waterOuter"] + rg["tier2PetalTip"]) / 2 * R, GOLD, 1, dash="1 6"))

    # lotus tiers (lower tier first, offset half a step)
    parts.append(f'<g id="lotus" fill="none" stroke="{INK}">')
    for k in range(n):
        a = k * spokes + off
        d, rib = petal(rg["tier2PetalTip"] * R, rg["jaladhari"] * R * 0.94, a, spokes / 2 * 0.92)
        parts.append(f'<path d="{d}" stroke-width="2"/>')
        parts.append(f'<path d="{rib}" stroke-width="1" opacity="0.6"/>')
    for k in range(n):
        a = k * spokes
        d, rib = petal(rg["tier1PetalTip"] * R, rg["jaladhari"] * R * 0.9, a, spokes / 2 * 0.98)
        parts.append(f'<path d="{d}" stroke-width="2.5"/>')
        parts.append(f'<path d="{rib}" stroke-width="1" opacity="0.6"/>')
    parts.append("</g>")

    # jaladhari ring + the hub: the linga from above = the bindu
    parts.append(circle(rg["jaladhari"] * R, INK, 2))
    parts.append(circle(rg["linga"] * R, INK, 2.5))
    parts.append(circle(rg["linga"] * R * 0.5, GOLD, 0, fill=GOLD))

    # medallions — the 12 Adityas
    for k in range(G["counts"]["medallions"]):
        a = k * spokes
        mx, my = P(rg["medallionCenter"] * R, a)
        parts.append(circle(rg["medallionRadius"] * R, GOLD, 2, cx=mx, cy=my))
        parts.append(circle(rg["medallionRadius"] * R * 0.35, GOLD, 0, fill=GOLD, cx=mx, cy=my))

    if with_nali:
        na = G["nali"]
        aw = na["widthOverR"] * R / 2
        a0 = na["orientationDeg"]
        # channel: two parallel walls from the water edge out past the rim
        for s in (-1, 1):
            x1, y1 = P(rg["waterOuter"] * R, a0 + s * math.degrees(aw / (rg["waterOuter"] * R)))
            x2, y2 = P(R * (1 + na["lengthBeyondRimOverR"]), a0 + s * math.degrees(aw / R) * 0.55)
            parts.append(f'<line x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" y2="{fmt(y2)}" '
                         f'stroke="{INK}" stroke-width="2.5"/>')
        # lip + the returned drop
        lx, ly = P(R * (1 + na["lengthBeyondRimOverR"]), a0)
        parts.append(f'<line x1="{fmt(lx - aw * 0.55)}" y1="{fmt(ly)}" x2="{fmt(lx + aw * 0.55)}" y2="{fmt(ly)}" '
                     f'stroke="{INK}" stroke-width="2.5"/>')
        parts.append(circle(6, GOLD, 0, fill=GOLD, cx=lx, cy=ly + 18))

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def front_elevation() -> str:
    rg, el = G["rings"], G["elevation"]
    W, H = 1200, 1500
    cx = W / 2
    ground = 1310.0
    rimh = el["rimHeight"] * R
    rim_top = ground - rimh
    water_y = ground - rimh * el["waterlineOverRimHeight"]
    lotus_top = rim_top - el["lotusCupTopAboveRim"] * R
    linga_r = rg["linga"] * R
    linga_top = lotus_top - el["lingaHeightAboveLotus"] * R
    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">')
    p.append(f'<rect width="{W}" height="{H}" fill="{IVORY}"/>')

    # light shaft (construction layer)
    p.append(f'<g opacity="0.6"><line x1="{fmt(cx - 90)}" y1="40" x2="{fmt(cx - 46)}" y2="{fmt(linga_top - 24)}" stroke="{STONE}" stroke-width="1" stroke-dasharray="7 8"/>'
             f'<line x1="{fmt(cx + 90)}" y1="40" x2="{fmt(cx + 46)}" y2="{fmt(linga_top - 24)}" stroke="{STONE}" stroke-width="1" stroke-dasharray="7 8"/></g>')
    # abhisheka stream + the drop
    p.append(f'<line x1="{fmt(cx)}" y1="46" x2="{fmt(cx)}" y2="{fmt(linga_top - 58)}" stroke="{GOLD}" stroke-width="1.5" stroke-dasharray="2 10"/>')
    p.append(f'<circle cx="{fmt(cx)}" cy="{fmt(linga_top - 34)}" r="9" fill="{GOLD}"/>')

    # linga: dome + shaft
    p.append(f'<path d="M {fmt(cx - linga_r)} {fmt(lotus_top)} L {fmt(cx - linga_r)} {fmt(linga_top + linga_r)} '
             f'A {fmt(linga_r)} {fmt(linga_r)} 0 0 1 {fmt(cx + linga_r)} {fmt(linga_top + linga_r)} '
             f'L {fmt(cx + linga_r)} {fmt(lotus_top)}" fill="none" stroke="{INK}" stroke-width="3"/>')

    # lotus cup: two scallop rows between jaladhari and tier tips
    def scallops(y_base, half_span, n_vis, rise, sw):
        seg = 2 * half_span / n_vis
        d = [f"M {fmt(cx - half_span)} {fmt(y_base)}"]
        for i in range(n_vis):
            x0 = cx - half_span + i * seg
            d.append(f"Q {fmt(x0 + seg / 2)} {fmt(y_base - rise)} {fmt(x0 + seg)} {fmt(y_base)}")
        p.append(f'<path d="{" ".join(d)}" fill="none" stroke="{INK}" stroke-width="{sw}"/>')

    scallops(lotus_top + 26, rg["tier1PetalTip"] * R, 6, 34, 2.5)   # upper tier (6 visible of 12)
    scallops(lotus_top + 56, rg["tier2PetalTip"] * R, 7, 30, 2)     # lower tier, offset
    # jaladhari seat line
    p.append(f'<line x1="{fmt(cx - rg["jaladhari"] * R)}" y1="{fmt(lotus_top)}" x2="{fmt(cx + rg["jaladhari"] * R)}" y2="{fmt(lotus_top)}" stroke="{INK}" stroke-width="2"/>')

    # basin: rim walls + top, waterline
    for s in (-1, 1):
        x = cx + s * R
        xi = cx + s * rg["waterOuter"] * R
        p.append(f'<line x1="{fmt(x)}" y1="{fmt(ground)}" x2="{fmt(x)}" y2="{fmt(rim_top)}" stroke="{INK}" stroke-width="3"/>')
        p.append(f'<line x1="{fmt(min(x, xi))}" y1="{fmt(rim_top)}" x2="{fmt(max(x, xi))}" y2="{fmt(rim_top)}" stroke="{INK}" stroke-width="3"/>')
        p.append(f'<line x1="{fmt(xi)}" y1="{fmt(rim_top)}" x2="{fmt(xi)}" y2="{fmt(water_y)}" stroke="{INK}" stroke-width="1.5"/>')
    p.append(f'<line x1="{fmt(cx - rg["waterOuter"] * R)}" y1="{fmt(water_y)}" x2="{fmt(cx + rg["waterOuter"] * R)}" y2="{fmt(water_y)}" stroke="{GOLD}" stroke-width="2"/>')
    p.append(f'<line x1="{fmt(cx - R)}" y1="{fmt(ground)}" x2="{fmt(cx + R)}" y2="{fmt(ground)}" stroke="{INK}" stroke-width="2"/>')

    # medallions on the rim face (7 visible of 12)
    for k in range(-3, 4):
        mx = cx + math.sin(math.radians(k * 30)) * rg["medallionCenter"] * R
        p.append(f'<circle cx="{fmt(mx)}" cy="{fmt(rim_top + rimh * 0.32)}" r="{fmt(rg["medallionRadius"] * R * (0.55 + 0.45 * math.cos(math.radians(k * 30))))}" fill="none" stroke="{GOLD}" stroke-width="2"/>')

    # nali: spout at front centre + stream + floor pool
    p.append(f'<line x1="{fmt(cx - 14)}" y1="{fmt(water_y)}" x2="{fmt(cx - 14)}" y2="{fmt(ground + 6)}" stroke="{INK}" stroke-width="1.5"/>')
    p.append(f'<line x1="{fmt(cx + 14)}" y1="{fmt(water_y)}" x2="{fmt(cx + 14)}" y2="{fmt(ground + 6)}" stroke="{INK}" stroke-width="1.5"/>')
    p.append(f'<line x1="{fmt(cx)}" y1="{fmt(water_y + 8)}" x2="{fmt(cx)}" y2="{fmt(ground + 52)}" stroke="{GOLD}" stroke-width="1.5" stroke-dasharray="2 8"/>')
    pool_w = el["poolWidth"] * R
    p.append(f'<rect x="{fmt(cx - pool_w / 2)}" y="{fmt(ground + 52)}" width="{fmt(pool_w)}" height="{fmt(el["poolDepth"] * R)}" fill="none" stroke="{INK}" stroke-width="2"/>')
    p.append(f'<line x1="{fmt(cx - pool_w / 2 + 8)}" y1="{fmt(ground + 52 + 14)}" x2="{fmt(cx + pool_w / 2 - 8)}" y2="{fmt(ground + 52 + 14)}" stroke="{GOLD}" stroke-width="1.5"/>')

    p.append("</svg>")
    return "\n".join(p) + "\n"


def main():
    (HERE / "plan-view-pure.svg").write_text(plan_view(False))
    (HERE / "plan-view-nali.svg").write_text(plan_view(True))
    (HERE / "front-elevation.svg").write_text(front_elevation())
    print("wrote plan-view-pure.svg, plan-view-nali.svg, front-elevation.svg")


if __name__ == "__main__":
    main()
