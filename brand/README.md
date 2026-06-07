# RTAM Foundation — Brand Kit

This directory holds the complete RTAM Foundation visual identity as real, reproducible vector assets. Everything here is human-authored SVG, HTML, CSS, JSON, or Markdown — no rasterized logo files, no AI-generated artifacts in the source of truth.

## Identity in one paragraph

**RTAM Foundation** is the public English name. **ṚTAM Foundation** is the sacred form, where the under-dot beneath the **R** is the brand signature (bindu / root / source). The Sanskrit equivalent is **ऋतम् फाउंडेशन** (or **ऋतम् प्रतिष्ठान** in pure Sanskritic form). The temple lockup uses **Rtambhareshvara Mandir / ऋतम्भरेश्वर मंदिर**. The visual language is typography-led, minimal, modern, and scholarly — sacred without being decorative.

## Folder map

```
brand/
├── spec/         brand.json — the asset tree as data (SINGLE SOURCE OF TRUTH)
├── palette/      colors.json + colors.css
├── logos/        Foundation wordmarks: 5 Latin + 2 Devanagari + 3 temple
├── icons/        Ṛ monogram (5) + ऋ monogram (4) + favicon
├── lockups/      bilingual + sanskritic + temple + donation lockups (4)
├── previews/     HTML pages to view every asset in a browser
│   ├── index.html                  master gallery
│   ├── typography-specimen.html    every test string × every font
│   └── mockups/                    letterhead, poster, avatar, etc.
├── guidelines/   brand-book.md + usage-rules.md
├── tools/        brandlib + generate/outline/parity + build.sh, rasterization helpers
├── dist/         outlined distribution masters (built; gitignored)
└── exports/      rendered PNGs (favicon sizes, mockups) and PDFs
```

## How to view the brand kit

Open any `.svg` file directly in a modern browser. To see the full gallery with every variant across color modes and sizes, open `previews/index.html` after US-8 is complete.

```bash
# Once previews exist:
xdg-open brand/previews/index.html   # Linux
open     brand/previews/index.html   # macOS
```

## Fonts

All previews load fonts from Google Fonts via CDN — no install required to view in a browser:

- **Cinzel** (Latin display serif — primary wordmark face)
- **Marcellus** (Latin display serif — alternate / fallback face with softer terminals)
- **Inter** (Latin sans — UI and body)
- **Tiro Devanagari Sanskrit** (Devanagari sacred — wordmarks and sacred contexts)
- **Noto Serif Devanagari** (Devanagari serif fallback — long body text)
- **Noto Sans Devanagari** (Devanagari sans — UI labels, captions)

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

Two helper scripts live under `tools/`:

- `render_svg_to_png.py <in.svg> <out.png> [width]` — uses `cairosvg`.
- `render_html_to_png.py <in.html> <out.png|.pdf> [viewport_width]` — uses Playwright Chromium.

Install requirements:

```bash
pip install --user cairosvg playwright
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
