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
2. F6 — RESOLVED at US-11: the agent sheet's mash was a layout-arithmetic
   bug (its F_x values ignored RTAM's advance width → near-negative gaps),
   not the gap value. Corrected retest (F_x = advance-end + gap, real
   Cinzel): **gap locked at 56** (52 acceptable). ALL F6 resolved
   coordinates are invalidated and must be re-derived from the rule
   (symmetric optical margins + gap=56) at US-13.
3. Circle-icon composite — composite-centering rule (cy = baseline + capH/3,
   composite bbox centered in cell/ring) APPLIED at US-11 to the PLAIN icons:
   y=166.33/cy=213 — these stand. The CIRCLE variants (y=160.58/cy=200.25)
   were SUPERSEDED at US-11′: on full-size faithful render the user rejected
   them as lopsided — measurement confirmed the bbox was centered (cy 125.5)
   but the large R crowded the ring (top corners only ~8u clear) over a wide
   empty lower void holding a lonely bindu (R→bindu gap 25.8). Re-derived by
   optical mass-balance (not bbox-centering): shrink the glyph off the ring
   and pull the bindu up as an attached ṛ-accent. Locked from rendered
   candidates + eye-check + per-quadrant clearance — R-circle x=127 y=161
   fs=152, bindu cy=189 r=12 (was x=121.12 y=160.58 fs=170, cy=200.25 r=14.17);
   ऋ-circle y=190 fs=184 (was y=186 fs=180), dropped so the heavy shirorekha
   bar seats near center. Tooling: `brand/tools/_scratch/circlefix/sweep.py`.
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
