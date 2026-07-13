#!/usr/bin/env python3
"""ṚTAM website gates — run before every commit; there is no CI, this is the gate.

    python3 website/tools/verify_site.py

Gates (all must pass):
  A  color law     — color literals only on token-definition lines; every hex in
                     dist (CSS, inline styles, SVGs) ∈ palette canon ∪ effect registry
  B  face law      — every font-family resolves to Tiro / Cinzel / Inter (+ generics)
  C  contrast law  — computed WCAG ratios for every text-token/ground pair
  D  live probes   — each page served over http: layer ground painted, gauge stage
                     correct, zero console errors, zero failed or external requests
  E  link law      — every href/src/srcset/url() resolves inside dist; external
                     http(s) only on <a>; anchors resolve
  F  honesty       — visible [placeholders] counted; a production dist must have none
  G  font gate     — woff2 subsets only, no TTF/OTF, total under the byte cap
"""
import functools
import io
import json
import re
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image

TOOLS = Path(__file__).resolve().parent
WEB = TOOLS.parent
ROOT = WEB.parent
DIST = WEB / "dist"
CANON_CSS = ROOT / "brand" / "palette" / "colors.css"

FACES = {"Tiro", "Cinzel", "Inter"}
GENERICS = {"serif", "sans-serif", "monospace", "system-ui"}
FONT_TOTAL_CAP = 200_000  # bytes, all woff2 together
EXPECTED_FONTS = {"tiro-400.woff2", "cinzel-500.woff2", "inter-400.woff2", "inter-600.woff2"}

HEX_RE = re.compile(r"#[0-9A-Fa-f]{3,8}\b")
RGB_RE = re.compile(r"\brgba?\([^)]*\)")
DEF_LINE_RE = re.compile(r"^\s*--[\w-]+\s*:")

failures = []
notes = []


def fail(gate, msg):
    failures.append(f"[{gate}] {msg}")


def norm_hex(h):
    h = h.upper()
    if len(h) == 4:  # #abc → #AABBCC
        h = "#" + "".join(c * 2 for c in h[1:])
    return h


# ---------- gate A · color law ----------

def color_literals(text):
    return [norm_hex(m) for m in HEX_RE.findall(text)] + RGB_RE.findall(text)


def gate_a():
    canon = {norm_hex(m) for m in HEX_RE.findall(CANON_CSS.read_text())}
    css = (DIST / "assets" / "system.css").read_text()
    registry = set()
    for line in css.splitlines():
        if DEF_LINE_RE.match(line):
            registry.update(color_literals(line))
    allowed = canon | registry

    # canon section of system.css must not drift from the palette file
    sect = re.search(r"palette canon.*?effect registry", css, re.S)
    if sect:
        for h in {norm_hex(m) for m in HEX_RE.findall(sect.group(0))}:
            if h not in canon:
                fail("A", f"system.css canon section carries {h}, absent from palette canon")
    else:
        fail("A", "system.css lost its canon/effect-registry section markers")

    for line_no, line in enumerate(css.splitlines(), 1):
        if not DEF_LINE_RE.match(line) and color_literals(line):
            fail("A", f"system.css:{line_no} color literal outside a token line: {line.strip()!r}")

    for page in sorted(DIST.rglob("*.html")):
        html = page.read_text()
        for m in re.finditer(r'style="([^"]*)"', html):
            if color_literals(m.group(1)):
                fail("A", f"{page.relative_to(DIST)}: inline style carries a color literal: {m.group(1)!r}")
        for m in re.finditer(r"<style\b[^>]*>(.*?)</style>", html, re.S):
            for line in m.group(1).splitlines():
                if not DEF_LINE_RE.match(line) and color_literals(line):
                    fail("A", f"{page.relative_to(DIST)}: <style> color literal outside a token line: {line.strip()!r}")

    for svg in sorted(DIST.rglob("*.svg")):
        bad = {h for h in {norm_hex(m) for m in HEX_RE.findall(svg.read_text())}
               if h not in allowed}
        if bad:
            fail("A", f"{svg.relative_to(DIST)}: non-canon colors {sorted(bad)}")

    notes.append(f"A: canon {len(canon)} colors, registry {len(registry)} tokens")
    return canon, registry


# ---------- gate B · face law ----------

def gate_b():
    decls = []
    css = (DIST / "assets" / "system.css").read_text()
    decls += re.findall(r"font-family\s*:\s*([^;}]+)", css)
    for page in sorted(DIST.rglob("*.html")):
        html = page.read_text()
        decls += re.findall(r"font-family\s*:\s*([^;}\"]+)", html)
    for d in decls:
        first = d.split(",")[0].strip().strip("'\"")
        if first not in FACES and first not in GENERICS and not first.startswith("var("):
            fail("B", f"font-family {d.strip()!r} — first face {first!r} is not Tiro/Cinzel/Inter")
    notes.append(f"B: {len(decls)} font-family declarations checked")


