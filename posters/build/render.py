"""HTML -> true-size vector PDF (headless Chrome) -> PNG preview (Poppler).
Chrome 154's new headless writes the PDF and then never exits, so this watches its log for the
'written to file' line and closes that one private browser instance (its own profile directory)."""
import subprocess, time, os, signal, tempfile, shutil, sys
from pathlib import Path

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

def html_to_pdf(html, pdf, budget_ms=8000, timeout=180):
    html, pdf = Path(html).resolve(), Path(pdf).resolve()
    pdf.parent.mkdir(parents=True, exist_ok=True)
    if pdf.exists(): pdf.unlink()
    prof = tempfile.mkdtemp(prefix='rtam-chrome-')
    log = open(os.path.join(prof, 'chrome.log'), 'w')
    p = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
                          '--use-mock-keychain', '--password-store=basic', '--disable-background-networking',
                          '--disable-component-update', '--disable-sync', '--disable-extensions', '--hide-scrollbars',
                          f'--user-data-dir={prof}', '--allow-file-access-from-files', '--no-pdf-header-footer',
                          f'--virtual-time-budget={budget_ms}', f'--print-to-pdf={pdf}', html.as_uri()],
                         stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    t0 = time.time(); ok = False
    while time.time() - t0 < timeout:
        time.sleep(.4)
        txt = open(os.path.join(prof, 'chrome.log'), errors='ignore').read()
        if 'written to file' in txt: ok = True; break
        if p.poll() is not None: ok = pdf.exists(); break
    try: os.killpg(p.pid, signal.SIGTERM)
    except Exception: pass
    time.sleep(.3)
    subprocess.run(['pkill', '-f', f'user-data-dir={prof}'], capture_output=True)
    log.close(); shutil.rmtree(prof, ignore_errors=True)
    if not ok or not pdf.exists(): raise RuntimeError(f'Chrome did not produce {pdf}')
    return pdf

def html_to_screenshot(html, png, width=1440, height=2400, scale=1, budget_ms=8000, timeout=120):
    """Screenshot at a real viewport size (media queries see this width, unlike print)."""
    html, png = Path(html).resolve(), Path(png).resolve()
    if png.exists(): png.unlink()
    prof = tempfile.mkdtemp(prefix='rtam-chrome-'); log = open(os.path.join(prof, 'chrome.log'), 'w')
    p = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--use-mock-keychain',
                          '--password-store=basic', '--disable-background-networking', '--disable-component-update', '--disable-sync',
                          '--disable-extensions', '--hide-scrollbars', f'--user-data-dir={prof}', '--allow-file-access-from-files',
                          f'--window-size={width},{height}', f'--force-device-scale-factor={scale}', f'--virtual-time-budget={budget_ms}',
                          f'--screenshot={png}', html.as_uri()], stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(.4)
        if 'written to file' in open(os.path.join(prof, 'chrome.log'), errors='ignore').read() or p.poll() is not None: break
    try: os.killpg(p.pid, signal.SIGTERM)
    except Exception: pass
    time.sleep(.3); subprocess.run(['pkill', '-f', f'user-data-dir={prof}'], capture_output=True)
    log.close(); shutil.rmtree(prof, ignore_errors=True)
    if not png.exists(): raise RuntimeError(f'Chrome did not produce {png}')
    return png

def dump_dom(html, budget_ms=8000, timeout=90, width=1440, height=2400):
    """Serialized DOM after scripts have run (for functional checks of a page)."""
    html = Path(html).resolve(); prof = tempfile.mkdtemp(prefix='rtam-chrome-'); out = os.path.join(prof, 'dom.html'); f = open(out, 'w')
    p = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--use-mock-keychain',
                          '--password-store=basic', '--disable-background-networking', '--disable-component-update', '--disable-sync',
                          '--disable-extensions', f'--user-data-dir={prof}', '--allow-file-access-from-files', f'--window-size={width},{height}',
                          f'--virtual-time-budget={budget_ms}', '--dump-dom', html.as_uri()], stdout=f, stderr=subprocess.DEVNULL, start_new_session=True)
    t0 = time.time(); txt = ''
    while time.time() - t0 < timeout:
        time.sleep(.5); txt = open(out, errors='ignore').read()
        if '</html>' in txt or p.poll() is not None: break
    try: os.killpg(p.pid, signal.SIGTERM)
    except Exception: pass
    time.sleep(.3); subprocess.run(['pkill', '-f', f'user-data-dir={prof}'], capture_output=True)
    f.close(); txt = open(out, errors='ignore').read(); shutil.rmtree(prof, ignore_errors=True)
    return txt

def pdf_to_png(pdf, png, long_side=1800):
    png = Path(png); stem = str(png.with_suffix(''))
    subprocess.run(['pdftoppm', '-png', '-singlefile', '-scale-to', str(long_side), str(pdf), stem], check=True)
    return png

def pdf_report(pdf):
    out = subprocess.run(['pdfinfo', str(pdf)], capture_output=True, text=True).stdout
    size = [l for l in out.splitlines() if l.startswith('Page size')][0].split(':')[1].strip()
    fonts = subprocess.run(['pdffonts', str(pdf)], capture_output=True, text=True).stdout.splitlines()[2:]
    imgs = subprocess.run(['pdfimages', '-list', str(pdf)], capture_output=True, text=True).stdout.splitlines()[2:]
    return {'page': size, 'fonts': [f.split()[0] for f in fonts], 'images': [' '.join(i.split()[2:5] + i.split()[8:9]) for i in imgs], 'MB': round(os.path.getsize(pdf) / 1e6, 2)}

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    html_to_pdf(src, dst); print(pdf_report(dst))
    if len(sys.argv) > 3: pdf_to_png(dst, sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 1800)
