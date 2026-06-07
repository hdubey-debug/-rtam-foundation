# RTAM Foundation — Brand Book

*ऋतम् फाउंडेशन · ṚTAM Foundation*

---

## 1 · Philosophy

**Ṛtam** (ऋतम्) names the cosmic order that holds — the structuring principle that turns chaos into form, season into return, breath into measure. It is the oldest word the Vedic tradition has for *truth* in the sense of *the way things are*. The foundation takes its name from that word, and its identity from a single mark: a dot beneath the letter R.

The dot is the *bindu* — root, seed, source, the point from which form arises. In the wordmark it sits beneath the R as the diacritic of *ṛ*. It is the brand signature. Without it the wordmark reads "RTAM"; with it the wordmark reads "ṚTAM" — and the foundation's whole claim is in that subtraction and return.

The visual system that follows is built to keep that mark intentional at every scale.

---

## 2 · Names

| Form | Use |
|---|---|
| **ṚTAM Foundation** | Primary written form in Latin-script contexts. Always with the dot under R when typeset; **RTAM Foundation** is the public ASCII fallback. |
| **ऋतम् फाउंडेशन** | Common-register Devanagari. Use in bilingual lockups, Hindi-speaking audiences, signage. |
| **ऋतम् प्रतिष्ठान** | Pure-Sanskritic Devanagari (*pratiṣṭhāna* — "established institution"). For scholarly, sacred, or trust-deed contexts. |
| **Rtambhareshvara Mandir** | The temple. Plain-English Latin form for physical signage and donor materials. |
| **Ṛtambhareśvara Mandir** | The temple, pronunciation form (mixed diacritic: leading Ṛ = R + bindu, native `ś`). Scholarly / sacred register. |
| **ऋतम्भरेश्वर मंदिर** | The temple, Devanagari. Always present in the temple lockup. |

**Spelling lock.** The canonical Latin spellings are exactly as written above —
`RTAM` / `Rtambhareshvara` (and the all-caps `RTAMBHARESHVARA` in the temple
lockup). Do not "correct" them to other IAST transliterations; the diacritic
forms (`Ṛ`, `ś`) are an *additive* register, never a replacement.

---

## 3 · The Logo System

The identity is a **two-entity × two-script tree** bound by one shared root mark.

- **Two entities:** RTAM **Foundation** (the organisation) and **Rtambhareshvara
  Mandir** (the temple).
- **Two scripts:** Latin and Devanagari.
- **One shared crest:** the vocalic-R — **Ṛ** (R + bindu) in Latin, **ऋ** in
  Devanagari — because *both names begin with it* (**Ṛ**TAM, **Ṛ**tambhareshvara).
  The crest names the family; the wordmark names the entity.

Two layout rules fall out of the names: the **Foundation is set horizontally**
(short acronym + smaller descriptor on one baseline); the **Temple is stacked**
(its long name centred over the descriptor). Each entity keeps that structure
across both scripts. **Latin forms carry the gold bindu under the leading R;
Devanagari forms never do** — ऋ already *is* the vocalic-R, so adding a dot would
be redundant. The pieces share no other chrome; what they share is this crest and
the typographic family.

### 3.1 Primary wordmark

The wordmark is the foundation's voice in public. Five variants:

| File | Use |
|---|---|
| `rtam-wordmark-sacred-RTAM-dot.svg` | Canonical. Charcoal letters, gold bindu. |
| `rtam-wordmark-gold.svg` | All-gold. For sacred contexts, embossed printing, dark backgrounds where gold + charcoal won't show. |
| `rtam-wordmark-black.svg` | All-black. For pure-black reproduction (single-color printing, fax, microform). |
| `rtam-wordmark-white.svg` | All-ivory on a **transparent** ground — a true overlay for charcoal, indigo, or photographs. Intentionally invisible on white; always preview on the intended dark surface. |
| `rtam-wordmark-public-RTAM.svg` | ASCII-only, no bindu. **Use only** when the bindu cannot be reliably reproduced (low-resolution sign vinyl, embroidered shirts under 6 cm wide). |

The Foundation name also exists as a **standalone Devanagari wordmark** in both
registers: `rtam-wordmark-devanagari-pratishthan.svg` (ऋतम् प्रतिष्ठान, the
Sanskritic default) and `rtam-wordmark-devanagari-faundeshan.svg` (ऋतम् फाउंडेशन,
the common register). Both set ऋतम् large with the descriptor smaller on a shared
baseline, mirroring the Latin wordmark; neither carries a bindu.

