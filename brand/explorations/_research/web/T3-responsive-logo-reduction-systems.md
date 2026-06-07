# T3 — Responsive / reductive logo systems: the reduction-tier spec for the ṛta-wheel cosmogram

Research track T3 for the RTAM Phase-2 logo exploration. Question: what is the state of the
art in multi-tier "responsive" / reductive logo systems (full → simplified → glyph), how do
complex emblems (seals, crests, mandalas) survive favicon scale, and what concrete reduction
tiers + 16px design rules must each exploration concept ship?

Scope note on sources: the strongest *primary* sources here are published brand-center pages
(Cornell, Johns Hopkins) and design-system docs (Material Design). A lot of the "responsive
logo" literature is secondary agency-blog commentary on one seminal student/portfolio project
(Joe Harrison, 2014); I flag where a claim rests only on secondary commentary. Several pages
(Johns Hopkins brand center 403'd; Material m2 page returned an empty body to the fetcher) I
could not read directly and instead corroborate from a second source — flagged inline. No
2026-specific hard numbers are invented; where I could not confirm a current figure I say so.

---

## Findings

### F1 — The canonical responsive-logo system is a 3–4 tier ladder, not a single scalable file
The repeatedly-described professional structure is a **tiered kit**: Master/primary lockup
(full detail) → Secondary (no tagline / reduced) → Compact or stacked → **Brand mark / glyph**
(icon-only, for favicons and small UI). Each tier is a *separate, redrawn asset*, not the same
artwork scaled. Complexity is removed deliberately as the display area shrinks — "strategic
omission" / "strategic simplification," described as a functional requirement, not a stylistic
one.
- https://inkbotdesign.com/responsive-logo-design/
- https://www.akrivi.io/learn/4-logo-variations
- https://clay.global/blog/responsive-logo-design

### F2 — The seminal precedent (Joe Harrison, "Responsive Logos," 2014) reduces each mark to ONE atomic feature
Harrison's project applies responsive-web principles to the *logo itself*: as the viewport
shrinks the mark sheds elements in discrete steps until only the smallest still-recognizable
feature survives — Chanel's interlocking C's, the Guinness harp, Nike's swoosh, Disney's "D".
Implementation: SVG sprites packaged with CSS rules + media queries in one encapsulated SVG, so
the *display size selects the tier*. The exact breakpoints/px per tier are not published on the
project pages I could reach (responsivelogos.co.uk and joeharrison.co.uk render the steps
interactively rather than documenting them) — so "how many tiers" is brand-specific, but the
*end state is consistently a single hub element*. (Primary concept; tier counts = secondary.)
- https://responsivelogos.co.uk/
- https://imjustcreative.com/responsive-logo-designs/2019/10/17
- https://graphicartistsguild.org/making-brands-or-at-least-their-logos-responsive/

### F3 — Complex emblems survive by shipping TWO marks: a ceremonial full seal and a redrawn simplified seal (Cornell, Northeastern)
This is the most load-bearing finding for a mandala/cosmogram brand. Universities with
centuries-old seals did **not** make one seal scale; they bifurcated:
- **Cornell:** the *Great Seal* (2-inch ceremonial medallion, double outlines, Ezra Cornell
  portrait + full inscription) is reserved for inaugurations. A separate **simplified seal**
  was created for online/branding use — reportedly "identical to the main seal but does **not**
  have double outlines — all elements consist of single lines," with a stated cap that **digital
  use must not exceed ~120 px**. A still-simpler shield mark carries everyday/decorative
  branding. (The single-line detail and the 120px cap come from the search index summarizing the
  Cornell brand-center pages, not from a page I fetched directly — treat the *bifurcation
  pattern* as confirmed and the exact 120px number as unverified.)
  - https://alumni.cornell.edu/cornellians/seal-emblem/
  - https://brand.cornell.edu/logos/
  - https://president.cornell.edu/the-presidency/symbols/
- **Northeastern (Upstatement):** the iconic seal was **redrawn for legibility and balance**
  and "key elements elevated" so the identity expands across platforms — i.e. the seal was
  re-mastered for digital, not shrunk. (The case-study page confirms the redraw-for-legibility
  intent; it does not publish the per-size mechanics.)
  - https://upstatement.com/case-study/northeastern-brand

Takeaway: an emblem at favicon scale is a *redraw problem, not a scaling problem*. The full
ring-of-12 + portrait/inscription does not reduce; a single-line variant with a hard upper px
cap does, and below that you switch to a different (hub) mark entirely.

### F4 — Favicons must be designed UP from 16px, never shrunk down; redraw is expected and sanctioned
Consistent across favicon-specific sources: the classic mistake is designing at 512 and scaling
down. Instead, work *within* a 16×16 / 32×32 grid from the start and add detail as size allows.
"Conventional wisdom says logos should be reproduced exactly, but when reduced to 32×32 or 16×16
some leeway in interpretation is necessary; ideally you would design a separate logo for each
resolution." At 16px: 1–2 characters max if any text, 1–3 colors, no gradients, basic geometry
only, remove taglines/decorative detail. A line that falls *between* pixels blurs; a circle off
the grid becomes "an uneven blob."
- https://www.premiumfavicon.com/blog/how-to-make-favicon-from-logo
- https://evilmartians.com/chronicles/how-to-favicon-in-2021-six-files-that-fit-most-needs

### F5 — Construction-grid / keyline numbers from the dominant icon system (Material Design)
The de-facto reference grid for system icons (corroborated across the Material docs and a
secondary keyline survey, since the m2 page itself returned no body to the fetcher):
- Canvas **24×24 dp**, drawn at 100% for pixel accuracy.
- **Live area 20×20 dp**, i.e. **2 dp padding** on every side (padding = stroke weight).
- **Stroke weight 2 dp**, consistent on curves, angles, interior and exterior.
- Keyline shapes (circle / square / portrait + landscape rectangle) anchor element sizing.
- **Pixel-snap** strokes to whole-px increments; for a 1px stroke, offset by 0.5px so the
  stroke straddles a pixel boundary cleanly; for 1.5px strokes align the outer edge to the
  grid. (Pixel-snapping matters most at small sizes; one survey notes it has *relaxed*
  somewhat as rendering improved, but it is still the rule at 16px.)
- **At 16px specifically: reduce the level of detail**; use ~1–2px corner radius so small
  shapes aren't over-rounded.
- https://m2.material.io/design/iconography/system-icons.html
- https://m3.material.io/styles/icons/designing-icons
- https://minoraxis.medium.com/icon-grids-keylines-demystified-5a228fe08cfd
- https://uxdesign.cc/pixel-snapping-in-icon-design-a-rendering-test-6ecd5b516522

### F6 — Optical-size compensation: small marks need heavier strokes, lower contrast, wider counters, looser spacing
The type-design principle that transfers directly to a reductive mark: smaller optical sizes
are drawn with **thicker/robust strokes, reduced thin-to-thick contrast, wider counters/larger
openings, increased width, and looser spacing**; fine detail is "simplified and exaggerated to
maintain the impression" of the form. (Caption/SmText vs Display masters in variable fonts.)
This is *not* the same artwork at a smaller point size — the small master is a different drawing.
The literature is explicit that there are **no universal numeric thresholds** (it's "art and
science"); the numbers must be eye-tuned per form.
- https://www.monotype.com/resources/articles/what-is-optical-sizing-and-how-can-it-help-your-brand
- https://blazetype.eu/blog/optical-size/
- https://typenetwork.com/articles/inside-the-fonts-optical-sizes
- https://developer.mozilla.org/en-US/docs/Web/CSS/font-optical-sizing

### F7 — A mandala/wheel's legibility budget is set by its spoke/petal count; even counts (4/6/8/12) read as stable wheels but 12 is near the small-scale ceiling
Mandala design guidance: shapes repeat around a central dot "like a bicycle wheel where spokes
radiate from the hub"; 4/6/8/12 are the canonical divisions, with 4 reading "stable and
directional" and 8/12 reading "intricate, like wheels with many spokes." The reductive
implication: at small scale a 12-fold ring is at the busy end — it must shed spokes/petals (to a
lower-count ring, then to bare hub) rather than try to keep all 12 readable. General small-scale
reduction guidance independently quantifies the stakes: marks at 32px and below lose a large
share of visual complexity, so the wheel cannot rely on its 12 medallions surviving.
- https://99designs.com/inspiration/logos/mandala
- https://symbolsage.com/mandala-symbols-and-colour-meanings/
- https://rabbitlogo.com/scalable-logo-design/

### F8 — The 2025–2026 favicon delivery set (so the glyph tier ships as real files, not a guideline)
The current recommended favicon bundle (Evil Martians, widely cited; numbers stable through the
2024–2026 updates I could see):
- `favicon.ico` — **32×32** (legacy).
- `icon.svg` — single vector, with an embedded `<style>` using
  `@media (prefers-color-scheme: dark)` to swap fill for dark UI.
- `apple-touch-icon.png` — **180×180**.
- `icon-192.png`, `icon-512.png` — PWA / Android.
- `icon-mask.png` (maskable) — **512×512 canvas with a 409×409 central safe zone** (the launcher
  may crop to a circle/squircle; nothing essential outside 409). Verify on maskable.app.
- `manifest.webmanifest` ties them together.
- https://evilmartians.com/chronicles/how-to-favicon-in-2021-six-files-that-fit-most-needs

---

## Implications for RTAM

The Phase-2 brief is a **ṛta-wheel cosmogram** encoding shivling + lotus + 12-medallion temple
architecture — i.e. exactly the "complex emblem that dies at favicon scale" class (F3, F7). The
repo *already has direct evidence of this failure*: `F9-seal-geometry.md` documents that the
current 12-medallion seal "collapses below ~96px" because beads straddle the ring and the hub is
only 1.25× a bead. T3's job is to make sure each cosmogram concept is born as a **tier ladder**
so it never lands in that collapse zone.

1. **Every cosmogram concept must ship three redrawn tiers, not one scalable file** (F1, F2, F4).
   For RTAM:
   - **T-Full — full cosmogram** (≥ ~96–512px / print): shivling axis + lotus petals + 12
     medallions + outer ring + hub. This is the *ceremonial* tier, analogous to Cornell's Great
     Seal — it is allowed to be detailed because it never renders tiny.
   - **T-Simplified — simplified wheel** (~24–96px): single-line ring, **petal/medallion count
     dropped from 12 to a lower even count** (8, 6, or 4 — eye-test which still reads as "the
     wheel"; F7), no shivling interior modeling, hub promoted. This is Cornell's "single-line
     seal, ≤120px digital" analog and is the tier most app/social/header contexts actually use.
   - **T-Glyph — hub glyph** (≤16–24px / favicon): the **single atomic element only** (F2). The
     natural RTAM atom is the **bindu-in-hub** (the brand's existing signature gold dot) or the
     ऋ monogram — *not* a shrunk wheel. The ring and all petals are gone.

2. **The atom is already decided by the brand, and it resolves the redesign tension.** The memory
   notes an open question — "promote ऋ to system anchor" vs. "bindu as negative space" vs. fuse
   R+ऋ. T3 says: whatever the full cosmogram looks like, **its T-Glyph tier must be a mark the
   brand already owns** (bindu / ऋ / R), because F2/F4 require the favicon to be a deliberate
   small drawing, and the bindu is the one element guaranteed to read at 16px. This makes the
   hub-glyph the *spine* the three full-concept directions must each terminate in.

3. **The favicon is a hard switch, not a continuous shrink** (F3, F4). Reaffirm and generalize
   the existing rule (`usage-rules.md §2`: "favicon's bindu detaches at scale… above 64px use the
   full R-monogram"). The cosmogram inherits a **tier-switch rule**: full cosmogram never below
   its min-clear-size; simplified wheel in the mid band with a hard upper px cap on its small
   variant; hub-glyph only at/below the favicon band. Pin the band boundaries to the F9 evidence
   (~96px) rather than guessing.

4. **16px design rules the cosmogram concepts must obey** (F4, F5, F6) — concrete, eye-tuned:
   - Design the T-Glyph **up from a 16×16 grid**, then derive 32 and larger — never down from the
     full cosmogram.
   - **Pixel-snap** every stroke; the hub bindu must sit on whole-px center; the ring (if any
     survives in the simplified tier) must be an even stroke width snapped to the grid.
   - **Optical compensation:** the small tiers carry **heavier strokes and a larger hub** than a
     naive scale-down — F9 already found the hub needs to be ≥ ~1.5–1.6× the bead to read as
     center; T3 says push that ratio *further* in the small tiers, and thicken the ring stroke
     relative to its full-tier proportion (F6: small masters are heavier, lower-contrast).
   - **Color:** 1–3 colors, no gradients at glyph scale; respect the brand's contrast floor —
     the gold bindu at glyph scale must sit on charcoal/indigo (gold-on-ivory is 2.18:1,
     decorative-only per the contrast rules), or be charcoal.
   - **Count budget:** do not attempt 12 medallions below ~96px; the simplified tier drops to an
     even lower count, the glyph tier drops the ring entirely (F7).

5. **Ship the glyph tier as real favicon files** (F8): each concept that reaches finalist stage
   owes an `icon.svg` (with `prefers-color-scheme` dark swap), `favicon.ico` 32×32, the 180/192/
   512 PNGs, and a maskable `icon-mask.png` keeping the hub inside the 409/512 safe zone. The
   existing `brand/icons/favicon.svg` is already a 32×32 viewBox — the cosmogram glyph slots into
   that contract.

---

## Implied repo changes   (mandatory, concrete)

### A) Rule to add to `brand/guidelines/usage-rules.md`
Add a new section **"§10 · Reduction tiers (responsive logo)"** establishing the 3-tier contract
for any emblem/cosmogram mark (and retro-fitting the existing seal + favicon to name their tier):

> Every emblem mark ships **three redrawn tiers**, selected by render size — not one file scaled:
> - **Full** (≥ 96 px / print): full detail. Never rendered below its min-clear-size.
> - **Simplified** (24–96 px): single-line ring, reduced petal/medallion count (≤ 8), promoted
>   hub. Hard upper px cap on the smallest simplified variant.
> - **Glyph** (≤ 24 px / favicon): the hub atom only (bindu or ऋ) — no ring, no petals.
> Switching tiers is a **hard swap at the band boundary**, not a continuous shrink. Designing a
> small tier by scaling the full mark down is prohibited; small tiers are drawn up from a 16×16
> grid and pixel-snapped.

**Conflict to resolve, not average (CLAUDE.md Rule 8).** §2 currently sets the existing
bindu-favicon boundary at **64 px** ("above 64 px use the full R-monogram"), while these proposed
cosmogram bands are **24 px (glyph) / 96 px (full)** — pinned to the F9 ~96px collapse evidence. A
48 px render is "favicon" under §2 but "simplified wheel" under §10, and §2's 64px has no home in
the new scheme. Do **not** silently blend them: either (a) the cosmogram uses its own 24/96 bands,
distinct from the bindu-favicon's 64px, or (b) re-pin §2's 64px to the same eye-tested boundaries.
Recommend (a) for now (the cosmogram is a different mark with a different collapse point), with a
single-source-of-truth pass deferred until the band boundaries are eye-tested on a real concept.

### B) Asset spec to add to the deliverables list (the per-concept exploration requirement)
Each ṛta-wheel **exploration concept must deliver a tier triplet + favicon bundle** before it can
be scored:
- `*-cosmogram-full.svg` (full tier, with `<desc>` recording the 12-medallion/shivling/lotus
  encoding).
- `*-wheel-simplified.svg` (mid tier; single-line ring; documented reduced count).
- `*-hub-glyph.svg` (glyph tier; hub atom only) **plus** the F8 favicon bundle:
  `icon.svg` (with `@media (prefers-color-scheme: dark)`), `favicon.ico` 32×32,
  `apple-touch-icon.png` 180, `icon-192.png`, `icon-512.png`, maskable `icon-mask.png`
  (hub inside 409/512 safe zone).
- A **`*-reduction-strip.png`** proof: the three tiers rendered side-by-side at their target
  sizes (e.g. 256 / 64 / 16 px), analogous to the existing `proofs/` strips, so the eye-check
  gate (US-10.3) can confirm each tier reads at size.

### C) Rubric criterion + scoring anchor for `brand/explorations/_rubric/rubric.md`
(Create the file if absent; the brief mandates referencing this path.) Add criterion
**"Reduces (3-tier survival)":**
- **0 — fails:** single artwork that just scales; ring + 12 medallions still present at 16px;
  collapses into a blob (repeats the F9 seal failure).
- **3 — partial:** distinct full and glyph tiers exist, but the glyph is a shrunk wheel rather
  than a redrawn hub atom, or the simplified tier still carries all 12 elements.
- **5 — passes:** three deliberately-redrawn tiers; glyph tier is a brand-owned hub atom (bindu /
  ऋ) legible at 16px on the contrast-safe ground; simplified tier uses ≤ 8 elements; favicon
  bundle present; reduction-strip proof reads cleanly at 256/64/16 px with pixel-snapped strokes.

### D) Risk to log
- **R-T3-1 — "cosmogram dies at favicon scale" (repeat of F9):** the 12-medallion + shivling +
  lotus density is at the small-scale ceiling (F7); a concept that omits a real hub-atom glyph
  tier will be illegible below ~96px exactly as the current seal is (F9). *Mitigation:* gate every
  concept on the 3-tier triplet (B) and the rubric "Reduces" criterion (C); pin the band boundary
  to the measured ~96px, not a guess.
- **R-T3-2 — gold-on-ivory glyph illegibility:** the hub atom is the gold bindu; gold-on-ivory is
  2.18:1 (decorative-only per the contrast rules). A favicon placing the gold hub on an ivory/
  light browser-tab ground fails. *Mitigation:* glyph tier defaults to charcoal hub, or gold hub
  on charcoal/indigo ground only; encode the dark-mode swap in `icon.svg` via
  `prefers-color-scheme` (F8).

---

## Sources

Primary / authoritative:
- Cornell University — seal history & ceremonial vs. simplified use: https://alumni.cornell.edu/cornellians/seal-emblem/ · https://brand.cornell.edu/logos/ · https://president.cornell.edu/the-presidency/symbols/
- Northeastern University brand (Upstatement) — seal redrawn for legibility: https://upstatement.com/case-study/northeastern-brand
- Johns Hopkins primary logo / minimum-size brand page (referenced; page 403'd to the fetcher, corroborated via search index): https://brand.jhu.edu/visual-identity/primary-logo/
- Material Design — system-icon construction grid / keylines: https://m2.material.io/design/iconography/system-icons.html · https://m3.material.io/styles/icons/designing-icons
- MDN — `font-optical-sizing`: https://developer.mozilla.org/en-US/docs/Web/CSS/font-optical-sizing
- Monotype — optical sizing for brands: https://www.monotype.com/resources/articles/what-is-optical-sizing-and-how-can-it-help-your-brand
- Type Network — optical sizes inside fonts: https://typenetwork.com/articles/inside-the-fonts-optical-sizes
- Evil Martians — modern favicon delivery set (sizes, SVG dark-mode, maskable 409/512): https://evilmartians.com/chronicles/how-to-favicon-in-2021-six-files-that-fit-most-needs

Seminal concept (primary project pages) + secondary commentary:
- Joe Harrison — Responsive Logos: https://responsivelogos.co.uk/ · https://mail.joeharrison.co.uk/projects/responsivelogos.html · https://imjustcreative.com/responsive-logo-designs/2019/10/17 · https://graphicartistsguild.org/making-brands-or-at-least-their-logos-responsive/

Practitioner / secondary (corroborating, dated where shown):
- Responsive-logo tier kit: https://inkbotdesign.com/responsive-logo-design/ · https://www.akrivi.io/learn/4-logo-variations · https://clay.global/blog/responsive-logo-design
- Favicon redraw / pixel-grid: https://www.premiumfavicon.com/blog/how-to-make-favicon-from-logo
- Icon keylines / pixel-snapping: https://minoraxis.medium.com/icon-grids-keylines-demystified-5a228fe08cfd · https://uxdesign.cc/pixel-snapping-in-icon-design-a-rendering-test-6ecd5b516522
- Optical size (type foundry): https://blazetype.eu/blog/optical-size/
- Mandala/wheel structure & small-scale: https://99designs.com/inspiration/logos/mandala · https://symbolsage.com/mandala-symbols-and-colour-meanings/ · https://rabbitlogo.com/scalable-logo-design/

Repo cross-references (not web): `brand/explorations/_research/fix-specs/F9-seal-geometry.md` (seal collapses < ~96px; hub/bead hierarchy), `brand/guidelines/usage-rules.md` §2 (favicon bindu detaches > 64px) and §4 (gold-on-ivory 2.18:1 decorative-only), `brand/icons/favicon.svg` (32×32 viewBox).
