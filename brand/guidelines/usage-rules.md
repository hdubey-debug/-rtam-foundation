# RTAM Foundation — Usage Rules

Quick reference. For the full rationale see `brand-book.md`.

---

## 1 · Picking a wordmark

| Context | File |
|---|---|
| Default. Anywhere the bindu reproduces. | `rtam-wordmark-sacred-RTAM-dot.svg` |
| Sacred surface, embossed, foil, single-color gold print. | `rtam-wordmark-gold.svg` |
| Pure-black reproduction (fax, microform, single-color). | `rtam-wordmark-black.svg` |
| Any dark ground (charcoal / indigo / photo). Transparent overlay — invisible on white. | `rtam-wordmark-white.svg` |
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
| Square app icon, social avatar, charcoal R. | `rtam-rdot-icon-gold.svg` |
| Dark theme, ivory R + gold bindu. | (use `-gold` on charcoal ground) |
| App icon needing visual frame. | `rtam-rdot-icon-circle-gold.svg` |
| Pure-black version of the framed icon. | `rtam-rdot-icon-circle-charcoal.svg` |
| Browser tab (≤ 64 px). | `favicon.svg` |
| Anywhere above 64 px — favicon's bindu detaches at scale. | full R-monogram, not the favicon |
| Devanagari-first contexts. | `rtam-devanagari-ri-icon-*.svg` |

---

## 3 · Picking a lockup

| Context | File |
|---|---|
| Default bilingual (website footer, certificate, letterhead). | `rtam-bilingual-foundation.svg` |
| Scholarly / sacred / trust deed. | `rtam-sanskritic-pratishthan.svg` |
| Temple signage, donor materials. | `rtambhareshvara-mandir-lockup.svg` |
| Donation receipts, fundraising pages, contribution forms. | `donation-lockup.svg` |

---

## 4 · Color rules

- Default ground: **ivory** (`#F7F3E9`).
- Sacred ground: **indigo** (`#1C1A3D`).
- Body text: **charcoal** (`#1A1A1A`).
- Bindu and rules: **gold** (`#C8A15A`) — decorative only. Gold on ivory is 2.18:1, below AA; never body text.
- Quiet supporting copy: **stone gray** (`#B8B1A4`) — large captions only. Stone on ivory is 1.92:1, below AA.
- The wordmark MUST work in pure `#1A1A1A` — this is the reproduction floor. Charcoal on ivory is 15.9:1 (AAA).

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
