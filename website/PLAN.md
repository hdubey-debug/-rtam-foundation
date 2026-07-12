# ṚTAM Foundation — Website Program Plan (v1, 2026-07-12)

Goal, in the founder's words: **stunning and innovative — if someone's
looking at it, they should be impressed. Quality work.** Everything
inherits the locked system: the ṛta-chakra + sanctity ladder, the R-dot
wordmark, the substance palette (Garbhagriha leads / Bhasma-day reads /
Kanaka festival), the ṛta-grid (12 columns, 6/12/24 spacing, 30°/15°).

## 1 · What we CAN do (in this repo, provable)

- **A complete static site**, hand-crafted HTML/CSS/vanilla-JS — no
  framework debt, deterministic build (jinja2 templates → `website/dist/`),
  rendered and eye-checked through the same Playwright pipeline as every
  asset, with our contrast gates run against the *rendered pages*.
- **The signature experience** (what makes it stunning):
  - a **Garbhagriha hero**: near-black; the gold hub is the first light
    on screen — the page opens like aarti in the sanctum;
  - the **ladder as scroll narrative**: bindu → anāhata → ṛta-chakra as
    you scroll — "the Lord in your heart runs the cosmos," told by zoom;
  - **ṛta-grid layout** with the waterline as the section divider;
    rotational elements only at 30°/15°;
  - Devanagari display moments (Tiro) over English body (Inter),
    bilingual EN/हिं structure prepared from day one;
  - subtle, tasteful motion (CSS transforms; no animation libraries);
  - AA contrast enforced by gates, self-hosted fonts, fast static pages.
- **Pages**: Home · Philosophy (the three readings — content already
  exists in the murti codex) · Mandir (the temple, darshan info) ·
  Seva/Donate (UI + hosted-checkout links) · Events/Festivals (Kanaka-
  dressed cards) · Visit/Contact. Favicon, manifest, OG images already
  shipped in `exports/platform/` + `exports/kits/`.
- **A deploy-ready tree** for GitHub Pages / Netlify / any static host,
  with step-by-step deploy instructions.

## 2 · What we CANNOT do (needs you or a third party)

- **Payments**: no server here — real donations need Razorpay / Stripe /
  PayPal / Zeffy (US 501c3-friendly). We integrate their *hosted*
  checkout (link or embed); we never process cards ourselves. **You pick
  the provider and create the account.**
- **Domain + hosting**: `rtamfoundation.org` must be registered and DNS
  pointed by you; we cannot buy or configure it from this cluster. We
  can prepare GitHub Pages so the site is live on a github.io URL the
  day you enable it in repo settings.
- **Live deployment**: no tokens here — we produce the tree + you click
  deploy (or enable Pages).
- **Forms/email**: no backend — contact forms via Formspree/Google
  Forms embed or mailto; newsletter needs a provider account.
- **Real content**: temple photographs, the actual address, darshan
  times, event dates, trustee names, 501(c)(3)/legal wording, and the
  final domain — all from you. Design proceeds with clearly-bracketed
  placeholders (same convention as the city poster).
- **CMS**: content edits happen through this repo (spec-driven, gated).
  A CMS is possible later but out of scope now.

## 3 · Phases

- **W0 — this plan** (you are here): review + your inputs list opened.
- **W1 — samples**: two to three *complete homepage concepts* — same
  content, different expressions of "stunning" — rendered full-page,
  eye-checked, presented like the design rounds (this is the next
  deliverable on your go).
- **W2 — build-out**: the winning concept becomes the design language;
  all pages built on it; gates wired (contrast on rendered pages, link
  check, export probes).
- **W3 — launch pack**: GitHub Pages/Netlify setup, domain checklist,
  meta/OG/sitemap/robots, Lighthouse pass, handover doc.

## 4 · What I need from you (whenever ready — placeholders until then)

photos of the murti/site · address + darshan times · 2–3 real events
with dates · donation provider choice · domain confirmation · legal
footer text. None of these block W1 samples.
