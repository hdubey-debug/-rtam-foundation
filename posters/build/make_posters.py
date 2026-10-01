#!/usr/bin/env python3
"""RTAM poster system: nine layouts applied to six subjects.

Everything is laid out in page units (1 unit = 0.1 in at the reference size), so a design scales to any print size by
changing one number. Photographs are composed by prep.py and cutout.py; type and marks stay vector.

usage: python3 make_posters.py [--subjects front,right,...] [--styles 01,03,...] [--k 2]"""
import sys, time, json, argparse
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).parent))
import prep, render, cutout

ROOT = Path(__file__).resolve().parent.parent
SRC, OUTROOT, PAGES = ROOT / 'source', ROOT / 'out', ROOT / 'build' / 'pages'
MARK, FONT = '../../brand/marks/', '../../brand/fonts/'

# brand tokens (brand/palette/colors.json v0.2.0)
MAHAKALA, CHANDRA, INK = '#141414', '#EDEBE6', '#1A1A1A'
BHASMA, BHASMA_DEEP, STONE, GOLD, TAMRA = '#C9C2B6', '#8F887C', '#B8B1A4', '#C8A15A', '#7A5423'

# copy (the address block is the founder-locked letterhead foot, both scripts in full)
ADDR_DN = 'ग्राम पहाड़ीखेड़ा, मनेरी रोड · बरेला – 483001 · जिला जबलपुर (म.प्र.)'
ADDR_EN = 'Vill. Pahadi Kheda, Maneri Road · Barela (M.P.) – 483001'
FOUND_DN = 'संस्थापक — श्री राजेश दुबे · श्रीमती किरण बाला दुबे'
FOUND_EN = 'Founders — Shri Rajesh Dubey · Smt. Kiran Bala Dubey'
PHONES = '9098225177 · 9407381069'
STATUS_DN, STATUS_EN = 'पहाड़ीखेड़ा में बन रहा है', 'Now rising at Pahadi Kheda'      # the opening of a sentence the name completes
STATUS_W = (8.45, 20.15)                                                              # their widths in em (text-metrics.json)
MOTTO = 'ऋतस्य पन्थाम्'
NOTE_DN, NOTE_EN = 'प्रस्तावित स्वरूप', 'Architect’s visualisation'
QR_DN, QR_EN = 'मंदिर को 3D में देखें', 'Walk through in 3D'
NAME_DN = 'ऋतम्भरेश्वर मंदिर'

def u(n): return f'{n / 10:.4f}in'

def css(w_in, h_in, ground):
    return f"""
@font-face{{font-family:'Tiro';src:url('{FONT}tiro-devanagari-sanskrit-400.ttf')}}
@font-face{{font-family:'Cinzel';font-weight:400;src:url('{FONT}cinzel-400.ttf')}}
@font-face{{font-family:'Cinzel';font-weight:500;src:url('{FONT}cinzel-500.ttf')}}
@font-face{{font-family:'Inter';font-weight:300;src:url('{FONT}inter-300.ttf')}}
@font-face{{font-family:'Inter';font-weight:400;src:url('{FONT}inter-400.ttf')}}
@font-face{{font-family:'Inter';font-weight:500;src:url('{FONT}inter-500.ttf')}}
@page{{size:{w_in}in {h_in}in;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{-webkit-print-color-adjust:exact;print-color-adjust:exact;background:{ground}}}
.page{{position:relative;width:{w_in}in;height:{h_in}in;overflow:hidden;background:{ground}}}
.a{{position:absolute}} .c{{position:absolute;left:0;right:0;text-align:center}}
.deva{{font-family:'Tiro',serif;font-weight:400;line-height:1.55}}
.caps{{font-family:'Cinzel',serif;font-weight:500;letter-spacing:.22em;text-transform:uppercase;line-height:1.55}}
.echo{{font-family:'Inter',sans-serif;font-weight:400;letter-spacing:.2em;text-transform:uppercase}}
img{{display:block}}
"""

def page(name, w_u, h_u, ground, body):
    PAGES.mkdir(parents=True, exist_ok=True)
    html = f'<!doctype html><html lang="hi"><head><meta charset="utf-8"><title>{name}</title><style>{css(w_u / 10, h_u / 10, ground)}</style></head><body><div class="page">{body}</div></body></html>'
    p = PAGES / f'{name}.html'; p.write_text(html, encoding='utf-8'); return p

def address(x, y, w, size, ink, founders=False, phones=True, align='center'):
    """The address pair (and optionally the founders pair), proportioned as on the letterhead foot:
    Devanagari : caps = 9.5 : 6.4, founders line 9 : 9.5, leading 1.55."""
    cap = size * 6.4 / 9.5; meta = size * 9 / 9.5
    rows = [f'<div class="deva" style="font-size:{u(size)}">{ADDR_DN}</div>',
            f'<div class="caps" style="font-size:{u(cap)};margin-top:{u(size * .08)}">{ADDR_EN}</div>']
    if founders:
        rows += [f'<div class="deva" style="font-size:{u(meta)};margin-top:{u(size * .34)}">{FOUND_DN}' + (f' &nbsp;·&nbsp; मो. {PHONES}' if phones else '') + '</div>',
                 f'<div class="caps" style="font-size:{u(cap)};margin-top:{u(size * .08)}">{FOUND_EN}' + (f' &nbsp;·&nbsp; Mob. {PHONES}' if phones else '') + '</div>']
    elif phones:
        rows += [f'<div class="deva" style="font-size:{u(meta)};margin-top:{u(size * .34)}">मो. {PHONES}</div>']
    return f'<div class="a" style="left:{u(x)};top:{u(y)};width:{u(w)};text-align:{align};color:{ink}">' + ''.join(rows) + '</div>'

