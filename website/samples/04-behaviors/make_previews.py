#!/usr/bin/env python3
"""Render the six behavior samples: stills for layout eye-checks, GIFs for the
motions. Each page exposes a freeze API (setTime/setFocus/setFoil/setWalk/
setSound/setLife) behind ?freeze.

    python3 make_previews.py
"""
import io
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
NO_TRANSITIONS = "*{transition:none!important}"


def gif(frames, name, ms):
    small = [f.resize((900, 600), Image.LANCZOS).quantize(colors=96, dither=Image.NONE)
             for f in frames]
    small[0].save(HERE / name, save_all=True, append_images=small[1:], duration=ms, loop=0)
    print(f"wrote {name} ({len(small)} frames)")


def shot(page, full=False):
    return Image.open(io.BytesIO(page.screenshot(full_page=full))).convert("RGB")


def main():
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        page = b.new_page(viewport={"width": 1200, "height": 800})

        def load(src, kill_transitions=False):
            page.goto(f"file://{HERE / src}")
            page.wait_for_timeout(750)
            if kill_transitions:
                page.add_style_tag(content=NO_TRANSITIONS)

        # ---- 1 · temple time: three registers + the day-cycle gif ----
        for at, name in [("12:30", "tt-day"), ("19:05", "tt-sandhya"), ("22:30", "tt-night")]:
            load(f"temple-time.html?at={at}&freeze")
            page.wait_for_timeout(1600)                # let the register transition settle
            shot(page, full=True).save(HERE / f"{name}.png")
        load("temple-time.html?freeze", kill_transitions=True)
        frames = []
        for i in range(39):                            # 04:30 -> 23:30, one frame per half hour
            m = 4 * 60 + 30 + i * 30
            page.evaluate(f'window.setTime("{m//60:02d}:{m%60:02d}")')
            page.wait_for_timeout(25)
            frames.append(shot(page))
        gif(frames, "temple-time.gif", 150)

        # ---- 2 · year-wheel: full page + focus walk ----
        page.set_viewport_size({"width": 1300, "height": 900})
        load("year-wheel.html?freeze&today=194", kill_transitions=True)   # 13 Jul
        shot(page, full=True).save(HERE / "year-wheel.png")
        frames = []
        for i in range(11):
            page.evaluate(f"window.setFocus({i})")
            page.wait_for_timeout(25)
            frames.extend([shot(page)] * 4)
        gif(frames, "year-wheel.gif", 150)
        page.set_viewport_size({"width": 1200, "height": 800})

        # ---- 3 · foil gold: still + the scroll-catch gif ----
        load("foil-gold.html?freeze")
        shot(page, full=True).save(HERE / "foil-gold.png")
        frames = []
        for i in range(48):
            page.evaluate(f"window.setFoil({i/47:.4f})")
            page.wait_for_timeout(25)
            frames.append(shot(page))
        gif(frames, "foil-gold.gif", 110)

        # ---- 4 · pradakshina: start still + the walk gif ----
        load("pradakshina.html?freeze")
        shot(page, full=True).save(HERE / "pradakshina.png")
        frames = []
        for k in range(4):                             # hold each stop, then sweep to the next
            for _ in range(5):
                page.evaluate(f"window.setWalk({k/4:.4f})")
                page.wait_for_timeout(25)
                frames.append(shot(page))
            for j in range(1, 7):
                page.evaluate(f"window.setWalk({(k + j/6)/4:.4f})")
                page.wait_for_timeout(25)
                frames.append(shot(page))
        for _ in range(8):
            page.evaluate("window.setWalk(1)")
            page.wait_for_timeout(25)
            frames.append(shot(page))
        gif(frames, "pradakshina.gif", 130)

        # ---- 5 · the unstruck sound: two visual states ----
        load("anahata-sound.html?freeze")
        page.evaluate("window.setSound(0)")
        shot(page, full=True).save(HERE / "sound-off.png")
        page.evaluate("window.setSound(1)")
        page.wait_for_timeout(1300)
        shot(page, full=True).save(HERE / "sound-on.png")

        # ---- 6 · small life: lit page + one threshold sweep ----
        load("small-life.html?freeze")
        page.evaluate("document.querySelectorAll('.thresh').forEach(h=>{"
                      "h.style.transition='none';h.classList.add('lit')})")
        page.wait_for_timeout(120)
        shot(page, full=True).save(HERE / "small-life.png")
        page.evaluate("document.querySelector('.piece').scrollIntoView()")
        frames = []
        for i in range(16):
            page.evaluate(f"window.setLife({i/15:.4f})")
            page.wait_for_timeout(25)
            frames.append(shot(page))
        gif(frames, "small-life-threshold.gif", 110)

        b.close()


if __name__ == "__main__":
    main()
