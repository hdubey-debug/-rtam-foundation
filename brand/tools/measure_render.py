#!/usr/bin/env python3
"""Faithful render + empirical geometry measurement for every RTAM brand SVG.

For each SVG:
  1. Load it as a top-level document in Chromium (so @import web fonts work),
     await document.fonts.ready, then:
       - extract viewBox, every <text> bbox + per-char glyph extents,
         every <circle>/<rect>/<path> bbox, font load status  -> JSON
       - screenshot at 2x on ivory AND charcoal backgrounds   -> PNGs
  2. Render the same SVG with cairosvg (the repo's legacy tool path) so we can
     see what a font-less consumer gets                        -> PNG

Outputs land in brand/tools/_scratch/{renders,fallback,geometry.json}
(gitignored — scratch renders are never committed).
"""

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parent.parent          # brand/
OUT = Path(__file__).resolve().parent / "_scratch"
RENDERS = OUT / "renders"
FALLBACK = OUT / "fallback"
TMP = OUT / "tmp-svg"

BGS = {"ivory": "#F7F3E9", "charcoal": "#1A1A1A"}

MEASURE_JS = """
() => {
  const svg = document.documentElement;
  const vb = svg.viewBox && svg.viewBox.baseVal
    ? {x: svg.viewBox.baseVal.x, y: svg.viewBox.baseVal.y,
       w: svg.viewBox.baseVal.width, h: svg.viewBox.baseVal.height}
    : null;
  const texts = [...document.querySelectorAll('text')].map(t => {
    let bb = null, chars = [], tl = null;
    try { const b = t.getBBox(); bb = {x: b.x, y: b.y, w: b.width, h: b.height}; } catch (e) {}
    try { tl = t.getComputedTextLength(); } catch (e) {}
    try {
      const n = t.getNumberOfChars();
      for (let i = 0; i < Math.min(n, 24); i++) {
        const ex = t.getExtentOfChar(i);
        chars.push({ch: (t.textContent || '')[i], x: ex.x, y: ex.y, w: ex.width, h: ex.height});
      }
    } catch (e) {}
    return {
      content: (t.textContent || '').trim(),
      attrs: {x: t.getAttribute('x'), y: t.getAttribute('y'),
              fontSize: t.getAttribute('font-size'),
              fontFamily: t.getAttribute('font-family'),
              letterSpacing: t.getAttribute('letter-spacing'),
              anchor: t.getAttribute('text-anchor'),
              transform: t.getAttribute('transform')},
      inheritedFontFamily: getComputedStyle(t).fontFamily,
      bbox: bb, textLength: tl, chars
    };
  });
  const circles = [...document.querySelectorAll('circle')].map(c => ({
    cx: +c.getAttribute('cx'), cy: +c.getAttribute('cy'),
    r: +c.getAttribute('r'), fill: c.getAttribute('fill'),
    transform: c.getAttribute('transform')
  }));
  let unionBox = null;
  try {
    for (const el of svg.querySelectorAll('text, circle, rect, path, line, polygon, ellipse, g')) {
      if (el.tagName === 'g') continue;
      const b = el.getBBox();
      if (!b || (b.width === 0 && b.height === 0)) continue;
      if (!unionBox) unionBox = {x0: b.x, y0: b.y, x1: b.x + b.width, y1: b.y + b.height};
      else {
        unionBox.x0 = Math.min(unionBox.x0, b.x); unionBox.y0 = Math.min(unionBox.y0, b.y);
        unionBox.x1 = Math.max(unionBox.x1, b.x + b.width); unionBox.y1 = Math.max(unionBox.y1, b.y + b.height);
      }
    }
  } catch (e) {}
  const loaded = [];
  try { document.fonts.forEach(f => loaded.push({family: f.family, status: f.status})); } catch (e) {}
  return {viewBox: vb, texts, circles, unionBox, fontsLoaded: loaded};
}
"""


def collect_svgs():
    dirs = ["logos", "icons", "lockups", "seal"]
    files = []
    for d in dirs:
        files.extend(sorted((REPO / d).glob("*.svg")))
    return files


def with_background(svg_src: str, color: str) -> str:
    # Inject a full-bleed background rect right after the opening <svg ...> tag.
    idx = svg_src.index(">", svg_src.index("<svg")) + 1
    rect = f'<rect x="-10000" y="-10000" width="30000" height="30000" fill="{color}"/>'
    return svg_src[:idx] + rect + svg_src[idx:]


def main():
    for d in (RENDERS, FALLBACK, TMP):
        d.mkdir(parents=True, exist_ok=True)
    svgs = collect_svgs()
    geometry = {}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for svg in svgs:
            rel = svg.relative_to(REPO)
            stem = f"{rel.parent.name}__{svg.stem}"
            src = svg.read_text()

            # --- measurement pass (original file, fonts awaited) ---
            ctx = browser.new_context(viewport={"width": 1400, "height": 900},
                                      device_scale_factor=2)
            page = ctx.new_page()
            page.goto(svg.resolve().as_uri(), wait_until="networkidle")
            try:
                page.evaluate("() => document.fonts.ready")
            except Exception:
                pass
            page.wait_for_timeout(400)
            try:
                geometry[str(rel)] = page.evaluate(MEASURE_JS)
            except Exception as e:
                geometry[str(rel)] = {"error": str(e)}
            ctx.close()

            # --- faithful screenshots on both grounds ---
            for bgname, bghex in BGS.items():
                tmp = TMP / f"{stem}__{bgname}.svg"
                tmp.write_text(with_background(src, bghex))
                ctx = browser.new_context(viewport={"width": 1400, "height": 900},
                                          device_scale_factor=2)
                page = ctx.new_page()
                page.goto(tmp.resolve().as_uri(), wait_until="networkidle")
                try:
                    page.evaluate("() => document.fonts.ready")
                except Exception:
                    pass
                page.wait_for_timeout(400)
                page.screenshot(path=str(RENDERS / f"{stem}__{bgname}.png"), full_page=False)
                ctx.close()

            # --- cairosvg fallback render (the repo's legacy tool path) ---
            try:
                import cairosvg
                cairosvg.svg2png(url=str(svg),
                                 write_to=str(FALLBACK / f"{stem}__cairosvg.png"),
                                 output_width=1024,
                                 background_color="#F7F3E9")
            except Exception as e:
                (FALLBACK / f"{stem}__cairosvg.ERROR.txt").write_text(str(e))

            print(f"done: {rel}", flush=True)
        browser.close()

    (OUT / "geometry.json").write_text(json.dumps(geometry, indent=2))
    print(f"\nwrote {OUT/'geometry.json'} with {len(geometry)} entries")


if __name__ == "__main__":
    sys.exit(main())
