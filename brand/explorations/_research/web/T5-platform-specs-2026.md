# T5 — Current (2026) platform asset specs: the definitive US-15 deliverables table

*Research track T5 · web survey · compiled 2026-06-07.*
*Scope: exact CURRENT (2026) export dimensions, formats, and safe-zone notes for every surface RTAM ships on — Instagram (avatar + circular-crop math, feed, Stories, Reels cover), YouTube (channel icon + banner + device safe area), favicon best-practice set + site.webmanifest, Open Graph / Twitter card, plus WhatsApp Business and X/Twitter avatar crops. Sources dated inline. Where platforms publish conflicting numbers, the conflict is named and the load-bearing figure justified rather than averaged (CLAUDE.md Rule 8).*

> **Confirmation note.** Platforms (Meta, Google/YouTube, X) no longer publish a single canonical "image sizes" spec sheet for most of these surfaces; the durable numbers below are the ones that recur unchanged across multiple independently-dated June/March-2026 guides AND match the long-standing platform-published values. Two figures carry a documented conflict (YouTube banner safe area; X large-card ratio) — both are flagged in-table and in Findings rather than silently picked.

---

## Findings

### F1 — Instagram profile picture: upload 320×320 min, master at 1080×1080; the real constraint is the **circular crop**
Instagram accepts a **320×320 px** square (1:1) minimum but compresses hard, so the working master should be **1080×1080 px**; it then **displays the avatar tiny — ~110×110 px on mobile, ~180×180 px on desktop web — inside a circle** (Influencer Marketing Hub, *Instagram Image Sizes 2026*, dated 2026-03-30 — https://influencermarketinghub.com/instagram-image-sizes/ ; Hootsuite *Social media image sizes* dated 2026-06-01 — https://blog.hootsuite.com/social-media-image-sizes-guide/ ). The circular crop is the load-bearing fact: the **inscribed circle covers only 70.71% of the square's width**, leaving ~14.64% of dead corner on each side, so logos must sit inside a **central 60–65% working zone** (a face can use the inner ~80%) (trustypost.ai, *Instagram profile picture size 2026: pixels, ratio, safe crop* — https://trustypost.ai/blog/instagram-profile-picture-size-2026-pixels-ratio-safe-crop/ ). At a ~110 px render, thin strokes and small diacritics collapse — this is the same scale regime as a favicon.

### F2 — Instagram feed + Stories + Reels: one 9:16 frame, but Reels has a **1:1 grid crop** and a heavier bottom safe zone
- **Feed:** square **1080×1080** (1:1), portrait **1080×1350** (4:5, the most screen real estate), landscape **1080×566** (1.91:1) (Influencer Marketing Hub 2026; Buffer *Instagram Post Size Guide 2026* — https://buffer.com/resources/instagram-image-size/ ).
- **Stories / Reels video:** **1080×1920** (9:16). Stories UI eats ~**220 px top and ~220 px bottom**, leaving a ~**1080×1480** safe band for text/CTAs. **Reels reserve more at the bottom (~320–410 px)** for the caption/audio/CTA bar — Reels safe insets cited as ~108 px top / ~320 px bottom / 60 px left / 120 px right (screensnap.pro *Instagram Story/Reels Size 2026* — https://www.screensnap.pro/blog/instagram-story-size-guide ; sellerpic *Instagram Safe Zone & Reels 2026* — https://www.sellerpic.ai/blog/instagram-safe-zone ).
- **Reels cover:** the cover is **1080×1920**, but on the **profile grid it is center-cropped to 1:1** — keep the meaningful element inside the **central 1080×1080** of the cover or it is lost on the grid (screensnap.pro, above; Buffer 2026).

### F3 — YouTube: channel icon **800×800**, banner **2560×1440** (mobile-safe **1546×423**), video watermark **150×150**
Channel icon: **800×800 px**, 1:1, ≤2 MB. Banner ("channel art"): design at **2560×1440 px** (min upload **2048×1152**), ≤6 MB, JPG/PNG. The banner renders differently per device — full 2560×1440 on TV, a ~2560×423 strip on desktop, and on **mobile only the center 1546×423** shows. That **1546×423 px center block is the all-device safe area** for logo/text (picssizer *YouTube Image Size 2026* — https://www.picssizer.com/image-sizes/youtube ; postfa.st *YouTube Banner Size, updated 2026-03* — https://postfa.st/sizes/youtube/banner ; pixpipe *YouTube Channel Banner Size Guide 2026* — https://pixpipe.app/en/guides/youtube-channel-banner-size ; socialsizes.io — https://socialsizes.io/youtube-cover-photo-size/ ). **CONFLICT:** Hootsuite (2026-06-01) lists the safe area as **1235×338** — an outlier against every dedicated YouTube guide and against YouTube's own long-published 1546×423 figure. **I use 1546×423** (more sources, matches the platform-historical value) and flag Hootsuite's number as likely stale/erroneous.

**Video watermark (branding):** a third, separate YouTube asset — the small overlay baked bottom-right onto **every** video in the channel. Spec: **150×150 px, transparent PNG, ≤1 MB**, square. It must be a **single high-contrast icon** — "Small 150×150 images cannot display complex text" (unifab *YouTube Watermark Size Guide 2026* — https://unifab.ai/resource/what-is-youtube-watermark-size ; softorbits *YouTube Watermark Size in 2026* — https://www.softorbits.net/how-to/youtube-watermark.html ). This is another tiny single-mark, transparent-ground surface — the same regime as the avatar/favicon (F7): the wordmark fails here; only the framed-R / bindu icon reads.

### F4 — Favicon (2026): a **minimal multi-file set** — .ico(32) + SVG + apple-touch 180 + 192/512 PNGs + a maskable 512, declared in HTML + a webmanifest
The current authoritative minimal pattern (Evil Martians, *How to Favicon*, with a live "Editor's note 2026" — https://evilmartians.com/chronicles/how-to-favicon-in-2021-six-files-that-fit-most-needs ) is:
- **favicon.ico** at **32×32** (single image is enough now; legacy browsers/tab),
- **icon.svg** (vector, can carry light/dark via CSS media query) as the primary modern favicon,
- **apple-touch-icon.png 180×180** (iOS home-screen; Safari ignores `rel="icon"` so this tag is required, no transparency, no pre-rounded corners),
- **icon-192.png** (Android home screen) and **icon-512.png** (PWA splash) in the manifest,
- **a maskable 512×512** whose **safe zone is a central circle of 409×409** (Android launchers crop the corners).

HTML links:
```html
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
```
`site.webmanifest` icons block (Evil Martians; cross-checked favicon.io *Favicon Size Guide 2026* — https://favicon.io/tutorials/favicon-sizes/ ):
```json
{
  "name": "RTAM Foundation",
  "short_name": "RTAM",
  "icons": [
    { "src": "/icon-192.png", "type": "image/png", "sizes": "192x192" },
    { "src": "/icon-512.png", "type": "image/png", "sizes": "512x512" },
    { "src": "/icon-mask.png", "type": "image/png", "sizes": "512x512", "purpose": "maskable" }
  ],
  "theme_color": "#1C1A3D",
  "background_color": "#F7F3E9"
}
```
(16×16 and 32×32 PNGs are optional extras; the .ico + SVG pair already covers the tab. `theme_color`/`background_color` are not in the Evil Martians snippet but are standard manifest fields — values above are RTAM palette, not from the source.)

### F5 — Open Graph / link previews: one **1200×630** (1.91:1) asset covers almost everything; keep content in a **center 1080×600** safe zone
The universal link-preview asset is **1200×630 px, 1.91:1, JPG or PNG, <1 MB ideal (≤5 MB)** — it works for Facebook, LinkedIn (≈1200×627), Slack, Discord, Pinterest, and X's large card (Krumzi *OG Image Sizes 2026*, updated 2026-05 — https://www.krumzi.com/blog/open-graph-image-sizes-for-social-media-the-complete-2026-guide ). Set `og:image:width`=1200 / `og:image:height`=630. Keep headline/wordmark inside the **center 1080×600** safe zone against platform crops. **CONFLICT / nuance on X:** the X `summary_large_image` card is variously cited as **1200×630 (1.91:1)**, **1200×675 (16:9)**, or **1200×600 (2:1)**; X accepts 1200×630 and may shave a few px top/bottom. **One 1200×630 asset is the correct single deliverable**; if a tighter X crop matters, keep type away from the extreme top/bottom edges. The small `summary` card is square (min 144×144, ~800×418 thumbnail variant cited too).

### F6 — WhatsApp Business + X/Twitter avatars (quick): both are **center-circle crops**; export 800×800 and 400×400 respectively
- **WhatsApp Business** profile photo: upload a **square**, recommended **800×800 px** (640×640 acceptable; min 192×192), ≤5 MB; WhatsApp **center-crops to a circle** (max stored edge ~640 px) — center the mark (chatarmin *WhatsApp Image Size Guide 2026* — https://chatarmin.com/en/blog/whats-app-image-size-guide ; imresizer *WhatsApp Image Sizes 2026* — https://imresizer.com/blog/whatsapp-image-sizes-2026-complete-guide ).
- **X / Twitter** profile picture: **400×400 px**, 1:1, ≤2 MB, **displayed as a circle** at 48–200 px; header **1500×500** (3:1) with the avatar + name overlapping the lower-left — keep header content in a **center ~1260×420** band and out of the lower-left ~20% (socialez *X Image Sizes 2026* — https://www.socialez.com/blog/twitter-image-sizes/ ; postfa.st *X Header, updated 2026-03* — https://postfa.st/sizes/x/header ).

### F7 — The cross-platform constant: **every avatar is a center-circle crop and renders tiny.** 
IG (70.71% inscribed circle, ~110 px render), WhatsApp (center circle), X (circle 48–200 px), YouTube/Google account (circle) all crop a square to a circle and display it small. One **single square avatar master, content inside a center safe-circle, tested at ~48–110 px**, satisfies all of them. This is the same regime as the 32×32 favicon — i.e. RTAM's existing "the bindu detaches above 64 px / favicon ≤64 px" caveat (usage-rules §2, brand-book §3.2) governs the *whole avatar tier*, not just the browser tab.

---

## Implications for RTAM

- **The avatar IS the favicon problem at a slightly bigger size.** Every social avatar (IG ~110 px, X down to 48 px, WhatsApp small, YouTube icon circle) is a tiny center-circle crop. RTAM already knows its bindu "detaches at scale" and that the favicon must use the simplified `favicon.svg` ≤64 px (usage-rules §2). The same rule must extend to all avatars: **the full wordmark and the gold bindu must NOT be the avatar.** The correct avatar is the framed icon — `rtam-rdot-icon-circle-gold.svg` / `-circle-charcoal.svg` (already named in usage-rules §2 as "App icon needing visual frame") — because the circle frame is what survives the platform's circular crop, and the icon's single R reads where a four-letter wordmark + 10-px bindu would not.

- **Center-circle crop kills any rectangular lockup as an avatar.** None of the lockups (`rtam-bilingual-foundation.svg`, `rtambhareshvara-mandir-lockup.svg`, etc.) can be an avatar — they are wide, and 29% of a square avatar is discarded by the circle. Lockups belong only on the **wide** surfaces (YouTube banner safe area, OG image, X/IG covers), never in the avatar slot.

- **The 1200×630 OG image and the YouTube banner are the two places the wordmark belongs** — both are wide, both have generous center safe zones (OG 1080×600; YT 1546×423). These map cleanly to the existing wordmark on **ivory** ground. Caution: the documented **gold-on-ivory 2.18:1 contrast failure** (repo memory / F13 fix-spec) matters most here because these previews render at thumbnail scale in feeds — the wordmark on these assets should use the **charcoal** wordmark on ivory, with gold reserved for the bindu, not for type.

- **`theme_color` / `background_color` should be brand tokens, not defaults.** Indigo `#1C1A3D` (sacred ground) for `theme_color` and ivory `#F7F3E9` for `background_color` make the PWA chrome and splash on-brand — a free, durable win once the manifest exists.

- **Maskable-icon safe circle (409/512 ≈ 80%) is a hard new constraint.** Android crops the 512 maskable icon to a circle/squircle; the R-in-circle icon must keep its R inside the central **409×409** or launchers will clip the gold ring. The existing `-circle-` icons already frame the R — they need a padded **maskable** export, not the tight-bleed version.

- **Reels grid 1:1 crop reinforces the same discipline.** A Reels cover designed full-bleed 9:16 loses its edges on the profile grid (center 1080×1080 only). Any RTAM Reels cover template must place the mark in the central square — same center-safe rule as the avatar.

---

## Implied repo changes (MANDATORY)

1. **usage-rules.md — new section "§2.1 · Social avatars + tiny single-mark surfaces (all platforms)":** add a table/rule:
   *"Every social avatar is a center-circle crop rendered small (IG ~110 px, X down to 48 px, WhatsApp/YouTube circle), and the YouTube video watermark is a 150×150 transparent single-mark overlay. NEVER use a wordmark or any rectangular lockup in these slots. Use `rtam-rdot-icon-circle-gold.svg` (default) or `-circle-charcoal.svg` (dark) for circular avatars, and a transparent-ground R/bindu icon for the watermark; export square and keep the R inside the central 70% (IG's inscribed circle is only 70.71% of the square). The favicon scale rule (§2: bindu detaches above 64 px) governs this entire tier."* (Basis F1, F3, F6, F7.)

2. **usage-rules.md §2 — add favicon/manifest file list:** ship **favicon.ico (32×32), favicon.svg, apple-touch-icon.png (180×180, no transparency/no pre-rounded corners), icon-192.png, icon-512.png, icon-mask.png (512×512 maskable, R inside central 409×409), site.webmanifest**. Manifest `theme_color: #1C1A3D`, `background_color: #F7F3E9`. (Basis F4.)

3. **Deliverables list (US-15) — add the definitive asset spec table** (this is the core US-15 output):

   | # | Asset / filename | Export px | Format | Safe-zone note |
   |---|---|---|---|---|
   | 1 | `avatar-master.png` (square avatar, all platforms) | 1080×1080 | PNG | Center-circle crop; R inside central 70% (~756 px dia.); test at 48–110 px |
   | 2 | `ig-avatar.png` | 320×320 (master 1080) | PNG | IG circle = 70.71% of square; logo in central 60–65% |
   | 3 | `whatsapp-avatar.png` | 800×800 | PNG | Center-circle crop; subject centered |
   | 4 | `x-avatar.png` | 400×400 | PNG/JPG | Circle 48–200 px; ≤2 MB |
   | 5 | `youtube-channel-icon.png` | 800×800 | PNG/JPG | Circle; ≤2 MB |
   | 6 | `youtube-banner.png` | 2560×1440 (min 2048×1152) | PNG/JPG ≤6 MB | All-device safe area = center **1546×423**; wordmark here |
   | 6b | `youtube-watermark.png` (video branding overlay) | 150×150 | **transparent PNG** ≤1 MB | Bottom-right of every video; single icon only (no text) — framed-R / bindu icon |
   | 7 | `x-header.png` | 1500×500 | PNG/JPG ≤5 MB | Content in center ~1260×420; avoid lower-left ~20% (avatar/name overlay) |
   | 8 | `og-image.png` (Open Graph + X large card + LinkedIn/Slack/Discord) | 1200×630 (1.91:1) | PNG/JPG <1 MB ideal | Headline/wordmark in center **1080×600**; charcoal wordmark on ivory |
   | 9 | `ig-post-square.png` | 1080×1080 | PNG | 1:1 |
   | 10 | `ig-post-portrait.png` | 1080×1350 | PNG | 4:5 (max feed real estate) |
   | 11 | `ig-story.png` / `.mp4` | 1080×1920 (9:16) | PNG/MP4 | ~220 px top + ~220 px bottom UI; safe band ~1080×1480 |
   | 12 | `ig-reel-cover.png` | 1080×1920 | PNG | Grid center-crops to 1:1 — key element in central **1080×1080** |
   | 13 | `favicon.ico` | 32×32 | ICO | Tab/legacy |
   | 14 | `favicon.svg` | vector | SVG | Primary modern favicon; ≤64 px simplified mark |
   | 15 | `apple-touch-icon.png` | 180×180 | PNG | No transparency, no pre-rounded corners |
   | 16 | `icon-192.png` | 192×192 | PNG | Android home screen |
   | 17 | `icon-512.png` | 512×512 | PNG | PWA splash |
   | 18 | `icon-mask.png` | 512×512 | PNG (`purpose:maskable`) | R inside central **409×409** circle |
   | 18a | `favicon-16.png` | 16×16 | PNG | Legacy/optional — `.ico`+SVG already cover the tab; ship if a PNG-only fallback is wanted |
   | 18b | `favicon-32.png` | 32×32 | PNG | Legacy/optional — same rationale as 16×16 |
   | 19 | `site.webmanifest` | — | JSON | `theme_color #1C1A3D`, `background_color #F7F3E9` |

   (Basis F1–F6. PNG chosen over JPG for flat brand fields to avoid artefacting on the ivory ground and around the bindu; JPG acceptable only on photographic OG variants.)

4. **rubric.md (`brand/explorations/_rubric/rubric.md` — does not yet exist; T1 also asks to create it) — add criterion "C-Avatar/Crop Survival"** with anchors:
   - **5** — mark is legible and on-brand inside a **center circle covering 70%** of the square AND at a 48–110 px render; nothing critical in the corners.
   - **3** — survives the circle but loses minor detail at ~110 px; needs the framed-icon variant.
   - **1** — relies on the full wordmark / a wide lockup / a sub-10-px bindu → clipped by the circle or invisible at avatar scale.
   (Basis F1, F6, F7. This is the social-surface complement to T1's C-Reproduction-Floor favicon criterion.)

5. **rubric.md — add criterion "C-Wide-Surface Safe-Zone Fit"** with anchors:
   - **5** — wordmark/lockup composition keeps all type and the bindu inside the platform safe zones (YT center 1546×423; OG center 1080×600; X header center 1260×420) and stays legible at feed-thumbnail scale.
   - **3** — fits the safe zone but type crowds an edge or relies on gold-on-ivory (2.18:1) at thumbnail scale.
   - **1** — content bleeds outside the safe zone (clipped on mobile) or is illegible at preview size.
   (Basis F3, F5, F6 + repo contrast-failure memory.)

6. **Risk log — add risk R-T5a "Avatar = wordmark mistake":** *"If any RTAM avatar ships the wordmark or a lockup instead of the framed R-in-circle icon, the platform center-circle crop (IG keeps only 70.71% of the square) plus the ~48–110 px render destroys legibility and the 10-px bindu vanishes. Mitigation: §2.1 avatar rule + C-Avatar/Crop-Survival rubric gate; only `rtam-rdot-icon-circle-*` may be an avatar. Likelihood: high if unmanaged."*

7. **Risk log — add risk R-T5b "Spec drift / unconfirmed platform numbers":** *"These dimensions are aggregated from dated 2026 third-party guides; platforms ship no single canonical spec page and change crops silently. Two figures are already disputed in-sources (YouTube safe area 1546×423 vs Hootsuite's 1235×338; X large-card 1.91:1 vs 16:9 vs 2:1). Mitigation: design every avatar/cover to the *most conservative* safe zone (smallest center block), re-verify before any major asset re-export, and validate OG via Facebook Sharing Debugger / X Card Validator before launch. Owner: brand lead."*

8. **Risk log — add risk R-T5c "Gold-on-ivory at thumbnail scale":** *"OG/banner previews render at feed-thumbnail size where the gold-on-ivory 2.18:1 contrast failure (F13 / repo memory) is worst. Mitigation: on all wide social/preview assets the wordmark TYPE is charcoal `#1A1A1A` on ivory; gold is reserved for the bindu only."*

---

## Sources

- Influencer Marketing Hub — *Your Complete Guide to Instagram Image Sizes for 2026* (dated 2026-03-30) — https://influencermarketinghub.com/instagram-image-sizes/
- trustypost.ai — *Instagram profile picture size (2026): pixels, ratio, safe crop* — https://trustypost.ai/blog/instagram-profile-picture-size-2026-pixels-ratio-safe-crop/
- Hootsuite — *Social media image sizes for all networks* (dated 2026-06-01) — https://blog.hootsuite.com/social-media-image-sizes-guide/
- Buffer — *Instagram Post Size Guide 2026* — https://buffer.com/resources/instagram-image-size/
- screensnap.pro — *Instagram Story Size 2026: Dimensions & Safe Zones* — https://www.screensnap.pro/blog/instagram-story-size-guide
- sellerpic — *Instagram Story Safe Zone & Reels Guide 2026* — https://www.sellerpic.ai/blog/instagram-safe-zone
- picssizer — *YouTube Image Size Guide 2026* — https://www.picssizer.com/image-sizes/youtube
- postfa.st — *YouTube Banner Size: 2560×1440 (updated March 2026)* — https://postfa.st/sizes/youtube/banner
- pixpipe — *YouTube Channel Banner Size Guide 2026* — https://pixpipe.app/en/guides/youtube-channel-banner-size
- socialsizes.io — *YouTube Cover Photo Size / Channel Banner (2026)* — https://socialsizes.io/youtube-cover-photo-size/
- unifab — *YouTube Watermark Size Guide: Exact Dimensions, Formats & Best Practices (2026)* — https://unifab.ai/resource/what-is-youtube-watermark-size
- softorbits — *YouTube Watermark Size in 2026: Specs, Studio, and a Video Watermark Maker* — https://www.softorbits.net/how-to/youtube-watermark.html
- Evil Martians — *How to Favicon* (live "Editor's note 2026") — https://evilmartians.com/chronicles/how-to-favicon-in-2021-six-files-that-fit-most-needs
- favicon.io — *Favicon Size Guide — All Favicon Sizes for 2026* — https://favicon.io/tutorials/favicon-sizes/
- Krumzi — *Open Graph Image Sizes 2026 — complete guide* (updated 2026-05) — https://www.krumzi.com/blog/open-graph-image-sizes-for-social-media-the-complete-2026-guide
- og-image.org — *Twitter Card Image Size (2026): Specs + Fixes* — https://og-image.org/learn/twitter-card-size
- chatarmin — *WhatsApp Image Size Guide 2026* — https://chatarmin.com/en/blog/whats-app-image-size-guide
- imresizer — *WhatsApp Image Sizes 2026: Complete Guide* — https://imresizer.com/blog/whatsapp-image-sizes-2026-complete-guide
- socialez — *X (Twitter) Image Sizes 2026: Profile, Header & Post Dimensions* — https://www.socialez.com/blog/twitter-image-sizes/
- postfa.st — *X (Twitter) Header Size: 1500×500 (updated March 2026)* — https://postfa.st/sizes/x/header

*Confirmed-vs-flagged: (1) Core numbers (IG 320/1080/1080×1350/1080×1920; YT icon 800×800, banner 2560×1440, min 2048×1152; favicon set; OG 1200×630; X 400×400/1500×500; WhatsApp 800×800) recur consistently across multiple dated 2026 sources AND match platform-historical published values — treated as confirmed. (2) FLAGGED CONFLICTS: YouTube banner safe area — 1546×423 (multi-source, platform-historical, used here) vs Hootsuite 1235×338 (outlier); X summary_large_image ratio — 1200×630 (1.91:1, used as the single asset) vs 1200×675 (16:9) vs 1200×600 (2:1). (3) No platform publishes a single canonical 2026 spec sheet for most of these surfaces, so all figures should be re-validated (and OG tested via the platform debuggers) before a major asset re-export — see risk R-T5b. (4) `theme_color`/`background_color` manifest values are RTAM-chosen brand tokens, not from any source.*
