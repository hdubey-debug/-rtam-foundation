#!/usr/bin/env python3
"""RTAM brand engine — the single source of truth behind generate.py / outline.py.

Model-based (not SVG-parsing): brand.json describes each asset's geometry ONCE
(text runs + shapes, literal coords) plus a list of colour-variant outputs.
`resolve(asset, output)` returns the concrete element list; two backends
serialize it:
  - emit_livetext()  -> <text>/<circle>/<line>  (what ships as the editable source)
  - emit_outlined()  -> <path> only             (renderer-independent dist master)

The outline core (HarfBuzz shape -> fontTools glyf -> SVGPathPen) is the
Phase-0-proven pipeline (see explorations/_research/spikes/shaping_spike.py).
Letter-spacing is added once per HarfBuzz cluster INCLUDING the last, matching
SVG/CSS; text-anchor is resolved to a start-x using that same total advance so
the outlined wordmark lands on the live-text one (the centred-wordmark trap).

No browser here. Bindu/positions in brand.json are baked literals (calibrated
once); see comments in brand.json for the derivation rules.
"""
from __future__ import annotations
import json
from pathlib import Path

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

TOOLS = Path(__file__).resolve().parent
BRAND = TOOLS.parent
SPEC = BRAND / "spec" / "brand.json"
FONTS = BRAND / "fonts"

_TTF_CACHE: dict[str, TTFont] = {}
_HBFONT_CACHE: dict[str, tuple] = {}


def load_brand(path: Path = SPEC) -> dict:
    return json.loads(path.read_text())


def import_url(brand: dict, font_keys) -> str:
    """Build a Google-Fonts css2 @import URL for one or more font keys (lockups
    combine families). Each font contributes its `familyQuery`."""
    if isinstance(font_keys, str):
        font_keys = [font_keys]
    qs = "&".join(f"family={brand['fonts'][k]['familyQuery']}" for k in font_keys)
    return f"https://fonts.googleapis.com/css2?{qs}&display=swap"


# ---- font resolution -------------------------------------------------------
def ttf_path(brand: dict, font_key: str, weight: int) -> Path:
    f = brand["fonts"][font_key]
    fname = f["files"][str(weight)] if "files" in f else f["file"]
    return FONTS / fname


def _ttfont(p: Path) -> TTFont:
    k = str(p)
    if k not in _TTF_CACHE:
        _TTF_CACHE[k] = TTFont(p)
    return _TTF_CACHE[k]


def _hb(p: Path):
    k = str(p)
    if k not in _HBFONT_CACHE:
        blob = hb.Blob.from_file_path(str(p))
        face = hb.Face(blob)
        font = hb.Font(face)
        _HBFONT_CACHE[k] = (font, face.upem)
    return _HBFONT_CACHE[k]


# ---- shaping + outlining (Phase-0 core) ------------------------------------
def _shape(ttf: Path, text: str):
    font, upem = _hb(ttf)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf)
    return buf.glyph_infos, buf.glyph_positions, upem


def total_advance(ttf: Path, text: str, fs: float, letter_spacing: float = 0.0) -> float:
    """Advance width as the browser lays it out: sum of glyph advances + one
    letter_spacing per cluster INCLUDING the last (SVG/CSS semantics)."""
    infos, positions, upem = _shape(ttf, text)
    s = fs / upem
    adv = 0.0
    for i, (info, pos) in enumerate(zip(infos, positions)):
        adv += pos.x_advance * s
        last = (i + 1 == len(infos) or infos[i + 1].cluster != info.cluster)
        if letter_spacing and last:
            adv += letter_spacing
    return adv


def outline_paths(ttf: Path, text: str, fs: float, start_x: float, y: float,
                  letter_spacing: float = 0.0):
    """Return list of path-d strings, positioned, baseline at y, left at start_x."""
    infos, positions, upem = _shape(ttf, text)
    tt = _ttfont(ttf)
    gs = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    s = fs / upem
    cx = start_x
    ds = []
    for i, (info, pos) in enumerate(zip(infos, positions)):
        gname = order[info.codepoint]
        spen = SVGPathPen(gs)
        tpen = TransformPen(spen, (s, 0, 0, -s, cx + pos.x_offset * s, y - pos.y_offset * s))
        gs[gname].draw(tpen)
        d = spen.getCommands()
        if d:
            ds.append(d)
        cx += pos.x_advance * s
        last = (i + 1 == len(infos) or infos[i + 1].cluster != info.cluster)
        if letter_spacing and last:
            cx += letter_spacing
    return ds


def start_x_for(brand: dict, run: dict) -> float:
    """Resolve text-anchor to the glyph-run start-x (left edge)."""
    anchor = run.get("anchor", "start")
    x = run["x"]
    if anchor == "start":
        return x
    ttf = ttf_path(brand, run["font"], run.get("weight", 400))
    adv = total_advance(ttf, run["text"], run["fs"], run.get("letterSpacing", 0.0))
    return x - adv / 2 if anchor == "middle" else x - adv


