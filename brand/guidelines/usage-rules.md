# RTAM Foundation — Usage Rules

Quick reference. For the full rationale see `brand-book.md`.

---

## 1 · Picking a wordmark

| Context | File |
|---|---|
| Default. Anywhere the bindu reproduces. | `rtam-wordmark-sacred-RTAM-dot.svg` |
| Default on dark grounds (charcoal / indigo / photo) — the sacred form with the gold bindu preserved. Transparent overlay, invisible on white. | `rtam-wordmark-ivory-golddot.svg` |
| Sacred surface, embossed, foil, single-color gold print. | `rtam-wordmark-gold.svg` |
| Single-colour charcoal reproduction (fax, microform, mono print). | `rtam-wordmark-charcoal.svg` |
| Dark ground where a second colour (gold) cannot reproduce — all-ivory overlay. | `rtam-wordmark-ivory.svg` |
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
| Dark theme (ivory R, gold bindu). | `rtam-rdot-icon-ivory-golddot.svg` |
| Warm / ceremonial all-gold mark on light grounds. | `rtam-rdot-icon-gold.svg` |
| Single-colour charcoal (mono print, stamps). | `rtam-rdot-icon-charcoal.svg` |
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
| Temple lockup on dark grounds (event banners, night signage). | `rtambhareshvara-mandir-lockup-ivory-golddot.svg` |
| Donation receipts, fundraising pages, contribution forms. | `donation-lockup.svg` |

---

## 4 · Color rules