# ---------- gate C · contrast law ----------

def lum(hex6):
    def f(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(int(hex6[i:i + 2], 16) / 255) for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def parse_tokens(block):
    return dict(re.findall(r"--([\w-]+)\s*:\s*(#[0-9A-Fa-f]{6})", block))


def gate_c():
    css = (DIST / "assets" / "system.css").read_text()
    layers = {}
    for m in re.finditer(r'((?:body\[data-layer="\d"\][^{]*)+)\{([^}]*)\}', css):
        toks = parse_tokens(m.group(2))
        if "ground" in toks:
            for lay in re.findall(r'data-layer="(\d)"', m.group(1)):
                layers[lay] = toks
    root = parse_tokens(re.search(r":root\s*\{([^}]*)\}", css).group(1))

    # (token, on, min_ratio, why) — essential text everywhere it can stand
    for lay, t in sorted(layers.items()):
        pairs = [
            ("ink", "ground", 4.5), ("ink", "panel", 4.5),
            ("mut", "ground", 4.5), ("mut", "panel", 4.5),
            ("accent", "ground", 4.5), ("accent", "panel", 4.5),
            ("flame-ink", "flame-bg", 4.5),
        ]
        if lay == "3":
            pairs.append(("gold", "ground", 4.5))  # gold IS the accent in mahakala
        for fg, bg, need in pairs:
            r = ratio(t[fg], t[bg])
            if r < need:
                fail("C", f"layer {lay}: --{fg} {t[fg]} on --{bg} {t[bg]} = {r:.2f} < {need}")
    # the dark door on light pages, and the sanctum's own furniture
    for fg, bg, need, why in [
        ("gold-dipa", "mahakala", 3.0, "door-garbha दन (26px display)"),
        ("bhasma-deep", "mahakala", 4.5, "door-garbha caption"),
        ("ink-charcoal", "bhasma", 4.5, "door-hall text"),
    ]:
        r = ratio(root[fg], root[bg])
        if r < need:
            fail("C", f"{why}: --{fg} on --{bg} = {r:.2f} < {need}")
    notes.append(f"C: {len(layers)} layers × 7 pairs + 3 door pairs computed")


# ---------- gate D · live probes ----------

def gate_d():
    from playwright.sync_api import sync_playwright

    css = (DIST / "assets" / "system.css").read_text()
    grounds = {}
    for m in re.finditer(r'((?:body\[data-layer="\d"\][^{]*)+)\{([^}]*)\}', css):
        g = re.search(r"--ground\s*:\s*(#[0-9A-Fa-f]{6})", m.group(2))
        if g:
            for lay in re.findall(r'data-layer="(\d)"', m.group(1)):
                grounds[lay] = g.group(1)

    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, *args, **kwargs):
            pass

    handler = functools.partial(QuietHandler, directory=str(DIST))
    srv = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    def rgb(hex6):
        return f"rgb({int(hex6[1:3], 16)}, {int(hex6[3:5], 16)}, {int(hex6[5:7], 16)})"

    pages = sorted(p.relative_to(DIST).as_posix() for p in DIST.rglob("*.html"))
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for rel in pages:
                ctx = browser.new_context(viewport={"width": 1200, "height": 800})
                page = ctx.new_page()
                errors, ext = [], []
                page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
                page.on("pageerror", lambda e: errors.append(str(e)))
                page.on("response", lambda r: errors.append(f"{r.status} {r.url}") if r.status >= 400 else None)
                page.on("request", lambda r: ext.append(r.url) if not r.url.startswith(f"http://127.0.0.1:{port}") else None)
                page.goto(f"http://127.0.0.1:{port}/{rel}", wait_until="networkidle")

                lay = page.get_attribute("body", "data-layer")
                want = grounds[lay]
                got = page.evaluate("getComputedStyle(document.body).backgroundColor")
                if got != rgb(want):
                    fail("D", f"{rel}: body ground {got} ≠ layer {lay} {want}")
                shot = Image.open(io.BytesIO(page.screenshot())).convert("RGB")
                px = shot.getpixel((1100, 520))
                want_rgb = tuple(int(want[i:i + 2], 16) for i in (1, 3, 5))
                if px != want_rgb:
                    fail("D", f"{rel}: rendered pixel at (1100,520) {px} ≠ ground {want_rgb}")
                stage = 3 if lay == "3" else (1 if lay in ("1", "2") else 0)
                vis = page.evaluate(
                    "[...document.querySelectorAll('#gm img')]"
                    ".find(i => getComputedStyle(i).opacity === '1')?.dataset.d")
                if vis != str(stage):
                    fail("D", f"{rel}: gauge shows stage {vis}, expected {stage} for layer {lay}")
                sut = page.evaluate(
                    "(() => { const s = document.querySelector('.sutra:not(.foil)');"
                    " if (!s) return null;"
                    " return [getComputedStyle(s).color, s.classList.contains('gilt')]; })()")
                if sut:
                    col, gilt = sut
                    toks = {}
                    m = re.search(r'body\[data-layer="%s"\][^{]*\{([^}]*)\}' % lay, css) \
                        or re.search(r'\[data-layer="%s"\][^{]*\{([^}]*)\}' % lay, css)
                    toks = parse_tokens(m.group(1)) if m else {}
                    want_col = rgb(toks["gold"] if gilt else toks["ink"])
                    if col != want_col:
                        fail("D", f"{rel}: sutra color {col} ≠ {want_col}")
                if errors:
                    fail("D", f"{rel}: console/request errors {errors[:4]}")
                if ext:
                    fail("D", f"{rel}: EXTERNAL requests fired {ext[:4]}")
                ctx.close()
            browser.close()
    finally:
        srv.shutdown()
    notes.append(f"D: {len(pages)} pages probed over http (chromium)")


