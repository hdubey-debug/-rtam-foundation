# F15 — Documentation contradicts measured reality + US-Letter for an India trust

## Root cause

Five independent documentation/format defects, all confirmed against primary sources in the repo:

1. **Cap-height claim is wrong (font-size ≠ cap-height).** Brand-book §6, usage-rules §6, and the canonical wordmark SVG's `<desc>` all say the wordmark clear-space rule equals "the cap-height of R ≈ 120 viewBox units." But 120 is the `font-size` attribute on the `RTAM` `<text>`, not the cap-height. The actual rendered Cinzel-500 cap "R" spans Y = 76.0 → 160.0 = **84.0 viewBox units** (measured from the outlined R path in `brand/explorations/_research/spikes/negative-space-R-plain.svg`, confirmed by Spike 3 which outlined this exact glyph at fs=120). The doc conflated font-size with cap height.

2. **Font-family count is inconsistent across three docs.** `brand-book.md §5` says "Three faces" (Cinzel, Tiro, Inter) — it omits Marcellus, even though Marcellus is vendored AND is in the fallback stack of every shipped wordmark/icon/lockup SVG. `README.md` lists "six" families (adds Marcellus + Noto Serif Devanagari + Noto Sans Devanagari) but conflates vendored families with CDN-only fallbacks. `fonts/README.md` says "four font families … vendored." Ground truth (`find brand/fonts -name '*.ttf'`): **4 families vendored** — Cinzel, Marcellus, Inter, Tiro Devanagari Sanskrit. Noto Serif/Sans Devanagari are referenced in font-family stacks but **not vendored** (CDN-only Devanagari fallbacks).

3. **README falsely claims "no rasterized logo files."** `README.md` line 3 says "no rasterized logo files." False: `brand/exports/png/` contains `rtam-wordmark-white.png`, `rtam-rdot-icon-white.png`, `rtam-12-medallion-seal.png`, `rtam-12-medallion-pattern.png`, and 6 specimen PNGs; `brand/exports/mockups/` contains 9 more PNGs. The intended claim is that the *source of truth* (logos/, icons/, lockups/, seal/) is vector-only and the PNGs are *derived exports*.

4. **usage-rules §2 dark-theme row points to an instruction, not a file.** Every other row in the §2 "Picking an icon" table names a file; the dark-theme row's File cell is `(use \`-gold\` on charcoal ground)` — an instruction. The actual file to name is `rtam-rdot-icon-gold.svg` (the same gold-R icon, placed on a charcoal ground), keeping the column type-consistent.

5. **12-medallion symbolism is an uncommitted four-way pick-list.** `brand-book.md §3.5`, the seal SVG `<desc>`, and the seal-pattern SVG describe the twelve medallions as "the months of the ritual year, the signs of the zodiac, the hours of the day — or simply *the full circle*." Four meanings, none committed. **Decision (this spec): commit to the twelve Ādityas / twelve solar months of the ritual year** for the Foundation seal; reserve the twelve Jyotirliṅgas reading for a future temple-specific seal variant. (Zodiac and "hours of the day" are dropped — zodiac is astrological rather than Vedic, "hours" is a weak twelfth-fold reading for a sacred mark.)

6. **Letterhead and donation-receipt mockups are US Letter; the trust is India-based (A4).** `letterhead.html` and `donation-receipt.html` both set `.page { width: 816px; min-height: 1056px; }` (US Letter, 8.5×11in @96dpi). `render_html_to_png.py:33` hardcodes `format="Letter"` for PDF output, and `render_md_to_pdf.py` prints the shipped brand-book.pdf / usage-rules.pdf at Letter in two places (line 38 `@page { size: Letter; … }` and line 173 `format="Letter"`, plus the docstring line 9). An India-registered trust uses **A4** (210×297mm = **794×1123px @96dpi**).

## Files touched