# ---- variant resolution ----------------------------------------------------
def color(brand: dict, token_or_hex: str) -> str:
    return brand["tokens"].get(token_or_hex, token_or_hex)


def resolve(brand: dict, asset: dict, output: dict) -> dict:
    """Concrete render model for one colour variant: viewBox, optional ground,
    and elements (runs + shapes) with resolved hex colours."""
    cols = output["colors"]
    drop = set(output.get("drop", []))
    runs = []
    for r in asset.get("runs", []):
        if r["role"] in drop:
            continue
        runs.append({**r, "fill": color(brand, cols[r["role"]])})
    shapes = []
    for sh in asset.get("shapes", []):
        if sh["role"] in drop:
            continue
        c = color(brand, cols[sh["role"]])
        shapes.append({**sh, "color": c})
    ground = color(brand, output["ground"]) if output.get("ground") else None
    return {"viewBox": asset["viewBox"], "ground": ground, "runs": runs, "shapes": shapes}


# ---- backends --------------------------------------------------------------
def _shape_el_livetext(sh: dict) -> str:
    if sh["type"] == "circle":
        if sh.get("fillKind") == "stroke":
            return (f'<circle cx="{sh["cx"]}" cy="{sh["cy"]}" r="{sh["r"]}" fill="none" '
                    f'stroke="{sh["color"]}" stroke-width="{sh["strokeWidth"]}"/>')
        return f'<circle cx="{sh["cx"]}" cy="{sh["cy"]}" r="{sh["r"]}" fill="{sh["color"]}"/>'
    if sh["type"] == "line":
        return (f'<line x1="{sh["x1"]}" y1="{sh["y1"]}" x2="{sh["x2"]}" y2="{sh["y2"]}" '
                f'stroke="{sh["color"]}" stroke-width="{sh["strokeWidth"]}"/>')
    raise ValueError(sh["type"])


def _text_el(brand: dict, r: dict) -> str:
    fam = brand["fonts"][r["font"]]["family"]
    attrs = [f'x="{r["x"]}"', f'y="{r["y"]}"', f'font-family="{fam}"']
    if r.get("weight"):
        attrs.append(f'font-weight="{r["weight"]}"')
    attrs.append(f'font-size="{r["fs"]}"')
    if r.get("letterSpacing"):
        attrs.append(f'letter-spacing="{r["letterSpacing"]}"')
    if r.get("anchor", "start") != "start":
        attrs.append(f'text-anchor="{r["anchor"]}"')
    attrs.append(f'fill="{r["fill"]}"')
    return f'<text {" ".join(attrs)}>{r["text"]}</text>'


def _svg_open(brand: dict, asset: dict, output: dict) -> str:
    w, h = asset["viewBox"]
    label = output.get("label", asset.get("label", ""))
    title = output.get("title", "")
    desc = output.get("desc", "")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="{label}">\n  <title>{title}</title>\n  <desc>{desc}</desc>\n')


def emit_livetext(brand: dict, asset: dict, output: dict) -> str:
    m = resolve(brand, asset, output)
    imp = import_url(brand, asset["fontImport"]).replace("&", "&amp;")
    parts = [_svg_open(brand, asset, output)]
    parts.append(f'  <defs>\n    <style type="text/css">@import url(\'{imp}\');</style>\n  </defs>\n')
    if m["ground"]:
        w, h = m["viewBox"]
        parts.append(f'  <rect x="0" y="0" width="{w}" height="{h}" fill="{m["ground"]}"/>\n')
    for r in m["runs"]:
        parts.append("  " + _text_el(brand, r) + "\n")
    for sh in m["shapes"]:
        parts.append("  " + _shape_el_livetext(sh) + "\n")
    parts.append("</svg>\n")
    return "".join(parts)


def _shape_el_outlined(sh: dict) -> str:
    # circles/lines are already renderer-independent primitives -> keep as-is
    return _shape_el_livetext(sh)


def emit_outlined(brand: dict, asset: dict, output: dict) -> str:
    m = resolve(brand, asset, output)
    parts = [_svg_open(brand, asset, output)]
    if m["ground"]:
        w, h = m["viewBox"]
        parts.append(f'  <rect x="0" y="0" width="{w}" height="{h}" fill="{m["ground"]}"/>\n')
    for r in m["runs"]:
        ttf = ttf_path(brand, r["font"], r.get("weight", 400))
        sx = start_x_for(brand, r)
        ds = outline_paths(ttf, r["text"], r["fs"], sx, r["y"], r.get("letterSpacing", 0.0))
        for d in ds:
            parts.append(f'  <path d="{d}" fill="{r["fill"]}"/>\n')
    for sh in m["shapes"]:
        parts.append("  " + _shape_el_outlined(sh) + "\n")
    parts.append("</svg>\n")
    return "".join(parts)


def all_outputs(brand: dict):
    """Yield (asset, output) for every shipping file."""
    for asset in brand["assets"]:
        for output in asset["outputs"]:
            yield asset, output