def label(x, y, w, dn, en, size, ink, ink2, align='center', stack=False):
    """A structural label: Devanagari leads, a small letterspaced English echo follows (never letterspace Devanagari)."""
    e = size * .46
    if stack:
        inner = f'<div class="deva" style="font-size:{u(size)};line-height:1.25">{dn}</div><div class="echo" style="font-size:{u(e)};color:{ink2};margin-top:{u(size * .12)}">{en}</div>'
    else:
        inner = f'<span class="deva" style="font-size:{u(size)}">{dn}</span><span class="echo" style="font-size:{u(e)};color:{ink2};margin-left:{u(size * .55)}">{en}</span>'
    return f'<div class="a" style="left:{u(x)};top:{u(y)};width:{u(w)};text-align:{align};color:{ink};white-space:nowrap">{inner}</div>'

def rule(x, y, w, ink=STONE, t=.28):
    return f'<div class="a" style="left:{u(x)};top:{u(y)};width:{u(w)};height:{u(t)};background:{ink}"></div>'

def img(src, x, y, w, h=None):
    hh = f'height:{u(h)};' if h else ''
    return f'<img class="a" src="{src}" style="left:{u(x)};top:{u(y)};width:{u(w)};{hh}">'

def save_rgba(rgba, path):
    Image.fromarray(np.clip(rgba + .5, 0, 255).astype(np.uint8), 'RGBA').save(path)

# ------------------------------------------------------------------ subjects
class Subject:
    """One picture: its photograph (for plate and sky layouts) and its cut-out (for the layouts on the brand black).
    Geometry is in source pixels: pl..pr is the span of the base (what the name's width matches), top the highest point,
    foot the lowest, line the level that stands on a ground rule, axis the x that goes on a page axis."""
    def __init__(s, key, n, slug, title, deva, src, kind='exterior', paxis=None, line=None, axis=None, mirror=False, clouds=(), overlap=16., geom=None, note=''):
        s.key, s.n, s.slug, s.title, s.deva, s.kind, s.mirror, s.clouds, s.overlap, s.note = key, n, slug, title, deva, kind, mirror, list(clouds), overlap, note
        s.src = SRC / src if src else None; s._paxis, s._line, s._axis, s._geom = paxis, line, axis, geom; s._photo, s._cut = {}, {}
    @property
    def out(s): return OUTROOT / f'{s.n}-{s.slug}'
    def photo(s, k):
        if k not in s._photo:
            im = prep.upscale(prep.load(s.src), k); s._photo[k] = (im, prep.sky_matte(im) if s.kind == 'exterior' else None)
        return s._photo[k]
    @property
    def W(s): return Image.open(s.src).size[0]
    @property
    def H(s): return Image.open(s.src).size[1]
    def cut(s, k):
        if k in s._cut: return s._cut[k]
        PAGES.mkdir(parents=True, exist_ok=True); f = f'cut-{s.slug}.png'
        if s.key == 'front':                                   # the approved hand-measured outline
            im, _ = s.photo(k); rgba, (x0, y0) = prep.cut_building(im, k)
            g = dict(x0=x0 / k, y0=y0 / k, pl=113., pr=1316., top=16., foot=979.)
        else:
            full, a, _ = cutout.make(s.key, k); g = cutout.geometry(a, k)
            X0, Y0, X1, Y1 = [int(v) for v in cutout.bbox(a, .01)]; pad = 6
            X0, Y0 = max(0, X0 - pad), max(0, Y0 - pad); rgba = full[Y0:Y1 + pad, X0:X1 + pad]; g.update(x0=X0 / k, y0=Y0 / k)
            fr = int(round(g['foot'] * k)); xs = np.where((a[max(0, fr - 5 * k):fr] > .5).any(0))[0]; g.update(c0=xs.min() / k, c1=(xs.max() + 1) / k)
        if s.key != 'front': rgba = cutout.bleed(rgba)
        save_rgba(rgba, PAGES / f)
        g.update(file=f, w=rgba.shape[1] / k, h=rgba.shape[0] / k)
        g['axis'] = s._axis if s._axis is not None else (g['pl'] + g['pr']) / 2
        g['line'] = s._line if s._line is not None else g['foot']
        s._cut[k] = g; return g
    def paxis(s, k=2):
        return s._paxis if s._paxis is not None else s.cut(k)['axis']
    def pfull(s, k=2):
        """Axis used by the full-bleed photograph layouts (07, 08, 09)."""
        return getattr(s, 'paxis_full', None) or s.paxis(k)
    def aspect(s, k, on='foot'):
        c = s.cut(k); return (c['pr'] - c['pl']) / (c[on] - c['top'])

