"""Read-only thumbnail inventory for visual triage, not watermark certification."""
import json
from pathlib import Path
from urllib.parse import urlsplit, unquote
from PIL import Image, ImageDraw, ImageOps
ROOT = Path(__file__).resolve().parents[1]
rows = json.loads((ROOT / 'reports/all-article-copy-audit.json').read_text(encoding='utf-8'))
previous_file = ROOT / 'reports/image-inventory.json'
previous = set(json.loads(previous_file.read_text(encoding='utf-8'))) if previous_file.exists() else set()
images = []
for row in rows:
    for src in row['images'] + row.get('responsive_images', []):
        src = src.split(',')[0].split()[0]
        parsed = urlsplit(src)
        if parsed.netloc and parsed.hostname not in ('nichehubpro.com', 'www.nichehubpro.com'):
            continue
        target = unquote(parsed.path)
        file = ((ROOT / target.lstrip('/')) if target.startswith('/') else (ROOT / 'articles' / target)).resolve()
        if ROOT in file.parents and file.is_file() and file not in images:
            images.append(file)
remaining = [file for file in images if str(file) not in previous]
for offset in range(0, len(remaining), 24):
    sheet = Image.new('RGB', (1600, 1140), 'white')
    draw = ImageDraw.Draw(sheet)
    for index, file in enumerate(remaining[offset:offset + 24]):
        x, y = (index % 4) * 400, (index // 4) * 190
        with Image.open(file) as original:
            thumb = ImageOps.contain(original.convert('RGB'), (396, 160))
            sheet.paste(thumb, (x, y))
        draw.text((x + 3, y + 162), f'{offset + index}: {file.name[:58]}', fill='black')
    sheet.save(ROOT / f'reports/image-remaining-{offset // 24:02}.jpg', quality=90)
(ROOT / 'reports/image-inventory.json').write_text(json.dumps([str(p) for p in images], indent=2), encoding='utf-8')
print(f'{len(images)} unique images inventoried; {(len(images) + 23) // 24} contact sheets.')
print(f'{len(remaining)} additional source/fallback variants; {(len(remaining) + 23) // 24} remaining sheets.')
