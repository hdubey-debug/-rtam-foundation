#!/usr/bin/env python3
"""The Vertical Grammar plate, bilingual — labels shivling2.png with the locked
verticals and emits, per language:
  plates/shivling2-labeled[-hi].png
  plates/vertical-grammar[-hi].pdf   (p1 = plate, p2 = the numbers)

The jalādhārī is written as explicit arithmetic (total 38 − 9 in water =
29 visible) so builders cannot misread it. Anchors measured off this exact
image (1153x1364); if the drawing is swapped, re-measure TOP/CUP/RIM/BOT
and the drum edges.
"""
from PIL import Image, ImageDraw, ImageFont
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "plates", "shivling3.png")
OUT = os.path.join(HERE, "plates")
os.makedirs(OUT, exist_ok=True)

IVORY = (247, 243, 233)
INK = (26, 26, 26)
GOLD = (138, 106, 47)
STONE = (150, 143, 128)

F = os.path.join(HERE, "..", "brand", "fonts")
def _f(path, s): return ImageFont.truetype(os.path.join(F, path), s)
cinzel = lambda s: _f("cinzel/cinzel-600.ttf", s)
cinzelL = lambda s: _f("cinzel/cinzel-500.ttf", s)
marc = lambda s: _f("marcellus/marcellus-400.ttf", s)
tiro = lambda s: _f("tiro-devanagari-sanskrit/tiro-devanagari-sanskrit-400.ttf", s)

# measured anchors in shivling3.png pixel space (1188x1324) — fourth survey
# per the founder: the 109 INCLUDES the belt (collar), so the linga bracket
# ends below it; the jaladhari bracket rises to meet it at the same row; the
# podium bracket spans band-top (its true top surface) to the ground.
TOP = 149
BELT = 756           # below the belt — linga bottom AND jaladhari top
JB = 966             # pad bottoms — jaladhari bracket bottom
PT, PB = 838, 1140   # podium: rim-band top surface .. ground
DRUM_L, DRUM_R = 56, 1132
WATER_PT = (240, 905)