class Pair(Subject):
    """The sixth image: the temple (side view, entrance to the right) with the Nandi pavilion before its entrance, Nandi
    facing the door, both standing on one line. It is a composed pair of two cut-outs: no single render shows both."""
    def __init__(s, temple, nandi, scale=.42, gap=44):
        Subject.__init__(s, 'pair', '06', 'temple-and-nandi', 'Temple and Nandi', 'मंदिर और नंदी', None, kind='pair', mirror=True)
        s.parts, s.scale, s.gap = (temple, nandi), scale, gap; s.src = temple.src; s.clouds = temple.clouds
    def photo(s, k): return s.parts[0].photo(k)
    def cut(s, k):
        if k in s._cut: return s._cut[k]
        A, B = s.parts[0].cut(k), s.parts[1].cut(k); sc = s.scale
        a = np.asarray(Image.open(PAGES / A['file']), dtype=np.float32); b = np.asarray(Image.open(PAGES / B['file']), dtype=np.float32)
        b = cutout.resize_rgba(b, (round(b.shape[1] * sc), round(b.shape[0] * sc)))
        fa = round((A['foot'] - A['y0']) * k); fb = round((B['foot'] - B['y0']) * k * sc)             # both feet on one line
        xb = round((A['pr'] - A['x0'] + s.gap) * k - (B['pl'] - B['x0']) * k * sc); yb = fa - fb
        canvas = np.zeros((max(a.shape[0], yb + b.shape[0]), max(a.shape[1], xb + b.shape[1]), 4), np.float32)
        canvas[:a.shape[0], :a.shape[1]] = a
        sub = canvas[yb:yb + b.shape[0], xb:xb + b.shape[1]]; al = b[..., 3:4] / 255.
        sub[..., :3] = np.where(al > 0, b[..., :3], sub[..., :3]) * np.where(sub[..., 3:4] > 0, al, 1) + sub[..., :3] * np.where(sub[..., 3:4] > 0, 1 - al, 0)
        sub[..., 3:4] = np.maximum(sub[..., 3:4], b[..., 3:4])
        canvas = cutout.bleed(canvas); f = f'cut-{s.slug}.png'; save_rgba(canvas, PAGES / f)
        solid = canvas[..., 3] > 127; colsum = solid.any(0); bottoms = np.where(colsum, solid.shape[0] - 1 - np.argmax(solid[::-1], axis=0), 10 ** 9)
        g = dict(file=f, x0=0., y0=0., w=canvas.shape[1] / k, h=canvas.shape[0] / k, pl=A['pl'] - A['x0'], pr=xb / k + (B['pr'] - B['x0']) * sc,
                 top=A['top'] - A['y0'], foot=fa / k, tx0=A['x0'], ty0=A['y0'], far=float(bottoms.min()) / k,
                 c0=A['c0'] - A['x0'], c1=xb / k + (B['c1'] - B['x0']) * sc, nandi_x=xb / k, nandi_scale=sc)
        g['axis'] = (g['pl'] + g['pr']) / 2; g['line'] = g['foot']
        s._cut[k] = g; return g

SUBJECTS = {}
def _add(sub): SUBJECTS[sub.key] = sub; return sub
FRONT = _add(Subject('front', '01', 'front', 'Front elevation', 'सामने से', '01-exterior-front.png', paxis=717, line=957, axis=717, clouds=[(0, 20, 360, 350)]))
FRONT.paxis_full = .4959 * 1448
RIGHT = _add(Subject('right', '02', 'side-tower-right', 'Side view, tower right', 'दाहिनी ओर से', '02-exterior-tower-right.png', clouds=[(0, 30, 330, 230)]))
LEFT = _add(Subject('left', '03', 'side-tower-left', 'Side view, tower left', 'बाईं ओर से', '03-exterior-tower-left.png', mirror=True, clouds=[(0, 20, 340, 200), (760, 20, 1448, 230)], overlap=-3.))
LINGA = _add(Subject('linga', '04', 'shivalinga', 'Shivalinga', 'शिवलिंग', '04-interior-shivalinga.png', kind='interior', paxis=cutout.LINGA_AXIS, axis=cutout.LINGA_AXIS, line=812.5))
NANDI = _add(Subject('nandi', '05', 'nandi', 'Nandi pavilion', 'नंदी मंडप', '05-nandi-pavilion.from-webp.png', clouds=[(0, 20, 400, 230)], overlap=-3.))
PAIR = _add(Pair(LEFT, NANDI))

def place(sub, k, base_w, axis_x, y, on='foot'):
    """The cut-out with its base `base_w` wide, its axis at axis_x, and its `on` level (foot or line) at y."""
    c = sub.cut(k); s = base_w / (c['pr'] - c['pl']); ref = c[on]
    X, Y = axis_x - (c['axis'] - c['x0']) * s, y - (ref - c['y0']) * s
    geo = dict(s=s, top=y - (ref - c['top']) * s, pl=axis_x - (c['axis'] - c['pl']) * s, pr=axis_x + (c['pr'] - c['axis']) * s,
               line=y - (ref - c['line']) * s, foot=y - (ref - c['foot']) * s, x=X, y=Y)
    return img(c['file'], X, Y, c['w'] * s), geo

# ------------------------------------------------------------------ photographic grounds
def clamp_ix(ix, iw, lo, hi):
    """Keep the picture covering lo..hi."""
    return max(hi - iw, min(lo, ix))

