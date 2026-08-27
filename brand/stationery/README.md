# ṚTAM stationery — the temple's hand

Print instruments for ऋतम्भरेश्वर मंदिर: letterhead, दान-रसीद book, seal &
address stamps, return-address labels. Research + nine ratified decisions:
the "The Temple's Hand" dossier (2026-08-26). Build: `python3 build.py` ·
gate: `python3 checks.py` (PyMuPDF, read-only, undeclared-on-purpose).

## The pieces

| Piece | Master | Order/use |
|---|---|---|
| Letterhead (press) | `dist/letterhead.pdf` | Offset/digital press run. **Paper IS the chandra ground: BILT Royal Executive Bond "Corona Cream" 100 gsm** (everyday) or **Conqueror Cream Wove 100 gsm** (formal). Ground is never printed. Tell an offset shop: wax-free inks (sheets go through home lasers later) |
| Letterhead (mono) | `dist/letterhead-mono.pdf` | Home-laser edition — single ink, neutral hairlines, mono chakra. Print on the same cream bond |
| Typing template | `dist/letterhead.docx` | Word/Docs — head+footer are locked images; body Georgia 11/1.4 (graceful fallback). **Digital letters only; print correspondence uses the printed sheets** (the Yale boundary) |
| Second sheet | — | Plain matching cream stock, no artwork. Continuation header is typed |
| दान-रसीद book | `dist/receipt-a5.pdf` + `dist/receipt-cover-a5.pdf` | NCR duplicate books (single ink) — hand `receipt-press-spec.md` to the printer |
| दान-रसीद colour | `dist/receipt-a5-color.pdf` | Donor-facing colour edition (gold hub) — digital receipts / premium print runs; generated from the same source, editions can't drift |
| Seal (मुहर) |  `dist/seal-chakra-round.pdf` (Ø50, RATIFIED) | The FULL chakra in its thickened stamp edition — `stamp-vendor-spec.md` to the stamp shop. Violet pad |
| Address stamp | `../dist/outlined/icons/rtam-address-stamp.svg` | Fully bilingual, 75×38 mm, Trodat 4926 class — same vendor sheet |
| Labels | `dist/labels-st8.pdf` | Home laser on **Oddy ST-8** (99.1×67.7, 8-up A4) sheets at **100% scale**. First run `dist/labels-alignment-test.pdf` on plain paper. Sticker sits bottom-left of the envelope face (PO Guide cl. 30) |

## Rules that bind these pieces

- **One gold per page** — on the letterhead it is the chakra's hub, which is
  the wordmark's bindu in another rendering (ratified D1a). Nothing else gilds.
- **Devanagari leads** at ≥2× its English line (here 3×) — city print voice.
- **Mail-facing artifacts** (labels, address stamp, envelopes): figures in
  international numerals, post town as BARELA in Latin block letters (G4).
  The round seal never mails — Devanagari digits welcome there.
- **Nothing prints a legal claim until it is real** (D6/D8): no email until
  the mailbox is live, no regn./PAN/80G until registered — then the artwork
  gets its one-line revision and the next printing carries the fact. Never
  hand-fill a legal line.
- Ceremonial tier (later): foil hub + blind emboss on 120–160 gsm; watermark
  stays off working sheets (D9).

## Regeneration

Assets come from `brand/spec/brand.json` → `bash brand/tools/build.sh --write`
(includes the arc-rim seal via the per-cluster arc-text primitive in
brandlib). Then `python3 build.py && python3 checks.py` here. The DOCX needs
python-docx (present on the cluster).
