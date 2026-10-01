"""Image preparation for the RTAM poster system (numpy + Pillow only).

The supplied renders are 4:3 and small, so every poster background is composed here:
  * the sky is continued above the picture from the picture's own top-edge colour,
  * the continued sky and the plaza can melt into a brand ground (mahakala or chandra),
  * a sky matte lets grading touch only sky and lets type sit behind the building.
The building's pixels are never repainted.
"""
import numpy as np
from PIL import Image

MAHAKALA = (20, 20, 20)      # #141414  the sanctum dark
CHANDRA = (237, 235, 230)    # #EDEBE6  the moon-paper

# ---------------------------------------------------------------- colour (OKLab)
_M1 = np.array([[.4122214708, .5363325363, .0514459929], [.2119034982, .6806995451, .1073969566], [.0883024619, .2817188376, .6299787005]])
_M2 = np.array([[.2104542553, .7936177850, -.0040720468], [1.9779984951, -2.4285922050, .4505937099], [.0259040371, .7827717662, -.8086757660]])
_M1i, _M2i = np.linalg.inv(_M1), np.linalg.inv(_M2)

def s2l(u):
    u = np.asarray(u, dtype=np.float32) / 255.
    return np.where(u <= .04045, u / 12.92, ((u + .055) / 1.055) ** 2.4)

def l2s(v):
    v = np.clip(v, 0, 1)
    return 255. * np.where(v <= .0031308, 12.92 * v, 1.055 * np.power(v, 1 / 2.4) - .055)

def to_lab(rgb):
    return (np.cbrt(s2l(rgb) @ _M1.T.astype(np.float32)) @ _M2.T.astype(np.float32)).astype(np.float32)

def to_rgb(lab):
    return l2s(((lab @ _M2i.T.astype(np.float32)) ** 3) @ _M1i.T.astype(np.float32)).astype(np.float32)

def smooth(t):
    t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)

def smoother(t):
    t = np.clip(t, 0, 1); return t * t * t * (t * (6 * t - 15) + 10)

