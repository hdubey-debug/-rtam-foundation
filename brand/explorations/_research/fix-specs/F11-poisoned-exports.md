# F11 — Committed PNG/PDF exports are fallback-font (poisoned) renders

## Root cause

The repo's two export tools rasterize **live-text** assets (SVGs with
`<text>` + `@import` Google Fonts, or markdown rendered through a web-font HTML
template) but neither tool guarantees the brand fonts are actually present at
rasterization time. Two distinct mechanisms produce the same defect — a
shipped export in which the brand typeface (Cinzel for Latin, Inter for body)
has been silently replaced by a generic fallback and **baked into the pixels**:

1. **cairosvg cannot load web fonts** (`tools/render_svg_to_png.py` calls
   `cairosvg.svg2png`). For any live-text SVG it substitutes a generic
   sans-serif. `exports/png/rtam-wordmark-white.png` and
   `rtam-rdot-icon-white.png` are such renders — the "RTAM Foundation"
   wordmark and the "Ṛ" monogram ship in a plain sans, not Cinzel.

2. **Network web-font failure in the Chromium PDF path**
   (`tools/render_md_to_pdf.py`). The HTML template pulls Cinzel/Inter/Tiro/
   JetBrains via a single combined `<link>` to `fonts.googleapis.com`, waits
   only for `networkidle` + 500 ms, and never awaits `document.fonts.ready`.
   On this cluster that combined request does not reliably deliver Cinzel and
   Inter, so `exports/pdf/brand-book.pdf` and `usage-rules.pdf` embed
   **DejaVuSans / DroidSansDevanagari** for the headings and body instead of
   Cinzel and Inter. (Re-running with `document.fonts.ready` awaited did **not**
   fix it — the network faces simply do not arrive; only removing the network
   `<link>` and substituting local `file://` faces does — see Parameters.)

The seal / pattern PNGs are **pure geometry** (`<circle>`/`<rect>`/`<pattern>`,
no `<text>`, no fonts), so cairosvg renders them faithfully — they are clean
despite also coming from `render_svg_to_png.py`. The specimen and mockup PNGs
were rendered by Chromium (`render_html_to_png.py`) and reproduce faithfully.

## Files touched

Regeneration replaces poisoned export **bytes** (no source SVG/MD/HTML edits —
those are owned by other findings):

- `brand/exports/png/rtam-wordmark-white.png`  (regenerate)
- `brand/exports/png/rtam-rdot-icon-white.png`  (regenerate)
- `brand/exports/pdf/brand-book.pdf`  (regenerate)
- `brand/exports/pdf/usage-rules.pdf`  (regenerate)

Pipeline-rule change (owned here, applied in the build/generator US, not in
this research phase):

- `brand/tools/render_svg_to_png.py` — restrict to **outlined-path SVGs
  only** (or deprecate); it must never be the export path for a live-text SVG.
- The PNG export of live-text logos/icons must come from the **outlined
  master** (US-13 Track C `outline.py`) rasterized by Chromium, OR directly
  from a faithful Chromium render of the live-text SVG.
- The PDF export tool must load brand fonts from **local `file://` TTFs**, not
  a network `<link>`, and must await `document.fonts.ready`.

## Exact change

### A. Definitive poisoned / clean inventory (every file in `exports/`)

Metric: `brand/tools/render_diff.py::structural_diff` on ink masks
(`max_blob` px on the 1024 grid; gate 150) plus white-composited ink-pixel
counts and embedded-BaseFont inspection. "committed vs CHROMIUM" = committed
export vs a faithful Chromium re-render of the same source; "committed vs
CAIROSVG" = committed export vs a cairosvg re-render of the same SVG.

