#!/usr/bin/env python3
"""US-16: generate platform raster deliverables from the OUTLINED masters (which
render font-lessly, so cairosvg produces correct glyphs without the web fonts).

Outputs into brand/exports/platform/:
  favicon-{16,32,48}.png + favicon.ico   — bare Ṛ mark, transparent (favicon master)
  apple-touch-icon-180.png               — circle Ṛ on ivory, 12% safe padding
  icon-{192,512}.png + maskable-512.png  — PWA / Android (maskable: 20% safe zone)
  og-image-1200x630.png                  — bilingual lockup centred on ivory
  site.webmanifest                       — references the icon set

Run build.sh --write first so brand/dist/outlined/ exists.
"""
import json
from pathlib import Path

import cairosvg
from PIL import Image

BRAND = Path(__file__).resolve().parent.parent
DIST = BRAND / "dist" / "outlined"
OUT = BRAND / "exports" / "platform"
IVORY = "#F7F3E9"


def svg_png(src: Path, size: int, bg=None, scale=1.0) -> Image.Image:
    """Rasterize an SVG to a square RGBA PIL image; `scale`<1 insets the mark
    (centred) leaving transparent/bg padding — for maskable safe zones."""
    inner = max(1, round(size * scale))
    raw = cairosvg.svg2png(url=str(src), output_width=inner, output_height=inner)
    mark = Image.open(__import__("io").BytesIO(raw)).convert("RGBA")
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0) if bg is None else bg)
    off = (size - inner) // 2
    canvas.alpha_composite(mark, (off, off))
    return canvas


def hex_rgba(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


def write_ico(out: Path, png_paths) -> None:
    """Assemble a multi-resolution .ico embedding each PNG frame verbatim (PNG-in-ICO,
    universally supported for sizes <=256). Avoids PIL downsampling one source."""
    import struct
    frames = [(Path(p).stat().st_size, Path(p).read_bytes(), Image.open(p).size) for p in png_paths]
    n = len(frames)
    header = struct.pack("<HHH", 0, 1, n)
    offset = 6 + 16 * n
    entries, data = b"", b""
    for size_bytes, raw, (w, h) in frames:
        entries += struct.pack("<BBBBHHII", w & 0xFF, h & 0xFF, 0, 0, 1, 32, len(raw), offset)
        data += raw
        offset += len(raw)
    out.write_bytes(header + entries + data)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    favicon = DIST / "icons" / "favicon.svg"
    circle = DIST / "icons" / "rtam-rdot-icon-circle-gold.svg"
    lockup = DIST / "lockups" / "rtam-bilingual-foundation.svg"
    ivory = hex_rgba(IVORY)

    # --- favicons (bare mark, transparent) ---
    for sz in (16, 32, 48):
        svg_png(favicon, sz).save(OUT / f"favicon-{sz}.png")
    # multi-resolution .ico — embed each NATIVELY-rendered frame, NOT PIL's
    # downsample-from-the-largest (a Lanczos 48→16 smears the 1px bindu). Build
    # the container by hand so each entry is the crisp SVG-rendered PNG.
    write_ico(OUT / "favicon.ico", [OUT / f"favicon-{s}.png" for s in (16, 32, 48)])

    # --- app icons (circle Ṛ on ivory) ---
    svg_png(circle, 180, bg=ivory, scale=0.88).save(OUT / "apple-touch-icon-180.png")
    svg_png(circle, 192, bg=ivory, scale=0.88).save(OUT / "icon-192.png")
    svg_png(circle, 512, bg=ivory, scale=0.88).save(OUT / "icon-512.png")
    # maskable: mark within the 80% safe zone, full-bleed ivory
    svg_png(circle, 512, bg=ivory, scale=0.66).save(OUT / "maskable-512.png")

    # --- OG image 1200x630: bilingual lockup centred on ivory ---
    og = Image.new("RGBA", (1200, 630), ivory)
    lk_w = 860  # lockup 1080x380 -> scaled
    lk_h = round(lk_w * 380 / 1080)
    raw = cairosvg.svg2png(url=str(lockup), output_width=lk_w, output_height=lk_h)
    lk = Image.open(__import__("io").BytesIO(raw)).convert("RGBA")
    og.alpha_composite(lk, ((1200 - lk_w) // 2, (630 - lk_h) // 2))
    og.convert("RGB").save(OUT / "og-image-1200x630.png")

    # --- web manifest ---
    manifest = {
        "name": "RTAM Foundation",
        "short_name": "RTAM",
        "icons": [
            {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
        "theme_color": "#1A1A1A",
        "background_color": IVORY,
        "display": "standalone",
    }
    (OUT / "site.webmanifest").write_text(json.dumps(manifest, indent=2) + "\n")

    print("wrote platform deliverables to brand/exports/platform/:")
    for p in sorted(OUT.iterdir()):
        print(f"  {p.name}")


if __name__ == "__main__":
    main()
