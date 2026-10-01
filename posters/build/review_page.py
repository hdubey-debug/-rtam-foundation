#!/usr/bin/env python3
"""Build the review page (one self-contained HTML file) from the rendered previews: six images x nine styles,
compared by style or by image, with a shortlist. usage: review_page.py OUT.html"""
import base64, io, sys, html as H
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parent.parent; OUT = ROOT / 'out'

SUBJECTS = [('01-front', 'Front', 'The approved pilot image. It is symmetrical, so everything shares its axis.'),
            ('02-side-tower-right', 'Side, tower right', 'Steps on the left, tower on the right.'),
            ('03-side-tower-left', 'Side, tower left', 'Steps on the right, tower on the left. The wide boards mirror for this view.'),
            ('04-shivalinga', 'Shivalinga', 'Cut from the interior picture. The photo styles show the whole hall.'),
            ('05-nandi', 'Nandi pavilion', 'The statue is brightened in the cut-out styles so that it reads on black.'),
            ('06-temple-and-nandi', 'Temple and Nandi', 'Composed from two pictures. The note further down explains how.')]
STYLES = [('01-adhishthana', 'Adhishthana', 'अधिष्ठान', '24 × 36 in', 'The name bears the picture. The lockup is as wide as the base of whatever stands on it.', 'up'),
          ('02-shirshak', 'Shirshak', 'शीर्षक', '24 × 36 in', 'The name on top, for flex hung at ground level. The foot carries the address and the QR.', 'up'),
          ('03-ek-rekha', 'Ek Rekha', 'एक रेखा', '2:1 hoarding', 'One ground line across the board. Where the steps are on the right of the picture, the board is mirrored so the line arrives at the steps.', 'w2'),
          ('04-torana', 'Torana', 'तोरण', '3:1 gate or street banner', 'Name, picture and status read along one line.', 'w3'),
          ('05-stambha', 'Stambha', 'स्तम्भ', '85 × 200 cm standee', 'The name sits at eye level. The lowest third stays dark because chairs and people hide it.', 'up'),
          ('06-chandra', 'Chandra', 'चन्द्र', '24 × 36 in, indoor walls', 'The day register. The picture is a plate on moon-paper.', 'up'),
          ('07-akasha', 'Akasha', 'आकाश', '24 × 36 in, alternate', 'The sky deepens into the black where the name sits.', 'up'),
          ('08-dhvaja', 'Dhvaja', 'ध्वज', '24 × 36 in, alternate', 'The name is set inside the picture.', 'up'),
          ('09-patta', 'Patta', 'पट्ट', '24 × 36 in, alternate', 'Your letterhead enlarged, with the founders line.', 'up')]
LONG = {'up': 1350, 'w2': 1800, 'w3': 2000}

