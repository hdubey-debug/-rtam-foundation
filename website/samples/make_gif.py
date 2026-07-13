#!/usr/bin/env python3
"""Render derivation-hero.html frame by frame (window.setT) and assemble the
animated GIF the founder can watch, plus key-frame PNGs for the eye-check.

    python3 make_gif.py            # frames 0..14.6 step .2 -> derivation-hero.gif
"""
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SRC = HERE / "derivation-hero.html"
GIF = HERE / "derivation-hero.gif"
KEYS = [1.6, 3.4, 5.7, 8.6, 10.8, 13.6]      # storyboard frames
STEP, END = 0.2, 14.6

def main():
    frames = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        page = b.new_page(viewport={"width": 1200, "height": 800})
        page.goto(f"file://{SRC}?t=0")
        page.wait_for_timeout(700)           # fonts + svg init
        t = 0.0
        while t <= END + 1e-9:
            page.evaluate(f"window.setT({t:.2f})")
            page.wait_for_timeout(30)
            png = page.screenshot()
            frames.append(Image.open(__import__("io").BytesIO(png)).convert("RGB"))
            for k in KEYS:
                if abs(t - k) < STEP / 2:
                    frames[-1].save(HERE / f"frame-{k:04.1f}.png")
            t += STEP
        b.close()
    small = [f.resize((900, 600), Image.LANCZOS).quantize(colors=96, dither=Image.NONE)
             for f in frames]
    small[0].save(GIF, save_all=True, append_images=small[1:], duration=200, loop=0)
    print(f"wrote {GIF.name} ({len(small)} frames) + {len(KEYS)} key frames")

if __name__ == "__main__":
    main()
