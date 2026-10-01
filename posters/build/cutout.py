"""Subject cut-outs: Apple Vision's on-device foreground matte, refined against the picture.

Vision gives a soft matte with the right shape but a blurred, slightly wavy edge. Here it is
  1. snapped to the picture's own edges with a colour guided filter,
  2. tightened to a one-to-two pixel edge,
  3. replaced by the exact sky matte wherever the subject meets sky,
  4. cleaned of background colour along the rim.
Nothing inside the subject is repainted."""
import subprocess, hashlib
from pathlib import Path
import numpy as np
from PIL import Image
import prep

HERE = Path(__file__).resolve().parent
CACHE = HERE / 'cache'

def vision_mask(path):
    """Soft foreground matte (0..1 float32) from Vision, cached next to the build scripts."""
    path = Path(path); CACHE.mkdir(exist_ok=True)
    tag = hashlib.sha1(path.read_bytes()).hexdigest()[:10]; out = CACHE / f'{path.stem}-{tag}'
    if not Path(str(out) + '-all.png').exists():
        r = subprocess.run(['swift', str(HERE / 'subject_mask.swift'), str(path), str(out)], capture_output=True, text=True)
        if not Path(str(out) + '-all.png').exists(): raise RuntimeError('Vision mask failed: ' + r.stdout[-400:] + r.stderr[-400:])
    return np.asarray(Image.open(str(out) + '-all.png').convert('L'), dtype=np.float32) / 255.

def _box(a, r):
    k = 2 * r + 1; return prep.box1d(prep.box1d(a, k, 0), k, 1)

def guided_filter(I, p, r=8, eps=1e-3):
    """Colour guided filter (He, Sun, Tang): p follows the edges of I. I in 0..1 (h,w,3), p in 0..1 (h,w)."""
    mI = [_box(I[..., c], r) for c in range(3)]; mp = _box(p, r)
    cov = [_box(I[..., c] * p, r) - mI[c] * mp for c in range(3)]
    S = {}
    for i in range(3):
        for j in range(i, 3):
            S[(i, j)] = _box(I[..., i] * I[..., j], r) - mI[i] * mI[j] + (eps if i == j else 0.)
    a00, a01, a02, a11, a12, a22 = S[(0, 0)], S[(0, 1)], S[(0, 2)], S[(1, 1)], S[(1, 2)], S[(2, 2)]
    c00 = a11 * a22 - a12 * a12; c01 = a02 * a12 - a01 * a22; c02 = a01 * a12 - a02 * a11
    c11 = a00 * a22 - a02 * a02; c12 = a01 * a02 - a00 * a12; c22 = a00 * a11 - a01 * a01
    det = a00 * c00 + a01 * c01 + a02 * c02; det = np.where(np.abs(det) < 1e-12, 1e-12, det)
    A = [(c00 * cov[0] + c01 * cov[1] + c02 * cov[2]) / det, (c01 * cov[0] + c11 * cov[1] + c12 * cov[2]) / det, (c02 * cov[0] + c12 * cov[1] + c22 * cov[2]) / det]
    b = mp - A[0] * mI[0] - A[1] * mI[1] - A[2] * mI[2]
    return np.clip(_box(A[0], r) * I[..., 0] + _box(A[1], r) * I[..., 1] + _box(A[2], r) * I[..., 2] + _box(b, r), 0, 1)

def refine(img, a0, sky=None, r=10, eps=6e-4, lo=.38, hi=.62):
    """Refined alpha at the resolution of img (0..255 float). a0: Vision matte resized to img. sky: sky matte or None."""
    I = img / 255.
    q = guided_filter(I, a0, r, eps)
    a = prep.smooth((q - lo) / (hi - lo))
    a = a * (a0 > .04)                                   # the filter may leak into far background of similar colour: Vision vetoes it
    if sky is not None:
        near = _box((sky > .5).astype(np.float32), 5) > .02
        gen = prep.smooth((np.maximum(q, a0) - .08) / .22)   # generous inside the subject near sky: the sky matte owns that edge
        a = np.where(near, np.minimum(gen, 1 - sky), a)
        a = a * (1 - (sky > .97))
    return np.clip(a, 0, 1).astype(np.float32)

