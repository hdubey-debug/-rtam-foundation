#!/usr/bin/env python3
"""ṚTAM website build — jinja2 → website/dist/ (self-contained, zero third-party).

    python3 website/src/build.py                # draft: placeholders visible, sample dates flagged
    python3 website/src/build.py --production   # hard-fails if anything placeholder would ship

Draft is for design review. Production refuses to write dist unless every visible
[bracket] is resolved, the donation link is live, and only pañchāṅga-confirmed
dates ship (unconfirmed ones degrade to the wheel's confirmation state, by design).
"""
import json
import re
import shutil
import sys
from pathlib import Path

from fontTools import subset
from jinja2 import Environment, FileSystemLoader, select_autoescape
from PIL import Image

SRC = Path(__file__).resolve().parent
WEB = SRC.parent
ROOT = WEB.parent
DIST = WEB / "dist"
BRAND = ROOT / "brand"

DAY_ICONS = ("rtam-chakra-day.svg", "rtam-anahata-day.svg", "rtam-bindu-day.svg")
GARBHA_ICONS = ("rtam-chakra-garbhagriha.svg", "rtam-anahata-garbhagriha.svg",
                "rtam-bindu-garbhagriha.svg")
PRELOAD_FONTS = ("tiro-400.woff2", "cinzel-500.woff2")

PAGES = [
    dict(tpl="index.html.j2", out="index.html", layer=0, path="",
         title="ऋतम्भरेश्वर मंदिर — rising in Jabalpur · ṚTAM Foundation",
         desc="A Shiva mandir rising in Jabalpur, Madhya Pradesh. The land, the festivals, "
              "the sevā, and the way in — ṚTAM Foundation."),
    dict(tpl="mandir.html.j2", out="mandir/index.html", layer=2, path="mandir/",
         title="मंदिर · the walk — ṚTAM Foundation",
         desc="Pradakṣiṇā around the rising Rtambhareshvara Mandir — east, south, west, "
              "north, and the threshold."),
    dict(tpl="darshana.html.j2", out="darshana/index.html", layer=3, path="darshana/",
         title="दर्शन · गर्भगृह — ṚTAM Foundation",
         desc="The innermost chamber of the Rtambhareshvara Mandir — the approach, "
              "the three readings, the point."),
    dict(tpl="utsava.html.j2", out="utsava/index.html", layer=1, path="utsava/",
         title="उत्सव · the year-wheel — ṚTAM Foundation",
         desc="The mandir's year as a wheel — utsava days at the Rtambhareshvara Mandir, "
              "Jabalpur."),
    dict(tpl="seva.html.j2", out="seva/index.html", layer=1, path="seva/",
         title="सेवा · offer — ṚTAM Foundation",
         desc="Annadāna, śilā-dāna, nitya-pūjā — carry the rising mandir, quietly, "
              "in your name."),
    dict(tpl="system.html.j2", out="system.html", layer=0, path="system.html",
         title="the system — ṚTAM constitution specimen",
         desc="The structural constitution of the ṚTAM site, rendered as a specimen."),
]

FONTS = [
    ("tiro-devanagari-sanskrit/tiro-devanagari-sanskrit-400.ttf", "tiro-400.woff2", "deva"),
    ("cinzel/cinzel-500.ttf", "cinzel-500.woff2", "latin"),
    ("inter/inter-400.ttf", "inter-400.woff2", "latin"),
    ("inter/inter-600.ttf", "inter-600.woff2", "latin"),
]

IMG_WIDTHS = (480, 960)  # + the source width, appended at runtime


def is_deva(ch):
    o = ord(ch)
    return 0x0900 <= o <= 0x097F or 0x1CD0 <= o <= 0x1CFF or 0xA8E0 <= o <= 0xA8FF


def visible_text(html):
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t)  # collapse — placeholders may wrap across lines


def parse_layer_grounds(css):
    grounds = {}
    for m in re.finditer(r'body\[data-layer="(\d)"\][^{]*\{([^}]*)\}', css):
        g = re.search(r"--ground\s*:\s*(#[0-9A-Fa-f]{6})", m.group(2))
        if g:
            for layer in re.findall(r'data-layer="(\d)"', m.group(0)):
                grounds[int(layer)] = g.group(1)
    return grounds


def hero_meta(im):
    widths = [*IMG_WIDTHS, im.width]
    return dict(
        webp=[(f"temple-{w}.webp", w) for w in widths],
        jpg=[(f"temple-{w}.jpg", w) for w in widths],
        fallback="temple-960.jpg", w=im.width, h=im.height,
    )


def write_images(im, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    total = 0
    for w in (*IMG_WIDTHS, im.width):
        r = im if w == im.width else im.resize(
            (w, round(im.height * w / im.width)), Image.LANCZOS)
        jp, wp = outdir / f"temple-{w}.jpg", outdir / f"temple-{w}.webp"
        r.save(jp, quality=80, optimize=True, progressive=True)
        r.save(wp, quality=78, method=6)
        total += jp.stat().st_size + wp.stat().st_size
    return total


def subset_font(src, out, text):
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]     # keep GSUB — Devanagari conjuncts and matras
    opts.name_IDs = ["*"]            # keep the OFL notices inside the font
    opts.notdef_outline = True
    font = subset.load_font(str(src), opts)
    s = subset.Subsetter(opts)
    s.populate(text=text)
    s.subset(font)
    subset.save_font(font, str(out), opts)
    font.close()
    return out.stat().st_size


