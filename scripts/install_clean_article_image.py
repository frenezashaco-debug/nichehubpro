"""Install an inspected generated replacement; only encode the chosen image."""
import argparse
import io
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    'pomo_setup': ('pomodoro-technique-explained-for-beginners', 'pomodoro-technique-explained-for-beginners-sec1-inline-v1.webp', 'Woman setting an unmarked glass sand timer beside a blank closed notebook'),
    'pomo_break': ('pomodoro-technique-explained-for-beginners', 'pomodoro-technique-explained-for-beginners-sec5-inline-v1.webp', 'Man standing beside an open balcony door looking toward a garden'),
    'fatigue': ('why-you-feel-tired-all-the-time', 'why-you-feel-tired-all-the-time-sec1.webp', 'Woman pausing at a wooden table beside a blank notebook and mug in natural window light'),
    'bedtime': ('anxiety-before-sleep', 'anxiety-before-sleep-sec1.webp', 'Man sitting on the edge of a bed beside a window in the early evening'),
    'deadlines': ('the-psychology-behind-why-deadlines-make-you-more-productive', 'the-psychology-behind-why-deadlines-make-you-more-productive-sec5.webp', 'Man arranging blank task cards to review a realistic deadline plan'),
    'sleep': ('how-sleep-debt-silently-drains-your-daily-performance', 'how-sleep-debt-silently-drains-your-daily-performance-sec5.webp', 'Woman closing bedroom curtains while preparing for a quiet evening'),
    'cognitive': ('what-cognitive-load-does-to-your-decision-making', 'what-cognitive-load-does-to-your-decision-making-sec5.webp', 'Woman comparing options using plain counters at a kitchen table'),
    'glucose': ('how-blood-sugar-swings-affect-your-energy-and-mood', 'how-blood-sugar-swings-affect-your-energy-and-mood-sec5.webp', 'Man preparing a varied lunch with a closed notebook nearby'),
    'rest': ('how-to-stop-feeling-guilty-for-resting', 'how-to-stop-feeling-guilty-for-resting-sec5.webp', 'Man taking a comfortable reading break on a garden patio'),
    'habit': ('the-science-of-habit-formation-explained-simply', 'the-science-of-habit-formation-explained-simply-sec5.webp', 'Man placing unbranded walking shoes by the door as a routine cue'),
    'energy': ('how-to-build-energy-that-lasts-all-day-without-crashing', 'how-to-build-energy-that-lasts-all-day-without-crashing-sec5.webp', 'Woman preparing an ordinary varied lunch in her home kitchen'),
    'entrepreneurs': ('healthy-productivity-habits-for-entrepreneurs', 'healthy-productivity-habits-for-entrepreneurs-sec1.webp', 'Woman arranging blank priority cards at a home desk'),
    'pressure': ('how-to-stay-calm-under-pressure', 'how-to-stay-calm-under-pressure-sec1.webp', 'Man pausing before a task at a quiet desk'),
    'procrastination': ('how-to-stop-procrastination', 'how-to-stop-procrastination-sec5-inline-v1.webp', 'Woman opening a blank notebook to begin a task'),
}
parser = argparse.ArgumentParser()
parser.add_argument('key', choices=[*TARGETS, 'discipline', 'dopamine'])
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

if args.key in ('discipline', 'dopamine'):
    cover_slug = 'how-to-build-discipline' if args.key == 'discipline' else 'how-dopamine-actually-works-and-why-quick-fixes-backfire'
    for extension, fmt in [('jpg', 'JPEG'), ('webp', 'WEBP')]:
        output = ROOT / 'images' / (cover_slug + '-clean-v2.' + extension)
        encode(output, fmt)
        old = cover_slug + '.' + extension
        new = output.name
        # These exact filenames are public asset references in site pages/catalogues.
        for file in [*(ROOT / 'articles').glob('*.html'), ROOT / 'index.html', ROOT / 'articles.js', ROOT / 'api/articles.json']:
            text = file.read_text(encoding='utf-8')
            if old in text:
                file.write_text(text.replace(old, new), encoding='utf-8', newline='')
        print(output)
    if args.key == 'dopamine':
        file = ROOT / 'articles' / (cover_slug + '.html')
        text = file.read_text(encoding='utf-8')
        import re
        def update_cover(match):
            tag = re.sub(r'alt="[^"]*"', 'alt="Woman putting her phone aside before choosing a planned guitar activity"', match[0])
            tag = re.sub(r'width="\d+"', f'width="{selected.width}"', tag)
            return re.sub(r'height="\d+"', f'height="{selected.height}"', tag)
        text = re.sub(r'<img\b[^>]*src="[^\"]*' + re.escape(cover_slug) + r'-clean-v2\.(?:jpg|webp)"[^>]*>', update_cover, text)
        file.write_text(text, encoding='utf-8', newline='')
else:
    slug, old, alt = TARGETS[args.key]
    new = slug + ('-sec5-clean-v2.webp' if '-sec5' in old else '-sec1-clean-v2.webp')
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
