# RTAM Foundation — Brand Kit

This directory holds the complete RTAM Foundation visual identity as real, reproducible vector assets. Everything here is human-authored SVG, HTML, CSS, JSON, or Markdown — no rasterized logo files, no AI-generated artifacts in the source of truth.

## Identity in one paragraph

**RTAM Foundation** is the public English name. **ṚTAM Foundation** is the sacred form, where the under-dot beneath the **R** is the brand signature (bindu / root / source). The Sanskrit equivalent is **ऋतम् फाउंडेशन** (or **ऋतम् प्रतिष्ठान** in pure Sanskritic form). The temple lockup uses **Rtambhareshvara Mandir / ऋतम्भरेश्वर मंदिर**. The visual language is typography-led, minimal, modern, and scholarly — sacred without being decorative.

## Folder map

```
brand/
├── spec/         brand.json — the asset tree as data (SINGLE SOURCE OF TRUTH)
├── palette/      colors.json (colour canon) + colors.css (generated from it)
├── logos/        Foundation wordmarks: 6 Latin + 2 Devanagari + 3 temple
├── icons/        Ṛ monogram (8: 5 open + 3 circle) + ऋ monogram (4) + favicon (light + dark)
├── lockups/      bilingual + sanskritic + temple (light + dark) + donation (5)
├── iconography/  sanctum murti reference (design intent; not distribution)
├── previews/     HTML pages to view every asset in a browser
│   ├── index.html                  master gallery (marks embedded from dist/)
│   ├── typography-specimen.html    every test string × every font
│   └── mockups/                    letterhead, poster, avatar, etc.
├── guidelines/   brand-book.md + usage-rules.md
├── tools/        brandlib + generate/outline/parity/palette_sync + build.sh, render helpers
├── dist/         outlined distribution masters (COMMITTED — the consumer path)
└── exports/      rendered PNGs (favicon sizes, mockups, platform) and PDFs
```

## How to use the assets

**Consumers: take files from `brand/dist/outlined/`.** Every glyph there is
already outlined to `<path>`, so the SVGs render identically everywhere — as
`<img>`, in Office/print pipelines, and in design tools — with no fonts
installed. The SVGs under `logos/ icons/ lockups/` are the *editable sources*
(live `<text>`); they are faithful only where the brand fonts are available.

To browse everything, open the gallery:

```bash
xdg-open brand/previews/index.html   # Linux
open     brand/previews/index.html   # macOS
```

## Fonts

**Four families are vendored in `brand/fonts/`** (the canonical statement —
`fonts/README.md` has files, provenance, licenses):

- **Cinzel** 400/500/600/700 (Latin display serif — primary wordmark face)
- **Marcellus** 400 (reserve display serif — Cinzel's fallback stack only)
- **Inter** 300/400/500/600 (Latin sans — UI and body)
- **Tiro Devanagari Sanskrit** 400 (Devanagari sacred — wordmarks and sacred contexts)

CDN-only fallbacks (never vendored): **Noto Serif Devanagari** and **Noto Sans
Devanagari**, after Tiro in Devanagari stacks. Preview *pages* load fonts from
Google Fonts for their own chrome, but the brand marks they display are `<img>`
embeds of the outlined masters — correct with no fonts at all.

SVG files reference these fonts by `font-family`. When opening an SVG in Inkscape / Illustrator / Figma without the fonts installed, install them locally first (or run **Path → Object to Path** in Inkscape / **Type → Create Outlines** in Illustrator) to convert text to outlined paths.

### Installing fonts locally

The most reliable path is the Google Fonts website itself:

1. Visit each family's page (e.g. <https://fonts.google.com/specimen/Cinzel>) — search for the family name, then click **Download family**.
2. Unzip the downloaded archive into your fonts directory:
   - **Linux:** `~/.fonts/` then run `fc-cache -f`
   - **macOS:** open each `.ttf`/`.otf` in Font Book → *Install Font*
   - **Windows:** right-click each `.ttf`/`.otf` → *Install*

Family URLs for the kit:

- <https://fonts.google.com/specimen/Cinzel>
- <https://fonts.google.com/specimen/Marcellus>
- <https://fonts.google.com/specimen/Inter>
- <https://fonts.google.com/specimen/Tiro+Devanagari+Sanskrit>
- <https://fonts.google.com/specimen/Noto+Serif+Devanagari>
- <https://fonts.google.com/specimen/Noto+Sans+Devanagari>

The brand signature (the dot under **R**) is drawn as an SVG `<circle>` element, **not** the Unicode combining dot — so the bindu renders correctly regardless of font availability.

## Color tokens

| Token | Hex | Use |
|---|---|---|
| `--rtam-gold` | `#C8A15A` | Sacred accent — bindu, accent strokes |
| `--rtam-ivory` | `#F7F3E9` | Primary light background |
| `--rtam-charcoal` | `#1A1A1A` | Primary text, dark surfaces |
| `--rtam-sandstone` | `#E6DED1` | Secondary surface, dividers |
| `--rtam-indigo` | `#1C1A3D` | Optional dark surface (sacred night) |
| `--rtam-bronze` | `#9B6A2F` | Heavier accent for print |
| `--rtam-stone` | `#B8B1A4` | Captions, metadata, low-emphasis text |

Source of truth: [`palette/colors.json`](palette/colors.json). CSS variables: [`palette/colors.css`](palette/colors.css).

## Tooling

The pipeline lives under `tools/` — one command proves and (re)builds the tree:

```bash
brand/tools/build.sh          # verify: palette canon + parity gates + dry-runs
brand/tools/build.sh --write  # regenerate sources + dist/outlined, re-verify
```

Pieces: `brandlib.py` (the engine), `generate.py` (live-text sources),
`outline.py` (dist masters), `parity.py` (3-gate fidelity proof),
`palette_sync.py` (colors.json → colors.css + token check), `contrast.py`
(WCAG pairs), plus render helpers (`render_svg_to_png.py`,
`render_html_to_png.py`, `render_md_to_pdf.py`).

Install requirements (pinned):

```bash
pip install --user -r brand/tools/requirements.txt
python3 -m playwright install chromium
```

## Build order (per the project plan)

The kit is built one user story at a time with an approval gate after each:

1. **US-1** — scaffold + tokens + tooling (this commit)
2. **US-2** — typography specimen
3. **US-3** — primary wordmark
4. **US-4** — Ṛ monogram icon
5. **US-5** — Devanagari ऋ monogram icon
6. **US-6** — bilingual + temple lockups
7. **US-7** — ~~optional 12-medallion seal~~ *(built, then retired — the circle-enclosed Ṛ monogram is the system's contained "seal" mark)*
8. **US-8** — master preview + application mockups
9. **US-9** — brand book + usage rules + PDF export
10. **US-10–17** — Phase-1 consolidation: the two-entity × two-script tree
    (`spec/brand.json`), the generator + outlined-master pipeline + parity gate
    (`tools/build.sh`), circle-monogram reset, the missing standalone wordmarks,
    true overlay dark variants, and the retirement of the seal.

To edit the kit, change `spec/brand.json` and run `tools/build.sh --write`.
See [`guidelines/brand-book.md`](guidelines/brand-book.md) for the full system.
