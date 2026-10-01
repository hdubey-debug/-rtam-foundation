# पोस्टर · Posters — proofs for review

**समीक्षा के लिए यहाँ जाएँ · Review here: <https://hdubey-debug.github.io/-rtam-foundation/posters/>**

Nine poster and banner styles for the Rtambhareshvara Mandir, each applied to six images, so that a style can be judged
across the whole set before anything is prepared for a printer. **These are design proofs, not press files.**

## पोस्टर कैसे चुनें · How to review

1. Open the link above. Compare by style (one style, six images) or by image (one image, nine styles).
2. Tap a poster to see it large. Press **चुनें · Select** under the ones you like.
3. Write your name, add a comment if you wish, and press **WhatsApp पर भेजें · Send on WhatsApp** (or Share, or Copy).

Every poster has a code: a letter for the image and a number for the style.

| | A | B | C | D | E | F |
|---|---|---|---|---|---|---|
| **Image** | Front | Side, tower right | Side, tower left | Shivalinga | Nandi pavilion | Temple and Nandi |

| | Style | Format | Use |
|---|---|---|---|
| **1** | Adhishthana अधिष्ठान | 24 × 36 in | The picture stands on the name. Upright poster |
| **2** | Shirshak शीर्षक | 24 × 36 in | Name on top, for flex hung near the ground |
| **3** | Ek Rekha एक रेखा | 2 : 1 | Hoarding. Name and picture on one ground line |
| **4** | Torana तोरण | 3 : 1 | Gate or street banner |
| **5** | Stambha स्तम्भ | 85 × 200 cm | Standee |
| **6** | Chandra चन्द्र | 24 × 36 in | Light ground, for indoor walls |
| **7** | Akasha आकाश | 24 × 36 in | Alternate: the sky deepens into the black |
| **8** | Dhvaja ध्वज | 24 × 36 in | Alternate: the name set inside the picture |
| **9** | Patta पट्ट | 24 × 36 in | Alternate: the letterhead enlarged |

So `A1` is the front view in style 1, and `F3` is the temple with Nandi as a hoarding. A reply can be as short as
"A1, D1, F3". The selection message also carries a link that reopens the same selection on the page.

The page uploads nothing: a selection lives in the reviewer's own browser and in that link.

Sheets that can be saved and forwarded as pictures: [`sheets/all-54.jpg`](sheets/all-54.jpg) and
`sheets/style-1.jpg` … `sheets/style-9.jpg`.

## What is in this folder

| Path | What |
|---|---|
| `index.html` | The review page (static; fonts self-hosted in `fonts/`) |
| `img/thumb/`, `img/full/` | Each poster as a preview, named by code (`A1.webp` … `F9.webp`) |
| `sheets/` | One sheet per style, one sheet of all 54, and the link-preview picture |
| `source/` | The five supplied pictures |
| `build/` | The generator (see below) |
| `DESIGN-PHILOSOPHY.md` | The visual idea in six paragraphs |

The true-size PDFs are not committed: they are proofs of about 290 MB in total and will be replaced by press files once a
style is chosen. `build/make_posters.py` recreates them in `out/`.

## What was done to the pictures

- **Styles 1 to 5** lift the subject out of its picture and set it on the brand black (mahakala). Apple's on-device
  subject tool makes the first matte; it is then snapped to the picture's edges and cleaned by hand-set rules. Nothing
  inside the temple or the Shivalinga is repainted.
- **Nandi.** The statue is black stone and vanished on black, so in styles 1 to 5 its exposure is lifted. Styles 6 to 9
  show it untouched.
- **Shivalinga.** The cut-out is the linga and its pedestal; the hanging vessel and its stream stay with the hall in
  styles 6 to 9. The jaladhari is still light stone and is to be made dark.
- **Temple and Nandi (F).** No picture shows both, so F is composed from image C and image E on one ground line, Nandi
  facing the door. His size and distance are set by eye. In styles 6 to 9 the sky behind them is painted from image C's own
  sky colours.
- **Styles 3 and 4** are mirrored for C and F, whose steps are on the right, so that the ground line arrives at the steps.

## Rules every poster follows

From `brand/guidelines/usage-rules.md`:

- The city-print lockup `rtambhareshvara-mandir-lockup-devanagari-led`, unmodified: Devanagari leads, Cinzel caps echo.
- One gold per page: the chakra hub and the bindu. Type is bhasma ash on mahakala, ink on chandra.
- The address pair exactly as on the letterhead foot, both scripts in full.
- Devanagari is never letterspaced.
- The status line is a sentence the name completes: पहाड़ीखेड़ा में बन रहा है → ऋतम्भरेश्वर मंदिर.

## Rebuild

Needs macOS with Google Chrome and Swift (Xcode command-line tools), Poppler (`pdftoppm`), and Python 3 with Pillow and
numpy.

```sh
cd posters
python3 build/setup_brand.py                    # assemble brand/ from the repository's brand kit (once)
python3 build/make_posters.py                   # all 54 into out/, about 6 minutes
python3 build/make_posters.py --subjects front,pair --styles 01,03
python3 build/site.py                           # previews, sheets and index.html
```

| Script | Job |
|---|---|
| `make_posters.py` | The six subjects, the nine layouts, the copy and the colour tokens |
| `cutout.py`, `subject_mask.swift` | Subject cut-outs: Vision matte, refinement, per-picture corrections |
| `prep.py` | Sky matte, sky continuation, melts, the front elevation's measured outline |
| `render.py` | HTML to PDF with headless Chrome, PDF to PNG with Poppler |
| `site.py` | This folder's page, previews and sheets |
| `sheets.py`, `review_page.py` | Larger comparison sheets and a single-file review page |
| `qr_matrix.swift`, `qr_decode.swift` | Make the QR matrix and read it back from a rendered poster |

Layouts are written in page units (1 unit = 0.1 in at the reference size), so any print size is a scale factor.

## Before anything goes to a printer

1. Choose the styles and confirm the sizes, then export one file per exact size with bleed.
2. Enlarge the pictures: the supplied pictures are 1448 px wide, which is soft for prints seen up close.
3. Confirm the address, the phone numbers, the status wording, and where the QR code points.
4. Convert text to outlines and supply a flattened file as well; flex shops retype Devanagari.
5. Replace the composed temple-and-Nandi image with one true picture of both.
