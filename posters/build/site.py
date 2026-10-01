#!/usr/bin/env python3
"""Build the public review site next to the sources: index.html, img/, sheets/, fonts/.

The page is static (GitHub Pages): reviewers compare the posters by style or by image, select the ones they like, and
send their selection as a message (WhatsApp, share sheet or copy). Nothing is uploaded; the selection lives in the
reviewer's browser and in the link.  usage: python3 site.py"""
import shutil, html as H
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parent.parent; OUT = ROOT / 'out'
BASE_URL = 'https://hdubey-debug.github.io/-rtam-foundation/posters/'

# (folder, letter, English, Hindi, note_hi, note_en)
SUBJECTS = [('01-front', 'A', 'Front', 'सामने से', 'मंदिर का सामने का दृश्य।', 'The temple seen from the front.'),
            ('02-side-tower-right', 'B', 'Side, tower right', 'बगल से, शिखर दाईं ओर', 'सीढ़ियाँ बाईं ओर, शिखर दाईं ओर।', 'Steps on the left, tower on the right.'),
            ('03-side-tower-left', 'C', 'Side, tower left', 'बगल से, शिखर बाईं ओर', 'सीढ़ियाँ दाईं ओर, शिखर बाईं ओर।', 'Steps on the right, tower on the left.'),
            ('04-shivalinga', 'D', 'Shivalinga', 'शिवलिंग', 'भीतर का दृश्य। काले पोस्टरों में केवल शिवलिंग है।', 'The interior. On the black posters the Shivalinga stands alone.'),
            ('05-nandi', 'E', 'Nandi pavilion', 'नंदी मंडप', 'काले पोस्टरों में नंदी की मूर्ति थोड़ी उजली की गई है।', 'On the black posters the Nandi statue has been brightened.'),
            ('06-temple-and-nandi', 'F', 'Temple and Nandi', 'मंदिर और नंदी', 'यह चित्र दो अलग चित्रों को जोड़कर बनाया गया है।', 'This image is composed from two separate pictures.')]
# (file, digit, English, Hindi, size, desc_hi, desc_en, shape)
STYLES = [('01-adhishthana', '1', 'Adhishthana', 'अधिष्ठान', '24 × 36 in', 'नाम के ऊपर मंदिर। खड़ा पोस्टर।', 'The picture stands on the name. Upright poster.', 'up'),
          ('02-shirshak', '2', 'Shirshak', 'शीर्षक', '24 × 36 in', 'नाम ऊपर, चित्र नीचे। ज़मीन के पास लगने वाले फ्लेक्स के लिए।', 'Name on top, picture below. For flex hung near the ground.', 'up'),
          ('03-ek-rekha', '3', 'Ek Rekha', 'एक रेखा', '2 : 1', 'चौड़ा होर्डिंग। नाम और चित्र एक ही रेखा पर।', 'Wide hoarding. The name and the picture stand on one line.', 'w2'),
          ('04-torana', '4', 'Torana', 'तोरण', '3 : 1', 'लंबा बैनर, द्वार या सड़क के लिए।', 'Long banner for a gate or a street.', 'w3'),
          ('05-stambha', '5', 'Stambha', 'स्तम्भ', '85 × 200 cm', 'स्टैंडी। नाम आँखों की ऊँचाई पर।', 'Standee. The name sits at eye level.', 'up'),
          ('06-chandra', '6', 'Chandra', 'चन्द्र', '24 × 36 in', 'हल्की पृष्ठभूमि, भीतर की दीवारों के लिए।', 'Light ground, for indoor walls.', 'up'),
          ('07-akasha', '7', 'Akasha', 'आकाश', '24 × 36 in', 'विकल्प। आकाश ऊपर जाकर काले में घुल जाता है।', 'Alternate. The sky deepens into the black.', 'up'),
          ('08-dhvaja', '8', 'Dhvaja', 'ध्वज', '24 × 36 in', 'विकल्प। नाम चित्र के भीतर लिखा है।', 'Alternate. The name is set inside the picture.', 'up'),
          ('09-patta', '9', 'Patta', 'पट्ट', '24 × 36 in', 'विकल्प। लेटरहेड जैसा, संस्थापकों के नाम के साथ।', 'Alternate. Like the letterhead, with the founders line.', 'up')]
THUMB_W = {'up': 520, 'w2': 900, 'w3': 1100}

def webp(im, path, q):
    path.parent.mkdir(parents=True, exist_ok=True); im.save(path, 'WEBP', quality=q, method=6); return path.stat().st_size

def images():
    total = 0; sizes = {}
    for sub, letter, *_ in SUBJECTS:
        for sty, digit, _, _, _, _, _, shape in STYLES:
            code = letter + digit; im = Image.open(OUT / sub / f'{sty}.png').convert('RGB')
            tw = THUMB_W[shape]; th = round(im.height * tw / im.width)
            total += webp(im.resize((tw, th), Image.LANCZOS), ROOT / 'img' / 'thumb' / f'{code}.webp', 78)
            total += webp(im, ROOT / 'img' / 'full' / f'{code}.webp', 84); sizes[code] = (tw, th)
    return sizes, total

# ---------------------------------------------------------------- sheets that can be forwarded as pictures (JPEG, with codes)
BG, MAT, INK, QUIET, GOLD = (20, 20, 20), (70, 68, 64), (201, 194, 182), (143, 136, 124), (200, 161, 90)
F = lambda s, w=500: ImageFont.truetype(str(ROOT / f'brand/fonts/inter-{w}.ttf'), s)

