# Vendored Brand Fonts

The four font families the brand kit depends on, vendored so the repo is
self-contained — outlining tools (`brand/tools/outline.py`), faithful local
rendering, and design-app work no longer require a network fetch from
Google Fonts.

| Family | Files | Role | License |
|---|---|---|---|
| Cinzel | `cinzel/cinzel-{400,500,600,700}.ttf` | Primary Latin display face (wordmarks, icons) | OFL 1.1 |
| Marcellus | `marcellus/marcellus-400.ttf` | Alternate Latin display face (fallback stack) | OFL 1.1 |
| Inter | `inter/inter-{400,500,600}.ttf` | UI / body sans (previews, mockups, documents) | OFL 1.1 |
| Tiro Devanagari Sanskrit | `tiro-devanagari-sanskrit/tiro-devanagari-sanskrit-400.ttf` | Devanagari sacred contexts (ऋतम्, lockups, motto) | OFL 1.1 |

## Provenance

Static-instance TTFs served by the Google Fonts CSS v2 API
(`fonts.googleapis.com/css2` → `fonts.gstatic.com`), fetched 2026-06-07 with a
non-woff2 user agent so the API returns **full, unsubset** TTFs. Verified with
fontTools: family names, glyph counts (Cinzel 368, Marcellus 370, Inter 2871,
Tiro Devanagari Sanskrit 1600), GSUB shaping tables present, and coverage of
all brand-critical codepoints (Latin A–Z, ऋ, virāma, म भ श व, anusvāra).

## License

Every family is licensed under the SIL Open Font License 1.1 — see `OFL.txt`
inside each family folder (canonical OFL 1.1 text prefixed with that font's
own copyright notice from its `name` table). The OFL permits bundling,
redistribution, and commercial use; it does not permit selling the fonts by
themselves.