L = {
 "en": dict(
   head=cinzelL, num=cinzel, body=marc,
   title="THE MURTI — THE VERTICAL GRAMMAR",
   sub="RTAM · shivling3 study · declared design dimensions — the drawing is an illustrative ¾ perspective, not to scale",
   linga=("ŚIVALIṄGA", "109 in", "above the lotus"),
   jala_name="JALĀDHĀRĪ", jala_sub="both petal tiers",
   jala_rows=[("total", "38 in"), ("in the water", "− 9 in"), ("visible", "29 in")],
   jala_note="the rail marks the visible 29",
   podium=("PODIUM", "31 in", "ground to rim top"),
   total=("TOTAL", "169 in"),
   water=("WATER BASIN", "9 in deep"),
   dia="Ø 187 in  ·  OUTER PODIUM",
   footer="169 = 109 + 29 + 31   ·   jalādhārī 38 in total — 9 in the water, 29 in visible",
   p2title="THE VERTICAL GRAMMAR — THE NUMBERS",
   rows=[
     ("Total visible height", "169 in", "7", "the whole — 13²"),
     ("Śivaliṅga above the lotus", "109 in", "1", "the axis"),
     ("Jalādhārī, total", "38 in", "2", "the vessel"),
     ("   above the water, visible", "29 in", "2", "38 − 9 = 29"),
     ("   standing in the water", "9 in", "—", "the silent nine"),
     ("Podium (ground to rim top)", "31 in", "4", "form · support"),
     ("Water basin, stone depth", "9 in", "—", "silent"),
     ("Outer podium diameter", "Ø 187 in", "7", "the field"),
   ],
   notes=[
     "The stack: 169 = 109 + 29 + 31.  The code: 7 = 1 + 2 + 4 (whole = axis + vessel + form).",
     "To be explicit: the jalādhārī is 38 in tall in TOTAL. 9 in of it stands below the",
     "   water inside the basin, so 29 in shows above the water.  38 − 9 = 29.",
     "Dictated '165.69' read as 169 — the locked total; the stack confirms it.",
     "On record, not yet ratified (GRAMMAR.md §2b): the silent-nine shift — podium 40 ·",
     "   jalādhārī 29 (20 above the rim) · floor 31 — same total, every digit root unchanged.",
     "Waterline open: 38 in (water depth 7, freeboard 2) — or brimful at the rim.",
   ],
   foot1="RTAM · murti-3d/plates · 2026-08-25", foot2="ऋतस्य पन्थाम्",
   plate_no="PLATE I — THE VERTICAL GRAMMAR",
   equation="169 = 109 + 29 + 31   ·   digit roots 7 = 1 + 2 + 4",
   cart_note="declared design dimensions · not to scale",
   date_label="", date_value="2026 · 08 · 25",
   seal_caption="the seal is the murti seen from above",
   png="shivling3-labeled.png", pdf="vertical-grammar.pdf",
 ),
 "hi": dict(
   head=tiro, num=tiro, body=tiro,
   title="मूर्ति — ऊँचाई के माप",
   sub="ऋतम् · shivling3 · निर्धारित डिज़ाइन-माप — चित्र केवल संदर्भ हेतु (¾ दृश्य), पैमाने पर नहीं",
   linga=("शिवलिंग", "109 इंच", "कमल के ऊपर"),
   jala_name="जलाधारी", jala_sub="दोनों पंखुड़ी-स्तर",
   jala_rows=[("कुल ऊँचाई", "38 इंच"), ("जल में डूबी", "− 9 इंच"), ("जल के ऊपर दृश्य", "29 इंच")],
   jala_note="यह रेखा दृश्य 29 इंच नापती है",
   podium=("आधार-मंच", "31 इंच", "भूमि से किनारे तक"),
   total=("कुल ऊँचाई", "169 इंच"),
   water=("जल-कुंड", "9 इंच गहरा"),
   dia="व्यास 187 इंच · बाहरी घेरा",
   footer="169 = 109 + 29 + 31 · जलाधारी कुल 38 इंच — 9 इंच जल में, 29 इंच जल के ऊपर",
   p2title="ऊँचाई के माप — तालिका",
   rows=[
     ("कुल दृश्य ऊँचाई", "169 इंच", "7", "पूर्ण — 13²"),
     ("शिवलिंग (कमल के ऊपर)", "109 इंच", "1", "अक्ष — केंद्र"),
     ("जलाधारी — कुल", "38 इंच", "2", "पात्र"),
     ("   जल के ऊपर (दृश्य)", "29 इंच", "2", "38 − 9 = 29"),
     ("   जल में डूबी", "9 इंच", "—", "मौन नौ"),
     ("आधार-मंच — भूमि से किनारे तक", "31 इंच", "4", "रूप — आधार"),
     ("जल-कुंड की गहराई (पत्थर)", "9 इंच", "—", "मौन"),
     ("बाहरी व्यास", "Ø 187 इंच", "7", "क्षेत्र"),
   ],
   notes=[
     "योग: 169 = 109 + 29 + 31 · संकेत: 7 = 1 + 2 + 4 (पूर्ण = अक्ष + पात्र + रूप)।",
     "स्पष्टीकरण: जलाधारी की कुल ऊँचाई 38 इंच है। इसमें से 9 इंच जल के भीतर रहती है,",
     "   इसलिए जल के ऊपर केवल 29 इंच दिखाई देती है।  38 − 9 = 29।",
     "चित्र-जाँच: चौड़ाई और शिवलिंग घोषित मापों से मेल खाते हैं; चित्र में जलाधारी-भाग",
     "   कुछ बड़ा दिखता है — मान्य माप घोषित संख्याएँ ही हैं, चित्र केवल संदर्भ है।",
     "विकल्प (अभी स्वीकृत नहीं): आधार-मंच 40 इंच · जलाधारी 29 इंच — कुल वही 169,",
     "   प्रत्येक अंक-मूल वही रहता है।",
     "जल-रेखा का निर्णय शेष: 38 इंच (जल-गहराई 7, किनारा 2 ऊपर) — अथवा किनारे तक भरा।",
   ],
   foot1="ऋतम् फाउंडेशन · murti-3d/plates · 2026-08-25", foot2="ऋतस्य पन्थाम्",
   plate_no="माप-पट्ट I — ऊँचाई के माप",
   equation="169 = 109 + 29 + 31 · अंक-मूल 7 = 1 + 2 + 4",
   cart_note="निर्धारित डिज़ाइन-माप · पैमाने पर नहीं",
   date_label="दिनांक", date_value="२०२६ · ०८ · २५",
   seal_caption="यह मुहर ऊपर से देखी गई मूर्ति है।",
   png="shivling3-labeled-hi.png", pdf="vertical-grammar-hi.pdf",
 ),
}


