"""Run with python themes/ZedPaper/tests/test_video_embeds.py (requires Hugo)."""
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import subprocess
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

THEME = Path(__file__).resolve().parents[1]
ROOT = THEME.parents[1]


class Frames(HTMLParser):
    def __init__(self):
        super().__init__()
        self.frames = []

    def handle_starttag(self, tag, attrs):
        if tag == 'iframe': self.frames.append(dict(attrs))


site = ROOT / ('.embeds-check-' + uuid4().hex)
assert site.resolve().parent == ROOT.resolve()
site.mkdir()
try:
    (site / 'content').mkdir()
    config = f'baseURL="https://example.org/"\ntitle="Test"\ntheme="ZedPaper"\nthemesDir={json.dumps(THEME.parent.as_posix())}\n'
    post = site / 'content/embeds.md'
    post.write_text('+++\ntitle="Embeds"\n+++\n' + '\n\n'.join([
        '{{< bilibili "BV1634y1t7xR" >}}',
        '{{< bilibili "av170001" 2 >}}',
        '{{< bilibili id="BV1634y1t7xR" page=3 title="B & B" >}}',
        '{{< youtube ZJthWmvUzzc >}}',
        '{{< youtube id="ZJthWmvUzzc" autoplay=true title="You & Me" >}}',
    ]), encoding='utf-8')
    for privacy in ['', '[privacy.youtube]\nprivacyEnhanced=true\n', '[privacy.youtube]\ndisable=true\n']:
        (site / 'hugo.toml').write_text(config + privacy, encoding='utf-8')
        run = subprocess.run(['hugo', '--source', str(site)], capture_output=True, text=True, encoding='utf-8')
        assert run.returncode == 0, run.stdout + run.stderr
        parser = Frames()
        parser.feed((site / 'public/embeds/index.html').read_text(encoding='utf-8'))
        frames = parser.frames
        assert len(frames) == (3 if 'disable=true' in privacy else 5), frames
        queries = [parse_qs(urlparse(frame['src']).query) for frame in frames[:3]]
        assert queries[0]['bvid'] == ['BV1634y1t7xR'] and queries[0]['page'] == ['1']
        assert queries[1]['aid'] == ['170001'] and queries[1]['page'] == ['2']
        assert queries[2]['page'] == ['3'] and frames[2]['title'] == 'B & B'
        assert all(query['autoplay'] == ['0'] for query in queries)
        assert all(frame.get('loading') == 'lazy' and 'allowfullscreen' in frame for frame in frames)
        if len(frames) == 5:
            host = 'www.youtube-nocookie.com' if 'privacyEnhanced=true' in privacy else 'www.youtube.com'
            assert frames[3]['src'] == f'https://{host}/embed/ZJthWmvUzzc'
            assert frames[4]['src'] == f'https://{host}/embed/ZJthWmvUzzc?autoplay=1'
            assert frames[4]['title'] == 'You & Me'
    (site / 'hugo.toml').write_text(config, encoding='utf-8')
    for shortcode in ['bilibili id="not-an-id"', 'bilibili id="av170001" page=0', 'youtube id="not-an-id"']:
        post.write_text('+++\ntitle="Invalid"\n+++\n{{< ' + shortcode + ' >}}', encoding='utf-8')
        run = subprocess.run(['hugo', '--source', str(site)], capture_output=True, text=True, encoding='utf-8')
        assert run.returncode != 0, f'Invalid shortcode accepted: {shortcode}'
    print('Video embed tests passed: BV/AV IDs, pages, positional/named parameters, titles, autoplay, YouTube privacy settings, and invalid input.')
finally:
    shutil.rmtree(site)
