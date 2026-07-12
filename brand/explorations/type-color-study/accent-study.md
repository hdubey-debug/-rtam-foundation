# Phase-1 Type & Colour Study — findings

*Companion to `type-color-study.html` (render it; every claim below was
eye-checked on that page). Numbers are measured WCAG 2.x ratios via
`tools/contrast.py` math. These are Phase-1 **recommendations**; the palette
canon does not change until Phase-3 convergence.*

## A · Type — the mixed-case question

| Face | Verdict |
|---|---|
| **Cinzel** | Keeps the public, lapidary ALL-CAPS voice — the wordmark stays Cinzel. Confirmed: it has no true lowercase (small-caps substitution), so it cannot set *Ṛtam* or sentence-case headings. Composed Ṛ (R + U+0323) renders correctly. |
| **Marcellus** | **Recommended mixed-case display face.** Already vendored as the reserve; Trajan-adjacent skeleton so it reads as Cinzel's sibling, with true lowercase and clean Ṛ/ś marks. Promotion from "fallback only" to "sentence-case display" is a Phase-3 doc change, zero new dependencies. |
| Cormorant / EB Garamond | Elegant but bookish; smaller apparent size at equal em; would import a second voice. Keep as outside references only. |
| Tiro Latin | Strong slab-serif presence; see B. Not a display face. |

**Rule sketch (for Phase 3):** Cinzel = ceremonial caps (wordmarks, lockups,
certificate headings). Marcellus = mixed-case display (page titles, *Ṛtam* in
running heads). Inter = body/UI. Never three display faces in one composition.

## B · The Tiro-Latin embrace

Side-by-side (Tiro+Tiro vs Tiro+Inter vs Tiro+Cormorant): the Tiro Latin
glyphs share the Devanagari's weight, contrast and terminal logic — the
bilingual card reads as ONE typographic voice, where Inter reads as caption
and Cormorant as decoration. **Recommendation: sanction Tiro's built-in Latin
for bilingual quote/scripture settings only** (Devanagari present in the same
block). Standalone Latin body remains Inter. This legalizes exactly the
"unsanctioned fourth face" the audit caught leaking into
`website-header.html` — the bug becomes the rule, scoped.

## C · Colour — accents with measured ratios

Requirement: a functional accent legible as text on BOTH light surfaces.

| Candidate | on ivory | on sandstone | on indigo | on charcoal | Role verdict |
|---|---|---|---|---|---|
| gold `#C8A15A` (canon) | 2.18 | 1.81 | **6.88** | **7.21** | decorative on light; **functional accent on dark** |
| bronze `#9B6A2F` (canon, unused) | 4.21 | 3.49 | — | — | superseded below |
| minimal-shift bronze `#94652D` | 4.56 | 3.78 | — | — | rejected — fails sandstone |
| **deep bronze `#7A5423`** | **6.07** | **5.04** | 2.47 | — | **recommended functional accent on light** |
| kumkum vermilion `#C41E3A` | 5.27 | 4.38 | 2.84 | — | ceremonial accent on light (festivals, utsava) |
| deep kumkum `#9E1B32` | 7.13 | 5.92 | 2.10 | — | kumkum's small-text fallback |
| flame-ember `#D98E32` | 2.41 | 2.00 | **6.22** | 6.52 | ceremonial accent on dark (the lamp register) |

**The two-accent rule that falls out:** on light grounds, gold ornaments and
deep bronze speaks (links, CTAs, emphasis); on dark grounds they trade places —
gold speaks (it clears AA on indigo and charcoal) and nothing else is needed.
Ceremonial registers get kumkum (light) / flame-ember (dark), used the way the
temple uses them: on festival material, never in UI chrome.

**Phase-3 canon proposal:** re-point the `bronze` token from `#9B6A2F` (defined
but consumed nowhere) to `#7A5423`, rename-truthfully in the v2 pass, and add
the ceremonial pair as new tokens only if a Phase-2 branch actually uses them.

## D · Sanctum referents (locked language, from the murti codex §8)

sandstone = the carved stone · charcoal = the linga · gold = lamp flame ·
ivory = the lit stone · indigo = the water at night · deep bronze = the wet
stone where the abhisheka has run. The palette is a portrait of the sanctum.

## E · Print equivalents (indicative — press-proof before any production run)

| Token | CMYK (coated, indicative) | Pantone (nearest) | Foil |
|---|---|---|---|
| gold `#C8A15A` | 20 / 33 / 70 / 4 | 465 C (flat) · **871 C (metallic)** | Kurz Luxor 375 / matte gold |
| charcoal `#1A1A1A` | 0 / 0 / 0 / 90 (rich: 40/30/30/100) | Black 6 C | — |
| ivory `#F7F3E9` | 2 / 3 / 9 / 0 (usually = paper stock) | 9224 C | — |
| indigo `#1C1A3D` | 90 / 87 / 36 / 43 | 276 C | — |
| deep bronze `#7A5423` | 35 / 60 / 95 / 30 | 1405 C | — |

Foil rule: metallic gold foil replaces `gold` on ceremonial print; never foil
body text; the bindu MAY be foiled alone on charcoal/indigo stock (it is the
god-point — foil is appropriate there, and only there).
