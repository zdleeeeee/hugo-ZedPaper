"""Run with python themes/ZedPaper/tests/test_authors.py (requires Hugo)."""
import html
import json
from pathlib import Path
import re
import subprocess
from contextlib import contextmanager
import shutil
from uuid import uuid4
import xml.etree.ElementTree as ET

THEME = Path(__file__).resolve().parents[1]
ROOT = THEME.parents[1]
CASES = {
    'legacy': ("author = 'Legacy Author'", ['Legacy Author'], []),
    'names': ("author = ['Alice', 'Bob']", ['Alice', 'Bob'], []),
    'linked': ('author = [{name="Zed Lee", url="/"}, {name="Alice", url="https://alice.example/"}, {name="Bob"}]', ['Zed Lee', 'Alice', 'Bob'], ['/blog/', 'https://alice.example/']),
    'mixed': ('author = ["Plain", {name="Linked", url="/about/"}]', ['Plain', 'Linked'], ['/blog/about/']),
    'relative': ('author = [{name="Relative", url="about/"}]', ['Relative'], ['/blog/about/']),
    'anchored': ('author = [{name="Root", url="/about/team/#zed-lee"}, {name="Relative", url="about/team/#zed-lee"}]', ['Root', 'Relative'], ['/blog/about/team/#zed-lee', '/blog/about/team/#zed-lee']),
    'prefixed': ('author = [{name="Prefixed", url="/blog/about/team/#zed-lee"}]', ['Prefixed'], ['/blog/about/team/#zed-lee']),
    'map': ('author = {name="Solo", url="https://solo.example/"}', ['Solo'], ['https://solo.example/']),
    'fallback': ('', ['Default', 'Coauthor'], ['/blog/']),
    'escaped': ("author = 'A <B> & Co'", ['A <B> & Co'], []),
    'empty': ('author = [{url="/"}, {name=""}]', [], []),
    'hidden': ('author = [{name="Hidden", url="/"}]\nhideAuthor = true', ['Hidden'], []),
}

@contextmanager
def fixture_directory():
    directory = ROOT / ('.authors-check-' + uuid4().hex)
    assert directory.resolve().parent == ROOT.resolve()
    directory.mkdir()
    try:
        yield directory
    finally:
        shutil.rmtree(directory)


with fixture_directory() as folder:
    site = Path(folder)
    (site / 'content/posts').mkdir(parents=True)
    (site / 'hugo.toml').write_text(
        f'baseURL="https://example.org/blog/"\ntitle="Test"\ntheme="ZedPaper"\nthemesDir={json.dumps(THEME.parent.as_posix())}\n'
        '[params]\nauthor=[{name="Default",url="/",email="default@example.org"},{name="Coauthor"}]\n', encoding='utf-8')
    for slug, (front, _, _) in CASES.items():
        (site / f'content/posts/{slug}.md').write_text(
            f'+++\ntitle="{slug}"\ndate=2026-01-01\n{front}\n+++\nBody.\n', encoding='utf-8')
    subprocess.run(['hugo', '--source', str(site), '--environment', 'production'], check=True, capture_output=True, text=True, encoding='utf-8')
    for slug, (_, names, urls) in CASES.items():
        output = (site / f'public/posts/{slug}/index.html').read_text(encoding='utf-8')
        meta = re.search(r'<meta name="author" content="([^"]*)">', output)
        assert meta and html.unescape(meta[1]) == ', '.join(names), (slug, meta[1] if meta else None)
        visible = re.search(r'<div class="post-meta">(.*?)</div>', output, re.S)[1]
        actual_urls = re.findall(r'<a href="([^"]+)"', visible)
        assert actual_urls == urls, (slug, actual_urls)
        if slug == 'escaped': assert 'A &lt;B&gt; &amp; Co' in visible
        article = next(item for item in (
            json.loads(value) for value in re.findall(r'<script type="application/ld\+json">(.*?)</script>', output, re.S)
        ) if item.get('@type') == 'BlogPosting')
        people = article.get('author', [])
        if isinstance(people, dict): people = [people]
        assert [person['name'] for person in people] == names, (slug, people)
        expected_schema_urls = ['https://example.org' + url if url.startswith('/') else url for url in urls]
        if slug == 'hidden': expected_schema_urls = ['https://example.org/blog/']
        assert [person['url'] for person in people if 'url' in person] == expected_schema_urls, (slug, people)
    feed = ET.parse(site / 'public/index.xml')
    assert feed.findtext('./channel/managingEditor') == 'default@example.org (Default)'
    print('Author integration tests passed: legacy, multiple names, linked authors, relative URLs, defaults, escaping, hidden authors, schema, and RSS.')