def strip(sty, digit, name, size, cell_w, cols):
    ims = [Image.open(OUT / s[0] / f'{sty}.png').convert('RGB') for s in SUBJECTS]; gap, pad = 26, 40
    h = round(ims[0].height * cell_w / ims[0].width); rows = -(-len(ims) // cols)
    W = pad * 2 + cols * cell_w + (cols - 1) * gap; top = pad + 66
    sheet = Image.new('RGB', (W, top + rows * (h + 58) + (rows - 1) * gap + pad - 14), BG); d = ImageDraw.Draw(sheet)
    title = f'{digit}  {name.upper()}'; d.text((pad, pad - 6), title, font=F(32, 600), fill=INK)
    d.text((pad + 16 + d.textlength(title, font=F(32, 600)), pad + 6), f'{size}   ·   Rtambhareshvara Mandir poster review', font=F(20, 400), fill=QUIET)
    for i, (im, s) in enumerate(zip(ims, SUBJECTS)):
        x = pad + (i % cols) * (cell_w + gap); y = top + (i // cols) * (h + 58 + gap)
        d.rectangle([x - 1, y - 1, x + cell_w, y + h], outline=MAT); sheet.paste(im.resize((cell_w, h), Image.LANCZOS), (x, y))
        code = s[1] + digit; d.text((x, y + h + 10), code, font=F(30, 600), fill=GOLD); d.text((x + 16 + d.textlength(code, font=F(30, 600)), y + h + 18), s[2], font=F(20, 500), fill=INK)
    p = ROOT / 'sheets' / f'style-{digit}.jpg'; p.parent.mkdir(exist_ok=True); sheet.save(p, 'JPEG', quality=86, optimize=True, subsampling=0); return p.stat().st_size

def matrix(cell=400, gap=18, pad=40, lab_w=210):
    rows = []
    for sty, digit, name, _, size, *_ in STYLES:
        ims = [Image.open(OUT / s[0] / f'{sty}.png').convert('RGB') for s in SUBJECTS]; rows.append((digit, name, size, ims, round(ims[0].height * cell / ims[0].width)))
    W = pad * 2 + lab_w + 6 * cell + 5 * gap; H = pad + 86 + sum(r[4] + gap for r in rows) + pad
    sheet = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(sheet)
    for i, s in enumerate(SUBJECTS):
        x = pad + lab_w + i * (cell + gap); d.text((x, pad - 8), s[1], font=F(44, 600), fill=GOLD); d.text((x + 46, pad + 10), s[2].upper(), font=F(19, 600), fill=INK)
    y = pad + 86
    for digit, name, size, ims, h in rows:
        d.text((pad, y - 4), digit, font=F(56, 600), fill=GOLD); d.text((pad, y + 62), name, font=F(22, 600), fill=INK); d.text((pad, y + 94), size, font=F(16, 400), fill=QUIET)
        for i, im in enumerate(ims):
            x = pad + lab_w + i * (cell + gap); d.rectangle([x - 1, y - 1, x + cell, y + h], outline=MAT); sheet.paste(im.resize((cell, h), Image.LANCZOS), (x, y))
        y += h + gap
    p = ROOT / 'sheets' / 'all-54.jpg'; sheet.save(p, 'JPEG', quality=84, optimize=True); return p.stat().st_size

def preview():
    """Link-preview picture (1200 x 630): the front hoarding on the brand black."""
    im = Image.open(OUT / '01-front' / '03-ek-rekha.png').convert('RGB').resize((1200, 600), Image.LANCZOS)
    card = Image.new('RGB', (1200, 630), BG); card.paste(im, (0, 15)); p = ROOT / 'sheets' / 'preview.jpg'; card.save(p, 'JPEG', quality=86, optimize=True); return p.stat().st_size

def fonts():
    """Self-hosted web fonts, the same files the foundation's website ships."""
    dst = ROOT / 'fonts'; src = ROOT.parent / 'website' / 'dist' / 'assets' / 'fonts'
    if src.exists():
        dst.mkdir(exist_ok=True)
        for f in src.iterdir():
            if f.suffix in ('.woff2', '.txt'): shutil.copy2(f, dst / f.name)
    return sorted(p.name for p in dst.glob('*')) if dst.exists() else []

CSS = '''
@font-face{font-family:'Tiro';font-weight:400;font-display:swap;src:url('fonts/tiro-400.woff2') format('woff2')}
@font-face{font-family:'Cinzel';font-weight:500;font-display:swap;src:url('fonts/cinzel-500.woff2') format('woff2')}
@font-face{font-family:'Inter';font-weight:400;font-display:swap;src:url('fonts/inter-400.woff2') format('woff2')}
@font-face{font-family:'Inter';font-weight:600;font-display:swap;src:url('fonts/inter-600.woff2') format('woff2')}
/* A review bench in the brand's day register: posters hang on a wall-toned mat; a sticky bar chooses what to compare. */
:root{--ground:#EDEBE6;--ink:#1A1A1A;--quiet:#5C574F;--hair:rgba(26,26,26,.16);--accent:#7A5423;--gold:#C8A15A;--wall:#D8D4CA;--chip:#E2DFD8;--on-accent:#F3F1EC;--wa:#1F7A4D;
  --display:'Cinzel','Trajan Pro',Georgia,serif;--body:'Inter',system-ui,-apple-system,'Segoe UI',sans-serif;--deva:'Tiro','Noto Serif Devanagari','Kohinoor Devanagari',serif;color-scheme:light}
@media (prefers-color-scheme:dark){:root{--ground:#141414;--ink:#C9C2B6;--quiet:#8F887C;--hair:rgba(201,194,182,.2);--accent:#C8A15A;--wall:#2C2A27;--chip:#232220;--on-accent:#141414;--wa:#3FA06B;color-scheme:dark}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--ground);color:var(--ink);font:400 16px/1.6 var(--body);padding:0 max(16px,3vw)}
[hidden]{display:none!important}
img{max-width:100%}
.wrap{max-width:1560px;margin:0 auto;padding:36px 0 72px;display:flex;flex-direction:column;gap:52px}
[lang="hi"]{font-family:var(--deva)}
header.top{display:flex;flex-direction:column;gap:14px;max-width:50rem}
.eyebrow{font:600 .76rem/1.2 var(--body);letter-spacing:.2em;text-transform:uppercase;color:var(--quiet);display:flex;align-items:center;gap:.7em;flex-wrap:wrap}
.eyebrow [lang="hi"]{font:400 1.2rem/1 var(--deva);letter-spacing:0;text-transform:none;color:var(--ink)}
.bindu{width:.5em;height:.5em;border-radius:50%;background:var(--gold);display:inline-block}
h1{margin:0;display:flex;flex-direction:column;gap:6px}
h1 [lang="hi"]{font:400 clamp(2.1rem,6vw,3.2rem)/1.15 var(--deva)}
h1 .en{font:500 clamp(.95rem,2.2vw,1.2rem)/1.2 var(--display);letter-spacing:.16em;text-transform:uppercase;color:var(--quiet)}
h2{font:500 1rem/1.3 var(--display);letter-spacing:.14em;text-transform:uppercase;margin:0;padding-bottom:12px;border-bottom:1px solid var(--hair);display:flex;gap:.7em;align-items:baseline;flex-wrap:wrap}
h2 [lang="hi"]{font:400 1.25rem/1.2 var(--deva);letter-spacing:0;text-transform:none}
h3{font:500 1.1rem/1.3 var(--display);letter-spacing:.1em;text-transform:uppercase;margin:0;display:flex;align-items:baseline;gap:.5em;flex-wrap:wrap}
h3 .no{font:600 1.15rem/1 var(--body);color:var(--accent);letter-spacing:0}
h3 [lang="hi"]{font:400 1.2rem/1 var(--deva);letter-spacing:0;text-transform:none;color:var(--quiet)}
p{margin:0;max-width:48rem}
.hi{font-family:var(--deva);font-size:1.06em;line-height:1.7}
.en{color:var(--quiet)}
.pair{display:flex;flex-direction:column;gap:2px}
section{display:flex;flex-direction:column;gap:20px}
ol.steps{margin:0;padding:0;list-style:none;display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:14px 28px;counter-reset:s;max-width:66rem}
ol.steps li{counter-increment:s;display:grid;grid-template-columns:auto 1fr;gap:0 12px;padding-top:12px;border-top:1px solid var(--hair)}
ol.steps li::before{content:counter(s);font:600 1.1rem/1.5 var(--body);color:var(--accent)}
button,a.btn{font:inherit;color:inherit}
.bar{position:sticky;top:0;z-index:5;background:var(--ground);padding:10px 0;border-bottom:1px solid var(--hair);display:flex;flex-direction:column;gap:8px}
.seg{display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-size:.85rem;color:var(--quiet)}
.seg button,.tab,.pick,.btn{all:unset;box-sizing:border-box;cursor:pointer;font:600 .84rem/1.2 var(--body);padding:9px 12px;border:1px solid var(--hair);border-radius:4px;color:var(--ink);white-space:nowrap;display:inline-flex;align-items:center;gap:.45em}
.seg button [lang="hi"],.pick [lang="hi"],.btn [lang="hi"]{font:400 1.02rem/1 var(--deva)}
.seg button[aria-pressed="true"],.tab[aria-pressed="true"]{background:var(--ink);color:var(--ground);border-color:var(--ink)}
.tab b{font-weight:600;color:var(--accent)} .tab[aria-pressed="true"] b{color:var(--gold)}
.tabs{display:flex;gap:6px;overflow-x:auto;padding-bottom:2px;scrollbar-width:thin}
button:focus-visible,a:focus-visible,input:focus-visible,textarea:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.sethead{display:flex;flex-direction:column;gap:6px;margin-bottom:18px}
#stage{display:flex;flex-direction:column;gap:52px}
.grid{display:grid;gap:26px 20px;align-items:start}
.g-up{grid-template-columns:repeat(3,minmax(0,1fr))}
.g-w2,.g-w3{grid-template-columns:repeat(2,minmax(0,1fr))}
.g-four{grid-template-columns:repeat(4,minmax(0,1fr))}
.g-pair{grid-template-columns:minmax(0,2fr) minmax(0,3fr)}
.groups{display:flex;flex-direction:column;gap:34px}
.group{display:flex;flex-direction:column;gap:12px}
.gl{font:600 .72rem/1.2 var(--body);letter-spacing:.18em;text-transform:uppercase;color:var(--quiet)}
.piece{margin:0;display:flex;flex-direction:column;gap:8px;min-width:0}
.shot{all:unset;box-sizing:border-box;display:block;width:100%;cursor:zoom-in;background:var(--wall);padding:clamp(7px,1.1vw,15px);line-height:0}
.shot img{display:block;width:100%;height:auto}
.piece.picked .shot{box-shadow:0 0 0 3px var(--accent)}
figcaption{display:flex;align-items:center;gap:8px 10px;flex-wrap:wrap;font-size:.88rem;min-width:0}
.code{font:600 .95rem/1 var(--body);color:var(--on-accent);background:var(--accent);padding:5px 7px;border-radius:3px;letter-spacing:.04em}
.cap{flex:1 1 auto;min-width:0;overflow-wrap:anywhere}
.by-style .cap-style,.by-image .cap-image{display:none}
.pick{padding:7px 11px;font-size:.8rem}
.pick[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:var(--on-accent)}
#picklist{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:8px}
#picklist li{display:flex;align-items:center;gap:8px;background:var(--chip);border-radius:4px;padding:5px 5px 5px 6px;font-size:.88rem}
#picklist button{all:unset;cursor:pointer;padding:3px 9px;color:var(--quiet);border-radius:3px;font-size:1.05rem;line-height:1}
.form{display:grid;grid-template-columns:repeat(auto-fit,minmax(16rem,1fr));gap:16px 24px;max-width:66rem}
label{display:flex;flex-direction:column;gap:6px;font-size:.86rem;color:var(--quiet)}
label [lang="hi"]{font-size:1.05rem;color:var(--ink)}
input[type=text],textarea{font:400 1rem/1.5 var(--body);color:var(--ink);background:var(--chip);border:1px solid var(--hair);border-radius:4px;padding:10px 12px;width:100%}
textarea{min-height:5.2rem;resize:vertical}
#msg{min-height:9rem;font:400 .86rem/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;max-width:66rem}
.row{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.btn.primary{background:var(--wa);border-color:var(--wa);color:#fff;padding:12px 16px;font-size:.92rem}
.btn[aria-disabled="true"],.btn:disabled{opacity:.45;cursor:default;pointer-events:none}
.note{color:var(--quiet);font-size:.9rem}
.notice{background:var(--chip);border-left:3px solid var(--accent);padding:10px 14px;max-width:48rem;font-size:.92rem}
ul.plain{margin:0;padding-left:1.15em;display:flex;flex-direction:column;gap:12px;max-width:50rem}
.links{display:flex;flex-wrap:wrap;gap:8px}
footer{border-top:1px solid var(--hair);padding-top:18px;color:var(--quiet);font-size:.85rem;display:flex;gap:.8em;flex-wrap:wrap;align-items:baseline}
#lb{position:fixed;inset:0;background:rgba(12,12,12,.97);display:grid;grid-template-rows:auto minmax(0,1fr) auto;gap:10px;padding:12px 12px 14px;z-index:10}
#lb .lbtop,#lb .lbfoot{display:flex;align-items:center;justify-content:space-between;gap:10px;color:#C9C2B6;font-size:.9rem;flex-wrap:wrap}
#lb .lbimg{display:flex;align-items:center;justify-content:center;min-height:0;cursor:zoom-out}
#lb img{max-width:100%;max-height:100%;width:auto;height:auto;object-fit:contain}
#lb button,#lb a{all:unset;box-sizing:border-box;cursor:pointer;white-space:nowrap;color:#C9C2B6;font:600 .78rem/1 var(--body);letter-spacing:.1em;text-transform:uppercase;padding:11px 12px;border:1px solid rgba(201,194,182,.35);border-radius:4px}
#lb button [lang="hi"]{font:400 1rem/1 var(--deva);letter-spacing:0;text-transform:none}
#lb button[aria-pressed="true"]{background:#C8A15A;border-color:#C8A15A;color:#141414}
#lb button:focus-visible,#lb a:focus-visible{outline:2px solid #C8A15A;outline-offset:2px}
#lbcap b{color:#C8A15A;font-size:1.1rem;margin-right:.5em}
#lb .lbfoot{flex-wrap:nowrap}
#lbprev,#lbnext{font-size:1rem!important;letter-spacing:0!important}
#lbprev .w,#lbnext .w{font-size:.78rem;letter-spacing:.1em}
@media (max-width:520px){#lbprev .w,#lbnext .w{display:none}#lb button,#lb a{padding:11px 10px;letter-spacing:.06em}#lbprev,#lbnext{padding:9px 14px!important;font-size:1.25rem!important}}
@media (min-width:1500px){.g-up{grid-template-columns:repeat(6,minmax(0,1fr))}.g-w2{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media (max-width:1000px){.g-four{grid-template-columns:repeat(2,minmax(0,1fr))}.g-w3,.g-pair{grid-template-columns:minmax(0,1fr)}}
@media (max-width:640px){.g-up{grid-template-columns:repeat(2,minmax(0,1fr))}.g-w2{grid-template-columns:minmax(0,1fr)}.wrap{gap:40px;padding:24px 0 60px}.grid{gap:22px 12px}}
@media (prefers-reduced-motion:no-preference){.shot img{transition:opacity .2s}}
'''

JS = r'''
(function(){
  var META = __META__;
  var stage = document.getElementById('stage'), tabs = document.getElementById('tabs');
  var sets = Array.prototype.slice.call(stage.querySelectorAll('.set'));
  var styleTabs = tabs.innerHTML, imageTabs = document.getElementById('imagetabs').innerHTML;
  var mode = 'style', cur = {style: '1', image: 'A'}, built = {};
  function store(k, v){ try { localStorage.setItem(k, v); } catch(e){} }
  function read(k){ try { return localStorage.getItem(k); } catch(e){ return null; } }
  try { var v = JSON.parse(read('rtam-posters-view') || 'null'); if (v && (v.mode === 'style' || v.mode === 'image')) { mode = v.mode; if (/^[1-9]$/.test(v.style)) cur.style = v.style; if (/^[A-F]$/.test(v.image)) cur.image = v.image; } } catch(e){}

  function imageView(L){
    if (built[L]) return built[L];
    var m = META.images[L], box = document.createElement('div'); box.className = 'set';
    box.innerHTML = '<div class="sethead"><h3><span class="no">' + L + '</span> ' + m.en + ' <span lang="hi">' + m.hi + '</span></h3><div class="pair"><p class="hi" lang="hi">' + m.nhi + '</p><p class="en">' + m.nen + '</p></div></div>';
    var groups = [['काले पोस्टर और दीवार का पोस्टर · The system, upright', ['1','2','5','6'], 'g-four'], ['होर्डिंग और बैनर · The system, wide', ['3','4'], 'g-pair'], ['विकल्प · Alternates', ['7','8','9'], 'g-four']];
    var wrap = document.createElement('div'); wrap.className = 'groups';
    groups.forEach(function(g){
      var grp = document.createElement('div'); grp.className = 'group';
      var gl = document.createElement('div'); gl.className = 'gl'; gl.textContent = g[0]; grp.appendChild(gl);
      var grid = document.createElement('div'); grid.className = 'grid ' + g[2];
      g[1].forEach(function(d){ var src = stage.querySelector('.set[data-style="' + d + '"] .piece[data-code="' + L + d + '"]'); if (src) grid.appendChild(src.cloneNode(true)); });
      grp.appendChild(grid); wrap.appendChild(grp);
    });
    box.appendChild(wrap); built[L] = box; return box;
  }
  function render(){
    document.getElementById('m-style').setAttribute('aria-pressed', String(mode === 'style'));
    document.getElementById('m-image').setAttribute('aria-pressed', String(mode === 'image'));
    tabs.innerHTML = mode === 'style' ? styleTabs : imageTabs;
    Array.prototype.forEach.call(tabs.querySelectorAll('.tab'), function(t){ var on = t.getAttribute('data-id') === cur[mode]; t.setAttribute('aria-pressed', String(on)); if (on && t.scrollIntoView) try { t.scrollIntoView({block: 'nearest', inline: 'nearest'}); } catch(e){} });
    stage.className = mode === 'style' ? 'by-style' : 'by-image';
    Object.keys(built).forEach(function(k){ if (built[k].parentNode) built[k].parentNode.removeChild(built[k]); });
    sets.forEach(function(s){ s.hidden = !(mode === 'style' && s.getAttribute('data-style') === cur.style); });
    if (mode === 'image') stage.appendChild(imageView(cur.image));
    paint();
  }
  function remember(){ store('rtam-posters-view', JSON.stringify({mode: mode, style: cur.style, image: cur.image})); }
  document.getElementById('m-style').addEventListener('click', function(){ mode = 'style'; render(); remember(); });
  document.getElementById('m-image').addEventListener('click', function(){ mode = 'image'; render(); remember(); });
  tabs.addEventListener('click', function(e){ var t = e.target.closest('.tab'); if (!t) return; cur[mode] = t.getAttribute('data-id'); render(); remember(); });

  /* ---- the selection: lives in this browser and in the link (#p=A1.F3); nothing is uploaded ---- */
  var picks = {}, fromLink = false;
  function valid(c){ return /^[A-F][1-9]$/.test(c); }
  function codes(){ return Object.keys(picks).filter(function(c){ return picks[c]; }).sort(); }
  function label(c){ return META.images[c[0]].en + ' · ' + META.styles[c[1]].en; }
  (function init(){
    var m = /[#&]p=([A-F1-9.]*)/.exec(location.hash || '');
    if (m) { m[1].split('.').forEach(function(c){ if (valid(c)) picks[c] = true; }); fromLink = codes().length > 0; }
    if (!fromLink) { try { (JSON.parse(read('rtam-posters-picks') || '[]') || []).forEach(function(c){ if (valid(c)) picks[c] = true; }); } catch(e){} }
    var n = document.getElementById('who'), t = document.getElementById('remark');
    n.value = read('rtam-posters-name') || ''; t.value = read('rtam-posters-remark') || '';
    n.addEventListener('input', function(){ store('rtam-posters-name', n.value); paintMessage(); });
    t.addEventListener('input', function(){ store('rtam-posters-remark', t.value); paintMessage(); });
  })();
  function link(){ var c = codes(); return location.href.split('#')[0] + (c.length ? '#p=' + c.join('.') : ''); }
  function save(){
    store('rtam-posters-picks', JSON.stringify(codes()));
    try { history.replaceState(null, '', codes().length ? '#p=' + codes().join('.') : location.pathname + location.search); } catch(e){}
  }
  function message(){
    var c = codes(); if (!c.length) return '';
    var who = document.getElementById('who').value.trim(), note = document.getElementById('remark').value.trim();
    var lines = ['*ऋतम्भरेश्वर मंदिर · पोस्टर चयन*'];
    if (who) lines.push('नाम / Name: ' + who);
    lines.push('चयन / Selection (' + c.length + '):');
    c.forEach(function(k){ lines.push('• ' + k + ' – ' + label(k)); });
    if (note) lines.push('टिप्पणी / Note: ' + note);
    lines.push(link());
    return lines.join('\n');
  }
  function paintMessage(){
    var msg = message(), has = !!msg, wa = document.getElementById('wa');
    document.getElementById('msg').value = msg;
    if (has) { wa.setAttribute('href', 'https://wa.me/?text=' + encodeURIComponent(msg)); wa.removeAttribute('aria-disabled'); } else { wa.removeAttribute('href'); wa.setAttribute('aria-disabled', 'true'); }
    document.getElementById('copy').disabled = !has; document.getElementById('share').disabled = !has; document.getElementById('clear').disabled = !has;
  }
  function paint(){
    Array.prototype.forEach.call(document.querySelectorAll('.piece'), function(f){
      var on = !!picks[f.getAttribute('data-code')]; f.classList.toggle('picked', on);
      var b = f.querySelector('.pick'); if (b) { b.setAttribute('aria-pressed', String(on)); b.innerHTML = on ? '✓ <span lang="hi">चुना</span> · Selected' : '<span lang="hi">चुनें</span> · Select'; }
    });
    var c = codes(), ul = document.getElementById('picklist'); ul.textContent = '';
    c.forEach(function(k){
      var li = document.createElement('li'), chip = document.createElement('span'); chip.className = 'code'; chip.textContent = k; li.appendChild(chip);
      li.appendChild(document.createTextNode(label(k)));
      var x = document.createElement('button'); x.type = 'button'; x.setAttribute('aria-label', 'Remove ' + k); x.setAttribute('data-code', k); x.textContent = '×'; li.appendChild(x); ul.appendChild(li);
    });
    document.getElementById('pickempty').hidden = c.length > 0;
    document.getElementById('pickcount').textContent = c.length ? '(' + c.length + ')' : '';
    document.getElementById('fromlink').hidden = !fromLink;
    paintMessage(); if (lbCode) paintLb();
  }
  function toggle(c){ if (!valid(c)) return; picks[c] = !picks[c]; fromLink = false; save(); paint(); }
  document.addEventListener('click', function(e){
    var p = e.target.closest('.pick'); if (p) { toggle(p.closest('.piece').getAttribute('data-code')); return; }
    var x = e.target.closest('#picklist button'); if (x) { toggle(x.getAttribute('data-code')); return; }
    var s = e.target.closest('.shot'); if (s) openLb(s.closest('.piece'));
  });
  document.getElementById('clear').addEventListener('click', function(){ picks = {}; fromLink = false; save(); paint(); });
  var said = document.getElementById('said');
  document.getElementById('copy').addEventListener('click', function(){
    var ta = document.getElementById('msg');
    function manual(){ ta.focus(); ta.select(); said.textContent = 'संदेश चुन लिया गया है, अब कॉपी कीजिए · The message is selected, now copy it.'; }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(ta.value).then(function(){ said.textContent = 'कॉपी हो गया · Copied.'; }, manual); else manual();
  });
  var shareBtn = document.getElementById('share');
  if (navigator.share) { shareBtn.hidden = false; shareBtn.addEventListener('click', function(){ navigator.share({text: message()}).catch(function(){}); }); }

  /* ---- enlarged view ---- */
  var lb = document.getElementById('lb'), lbImg = lb.querySelector('img'), lbCap = document.getElementById('lbcap'), lbPick = document.getElementById('lbpick'), lbOpen = document.getElementById('lbopen'), lbCode = null, lbFrom = null;
  function visible(){ return Array.prototype.filter.call(stage.querySelectorAll('.piece'), function(f){ return f.offsetParent !== null; }); }
  function show(f){
    var c = f.getAttribute('data-code'), all = visible(); lbCode = c; lbFrom = f;
    lbImg.src = f.querySelector('img').src; lbImg.alt = f.querySelector('img').alt;
    var full = new Image(); full.onload = function(){ if (lbCode === c) lbImg.src = full.src; }; full.src = 'img/full/' + c + '.webp';
    lbOpen.setAttribute('href', 'img/full/' + c + '.webp');
    lbCap.innerHTML = '<b>' + c + '</b>' + label(c) + ' &nbsp; ' + (all.indexOf(f) + 1) + ' / ' + all.length; paintLb();
  }
  function paintLb(){ var on = !!picks[lbCode]; lbPick.setAttribute('aria-pressed', String(on)); lbPick.innerHTML = on ? '✓ <span lang="hi">चुना</span> · Selected' : '<span lang="hi">चुनें</span> · Select'; }
  function openLb(f){ show(f); lb.hidden = false; document.body.style.overflow = 'hidden'; document.getElementById('lbx').focus(); }
  function closeLb(){ lb.hidden = true; document.body.style.overflow = ''; lbImg.removeAttribute('src'); var b = lbFrom && lbFrom.querySelector('.shot'); lbCode = null; if (b) b.focus(); }
  function step(d){ var all = visible(), i = all.indexOf(lbFrom); if (i < 0) return; show(all[(i + d + all.length) % all.length]); }
  document.getElementById('lbx').addEventListener('click', closeLb);
  lb.querySelector('.lbimg').addEventListener('click', closeLb);
  document.getElementById('lbprev').addEventListener('click', function(){ step(-1); });
  document.getElementById('lbnext').addEventListener('click', function(){ step(1); });
  lbPick.addEventListener('click', function(){ if (lbCode) toggle(lbCode); });
  document.addEventListener('keydown', function(e){ if (lb.hidden) return; if (e.key === 'Escape') closeLb(); else if (e.key === 'ArrowLeft') step(-1); else if (e.key === 'ArrowRight') step(1); });
  var sx = null; lb.addEventListener('touchstart', function(e){ sx = e.touches.length === 1 ? e.touches[0].clientX : null; }, {passive: true});
  lb.addEventListener('touchend', function(e){ if (sx === null) return; var dx = e.changedTouches[0].clientX - sx; sx = null; if (Math.abs(dx) > 60) step(dx < 0 ? 1 : -1); }, {passive: true});

  render();
})();
'''

def page(sizes):
    e = H.escape
    def fig(sub, sty):
        code = sub[1] + sty[1]; w, h = sizes[code]
        return (f'<figure class="piece" data-code="{code}" data-style="{sty[1]}" data-image="{sub[1]}">'
                f'<button class="shot" type="button" aria-label="{code}: {e(sty[2])}, {e(sub[2])}. Enlarge"><img src="img/thumb/{code}.webp" width="{w}" height="{h}" alt="Poster {code}: {e(sub[2])} in the {e(sty[2])} style" loading="lazy" decoding="async"></button>'
                f'<figcaption><span class="code">{code}</span><span class="cap cap-image">{e(sub[2])}</span><span class="cap cap-style">{e(sty[2])}</span>'
                f'<button class="pick" type="button" aria-pressed="false"><span lang="hi">चुनें</span> · Select</button></figcaption></figure>')
    sets = ''.join(
        f'<div class="set" data-style="{sty[1]}"><div class="sethead"><h3><span class="no">{sty[1]}</span> {e(sty[2])} <span lang="hi">{sty[3]}</span></h3>'
        f'<div class="pair"><p class="hi" lang="hi">{sty[5]}</p><p class="en">{e(sty[6])} <span class="note">{sty[4]}</span></p></div></div>'
        f'<div class="grid g-{sty[7]}">{"".join(fig(sub, sty) for sub in SUBJECTS)}</div></div>' for sty in STYLES)
    style_tabs = ''.join(f'<button type="button" class="tab" data-id="{s[1]}"><b>{s[1]}</b> {e(s[2])}</button>' for s in STYLES)
    image_tabs = ''.join(f'<button type="button" class="tab" data-id="{s[1]}"><b>{s[1]}</b> {e(s[2])}</button>' for s in SUBJECTS)
    import json
    meta = json.dumps({'images': {s[1]: {'en': s[2], 'hi': s[3], 'nhi': s[4], 'nen': s[5]} for s in SUBJECTS}, 'styles': {s[1]: {'en': s[2], 'hi': s[3]} for s in STYLES}}, ensure_ascii=False)
    sheet_links = '<a class="btn" href="sheets/all-54.jpg" target="_blank" rel="noopener"><span lang="hi">सभी 54 एक शीट में</span> · All 54 on one sheet</a>' + ''.join(
        f'<a class="btn" href="sheets/style-{s[1]}.jpg" target="_blank" rel="noopener"><b>{s[1]}</b> {e(s[2])}</a>' for s in STYLES)
    return f'''<!doctype html>
<html lang="hi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>ऋतम्भरेश्वर मंदिर · पोस्टर समीक्षा · Poster review</title>
<meta name="description" content="Rtambhareshvara Mandir: nine poster styles on six images. Select the ones you like and send your selection.">
<meta name="robots" content="noindex,nofollow">
<meta name="theme-color" content="#141414">
<meta property="og:type" content="website">
<meta property="og:title" content="ऋतम्भरेश्वर मंदिर · पोस्टर समीक्षा">
<meta property="og:description" content="Nine poster styles on six images. Select the ones you like and reply.">
<meta property="og:url" content="{BASE_URL}">
<meta property="og:image" content="{BASE_URL}sheets/preview.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<link rel="preload" href="fonts/tiro-400.woff2" as="font" type="font/woff2" crossorigin>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header class="top">
  <div class="eyebrow"><span class="bindu" aria-hidden="true"></span><span lang="hi">ऋतम्भरेश्वर मंदिर</span><span>Poster review</span></div>
  <h1><span lang="hi">पोस्टर चुनिए</span><span class="en">Choose the posters</span></h1>
  <div class="pair">
    <p class="hi" lang="hi">मंदिर के पोस्टर और बैनर के लिए नौ शैलियाँ बनाई गई हैं। हर शैली छह चित्रों पर दिखाई गई है। जो पसंद आएँ उन्हें चुनिए और अपना चयन भेज दीजिए।</p>
    <p class="en">There are nine poster styles, each shown on six images. Select the ones you like and send your selection.</p>
  </div>
  <ol class="steps">
    <li><div class="pair"><span class="hi" lang="hi">किसी भी पोस्टर को दबाकर बड़ा देखिए।</span><span class="en">Tap any poster to see it large.</span></div></li>
    <li><div class="pair"><span class="hi" lang="hi">जो पसंद आए, उसके नीचे “चुनें” दबाइए।</span><span class="en">Press Select under the ones you like.</span></div></li>
    <li><div class="pair"><span class="hi" lang="hi">नीचे अपना नाम लिखिए और WhatsApp पर भेज दीजिए।</span><span class="en">Write your name below and send it on WhatsApp.</span></div></li>
  </ol>
  <div class="pair">
    <p class="hi" lang="hi">हर पोस्टर का एक कोड है, जैसे A1 या F3। बात करते समय यही कोड बताइए।</p>
    <p class="en">Every poster has a code such as A1 or F3. Use the code when you talk about a poster.</p>
  </div>
</header>

<section id="viewer" aria-label="Posters">
  <div class="bar">
    <div class="seg"><span><span lang="hi">देखिए</span> · Compare by</span>
      <button type="button" id="m-style" aria-pressed="true"><span lang="hi">शैली</span> · Style</button>
      <button type="button" id="m-image" aria-pressed="false"><span lang="hi">चित्र</span> · Image</button></div>
    <div class="tabs" id="tabs">{style_tabs}</div>
    <template id="imagetabs">{image_tabs}</template>
  </div>
  <div id="stage" class="by-style">{sets}</div>
</section>

<section aria-labelledby="h-picks">
  <h2 id="h-picks"><span lang="hi">आपका चयन</span><span>Your selection</span><span id="pickcount" class="note"></span></h2>
  <p class="notice" id="fromlink" hidden><span lang="hi">यह चयन एक लिंक से खुला है।</span> This selection was opened from a link.</p>
  <div class="pair" id="pickempty"><p class="hi" lang="hi">अभी कुछ नहीं चुना गया। किसी भी पोस्टर के नीचे “चुनें” दबाइए।</p><p class="en">Nothing selected yet. Press Select under any poster.</p></div>
  <ul id="picklist"></ul>
  <div class="form">
    <label><span><span lang="hi">आपका नाम</span> · Your name</span><input type="text" id="who" autocomplete="name" maxlength="80"></label>
    <label><span><span lang="hi">सुझाव या टिप्पणी</span> · Comment, if any</span><textarea id="remark" maxlength="1500"></textarea></label>
  </div>
  <label><span><span lang="hi">यह संदेश भेजा जाएगा</span> · This message will be sent</span><textarea id="msg" readonly></textarea></label>
  <div class="row">
    <a class="btn primary" id="wa" target="_blank" rel="noopener" aria-disabled="true"><span lang="hi">WhatsApp पर भेजें</span> · Send on WhatsApp</a>
    <button type="button" class="btn" id="share" hidden disabled><span lang="hi">साझा करें</span> · Share</button>
    <button type="button" class="btn" id="copy" disabled><span lang="hi">कॉपी करें</span> · Copy</button>
    <button type="button" class="btn" id="clear" disabled><span lang="hi">सब हटाएँ</span> · Clear all</button>
  </div>
  <div class="pair"><p class="hi" lang="hi">जिसने आपको यह लिंक भेजा है, उसी को अपना चयन भेजिए।</p><p class="en">Send your selection to the person who sent you this link.</p></div>
  <p class="note" id="said" role="status"></p>
  <div class="pair note"><p class="hi" lang="hi">यह पेज कुछ भी कहीं जमा नहीं करता। आपका चयन आपके ही फ़ोन या कंप्यूटर में रहता है, और तभी जाता है जब आप उसे भेजते हैं।</p>
  <p>This page uploads nothing. Your selection stays on your own device and goes out only when you send it.</p></div>
</section>

<section aria-labelledby="h-note">
  <h2 id="h-note"><span lang="hi">ध्यान दें</span><span>Please note</span></h2>
  <ul class="plain">
    <li><div class="pair"><span class="hi" lang="hi">ये अभी प्रूफ़ हैं। पता, फ़ोन नंबर और शब्द छपाई से पहले तय किए जाएँगे।</span><span class="en">These are proofs. The address, phone numbers and wording will be confirmed before printing.</span></div></li>
    <li><div class="pair"><span class="hi" lang="hi">“मंदिर और नंदी” वाला चित्र (F) दो अलग चित्रों को जोड़कर बनाया गया है। नंदी का आकार और दूरी अनुमान से रखी गई है।</span><span class="en">Image F, the temple with Nandi, is composed from two separate pictures. Nandi's size and distance are set by eye.</span></div></li>
    <li><div class="pair"><span class="hi" lang="hi">काले पोस्टरों में नंदी की मूर्ति थोड़ी उजली की गई है, ताकि वह काले रंग पर दिखे।</span><span class="en">On the black posters the Nandi statue has been brightened so that it shows against the black.</span></div></li>
    <li><div class="pair"><span class="hi" lang="hi">शिवलिंग की जलाधारी अभी हल्के रंग की है। उसे गहरे स्लेटी-काले रंग का किया जाना है।</span><span class="en">The jaladhari is still light stone. It is to be made dark grey-black.</span></div></li>
    <li><div class="pair"><span class="hi" lang="hi">शैली 7, 8 और 9 विकल्प हैं। इनमें चित्र अपने आकाश के साथ पूरा रखा गया है।</span><span class="en">Styles 7, 8 and 9 are alternates that keep the picture whole, with its sky.</span></div></li>
  </ul>
</section>

<section aria-labelledby="h-sheets">
  <h2 id="h-sheets"><span lang="hi">एक नज़र में</span><span>At a glance</span></h2>
  <div class="pair"><p class="hi" lang="hi">ये शीटें चित्र के रूप में खुलती हैं। इन्हें सहेजकर आगे भेजा जा सकता है।</p><p class="en">These sheets open as pictures. You can save and forward them.</p></div>
  <div class="links">{sheet_links}</div>
</section>

<footer><span lang="hi">ऋतम् प्रतिष्ठान</span><span>ṚTAM Foundation</span><span lang="hi">ऋतस्य पन्थाम्</span></footer>
</div>

<div id="lb" hidden role="dialog" aria-modal="true" aria-label="Enlarged poster">
  <div class="lbtop"><span id="lbcap"></span><button type="button" id="lbx"><span lang="hi">बंद करें</span> · Close</button></div>
  <div class="lbimg"><img alt=""></div>
  <div class="lbfoot"><button type="button" id="lbprev" aria-label="Previous poster">‹<span class="w"> Prev</span></button><button type="button" id="lbpick" aria-pressed="false"><span lang="hi">चुनें</span> · Select</button><a id="lbopen" target="_blank" rel="noopener">Full size</a><button type="button" id="lbnext" aria-label="Next poster"><span class="w">Next </span>›</button></div>
</div>
<script>{JS.replace('__META__', meta)}</script>
</body>
</html>
'''

if __name__ == '__main__':
    sizes, n = images(); print(f'images: {len(sizes)} posters, thumbs + full = {n / 1e6:.1f} MB')
    s = sum(strip(sty[0], sty[1], sty[2], sty[4], 1040 if sty[7] == 'w3' else (900 if sty[7] == 'w2' else 560), 2 if sty[7] == 'w3' else (3 if sty[7] == 'w2' else 6)) for sty in STYLES)
    print(f'sheets: 9 strips {s / 1e6:.1f} MB, matrix {matrix() / 1e6:.1f} MB, preview {preview() / 1e3:.0f} KB')
    print('fonts:', fonts())
    (ROOT / 'index.html').write_text(page(sizes), encoding='utf-8'); print(f'index.html {(ROOT / "index.html").stat().st_size / 1e3:.0f} KB')
