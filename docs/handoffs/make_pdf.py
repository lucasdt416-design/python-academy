"""Turn a handoff Markdown file into a PDF next to it.

Usage, from the repository root:
    uv run --with markdown python docs/handoffs/make_pdf.py docs/handoffs/<file>.md

Needs the frontend's Playwright Chromium (cd frontend && npm ci && npx playwright install chromium).
"""
import html
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[2]
STYLE = """
@page { size: Letter; margin: 18mm 16mm; }
body { font: 10.5pt/1.5 -apple-system, "Helvetica Neue", Arial, sans-serif; color: #1f2a2c; }
h1 { font-size: 20pt; color: #234a40; margin: 0 0 6pt; }
h2 { font-size: 14pt; color: #234a40; border-bottom: 1px solid #cfd9d4; padding-bottom: 3pt; margin-top: 18pt; }
h3 { font-size: 11.5pt; margin: 14pt 0 4pt; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0 10pt; font-size: 9.5pt; page-break-inside: auto; }
tr { page-break-inside: avoid; }
th, td { border: 1px solid #cfd9d4; padding: 4pt 6pt; text-align: left; vertical-align: top; }
th { background: #eef3f0; }
code { font: 9pt Menlo, monospace; background: #f1f4f2; padding: 0 2pt; border-radius: 2pt; }
pre { background: #f1f4f2; padding: 8pt; border-radius: 4pt; white-space: pre-wrap; }
pre code { background: none; padding: 0; }
blockquote { margin: 8pt 0; padding: 6pt 10pt; background: #fbf5e9; border-left: 3pt solid #d9b56b; }
a { color: #2c6a58; }
img { max-width: 100%; border: 1px solid #cfd9d4; border-radius: 4pt; margin: 4pt 0 10pt; }
img.phone { max-width: 45%; }
"""

PRINT = """
const {chromium} = require('@playwright/test');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + process.argv[1]);
  await page.pdf({path: process.argv[2], format: 'Letter', printBackground: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#777">Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>',
    margin: {top: '18mm', bottom: '18mm', left: '16mm', right: '16mm'}});
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
"""


def main(source):
    source = Path(source).resolve()
    text = source.read_text()
    title = text.splitlines()[0].lstrip('# ').strip()
    body = markdown.markdown(text, extensions=['tables', 'fenced_code', 'sane_lists'])
    # The base URL lets the Markdown reference images next to it, e.g. images/03-home.png.
    page = f'<!doctype html><html><head><meta charset="utf-8"><base href="{source.parent.as_uri()}/"><title>{html.escape(title)}</title><style>{STYLE}</style></head><body>{body}</body></html>'
    target = source.with_suffix('.pdf')
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False) as tmp:
        tmp.write(page)
    modules = ROOT / 'frontend' / 'node_modules'
    subprocess.run(['node', '-e', PRINT, tmp.name, str(target)], check=True, env={'NODE_PATH': str(modules), 'PATH': '/usr/local/bin:/usr/bin:/bin'})
    Path(tmp.name).unlink()
    print(f'Wrote {target.relative_to(ROOT)}')


if __name__ == '__main__':
    main(sys.argv[1])
