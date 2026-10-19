"""Run with python themes/ZedPaper/tests/test_cover_urls.py (requires Hugo)."""
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import subprocess
from uuid import uuid4

THEME = Path(__file__).resolve().parents[1]
ROOT = THEME.parents[1]


class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            self.sources.append(dict(attrs)['src'])


site = ROOT / ('.cover-urls-check-' + uuid4().hex)
assert site.resolve().parent == ROOT.resolve()
site.mkdir()
try:
    (site / 'content/catalog').mkdir(parents=True)
    (site / 'content/catalog/_index.md').write_text(
        '+++\ntitle="Catalog"\nlayout="directory"\n+++\n', encoding='utf-8')
    for prefix in ['/', '/blog/']:
        cases = {
            'root': ('/images/cover.svg', f'https://example.org{prefix}images/cover.svg'),
            'relative': ('images/cover.svg', f'https://example.org{prefix}images/cover.svg'),
            'prefixed': (prefix + 'images/cover.svg', f'https://example.org{prefix}images/cover.svg'),
            'external': ('https://cdn.example.net/cover.svg', 'https://cdn.example.net/cover.svg'),
            'protocol-relative': ('//cdn.example.net/cover.svg', '//cdn.example.net/cover.svg'),
        }
        (site / 'hugo.toml').write_text(
            f'baseURL="https://example.org{prefix}"\ntitle="Test"\ntheme="ZedPaper"\n'
            f'themesDir={json.dumps(THEME.parent.as_posix())}\n', encoding='utf-8')
        for name, (image, _) in cases.items():
            folder = site / 'content/catalog' / name
            folder.mkdir(exist_ok=True)
            (folder / '_index.md').write_text(
                f'+++\ntitle="{name}"\n[cover]\nimage={json.dumps(image)}\n+++\n', encoding='utf-8')
        for environment in ['production', 'development']:
            run = subprocess.run(
                ['hugo', '--source', str(site), '--environment', environment],
                capture_output=True, text=True, encoding='utf-8')
            assert run.returncode == 0, run.stdout + run.stderr
            parser = Images()
            parser.feed((site / 'public/catalog/index.html').read_text(encoding='utf-8'))
            assert sorted(parser.sources) == sorted(expected for _, expected in cases.values()), (
                prefix, environment, parser.sources)
    print('Cover URL tests passed: root and subdirectory hosting, both environments, relative paths, existing prefixes and external URLs.')
finally:
    shutil.rmtree(site)
