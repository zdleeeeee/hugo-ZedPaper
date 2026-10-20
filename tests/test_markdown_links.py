"""Run with python themes/ZedPaper/tests/test_markdown_links.py (requires Hugo)."""
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import subprocess
from urllib.parse import unquote
from uuid import uuid4

THEME = Path(__file__).resolve().parents[1]
ROOT = THEME.parents[1]


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.in_main = False

    def handle_starttag(self, tag, attrs):
        if tag == 'main':
            self.in_main = True
        if tag == 'a' and self.in_main:
            self.links.append(dict(attrs))

    def handle_endtag(self, tag):
        if tag == 'main':
            self.in_main = False


site = ROOT / ('.markdown-links-check-' + uuid4().hex)
assert site.resolve().parent == ROOT.resolve()
site.mkdir()
try:
    (site / 'content/about/加入创作').mkdir(parents=True)
    (site / 'content/about/加入创作/index.md').write_text(
        '+++\ntitle="Target"\nslug="join"\n+++\n## Details\n', encoding='utf-8')
    (site / 'content/sample.md').write_text(
        '+++\ntitle="Sample"\n+++\n' + '\n\n'.join([
            '[Canonical](/about/加入创作/ "Link title")',
            '[Legacy](/gog/about/加入创作/?a=1&b=2#details)',
            '[External](https://example.net/gog/about/加入创作/)',
            '[CDN](//cdn.example.net/file.pdf)',
            '[Email](mailto:author@example.net)',
            '[Anchor](#details)',
            '[Relative](files/manual.pdf)',
            '[Missing](/missing/not-a-page/)',
            '[Download](/downloads/manual.pdf)',
            '{{< quote source="— Author [Title](/gog/about/加入创作/#details)" >}}Quoted.{{< /quote >}}',
        ]), encoding='utf-8')
    for prefix in ['/', '/gog/', '/new/']:
        (site / 'hugo.toml').write_text(
            f'baseURL="https://example.org{prefix}"\ntitle="Test"\ntheme="ZedPaper"\n'
            f'themesDir={json.dumps(THEME.parent.as_posix())}\n', encoding='utf-8')
        run = subprocess.run(['hugo', '--source', str(site)], capture_output=True, text=True, encoding='utf-8')
        assert run.returncode == 0, run.stdout + run.stderr
        parser = Links()
        parser.feed((site / 'public/sample/index.html').read_text(encoding='utf-8'))
        links = parser.links
        assert [unquote(a['href']) for a in links] == [
            prefix + 'about/join/',
            prefix + 'about/join/?a=1&b=2#details',
            'https://example.net/gog/about/加入创作/',
            '//cdn.example.net/file.pdf', 'mailto:author@example.net', '#details',
            'files/manual.pdf', '/missing/not-a-page/', '/downloads/manual.pdf',
            prefix + 'about/join/#details',
        ], (prefix, links)
        assert links[0]['title'] == 'Link title'
    print('Markdown link tests passed: three base paths, legacy prefixes, slugs, queries, fragments, quote source, and unchanged external/unresolved links.')
finally:
    shutil.rmtree(site)