The bindu is **drawn as a separate `<circle>`** in every Latin SVG. It is not a Unicode combining mark. This is deliberate: the bindu must remain exact in size and position across every reproduction surface. Its geometry follows one rule everywhere — centred under the leading R, `cy = baseline + 0.233·fontsize`, `r = fontsize ÷ 12`.

### 3.1a Temple wordmarks

The temple name is set in three standalone renderings, all stacked (name over
descriptor):

| File | Use |
|---|---|
| `rtam-temple-wordmark-latin.svg` | Rtambhareshvara / Temple. Plain English form (signage, donor materials). Leading R carries the bindu. |
| `rtam-temple-wordmark-diacritic.svg` | Ṛtambhareśvara / Mandir. The pronunciation form — leading R + bindu reads as Ṛ, the native Cinzel `ś` carries the palatal sibilant. Scholarly / sacred register. |
| `rtam-temple-wordmark-devanagari.svg` | ऋतम्भरेश्वर / मंदिर. Devanagari, no bindu. |

### 3.2 R-monogram

A square mark of the bare R with the bindu beneath, in two families:

- **Open form** — gold / black / ivory variants for plain-background contexts.
- **Circle-enclosed** — gold ring or all-charcoal, for app icons, social avatars, and any context where the mark needs to claim its own visual territory.

Plus `favicon.svg` (32 viewBox) for browser tabs. The favicon scales cleanly to **64 px**; above that, switch to the full R-monogram SVG, because the bindu spacing was tuned for the favicon's small size and visibly detaches at 8× scale.

### 3.3 Devanagari ऋ monogram

The Devanagari letter *ṛ* (ऋ) is itself the bindu's complement — the glyph carries the sacred mark intrinsically. The ऋ monogram therefore has **no separate dot**. It is the only icon in the system without one, and that absence is the point.

Four variants: gold / black / ivory / circle-enclosed.

### 3.4 Lockups

| File | Use |
|---|---|
| `rtam-bilingual-foundation.svg` | Common-register: ṚTAM Foundation over ऋतम् फाउंडेशन. Default bilingual. |
| `rtam-sanskritic-pratishthan.svg` | Pure-Sanskritic: ṚTAM Foundation over ऋतम् प्रतिष्ठान. Scholarly / sacred. |
| `rtambhareshvara-mandir-lockup.svg` | Temple name, both scripts, leading R carries the bindu. Wider viewBox (1280) to fit the longest name. |
| `donation-lockup.svg` | Wordmark + thin gold rule + a single quiet stone-gray line. Header, not CTA. |

---

## 4 · Color

Seven tokens. Use them by name, not by hex. The CSS variables live in `brand/palette/colors.css`.

| Token | Hex | Role |
|---|---|---|
| `--rtam-gold` | `#C8A15A` | Antique gold. The bindu. Rules and accents. |
| `--rtam-ivory` | `#F7F3E9` | Warm ivory. The default ground. |
| `--rtam-charcoal` | `#1A1A1A` | Near-black. Body text and the wordmark on light grounds. |
| `--rtam-sandstone` | `#E6DED1` | Soft warm gray. Borders, dividers, panel chrome. |
| `--rtam-indigo` | `#1C1A3D` | Sacred-night indigo. Reserved for sacred / poster / cover surfaces. |
| `--rtam-bronze` | `#9B6A2F` | Deeper gold. Use sparingly for emphasis on ivory. |
| `--rtam-stone` | `#B8B1A4` | Quiet stone gray. Supporting copy that should not compete. |

**The wordmark must work in pure black.** This is a non-negotiable reproduction test — every variant of the wordmark has been verified in pure `#1A1A1A` for fax, single-color print, and microform.

**Contrast (measured WCAG ratios).** Charcoal `#1A1A1A` on ivory is 15.9:1 —
the body-text pairing, comfortably AAA. But two warm pairings fall **below** the
4.5:1 AA threshold and are **decorative / large-only**: gold `#C8A15A` on ivory
is **2.18:1**, and stone `#B8B1A4` on ivory is **1.92:1**. Use gold for the bindu,
rules, and large display accents — never for body copy or small UI text on ivory.
For functional text on ivory, use charcoal; reserve stone for quiet captions that
are large enough not to need to be read at a glance.

---

## 5 · Typography

Three faces. Each does one job.

| Face | Use |
|---|---|
| **Cinzel** (400 / 500 / 600 / 700) | Display Latin. The wordmark, headlines, certificate citations, the brand's voice in public. |
| **Tiro Devanagari Sanskrit** (regular) | The sacred face. All Devanagari typesetting. |
| **Inter** (300 / 400 / 500 / 600) | Working sans. Body copy, captions, metadata, anything functional. |

