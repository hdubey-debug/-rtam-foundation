#!/usr/bin/env python3
"""Comparison sheets from the rendered previews.
  out/00-compare/style-NN-name.png   one style across the six images
  out/00-compare/matrix.png          every style (rows) against every image (columns)
  out/<image>/00-contact-sheet.png   one image in the nine styles
  out/00-compare/distance-test.png   the cut-out styles as tiny thumbnails (a 4 ft poster from about 30 m)"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parent.parent; OUT = ROOT / 'out'; CMP = OUT / '00-compare'
F = lambda s, w=500: ImageFont.truetype(str(ROOT / f'brand/fonts/inter-{w}.ttf'), s)
SUBJECTS = [('01-front', 'Front'), ('02-side-tower-right', 'Side, tower right'), ('03-side-tower-left', 'Side, tower left'),
            ('04-shivalinga', 'Shivalinga'), ('05-nandi', 'Nandi pavilion'), ('06-temple-and-nandi', 'Temple and Nandi')]
STYLES = [('01-adhishthana', 'Adhishthana', 'name bears the picture · 24×36 in'), ('02-shirshak', 'Shirshak', 'name on top · 24×36 in'),
          ('03-ek-rekha', 'Ek Rekha', 'one line · 2:1 hoarding'), ('04-torana', 'Torana', 'gate banner · 3:1'),
          ('05-stambha', 'Stambha', 'standee · 85×200 cm'), ('06-chandra', 'Chandra', 'day register · wall poster'),
          ('07-akasha', 'Akasha', 'alternate · sky into the dark'), ('08-dhvaja', 'Dhvaja', 'alternate · name in the picture'),
          ('09-patta', 'Patta', 'alternate · letterhead plate')]
BG, MAT, INK, QUIET = (34, 34, 34), (70, 68, 64), (201, 194, 182), (143, 136, 124)

def load(sub, sty): return Image.open(OUT / sub / f'{sty}.png').convert('RGB')

def strip(sty, name, sub, cell_w, gap=28, pad=40, head=True, cols=None):
    cols = cols or len(SUBJECTS); ims = [load(s, sty) for s, _ in SUBJECTS]
    h = round(ims[0].height * cell_w / ims[0].width); rows = -(-len(ims) // cols)
    W = pad * 2 + cols * cell_w + (cols - 1) * gap; top = pad + (64 if head else 0)
    sheet = Image.new('RGB', (W, top + rows * (h + 44) + (rows - 1) * gap + pad - 10), BG); d = ImageDraw.Draw(sheet)
    if head:
        d.text((pad, pad - 6), f'{sty[:2]}  {name.upper()}', font=F(30, 600), fill=INK); d.text((pad + 14 + d.textlength(f'{sty[:2]}  {name.upper()}', font=F(30, 600)), pad + 4), sub, font=F(20, 400), fill=QUIET)
    for i, (im, (_, lab)) in enumerate(zip(ims, SUBJECTS)):
        x = pad + (i % cols) * (cell_w + gap); y = top + (i // cols) * (h + 44 + gap)
        d.rectangle([x - 1, y - 1, x + cell_w, y + h], outline=MAT); sheet.paste(im.resize((cell_w, h), Image.LANCZOS), (x, y))
        d.text((x, y + h + 10), lab, font=F(18, 500), fill=QUIET)
    return sheet

def styles():
    CMP.mkdir(parents=True, exist_ok=True); out = []
    for sty, name, sub in STYLES:
        land = sty.startswith(('03', '04'))
        s = strip(sty, name, sub, 1040 if sty.startswith('04') else (900 if land else 560), cols=2 if sty.startswith('04') else (3 if land else 6))
        p = CMP / f'style-{sty}.png'; s.save(p); out.append((p.name, s.size))
    return out

def matrix(cell=400, gap=18, pad=36, lab_w=250):
    rows = []
    for sty, name, sub in STYLES:
        ims = [load(s, sty) for s, _ in SUBJECTS]; h = round(ims[0].height * cell / ims[0].width); rows.append((sty, name, sub, ims, h))
    W = pad * 2 + lab_w + 6 * cell + 5 * gap; H = pad + 60 + sum(r[4] + gap for r in rows) + pad
    sheet = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(sheet)
    for i, (_, lab) in enumerate(SUBJECTS): d.text((pad + lab_w + i * (cell + gap), pad), lab.upper(), font=F(20, 600), fill=INK)
    y = pad + 60
    for sty, name, sub, ims, h in rows:
        d.text((pad, y + 2), sty[:2], font=F(34, 600), fill=INK); d.text((pad, y + 46), name, font=F(22, 600), fill=INK)
        for j, part in enumerate(sub.split(' · ')): d.text((pad, y + 78 + j * 24), part, font=F(16, 400), fill=QUIET)
        for i, im in enumerate(ims):
            x = pad + lab_w + i * (cell + gap); d.rectangle([x - 1, y - 1, x + cell, y + h], outline=MAT); sheet.paste(im.resize((cell, h), Image.LANCZOS), (x, y))
        y += h + gap
    sheet.save(CMP / 'matrix.png'); return sheet.size

def contact(sub, label):
    H, gap, pad, lab = 820, 36, 48, 64
    P = [s for s in STYLES if not s[0].startswith(('03', '04'))]; L = [s for s in STYLES if s[0].startswith(('03', '04'))]
    ims = [load(sub, s[0]) for s in P]; ws = [round(i.width * H / i.height) for i in ims]
    W = sum(ws) + gap * (len(ws) - 1) + 2 * pad
    lims = [load(sub, s[0]) for s in L]; LH = 430; lws = [round(i.width * LH / i.height) for i in lims]
    sheet = Image.new('RGB', (W, pad + 70 + H + lab + gap + LH + lab + pad), BG); d = ImageDraw.Draw(sheet)
    d.text((pad, pad - 14), f'RTAMBHARESHVARA MANDIR  ·  {label.upper()}  ·  NINE STYLES', font=F(26, 500), fill=INK)
    d.text((pad, pad + 22), '01 to 06 are the proposed system; 07 to 09 are the alternates that keep the picture whole.', font=F(20, 400), fill=QUIET)
    x, y = pad, pad + 70
    for (sty, name, s2), im, w in zip(P, ims, ws):
        d.rectangle([x - 1, y - 1, x + w, y + H], outline=MAT); sheet.paste(im.resize((w, H), Image.LANCZOS), (x, y))
        d.text((x, y + H + 12), f'{sty[:2]}  {name}', font=F(22, 600), fill=INK); d.text((x, y + H + 40), s2, font=F(16, 400), fill=QUIET); x += w + gap
    x, y = pad, y + H + lab + gap
    for (sty, name, s2), im, w in zip(L, lims, lws):
        d.rectangle([x - 1, y - 1, x + w, y + LH], outline=MAT); sheet.paste(im.resize((w, LH), Image.LANCZOS), (x, y))
        d.text((x, y + LH + 12), f'{sty[:2]}  {name}', font=F(22, 600), fill=INK); d.text((x, y + LH + 40), s2, font=F(16, 400), fill=QUIET); x += w + gap
    sheet.save(OUT / sub / '00-contact-sheet.png'); return sheet.size

def distance():
    """The six images in the two lead styles, shrunk to the size a 4 ft poster (01) and an 8 ft hoarding (03) appear from about 30 m."""
    thumbs = [(lab, load(s, '01-adhishthana').resize((110, 165), Image.LANCZOS)) for s, lab in SUBJECTS] + [(lab, load(s, '03-ek-rekha').resize((220, 110), Image.LANCZOS)) for s, lab in SUBJECTS]
    gap, pad = 26, 32; W = pad * 2 + 6 * 220 + 5 * gap
    strip_ = Image.new('RGB', (W, pad * 2 + 165 + 30 + 110 + 30), (124, 121, 114)); d = ImageDraw.Draw(strip_)
    for i, (lab, t) in enumerate(thumbs[:6]):
        x = pad + i * (220 + gap); strip_.paste(t, (x + 55, pad)); d.text((x + 55, pad + 170), lab, font=F(13, 600), fill=(28, 28, 28))
    for i, (lab, t) in enumerate(thumbs[6:]):
        x = pad + i * (220 + gap); strip_.paste(t, (x, pad + 165 + 34))
    strip_.save(CMP / 'distance-test.png'); return strip_.size

if __name__ == '__main__':
    for n, sz in styles(): print(n, sz)
    print('matrix', matrix())
    for s, lab in SUBJECTS: print(s, 'contact sheet', contact(s, lab))
    print('distance', distance())