def melt_ground(sub, name, k, pw, ph, ix, iy, iw, ground_rgb, night=None, bottom=(.90, 1.0), top_melt=None, grade=(250, .35), left=None, right=None,
                grade_cols=None, sky=None, clouds=None, cut_rows=None):
    """Full-page raster: the picture at (ix,iy), width iw (page units); its sky continued to the top of the page
    (travelling to the ground colour when `night` is given, staying a natural sky otherwise); the plaza melting
    into the ground; optional side melts and a sideways sky grade (fractions of the picture width).
    Interiors have no sky: they melt into the ground at the top (top_melt) and the bottom instead.
    cut_rows: also write an RGBA cut-out of the top of the picture (sky removed) for type-behind-building layouts."""
    im, matte = sub.photo(k); h, w, _ = im.shape; ppu = w / iw
    cw, ch = round(pw * ppu), round(ph * ppu); x0, y0 = round(ix * ppu), round(iy * ppu)
    g = im
    if matte is not None:
        for box in (clouds or []): g = prep.repaint_clouds(g, matte, tuple(round(v * k) for v in box))
        if grade: g = prep.grade_sky(g, matte, round(grade[0] * k), grade[1], ground_rgb)
        for gc in (grade_cols or []): g = prep.grade_sky_cols(g, matte, round(gc[0] * w), gc[1], ground_rgb, from_left=gc[2])
    body = prep.melt_rows(g, round(bottom[0] * h), round(bottom[1] * h), ground_rgb) if bottom else g
    if top_melt: body = prep.melt_rows(body, round(top_melt[0] * h), round(top_melt[1] * h), ground_rgb)
    if y0 > 0 and matte is not None:
        kw = dict(sky or {})
        if night is not None: kw.update(ground=ground_rgb, **night)
        block = np.concatenate([prep.continue_sky(g, y0, **kw), body], 0)
    elif y0 > 0:
        fill = np.empty((y0, w, 3), np.float32); fill[:] = np.array(ground_rgb, np.float32); block = np.concatenate([fill, body], 0)
    else: block = body
    if left: block = prep.melt_cols(block, round(left[0] * w), round(left[1] * w), ground_rgb)
    if right: block = prep.melt_cols(block, round(right[0] * w), round(right[1] * w), ground_rgb)
    canvas = np.empty((ch, cw, 3), np.float32); canvas[:] = np.array(ground_rgb, np.float32)
    bh, bw = block.shape[:2]; sx, dx = max(0, -x0), max(0, x0); ww = min(bw - sx, cw - dx); hh = min(bh, ch)
    canvas[:hh, dx:dx + ww] = block[:hh, sx:sx + ww]
    p = PAGES / f'{name}-ground.jpg'; prep.save(canvas, p, 93)
    meta = dict(ppu=round(ppu, 3), px=[cw, ch], ix=x0 / ppu, iy=y0 / ppu)
    if cut_rows and matte is not None:
        rows = round(cut_rows * k); save_rgba(prep.cutout(g, matte, rows), PAGES / f'{name}-cutout.png')
        meta.update(cut=f'{name}-cutout.png', cut_h=rows / ppu)
    return p.name, meta

def plate(sub, name, k, iw_u, ext_u=0., crop_bottom=1.0, tone=False):
    """A hard-edged plate: the picture with its own sky continued naturally above it (no travel to a ground)."""
    im, matte = sub.photo(k); h, w, _ = im.shape; ppu = w / iw_u
    if tone and matte is not None: im = prep.tone_sky(im, matte)
    body = im[:round(h * crop_bottom)]
    block = np.concatenate([prep.continue_sky(im, round(ext_u * ppu), ground=None), body], 0) if (ext_u and matte is not None) else body
    p = PAGES / f'{name}-plate.jpg'; prep.save(block, p, 93)
    return p.name, block.shape[0] / ppu

NIGHT = dict(d_keep=0.0, chroma_hold=.15)
LOCKUP = {'night': MARK + 'rtambhareshvara-mandir-lockup-devanagari-led-garbhagriha.svg', 'day': MARK + 'rtambhareshvara-mandir-lockup-devanagari-led.svg'}
CHAKRA = {'night': MARK + 'rtam-chakra-garbhagriha.svg', 'day': MARK + 'rtam-chakra-day.svg'}
QR = {'night': MARK + 'qr-3d-tour-on-dark.svg', 'day': MARK + 'qr-3d-tour-on-light.svg'}
INKS = {'night': (BHASMA, BHASMA_DEEP, STONE, BHASMA), 'day': (INK, INK, STONE, TAMRA)}     # text, quiet, hairline, motto
RULE_TO_STEPS = True     # hoarding, three-quarter views: end the ground line under the foot of the steps (False: run it the full width)
LOCK_H = 251.5 / 576          # the lockup's ink height over its ink width (matra top to bindu bottom)

def status(cx, y, half, reg, size=5.4, dn=STATUS_DN, en=STATUS_EN):
    """The status label on a hairline that runs out to `half` either side of cx: the hinge between picture and foot."""
    ink, quiet, hair, _ = INKS[reg]
    w = STATUS_W[0] * size + .55 * size + STATUS_W[1] * size * .46; gap = size * 1.5
    mid = y + size * (.275 + .425)                        # centre of the Devanagari letter body in a 1.55 line
    return (rule(cx - half, mid, half - w / 2 - gap, hair) + rule(cx + w / 2 + gap, mid, half - w / 2 - gap, hair)
            + label(cx - w / 2 - 10, y, w + 20, dn, en, size, ink, quiet))

def colophon(top, reg, pw=240, with_status=True, s=4.2):
    """Foot shared by the portrait layouts: status hinge; chakra | address pair + phones | QR; two small notes; the motto."""
    ink, quiet, hair, motto = INKS[reg]; b = ''
    if with_status: b += status(pw / 2, top, pw / 2 - 16, reg)
    b += img(CHAKRA[reg], 18, top + 12.6, 24)
    b += address(46, top + 12, pw - 92, s, ink, founders=False)
    b += img(QR[reg], pw - 42, top + 12.6, 24)
    b += label(8, top + 38.8, 44, NOTE_DN, NOTE_EN, 2.5, quiet, quiet, stack=True)
    b += label(pw - 52, top + 38.8, 44, QR_DN, QR_EN, 2.5, quiet, quiet, stack=True)
    b += f'<div class="c deva" style="top:{u(top + 38.2)};font-size:{u(3.6)};color:{motto}">{MOTTO}</div>'
    return b

