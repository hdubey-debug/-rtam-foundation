# Phase-0 Research — US-10 Deliverable

Everything here is **research, not applied fixes**: no shipped asset was
modified. The build phases (US-11…US-16) implement these specs after gate
approval.

## Contents

| Artifact | What it is |
|---|---|
| `spikes/` | Four engineering spikes, all PASSED — outlined-master strategy proven end-to-end (Devanagari conjunct shaping, Latin, pathops booleans, fonts vendored). See `spikes/README.md`. The calibrated render-fidelity gate lives in `brand/tools/render_diff.py`. |
| `fix-specs/F1…F15.md` | One implementable spec per confirmed audit finding: root cause, exact change, every number resolved, proof renders, verification, risks, dependencies. |
| `fix-specs/proofs/` | Before/after proof PNGs. **Files marked `-CINZEL` are the authoritative optical proofs** (rendered by the main agent with vendored fonts); same-named agent originals for F1/F3 are fallback-font poisoned and kept only for the record. |
| `web/T1…T6.md` | Six research briefs (institutional identity, Hindu iconography + sanctity-in-use, reduction systems, trademark/Emblems-Act, 2026 platform specs, SVG production). Each ends with mandatory **Implied repo changes**. |
| `MAIN-AGENT-EYECHECK.md` | The US-10.3 gate: personal visual verdict on every decision-bearing proof, incl. the two poisoned-proof catches and the build instructions they generated. |

## Headline numbers resolved (provisional on Cinzel where letterform-specific)

- **Bindu grammar**: cx = ink-bbox center of the outlined bearing glyph
  (wordmark: 126.5, was 118); r = fs/12; gap = capH/3 (cy = baseline + fs·7/30).
  Favicon small-size exception owned by F14.
- **Icon centering**: center the **ink**, not the advance — circle icons
  text x 128→121.12, plain icons 128→119.9, favicon 16→14.87.
- **Weights**: 500 identity / 600 standalone monogram ≥24px cap / 700 below.
- **ऋ recentering**: open y 215→196, circle y 210→186.
- **Seal**: medallions inset off the ring; hub enlarged for hierarchy;
  meaning committed to the 12 Ādityas (Jyotirliṅga reading reserved for a
  future temple variant).
- **Contrast**: gold/ivory 2.18:1 and stone/ivory 1.92:1 → decorative/large
  only; exact §4 rule text in F13.
- **A4**: letterhead/receipt 816×1056 → 794×1123; `render_html_to_png.py`
  Letter→A4 (F15).

## Carry-forward build instructions (from the eye-check)

1. Any render used for an optical judgment MUST use `@font-face` +
   `file://` URIs to `brand/fonts/` — two of fifteen agents shipped
   fallback-font proofs; bare `@import` is banned for proof renders.
2. F6's resolved RTAM↔Foundation gap (48) reads too tight — re-test 52–60
   at US-11 before applying.
3. Circle-icon composite sits low in the ring once F3's canonical gap is
   applied — raise the icon R baseline-y, then recompute F2 x and F3 cy
   (lever was unowned; now assigned to US-11 Track A).
4. Stale radius-ownership references in F1/F14 (cite F5; F3 owns r) —
   clean up when applying.
5. Multi-owner favicon reconciliation (checked at the gate): values compose
   — text x=14.87 (F2) + weight 700 (F4) + dot cx=16, r=2.86, cy=27.2 (F14,
   = F3's recorded exception) — but F14's rationale "no ink-vs-advance
   asymmetry" contradicts F2's measured +0.0435 em offset at w700. Numbers
   stand; correct F14's sentence when applying.

## Dependency order for US-11…US-16

F3 → F1/F2/F4 → F8/F14 → F6/F7 (layout) · F10 frames Track C ·
F13/F15 independent · F11 (export regen) last, after all source edits.
