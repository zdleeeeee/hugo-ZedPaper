"""Run with python themes/ZedPaper/tests/test_figure_links.py (requires Hugo)."""
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import subprocess
from uuid import uuid4

THEME = Path(__file__).resolve().parents[1]
ROOT = THEME.parents[1]


class Figures(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.caption = False

    def handle_starttag(self, tag, attrs):
        if tag == 'figcaption':
            self.caption = True
        if tag == 'a' and self.caption:
            self.links.append(dict(attrs)['href'])

    def handle_endtag(self, tag):
        if tag == 'figcaption':
            self.caption = False


site = ROOT / ('.figure-links-check-' + uuid4().hex)
assert site.resolve().parent == ROOT.resolve()
site.mkdir()
try:
    (site / 'content/about/authors').mkdir(parents=True)
    (site / 'content/about/authors/index.md').write_text(
        '+++\ntitle="Authors"\nslug="team"\n+++\n## Zed Lee\n', encoding='utf-8')
    (site / 'content/figures.md').write_text(
        '+++\ntitle="Figures"\n+++\n' + '\n\n'.join([
            '{{< figure src="image.jpg" attr="Zed Lee" attrref="/about/authors/#zed-lee" >}}',
            '{{< figure src="image.jpg" attr="External" attrlink="https://example.net/credits" >}}',
            '{{< figure src="image.jpg" attr="Relative" attrlink="credits.html" >}}',
            '{{< figure src="image.jpg" attr="Preferred" attrref="/about/authors/#zed-lee" attrlink="https://example.net/unused" >}}',
        ]), encoding='utf-8')
    for prefix in ['/', '/blog/']:
        (site / 'hugo.toml').write_text(
            f'baseURL="https://example.org{prefix}"\ntitle="Test"\ntheme="ZedPaper"\n'
            f'themesDir={json.dumps(THEME.parent.as_posix())}\n', encoding='utf-8')
        run = subprocess.run(['hugo', '--source', str(site)], capture_output=True, text=True, encoding='utf-8')
        assert run.returncode == 0, run.stdout + run.stderr
        parser = Figures()
        parser.feed((site / 'public/figures/index.html').read_text(encoding='utf-8'))
        target = prefix + 'about/team/#zed-lee'
        assert parser.links == [target, 'https://example.net/credits', 'credits.html', target], parser.links
    print('Figure link tests passed: root/subdirectory deployment, page slugs, anchors, legacy attrlink, and attrref precedence.')
finally:
    shutil.rmtree(site)