def lockup(reg, ink_x, ink_w, matra_top=None, rule_y=None):
    """The city-print lockup placed by its ink (in the 640 x 380 master: ink x 31..607, matra top 56, rule 216, bindu bottom 307.5)."""
    bw = ink_w * 640 / 576; bx = ink_x - 31 / 640 * bw
    by = rule_y - 216 / 640 * bw if rule_y is not None else matra_top - 56 / 640 * bw
    f = bw / 640
    return img(LOCKUP[reg], bx, by, bw), dict(top=by + 56 * f, rule=by + 216 * f, bottom=by + 307.5 * f, base=by + 140.8 * f, caps=by + 273 * f, D=ink_w / 6.0, hair=1.5 * f, x=ink_x, w=ink_w)

def kicker(cx, y, size, ink, quiet, dn=STATUS_DN, en=STATUS_EN):
    """The opening line: 'being built at Pahadi Kheda', which the name below it completes. English echo beneath."""
    return (f'<div class="a deva" style="left:{u(cx - 150)};top:{u(y)};width:{u(300)};text-align:center;font-size:{u(size)};line-height:1;color:{ink};white-space:nowrap">{dn}</div>'
            f'<div class="a echo" style="left:{u(cx - 150)};top:{u(y + size * 1.2)};width:{u(300)};text-align:center;font-size:{u(size * .30)};font-weight:500;color:{quiet};white-space:nowrap">{en}</div>')

def note(x, y, w, reg='night', size=2.5, align='center'):
    return label(x, y, w, NOTE_DN, NOTE_EN, size, INKS[reg][1], INKS[reg][1], align=align)

# ------------------------------------------------------------------ the family: the lamp in the dark
def L01(sub, k):
    """Portrait 24 x 36 · Adhishthana. The name bears the subject: the lockup is as wide as its base and it stands on the name.
    For the front elevation chakra, flag, door and name share one axis (the icon is the linga seen from above)."""
    PW, PH = 240, 360; asp = sub.aspect(k)
    pw = 192. if sub.key == 'front' else min(208., 243.8 / (.46163 + 1 / asp))
    mt = 312.3 - pw * LOCK_H; foot = mt - 4.8 * pw / 192
    b = img(CHAKRA['night'], 108, 12, 24) + kicker(120, 46, 9.6, BHASMA, BHASMA_DEEP)
    t, g = place(sub, k, pw, 120, foot, 'foot'); b += t
    l, lg = lockup('night', g['pl'], pw, matra_top=mt); b += l
    b += address(16, lg['bottom'] + 8, 208, 4.2, BHASMA, founders=False) + note(0, 348, PW)
    return (PW, PH, MAHAKALA, b), dict(geo=g, lockup=lg)

def L02(sub, k):
    """Portrait 24 x 36 · Shirshak. The same parts with the name on top, for flex hung at ground level where the foot gets hidden."""
    PW, PH = 240, 360; asp = sub.aspect(k); c = sub.cut(k)
    pw = 192. if sub.key == 'front' else min(208., 248.7 / (.495 + 1 / asp))
    b = kicker(120, 14, 9.6, BHASMA, BHASMA_DEEP)
    l, lg = lockup('night', 120 - (c['axis'] - c['pl']) * pw / (c['pr'] - c['pl']), pw, matra_top=37); b += l
    ztop, zbot, h = lg['bottom'] + .35 * lg['D'], 285.7, pw / asp
    t, g = place(sub, k, pw, 120, zbot - max(0., (zbot - ztop - h) / 2), 'foot'); b += t
    b += colophon(288.7, 'night', with_status=False)
    return (PW, PH, MAHAKALA, b), dict(geo=g, lockup=lg)

def L03(sub, k):
    """Landscape 2:1 hoarding · Ek Rekha. One line: the lockup's own hairline runs the width of the board and the subject stands on it.
    A subject whose entrance is on its right is mirrored (name right, picture left) so the line arrives at the steps."""
    PW, PH, Y = 480, 240, 168; m = sub.mirror; X = (lambda x, w=0: PW - x - w) if m else (lambda x, w=0: x)
    l, lg = lockup('night', X(24, 232), 232, rule_y=Y)
    bw = 168. if sub.key == 'front' else min(186., 132 * sub.aspect(k, 'line')); cx, ct = X(365), X(140)
    t, g = place(sub, k, bw, cx, Y, 'line'); c = sub.cut(k)
    r0, r1 = 24., PW - 24.
    if RULE_TO_STEPS and 'c0' in c and sub.kind in ('exterior', 'pair') and sub.key != 'nandi':     # a perspective view: the line is the path to the steps
        e0, e1 = g['pl'] + (c['c0'] - c['pl']) * g['s'], g['pl'] + (c['c1'] - c['pl']) * g['s']
        if m: r0 = e0 + .6
        else: r1 = e1 - .6
    b = rule(r0, Y - lg['hair'] / 2, r1 - r0, STONE, lg['hair']) + l + t
    b += img(CHAKRA['night'], ct - 16, 16, 32) + kicker(ct, 62, 12, BHASMA, BHASMA_DEEP)
    b += address(cx - 90, max(181, g['foot'] + 6), 180, 4.4, BHASMA, founders=False, phones=False) + note(cx - 90, 214, 180, size=2.6)
    return (PW, PH, MAHAKALA, b), dict(geo=g, lockup=lg)

