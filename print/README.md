# छपाई के लिए · To Print

*हर PDF यहाँ छपाई-तैयार है — डाउनलोड करें, 100% आकार ("Actual size") पर छापें।*
*Every PDF here is print-ready — download, print at 100% scale ("Actual size").*

**काग़ज़ का आकार पहले देखें · Match the paper size first.** भारत में A4 काग़ज़ —
सभी मुख्य PDF A4 हैं · In India, use the A4 files (India's standard). **In the
USA** printer trays hold **US Letter** (shorter than A4 — printing an A4 file at
100% cuts off the bottom): use the **`-us` letterhead files**, or set the print
dialog to "Fit to printable area" for any other piece.

| फ़ोल्डर · Folder | क्या है · What | कागज़ / निर्देश · Paper / Instructions |
|---|---|---|
| **letterhead/** | पत्र-शीर्ष · Letterhead (काला/garbhagriha — मुख्य) | क्रीम बॉन्ड 100 gsm — BILT "Corona Cream" · भारत में A4: `letterhead.pdf` (मुख्य, रंगीन लेज़र/प्रेस) / `letterhead-mono.pdf` (एक-रंग) · **USA: `letterhead-us.pdf` / `-us-mono.pdf`** · क्रीम संस्करण: `letterhead-chandra*.pdf` · `letterhead.docx` में पत्र टाइप करें · The dark garbhagriha edition is THE letterhead; chandra cream editions remain the day alternative; DOCX to type letters |
| **receipt/** | दान-रसीद · Donation receipt (A5) | मुख्य रंगीन (सुनहरा केंद्र): `receipt-a5.pdf` + `receipt-cover-a5.pdf` — डिजिटल/प्रीमियम के लिए · छापेखाने को NCR किताबों के लिए `-book` फ़ाइलें + `receipt-press-spec.md` दें · Colour primaries (gold hub) for digital/premium; give the printer the `-book` single-ink files + the press spec for NCR duplicate books (50 sets) |
| **seal/** | मुहर · Rubber stamps | मुहर-वाले को `seal-chakra-round.pdf` (गोल Ø50, Trodat 46050/Colop R50) + `address-stamp.pdf` (75×38, Trodat 4926) + `stamp-vendor-spec.md` दें — **बैंगनी (violet) स्याही** · Give all three to the stamp shop — violet ink pad |
| **labels/** | पता-स्टिकर · Address labels (A4) | Oddy ST-8 शीट (99×68, 8 प्रति पृष्ठ) — पहले `labels-alignment-test.pdf` सादे कागज़ पर छाप कर मिलाएँ · Oddy ST-8 sheets; print the alignment test on plain paper first |
| **plates/** | मूर्ति-माप पट्ट · Murti dimension plates (A4 landscape) | `vertical-grammar-hi.pdf` कारीगरों के लिए हिंदी में, `vertical-grammar.pdf` English — दोनों A4 · Hindi edition for the craftsmen, English edition, both A4 landscape |

**नियम · Rules:** काग़ज़ ही पृष्ठभूमि है — कोई रंग की पृष्ठभूमि नहीं छपती · The
paper itself is the ground — no background is ever printed. रसीद पर कोई
कर-छूट/पंजीयन पंक्ति तब तक नहीं जब तक असली न हो · No tax/registration line on
receipts until it is real.

*नया संस्करण बनाने के लिए · To regenerate:* `python3 brand/stationery/build.py`
→ `python3 brand/stationery/checks.py` → `python3 brand/stationery/publish_print.py`

ऋतस्य पन्थाम्
