# exp/letterform — eye-check gate (F-format)

**Method.** Glyph geometry via fontTools bounds through brandlib's shaping
path (no guessed metrics); battery rendered through the Phase-0 pipeline.

| # | Check | Verdict |
|---|---|---|
| 1 | Re-cut Ṛ monogram, hero size | PASS — reads as one gesture (R reaching for the bindu); "R." punctuation reading gone |
| 2 | Tail misreading risk | WATCH — at some sizes the tail edges toward a comma ("R,"). Carried: Phase-3 refinement = shorter, straighter terminal if this direction is picked |
| 3 | Mixed-case Ṛtam (Marcellus) on indigo, ivory + gold bindu | PASS — the system's first credible whisper; bindu grammar (cy=b+0.233fs) transfers to Marcellus without adjustment |
| 4 | Script parity strip (R vs ऋ at fs 216) | PASS — measured ink-height parity 140.0u vs 140.0u; optical mass now comparable (old fs 210 read undersized) |
| 5 | Parity ऋ icon standalone | PASS — recentred on ink mid-line |
| 6 | Favicon 16 px (typographic R + dot, unchanged system favicon) | KNOWN LIMIT — R strokes mush at 16 px; this direction inherits the problem it cannot solve; A/B's constructed favicons do |
| 7 | Mono 6 cm re-cut monogram | PASS — tail survives single-colour reduction |
| 8 | Co-brand row (Ṛ monogram + RTAM wordmark) | WATCH — R-beside-RTAM is redundant in tight lockups; rule: monogram and wordmark never co-occur at equal weight |
| 9 | Tail implementation | NOTE — same-fill overlay (raster-identical to union); boolean-union before any vector handoff (Phase 3) |

**Net:** strong hedge. The mixed-case Ṛtam and the parity fix are keepers
regardless of direction; the re-cut R is expressive but needs terminal
refinement; the favicon weakness is structural.