Documentation / content:
- `brand/guidelines/brand-book.md` (cap-height §6, font-count §5, 12-medallion symbolism §3.5)
- `brand/guidelines/usage-rules.md` (cap-height §6, dark-theme row §2)
- `brand/README.md` (rasterized-files claim, font-family list)
- `brand/logos/rtam-wordmark-sacred-RTAM-dot.svg` (cap-height in `<desc>`)
- `brand/seal/rtam-12-medallion-seal.svg` (12-medallion symbolism in `<desc>`)
- `brand/seal/rtam-12-medallion-pattern.svg` (no symbolism text — see Residual risk; no change needed)

A4 page format:
- `brand/previews/mockups/letterhead.html` (`.page` width/height)
- `brand/previews/mockups/donation-receipt.html` (`.page` width/height)
- `brand/tools/render_html_to_png.py` (PDF format)
- `brand/tools/render_md_to_pdf.py` (PDF format, @page size, docstring)
- Re-render after edits (derived PNGs, not source edits): `brand/exports/mockups/letterhead.png`, `brand/exports/mockups/donation-receipt.png`, `brand/exports/pdf/brand-book.pdf`, `brand/exports/pdf/usage-rules.pdf`

Note: `brand/logos/`, `brand/icons/`, `brand/seal/`, `brand/tools/*.py` are normally off-limits to this research phase; the edits above are part of the *fix* (a later phase), listed here for blind implementation.

## Exact change

### A. Cap-height: 120 → 84 (three occurrences)

**`brand/guidelines/brand-book.md`** line 113.
Current:
> The wordmark gets a clear-space margin equal to the **cap-height of R** on every side. In the canonical 1080×240 viewBox that is ≈120 viewBox units. Nothing — image, fold, type, or border — may enter that zone.

Replace with:
> The wordmark gets a clear-space margin equal to the **cap-height of R** on every side. In the canonical 1080×240 viewBox the Cinzel-500 cap-R measures **84 viewBox units** tall (the `font-size` is 120; cap-height is not the same as font-size). Use **84 units** as the clear-space margin. Nothing — image, fold, type, or border — may enter that zone.

**`brand/guidelines/usage-rules.md`** line 68.
Current:
> - **Wordmark:** clear-space = cap-height of R on every side (≈120 viewBox units in the 1080×240 canonical).

Replace with:
> - **Wordmark:** clear-space = cap-height of R on every side (**84 viewBox units** in the 1080×240 canonical; the 120 figure was the font-size, not the cap-height).

**`brand/logos/rtam-wordmark-sacred-RTAM-dot.svg`** line 3, inside `<desc>`.
Current substring:
> Clear-space rule: minimum padding equal to the cap-height of R (≈120px in viewBox units) on every side.

Replace that substring with:
> Clear-space rule: minimum padding equal to the cap-height of R (84 viewBox units; the font-size is 120 but the cap-height is 84) on every side.

### B. Font-family count — make all three docs say "4 vendored brand families + Noto fallbacks"

**`brand/guidelines/brand-book.md`** §5. Line 99 currently:
> Three faces. Each does one job.

Replace with:
> Four brand faces, plus two Devanagari fallbacks. Each does one job.

Immediately after the existing 3-row table (after line 105, the Inter row), insert one new table row for Marcellus so the table reads four faces. New row (insert as line after the Inter row, before the blank line at 106):
> | **Marcellus** (400) | Alternate Latin display. The fallback face in every wordmark/icon stack when Cinzel is unavailable; softer terminals. |

Then replace line 107:
> A printable font-installation note for vendors is in `brand/README.md`. SVG glyphs can be outlined in Inkscape (`Path → Object to Path`) or Illustrator (`Type → Create Outlines`) before being sent to a print shop that lacks the fonts.

with:
> Two Devanagari web fallbacks — **Noto Serif Devanagari** and **Noto Sans Devanagari** — are referenced in font-family stacks for graceful degradation but are **not vendored** (CDN-only); the four faces above are the vendored brand families (`brand/fonts/`). A printable font-installation note for vendors is in `brand/README.md`. SVG glyphs can be outlined in Inkscape (`Path → Object to Path`) or Illustrator (`Type → Create Outlines`) before being sent to a print shop that lacks the fonts.

