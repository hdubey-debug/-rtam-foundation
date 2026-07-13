#!/usr/bin/env python3
"""Render the structural prototype: one full-page still per chamber, plus the
descent GIF — street -> hall -> garbhagriha -> touch the bindu -> street,
catching the depth-gauge morph at each threshold.

    python3 make_previews.py
"""
import io
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent


def shot(page, full=False):
    return Image.open(io.BytesIO(page.screenshot(full_page=full))).convert("RGB")


def main():
    with sync_playwright() as pw:
        b = pw.chromium.launch()

        # ---- stills: fresh context each, veils parted for the full-page read ----
        for name in ("street", "hall", "garbhagriha"):
            page = b.new_page(viewport={"width": 1200, "height": 800})
            page.goto(f"file://{HERE / f'{name}.html'}")
            page.wait_for_timeout(900)
            page.evaluate("document.querySelectorAll('.veil').forEach(v=>{"
                          "v.querySelector(':scope > *')&&(v.style.setProperty('--x',1));"
                          "v.classList.add('parted')})")
            page.add_style_tag(content=".veil::after{transition:none!important}")
            page.wait_for_timeout(250)
            shot(page, full=True).save(HERE / f"{name}.png")
            page.close()

        # ---- the descent GIF: one tab, real navigation, morphs included ----
        page = b.new_page(viewport={"width": 1200, "height": 800})
        frames = []

        def burst(n, gap=90):
            for _ in range(n):
                frames.append(shot(page))
                page.wait_for_timeout(gap)

        def drift(sel, hold=2):
            page.evaluate(f"document.querySelector('{sel}').scrollIntoView({{behavior:'instant',block:'center'}})")
            page.wait_for_timeout(120)
            burst(hold)

        page.goto(f"file://{HERE / 'street.html'}")
        page.wait_for_timeout(900)
        burst(5)                                   # the street, at rest
        drift(".cols3")                            # the stones
        drift(".veil", hold=6)                     # the veil parts on arrival
        drift(".door-hall", hold=3)                # the ash doorway visible
        page.click(".door-hall")
        page.wait_for_timeout(120)
        burst(8)                                   # morph: chakra -> anahata
        drift(".cols3")
        drift(".door-garbha", hold=3)              # the black doorway visible
        page.click(".door-garbha")
        page.wait_for_timeout(120)
        burst(8)                                   # morph: anahata -> bindu
        drift(".chamber:nth-of-type(2)")
        drift(".bindu-end", hold=6)                # the breathing point
        page.click(".bindu-end")
        page.wait_for_timeout(120)
        burst(8)                                   # the point contains the street
        b.close()

    small = [f.resize((900, 600), Image.LANCZOS).quantize(colors=96, dither=Image.NONE)
             for f in frames]
    small[0].save(HERE / "descent.gif", save_all=True, append_images=small[1:],
                  duration=140, loop=0)
    print(f"wrote descent.gif ({len(small)} frames) + 3 stills")


if __name__ == "__main__":
    main()