def main():
    production = "--production" in sys.argv

    data = {p.stem: json.loads(p.read_text()) for p in (SRC / "data").glob("*.json")}
    site = data["site"]
    festivals = data["festivals"]["festivals"]
    if production:
        festivals = [f for f in festivals if not f.get("sample")]
    months = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN",
              "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
    for f in festivals:
        y, m, d = f["date"].split("-")
        f["display"] = f"{int(d)} {months[int(m) - 1]} {y}"

    system_css = (SRC / "static" / "system.css").read_text()
    grounds = parse_layer_grounds(system_css)

    im = Image.open(WEB / "temple.jpeg").convert("RGB")
    hero = hero_meta(im)

    env = Environment(loader=FileSystemLoader(SRC / "templates"),
                      autoescape=select_autoescape(["html", "j2"]))

    rendered = {}
    for p in PAGES:
        root = "../" if "/" in p["out"] else ""
        rendered[p["out"]] = env.get_template(p["tpl"]).render(
            site=site, festivals=festivals, seva=data["seva"],
            title=p["title"], desc=p["desc"], layer=p["layer"], page_path=p["path"],
            root=root, theme=grounds[p["layer"]],
            icons=GARBHA_ICONS if p["layer"] == 3 else DAY_ICONS,
            preload_fonts=PRELOAD_FONTS, hero=hero, production=production,
        )

    # ---- the honesty gate: what would ship? ----
    problems, placeholders = [], 0
    for out, html in rendered.items():
        found = re.findall(r"\[[^\]]{1,200}\]", visible_text(html))
        placeholders += len(found)
        if production:
            problems += [f"{out}: placeholder {b!r}" for b in found]
    if production and not site["donation"]["url"].startswith("https://"):
        problems.append("site.json: donation.url is not a live https link")
    if production and problems:
        print("PRODUCTION BUILD REFUSED — nothing placeholder may ship:")
        for p in problems:
            print(f"  ✗ {p}")
        sys.exit(1)

    # ---- write dist ----
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "assets").mkdir(parents=True)

    for out, html in rendered.items():
        path = DIST / out
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html)

    static_texts = {}
    for f in sorted((SRC / "static").iterdir()):
        static_texts[f.name] = f.read_text()
        (DIST / "assets" / f.name).write_text(static_texts[f.name])

    icons_out = DIST / "assets" / "icons"
    icons_out.mkdir()
    for name in {*DAY_ICONS, *GARBHA_ICONS, "favicon.svg", "favicon-dark.svg"}:
        shutil.copy2(BRAND / "dist" / "outlined" / "icons" / name, icons_out / name)

    # the sanctum's construction drawing — rung-1 context extended to /darshana/
    # for THIS file only (codex §7); the reference photograph never ships.
    geo_out = DIST / "assets" / "geometry"
    geo_out.mkdir()
    shutil.copy2(BRAND / "iconography" / "geometry" / "front-elevation.svg",
                 geo_out / "front-elevation.svg")

    img_bytes = write_images(im, DIST / "assets" / "img")

    # ---- font subsetting: every shipped string, plus shaping/runtime safety sets.
    # Full-face TTFs never ship; verify_site's byte gate enforces it. ----
    corpus = ("".join(rendered.values()) + "".join(static_texts.values())
              + json.dumps(data, ensure_ascii=False))
    ascii_printable = "".join(chr(c) for c in range(0x20, 0x7F))
    deva_chars = {c for c in corpus if is_deva(c)}
    other_chars = {c for c in corpus if ord(c) > 0x7F and not is_deva(c)}
    zw = "\u200c\u200d"  # ZWNJ + ZWJ — Devanagari shaping controls
    tiro_text = ("".join(deva_chars) + "०१२३४५६७८९।॥ॐ" + zw
                 + ascii_printable + "·—–")
    latin_text = ascii_printable + "".join(other_chars) + "·—–‘’“”…₹"

    fonts_out = DIST / "assets" / "fonts"
    fonts_out.mkdir()
    font_bytes = {}
    for rel, out, kind in FONTS:
        text = tiro_text if kind == "deva" else latin_text
        font_bytes[out] = subset_font(BRAND / "fonts" / rel, fonts_out / out, text)
    for fam in ("tiro-devanagari-sanskrit", "cinzel", "inter"):
        shutil.copy2(BRAND / "fonts" / fam / "OFL.txt",
                     fonts_out / f"OFL-{fam.split('-')[0]}.txt")

    (DIST / ".nojekyll").write_text("")
    (DIST / "BUILDINFO.json").write_text(json.dumps(dict(
        mode="production" if production else "draft",
        pages=sorted(rendered), placeholders=placeholders,
        fonts=font_bytes, image_bytes=img_bytes,
    ), indent=2, ensure_ascii=False))

    total_fonts = sum(font_bytes.values())
    print(f"built {len(rendered)} pages → {DIST}")
    print(f"fonts (woff2 subsets): {total_fonts:,} B  "
          + " ".join(f"{k}={v:,}" for k, v in font_bytes.items()))
    print(f"images: {img_bytes:,} B across {len(IMG_WIDTHS) + 1} widths × 2 formats")
    mode = "PRODUCTION" if production else "draft"
    print(f"mode: {mode} · visible placeholders: {placeholders}"
          + ("" if production else "  (draft keeps them visible by design)"))


if __name__ == "__main__":
    main()