**`brand/README.md`** §Fonts, lines 41–46. Current block:
> - **Cinzel** (Latin display serif — primary wordmark face)
> - **Marcellus** (Latin display serif — alternate / fallback face with softer terminals)
> - **Inter** (Latin sans — UI and body)
> - **Tiro Devanagari Sanskrit** (Devanagari sacred — wordmarks and sacred contexts)
> - **Noto Serif Devanagari** (Devanagari serif fallback — long body text)
> - **Noto Sans Devanagari** (Devanagari sans — UI labels, captions)

Replace lines 39–46 (the intro sentence + 6 bullets). Current line 39:
> All previews load fonts from Google Fonts via CDN — no install required to view in a browser:

Replace the intro line 39 with:
> Four brand families are vendored as TTFs in `brand/fonts/` (Cinzel, Marcellus, Inter, Tiro Devanagari Sanskrit). Previews additionally load two CDN-only Devanagari fallbacks. No install is required to view previews in a browser:

Then replace the six bullets (lines 41–46) with:
> **Vendored brand families** (in `brand/fonts/`):
> - **Cinzel** (Latin display serif — primary wordmark face)
> - **Marcellus** (Latin display serif — alternate / fallback face with softer terminals)
> - **Inter** (Latin sans — UI and body)
> - **Tiro Devanagari Sanskrit** (Devanagari sacred — wordmarks and sacred contexts)
>
> **CDN-only Devanagari fallbacks** (referenced in stacks, not vendored):
> - **Noto Serif Devanagari** (Devanagari serif fallback — long body text)
> - **Noto Sans Devanagari** (Devanagari sans — UI labels, captions)

(The "Family URLs for the kit" list at README lines 60–67 may keep all six entries — they are install URLs, not a brand-face count, so no change needed there.)

### C. README "no rasterized logo files"

**`brand/README.md`** line 3. Current:
> This directory holds the complete RTAM Foundation visual identity as real, reproducible vector assets. Everything here is human-authored SVG, HTML, CSS, JSON, or Markdown — no rasterized logo files, no AI-generated artifacts in the source of truth.

Replace with:
> This directory holds the complete RTAM Foundation visual identity as real, reproducible vector assets. The source of truth (`logos/`, `icons/`, `lockups/`, `seal/`) is human-authored SVG, HTML, CSS, JSON, and Markdown — no rasterized logos in the source. Rasterized PNGs and PDFs exist only as *derived exports* under `exports/`, regenerated from the vector sources by the `tools/` scripts.

### D. usage-rules §2 dark-theme row → name a file

**`brand/guidelines/usage-rules.md`** line 24. Current:
> | Dark theme, ivory R + gold bindu. | (use `-gold` on charcoal ground) |

Replace with:
> | Dark theme, ivory R + gold bindu. On a charcoal ground. | `rtam-rdot-icon-gold.svg` |

### E. 12-medallion symbolism → commit to twelve Ādityas / solar months

**`brand/guidelines/brand-book.md`** §3.5 line 73. Current:
> The 12-medallion seal: one outer ring, twelve gold dots at 30° spacing, one central bindu. Reads as the months of the ritual year, the signs of the zodiac, the hours of the day — or simply *the full circle*. Use it as a **watermark**, never as the primary mark. The wordmark always wins.

Replace with:
> The 12-medallion seal: one outer ring, twelve gold dots at 30° spacing, one central bindu. The twelve medallions are the **twelve Ādityas — the twelve solar months of the ritual year**; the central bindu is the same source-dot that signs the wordmark. (A future temple-specific seal variant may read the twelve as the Jyotirliṅgas.) Use it as a **watermark**, never as the primary mark. The wordmark always wins.

**`brand/seal/rtam-12-medallion-seal.svg`** line 3, inside `<desc>`. Current `<desc>` substring:
> The twelve medallions read as: months of the ritual year, signs of the zodiac, hours of the day, or simply "the full circle". The mark is read at a glance, not parsed.