def L04(sub, k):
    """Landscape 3:1 gate banner · Torana. Name, picture, and where it is rising, read along one line."""
    PW, PH, Y = 720, 240, 174; m = sub.mirror; X = (lambda x, w=0: PW - x - w) if m else (lambda x, w=0: x)
    l, lg = lockup('night', X(28, 220), 220, rule_y=Y)
    bw = 178. if sub.key == 'front' else min(222., 140 * sub.aspect(k, 'line')); cx, ct = X(362 if sub.key == 'front' else 379.3), X(574)
    t, g = place(sub, k, bw, cx, Y, 'line'); b = rule(28, Y - lg['hair'] / 2, PW - 56, STONE, lg['hair']) + l + t
    fs = 15.0
    b += f'<div class="a deva" style="left:{u(ct - 150)};top:{u(lg["base"] - .70 * fs)};width:{u(300)};text-align:center;font-size:{u(fs)};line-height:1;color:{BHASMA};white-space:nowrap">{STATUS_DN}</div>'
    b += f'<div class="a echo" style="left:{u(ct - 150)};top:{u(lg["caps"] + 2.4)};width:{u(300)};text-align:center;font-size:{u(4.5)};font-weight:500;color:{BHASMA_DEEP};white-space:nowrap">{STATUS_EN}</div>'
    b += img(CHAKRA['night'], ct - 22, 44, 44)
    return (PW, PH, MAHAKALA, b), dict(geo=g, lockup=lg)

def L05(sub, k):
    """Standee 85 x 200 cm · Stambha. Name at eye level, the picture below it, QR and address under the picture; the lowest
    third stays dark (hidden by chairs, people and the base) and closes on a foot line with the motto."""
    PW, PH = 240, 564; asp = sub.aspect(k); c = sub.cut(k); pw = 204. if asp < 1.4 else 208.
    x0 = 120 - (c['axis'] - c['pl']) * pw / (c['pr'] - c['pl'])
    b = img(CHAKRA['night'], 106, 16, 28) + kicker(120, 56, 10.5, BHASMA, BHASMA_DEEP)
    l, lg = lockup('night', x0, pw, matra_top=84); b += l
    ztop, zbot, h = lg['bottom'] + .35 * lg['D'], 348.3, pw / asp
    t, g = place(sub, k, pw, 120, min(zbot, ztop + h + max(0., (zbot - ztop - h) / 2)), 'foot'); b += t
    top = 368.3
    b += img(QR['night'], 20, top, 34) + label(12, top + 36.5, 50, QR_DN, QR_EN, 2.5, BHASMA_DEEP, BHASMA_DEEP, stack=True)
    b += address(62, top + 6, 160, 4.8, BHASMA, founders=False)
    b += rule(x0, 494, pw, STONE, lg['hair'])
    b += f'<div class="c deva" style="top:{u(500)};font-size:{u(4.4)};color:{BHASMA}">{MOTTO}</div>' + note(0, 513, PW)
    cm = lambda y: round((PH - y) * 200 / PH)
    return (PW, PH, MAHAKALA, b), dict(geo=g, lockup=lg, cm_from_floor=dict(name_top=cm(lg['top']), name_bottom=cm(lg['bottom']), picture_foot=cm(g['foot']), qr_centre=cm(top + 17)))

def L06(sub, k):
    """Portrait 24 x 36 · Chandra. The day register for walls indoors: moon-paper, ink lockup, the picture as a plate."""
    PW, PH, px, win = 240, 360, 16, 208; name = f'{sub.slug}--06'
    if sub.kind == 'interior':
        iw = 255.; pl_file, plh = plate(sub, name, k, iw); xi = clamp_ix(120 - sub.paxis(k) * iw / sub.W, iw, px, px + win)
        l, lg = lockup('day', 30, 180, matra_top=22)
    else:
        iw = 216.; c = sub.cut(k); pl_file, plh = plate(sub, name, k, iw, 14.6, 1040 / 1086, tone=True)
        xi = clamp_ix(120 - sub.paxis(k) * iw / sub.W, iw, px, px + win)
        l, lg = lockup('day', xi + c['pl'] * iw / sub.W, (c['pr'] - c['pl']) * iw / sub.W, matra_top=22)
    py = lg['bottom'] + 9.5
    b = l + f'<div class="a" style="left:{u(px)};top:{u(py)};width:{u(win)};height:{u(plh)};overflow:hidden">' + img(pl_file, xi - px, 0, iw) + '</div>'
    b += colophon(py + plh + 8.5, 'day')
    return (PW, PH, CHANDRA, b), dict(plate_h=plh, lockup=lg)

# ------------------------------------------------------------------ alternates: the picture kept whole
def L07(sub, k):
    """Portrait 24 x 36 · Akasha. The blended version: the sky deepens into the sanctum dark, where the name sits; the ground melts
    into the foot. An interior has no sky, so the hall itself emerges from the dark."""
    PW, PH = 240, 360; name = f'{sub.slug}--07'
    if sub.kind == 'interior':
        iw, iy = 274.5, 124; ix = clamp_ix(120 - sub.pfull(k) * iw / sub.W, iw, 0, PW)
        ground, meta = melt_ground(sub, name, k, PW, PH, ix, iy, iw, prep.MAHAKALA, bottom=(.84, 1.0), top_melt=(.34, 0.0))
    else:
        iw, iy = 244, 124; ix = clamp_ix(120 - sub.pfull(k) * iw / sub.W, iw, 0, PW)
        ground, meta = melt_ground(sub, name, k, PW, PH, ix, iy, iw, prep.MAHAKALA, night=dict(NIGHT, d_full=.484), grade=(330, .40))
    b = img(ground, 0, 0, PW, PH) + img(LOCKUP['night'], 47, 3, 146) + colophon(308.4, 'night')
    return (PW, PH, MAHAKALA, b), meta