def decontaminate(img, a, sky=None):
    """Rim pixels take the subject's own colour: sky is un-mixed exactly; elsewhere colour is pulled from just inside the edge."""
    rgb = img.copy(); solid = (a > .97).astype(np.float32)
    num = np.stack([_box(img[..., c] * solid, 3) for c in range(3)], -1); den = _box(solid, 3)[..., None]
    inner = num / np.maximum(den, 1e-4)
    rim = (a > .01) & (a < .97) & (den[..., 0] > .04)
    t = np.clip((.97 - a) / .5, 0, 1)[..., None]            # the more transparent, the more it is replaced
    mix = img * (1 - t) + inner * t
    rgb[rim] = mix[rim]
    if sky is not None:
        field = prep.sky_colour_field(img, sky)
        srim = (sky > .02) & (sky < .98) & (a > .01)
        fg = (img - sky[..., None] * field) / np.maximum(1 - sky, .08)[..., None]
        rgb[srim] = np.clip(fg[srim], 0, 255)
    return rgb

def poly_mask(shape, pts, k=1, ss=3):
    """Anti-aliased polygon mask (0..1) for points given in source pixels, on an image enlarged k times."""
    from PIL import ImageDraw
    h, w = shape; m = Image.new('L', (w * ss, h * ss), 0)
    ImageDraw.Draw(m).polygon([(x * k * ss, y * k * ss) for x, y in pts], fill=255)
    return np.asarray(m.resize((w, h), Image.LANCZOS), dtype=np.float32) / 255.

