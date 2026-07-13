#!/usr/bin/env python3
"""Re-cut the descent GIF on the REAL site (website/dist/): the full axial path —
the land → मंदिर (the walk, clockwise) → गर्भगृह (the approach contracts) →
the point → the land again. Gauge morphs at each threshold.

    python3 make_previews.py
"""
import functools
import io
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
DIST = HERE.parent.parent / "dist"


def main():
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *a, **k):
            pass
    srv = ThreadingHTTPServer(("127.0.0.1", 0),
                              functools.partial(Quiet, directory=str(DIST)))
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    frames = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        page = b.new_page(viewport={"width": 1200, "height": 800})

        def shot():
            frames.append(Image.open(io.BytesIO(page.screenshot())).convert("RGB"))

        def burst(n, gap=90):
            for _ in range(n):
                shot()
                page.wait_for_timeout(gap)

        def drift(sel, hold=2):
            page.eval_on_selector(sel,
                "el => el.scrollIntoView({behavior:'instant', block:'center'})")
            page.wait_for_timeout(150)
            burst(hold)

        # the land
        page.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        page.wait_for_timeout(700)
        burst(4)
        drift(".hero-head", hold=3)                    # the foil heading + flame
        drift(".stone.center", hold=2)                 # निर्माणाधीन honesty
        drift(".door-hall", hold=2)
        page.click(".door-hall")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(150)
        burst(6)                                       # morph: chakra → anāhata
        # the walk
        drift(".walkband", hold=2)
        for t in (0.25, 0.5, 0.75, 1.0):               # pradakshina, clockwise
            page.evaluate(f"setWalk({t})")
            page.wait_for_timeout(150)
            burst(2)
        drift(".door-garbha", hold=2)
        page.click(".door-garbha")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(150)
        burst(6)                                       # morph: anāhata → bindu
        # the approach: the contraction, stepped
        page.eval_on_selector("#approach",
            "el => el.scrollIntoView({behavior:'instant'})")
        page.wait_for_timeout(200)
        for t in (0.0, 0.18, 0.36, 0.5, 0.64, 0.8, 0.95):
            page.evaluate(f"setApproach({t})")
            page.wait_for_timeout(120)
            burst(2)
        drift(".murti", hold=3)                        # the construction drawing
        drift(".bindu-end", hold=4)                    # the breathing point
        page.click(".bindu-end")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(150)
        burst(6)                                       # the point contains the land
        b.close()
    srv.shutdown()

    small = [f.resize((900, 600), Image.LANCZOS).quantize(colors=96, dither=Image.NONE)
             for f in frames]
    small[0].save(HERE / "descent.gif", save_all=True, append_images=small[1:],
                  duration=150, loop=0)
    print(f"wrote descent.gif ({len(small)} frames)")


if __name__ == "__main__":
    main()
