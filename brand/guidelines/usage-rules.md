# RTAM Foundation — Usage Rules

Quick reference. For the full rationale see `brand-book.md`.

---

## 1 · Picking a wordmark

| Context | File |
|---|---|
| Default. Anywhere the bindu reproduces. | `rtam-wordmark-sacred-RTAM-dot.svg` |
| Default on dark grounds (charcoal / indigo / photo) — the sacred form with the gold bindu preserved. Transparent overlay, invisible on white. | `rtam-wordmark-white-golddot.svg` |
| Sacred surface, embossed, foil, single-color gold print. | `rtam-wordmark-gold.svg` |
| Single-colour charcoal reproduction (fax, microform, mono print). | `rtam-wordmark-black.svg` |
| Dark ground where a second colour (gold) cannot reproduce — all-ivory overlay. | `rtam-wordmark-white.svg` |
| Bindu cannot reproduce (small sign vinyl, embroidery < 6 cm). | `rtam-wordmark-public-RTAM.svg` |
| Devanagari, Sanskritic register (default). | `rtam-wordmark-devanagari-pratishthan.svg` |
| Devanagari, common register. | `rtam-wordmark-devanagari-faundeshan.svg` |
| Temple, plain English. | `rtam-temple-wordmark-latin.svg` |
| Temple, pronunciation form (Ṛ + ś). | `rtam-temple-wordmark-diacritic.svg` |
| Temple, Devanagari. | `rtam-temple-wordmark-devanagari.svg` |

---

## 2 · Picking an icon

| Context | File |
|---|---|
| Default plain mark on light grounds (charcoal R, gold bindu). | `rtam-rdot-icon-sacred.svg` |
| Dark theme (ivory R, gold bindu). | `rtam-rdot-icon-white-golddot.svg` |
| Warm / ceremonial all-gold mark on light grounds. | `rtam-rdot-icon-gold.svg` |
| Single-colour charcoal (mono print, stamps). | `rtam-rdot-icon-black.svg` |
| App icon / avatar needing a visual frame. | `rtam-rdot-icon-circle-gold.svg` |
| Framed icon, single-colour charcoal. | `rtam-rdot-icon-circle-charcoal.svg` |
| Framed icon on dark / ceremonial grounds — all gold. | `rtam-rdot-icon-circle-allgold.svg` |
| Browser tab, light chrome (≤ 64 px). | `favicon.svg` |
| Browser tab, dark chrome (≤ 64 px). | `favicon-dark.svg` |
| Anywhere above 64 px — favicon's bindu detaches at scale. | full R-monogram, not the favicon |
| Devanagari-first contexts. | `rtam-devanagari-ri-icon-*.svg` |

---

## 3 · Picking a lockup

| Context | File |
|---|---|
| Default bilingual (website footer, certificate, letterhead). | `rtam-bilingual-foundation.svg` |
| Scholarly / sacred / trust deed. | `rtam-sanskritic-pratishthan.svg` |
| Temple signage, donor materials. | `rtambhareshvara-mandir-lockup.svg` |
| Temple lockup on dark grounds (event banners, night signage). | `rtambhareshvara-mandir-lockup-white-golddot.svg` |
| Donation receipts, fundraising pages, contribution forms. | `donation-lockup.svg` |

---

## 4 · Color rules

- Default ground: **ivory** (`#F7F3E9`).
- Sacred ground: **indigo** (`#1C1A3D`).
- Body text: **charcoal** (`#1A1A1A`).
- Bindu and rules: **gold** (`#C8A15A`) — decorative only. Gold on ivory is 2.18:1, below AA; never body or UI text on ivory. (An AA-passing functional accent is under study — until it ships, functional text and CTAs on ivory are charcoal.)
- **Stone gray** (`#B8B1A4`) is decorative-only on ivory (1.92:1): dividers, oversized folios — never text that must be read. Shipped assets no longer set stone as text; for quiet copy use charcoal at light weight (the donation lockup's pattern).
- The wordmark MUST work in single-colour charcoal `#1A1A1A` — this is the reproduction floor. Charcoal on ivory is 15.7:1 (AAA).
- File-name legend: `-white` = ivory, `-black` = charcoal, `-golddot` = gold bindu preserved on a two-tone mark.

---

## 5 · Type rules

- Display Latin: **Cinzel** 400–700.
- Devanagari: **Tiro Devanagari Sanskrit** (regular).
- Body / UI: **Inter** 300–600.
- Pair Cinzel with Tiro Devanagari Sanskrit. Never pair either with a third display face.
- For headlines: Cinzel 500 with letter-spacing 0.04–0.10 em depending on size.
- For all-caps labels (kickers, metadata): Inter 300, letter-spacing 0.20–0.40 em.

---

## 6 · Clear-space

- **Wordmark:** clear-space = cap-height of R on every side (≈84 viewBox units in the 1080×240 canonical — the measured Cinzel cap-height, not the font-size).
- **R-monogram, ऋ-monogram:** clear-space = ¼ of icon width.
- **Temple lockup:** preserve the full 1280×380 viewBox — no cropping, no letter-spacing reduction.

---

## 7 · The bindu

The bindu is **drawn**, not typed. It is a `<circle>` in the SVG with explicit `cx`, `cy`, and `r`. Do not:

- replace it with the Unicode combining dot below (U+0323),
- shift it independently of the R,
- recolor it independently of the wordmark variant,
- shrink it below `r=10` in the 1080-wide wordmark (it becomes invisible).

Need a different placement? Edit `brand/spec/brand.json` and run `brand/tools/build.sh --write` — never hand-edit the SVG in place. The generator keeps the bindu identical across the whole tree.

Two sanctioned deviations from the placement grammar (and only these): the
**circle-enclosed icons** centre the bindu on the canvas axis so the composition
sits still inside the ring; the **favicon** enlarges the dot and tightens its gap
to survive 16 px tabs. Everything else follows `cy = baseline + 0.233·fs`, `r = fs/12`.

The Devanagari marks (ऋ, ऋतम्…) take **no** bindu — the glyph already carries the vocalic-R.

---

## 8 · What never to do

- Render the wordmark on a busy photo background.
- Outline, emboss, drop-shadow, or gradient the wordmark.
- Recolor the bindu without recoloring the wordmark to match a variant.
- Use the `public-RTAM` (no-bindu) variant when the bindu would reproduce.
- Use the favicon SVG above 64 px.
- Pair the brand with a competing serif display face.
- Add a tagline directly under the wordmark inside its clear-space.