def data(sub, sty, long_side, q=80):
    im = Image.open(OUT / sub / f'{sty}.png').convert('RGB'); r = long_side / max(im.size)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS); b = io.BytesIO(); im.save(b, 'WEBP', quality=q, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode(), im.size, len(b.getvalue())

total = 0
def fig(sub, slabel, sty, sname, shape):
    global total
    src, (w, h), n = data(sub, sty, 1600 if sty.startswith('05') else LONG[shape]); total += n
    key = f'{sub}/{sty}'; num = sty[:2]
    return (f'<figure class="piece" data-key="{key}" data-style="{num}" data-subject="{sub[:2]}" data-shape="{shape}" data-label="{num} {H.escape(sname)} · {H.escape(slabel)}">'
            f'<button class="shot" type="button" aria-label="Enlarge {H.escape(sname)}, {H.escape(slabel)}"><img src="{src}" width="{w}" height="{h}" alt="{H.escape(sname)} style, {H.escape(slabel)}" loading="lazy" decoding="async"></button>'
            f'<figcaption><span class="cap cap-subject">{H.escape(slabel)}</span><span class="cap cap-style"><b>{num}</b> {H.escape(sname)}</span>'
            f'<button class="pick" type="button" aria-pressed="false">Shortlist</button></figcaption></figure>')

sets = []
for sty, sname, deva, size, blurb, shape in STYLES:
    figs = ''.join(fig(sub, slabel, sty, sname, shape) for sub, slabel, _ in SUBJECTS)
    sets.append(f'<div class="set" id="set-{sty[:2]}" data-style="{sty[:2]}"><div class="sethead"><h3><span class="no">{sty[:2]}</span> {sname} <span class="dv" lang="hi">{deva}</span></h3>'
                f'<p><span class="sz">{size}.</span> {blurb}</p></div><div class="grid g-{shape}">{figs}</div></div>')
style_tabs = ''.join(f'<button type="button" class="tab" data-mode="style" data-id="{s[0][:2]}"><b>{s[0][:2]}</b> {s[1]}</button>' for s in STYLES)
image_tabs = ''.join(f'<button type="button" class="tab" data-mode="image" data-id="{s[0][:2]}">{s[1]}</button>' for s in SUBJECTS)
image_notes = '{' + ','.join(f'"{s[0][:2]}":{{"name":"{s[1]}","note":"{s[2]}"}}' for s in SUBJECTS) + '}'

CSS = '''
/* Layout: a comparison bench in the brand's day register. A sticky bar chooses what to compare; posters hang on a wall-toned mat. */
:root {
  --ground:#EDEBE6; --ink:#1A1A1A; --quiet:#5C574F; --hair:rgba(26,26,26,.16); --accent:#7A5423; --gold:#C8A15A; --wall:#D8D4CA; --chip:#E2DFD8; --on-accent:#F3F1EC;
  --display:'Cinzel','Trajan Pro',Georgia,serif; --body:'Inter',system-ui,-apple-system,'Segoe UI',sans-serif; --deva:'Tiro Devanagari Sanskrit','Noto Serif Devanagari',serif;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --ground:#141414; --ink:#C9C2B6; --quiet:#8F887C; --hair:rgba(201,194,182,.2); --accent:#C8A15A; --gold:#C8A15A; --wall:#2C2A27; --chip:#232220; --on-accent:#141414; color-scheme:dark } }
:root[data-theme="dark"] { --ground:#141414; --ink:#C9C2B6; --quiet:#8F887C; --hair:rgba(201,194,182,.2); --accent:#C8A15A; --gold:#C8A15A; --wall:#2C2A27; --chip:#232220; --on-accent:#141414; color-scheme:dark }
* { box-sizing:border-box }
body { background:var(--ground); color:var(--ink); font:400 16px/1.6 var(--body); padding-inline:max(16px,3vw); padding-block:0 }
.wrap { max-width:1560px; margin:0 auto; padding-block:44px 80px; display:flex; flex-direction:column; gap:56px }
header.top { display:flex; flex-direction:column; gap:14px; max-width:48rem }
.eyebrow { font:500 .78rem/1.2 var(--body); letter-spacing:.2em; text-transform:uppercase; color:var(--quiet); display:flex; align-items:center; gap:.7em; flex-wrap:wrap }
.eyebrow [lang="hi"] { font:400 1.15rem/1 var(--deva); letter-spacing:0; text-transform:none; color:var(--ink) }
.bindu { width:.5em; height:.5em; border-radius:50%; background:var(--gold); display:inline-block }
h1 { font:500 clamp(1.9rem,4.4vw,2.9rem)/1.12 var(--display); letter-spacing:.04em; margin:0; text-wrap:balance }
h2 { font:500 1.05rem/1.3 var(--display); letter-spacing:.14em; text-transform:uppercase; margin:0; padding-bottom:12px; border-bottom:1px solid var(--hair) }
h3 { font:500 1.15rem/1.3 var(--display); letter-spacing:.1em; text-transform:uppercase; margin:0; display:flex; align-items:baseline; gap:.5em; flex-wrap:wrap }
h3 .no { font:600 .95rem/1 var(--body); color:var(--accent); letter-spacing:0; font-variant-numeric:tabular-nums }
h3 .dv { font:400 1.15rem/1 var(--deva); letter-spacing:0; text-transform:none; color:var(--quiet) }
p { margin:0; max-width:46rem }
.lead { font-size:1.06rem }
section { display:flex; flex-direction:column; gap:22px }
[lang="hi"] { font-family:var(--deva) }
button { font:inherit; color:inherit }
.bar { position:sticky; top:env(safe-area-inset-top,0px); z-index:5; background:var(--ground); padding-block:12px; border-bottom:1px solid var(--hair); display:flex; flex-direction:column; gap:10px }
.seg { display:flex; align-items:center; gap:10px; flex-wrap:wrap; font-size:.85rem; color:var(--quiet) }
.seg button, .tab, .pick, .ghost { all:unset; box-sizing:border-box; cursor:pointer; font:500 .85rem/1 var(--body); padding:9px 12px; border:1px solid var(--hair); border-radius:3px; color:var(--ink); white-space:nowrap }
.seg button[aria-pressed="true"], .tab[aria-pressed="true"] { background:var(--ink); color:var(--ground); border-color:var(--ink) }
.tab b { font-weight:600; font-variant-numeric:tabular-nums; margin-right:.25em }
.tabs { display:flex; gap:6px; overflow-x:auto; padding-bottom:2px; scrollbar-width:thin }
button:focus-visible { outline:2px solid var(--accent); outline-offset:2px }
.sethead { display:flex; flex-direction:column; gap:6px; margin-bottom:18px }
.sethead .sz { color:var(--quiet) }
#stage { display:flex; flex-direction:column; gap:56px }
.grid { display:grid; gap:28px 22px; align-items:start }
.g-up { grid-template-columns:repeat(3,minmax(0,1fr)) }
.g-w2 { grid-template-columns:repeat(2,minmax(0,1fr)) }
.g-w3 { grid-template-columns:repeat(2,minmax(0,1fr)) }
.g-four { grid-template-columns:repeat(4,minmax(0,1fr)) }
.g-pair { grid-template-columns:minmax(0,2fr) minmax(0,3fr) }
.group { display:flex; flex-direction:column; gap:14px }
.group > .gl { font:500 .72rem/1.2 var(--body); letter-spacing:.18em; text-transform:uppercase; color:var(--quiet) }
.piece { margin:0; display:flex; flex-direction:column; gap:8px; min-width:0 }
.shot { all:unset; box-sizing:border-box; display:block; width:100%; cursor:zoom-in; background:var(--wall); padding:clamp(8px,1.2vw,16px); line-height:0 }
.shot img { display:block; width:100%; height:auto }
.piece.picked .shot { box-shadow:0 0 0 2px var(--accent) }
figcaption { display:flex; align-items:center; justify-content:space-between; gap:10px; font-size:.88rem; min-width:0 }
.cap { min-width:0; overflow-wrap:anywhere }
.cap b { color:var(--accent); font-weight:600; font-variant-numeric:tabular-nums }
.by-style .cap-style, .by-image .cap-subject { display:none }
.pick { padding:6px 10px; font-size:.78rem; color:var(--quiet) }
.pick[aria-pressed="true"] { background:var(--accent); border-color:var(--accent); color:var(--on-accent) }
.two { display:grid; grid-template-columns:repeat(auto-fit,minmax(18rem,1fr)); gap:26px 44px }
.two > div { display:flex; flex-direction:column; gap:10px; min-width:0 }
ul.plain, ol.plain { margin:0; padding-left:1.15em; display:flex; flex-direction:column; gap:8px; max-width:46rem }
#picklist { list-style:none; margin:0; padding:0; display:flex; flex-wrap:wrap; gap:8px }
#picklist li { display:flex; align-items:center; gap:8px; background:var(--chip); border-radius:3px; padding:6px 6px 6px 12px; font-size:.88rem }
#picklist button { all:unset; cursor:pointer; padding:2px 8px; color:var(--quiet); border-radius:3px }
.row { display:flex; align-items:center; gap:12px; flex-wrap:wrap }
.ghost[disabled] { opacity:.45; cursor:default }
.note { color:var(--quiet); font-size:.9rem }
textarea#picktext { width:100%; max-width:46rem; min-height:5.5rem; font:400 .85rem/1.5 ui-monospace,SFMono-Regular,Menlo,monospace; color:var(--ink); background:var(--chip); border:1px solid var(--hair); border-radius:3px; padding:10px }
code { font:500 .86em ui-monospace,SFMono-Regular,Menlo,monospace; background:var(--chip); padding:.1em .35em; border-radius:3px; overflow-wrap:anywhere }
#lb { position:fixed; inset:0; background:rgba(12,12,12,.96); display:grid; grid-template-rows:auto minmax(0,1fr) auto; gap:10px; padding:calc(12px + env(safe-area-inset-top,0px)) 14px calc(14px + env(safe-area-inset-bottom,0px)); z-index:10 }
#lb .lbtop, #lb .lbfoot { display:flex; align-items:center; justify-content:space-between; gap:12px; color:#C9C2B6; font-size:.9rem; flex-wrap:wrap }
#lb .lbimg { display:flex; align-items:center; justify-content:center; min-height:0; cursor:zoom-out }
#lb img { max-width:100%; max-height:100%; width:auto; height:auto; object-fit:contain }
#lb button { all:unset; box-sizing:border-box; cursor:pointer; color:#C9C2B6; font:500 .8rem/1 var(--body); letter-spacing:.12em; text-transform:uppercase; padding:10px 12px; border:1px solid rgba(201,194,182,.35); border-radius:3px }
#lb button[aria-pressed="true"] { background:#C8A15A; border-color:#C8A15A; color:#141414 }
#lb button:focus-visible { outline:2px solid #C8A15A; outline-offset:2px }
@media (min-width:1500px) { .g-up { grid-template-columns:repeat(6,minmax(0,1fr)) } .g-w2 { grid-template-columns:repeat(3,minmax(0,1fr)) } }
@media (max-width:1000px) { .g-four { grid-template-columns:repeat(2,minmax(0,1fr)) } .g-w3, .g-pair { grid-template-columns:minmax(0,1fr) } }
@media (max-width:640px) { .g-up { grid-template-columns:repeat(2,minmax(0,1fr)) } .g-w2 { grid-template-columns:minmax(0,1fr) } .wrap { gap:44px; padding-block:28px 64px } figcaption { flex-direction:column; align-items:flex-start } }
'''

JS = r'''
(function(){
  var NOTES = __IMAGE_NOTES__;
  var stage = document.getElementById('stage'), tabs = document.getElementById('tabs');
  var sets = Array.prototype.slice.call(stage.querySelectorAll('.set'));
  var mode = 'style', current = {style:'01', image:'01'}, built = {};
  var styleTabs = tabs.innerHTML, imageTabs = document.getElementById('imagetabs').innerHTML;
  function remember(){ try { localStorage.setItem('rtam-view', JSON.stringify({mode:mode, current:current})); } catch(e){} }
  try { var v = JSON.parse(localStorage.getItem('rtam-view') || 'null'); if (v && v.current && (v.mode === 'style' || v.mode === 'image')) { mode = v.mode; current.style = v.current.style || '01'; current.image = v.current.image || '01'; } } catch(e){}

  function imageView(id){
    if (built[id]) return built[id];
    var box = document.createElement('div'); box.className = 'set'; box.setAttribute('data-image', id);
    var head = document.createElement('div'); head.className = 'sethead';
    var h = document.createElement('h3'); h.textContent = NOTES[id].name; var p = document.createElement('p'); p.textContent = NOTES[id].note;
    head.appendChild(h); head.appendChild(p); box.appendChild(head);
    var groups = [['The system, upright', ['01','02','05','06'], 'g-four'], ['The system, wide', ['03','04'], 'g-pair'], ['Alternates that keep the picture whole', ['07','08','09'], 'g-four']];
    var wrap = document.createElement('div'); wrap.style.display = 'flex'; wrap.style.flexDirection = 'column'; wrap.style.gap = '36px';
    groups.forEach(function(g){
      var grp = document.createElement('div'); grp.className = 'group';
      var gl = document.createElement('div'); gl.className = 'gl'; gl.textContent = g[0]; grp.appendChild(gl);
      var grid = document.createElement('div'); grid.className = 'grid ' + g[2];
      g[1].forEach(function(st){
        var src = stage.querySelector('#set-' + st + ' .piece[data-subject="' + id + '"]'); if (!src) return;
        grid.appendChild(src.cloneNode(true));
      });
      grp.appendChild(grid); wrap.appendChild(grp);
    });
    box.appendChild(wrap); built[id] = box; return box;
  }
  function render(){
    document.getElementById('m-style').setAttribute('aria-pressed', String(mode === 'style'));
    document.getElementById('m-image').setAttribute('aria-pressed', String(mode === 'image'));
    tabs.innerHTML = mode === 'style' ? styleTabs : imageTabs;
    Array.prototype.forEach.call(tabs.querySelectorAll('.tab'), function(t){ t.setAttribute('aria-pressed', String(t.getAttribute('data-id') === current[mode])); });
    stage.className = mode === 'style' ? 'by-style' : 'by-image';
    Object.keys(built).forEach(function(k){ if (built[k].parentNode) built[k].parentNode.removeChild(built[k]); });
    sets.forEach(function(s){ s.hidden = !(mode === 'style' && s.getAttribute('data-style') === current.style); });
    if (mode === 'image') stage.appendChild(imageView(current.image));
    paintPicks();
  }
  document.getElementById('m-style').addEventListener('click', function(){ mode = 'style'; render(); remember(); });
  document.getElementById('m-image').addEventListener('click', function(){ mode = 'image'; render(); remember(); });
  tabs.addEventListener('click', function(e){ var t = e.target.closest('.tab'); if (!t) return; current[mode] = t.getAttribute('data-id'); render(); remember(); });

  /* ---- shortlist: kept in this browser, and with the page itself when the viewer allows it ---- */
  var picks = {}, touched = {}, doc = null, dbState = 'off', writing = false, dirty = false;
  var labels = {}; Array.prototype.forEach.call(stage.querySelectorAll('.piece'), function(f){ labels[f.getAttribute('data-key')] = f.getAttribute('data-label'); });
  try { (JSON.parse(localStorage.getItem('rtam-picks') || '[]') || []).forEach(function(k){ if (labels[k]) picks[k] = true; }); } catch(e){}
  function keys(){ return Object.keys(picks).filter(function(k){ return picks[k]; }).sort(function(a, b){ return labels[a] < labels[b] ? -1 : 1; }); }
  function saveLocal(){ try { localStorage.setItem('rtam-picks', JSON.stringify(keys())); } catch(e){} }
  function pushDb(){
    if (!doc) return; if (writing) { dirty = true; return; }
    writing = true; dirty = false; var ks = keys();
    doc.set({keys: ks, labels: ks.map(function(k){ return labels[k]; }), updated: new Date().toISOString()})
      .then(function(){ dbState = 'on'; }, function(){ dbState = 'failed'; })
      .then(function(){ writing = false; paintStatus(); if (dirty) pushDb(); });
  }
  function adopt(snap){
    if (snap && snap.exists) { var d = snap.data() || {}, remote = {};
      (Array.isArray(d.keys) ? d.keys : []).forEach(function(k){ if (labels[k]) remote[k] = true; });
      Object.keys(touched).forEach(function(k){ if (picks[k]) remote[k] = true; else delete remote[k]; });
      picks = remote; saveLocal(); }
    dbState = 'on'; paintPicks(); if (Object.keys(touched).length || !(snap && snap.exists) && keys().length) pushDb();
  }
  function connect(prompted){
    if (doc || dbState === 'failed') return;
    if (!(window.claude && typeof window.claude.use === 'function')) return;
    Promise.all([window.claude.use('db'), window.claude.use('permissions')]).then(function(r){
      var db = r[0], perms = r[1]; if (!db) return;
      var ready = perms && perms.state ? perms.state('db') : Promise.resolve('granted');
      return ready.then(function(st){
        if (st === 'denied' || st === 'unavailable') return;
        if (st === 'prompt' && !prompted) { dbState = 'ask'; paintStatus(); return; }
        try { doc = db.doc('picks/shortlist'); } catch(e){ return; }
        return doc.get().then(adopt, function(){ doc = null; dbState = 'failed'; paintStatus(); });
      });
    }).catch(function(){});
  }
  function toggle(key){ if (!labels[key]) return; picks[key] = !picks[key]; touched[key] = true; saveLocal(); paintPicks(); if (doc) pushDb(); else connect(true); }
  function paintStatus(){
    var el = document.getElementById('pickstatus'); if (!el) return;
    el.textContent = dbState === 'on' ? 'Saved with this page. Claude can read your shortlist from here.' : 'Saved in this browser. Copy the list and paste it into the chat.';
  }
  function paintPicks(){
    Array.prototype.forEach.call(document.querySelectorAll('.piece'), function(f){
      var on = !!picks[f.getAttribute('data-key')]; f.classList.toggle('picked', on);
      var b = f.querySelector('.pick'); if (b) { b.setAttribute('aria-pressed', String(on)); b.textContent = on ? 'Shortlisted' : 'Shortlist'; }
    });
    var ks = keys(), ul = document.getElementById('picklist'); ul.textContent = '';
    ks.forEach(function(k){ var li = document.createElement('li'); li.appendChild(document.createTextNode(labels[k]));
      var x = document.createElement('button'); x.type = 'button'; x.setAttribute('aria-label', 'Remove ' + labels[k]); x.textContent = '×'; x.setAttribute('data-key', k); li.appendChild(x); ul.appendChild(li); });
    document.getElementById('pickempty').hidden = ks.length > 0;
    document.getElementById('pickcount').textContent = ks.length ? String(ks.length) : '';
    var txt = ks.length ? 'My poster shortlist:\n' + ks.map(function(k){ return '- ' + labels[k]; }).join('\n') : '';
    document.getElementById('picktext').value = txt; document.getElementById('copy').disabled = !ks.length;
    paintStatus(); if (lbKey) paintLb();
  }
  document.addEventListener('click', function(e){
    var p = e.target.closest('.pick'); if (p) { toggle(p.closest('.piece').getAttribute('data-key')); return; }
    var x = e.target.closest('#picklist button'); if (x) { toggle(x.getAttribute('data-key')); return; }
    var s = e.target.closest('.shot'); if (s) { openLb(s.closest('.piece')); }
  });
  document.getElementById('copy').addEventListener('click', function(){
    var ta = document.getElementById('picktext'), msg = document.getElementById('copied');
    function fallback(){ ta.hidden = false; ta.focus(); ta.select(); msg.textContent = 'Select the text and copy it.'; }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(ta.value).then(function(){ msg.textContent = 'Copied.'; }, fallback); else fallback();
  });

  /* ---- enlarged view: steps through whatever is on the bench ---- */
  var lb = document.getElementById('lb'), lbImg = lb.querySelector('img'), lbCap = document.getElementById('lbcap'), lbPick = document.getElementById('lbpick'), lbKey = null, lbFrom = null;
  function visible(){ return Array.prototype.filter.call(stage.querySelectorAll('.piece'), function(f){ return f.offsetParent !== null; }); }
  function show(f){ var i = f.querySelector('img'); lbImg.src = i.src; lbImg.alt = i.alt; lbKey = f.getAttribute('data-key'); lbFrom = f; var all = visible();
    lbCap.textContent = f.getAttribute('data-label') + '   ' + (all.indexOf(f) + 1) + ' of ' + all.length; paintLb(); }
  function paintLb(){ var on = !!picks[lbKey]; lbPick.setAttribute('aria-pressed', String(on)); lbPick.textContent = on ? 'Shortlisted' : 'Shortlist'; }
  function openLb(f){ show(f); lb.hidden = false; document.getElementById('lbx').focus(); }
  function closeLb(){ lb.hidden = true; lbImg.removeAttribute('src'); var b = lbFrom && lbFrom.querySelector('.shot'); lbKey = null; if (b) b.focus(); }
  function step(d){ var all = visible(), i = all.indexOf(lbFrom); if (i < 0) return; show(all[(i + d + all.length) % all.length]); }
  document.getElementById('lbx').addEventListener('click', closeLb);
  lb.querySelector('.lbimg').addEventListener('click', closeLb);
  document.getElementById('lbprev').addEventListener('click', function(){ step(-1); });
  document.getElementById('lbnext').addEventListener('click', function(){ step(1); });
  lbPick.addEventListener('click', function(){ if (lbKey) toggle(lbKey); });
  document.addEventListener('keydown', function(e){ if (lb.hidden) return; if (e.key === 'Escape') closeLb(); else if (e.key === 'ArrowLeft') step(-1); else if (e.key === 'ArrowRight') step(1); });

  render(); connect(false);
})();
'''.replace('__IMAGE_NOTES__', image_notes)

page = f'''<title>Rtambhareshvara Poster Pilot</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600&family=Inter:wght@400;500;600&family=Tiro+Devanagari+Sanskrit&display=swap">
<style>{CSS}</style>

<div class="wrap">
<header class="top">
  <div class="eyebrow"><span class="bindu" aria-hidden="true"></span><span lang="hi">ऋतम्भरेश्वर मंदिर</span><span>Poster pilot · round two</span></div>
  <h1>Six images, nine styles</h1>
  <p class="lead">The nine styles from the first round are now applied to every picture: the three exteriors, the Shivalinga, the Nandi pavilion, and a sixth image that brings the temple and Nandi together. Compare one style across the images, or one image across the styles. Shortlist what you like and I will take those forward.</p>
</header>

<section id="viewer" aria-label="Compare the posters">
  <div class="bar">
    <div class="seg"><span>Compare by</span><button type="button" id="m-style" aria-pressed="true">Style</button><button type="button" id="m-image" aria-pressed="false">Image</button><span class="note">Tap a poster to enlarge it. Use the arrow keys to step through.</span></div>
    <div class="tabs" id="tabs">{style_tabs}</div>
    <template id="imagetabs">{image_tabs}</template>
  </div>
  <div id="stage" class="by-style">{''.join(sets)}</div>
</section>

<section aria-labelledby="h-picks">
  <h2 id="h-picks">Your shortlist <span id="pickcount" class="note"></span></h2>
  <p id="pickempty">Nothing shortlisted yet. Use the Shortlist button under any poster.</p>
  <ul id="picklist"></ul>
  <div class="row"><button type="button" class="ghost" id="copy" disabled>Copy the list</button><span class="note" id="copied" role="status"></span></div>
  <textarea id="picktext" readonly hidden aria-label="Shortlist as text"></textarea>
  <p class="note" id="pickstatus">Saved in this browser. Copy the list and paste it into the chat.</p>
</section>

<section aria-labelledby="h-held">
  <h2 id="h-held">How the styles held up</h2>
  <div class="two">
    <div><h3>What I see</h3>
      <ul class="plain">
        <li>Styles 01, 02 and 05 hold for all six images. In each, the name is exactly as wide as the base of the picture.</li>
        <li>Styles 03 and 04 hold as well. The Shivalinga and Nandi carry a hoarding as well as the temple does.</li>
        <li>The temple with Nandi is a wide picture. It is strongest in 03 and 04 and looks small in the upright posters.</li>
        <li>Style 06 works for every image. With the Shivalinga it becomes a picture of the hall.</li>
        <li>Styles 07, 08 and 09 lean on a sky. The interior has none, so there they become darker posters of the hall.</li>
        <li>In 08 the flag crosses the name at a different letter in each view. In the tower-left view I lifted the name clear of it.</li>
      </ul></div>
    <div><h3>My pick</h3>
      <p>For the set of five I would print style 01. It is the one style where the temple, the Shivalinga and Nandi all read at the same strength, and the name sits in the same place on every poster.</p>
      <p>For hoardings I would use style 03 with a side view, because the temple is largest there. For a gate or a long wall I would use style 04 with the temple and Nandi together.</p>
    </div>
  </div>
</section>

<section aria-labelledby="h-changed">
  <h2 id="h-changed">What I changed in the pictures</h2>
  <ul class="plain">
    <li><b>Cut-outs.</b> In styles 01 to 05 each subject is lifted out of its picture and set on the brand black. Nothing inside the temple or the Shivalinga is repainted.</li>
    <li><b>Nandi.</b> The statue is black stone and vanished on a black ground. In the cut-out styles I brightened the statue so its form shows. Styles 06 to 09 show it untouched.</li>
    <li><b>Shivalinga.</b> The cut-out shows the linga and its pedestal alone. The hanging vessel and its stream belong to the hall and stay in styles 06 to 09. The jaladhari is still the light stone of the current picture.</li>
    <li><b>Temple and Nandi.</b> No picture shows both, so the sixth image is composed from the tower-left view and the Nandi picture, standing on one line with Nandi facing the door. His size and distance are set by eye. In styles 06 to 09 the sky behind them is painted from the temple picture's own sky colours, and there are no trees or paving.</li>
    <li><b>Mirrored boards.</b> In the tower-left view and the sixth image the steps are on the right, so styles 03 and 04 put the name on the right and the picture on the left.</li>
  </ul>
</section>

<section aria-labelledby="h-dec">
  <h2 id="h-dec">Decisions I need from you</h2>
  <ol class="plain">
    <li>Your shortlist: which style for the set of five posters, and which for hoardings and banners.</li>
    <li>For the temple with Nandi: is the composed pair good enough for now? Tell me if Nandi should be larger, smaller, nearer or further. One true picture of both would be better for a final print.</li>
    <li>Is the brightened Nandi acceptable, or should he stay as dark as in the picture?</li>
    <li>Still open from round one: whether black is acceptable for an auspicious announcement, the status wording and the spelling of <span lang="hi">पहाड़ीखेड़ा</span>, the address and phone numbers, where the QR should point, and the sizes you will print.</li>
    <li>Still needed: the Nandi picture as an original file, the interior with the dark jaladhari, and your word on enlarging the pictures with an AI upscaler for prints that people stand close to.</li>
  </ol>
</section>

<section aria-labelledby="h-files">
  <h2 id="h-files">Files on your Mac</h2>
  <p>Everything is in <code>Desktop/Temple/rtam-posters/out</code>. There is one folder per image, from <code>01-front</code> to <code>06-temple-and-nandi</code>. Each holds the nine styles as true-size PDFs with PNG previews and a contact sheet. The folder <code>00-compare</code> has one sheet per style and a matrix of all 54.</p>
</section>
</div>

<div id="lb" hidden role="dialog" aria-modal="true" aria-label="Enlarged poster">
  <div class="lbtop"><span id="lbcap"></span><button type="button" id="lbx">Close</button></div>
  <div class="lbimg"><img alt=""></div>
  <div class="lbfoot"><button type="button" id="lbprev">Previous</button><button type="button" id="lbpick" aria-pressed="false">Shortlist</button><button type="button" id="lbnext">Next</button></div>
</div>
<script>{JS}</script>
'''
out = Path(sys.argv[1]); out.write_text(page, encoding='utf-8')
print(f'{out.name}: {len(page.encode()) / 1e6:.2f} MB (images {total / 1e6:.2f} MB before base64)')