- Default ground: **ivory** (`#F7F3E9`).
- Sacred ground: **indigo** (`#1C1A3D`).
- Body text: **charcoal** (`#1A1A1A`).
- Bindu and rules: **gold** (`#C8A15A`) — decorative only. Gold on ivory is 2.18:1, below AA; never body or UI text on ivory. (An AA-passing functional accent is under study — until it ships, functional text and CTAs on ivory are charcoal.)
- **Stone gray** (`#B8B1A4`) is decorative-only on ivory (1.92:1): dividers, oversized folios — never text that must be read. Shipped assets no longer set stone as text; for quiet copy use charcoal at light weight (the donation lockup's pattern).
- The wordmark MUST work in single-colour charcoal `#1A1A1A` — this is the reproduction floor. Charcoal on ivory is 15.7:1 (AAA).
- File-name legend (v2, token-truthful): `-ivory` = ivory, `-charcoal` = charcoal, `-garbhagriha` = bhasma ash on mahakala, `-golddot` = gold bindu preserved on a two-tone mark.

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

Three sanctioned deviations from the placement grammar (and only these): the
**circle-enclosed icons** centre the bindu on the canvas axis so the composition
sits still inside the ring; the **favicon** enlarges the dot and tightens its gap
to survive 16 px tabs; the **stationery support line** (the small Cinzel caps in
the Devanagari-led lockup) enlarges its dot to `r = fs/8` — at fs/12 the dot
prints as 0.3 mm dust at letterhead scale. Everything else follows
`cy = baseline + 0.233·fs`, `r = fs/12`.

The Devanagari marks (ऋ, ऋतम्…) take **no** bindu — the glyph already carries the vocalic-R.

**The one gold (stationery ruling, 2026-08-26).** The dot under the R and the
hub of the chakra are the same point (brand-book v2.2). On any single page
they count as ONE gold in two renderings: a head may carry the chakra's gold
hub and the wordmark's gold bindu together. A third gold instance remains a
violation.

---

## 8 · What never to do

- Render the wordmark on a busy photo background.
- Outline, emboss, drop-shadow, or gradient the wordmark.
- Recolor the bindu without recoloring the wordmark to match a variant.
- Use the `public-RTAM` (no-bindu) variant when the bindu would reproduce.
- Use the favicon SVG above 64 px.
- Pair the brand with a competing serif display face.
- Add a tagline directly under the wordmark inside its clear-space.

---

## 9 · v2 addenda (2026-07-12 — the Ṛtāmbhareśvara system)

The icon system and substance palette are governed by brand-book §v2.
Additional hard rules:

**The icon.**
- Never scale the ṛta-chakra below 48 px — step down the sanctity
  ladder instead (anāhata for community surfaces, bindu below 48 px).
- Never rotate the icon: one petal points due north, always.
- Never recolor parts independently: use the four shipped cuts —
  `rtam-chakra-garbhagriha` (dark surfaces), `-day` (light), `-kanaka`
  (festival), `-mono` (single-ink) — plus the matching anahata/bindu.
- The hub is the only gold inside the icon except in kanaka. Never
  gild the petals outside the kanaka cut.

**Grounds (v2).**
- Dark surfaces are **mahakala `#141414`** — never indigo (retired
  2026-07-12), never pure `#000000`.
- Reading surfaces are **chandra `#EDEBE6`** — warmIvory grounds and
  sandstone panels are retired; legacy assets only.
- On mahakala: display type gold, body text bhasma; links gold. On
  chandra: ink text, tāmra links/CTAs; gold is decorative only.

**Voices.**
- Every entity/script voice has a `-garbhagriha` cut for dark
  surfaces; never place the charcoal cuts on mahakala.
- City print leads Devanagari (≥ 2× its English support line); web
  leads English.

**Favicon.**
- `favicon.svg` / `favicon-dark.svg` are the **bindu** (since P3.4).
  Never use a typographic R below 48 px.

**Stationery (2026-08-26 — the temple's hand; garbhagriha ruling 2026-08-27).**
- **THE letterhead is the garbhagriha edition** (founder-locked after four
  printed rounds): inset mahakala bands — never full-bleed (printer rims
  cheapen the black) — the V3-L śulba head (icon : name-block : gap =
  13 : 12 : 5, left lane), ash marks, ONE gold: the chakra's hub (kansya was
  print-tested and rejected — it dries brown). Single-ink reproduction uses
  the **night-ivory knockout cuts** (marks read as paper out of the band).
  The receipt leaf and book cover speak the same language. The chandra
  (cream) editions remain the day alternative.
- **Rubber stamps use the sanctioned seal artwork** (`seal-chakra-round` /
  `seal-chakra-rect` / `address-stamp` in the spec). The full chakra goes to
  rubber ONLY in its **thickened stamp edition** (founder ruling 2026-08-27):
  seams and window dots redrawn above the 0.5 mm rubber floor, at Ø ≥ 50 mm
  round or 60×40 rect. The screen chakra's 0.34 mm seams never go to rubber;
  the bindu rung remains the fallback for smaller dies.
- **Mail numerals:** on mail-facing artifacts — labels, address stamps,
  envelopes — figures are set in international numerals (483001) and the post
  town appears in Latin block letters (BARELA). Devanagari digits remain
  welcome on the round seal and anything that never enters the post.
- **City-print temple voice:** `rtambhareshvara-mandir-lockup-devanagari-led`
  (Devanagari 3× over Cinzel caps, stone rule, no bindu, no gold — the page's
  gold belongs to the chakra hub). Cuts: default · `-garbhagriha` ·
  `-charcoal` (single-ink reproduction floor).
- **Paper is the chandra:** reading stationery is bought cream stock (BILT
  Royal Executive Bond "Corona Cream" 100 gsm; Conqueror Cream Wove 100 gsm
  formal) — the ground is never printed. No watermark on working sheets;
  ceremony gets foil + blind emboss.
- **The bilingual doctrine — labels echo, scripture doesn't.** Every
  structural label (field names, tick options, serial rows, box captions)
  is bilingual: Devanagari leads, a small letterspaced English echo sits
  beneath or beside it. Sacred and ritual lines (ऋतस्य पन्थाम्, invocations)
  stay Devanagari alone — the temple speaking in its own tongue. Devanagari
  is never letterspaced. The support line inside the Devanagari-led lockup is
  a Latin form and carries the gold bindu under its leading R (§7, third
  deviation).
- **One address, one rule: the FULL pair, everywhere human-facing** (founder
  ruling 2026-08-27 — "every single thing" readable in both scripts): the
  Devanagari line AND the full Latin caps line (which carries the postal
  `BARELA (M.P.) – 483001`, G4). The earlier compact form is retired. The
  founders' line pairs the same way (संस्थापक — … / FOUNDERS — SHRI RAJESH
  DUBEY · SMT. KIRAN BALA DUBEY). One recorded de-minimis exception: the
  rubber stamps' मो. label (digits are script-neutral).
- **One hero edition per artifact** in any presentation: the mono edition is
  the same sheet's photocopy-safe shadow, shown as an appendix, never as a
  sibling design.
