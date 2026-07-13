#!/usr/bin/env python3
"""W2·S7 — the proof matrix and the performance measurements.

    python3 website/tools/proof_matrix.py

Produces, under website/samples/06-w2-proofs/:
  proofs/{page}-{engine}-{width}.jpg   full-page renders, every page ×
                                       {chromium, firefox[, webkit]} × {1440, 390}
  MEASUREMENTS.md                      cold-load transferred bytes per page @390,
                                       LCP under CDP 4G + 4× CPU throttle,
                                       the engine matrix (WebKit honestly reported)

Numbers are measured against a local http.server (no compression), so byte
counts are an UPPER bound on what a gzip/brotli host will actually transfer.
"""
import functools
import io
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

TOOLS = Path(__file__).resolve().parent
WEB = TOOLS.parent
DIST = WEB / "dist"
OUT = WEB / "samples" / "06-w2-proofs"
PROOFS = OUT / "proofs"

WIDTHS = (1440, 390)
BUDGET = 600_000          # landing cold-load bytes @390 — the plan's hard budget
LCP_BUDGET_MS = 2500

LCP_PROBE = """
window.__lcp = 0;
new PerformanceObserver(l => {
  for (const e of l.getEntries()) window.__lcp = e.startTime;
}).observe({type: 'largest-contentful-paint', buffered: true});
"""


def serve():
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *a, **k):
            pass
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(DIST)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def page_name(rel):
    n = rel.replace("/index.html", "").replace(".html", "").replace("/", "-")
    return n or "index"


def main():
    PROOFS.mkdir(parents=True, exist_ok=True)
    srv, port = serve()
    base = f"http://127.0.0.1:{port}"
    pages = sorted(p.relative_to(DIST).as_posix() for p in DIST.rglob("*.html"))

    engines, engine_notes = [], []
    with sync_playwright() as pw:
        for eng in ("chromium", "firefox", "webkit"):
            try:
                b = getattr(pw, eng).launch()
                engines.append(eng)
                engine_notes.append(f"- **{eng}** {b.version} — proofs rendered")
                b.close()
            except Exception as e:
                lines_ = [l.strip(" ║╔╚═╗╝") for l in str(e).splitlines()]
                first = next((l for l in lines_ if "missing" in l.lower()),
                             next((l for l in lines_ if l), "launch failed"))
                engine_notes.append(
                    f"- **{eng}** — CANNOT RUN on this host: {first} "
                    f"(HPC cluster, no sudo for system libraries). Mitigations: "
                    f"baseline-features-only policy + the founder's real-device "
                    f"Safari/iPhone checklist (FOUNDER-CHECKLIST.md).")

        # ---- proofs: every page × engine × width, full-page ----
        shot_count = 0
        for eng in engines:
            b = getattr(pw, eng).launch()
            for width in WIDTHS:
                for rel in pages:
                    page = b.new_page(viewport={"width": width, "height": 900})
                    page.goto(f"{base}/{rel}", wait_until="networkidle")
                    page.wait_for_timeout(500)
                    png = page.screenshot(full_page=True)
                    im = Image.open(io.BytesIO(png)).convert("RGB")
                    im.save(PROOFS / f"{page_name(rel)}-{eng}-{width}.jpg",
                            quality=80, optimize=True)
                    shot_count += 1
                    page.close()
            b.close()

        # ---- cold-load transferred bytes per page @390 (chromium) ----
        weights = {}
        b = pw.chromium.launch()
        for rel in pages:
            ctx = b.new_context(viewport={"width": 390, "height": 800})
            page = ctx.new_page()
            tally = {"n": 0, "bytes": 0}

            def on_response(resp, tally=tally):
                try:
                    body = resp.body()
                except Exception:
                    body = b""
                tally["n"] += 1
                tally["bytes"] += len(body)
            page.on("response", on_response)
            page.goto(f"{base}/{rel}", wait_until="networkidle")
            page.wait_for_timeout(400)
            weights[rel] = (tally["n"], tally["bytes"])
            ctx.close()

        # ---- LCP under throttling (chromium CDP): simulated 4G + 4× CPU ----
        lcps = {}
        for rel in pages:
            ctx = b.new_context(viewport={"width": 390, "height": 800})
            page = ctx.new_page()
            page.add_init_script(LCP_PROBE)
            cdp = ctx.new_cdp_session(page)
            cdp.send("Network.enable")
            cdp.send("Network.emulateNetworkConditions", {
                "offline": False, "latency": 150,
                "downloadThroughput": int(4 * 1024 * 1024 / 8),   # 4 Mbps
                "uploadThroughput": int(1.5 * 1024 * 1024 / 8),
            })
            cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
            page.goto(f"{base}/{rel}", wait_until="load")
            page.wait_for_timeout(1200)
            lcps[rel] = page.evaluate("window.__lcp")
            ctx.close()
        b.close()
    srv.shutdown()

    # ---- the report ----
    landing_bytes = weights["index.html"][1]
    lines = [
        "# W2 proof matrix & measurements",
        "",
        "Rendered from `website/dist/` over a local `http.server` (no compression —",
        "byte counts are an upper bound on a gzip/brotli host).",
        "",
        "## Engine matrix",
        "",
        *engine_notes,
        "",
        f"Proof renders: `proofs/` — {shot_count} shots "
        f"(every page × {{{', '.join(engines)}}} × {{1440, 390}}).",
        "",
        "## Cold-load transferred bytes @390px (chromium, fresh context)",
        "",
        "| page | requests | bytes | budget |",
        "|---|---|---|---|",
    ]
    for rel, (n, byt) in sorted(weights.items()):
        mark = ""
        if rel == "index.html":
            ok = "PASS" if byt <= BUDGET else "**FAIL**"
            mark = f"≤ {BUDGET:,} → {ok}"
        lines.append(f"| /{rel} | {n} | {byt:,} | {mark} |")
    lines += [
        "",
        "## LCP under CDP throttling (4 Mbps / 150 ms RTT / 4× CPU, @390px)",
        "",
        "| page | LCP (ms) | budget |",
        "|---|---|---|",
    ]
    for rel, ms in sorted(lcps.items()):
        mark = ""
        if rel == "index.html":
            ok = "PASS" if ms and ms <= LCP_BUDGET_MS else "**FAIL**"
            mark = f"< {LCP_BUDGET_MS:,} ms → {ok}"
        lines.append(f"| /{rel} | {ms:.0f} | {mark} |")
    lines += [
        "",
        "The landing's LCP element is the hero `<img>` — painted immediately, never veiled",
        "(verify_site gate D asserts it).",
        "",
    ]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "MEASUREMENTS.md").write_text("\n".join(lines))
    print(f"engines: {engines}")
    print(f"landing @390: {landing_bytes:,} B (budget {BUDGET:,}) · "
          f"LCP {lcps['index.html']:.0f} ms (budget {LCP_BUDGET_MS})")
    print(f"wrote {shot_count} proofs + MEASUREMENTS.md → {OUT}")


if __name__ == "__main__":
    main()
