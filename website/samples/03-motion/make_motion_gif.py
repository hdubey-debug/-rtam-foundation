#!/usr/bin/env python3
"""Frame-step concept-b-motion.html via window.setState(p, t) and assemble
the review GIF: hold at bindu (breath visible), scroll the ladder, hold at
the full mark. Plus key frames for the eye-check.

    python3 make_motion_gif.py
"""
import io
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SRC = HERE / "concept-b-motion.html"
GIF = HERE / "concept-b-motion.gif"
KEYS = {0.0: "m-bindu", 0.45: "m-bloom", 0.72: "m-rim", 1.0: "m-full"}

def main():
    frames = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        page = b.new_page(viewport={"width": 1200, "height": 800})
        page.goto(f"file://{SRC}?freeze")
        page.wait_for_timeout(700)

        def shot(p, t):
            page.evaluate(f"window.setState({p:.4f}, {t:.3f})")
            page.wait_for_timeout(25)
            frames.append(Image.open(io.BytesIO(page.screenshot())).convert("RGB"))
            for kp, name in KEYS.items():
                if abs(p - kp) < 1e-6 and abs(t % 5.5) < 0.2:
                    frames[-1].save(HERE / f"{name}.png")

        t = 0.0
        for _ in range(22):                 # hold: the dipa breath at the bindu
            shot(0.0, t); t += 0.25
        for i in range(48):                 # the scroll: ladder unfolds
            shot(i / 47, t); t += 0.25
        for _ in range(22):                 # hold: the full mark breathing
            shot(1.0, t); t += 0.25
        b.close()
    small = [f.resize((900, 600), Image.LANCZOS).quantize(colors=96, dither=Image.NONE)
             for f in frames]
    small[0].save(GIF, save_all=True, append_images=small[1:], duration=110, loop=0)
    print(f"wrote {GIF.name} ({len(small)} frames)")

if __name__ == "__main__":
    main()
