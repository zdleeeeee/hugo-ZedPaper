"""Run with python themes/ZedPaper/tests/test_profile_image.py (requires Hugo)."""
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import struct
import subprocess
from urllib.parse import urlparse
from uuid import uuid4
import zlib

THEME = Path(__file__).resolve().parents[1]
ROOT = THEME.parents[1]


def png(width, height):
    def chunk(name, data):
        return struct.pack('>I', len(data)) + name + data + struct.pack('>I', zlib.crc32(name + data))
    header = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    pixels = (b'\0' + b'\x40\x80\xc0' * width) * height
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header) + chunk(b'IDAT', zlib.compress(pixels)) + chunk(b'IEND', b'')


class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag == 'img': self.images.append(dict(attrs))


site = ROOT / ('.profile-check-' + uuid4().hex)
assert site.resolve().parent == ROOT.resolve()
site.mkdir()
try:
    (site / 'assets').mkdir()
    (site / 'assets/avatar.png').write_bytes(png(900, 900))
    (site / 'assets/small.png').write_bytes(png(80, 80))
    (site / 'assets/avatar.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="150" height="150"/>', encoding='utf-8')
    base = f'baseURL="https://example.org/"\ntitle="Test"\ntheme="ZedPaper"\nthemesDir={json.dumps(THEME.parent.as_posix())}\n[params.profileMode]\nenabled=true\nimageWidth=150\nimageHeight=150\n'
    for image, expected in [('avatar.png', [150, 300, 450, 900]), ('small.png', [80]), ('avatar.svg', []), ('https://example.org/external.png', [])]:
        (site / 'hugo.toml').write_text(base + f'imageUrl="{image}"\n', encoding='utf-8')
        for environment in ['development', 'production']:
            run = subprocess.run(['hugo', '--source', str(site), '--environment', environment], capture_output=True, text=True, encoding='utf-8')
            assert run.returncode == 0, run.stdout + run.stderr
            parser = Images()
            parser.feed((site / 'public/index.html').read_text(encoding='utf-8'))
            avatar = next(img for img in parser.images if img.get('alt') == 'profile image')
            assert avatar['width'] == avatar['height'] == '150'
            if not expected:
                assert 'srcset' not in avatar
                continue
            assert avatar.get('sizes') == '150px', avatar
            candidates = [value.strip().rsplit(' ', 1) for value in avatar['srcset'].split(',')]
            assert [int(descriptor[:-1]) for _, descriptor in candidates] == expected, avatar
            for url, descriptor in candidates:
                data = (site / 'public' / urlparse(url).path.lstrip('/')).read_bytes()
                width, height = struct.unpack('>II', data[16:24])
                assert width == height == int(descriptor[:-1]), (url, width, height)
    print('Profile image tests passed: responsive candidates, original-resolution fallback, no upscaling, consistent builds, SVG and external images.')
finally:
    shutil.rmtree(site)