def corner_block(canvas, dcv, T, lang, ax1, ay1):
    """Tiny bordered block, bottom-right anchored at (ax1, ay1)."""
    AST = os.path.join(OUT, "assets")
    fs_t = cinzelL(24) if lang == "en" else tiro(26)
    fs_d = cinzel(24) if lang == "en" else tiro(24)
    line1 = T["plate_no"]
    line2 = T["date_value"]
    w_text = max(dcv.textlength(line1, font=fs_t), dcv.textlength(line2, font=fs_d))
    bw = int(100 + 24 + w_text + 56)
    bh = 148
    bx0, by0 = ax1 - bw, ay1 - bh
    dcv.rectangle([bx0, by0, ax1, ay1], outline=INK, width=2)
    seal = Image.open(os.path.join(AST, "brand-seal-chakra-kanaka.png")).convert("RGBA")
    seal = seal.resize((100, 100), Image.LANCZOS)
    canvas.paste(seal, (bx0 + 20, by0 + (bh - 100) // 2), seal)
    tx = bx0 + 140
    dcv.text((tx, by0 + 34), line1, font=fs_t, fill=INK)
    dcv.text((tx, by0 + 82), line2, font=fs_d, fill=GOLD)

def build(lang):
    T = L[lang]
    head, num, body = T["head"], T["num"], T["body"]
    ML, MR, MT, MB = 770, 500, 150, 240
    img = Image.open(SRC).convert("RGB")
    W, H = img.size
    sheet = Image.new("RGB", (W + ML + MR, H + MT + MB), IVORY)
    sheet.paste(img, (ML, MT))
    d = ImageDraw.Draw(sheet)
    X = lambda x: x + ML
    Y = lambda y: y + MT

    def tick(x, y):
        d.line([x - 13, y + 13, x + 13, y - 13], fill=INK, width=6)
    def vrail(x, y0, y1):
        d.line([x, y0, x, y1], fill=INK, width=5); tick(x, y0); tick(x, y1)
    def hrail(y, x0, x1):
        d.line([x0, y, x1, y], fill=INK, width=5); tick(x0, y); tick(x1, y)
    def ext(x0, y, x1): d.line([x0, y, x1, y], fill=STONE, width=3)
    def extv(x, y0, y1): d.line([x, y0, x, y1], fill=STONE, width=3)

    # ZIGZAG marking (founder's layout): right — Sivalinga (upper) and
    # Podium (lower); left — Jaladhari with its arithmetic; Total outermost
    # left. One measure per lane, nothing stacked.
    xr = X(W) + 60

    def simple_label(ymid, name, val, sub=None):
        d.text((xr + 26, ymid - 48), name, font=head(32), fill=INK)
        d.text((xr + 26, ymid - 6), val, font=num(40), fill=GOLD)
        if sub: d.text((xr + 26, ymid + 46), sub, font=body(24), fill=STONE)

    # right upper: the linga (includes the belt)
    ext(X(748), Y(TOP), xr + 14)
    ext(X(768), Y(BELT), xr + 14)
    vrail(xr, Y(TOP), Y(BELT))
    simple_label((Y(TOP) + Y(BELT)) // 2, *T["linga"])

    # right lower: the podium, band top to ground
    ext(X(1122), Y(PT), xr + 14)
    ext(X(1085), Y(PB), xr + 14)
    vrail(xr, Y(PT), Y(PB))
    simple_label((Y(PT) + Y(PB)) // 2 + 30, *T["podium"])

    # left middle: the jaladhari — bracket on the lotus, arithmetic beside it
    xjl = X(0) - 70
    ext(X(330), Y(BELT), xjl - 14)
    ext(X(240), Y(JB), xjl - 14)
    vrail(xjl, Y(BELT), Y(JB))
    bx0, by = 300, Y(732)
    d.text((bx0, by), T["jala_name"], font=head(32), fill=INK)
    d.text((bx0 + d.textlength(T["jala_name"], font=head(32)) + 16, by + 6),
           "· " + T["jala_sub"], font=body(24), fill=STONE)
    ry = by + 52
    colv = 600
    for i, (lab, val) in enumerate(T["jala_rows"]):
        gold = i == 2
        d.text((bx0, ry), lab, font=body(28), fill=INK)
        d.text((colv + 60, ry - 4), val, font=num(32 if gold else 30),
               fill=GOLD if gold else INK, anchor="ra")
        ry += 44
        if i == 1:
            d.line([colv - 110, ry - 4, colv + 62, ry - 4], fill=INK, width=2)
            ry += 8

    # outermost left: the total
    xl = 250
    ext(X(445), Y(TOP), xl - 14); ext(X(140), Y(PB) - 4, xl - 14)
    vrail(xl, Y(TOP), Y(PB))
    d.text((xl - 30, (Y(TOP) + Y(PB)) // 2 - 52), T["total"][0], font=head(32), fill=INK, anchor="ra")
    d.text((xl - 30, (Y(TOP) + Y(PB)) // 2 - 8), T["total"][1], font=num(40), fill=GOLD, anchor="ra")

    # bottom rail: diameter
    yb = Y(1338)   # below the drawing's own frame
    DIA_EXT_Y = 1000
    extv(X(DRUM_L), Y(DIA_EXT_Y), yb + 14); extv(X(DRUM_R), Y(DIA_EXT_Y), yb + 14)
    hrail(yb, X(DRUM_L), X(DRUM_R))
    d.text((X((DRUM_L + DRUM_R) // 2), yb + 26), T["dia"], font=num(38), fill=GOLD, anchor="ma")

    # water basin callout (upper-left sky)
    wx, wy = X(WATER_PT[0]), Y(WATER_PT[1])
    d.text((X(46), Y(300)), T["water"][0], font=head(30), fill=INK)
    d.text((X(46), Y(340)), T["water"][1], font=num(34), fill=GOLD)
    d.line([X(150), Y(392), wx, wy], fill=GOLD, width=2)
    d.ellipse([wx - 6, wy - 6, wx + 6, wy + 6], fill=GOLD)

    # title + footer
    tfont = cinzel(44) if lang == "en" else tiro(46)
    d.text((X(10), 30), T["title"], font=tfont, fill=INK)
    d.text((X(10), 96), T["sub"], font=body(26), fill=STONE)
    d.text((X(10), sheet.height - 74), T["footer"], font=body(28), fill=INK)
    corner_block(sheet, d, T, lang, sheet.width - 44, sheet.height - 40)

    plate_png = os.path.join(OUT, T["png"])
    sheet.save(plate_png)

    # PDF — LANDSCAPE A4: the plate is a landscape sheet, so the page is too.
    # Page 1 carries the plate at ~90% of the page; page 2 the numbers, airy.
    A4L = (2339, 1654)  # 200 dpi landscape
    p1 = Image.new("RGB", A4L, IVORY)
    fit = min((A4L[0] - 90) / sheet.width, (A4L[1] - 90) / sheet.height)
    sc = sheet.resize((int(sheet.width * fit), int(sheet.height * fit)), Image.LANCZOS)
    p1.paste(sc, ((A4L[0] - sc.width) // 2, (A4L[1] - sc.height) // 2))

    # merge manual wrap-continuations (lines starting with spaces) — the
    # landscape measure holds them on one line
    merged = []
    for n in T["notes"]:
        if n.startswith("   ") and merged:
            merged[-1] = merged[-1].rstrip() + " " + n.strip()
        else:
            merged.append(n)
    meas = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    notes = []
    for m in merged:
        words, line = m.split(" "), ""
        for w2 in words:
            t2 = (line + " " + w2).strip()
            if meas.textlength(t2, font=body(33)) > 2040 and line:
                notes.append(line); line = "   " + w2
            else:
                line = t2
        notes.append(line)

    p2 = Image.new("RGB", A4L, IVORY)
    d2 = ImageDraw.Draw(p2)
    yy = 96
    d2.text((140, yy), T["p2title"], font=(cinzel(50) if lang == "en" else tiro(52)), fill=INK)
    tw2 = d2.textlength(T["p2title"], font=(cinzel(50) if lang == "en" else tiro(52)))
    d2.ellipse([140 + tw2 + 18, yy + 24, 140 + tw2 + 38, yy + 44], fill=GOLD)
    yy += 118
    for name, val, root, note in T["rows"]:
        d2.text((140, yy), name, font=head(34), fill=INK)
        d2.text((1150, yy), val, font=num(36), fill=GOLD)
        d2.text((1440, yy), root, font=num(34), fill=INK)
        d2.text((1580, yy), note, font=body(32), fill=STONE)
        yy += 84
    yy += 36
    d2.line([140, yy, A4L[0] - 140, yy], fill=STONE, width=2); yy += 56
    for n in notes:
        d2.text((140, yy), n, font=body(33), fill=INK); yy += 58
    corner_block(p2, d2, T, lang, A4L[0] - 80, A4L[1] - 40)
    d2.text((140, A4L[1] - 84), T["foot1"], font=body(28), fill=STONE)
    d2.text((140 + d2.textlength(T["foot1"], font=body(28)) + 44, A4L[1] - 86),
            T["foot2"], font=tiro(30), fill=STONE)

    # cover — professional title sheet: one big title, and the rectangular
    # title-block at the bottom (lockup | plate | date | seal), each in its
    # own ruled cell. Nothing overlaps anything.
    AST = os.path.join(OUT, "assets")
    cover = Image.new("RGB", A4L, IVORY)
    dc = ImageDraw.Draw(cover)
    ctitle = cinzel(64) if lang == "en" else tiro(68)
    dc.text((170, 640), T["title"], font=ctitle, fill=INK)

    bx0, by0, bx1, by1 = 150, 1280, 2189, 1510
    dc.rectangle([bx0, by0, bx1, by1], outline=INK, width=2)
    cA, cB, cC = 710, 1500, 1930          # cell dividers
    for cx in (cA, cB, cC):
        dc.line([cx, by0, cx, by1], fill=STONE, width=1)
    cyc = (by0 + by1) // 2
    # cell 1 — lockup
    lock = Image.open(os.path.join(AST, "brand-lockup-mandir.png")).convert("RGBA")
    lock = lock.resize((440, int(lock.height * 440 / lock.width)), Image.LANCZOS)
    cover.paste(lock, (bx0 + (cA - bx0 - lock.width) // 2, cyc - lock.height // 2), lock)
    # cell 2 — plate designation
    dc.text((cA + 34, cyc - 40), T["plate_no"], font=(cinzelL(30) if lang == "en" else tiro(32)), fill=INK)
    dc.text((cA + 34, cyc + 10), T["cart_note"], font=body(23), fill=STONE)
    # cell 3 — date
    dl = T["date_label"] if T["date_label"] else ("DATE" if lang == "en" else "")
    if dl:
        dc.text((cB + 34, cyc - 42), dl, font=(head(22) if lang == "en" else tiro(24)), fill=STONE)
    dc.text((cB + 34, cyc + 2), T["date_value"], font=num(32), fill=INK)
    # cell 4 — the stamp, in its own field
    seal = Image.open(os.path.join(AST, "brand-seal-chakra-kanaka.png")).convert("RGBA")
    seal = seal.resize((180, 180), Image.LANCZOS)
    cover.paste(seal, (cC + (bx1 - cC - 180) // 2, cyc - 90), seal)

    pdf = os.path.join(OUT, T["pdf"])
    cover.save(pdf, save_all=True, append_images=[p1, p2], resolution=200)
    print("wrote", plate_png)
    print("wrote", pdf)

for lang in ("en", "hi"):
    build(lang)
