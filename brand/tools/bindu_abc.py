#!/usr/bin/env python3
"""Side-by-side optical test: bindu at cx=118 (shipped / advance center),
cx=123 (compromise), cx=126.5 (ink bbox center) — plus Cinzel's own
rendering of precomposed Ṛ (U+1E5A) and R + combining dot below (U+0323)
to see the font's native dot placement."""

from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent / "_scratch"

SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 760">
<defs><style>@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500&amp;display=swap');</style></defs>
<rect width="760" height="760" fill="#F7F3E9"/>
<g font-family="Cinzel" font-size="120" font-weight="500" fill="#1A1A1A">
  <text x="80" y="160">RTA</text>
  <text x="80" y="340">RTA</text>
  <text x="80" y="520">RTA</text>
  <text x="80" y="700">R&#x0323;TA</text>
  <text x="500" y="700">&#x1E5A;TA</text>
</g>
<g fill="#C8A15A">
  <circle cx="118" cy="188" r="10"/>
  <circle cx="123" cy="368" r="10"/>
  <circle cx="126.5" cy="548" r="10"/>
</g>
<g font-family="Inter, sans-serif" font-size="20" fill="#888">
  <text x="500" y="120">cx=118 shipped</text>
  <text x="500" y="300">cx=123 compromise</text>
  <text x="500" y="480">cx=126.5 ink-bbox center</text>
  <text x="80" y="745">font: R+U+0323</text>
  <text x="500" y="745">font: U+1E5A</text>
</g>
</svg>"""

OUT.mkdir(parents=True, exist_ok=True)
p = OUT / "bindu-abc.svg"
p.write_text(SVG)
with sync_playwright() as pw:
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={"width": 1140, "height": 1140}, device_scale_factor=2)
    page = ctx.new_page()
    page.goto(p.resolve().as_uri(), wait_until="networkidle")
    page.evaluate("() => document.fonts.ready")
    page.wait_for_timeout(500)
    page.screenshot(path=str(OUT / "bindu-abc.png"))
    b.close()
print("wrote", OUT / "bindu-abc.png")