| Export | Source | Renderer used | committed vs CHROMIUM | committed vs CAIROSVG | Verdict |
|---|---|---|---|---|---|
| png/rtam-wordmark-white.png | logos/…white.svg (live text) | cairosvg | **217062 px** / IoU 0.064 | 184 px / IoU 0.918 | **POISONED** |
| png/rtam-rdot-icon-white.png | icons/…white.svg (live text) | cairosvg | **84363 px** / IoU 0.578 | 166 px / IoU 0.994 | **POISONED** |
| png/rtam-12-medallion-seal.png | seal/…seal.svg (geometry) | cairosvg | 704 px* | 27 px | CLEAN |
| png/rtam-12-medallion-pattern.png | seal/…pattern.svg (geometry) | cairosvg | 4649 px* | 22 px | CLEAN |
| png/wordmark-specimen.png | previews/wordmark-specimen.html | Chromium | 0 px / IoU 1.000 | — | CLEAN |
| png/typography-specimen.png | previews/typography-specimen.html | Chromium | 0 px / IoU 1.000 | — | CLEAN |
| png/monogram-specimen.png | previews/monogram-specimen.html | Chromium | 0 px / IoU 1.000 | — | CLEAN |
| png/devanagari-monogram-specimen.png | previews/…html | Chromium | 0 px / IoU 1.000 | — | CLEAN |
| png/lockups-specimen.png | previews/lockups-specimen.html | Chromium | 0 px / IoU 1.000 | — | CLEAN |
| png/seal-specimen.png | previews/seal-specimen.html | Chromium | 0 px / IoU 1.000 | — | CLEAN |
| mockups/index.png | previews/index.html | Chromium | 0 px / IoU 1.000 | — | CLEAN |
| mockups/certificate.png | previews/mockups/…html | Chromium | 0 px / IoU 1.000 | — | CLEAN |
| mockups/donation-poster.png | …html | Chromium | 0 px / IoU 1.000 | — | CLEAN |
| mockups/donation-receipt.png | …html | Chromium | 0 px / IoU 1.000 | — | CLEAN |
| mockups/favicon-scale-test.png | …html | Chromium | 0 px / IoU 1.000 | — | CLEAN |
| mockups/instagram-avatar.png | …html | Chromium | 0 px / IoU 1.000 | — | CLEAN |
| mockups/letterhead.png | …html | Chromium | 0 px / IoU 1.000 | — | CLEAN |
| mockups/website-header.png | …html | Chromium | 0 px / IoU 1.000 | — | CLEAN |
| mockups/youtube-banner.png | …html | Chromium | 17 px / IoU 0.934 | — | CLEAN |
| pdf/brand-book.pdf | guidelines/brand-book.md | Chromium (net-font) | embeds DejaVuSans + DroidSansDevanagari (no Cinzel, no Inter) | — | **POISONED** |
| pdf/usage-rules.pdf | guidelines/usage-rules.md | Chromium (net-font) | embeds DejaVuSans + JetBrainsMono (no Cinzel, no Inter) | — | **POISONED** |

