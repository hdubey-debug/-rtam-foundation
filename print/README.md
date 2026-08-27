# छपाई के लिए · To Print

*हर PDF यहाँ छपाई-तैयार है — डाउनलोड करें, 100% आकार ("Actual size") पर छापें।
कभी "Fit to page" नहीं।*
*Every PDF here is print-ready — download, print at 100% scale ("Actual size").
Never "Fit to page."*

| फ़ोल्डर · Folder | क्या है · What | कागज़ / निर्देश · Paper / Instructions |
|---|---|---|
| **letterhead/** | पत्र-शीर्ष · Letterhead (A4) | क्रीम बॉन्ड 100 gsm — BILT Royal Executive Bond "Corona Cream" · `letterhead.pdf` रंगीन प्रेस के लिए, `letterhead-mono.pdf` घर के लेज़र/फोटोकॉपी के लिए, `letterhead.docx` में पत्र टाइप करें · Cream bond 100 gsm; colour PDF for press, mono for home laser, DOCX to type letters |
| **receipt/** | दान-रसीद · Donation receipt (A5) | छापेखाने को `receipt-a5.pdf` + `receipt-cover-a5.pdf` + `receipt-press-spec.md` दें (NCR किताबें, 50 सेट) · Give all three files to the printer for NCR duplicate books; `receipt-a5-color.pdf` रंगीन/डिजिटल के लिए · colour edition for digital/premium |
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
