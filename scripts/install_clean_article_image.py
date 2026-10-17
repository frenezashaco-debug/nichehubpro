"""Install an inspected generated replacement; only encode the chosen image."""
import argparse
import io
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    'entrepreneurs': ('healthy-productivity-habits-for-entrepreneurs', 'healthy-productivity-habits-for-entrepreneurs-sec1.webp', 'Woman arranging blank priority cards at a home desk'),
    'pressure': ('how-to-stay-calm-under-pressure', 'how-to-stay-calm-under-pressure-sec1.webp', 'Man pausing before a task at a quiet desk'),
    'procrastination': ('how-to-stop-procrastination', 'how-to-stop-procrastination-sec5-inline-v1.webp', 'Woman opening a blank notebook to begin a task'),
}
parser = argparse.ArgumentParser()
parser.add_argument('key', choices=[*TARGETS, 'discipline'])
parser.add_argument('source', type=Path)
args = parser.parse_args()
with Image.open(args.source) as original:
    selected = original.convert('RGB')

def encode(output, fmt):
    for quality in range(80, 29, -5):
        buffer = io.BytesIO()
        selected.save(buffer, format=fmt, quality=quality, optimize=True, method=6)
        if buffer.tell() <= 99000:
            output.write_bytes(buffer.getvalue())
            return
    raise ValueError('Could not meet the 100 KB image budget: ' + str(output))

if args.key == 'discipline':
    for extension, fmt in [('jpg', 'JPEG'), ('webp', 'WEBP')]:
        output = ROOT / 'images' / ('how-to-build-discipline-clean-v2.' + extension)
        encode(output, fmt)
        old = 'how-to-build-discipline.' + extension
        new = output.name
        # These exact filenames are public asset references in site pages/catalogues.
        for file in [*(ROOT / 'articles').glob('*.html'), ROOT / 'index.html', ROOT / 'articles.js', ROOT / 'api/articles.json']:
            text = file.read_text(encoding='utf-8')
            if old in text:
                file.write_text(text.replace(old, new), encoding='utf-8', newline='')
        print(output)
else:
    slug, old, alt = TARGETS[args.key]
    new = slug + ('-sec5-clean-v2.webp' if args.key == 'procrastination' else '-sec1-clean-v2.webp')
    output = ROOT / 'images' / new
    encode(output, 'WEBP')
    file = ROOT / 'articles' / (slug + '.html')
    text = file.read_text(encoding='utf-8')
    import re
    pattern = r'<img\b[^>]*src="\.\./images/(?:' + re.escape(old) + '|' + re.escape(new) + r')"[^>]*>'
    match = re.search(pattern, text)
    if not match:
        raise ValueError('Expected image reference not found: ' + old)
    tag = match.group(0).replace(old, new)
    tag = re.sub(r'alt="[^"]*"', 'alt="' + alt + '"', tag)
    tag = re.sub(r'width="\d+"', f'width="{selected.width}"', tag)
    tag = re.sub(r'height="\d+"', f'height="{selected.height}"', tag)
    file.write_text(text[:match.start()] + tag + text[match.end():], encoding='utf-8', newline='')
    print(output)
