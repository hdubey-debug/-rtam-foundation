#!/usr/bin/env python3
"""exp/letterform — Direction C (conservative hedge): the identity stays
typographic, but the letters learn the murti's lesson.

1. Re-cut R: the leg gains a below-baseline tail that tapers toward the
   bindu — the R reaches for its root. Kills the "R." punctuation reading.
   (Drawn as a same-fill overlay on the Cinzel outline; raster-identical to
   a boolean union — production union is a Phase-3 task.)
2. Script parity: the Devanagari ऋ is optically undersized next to the Latin
   R (ink 53% vs 79% of canvas). Measured with fontTools bounds and rescaled
   to ink-height parity.
3. Mixed-case "Ṛtam" in Marcellus (the vendored Phase-1 candidate) with the
   drawn bindu — the system finally whispers.
4. Bindu-gap A/B/C at wordmark scale (bindu_abc pattern).

    python3 build.py    regenerates all SVGs + battery.html
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRAND = HERE.parents[2]
sys.path.insert(0, str(BRAND / "tools"))
sys.path.insert(0, str(HERE.parents[0] / "_shared"))
import brandlib as bl  # noqa: E402
from battery import emit_battery  # noqa: E402
from fontTools.pens.boundsPen import BoundsPen  # noqa: E402
from fontTools.pens.transformPen import TransformPen  # noqa: E402

INK, GOLD, IVORY = "#1A1A1A", "#C8A15A", "#F7F3E9"
brand = bl.load_brand()


def F(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def glyph_bboxes(ttf: Path, text: str, fs: float, start_x: float, y: float,
                 letter_spacing: float = 0.0):
    """Tight ink bbox per glyph, positioned (same transform as outline_paths)."""
    infos, positions, upem = bl._shape(ttf, text)
    tt = bl._ttfont(ttf)
    gs = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    s = fs / upem
    cx = start_x
    boxes = []
    for i, (info, pos) in enumerate(zip(infos, positions)):
        gname = order[info.codepoint]
        bp = BoundsPen(gs)
        tp = TransformPen(bp, (s, 0, 0, -s, cx + pos.x_offset * s, y - pos.y_offset * s))
        gs[gname].draw(tp)
        if bp.bounds:
            x0, y1n, x1, y0n = bp.bounds  # note: y flipped by transform
            boxes.append((min(x0, x1), min(y1n, y0n), max(x0, x1), max(y1n, y0n)))
        cx += pos.x_advance * s
        last = (i + 1 == len(infos) or infos[i + 1].cluster != info.cluster)
        if letter_spacing and last:
            cx += letter_spacing
    return boxes


def svg_open(size_w, size_h):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size_w} {size_h}">']


def text_paths(ttf, text, fs, start_x, y, fill, letter_spacing=0.0):
    return [f'<path d="{d}" fill="{fill}"/>'
            for d in bl.outline_paths(ttf, text, fs, start_x, y, letter_spacing)]


# --- 1 · the re-cut R monogram ------------------------------------------------
def recut_monogram(size, glyph_col, bindu_col):
    """Cinzel R (monogram metrics from brand.json rdot-icon) + the tail overlay
    + the bindu. Tail: leaves the leg's foot just above the baseline and
    tapers below it toward the bindu."""
    fs, x, y = 200, 119.9, 166.33          # rdot-icon spec metrics (256 canvas)
    bcx, bcy, br = 128, 213, 16.67
    ttf = bl.ttf_path(brand, "cinzel", 600)
    sx = bl.start_x_for(brand, {"text": "R", "font": "cinzel", "weight": 600,
                                "fs": fs, "x": x, "anchor": "middle"})
    (gx0, gy0, gx1, gy1) = glyph_bboxes(ttf, "R", fs, sx, y)[0]
    p = svg_open(size, size)
    p += text_paths(ttf, "R", fs, sx, y, glyph_col)
    # tail: from inside the leg's foot, swooping below the baseline toward the
    # bindu; a tapered sliver (outer curve out, inner curve back, zero-width tip)
    foot_x = gx1 - 6            # just inside the leg's right extreme
    base = y + 1                # sit on the baseline
    tip = (bcx + br + 14, bcy - br - 4)   # aimed at the bindu's shoulder
    d = (f"M {F(foot_x - 20)} {F(base - 26)} "
         f"C {F(foot_x + 2)} {F(base - 8)} {F(foot_x + 6)} {F(base + 10)} "
         f"{F(tip[0])} {F(tip[1])} "
         f"C {F(foot_x - 6)} {F(base + 8)} {F(foot_x - 14)} {F(base - 10)} "
         f"{F(foot_x - 30)} {F(base - 22)} Z")
    p.append(f'<path d="{d}" fill="{glyph_col}"/>')
    p.append(f'<circle cx="{bcx}" cy="{bcy}" r="{br}" fill="{bindu_col}"/>')
    p.append("</svg>")
    return "\n".join(p) + "\n"


# --- 2 · script parity --------------------------------------------------------
def parity_pair(size=256):
    """Side-by-side R and ऋ at measured ink-height parity, in one strip."""
    ttf_r = bl.ttf_path(brand, "cinzel", 600)
    ttf_ri = bl.ttf_path(brand, "tiro", 400)
    r_box = glyph_bboxes(ttf_r, "R", 200, 0, 200)[0]
    r_h = r_box[3] - r_box[1]
    ri_box = glyph_bboxes(ttf_ri, "ऋ", 210, 0, 200)[0]
    ri_h = ri_box[3] - ri_box[1]
    ri_fs = 210 * (r_h / ri_h)
    # strip 2:1 — R centred in left square, parity-scaled ऋ in right square
    W, H = 2 * size, size
    p = svg_open(W, H)
    for (ttf, text, fs, cx) in ((ttf_r, "R", 200, size / 2), (ttf_ri, "ऋ", ri_fs, size * 1.5)):
        adv = bl.total_advance(ttf, text, fs)
        box = glyph_bboxes(ttf, text, fs, 0, 0)[0]
        ink_mid_y = (box[1] + box[3]) / 2
        y = H / 2 - ink_mid_y          # centre ink vertically
        sxx = cx - adv / 2
        p += text_paths(ttf, text, fs, sxx, y, INK)
    p.append(f'<line x1="{size}" y1="{H * 0.14}" x2="{size}" y2="{H * 0.86}" stroke="{GOLD}" stroke-width="2"/>')
    p.append("</svg>")
    return "\n".join(p) + "\n", ri_fs, r_h, ri_h


def ri_parity_icon(size, col, ri_fs):
    """The ऋ monogram at parity scale, recentred (replaces fs 210)."""
    ttf = bl.ttf_path(brand, "tiro", 400)
    adv = bl.total_advance(ttf, "ऋ", ri_fs)
    box = glyph_bboxes(ttf, "ऋ", ri_fs, 0, 0)[0]
    ink_mid = (box[1] + box[3]) / 2
    y = size / 2 - ink_mid
    sx = size / 2 - adv / 2
    p = svg_open(size, size)
    p += text_paths(ttf, "ऋ", ri_fs, sx, y, col)
    p.append("</svg>")
    return "\n".join(p) + "\n"


# --- 3 · mixed-case Rtam in Marcellus ------------------------------------------
def mixedcase_wordmark(letters_col, bindu_col):
    """"Rtam" in Marcellus with the drawn bindu under the R's ink centre.
    Bindu grammar: cy = baseline + 0.233*fs, r = fs/12."""
    fs, y = 150, 170
    ttf = BRAND / "fonts" / "marcellus" / "marcellus-400.ttf"
    adv = bl.total_advance(ttf, "Rtam", fs)
    W, H = 720, 260
    sx = (W - adv) / 2
    boxes = glyph_bboxes(ttf, "Rtam", fs, sx, y)
    r0 = boxes[0]
    bcx = (r0[0] + r0[2]) / 2
    bcy, br = y + 0.233 * fs, fs / 12
    p = svg_open(W, H)
    p += text_paths(ttf, "Rtam", fs, sx, y, letters_col)
    p.append(f'<circle cx="{F(bcx)}" cy="{F(bcy)}" r="{F(br)}" fill="{bindu_col}"/>')
    p.append("</svg>")
    return "\n".join(p) + "\n"


# --- 4 · bindu gap study --------------------------------------------------------
def gap_study():
    """Three R+bindu at wordmark scale: shipped gap, tightened, enlarged dot."""
    fs, y = 120, 150
    ttf = bl.ttf_path(brand, "cinzel", 500)
    W, H = 900, 230
    p = svg_open(W, H)
    variants = [("A — shipped (cy=b+0.233fs, r=fs/12)", 0.233, 1 / 12),
                ("B — tightened (cy=b+0.20fs)", 0.20, 1 / 12),
                ("C — heavier dot (r=fs/10)", 0.233, 1 / 10)]
    for i, (label, cyk, rk) in enumerate(variants):
        ox = 60 + i * 290
        boxes = glyph_bboxes(ttf, "R", fs, ox, y)
        r0 = boxes[0]
        bcx = (r0[0] + r0[2]) / 2
        p += text_paths(ttf, "R", fs, ox, y, INK)
        p.append(f'<circle cx="{F(bcx)}" cy="{F(y + cyk * fs)}" r="{F(fs * rk)}" fill="{GOLD}"/>')
        p.append(f'<text x="{F(ox + 45)}" y="{H - 14}" font-family="sans-serif" font-size="12" '
                 f'text-anchor="middle" fill="#888">{label}</text>')
    p.append("</svg>")
    return "\n".join(p) + "\n"


def main():
    strip, ri_fs, r_h, ri_h = parity_pair()
    out = {
        "rdot-recut-sacred.svg": recut_monogram(256, INK, GOLD),
        "rdot-recut-dark.svg": recut_monogram(256, IVORY, GOLD),
        "rdot-recut-mono.svg": recut_monogram(256, INK, INK),
        "parity-pair.svg": strip,
        "ri-parity-black.svg": ri_parity_icon(256, INK, ri_fs),
        "rtam-mixedcase.svg": mixedcase_wordmark(INK, GOLD),
        "rtam-mixedcase-dark.svg": mixedcase_wordmark(IVORY, GOLD),
        "bindu-gap-study.svg": gap_study(),
    }
    for name, svg in out.items():
        (HERE / name).write_text(svg)
        print(f"  wrote {name}")
    print(f"  parity: R ink h={r_h:.1f}, ऋ ink h={ri_h:.1f} @fs210 -> parity fs={ri_fs:.1f}")
    emit_battery(HERE, {
        "name": "letterform",
        "claim": ("The conservative hedge: the identity stays typographic, but the letters learn the "
                  "murti's lesson. The R's leg is re-cut with a tail that reaches below the baseline "
                  "toward the bindu (killing the \"R.\" reading), the Devanagari ऋ is rescaled to "
                  "measured ink parity with the Latin R, and vendored Marcellus gives the system a "
                  "mixed-case whisper: Ṛtam."),
        "hero": "rdot-recut-sacred.svg",
        "ladder": [("rdot-recut-sacred.svg", "re-cut Ṛ monogram"),
                   ("rtam-mixedcase.svg", "mixed-case Ṛtam — Marcellus"),
                   ("ri-parity-black.svg", "ऋ at measured parity scale")],
        "favicon_light": "../../../dist/outlined/icons/favicon.svg",
        "favicon_dark": "../../../dist/outlined/icons/favicon-dark.svg",
        "dark_indigo": "rtam-mixedcase-dark.svg",
        "dark_charcoal": "rdot-recut-dark.svg",
        "avatar": "rdot-recut-sacred.svg",
        "cobrand": "rdot-recut-sacred.svg",
        "poster_mark": "rdot-recut-dark.svg",
        "receipt_mark": "rdot-recut-sacred.svg",
        "mono": "rdot-recut-mono.svg",
        "specimen": [(n, n.replace(".svg", "")) for n in out],
    })
    print("  wrote battery.html")


if __name__ == "__main__":
    main()
