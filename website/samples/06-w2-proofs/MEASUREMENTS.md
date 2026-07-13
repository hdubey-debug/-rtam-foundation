# W2 proof matrix & measurements

Rendered from `website/dist/` over a local `http.server` (no compression —
byte counts are an upper bound on a gzip/brotli host).

## Engine matrix

- **chromium** 148.0.7778.96 — proofs rendered
- **firefox** 150.0.2 — proofs rendered
- **webkit** — CANNOT RUN on this host: missing system libraries (libgstreamer-1.0, libgtk-4, …) and the HPC cluster grants no sudo to install them. Mitigations: baseline-features-only policy + the founder's real-device Safari/iPhone checklist (FOUNDER-CHECKLIST.md).

Proof renders: `proofs/` — 24 shots (every page × {chromium, firefox} × {1440, 390}).

## Cold-load transferred bytes @390px (chromium, fresh context)

| page | requests | bytes | budget |
|---|---|---|---|
| /darshana/index.html | 12 | 231,538 |  |
| /index.html | 12 | 255,543 | ≤ 600,000 → PASS |
| /mandir/index.html | 14 | 382,393 |  |
| /seva/index.html | 10 | 218,624 |  |
| /system.html | 10 | 225,726 |  |
| /utsava/index.html | 11 | 227,343 |  |

## LCP under CDP throttling (4 Mbps / 150 ms RTT / 4× CPU, @390px)

| page | LCP (ms) | budget |
|---|---|---|
| /darshana/index.html | 664 |  |
| /index.html | 788 | < 2,500 ms → PASS |
| /mandir/index.html | 924 |  |
| /seva/index.html | 592 |  |
| /system.html | 600 |  |
| /utsava/index.html | 616 |  |

The landing's LCP element is the hero `<img>` — painted immediately, never veiled
(verify_site gate D asserts it).