Replace that substring with:
> The twelve medallions are the twelve Ādityas — the twelve solar months of the ritual year. The mark is read at a glance, not parsed.

### F. A4 page format

**`brand/previews/mockups/letterhead.html`** lines 20–21. Current:
>       width: 816px;
>       min-height: 1056px;

Replace with:
>       width: 794px;
>       min-height: 1123px;

**`brand/previews/mockups/donation-receipt.html`** lines 20–21. Current:
>       width: 816px;
>       min-height: 1056px;

Replace with:
>       width: 794px;
>       min-height: 1123px;

**`brand/tools/render_html_to_png.py`** line 33. Current:
>             page.pdf(path=str(out_path), format="Letter", print_background=True)

Replace with:
>             page.pdf(path=str(out_path), format="A4", print_background=True)

**`brand/tools/render_md_to_pdf.py`** — three edits.
Line 9 (docstring). Current:
> the brand palette), then printed to Letter-size PDF.

Replace with:
> the brand palette), then printed to A4-size PDF.

Line 38. Current:
>     @page {{ size: Letter; margin: 22mm 20mm; }}

Replace with:
>     @page {{ size: A4; margin: 22mm 20mm; }}

Line 173. Current:
>                 format="Letter",

Replace with:
>                 format="A4",

After these edits, regenerate the derived outputs:
```
python3 brand/tools/render_html_to_png.py brand/previews/mockups/letterhead.html      brand/exports/mockups/letterhead.png
python3 brand/tools/render_html_to_png.py brand/previews/mockups/donation-receipt.html brand/exports/mockups/donation-receipt.png
python3 brand/tools/render_md_to_pdf.py   brand/guidelines/brand-book.md   brand/exports/pdf/brand-book.pdf
python3 brand/tools/render_md_to_pdf.py   brand/guidelines/usage-rules.md  brand/exports/pdf/usage-rules.pdf
```

## Parameters resolved

| Parameter | Final value | Rationale |
|---|---|---|
| Cinzel-500 cap-R height (canonical viewBox) | **84 viewBox units** | Measured: outlined R path spans Y 76.0→160.0 in `negative-space-R-plain.svg` (Spike 3 outlined this exact fs=120 glyph). 160−76 = 84. |
| The mistaken figure being replaced | **120** | It is the `font-size` attribute on the `RTAM` `<text>`, not the cap-height. |
| Vendored brand-family count | **4** | `find brand/fonts -name '*.ttf'` → Cinzel, Marcellus, Inter, Tiro Devanagari Sanskrit. Matches `fonts/README.md`. |
| Brand faces named in brand-book §5 | **4** (add Marcellus) | Marcellus is vendored AND in every shipped SVG fallback stack; omitting it was the §5 error. |
| Noto Serif/Sans Devanagari status | **CDN-only fallbacks, not vendored** | Referenced in Devanagari stacks/specimen; no TTF in `brand/fonts/`. |
| Dark-theme icon file | **`rtam-rdot-icon-gold.svg`** | The gold-R icon exists and is the gold R placed on a charcoal ground; the row described that exact use. |
| 12-medallion committed meaning | **Twelve Ādityas / twelve solar months of the ritual year** | Per the locked finding decision; Vedic-grounded twelve-fold reading; Jyotirliṅgas reserved for a future temple seal variant. |
| A4 width @96dpi | **794px** | 210mm ÷ 25.4 × 96 = 793.7 → 794. |
| A4 height @96dpi | **1123px** | 297mm ÷ 25.4 × 96 = 1122.5 → 1123. |
| Letter values being replaced | **816 × 1056px** | 8.5in × 96 = 816; 11in × 96 = 1056. |
| PDF `format` string | **"A4"** | Playwright `page.pdf` accepts the named format "A4"; replaces "Letter". |

## Proof