\* The seal/pattern `max_blob` vs Chromium is a **measurement artifact**, not
poisoning: the committed PNGs are RGBA-transparent (1:1 with viewBox, exactly
cairosvg's default output), so `ink_mask`'s border-background auto-detection
plus ±4 px registration disagree with Chromium's white-bg screenshot on the
thin (1.25 px, opacity-0.55) gold strokes. Composited on white, ink-pixel
counts are identical: seal 17682 (committed) / 17682 (cairo) / 17681 (chrome);
pattern 10179 / 10179 / 9837 (3 % AA on faint strokes). Side-by-side
(`_scratch/rtam-12-medallion-pattern.3up.png`) is visually identical. **The
structural_diff gate is calibrated for same-content opaque renders; a large
blob from a transparent-vs-white compositing mismatch must NOT be read as
poisoning.**

### B. Regeneration procedure (exact)

Run from the repo root with the existing env (`/usr/bin/python3`, Playwright
Chromium already installed). Scratch is gitignored; write directly to
`exports/`.

**B1 — Two live-text PNGs.**

**Durable path (target architecture — lead with this): rasterize the US-13
outlined master.** US-13 Track C `outline.py` emits a path-only SVG of the
wordmark / icon (no `<text>`, no fonts — Spike 2 proved cross-renderer parity
at max-blob = 11 px for this exact Latin composition). Rasterize it with either
renderer (both pass the fidelity gate, since there are no fonts to load). This
is the path the task's pipeline decision mandates and the only one with **no
network dependency**:

```
# once outline.py exists (US-13 Track C):
python3 brand/tools/outline.py brand/logos/rtam-wordmark-white.svg  /tmp/wm.outlined.svg
python3 brand/tools/render_svg_to_png.py /tmp/wm.outlined.svg brand/exports/png/rtam-wordmark-white.png 2160
python3 brand/tools/outline.py brand/icons/rtam-rdot-icon-white.svg /tmp/ic.outlined.svg
python3 brand/tools/render_svg_to_png.py /tmp/ic.outlined.svg brand/exports/png/rtam-rdot-icon-white.png 512
```

**Interim path (until `outline.py` lands): faithful Chromium render of the
source live-text SVG**, transparent-background screenshot at native viewBox ×
integer scale (keeps the baked charcoal `<rect>` ground the SVG contains):

```
# rtam-wordmark-white.png  (viewBox 1080×240, render at 2× -> 2160×480)
python3 - <<'PY'
from playwright.sync_api import sync_playwright
from pathlib import Path
svg = Path("brand/logos/rtam-wordmark-white.svg").resolve()
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_context(viewport={"width":1080,"height":240},
                       device_scale_factor=2).new_page()
    pg.goto(svg.as_uri(), wait_until="networkidle")
    pg.evaluate("() => document.fonts.ready"); pg.wait_for_timeout(400)
    pg.screenshot(path="brand/exports/png/rtam-wordmark-white.png")
    b.close()
PY
# rtam-rdot-icon-white.png  (viewBox 256×256, render at 2× -> 512×512) — same
# block with svg=icons/rtam-rdot-icon-white.svg, viewport 256×256, scale 2.
```

The interim path works on this cluster today (the SVG `@import` *does* deliver
Cinzel — verified: `document.fonts` reports "Cinzel loaded") but is
network-dependent; switch to the outlined-master path as soon as US-13 lands.
Both produce identical pixels (proven cross-renderer parity).

**B2 — Two PDFs, from `render_md_to_pdf.py` with local fonts + fonts.ready.**
Four edits to the tool's TEMPLATE + render(), all required (each maps to a
proven defect):