A printable font-installation note for vendors is in `brand/README.md`. SVG glyphs can be outlined in Inkscape (`Path → Object to Path`) or Illustrator (`Type → Create Outlines`) before being sent to a print shop that lacks the fonts.

---

## 6 · Spacing & clear-space

The wordmark gets a clear-space margin equal to the **cap-height of R** on every side. Measured in real Cinzel, that cap-height is ≈**84 viewBox units** in the canonical 1080×240 wordmark (not 120 — the earlier figure mistook the font-size for the cap-height). Nothing — image, fold, type, or border — may enter that zone.

The R-monogram (square icon) gets a clear-space margin equal to ¼ of its width. The Devanagari ऋ monogram uses the same rule.

Lockups inherit their wordmark's clear-space. The temple lockup additionally requires its full 1280-unit viewBox; do not crop or letter-space-reduce the temple name.

---

## 7 · Do & Don't

**Do**

- Place the wordmark on ivory, charcoal, or sacred-night indigo.
- Use the bindu in every reproduction where it is legible (≥ 6 cm wide).
- Pair Cinzel with Tiro Devanagari Sanskrit; pair both with Inter for body.
- Keep the bindu on the Latin marks and off the Devanagari ones.

**Don't**

- Don't move, resize, or recolor the bindu independently of the wordmark. Use a variant file instead.
- Don't substitute the Cinzel R with a different serif. The R's shape is part of the mark.
- Don't render the wordmark on a busy photographic background. Use the ivory, charcoal, or indigo ground.
- Don't outline, emboss, drop-shadow, or gradient the wordmark. The mark is flat. Always.
- Don't add a dot to the Devanagari ऋ marks. The glyph already carries the vocalic-R.
- Don't use the public RTAM (no-bindu) variant when the bindu would reproduce correctly. It exists only as a fallback.
- Don't set gold or stone as body text on ivory — both fall below AA contrast; they are decorative / large-only.

---

## 8 · Applications

The brand kit ships HTML mockups for the most common contexts. See `brand/previews/mockups/` (sources) and `brand/exports/mockups/` (rendered PNGs).

| Mockup | Use |
|---|---|
| `website-header.html` | Web nav with wordmark + nav + Donate CTA. |
| `letterhead.html` | Trust correspondence, formal letters. |
| `donation-receipt.html` | Contribution receipts with 80G reference. |
| `donation-poster.html` | Annual renovation drive poster (1080×1350, sacred-night indigo). |
| `instagram-avatar.html` | Three avatar variants for social platforms. |
| `youtube-banner.html` | 2560×1440 with explicit mobile-safe area. |
| `certificate.html` | Certificate of Contribution with the bilingual lockup. |
| `favicon-scale-test.html` | Browser-tab favicon at 16–256 px. |

---

## 9 · Files at a glance

```
brand/
├── spec/brand.json                     # the asset tree as data — SINGLE SOURCE OF TRUTH
├── palette/colors.{json,css}           # design tokens
├── logos/rtam-wordmark-*.svg           # 5 Latin Foundation wordmark variants
├── logos/rtam-wordmark-devanagari-*.svg# 2 Devanagari Foundation wordmarks (pratishthan, faundeshan)
├── logos/rtam-temple-wordmark-*.svg    # 3 temple wordmarks (latin, diacritic, devanagari)
├── icons/rtam-rdot-icon-*.svg          # 5 R-monogram variants (open + circle)
├── icons/rtam-devanagari-ri-icon-*.svg # 4 ऋ monogram variants
├── icons/favicon.svg                   # 32 viewBox favicon
├── lockups/*.svg                       # 4 lockup compositions
├── previews/index.html                 # master gallery
├── previews/{wordmark,monogram,devanagari-monogram,lockups}-specimen.html
├── previews/mockups/*.html             # application mockups
├── guidelines/{brand-book,usage-rules}.md
├── tools/brandlib.py + generate.py + outline.py + parity.py + build.sh
│                                       # generator: brand.json → source SVGs + outlined masters + gate
├── tools/render_*.py                   # SVG→PNG, HTML→PNG/PDF, MD→PDF
├── dist/outlined/*.svg                 # built distribution masters (gitignored; `build.sh --write`)
└── exports/{png,pdf,mockups}/          # rendered outputs
```

**Editing the kit:** change `brand/spec/brand.json`, then run `brand/tools/build.sh --write`.
Hand-editing the SVGs is no longer the workflow — the generator regenerates every
source SVG and outlined master from the spec, and the parity gate proves fidelity.
This is what keeps the bindu (and every other coordinate) identical across the
whole tree.

---

*The work continues steadily, in keeping with the order it intends to serve.*

— **ऋतस्य पन्थाम्**