No proof PNG required (documentation/format-text edits; visual regression is out of scope for this finding). The cap-height number is verified arithmetically and geometrically above (R path Y-extent 76.0→160.0 = 84.0). The font-vendor count is verified by directory listing. The A4 pixel values are verified by the mm→px conversion at 96dpi.

## Verification steps

US-16 re-audit confirms each item mechanically:

1. **Cap-height:** `grep -rn "120 viewBox\|≈120px\|cap-height of R" brand/guidelines brand/logos` returns no "120" paired with cap-height; the strings now read "84." Optionally re-outline the canonical R and assert glyph-bbox height == 84 ± 0.5.
2. **Font count:** `brand-book.md §5` table has 4 face rows and names the Noto pair as non-vendored fallbacks; `README.md` Fonts section splits "vendored" (4) from "CDN-only" (2); `fonts/README.md` unchanged at "four." All three are now mutually consistent and match `find brand/fonts -name '*.ttf'` (4 families).
3. **Rasterized claim:** `grep -n "no rasterized logo files" brand/README.md` returns nothing; the replacement sentence scopes the no-raster claim to the source-of-truth directories and acknowledges `exports/` PNGs/PDFs.
4. **Dark-theme row:** `grep -n "use \`-gold\` on charcoal" brand/guidelines/usage-rules.md` returns nothing; the §2 File column is now 100% filenames (`grep` the table: every File cell ends in `.svg`).
5. **12-medallion:** `grep -rn "zodiac\|hours of the day" brand/guidelines brand/seal` returns nothing; brand-book §3.5 and the seal `<desc>` both say "twelve Ādityas / twelve solar months."
6. **A4:** `grep -rn "816\|1056" brand/previews/mockups/letterhead.html brand/previews/mockups/donation-receipt.html` returns nothing; `grep -rn "Letter" brand/tools/render_html_to_png.py brand/tools/render_md_to_pdf.py` returns nothing; re-rendered `letterhead.png`/`donation-receipt.png` have aspect ratio 794:1123 (1.414, A4) not 816:1056 (1.294); `brand-book.pdf`/`usage-rules.pdf` page boxes are 595×842pt (A4) not 612×792pt (Letter).

## Residual risk

- **A4 reflow:** the receipt/letterhead `.page` paddings (88×80 / 96×88) and the certificate are unchanged; A4 is 22px narrower and 67px taller than Letter, so content reflows slightly. Low risk (both pages have ample whitespace), but the re-rendered PNGs should be eyeballed once for content spilling past the page or awkward bottom gaps. The certificate (1100×850 landscape) is intentionally a landscape certificate format, not correspondence — left as-is and out of scope.
- **`render_md_to_pdf.py` scope creep:** the finding named only `render_html_to_png.py:33`, but the brand-book/usage-rules PDFs (the actual India-trust documents) are produced by `render_md_to_pdf.py` at Letter. Leaving it would ship Letter PDFs while claiming A4, so it is included; flag for reviewer confirmation that touching this second tool is acceptable.
- **`rtam-12-medallion-pattern.svg`** `<desc>` describes only the pattern tiling, not the four-way symbolism, so it needs no change — but if a future reviewer wants the Ādityas reading echoed there, it is a one-line optional add.
- **Marcellus row in §5** introduces a face the brand-book previously framed as "fallback only"; if the brand voice prefers to keep §5 listing only *primary* faces, an alternative is to keep "Three faces" but add a footnote "(plus Marcellus as the Cinzel fallback)". This spec chooses the four-row table for maximum doc/SVG consistency.

## Depends on

none

## Durable or provisional

**Durable.** These are documentation-truth and format corrections. The cap-height *number* (84) is tied to Cinzel's specific letterform and is therefore **provisional** in the narrow sense that a Phase-2 letterform replacement would change it — but the *rule* ("clear-space = the measured cap-height of R, which is not the font-size") is durable. The A4 decision, the vendored-vs-fallback font taxonomy, the rasterized-export clarification, the file-named dark-theme row, and the committed twelve-Ādityas symbolism are all durable.