def L08(sub, k):
    """Portrait 24 x 36 · Dhvaja. The name is set in the picture itself: in the sky, with the flag-staff and kalasha rising in front
    of it (for the interior, in the dark above the linga). Bends two brand rules; shown as an alternate."""
    PW, PH = 240, 360; fs = 208 / 6.0; name = f'{sub.slug}--08'
    if sub.kind == 'interior':
        iw, iy = 300., 70.; ix = clamp_ix(120 - sub.pfull(k) * iw / sub.W, iw, 0, PW); s = iw / sub.W
        ground, meta = melt_ground(sub, name, k, PW, PH, ix, iy, iw, prep.MAHAKALA, bottom=(.86, 1.0), top_melt=(.40, 0.0))
        base = iy + sub.cut(k)['top'] * s - 9.
        b = img(ground, 0, 0, PW, PH)
    else:
        iw, iy = 264, 102; ix = clamp_ix(120 - sub.pfull(k) * iw / sub.W, iw, 0, PW); s = iw / sub.W
        base = 121.0 if sub.key == 'front' else iy + sub.cut(k)['top'] * s + sub.overlap
        ground, meta = melt_ground(sub, name, k, PW, PH, ix, iy, iw, prep.MAHAKALA, night=None, grade=(260, .22),
                                   sky=dict(zenith=(18, 78, 196), tau=.5), clouds=sub.clouds, cut_rows=300)
        b = img(ground, 0, 0, PW, PH)
    b += kicker(120, base - .70 * fs - 24, 7.4, CHANDRA, CHANDRA)
    b += f'<div class="c deva" style="top:{u(base - .70 * fs)};font-size:{u(fs)};line-height:1;color:{CHANDRA};white-space:nowrap">{NAME_DN}</div>'
    if meta.get('cut'): b += img(meta['cut'], meta['ix'], meta['iy'], iw, meta['cut_h'])
    b += img(LOCKUP['night'] + '#svgView(viewBox(28,262,584,52))', 64, 304.0, 112, 112 * 52 / 584)
    b += colophon(308.0, 'night', with_status=False)
    return (PW, PH, MAHAKALA, b), meta

def L09(sub, k):
    """Portrait 24 x 36 · Patta. The letterhead, enlarged, for the site notice board: sulba head (13:12:5), the picture between the
    bands, the full locked foot."""
    PW, PH, kk, head = 240, 360, 5.2, 96; name = f'{sub.slug}--09'
    d, gap, lh = 13 * kk, 5 * kk, 12 * kk; lw = lh * 640 / 380; x0 = (PW - (d + gap + lw)) / 2
    if sub.kind == 'interior': iw = 306.; pl_file, plh = plate(sub, name, k, iw)
    else: iw = 244.; pl_file, plh = plate(sub, name, k, iw, 21)
    b = img(pl_file, clamp_ix(120 - sub.pfull(k) * iw / sub.W, iw, 0, PW), head, iw)
    b += f'<div class="a" style="left:0;top:0;width:{u(PW)};height:{u(head)};background:{MAHAKALA}"></div>'
    b += img(CHAKRA['night'], x0, (head - d) / 2, d) + img(LOCKUP['night'], x0 + d + gap, (head - lh) / 2, lw)
    top = head + plh + 5.2
    b += f'<div class="a" style="left:0;top:{u(head + plh)};width:{u(PW)};height:{u(PH - head - plh)};background:{MAHAKALA}"></div>'
    b += status(PW / 2, top, PW / 2 - 16, 'night', 5.0)
    b += address(16, top + 12.2, 208, 3.9, BHASMA, founders=True) + note(0, top + 41.6, PW)
    return (PW, PH, MAHAKALA, b), dict(plate_h=plh)

# ------------------------------------------------------------------ the pair in the picture-led layouts
# No photograph shows the temple and Nandi together, so these four layouts keep their idea and build the picture from the
# two cut-outs standing before a sky that continues the temple photograph's own sky (its colours, row for row).
def sky_raster(sub, k, name, x0, y0, w, h, origin, s, top_travel=None, horizon=None, ppu=8, **kw):
    """Sky for the page box (x0, y0, w, h) as if the temple photograph stood behind the cut-out.
    origin = page position of the photograph's pixel (0, 0); s = page units per source pixel; top_travel / horizon in page y."""
    im, matte = sub.photo(k)
    for box in sub.clouds: im = prep.repaint_clouds(im, matte, tuple(round(v * k) for v in box))
    rows = ((y0 + (np.arange(round(h * ppu)) + .5) / ppu) - origin[1]) / s * k
    cols = ((x0 + (np.arange(round(w * ppu)) + .5) / ppu) - origin[0]) / s * k
    cv = lambda pair: None if pair is None else tuple((v - y0) * ppu for v in pair)
    rgb = prep.sky_field(im, matte, rows, cols, top_travel=cv(top_travel), horizon=cv(horizon), **kw)
    f = f'{name}-sky.jpg'; prep.save(rgb, PAGES / f, 93); return f

def pair_place(sub, k, bw, axis_x, foot_y):
    t, g = place(sub, k, bw, axis_x, foot_y, 'foot'); c = sub.cut(k)
    origin = (g['x'] - c['tx0'] * g['s'], g['y'] - c['ty0'] * g['s'])
    return t, g, origin, g['y'] + c['far'] * g['s']                 # ..., page y of the highest point of either base

