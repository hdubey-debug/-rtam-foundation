# exp/rta-chakra — version history

The icon study: the murti's plan view (12 petals + 12 medallions + the
gold Shivalinga at the hub), one geometry across several craft registers,
every candidate shown in a live lockup with the shipped R-dot wordmark.

Versions are kept side by side so any of them can be returned to:

- **`v1-24petal/`** — the original six crafts (tanka, utkirna, shila,
  dvitala, jala, aditya) with the two-tier reading (24 petal shapes
  visible from above). Founder: good direction; shila liked most; jala
  rejected; correction issued — the top view shows twelve petals only.
- **`v2-12petal/`** — the ruling applied: one 12-petal corolla, petal
  silhouette redrawn as a true lotus petal (broad base, low belly, sharp
  ogival tip), podium rebalanced (tips reach .70 R). Candidates keep
  their v1 numbers — 1 tanka, 2 utkirna, 3 shila, 4 dvitala, 6 aditya —
  each faithful to its own identity; no components mixed between them.
- *(git only, reverted)* commit `78bd12e` — a synthesis iteration
  (ratna/mala) that mixed candidate 6's gold into candidate 3; rejected:
  candidates stay pure.

Regenerate a version: `python3 build.py` inside its directory, then
`python3 ../../../../tools/render_html_to_png.py gallery.html gallery.png 1500 2`.
