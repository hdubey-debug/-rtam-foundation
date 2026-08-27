# छपाई के लिए · To Print

*हर PDF छपाई-तैयार है — डाउनलोड करें, **100% आकार ("Actual size")** पर छापें।*
*Every PDF is print-ready — download, print at **100% scale ("Actual size")**.*

**पहला नियम — अपना काग़ज़ चुनें · First rule — pick your paper:** भारत में
**india-a4-paper** फ़ोल्डर, अमेरिका में **usa-letter-paper** फ़ोल्डर · In India
use the `india-a4-paper` folders; in the USA use `usa-letter-paper` (US Letter
is shorter than A4 — the wrong file loses its bottom edge).

## फ़ोल्डर गाइड · Folder guide

| फ़ोल्डर · Folder | किसके लिए · Who it's for |
|---|---|
| **letterhead/india-a4-paper/** | भारत में पत्र छापने के लिए — `letterhead-color.pdf` (रंगीन लेज़र/प्रेस) या `letterhead-black-only.pdf` (एक-रंग/फोटोकॉपी) · Printing letters in India — color, or black-only for mono printers and photocopies |
| **letterhead/usa-letter-paper/** | अमेरिका में — वही दो, US Letter काग़ज़ पर · The same two, sized for US Letter trays |
| **letterhead/cream-day-edition-a4/** | क्रीम (दिन) संस्करण — हल्का विकल्प · The cream day alternative |
| **letterhead/letterhead-typing-template.docx** | Word/Google Docs में पत्र टाइप करने के लिए — शीर्ष/तल स्थिर हैं · Type letters; head and foot are locked images |
| **receipt-book/give-to-printer/** | **यह पूरा फ़ोल्डर छापेखाने को दें** — रसीद-पृष्ठ, कवर, और छपाई-निर्देश (NCR किताबें, 50 सेट) · Hand this whole folder to the printer: page, cover, and instructions for NCR duplicate books |
| **receipt-book/color-edition/** | रंगीन रसीद (सुनहरा केंद्र) — डिजिटल/व्हाट्सऐप रसीदों और प्रीमियम छपाई के लिए · The colour receipt for digital use and premium runs |
| **stamps/** | **यह पूरा फ़ोल्डर मुहर-वाले को दें** — गोल मुहर Ø50 (Trodat 46050/Colop R50), पता-मुहर 75×38 (Trodat 4926), निर्देश — **बैंगनी स्याही** · Hand this whole folder to the stamp shop — violet ink pad |
| **address-labels/** | घर के प्रिंटर से Oddy ST-8 शीट (8 प्रति पृष्ठ) पर — **पहले** `alignment-test-print-first.pdf` सादे कागज़ पर छापें · Home-laser labels on Oddy ST-8 sheets; print the alignment test on plain paper first |
| **murti-plates/** | मूर्ति के माप-पट्ट — `murti-dimensions-hindi.pdf` कारीगरों के लिए, English भी (A4 landscape) · The murti dimension plates — Hindi for the craftsmen, English alongside |

**काग़ज़ · Paper:** पत्र-शीर्ष क्रीम बॉन्ड 100 gsm पर — BILT Royal Executive Bond
"Corona Cream" (औपचारिक: Conqueror Cream Wove) · Letterhead on cream bond
100 gsm. **नियम · Rule:** रसीद पर कोई कर-छूट/पंजीयन पंक्ति तब तक नहीं जब तक
असली न हो · No tax/registration line on receipts until it is real.

*नया संस्करण बनाने के लिए · To regenerate:* `python3 brand/stationery/build.py`
→ `checks.py` → `publish_print.py`

ऋतस्य पन्थाम्