def cut(path, k=2, exterior=True, fix=None, seed=None, post=None, paving=False, **kw):
    """RGBA cut-out of the picture's subject, enlarged k times. fix(img, a, sky, k) may edit alpha. Returns (rgba, alpha_full, sky)."""
    src = prep.load(path); img = prep.upscale(src, k)
    a0 = vision_mask(path); h, w = img.shape[:2]
    a0 = np.asarray(Image.fromarray((a0 * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), dtype=np.float32) / 255.
    sky = prep.sky_matte(img) if exterior else None
    a = refine(img, a0, sky, r=5 * k, **kw)
    if exterior: a = drop_edge_greens(img, a, k, paving=paving)
    a = clean_edges(a, k, sky)
    if fix is not None: a = fix(img, a, sky, k)
    if seed is not None: a = keep_connected(a, (int(seed[0] * k), int(seed[1] * k)))
    rgb = decontaminate(img, a, sky)
    if post is not None: rgb = post(rgb, a, k)
    return np.dstack([rgb, a * 255.]), a, sky

def keep_connected(a, seed, thr=.3):
    """Keep only the part of the matte connected to `seed` (x, y): removes stray specks around the subject."""
    cand = a > thr; reach = np.zeros_like(cand); x, y = seed; reach[y - 2:y + 3, x - 2:x + 3] = cand[y - 2:y + 3, x - 2:x + 3]
    h = cand.shape[0]
    for _ in range(200):
        before = int(reach.sum())
        for yy in range(1, h): reach[yy] = prep._spread((prep._nb(reach[yy - 1]) | reach[yy]) & cand[yy], cand[yy])
        for yy in range(h - 2, -1, -1): reach[yy] = prep._spread((prep._nb(reach[yy + 1]) | reach[yy]) & cand[yy], cand[yy])
        if int(reach.sum()) == before: break
    grown = _box(reach.astype(np.float32), 2) > 0          # keep the soft rim around the kept part
    return a * grown

def clean_edges(a, k, sky=None, r=1.4):
    """Feather-and-choke: averages out speckle and ragged pixels along the matte's edge (where subject and background
    are close in colour) and returns a one-to-two pixel edge. Edges against the sky are left alone: they are exact."""
    n = max(1, int(round(r * k)))
    b = _box(_box(a, n), n)
    out = prep.smooth((b - .36) / .28)
    if sky is not None:
        near = _box((sky > .5).astype(np.float32), 4 * k) > .01
        out = np.where(near, a, out)
    return out.astype(np.float32)

def drop_edge_greens(img, a, k, r=6, passes=3, paving=False):
    """Background that clings to the outline. Within a few pixels of the matte's edge: foliage (green-dominant pixels)
    anywhere, and plaza paving (warm pink) along the lowest part, where the subject itself is neutral grey granite.
    Repeated so that a clinging clump is eaten from its outside in; plants inside the subject are never near the edge."""
    R, G, B = img[..., 0], img[..., 1], img[..., 2]
    veg = (G >= R - 6) & (G > B + 10)
    ys = np.where((a > .5).any(1))[0]; y0, y1 = ys.min(), ys.max()
    low = (np.arange(a.shape[0]) > y1 - .14 * (y1 - y0))[:, None]
    lum = .3 * R + .59 * G + .11 * B
    bad = (veg | (low & (R - B > 38) & (R > G + 12) & (lum > 150))) if paving else veg      # paving is bright pink; never use it where the plinth itself is warm (Nandi)
    bad = bad.astype(np.float32)
    for _ in range(passes):
        near = _box((a > .5).astype(np.float32), int(r * k)); band = (near > .02) & (near < .98)
        a = a * (1 - np.clip(_box(bad * band, 1) * 1.6, 0, 1))
    return a

# ---------------------------------------------------------------- per-picture corrections (source pixels, measured on 8x crops)
# Nandi pavilion: Vision keeps the boundary wall seen between the pillars. These polygons are the wall areas,
# bounded by the pillar-base profiles, the statue and its pedestal, and the pavilion floor.
NANDI_WALL = [
    # left opening, between the front-left and rear-left pillar bases, down to the newel ball
    [(414.5, 640), (414.5, 645), (417, 646), (417, 650), (424, 651), (424, 658), (426, 662), (428, 668), (428.5, 680), (427, 688), (424, 693),
     (422, 697), (422, 703), (425, 708), (430, 712), (437, 713), (437, 721.5), (442.5, 721.5), (446.7, 717.5), (452.5, 716), (458.3, 717.5),
     (462.5, 721.5), (466, 721.5), (466, 714), (471.5, 713), (471.5, 708), (478, 707), (484, 705), (484, 697), (483, 693), (477, 690),
     (473.5, 684), (473.5, 676), (475, 668), (479, 664), (481, 658), (488, 657), (488, 650), (492.5, 649), (492.5, 640)],
    # centre, left of the statue
    [(574.5, 630), (574.5, 653), (578, 655), (578, 664), (577.5, 668), (580, 672), (584, 675), (589, 679), (591.5, 683), (590, 686.5), (584, 688),
     (582, 690.5), (581, 694), (581, 704), (584, 708), (590, 714), (596, 720), (598, 721.5), (604, 721.5), (604.5, 720.5), (619.5, 720), (620, 704),
     (614.5, 702), (614.5, 690.2), (641, 690.2), (641, 681), (646, 677), (651, 673), (648.5, 668), (649, 662), (652.5, 658), (652.5, 653),
     (648, 650), (646, 646), (646, 630)],
    # centre, right of the statue
    [(889, 632), (889, 648), (886.5, 654), (886.5, 666), (883, 668.5), (882.5, 671), (886, 673), (886, 688.8), (921.5, 689.2), (922, 703), (924, 705),
     (925, 720), (926, 722), (926, 729.5), (985.5, 729.5), (985.5, 722.5), (989.5, 721.5), (990, 716.5), (999, 714), (1002.5, 709), (1004.5, 702),
     (1004.5, 694), (1001, 690.5), (996.5, 686), (995.5, 680), (995.5, 672), (998, 666), (1002, 663), (1004, 660), (1004, 655.5), (1003, 650), (1003, 632)],
    # beyond the rear-right pillar
    [(1204.5, 632), (1204.5, 649), (1209, 651), (1210.5, 656), (1211, 664), (1216, 668), (1221, 672), (1224, 677), (1224.5, 683), (1221, 688),
     (1215.5, 690.5), (1215, 695), (1215, 704), (1219, 708), (1223, 712), (1225.5, 716), (1229.5, 718), (1229.5, 731.5), (1320, 731.5), (1320, 632)],
]
NANDI_SLIVER = (1112, 424, 1128, 646)
NANDI_NEUTRAL_ONLY = [(603, 700, 624, 727), (906, 686, 934, 732)]       # the strip of sky and trees between the two right-hand pillars: decided by colour

def fix_nandi(img, a, sky, k):
    h, w = a.shape
    for poly in NANDI_WALL: a = a * (1 - poly_mask((h, w), poly, k))
    x0, y0, x1, y1 = [int(v * k) for v in NANDI_SLIVER]; reg = img[y0:y1, x0:x1]
    lum = .3 * reg[..., 0] + .59 * reg[..., 1] + .11 * reg[..., 2]
    stone = ((reg[..., 0] - reg[..., 2] > 28) & (lum > 62) & (reg[..., 0] > reg[..., 1] + 14)).astype(np.float32)
    a[y0:y1, x0:x1] *= np.clip(_box(stone, 1) * 1.5 - .25, 0, 1)
    a = a * (1 - poly_mask((h, w), [(1117.5, 428), (1123.5, 428), (1123.5, 644), (1117.5, 644)], k))      # the gap itself, whatever its colour
    for bx in NANDI_NEUTRAL_ONLY:                         # beside the black pedestal only neutral stone and floor belong
        x0, y0, x1, y1 = [int(v * k) for v in bx]; reg = img[y0:y1, x0:x1]
        lum = .3 * reg[..., 0] + .59 * reg[..., 1] + .11 * reg[..., 2]
        warm = (reg[..., 0] - reg[..., 2] > 40) & (lum > 70); green = (reg[..., 1] >= reg[..., 0] - 6) & (reg[..., 1] > reg[..., 2] + 10)
        a[y0:y1, x0:x1] *= 1 - np.clip(_box((warm | green).astype(np.float32), 1) * 1.6, 0, 1)
    return a

def lift_dark_stone(rgb, a, k, box=(596, 420, 934, 742), gamma=.62, lum_max=84):
    """The Nandi is black stone; on a black ground he disappears. This is an exposure lift of the dark, neutral
    pixels inside `box` (statue and pedestal) only: the same stone, shown as if exposed for it."""
    x0, y0, x1, y1 = [int(v * k) for v in box]; reg = rgb[y0:y1, x0:x1]
    lum = .3 * reg[..., 0] + .59 * reg[..., 1] + .11 * reg[..., 2]; mx = reg.max(-1); mn = reg.min(-1)
    dark = ((lum < lum_max) & (mx - mn < 42)).astype(np.float32)
    m = np.clip(_box(_box(dark, 2 * k), 2 * k) * 1.4 - .2, 0, 1)[..., None]
    lifted = 255. * np.power(np.clip(reg, 0, 255) / 255., gamma)
    out = rgb.copy(); out[y0:y1, x0:x1] = reg * (1 - m) + lifted * m
    return out

# Shivalinga: the round pedestal's silhouette, measured from luminance profiles (axis x = 767.3). The drum's sides are
# vertical; its base is the lower half of an ellipse; the basin under the spout stands in front of it.
LINGA_AXIS = 767.3
def _linga_polys():
    cx, cy, ea, eb = LINGA_AXIS, 772., 346., 41.
    arc = [(cx + ea * np.cos(t), cy + eb * np.sin(t)) for t in np.linspace(0, np.pi, 72)]
    drum = [(1109.5, 640), (1109.5, 684), (1105.5, 689), (1105.5, 753), (1113.3, 757)] + arc + [(421.3, 757), (429.5, 753), (429.5, 689), (424.5, 684), (424.5, 640)]
    basin = [(699, 790), (699, 822), (697, 822), (695.2, 827), (695.2, 839.3), (839.2, 839.3), (839.2, 827), (837.5, 822), (834.5, 822), (834.5, 790)]
    return drum, basin

def fix_linga(img, a, sky, k):
    h, w = a.shape; drum, basin = _linga_polys()
    m = np.maximum(poly_mask((h, w), drum, k), poly_mask((h, w), basin, k))
    y = (np.arange(h, dtype=np.float32) / k)[:, None]
    clip = np.where(y >= 662, np.minimum(a, m), a)                 # nothing outside the drum from its rim down
    t = prep.smooth((y - 690) / 10.)                               # from the drum's body down, the silhouette is the geometry itself
    a = clip * (1 - t) + m * t
    a = a * (1 - poly_mask((h, w), [(761, 250), (781, 250), (781, 281.3), (761, 281.3)], k))    # the falling water above the dome
    return a

def bbox(a, thr=.5):
    ys, xs = np.where(a > thr); return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1

def bleed(rgba, radii=(2, 4, 8, 16)):
    """Spread the subject's edge colours outward under the transparent area, so a renderer that filters colour and
    alpha separately (PDF soft masks) cannot pull background colour into the edge."""
    rgb = rgba[..., :3].copy(); known = (rgba[..., 3] > 127).astype(np.float32)
    for r in radii:
        den = _box(known, r); fill = (known < .5) & (den > 1e-3)
        if not fill.any(): continue
        num = np.stack([_box(rgb[..., ch] * known, r) for ch in range(3)], -1)
        rgb[fill] = (num / np.maximum(den, 1e-6)[..., None])[fill]; known = np.maximum(known, fill.astype(np.float32))
    rgb[known < .5] = 20.
    return np.dstack([rgb, rgba[..., 3]])

def resize_rgba(rgba, size):
    """Resize with premultiplied alpha (no colour from transparent pixels leaks into the edge). size = (w, h)."""
    from PIL import Image as _I
    a = rgba[..., 3:4] / 255.; pm = np.dstack([rgba[..., :3] * a, rgba[..., 3]])
    out = np.stack([np.asarray(_I.fromarray(np.ascontiguousarray(pm[..., ch])).resize(size, _I.LANCZOS), dtype=np.float32) for ch in range(4)], -1)
    al = np.clip(out[..., 3:4] / 255., 0, 1)
    return np.dstack([np.clip(out[..., :3] / np.maximum(al, 1e-3), 0, 255), al[..., 0] * 255.])

# ---------------------------------------------------------------- the subjects' cut-outs
def make(key, k=2):
    """RGBA cut-out for a subject key, with its alpha: ('right' | 'left' | 'linga' | 'nandi')."""
    src = HERE.parent / 'source'
    if key == 'right': return cut(src / '02-exterior-tower-right.png', k, seed=(700, 600), paving=True)
    if key == 'left': return cut(src / '03-exterior-tower-left.png', k, seed=(700, 600), paving=True)
    if key == 'linga': return cut(src / '04-interior-shivalinga.png', k, exterior=False, fix=fix_linga, seed=(768, 500))
    if key == 'nandi': return cut(src / '05-nandi-pavilion.from-webp.png', k, seed=(740, 300), fix=fix_nandi,
                                  post=lambda rgb, a, kk: lift_dark_stone(rgb, a, kk, gamma=.72))
    raise KeyError(key)

def geometry(a, k):
    """Subject geometry in source pixels from the alpha: bounding box, top, foot, and the span of the base (lowest 28 %)."""
    x0, y0, x1, y1 = bbox(a); h = y1 - y0
    low = a[int(y1 - .28 * h):y1] > .5; xs = np.where(low.any(0))[0]
    return dict(x0=x0 / k, y0=y0 / k, x1=x1 / k, y1=y1 / k, top=y0 / k, foot=y1 / k, pl=xs.min() / k, pr=(xs.max() + 1) / k)