def P06(sub, k):
    """Chandra for the pair: a sky plate on the moon-paper whose horizon dissolves into the paper, where the pair stands."""
    PW, PH, px, win, bw = 240, 360, 16, 208, 196; name = f'{sub.slug}--06'
    l, lg = lockup('day', 120 - bw / 2, bw, matra_top=22); py = lg['bottom'] + 9.5
    t, g, origin, far = pair_place(sub, k, bw, 120, py + 160)
    sky = sky_raster(sub, k, name, px, py, win, far + 2 - py, origin, g['s'], horizon=(far - 22, far - 1.5), ground=prep.CHANDRA, tone=(.75, .94))
    b = l + img(sky, px, py, win, far + 2 - py) + t + colophon(g['foot'] + 8.5, 'day')
    return (PW, PH, CHANDRA, b), dict(geo=g, lockup=lg)

def P07(sub, k):
    """Akasha for the pair: the sky deepens into the sanctum dark where the name sits; the earth below the horizon is the dark itself."""
    PW, PH = 240, 360; name = f'{sub.slug}--07'
    t, g, origin, far = pair_place(sub, k, 226, 120, 297)
    sky = sky_raster(sub, k, name, 0, 0, PW, far + 2, origin, g['s'], top_travel=(78, 190), horizon=(far - 22, far - 1.5))
    b = img(sky, 0, 0, PW, far + 2) + t + img(LOCKUP['night'], 47, 3, 146) + colophon(308.4, 'night')
    return (PW, PH, MAHAKALA, b), dict(geo=g)

def P08(sub, k):
    """Dhvaja for the pair: the name set in the sky above the flag."""
    PW, PH = 240, 360; fs = 208 / 6.0; name = f'{sub.slug}--08'
    t, g, origin, far = pair_place(sub, k, 226, 120, 292)
    sky = sky_raster(sub, k, name, 0, 0, PW, far + 2, origin, g['s'], zenith=(18, 78, 196), tau=.5, horizon=(far - 22, far - 1.5))
    base = g['top'] - 4.
    b = img(sky, 0, 0, PW, far + 2) + kicker(120, base - .70 * fs - 24, 7.4, CHANDRA, CHANDRA)
    b += f'<div class="c deva" style="top:{u(base - .70 * fs)};font-size:{u(fs)};line-height:1;color:{CHANDRA};white-space:nowrap">{NAME_DN}</div>' + t
    b += img(LOCKUP['night'] + '#svgView(viewBox(28,262,584,52))', 64, 304.0, 112, 112 * 52 / 584) + colophon(308.0, 'night', with_status=False)
    return (PW, PH, MAHAKALA, b), dict(geo=g)

def P09(sub, k):
    """Patta for the pair: the letterhead head, a sky that begins hard under it, the pair on the dark earth, the full locked foot."""
    PW, PH, kk, head = 240, 360, 5.2, 96; name = f'{sub.slug}--09'
    d, gap, lh = 13 * kk, 5 * kk, 12 * kk; lw = lh * 640 / 380; x0 = (PW - (d + gap + lw)) / 2
    t, g, origin, far = pair_place(sub, k, 226, 120, 292)
    sky = sky_raster(sub, k, name, 0, head, PW, far + 2 - head, origin, g['s'], horizon=(far - 22, far - 1.5))
    b = img(sky, 0, head, PW, far + 2 - head) + t
    b += img(CHAKRA['night'], x0, (head - d) / 2, d) + img(LOCKUP['night'], x0 + d + gap, (head - lh) / 2, lw)
    top = 305.2
    b += status(PW / 2, top, PW / 2 - 16, 'night', 5.0) + address(16, top + 12.2, 208, 3.9, BHASMA, founders=True) + note(0, top + 41.6, PW)
    return (PW, PH, MAHAKALA, b), dict(geo=g)

PAIR_STYLES = {'06': P06, '07': P07, '08': P08, '09': P09}

STYLES = {'01': ('adhishthana', L01), '02': ('shirshak', L02), '03': ('ek-rekha', L03), '04': ('torana', L04), '05': ('stambha', L05),
          '06': ('chandra', L06), '07': ('akasha', L07), '08': ('dhvaja', L08), '09': ('patta', L09)}

def build(sub, sn, k=2, long_side=2400):
    sname, fn = STYLES[sn]; t = time.time()
    if sub.kind == 'pair' and sn in PAIR_STYLES: fn = PAIR_STYLES[sn]
    (pw, ph, ground, body), meta = fn(sub, k)
    html = page(f'{sub.slug}--{sn}-{sname}', pw, ph, ground, body)
    sub.out.mkdir(parents=True, exist_ok=True)
    pdf = sub.out / f'{sn}-{sname}.pdf'; render.html_to_pdf(html, pdf); rep = render.pdf_report(pdf)
    render.pdf_to_png(pdf, pdf.with_suffix('.png'), long_side)
    gpath = sub.out / 'geometry.json'; G = json.loads(gpath.read_text()) if gpath.exists() else {}
    G[f'{sn}-{sname}'] = dict(page_units=[pw, ph], k=k, meta=meta); gpath.write_text(json.dumps(G, indent=1, default=float))
    print(f'{sub.n}-{sub.slug:18s} {sn}-{sname:12s} {rep["page"]:>18s}  {rep["MB"]:5.2f} MB  fonts {len(rep["fonts"])}  {time.time() - t:4.1f}s', flush=True)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--subjects', default=','.join(SUBJECTS)); ap.add_argument('--styles', default=','.join(STYLES)); ap.add_argument('--k', type=int, default=2)
    a = ap.parse_args()
    for key in a.subjects.split(','):
        for sn in a.styles.split(','):
            build(SUBJECTS[key], sn, a.k)