# ---------- gate E · link law ----------

def gate_e():
    dead_hash = 0
    pages = sorted(DIST.rglob("*.html"))
    ids = {p: set(re.findall(r'id="([^"]+)"', p.read_text())) for p in pages}

    def resolve(base, target):
        t = (base.parent / target).resolve()
        if t.is_dir():
            t = t / "index.html"
        return t

    for page in pages:
        html = page.read_text()
        refs = re.findall(r'(?:href|src)="([^"]+)"', html)
        for ss in re.findall(r'srcset="([^"]+)"', html):
            refs += [part.strip().split()[0] for part in ss.split(",")]
        for ref in refs:
            if ref.startswith("mailto:"):
                continue
            if ref.startswith(("http://", "https://")):
                if not re.search(r'<a[^>]+href="%s"' % re.escape(ref), html):
                    fail("E", f"{page.relative_to(DIST)}: external ASSET {ref} — zero third-party law")
                continue
            if ref == "#":
                dead_hash += 1
                continue
            path_part, _, frag = ref.partition("#")
            target = page if not path_part else resolve(page, path_part)
            if not target.exists():
                fail("E", f"{page.relative_to(DIST)}: broken link {ref}")
                continue
            if frag and target.suffix == ".html" and frag not in ids.get(target, set()):
                fail("E", f"{page.relative_to(DIST)}: anchor #{frag} missing in {target.name}")

    css_file = DIST / "assets" / "system.css"
    for u in re.findall(r"url\(['\"]?([^)'\"]+)['\"]?\)", css_file.read_text()):
        if not u.startswith(("data:", "http")) and not (css_file.parent / u).exists():
            fail("E", f"system.css: url({u}) missing")
    notes.append(f"E: links checked across {len(pages)} pages · dead '#' links: {dead_hash}")
    return dead_hash


# ---------- gate F · honesty ----------

def gate_f(dead_hash):
    info = json.loads((DIST / "BUILDINFO.json").read_text())
    count = 0
    for page in sorted(DIST.rglob("*.html")):
        t = re.sub(r"<(script|style)\b.*?</\1>", " ", page.read_text(), flags=re.S | re.I)
        t = re.sub(r"<[^>]+>", " ", t)
        t = re.sub(r"\s+", " ", t)  # placeholders may wrap across lines
        count += len(re.findall(r"\[[^\]]{1,200}\]", t))
    if info["mode"] == "production" and (count or dead_hash):
        fail("F", f"production dist ships {count} placeholders / {dead_hash} dead links")
    notes.append(f"F: mode={info['mode']} · visible placeholders {count} (draft keeps them visible)")


# ---------- gate G · font gate ----------

def gate_g():
    for bad in [*DIST.rglob("*.ttf"), *DIST.rglob("*.otf")]:
        fail("G", f"full-face font shipped: {bad.relative_to(DIST)}")
    woffs = {p.name: p.stat().st_size for p in DIST.rglob("*.woff2")}
    missing = EXPECTED_FONTS - set(woffs)
    if missing:
        fail("G", f"expected subsets missing: {sorted(missing)}")
    total = sum(woffs.values())
    if total > FONT_TOTAL_CAP:
        fail("G", f"font payload {total:,} B exceeds cap {FONT_TOTAL_CAP:,} B")
    notes.append(f"G: {len(woffs)} woff2 subsets, {total:,} B total (cap {FONT_TOTAL_CAP:,})")


def main():
    if not DIST.exists():
        print("no dist/ — run website/src/build.py first")
        sys.exit(1)
    gate_a()
    gate_b()
    gate_c()
    gate_d()
    dead = gate_e()
    gate_f(dead)
    gate_g()

    print("── verify_site ──")
    for n in notes:
        print(f"  {n}")
    if failures:
        print(f"\nFAIL — {len(failures)} violation(s):")
        for f in failures:
            print(f"  ✗ {f}")
        sys.exit(1)
    print("\nALL GATES PASS")


if __name__ == "__main__":
    main()
