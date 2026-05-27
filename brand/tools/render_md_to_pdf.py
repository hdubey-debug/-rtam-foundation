#!/usr/bin/env python3
"""Render a Markdown file to a styled PDF using python-markdown + Playwright Chromium.

Usage:
    python3 render_md_to_pdf.py <input.md> <output.pdf>

The markdown is rendered with the `tables`, `fenced_code`, and `attr_list`
extensions, then embedded in a Cinzel/Inter-styled HTML template (matching
the brand palette), then printed to Letter-size PDF.
"""

import sys
import tempfile
from pathlib import Path

import markdown
from playwright.sync_api import sync_playwright


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Tiro+Devanagari+Sanskrit&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
  <style>
    :root {{
      --rtam-gold: #C8A15A;
      --rtam-ivory: #F7F3E9;
      --rtam-charcoal: #1A1A1A;
      --rtam-sandstone: #E6DED1;
      --rtam-indigo: #1C1A3D;
      --rtam-bronze: #9B6A2F;
      --rtam-stone: #B8B1A4;
    }}
    @page {{ size: Letter; margin: 22mm 20mm; }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, system-ui, sans-serif;
      font-size: 11pt;
      line-height: 1.65;
      color: var(--rtam-charcoal);
      background: var(--rtam-ivory);
    }}
    h1 {{
      font-family: Cinzel, serif;
      font-weight: 500;
      font-size: 28pt;
      letter-spacing: 0.06em;
      margin: 0 0 6pt;
      padding-bottom: 8pt;
      border-bottom: 1px solid var(--rtam-gold);
    }}
    h1 + p em {{
      font-family: 'Tiro Devanagari Sanskrit', serif;
      font-style: normal;
      font-size: 14pt;
      color: var(--rtam-charcoal);
    }}
    h2 {{
      font-family: Cinzel, serif;
      font-weight: 500;
      font-size: 16pt;
      letter-spacing: 0.05em;
      margin: 28pt 0 8pt;
      color: var(--rtam-charcoal);
      page-break-after: avoid;
    }}
    h3 {{
      font-family: Cinzel, serif;
      font-weight: 500;
      font-size: 12pt;
      letter-spacing: 0.05em;
      margin: 18pt 0 6pt;
      color: var(--rtam-charcoal);
      page-break-after: avoid;
    }}
    p {{ margin: 0 0 8pt; }}
    strong {{ font-weight: 600; }}
    em {{ font-style: italic; color: var(--rtam-bronze); }}
    a {{ color: var(--rtam-bronze); text-decoration: none; }}
    code {{
      font-family: 'JetBrains Mono', ui-monospace, Menlo, Consolas, monospace;
      font-size: 9.5pt;
      background: var(--rtam-sandstone);
      padding: 1pt 4pt;
      border-radius: 2pt;
      color: var(--rtam-charcoal);
    }}
    pre {{
      background: var(--rtam-sandstone);
      padding: 10pt 14pt;
      border-radius: 3pt;
      overflow-x: auto;
      font-size: 9pt;
      line-height: 1.55;
      page-break-inside: avoid;
    }}
    pre code {{ background: transparent; padding: 0; }}
    ul, ol {{ margin: 0 0 10pt; padding-left: 18pt; }}
    li {{ margin: 0 0 4pt; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 8pt 0 14pt;
      font-size: 10pt;
      page-break-inside: avoid;
    }}
    th, td {{
      text-align: left;
      padding: 6pt 10pt;
      border-bottom: 0.5pt solid var(--rtam-sandstone);
      vertical-align: top;
    }}
    th {{
      font-family: Inter, sans-serif;
      font-weight: 600;
      font-size: 9pt;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--rtam-stone);
      border-bottom: 1px solid var(--rtam-gold);
    }}
    hr {{
      border: 0;
      border-top: 0.5pt solid var(--rtam-sandstone);
      margin: 18pt 0;
    }}
    blockquote {{
      margin: 8pt 0;
      padding: 6pt 14pt;
      border-left: 2px solid var(--rtam-gold);
      color: var(--rtam-stone);
      font-style: italic;
    }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""


def render(md_path: Path, pdf_path: Path) -> None:
    md_text = md_path.read_text(encoding="utf-8")
    body_html = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "attr_list", "sane_lists"],
        output_format="html5",
    )
    title = md_path.stem.replace("-", " ").title()
    html_doc = TEMPLATE.format(title=title, body=body_html)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(html_doc)
        tmp_path = Path(tmp.name)
    try:
        url = tmp_path.resolve().as_uri()
        with sync_playwright() as p:
            browser = p.chromium.launch()
            ctx = browser.new_context(viewport={"width": 1100, "height": 1400})
            page = ctx.new_page()
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(500)
            page.pdf(
                path=str(pdf_path),
                format="Letter",
                margin={"top": "22mm", "bottom": "22mm", "left": "20mm", "right": "20mm"},
                print_background=True,
            )
            browser.close()
    finally:
        tmp_path.unlink(missing_ok=True)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    md_path = Path(argv[1])
    pdf_path = Path(argv[2])
    if not md_path.exists():
        print(f"error: input not found: {md_path}", file=sys.stderr)
        return 1
    render(md_path, pdf_path)
    print(f"wrote {pdf_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
