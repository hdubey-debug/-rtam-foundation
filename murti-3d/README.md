# murti-3d — The Murti, Measured

Parametric 3D study of the Ṛtambhareśvara murti (linga · lotus jaladhārī ·
water basin · podium drum) and the **dimension-plate pipeline** that turns the
locked vertical grammar into builder-ready drawings.

## The folder

| Path | What it is |
|---|---|
| `GRAMMAR.md` | The 7·1·4·2 grammar audit — locks, latent mathematics, open questions. The written canon |
| `plate.py` | The plate generator: labels `plates/shivling3.png` with the locked measures, bilingual, and binds the sealed PDFs |
| `plates/` | **The deliverables**: `vertical-grammar.pdf` (English) · `vertical-grammar-hi.pdf` (हिंदी, for the craftsmen) · the labeled plates and their source render · `assets/` (brand seal + lockup used on the cover) |
| `src/` | The 3D instrument's source (three.js app + study-board templates) |
| `dist/` | Self-contained artifact pages: `murti-measured.html` (the instrument), `vertical-plate.html` (the plates), `horizontal-question.html` (ring-system study), `glb-view.html` |
| `build.mjs` / `shoot.mjs` / `board-shots.mjs` / `glb-shots.mjs` | Build + headless-QA harnesses (three.js from `../mandir-3d/node_modules`) |

Print copies of the plates live in [`../print/plates/`](../print/plates/) —
point builders there.

## Build & QA

```bash
node build.mjs        # bundles src/app.js into dist/murti-measured.html
python3 plate.py      # regenerates the labeled plates + both PDFs
node shoot.mjs        # headless QA screenshots (output is local-only)
```

One normalized parameter state (R = rim outer radius = 1.0, the
`brand/iconography/geometry/grid.json` convention) drives the whole solid;
the **Codified** preset IS grid.json. Once a state is agreed, fold it back
into grid.json and re-run `brand/iconography/geometry/construct.py` so the
brand marks and this study never fork.

Published as the Claude artifacts "The Murti, Measured" and the vertical
plate (default-private; rung-1 content — share per the sanctity ladder in
`brand/iconography/rtambhareshvara-murti.md` §7).