def box1d(a, k, axis=0):
    """Box blur along one axis with edge padding (k odd)."""
    k = int(k) | 1; pad = [(0, 0)] * a.ndim; pad[axis] = (k // 2, k // 2)
    p = np.pad(a, pad, mode='edge').astype(np.float64); c = np.cumsum(p, axis=axis)
    z = np.zeros_like(np.take(c, [0], axis=axis)); c = np.concatenate([z, c], axis=axis)
    n = a.shape[axis]
    return ((np.take(c, range(k, k + n), axis=axis) - np.take(c, range(0, n), axis=axis)) / k).astype(np.float32)

# ---------------------------------------------------------------- loading / scaling
def load(path):
    return np.asarray(Image.open(path).convert('RGB'), dtype=np.float32)

def upscale(img, k):
    """Placeholder enlargement (Lanczos). Swap for an AI upscaler for the final print masters."""
    if k == 1: return img
    h, w, _ = img.shape
    return np.asarray(Image.fromarray(np.clip(img + .5, 0, 255).astype(np.uint8)).resize((round(w * k), round(h * k)), Image.LANCZOS), dtype=np.float32)

def save(img, path, quality=93):
    im = Image.fromarray(np.clip(img + .5, 0, 255).astype(np.uint8))
    if str(path).lower().endswith(('.jpg', '.jpeg')): im.save(path, quality=quality, subsampling=0, optimize=True)
    else: im.save(path)
    return path

# ---------------------------------------------------------------- sky matte
def _nb(row):
    p = np.pad(row, 1); return p[1:-1] | p[:-2] | p[2:]

def _spread(seed, allowed):
    """Fill each run of `allowed` that contains a seed pixel."""
    if not seed.any(): return seed
    a = allowed.astype(np.int8); edges = np.diff(np.concatenate([[0], a, [0]]))
    starts, ends = np.where(edges == 1)[0], np.where(edges == -1)[0]
    cs = np.concatenate([[0], np.cumsum(seed)])
    hit = (cs[ends] - cs[starts]) > 0
    out = np.zeros_like(seed)
    for s, e in zip(starts[hit], ends[hit]): out[s:e] = True
    return out

def _flood(cand, from_top=True):
    """8-connected flood through `cand` from the top (or bottom) edge, by alternating sweeps until stable."""
    reach = np.zeros_like(cand); h = cand.shape[0]
    if from_top: reach[0] = cand[0]
    else: reach[-1] = cand[-1]
    for _ in range(96):
        before = int(reach.sum())
        for y in range(1, h):
            reach[y] = _spread((_nb(reach[y - 1]) | reach[y]) & cand[y], cand[y])
        for y in range(h - 2, -1, -1):
            reach[y] = _spread((_nb(reach[y + 1]) | reach[y]) & cand[y], cand[y])
        if int(reach.sum()) == before: break
    return reach

def sky_matte(img):
    """Soft matte: 1 = sky or cloud connected to the top edge, 0 = building, trees, ground.
    Blue sky is blue-dominant; cloud is bright and not warm (the stone is warm, so it never qualifies).
    Specks of non-sky floating inside the sky (cloud highlights) are returned to the sky."""
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    mn = img.min(-1)
    blue = np.clip((b - r - 18) / 34., 0, 1) * (b > g + 4)          # soft, so anti-aliased rims get partial values
    cloud = ((mn > 168) & (b >= r - 12) & (b >= g - 10)).astype(np.float32)
    soft = np.maximum(blue, cloud)
    sky = _flood(soft > .15, from_top=True)
    solid = _flood(~sky, from_top=False)                             # everything standing on the bottom edge
    specks = (~sky) & (~solid)
    out = soft * sky; out[specks] = 1.0
    return out.astype(np.float32)

# ---------------------------------------------------------------- sky continuation
def top_edge_colour(img, rows=8, blur=241):
    """Per-column colour of the sky at the picture's top edge, smoothed along x."""
    c = np.median(img[:rows], axis=0)
    return box1d(c, min(blur, (c.shape[0] // 2) * 2 - 1), axis=0)

def continue_sky(img, height, ground=None, d_keep=0.10, d_full=0.78, zenith=(36, 110, 226), tau=1.1, chroma_hold=.30, grain=.55, seed=7):
    """Rows of sky to stack above `img` (returned top row first).
    The colour starts as the picture's own top-edge colour and deepens toward `zenith` (natural sky).
    With `ground` set, it then travels to that ground: lightness eases across [d_keep, d_full] of the height
    (measured upward from the picture), chroma is held for the first `chroma_hold` of that run and then drains,
    so the path passes through a deep saturated blue rather than a grey. Above d_full the rows are exactly `ground`."""
    w = img.shape[1]; rng = np.random.default_rng(seed)
    lab0 = to_lab(top_edge_colour(img)[None])[0]                    # (w,3)
    labz = to_lab(np.array(zenith, np.float32)[None])[0]
    d = (height - np.arange(height, dtype=np.float32)) / float(img.shape[0])   # distance above the picture, in picture heights
    tn = 1 - np.exp(-d / tau)
    lab = lab0[None] + (labz[None] - lab0[None]) * tn[:, None, None]            # (h,w,3) natural deepening
    flat = np.zeros(height, bool)
    if ground is not None:
        labg = to_lab(np.array(ground, np.float32)[None])[0]
        u = (d * img.shape[0] / height - d_keep) / (d_full - d_keep)              # 0..1 across the travel, in fractions of the extension
        tl = smoother(u)[:, None]
        cf = (1 - smooth((u - chroma_hold) / (1 - chroma_hold)))[:, None]
        L = lab[..., 0] + (labg[0] - lab[..., 0]) * tl
        a = lab[..., 1] * cf + labg[1] * (1 - cf)
        b = lab[..., 2] * cf + labg[2] * (1 - cf)
        lab = np.stack([L, a, b], -1); flat = u >= 1
    rgb = to_rgb(lab)
    if grain: rgb = rgb + rng.normal(0, grain, rgb.shape).astype(np.float32)
    if ground is not None: rgb[flat] = np.array(ground, np.float32)
    return rgb

def melt_rows(img, y0, y1, ground, power=1.0):
    """Melt picture rows y0..y1 into `ground` (y1 fully ground). Works downward (y1>y0) or upward (y1<y0)."""
    out = img.copy(); lo, hi = (y0, y1) if y1 > y0 else (y1, y0)
    ys = np.arange(lo, hi); t = (ys - y0) / float(y1 - y0)
    t = smoother(t) ** power
    lab = to_lab(out[lo:hi]); labg = to_lab(np.array(ground, np.float32)[None])[0]
    out[lo:hi] = to_rgb(lab + (labg - lab) * t[:, None, None])
    return out

def melt_cols(img, x0, x1, ground, power=1.0):
    return np.transpose(melt_rows(np.transpose(img, (1, 0, 2)), x0, x1, ground, power), (1, 0, 2))

def grade_sky(img, matte, y_end, amount, ground):
    """Let the travel toward `ground` begin inside the picture: only matte (sky) pixels, strongest at the top edge, zero at y_end."""
    out = img.copy(); t = (1 - smooth(np.arange(y_end) / float(y_end))) * amount
    lab = to_lab(out[:y_end]); labg = to_lab(np.array(ground, np.float32)[None])[0]
    k = (t[:, None] * matte[:y_end])[..., None]
    tgt = np.stack([lab[..., 0] + (labg[0] - lab[..., 0]) * 1.0, lab[..., 1], lab[..., 2]], -1)   # lightness only: keeps the blue
    out[:y_end] = to_rgb(lab + (tgt - lab) * k)
    return out

def grade_sky_cols(img, matte, x_end, amount, ground, from_left=True):
    """Horizontal twin of grade_sky: the sky deepens toward one side edge (night falling from the side)."""
    t = np.transpose(img, (1, 0, 2)); m = matte.T
    if not from_left: t, m = t[::-1], m[::-1]
    out = grade_sky(np.ascontiguousarray(t), np.ascontiguousarray(m), x_end, amount, ground)
    if not from_left: out = out[::-1]
    return np.ascontiguousarray(np.transpose(out, (1, 0, 2)))

def sky_colour_field(img, matte, k=41):
    """Local sky colour everywhere (normalised blur of sky pixels): used to clean sky tint out of cut-out rims."""
    k = int(k) | 1
    num = box1d(box1d(img * matte[..., None], k, 0), k, 1); den = box1d(box1d(matte, k, 0), k, 1)[..., None]
    return num / np.maximum(den, 1e-3)

def cutout(img, matte, rows):
    """RGBA of the top `rows` of the picture with the sky removed, so type can sit between sky and building.
    Rim pixels are un-mixed from the sky colour to avoid a blue fringe over the type."""
    a = (1 - matte[:rows]).astype(np.float32); rgb = img[:rows].copy()
    sky = sky_colour_field(img[:rows], matte[:rows])
    rim = (a > .02) & (a < .98)
    fg = (rgb - (1 - a)[..., None] * sky) / np.maximum(a, .08)[..., None]
    rgb[rim] = np.clip(fg[rim], 0, 255)
    return np.dstack([rgb, a * 255.])

def repaint_clouds(img, matte, box, pad=9, feather=17, grain=.45, seed=3, tol=4.5):
    """Replace cloud inside box=(x0,y0,x1,y1) with the surrounding clear sky: a smooth quadratic surface fitted
    to the clear-blue pixels in and around the box (two passes: the second pass treats anything that departs
    from the first fit by more than `tol` levels as cloud, which catches faint wisps). Sky only."""
    x0, y0, x1, y1 = box; out = img.copy(); rng = np.random.default_rng(seed)
    h, w, _ = img.shape; X0, Y0, X1, Y1 = max(0, x0 - 200), max(0, y0 - 200), min(w, x1 + 200), min(h, y1 + 200)
    reg = img[Y0:Y1, X0:X1]; m = matte[Y0:Y1, X0:X1]
    r, b = reg[..., 0], reg[..., 2]
    yy, xx = np.mgrid[0:reg.shape[0], 0:reg.shape[1]].astype(np.float32); xn, yn = xx / reg.shape[1], yy / reg.shape[0]
    A = np.stack([np.ones_like(xn), xn, yn, xn * xn, xn * yn, yn * yn], -1)
    clear = (m > .97) & (b - r > 95)
    for _ in range(3):
        coef = [np.linalg.lstsq(A[clear], reg[..., c][clear], rcond=None)[0] for c in range(3)]
        model = np.stack([A @ c for c in coef], -1)
        resid = np.abs(reg - model).max(-1)
        clear = (m > .97) & (resid < tol)
    cm = ((m > .5) & (resid >= tol)).astype(np.float32)
    for _ in range(pad):
        q = np.pad(cm, 1, mode='edge'); cm = np.maximum.reduce([q[1:-1, 1:-1], q[:-2, 1:-1], q[2:, 1:-1], q[1:-1, :-2], q[1:-1, 2:]])
    cm = np.clip(box1d(box1d(cm, feather, 0), feather, 1) * 1.6, 0, 1)
    inside = np.zeros_like(cm); inside[max(0, y0 - Y0):y1 - Y0, max(0, x0 - X0):x1 - X0] = 1
    inside = box1d(box1d(inside, 81, 0), 81, 1)
    k = (cm * inside * (m > .5))[..., None]
    out[Y0:Y1, X0:X1] = reg * (1 - k) + (model + rng.normal(0, grain, model.shape)) * k
    return out

# ---------------------------------------------------------------- building cut-out (front elevation)
# Outline of the temple in the supplied front elevation (1448 x 1086 px), read from 3x crops: the building's
# straight architectural edges below the main roof. Above y=442 the building meets only sky, so the sky matte
# gives the exact silhouette (dome, kalasha, flag, roof tiles).
FRONT_OUTLINE = dict(
    top=442, sky_window=(205, 1228),
    left=[(294, 442), (294, 478), (288, 482), (288, 496), (283, 500), (263, 506), (246, 512), (231, 518), (213, 524), (193, 530), (171, 536), (168, 540),
          (179, 546), (180, 574), (186, 576), (188, 590), (202, 594), (214, 604), (232, 616), (246, 628), (250, 640), (254, 646), (254, 754), (246, 760),
          (244, 776), (240, 778), (240, 790), (232, 792), (232, 814), (130, 814), (130, 826), (135, 828), (135, 850), (120, 853), (117, 864), (120, 876),
          (128, 879), (128, 931), (113, 933), (113, 957)],
    base=[(451, 957), (451, 979), (509, 979), (509, 975), (911, 975), (911, 979), (966, 979), (966, 957)],   # newel bases reach 979, the bottom step 975
    right=[(1316, 957), (1316, 933), (1302, 931), (1302, 879), (1309, 876), (1312, 864), (1309, 853), (1295, 850), (1295, 828), (1298, 826), (1298, 814),
           (1200, 814), (1200, 792), (1192, 790), (1192, 778), (1188, 776), (1186, 760), (1178, 754), (1178, 646), (1181, 640), (1186, 628), (1198, 616),
           (1216, 604), (1228, 594), (1241, 590), (1243, 576), (1250, 574), (1250, 546), (1259, 540), (1255, 536), (1233, 530), (1212, 524), (1200, 518),
           (1183, 512), (1167, 506), (1150, 500), (1144, 496), (1144, 482), (1138, 478), (1138, 442)])

def building_alpha(img, k, outline=FRONT_OUTLINE, shrink=1.0, ss=3):
    """Alpha of the building alone for a picture enlarged k times: sky matte above the main roof, the measured
    outline below it (anti-aliased by supersampling, pulled `shrink` source-px inside the stone so no background
    survives at the edge), with sky and edge-band foliage removed."""
    from PIL import Image, ImageDraw
    h, w, _ = img.shape
    sky = sky_matte(img)
    poly = outline['left'] + outline['base'] + outline['right']
    cx = sum(x for x, _ in poly) / len(poly)
    pts = [((x + (shrink if x < cx else -shrink)) * k * ss, y * k * ss) for x, y in poly]
    m = Image.new('L', (w * ss, h * ss), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    pa = np.asarray(m.resize((w, h), Image.LANCZOS), dtype=np.float32) / 255.
    top = np.zeros((h, w), np.float32); t = int(outline['top'] * k) + 2; x0, x1 = (int(v * k) for v in outline['sky_window'])
    top[:t, x0:x1] = 1 - sky[:t, x0:x1]
    a = np.maximum(pa, top) * (1 - sky)                                # sky is never building
    # Inside a narrow band along the outline the straight segments enclose slivers of background (palm fronds in
    # the bracket hollows, sky seen through leaves). Keep only what is stone-, tile- or granite-coloured there:
    # the stone's hue sits near 37 deg, fronds at 45 deg and beyond; stone is always warmer than it is blue.
    r, g, b = img[..., 0], img[..., 1], img[..., 2]; mx = img.max(-1); mn = img.min(-1)
    hue = np.where((r >= g) & (g >= b), 60. * (g - b) / np.maximum(r - b, 1.), 90.)
    sat = (mx - mn) / np.maximum(mx, 1.)
    leafy = ((g >= r - 6) & (g > b + 10)) | ((hue > 43) & (sat > .20) & (mx < 238))
    cool = b > r - 12
    n = 2 * int(8 * k) + 1
    band = (box1d(box1d(pa, n, 0), n, 1) < .985) & (pa > 0)
    upper = (np.arange(h) < int(818 * k))[:, None]
    drop = band & np.where(upper, leafy | cool, (g >= r - 6) & (g > b + 10))
    d = drop.astype(np.float32); d = box1d(box1d(d, 3, 0), 3, 1)                      # soften the removed edge by a pixel
    a = a * (1 - np.clip(d * 1.5, 0, 1))
    return np.clip(a, 0, 1), sky

def cut_building(img, k, outline=FRONT_OUTLINE, pad=6):
    """RGBA of the building alone, cropped to its bounding box; returns (rgba, (x0, y0) in enlarged px)."""
    a, sky = building_alpha(img, k, outline)
    rgb = img.copy(); field = sky_colour_field(img, sky)
    rim = (a > .02) & (a < .98) & (sky > .02)
    fg = (rgb - sky[..., None] * field) / np.maximum(1 - sky, .08)[..., None]
    rgb[rim] = np.clip(fg[rim], 0, 255)
    ys, xs = np.where(a > .01); y0, y1, x0, x1 = max(0, ys.min() - pad), ys.max() + pad, max(0, xs.min() - pad), xs.max() + pad
    return np.dstack([rgb, a * 255.])[y0:y1, x0:x1], (x0, y0)

def tone_sky(img, matte, chroma=.75, light=.94):
    """Quieten the sky only: less chroma, a touch deeper (for the day register, where the paper should stay the brightest thing)."""
    lab = to_lab(img); k = matte[..., None]
    toned = np.stack([lab[..., 0] * light, lab[..., 1] * chroma, lab[..., 2] * chroma], -1)
    return to_rgb(lab + (toned - lab) * k)

# ---------------------------------------------------------------- a sky that continues a picture's own sky
def sky_profile(img, matte):
    """Median Lab colour of the clear sky for every row of the picture (smoothed), and the last row that still has sky."""
    h, w, _ = img.shape; lab = to_lab(img)
    clear = (matte > .97) & (img[..., 2] - img[..., 0] > 60)
    ok = clear.sum(1) > .10 * w; ys = np.where(ok)[0]
    prof = np.zeros((h, 3), np.float32)
    for y in ys: prof[y] = np.median(lab[y][clear[y]], axis=0)
    last = int(ys.max())
    for c in range(3): prof[:last + 1, c] = np.interp(np.arange(last + 1), ys, prof[ys, c])
    prof[:last + 1] = box1d(prof[:last + 1], max(3, (last // 12) | 1), 0)
    return prof, last

def sky_field(img, matte, rows, cols, zenith=(36, 110, 226), tau=1.1, top_travel=None, horizon=None, ground=MAHAKALA, chroma_hold=.15, tone=None, grain=.55, seed=11):
    """A sky raster that continues the picture's sky beyond the picture. `rows` / `cols` give, for every output row and
    column, the picture coordinate it represents (rows may be negative: above the picture; below the last sky row the
    horizon colour is held). top_travel=(i_full, i_keep): output rows i <= i_full are exactly `ground`, rows >= i_keep are
    untouched, with the lightness-first travel of continue_sky between them. horizon=(i_start, i_end): the sky melts into
    `ground` between these output rows and is `ground` below (the ground plane is the page's own ground)."""
    h, w, _ = img.shape; rng = np.random.default_rng(seed)
    prof, last = sky_profile(img, matte)
    lab0 = to_lab(top_edge_colour(img)[None])[0]; base = lab0.mean(0); labz = to_lab(np.array(zenith, np.float32)[None])[0]
    rows = np.asarray(rows, np.float32); cols = np.clip(np.asarray(cols, np.float32), 0, w - 1)
    P = np.empty((len(rows), 3), np.float32)
    above = rows < 0; tn = 1 - np.exp(-(-rows[above] / h) / tau)
    P[above] = prof[0][None] + (labz - prof[0])[None] * tn[:, None]
    yi = np.clip(rows[~above], 0, last)
    for c in range(3): P[~above, c] = np.interp(yi, np.arange(last + 1), prof[:last + 1, c])
    dx = np.stack([np.interp(cols, np.arange(w), lab0[:, c] - base[c]) for c in range(3)], -1)       # the picture's left-to-right drift
    lab = P[:, None, :] + dx[None, :, :] * .8
    if tone is not None: lab = np.stack([lab[..., 0] * tone[1], lab[..., 1] * tone[0], lab[..., 2] * tone[0]], -1)      # (chroma, lightness): a quieter sky
    n = len(rows); i = np.arange(n, dtype=np.float32); labg = to_lab(np.array(ground, np.float32)[None])[0]; flat = np.zeros(n, bool)
    if top_travel is not None:
        i_full, i_keep = top_travel; u = (i_keep - i) / float(i_keep - i_full)
        tl = smoother(u)[:, None]; cf = (1 - smooth((u - chroma_hold) / (1 - chroma_hold)))[:, None]
        L = lab[..., 0] + (labg[0] - lab[..., 0]) * tl
        lab = np.stack([L, lab[..., 1] * cf + labg[1] * (1 - cf), lab[..., 2] * cf + labg[2] * (1 - cf)], -1); flat |= u >= 1
    if horizon is not None:
        i0, i1 = horizon; t = smoother((i - i0) / float(i1 - i0))[:, None, None]
        lab = lab + (labg - lab) * t; flat |= i >= i1
    rgb = to_rgb(lab)
    if grain: rgb = rgb + rng.normal(0, grain, rgb.shape).astype(np.float32)
    rgb[flat] = np.array(ground, np.float32)
    return rgb