(i) **Delete** the network `<link …fonts.googleapis…>` from the template.
(ii) **Vendor JetBrains Mono** (OFL — fetch the Regular TTF the same way Spike 4
fetched the others, place at `brand/fonts/jetbrains-mono/jetbrains-mono-400.ttf`
+ its `OFL.txt`). Without this, stripping the network link drops code-span
glyphs (JetBrains Mono is not currently vendored — confirmed by filesystem
search). This is FINAL, not optional.
(iii) **Add local `@font-face`** rules (file:// to the vendored TTFs) for every
brand family.
(iv) **Append `'Tiro Devanagari Sanskrit'` as a fallback to EVERY font stack**
(body, h1/h2/h3, th, code/pre). The committed template declares Tiro in only
ONE rule (`h1 + p em`, the tagline), so all Devanagari in body paragraphs,
table cells and headings (12 Devanagari lines in brand-book.md) fell to
DroidSansDevanagari. Adding Tiro to each stack removes Droid entirely (proven).
(v) **Await `document.fonts.ready`** before `page.pdf()`.

```
# Template <head> — replace the Google <link> with these local faces:
@font-face{font-family:'Cinzel';font-weight:400;src:url('file://…/brand/fonts/cinzel/cinzel-400.ttf')}
@font-face{font-family:'Cinzel';font-weight:500;src:url('file://…/brand/fonts/cinzel/cinzel-500.ttf')}
@font-face{font-family:'Cinzel';font-weight:600;src:url('file://…/brand/fonts/cinzel/cinzel-600.ttf')}
@font-face{font-family:'Cinzel';font-weight:700;src:url('file://…/brand/fonts/cinzel/cinzel-700.ttf')}
@font-face{font-family:'Inter';font-weight:400;src:url('file://…/brand/fonts/inter/inter-400.ttf')}
@font-face{font-family:'Inter';font-weight:500;src:url('file://…/brand/fonts/inter/inter-500.ttf')}
@font-face{font-family:'Inter';font-weight:600;src:url('file://…/brand/fonts/inter/inter-600.ttf')}
@font-face{font-family:'Tiro Devanagari Sanskrit';src:url('file://…/brand/fonts/tiro-devanagari-sanskrit/tiro-devanagari-sanskrit-400.ttf')}
@font-face{font-family:'JetBrains Mono';font-weight:400;src:url('file://…/brand/fonts/jetbrains-mono/jetbrains-mono-400.ttf')}

# Amend each font-family stack to include Tiro as a fallback:
body { font-family: Inter, 'Tiro Devanagari Sanskrit', system-ui, sans-serif; }
h1,h2,h3 { font-family: Cinzel, 'Tiro Devanagari Sanskrit', serif; }
th { font-family: Inter, 'Tiro Devanagari Sanskrit', sans-serif; }
code, pre, pre code { font-family: 'JetBrains Mono', 'Tiro Devanagari Sanskrit', ui-monospace, Menlo, Consolas, monospace; }
# (h1 + p em already has Tiro — leave it.)

# render() change: add  page.evaluate("() => document.fonts.ready")  before page.pdf()
python3 brand/tools/render_md_to_pdf.py brand/guidelines/brand-book.md  brand/exports/pdf/brand-book.pdf
python3 brand/tools/render_md_to_pdf.py brand/guidelines/usage-rules.md brand/exports/pdf/usage-rules.pdf
```

Proven by `brand/tools/_scratch/f11_pdf_full.py` (strips network link, injects
local faces, adds Tiro to every stack, awaits fonts.ready): after it ran, both
PDFs embed **only** `{Cinzel-Medium, Inter-Regular, Inter-SemiBold,
TiroDevaSanskrit-Regular}` — **zero DejaVuSans, zero DroidSansDevanagari**.
(That proof omitted JetBrains Mono because it is not yet vendored; vendoring it
per (ii) adds JetBrains Mono and is the only remaining BaseFont once the code
spans embed.)

### C. New export-pipeline rule

- **`render_svg_to_png.py` → outlined-path SVGs only.** It must reject (or is
  deprecated for) any SVG containing `<text>`/`@import`/`font-family`. Live-text
  logos and icons are exported by rasterizing the US-13 **outlined master**
  (durable, no network); the Chromium-from-SVG render (fonts.ready awaited) is
  only the interim path until `outline.py` exists.
- **All export rasterizers await `document.fonts.ready`** (SVG and HTML/PDF),
  and PDF/HTML font sources are **local `file://` TTFs**, never a network
  `<link>`/`@import`, so an export can never silently bake a fallback font.
- A CI gate (the existing `render_diff.py`/fidelity-gate, or a BaseFont
  whitelist check for PDFs) must run on every committed export so this defect
  cannot recur.

## Parameters resolved

- **Poisoned set = exactly 4 files** — rationale: only these fail a faithful
  comparison. The 2 PNGs match a cairosvg-fallback render (max_blob 184/166 px)
  and are catastrophically far from faithful Chromium (217062/84363 px); the 2
  PDFs embed DejaVuSans/DroidSansDevanagari instead of Cinzel/Inter (BaseFont
  inspection). FINAL.
- **Clean set = 17 files** — rationale: 6 specimen + 9 mockup PNGs re-render at
  max_blob ≤ 17 px (IoU ≥ 0.934, mostly 0/1.000) via faithful Chromium; the 2
  seal/pattern PNGs are geometry-only with identical white-composited ink
  counts. FINAL.
- **render_svg_to_png.py future role = outlined-only / deprecated for live
  text** — rationale: cairosvg structurally cannot load web fonts; it is
  correct *only* for path-only SVGs, which it proved on the seal/pattern. FINAL.
- **PDF font source = local file:// TTFs (all 4 families + JetBrains Mono),
  with Tiro appended as a fallback to every stack, network `<link>` removed,
  `document.fonts.ready` awaited** — rationale: awaiting fonts.ready alone still
  left Cinzel and Inter absent. The combined `<link>` failed to deliver Cinzel
  and Inter in both the committed PDFs *and* a fonts.ready-awaited re-run, while
  Tiro and JetBrains Mono from the **same** request did embed — a partial,
  family-specific network failure (the multi-weight families dropped), not a
  blanket block; the SVG `@import` for Cinzel even loaded successfully. The
  local file:// fix is robust regardless of cause. Removing the network `<link>`
  + local TTFs embedded Cinzel/Inter; adding Tiro to every stack removed
  DroidSansDevanagari (Devanagari appears in body/tables/headings, not just the
  tagline the template covered). All proven via `f11_pdf_full.py` → zero DejaVu,
  zero Droid. FINAL.
- **Vendor JetBrains Mono (OFL Regular TTF) to `brand/fonts/jetbrains-mono/`**
  — rationale: it is not vendored (filesystem search found none) and the
  committed PDFs got it only via the network `<link>` we are removing; without
  vendoring it, code spans regress to a generic fallback. Vendoring keeps the
  PDF fully offline/deterministic, consistent with the "local file:// only"
  rule. FINAL.
- **PNG export scale = 2× the native viewBox** → wordmark 2160×480, icon
  512×512. Rationale: a deliberate normalization to 2× (retina) for both, not
  a match to the committed sizes — the committed icon is already 512×512 (2×)
  but the committed wordmark is **1080×240 (1×)**, so this *changes* the
  wordmark's shipped dimensions to bring it in line with the repo's documented
  "2× DPI PNG renders" convention (commit 97a891a). Integer scale avoids
  resample blur. Provisional (a future size policy could revise it); the
  *mechanism* (Chromium / outlined master, fonts.ready) is durable. If the
  build US prefers to preserve the wordmark's exact 1080×240, use scale 1 — the
  poisoning fix is independent of scale.

## Proof

- `brand/explorations/_research/fix-specs/proofs/F11-wordmark-poisoned-sidebyside.png`
  — top: committed `rtam-wordmark-white.png`; bottom: faithful Chromium render
  of the same SVG. The eye sees the committed export in a flat geometric
  **sans-serif** ("RTAM Foundation"), while the faithful render is **Cinzel** —
  Trajan-like serifed Roman caps with classic stroke modulation and small-cap
  "FOUNDATION". Different typeface entirely; the gold bindu dot (a `<circle>`)
  is the only element identical in both.
- `brand/explorations/_research/fix-specs/proofs/F11-icon-poisoned-sidebyside.png`
  — left: committed `rtam-rdot-icon-white.png` (plain sans "R"); right: faithful
  Cinzel "Ṛ" with serifs and the characteristic curved leg. Bindu identical.
- `brand/explorations/_research/fix-specs/proofs/F11-pdf-devanagari-conjunct-check.png`
  — strengthener for the PDF recipe: the temple/Sanskritic strings rendered
  through the mixed brand stacks with Tiro appended as a per-glyph fallback. The
  eye should see the conjuncts form correctly (द्म्भ in ऋतम्भरेश्वर, ष्ठ in
  प्रतिष्ठान, श्व in रेश्वर, word-final virāma in ऋतम्) with no dotted circles —
  identical shaping to Spike 1, which validated Tiro as the sole Devanagari
  font; and the Latin "(HEADING STACK)" still renders in Cinzel, confirming the
  per-glyph fallback keeps Latin on the brand font while routing Devanagari to
  Tiro.

## Verification steps (US-16 re-audit)

1. For each of the 4 regenerated files, re-run the F11 comparison:
   `structural_diff(ink_mask(committed), ink_mask(faithful_chromium))` for the
   2 PNGs — expect **max_blob ≤ 150 px** (was 217062 / 84363). The
   reference script `brand/tools/_scratch/f11_audit.py` automates this for the
   PNGs; `f11_pdf_probe.py` / `f11_pdf_localfont.py` for the PDFs.
2. For the 2 PDFs, inspect embedded `/BaseFont` entries — they must be a
   **subset of the whitelist `{Cinzel*, Inter*, TiroDevaSanskrit*,
   JetBrainsMono*}`** and contain **zero `DejaVu*` and zero `Droid*`**. (Proven
   reachable: `f11_pdf_full.py` already yields `{Cinzel, Inter, Tiro}` with zero
   DejaVu/Droid; vendoring JetBrains Mono per B2(ii) adds JetBrainsMono for code
   spans.) A regex over the PDF bytes for `/BaseFont /([A-Za-z...]+)` automates
   this whitelist check — wire it into CI.
3. Confirm the 17 clean files are byte-unchanged (or, if re-exported by the new
   pipeline, still pass max_blob ≤ 150 / IoU ≥ 0.93).
4. Confirm `render_svg_to_png.py` now refuses a live-text SVG (or is removed
   from the export path), and that every export rasterizer awaits
   `document.fonts.ready` with local `file://` font sources.

## Residual risk

- **Vendoring JetBrains Mono is a prerequisite of B2(ii), not an open
  question** — but it does add one fetch step (Google Fonts API, non-woff2 UA,
  as Spike 4 did for the others) plus an `OFL.txt`. If that fetch is blocked at
  build time, code spans fall back to a generic monospace; visual impact is low
  (monospace fallbacks are close) and the *brand* fonts are unaffected.
- The interim Chromium-from-SVG PNG path depends on the SVG `@import` succeeding
  on the build host; it works on this cluster today but is network-dependent.
  The durable mitigation (lead path in B1) is to rasterize the US-13 **outlined
  master** — no fonts, no network, cross-renderer-proven. Once `outline.py`
  exists the network dependency is fully removed.
- `structural_diff` can mis-flag a clean transparent export against a white-bg
  reference (the seal/pattern artifact: 704/4649 px blobs from compositing, not
  poisoning). The re-audit must composite both on a common background (or
  compare same-renderer outputs) before trusting the blob.
- One ⅛-em-sized risk: the Tiro fallback is appended *after* the Latin family
  in each stack, so Latin still renders in Cinzel/Inter (browsers pick the
  first family that covers each codepoint per-glyph). Verified empirically
  (Cinzel/Inter still embed alongside Tiro); but if a future Tiro build ever
  claims Latin coverage, the per-glyph fallback order keeps Latin on
  Cinzel/Inter, so this is safe.

## Depends on

- **F11 stands alone for the audit + immediate regeneration.** The *durable*
  PNG path (rasterize outlined masters) depends on US-13 Track C `outline.py`.
- Any finding that edits the source SVGs/MD (e.g. font-loading hardening, the
  baked-ground rect, bindu geometry) must land **before** the final export
  regeneration so the regenerated bytes reflect the fixed source. Coordinate
  ordering with those F-numbers; this spec only owns the export bytes + the
  pipeline rule, not the source content.

## Durable or provisional

- **Durable:** the poisoned/clean classification and the root-cause analysis
  (cairosvg can't load web fonts; network web-font PDF race); the pipeline
  rules (render_svg_to_png.py = outlined-only; await `document.fonts.ready`;
  local `file://` fonts; CI fidelity/BaseFont gate). These hold regardless of
  the Phase-2 letterform decision.
- **Provisional:** the specific 2× export sizes and the exact pixel-diff
  numbers above are tied to today's Cinzel composition; if Phase-2 replaces the
  Cinzel letterform, the *numbers* change but the *procedure* does not.
