"""Make HTML's implicit paragraph closures explicit, preserving text and layout."""
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOCKS = {'address', 'article', 'aside', 'blockquote', 'details', 'div', 'dl',
          'fieldset', 'figcaption', 'figure', 'footer', 'form', 'h1', 'h2', 'h3',
          'h4', 'h5', 'h6', 'header', 'hgroup', 'hr', 'main', 'menu', 'nav', 'ol',
          'p', 'pre', 'section', 'table', 'ul'}

class Closures(HTMLParser):
    def __init__(self, raw):
        super().__init__(convert_charrefs=False)
        self.offsets = [0]
        for line in raw.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))
        self.open_p = False
        self.positions = []
        self.feed(raw)

    def position(self):
        line, column = self.getpos()
        return self.offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        if tag in BLOCKS and self.open_p:
            self.positions.append(self.position())
            self.open_p = False
        if tag == 'p':
            self.open_p = True

    def handle_endtag(self, tag):
        if tag == 'p':
            self.open_p = False
        elif tag in BLOCKS and self.open_p:
            self.positions.append(self.position())
            self.open_p = False

plans = []
for file in sorted((ROOT / 'articles').glob('*.html')):
    raw = file.read_text(encoding='utf-8')
    parser = Closures(raw)
    if parser.positions:
        for offset in sorted(set(parser.positions), reverse=True):
            raw = raw[:offset] + '</p>' + raw[offset:]
        plans.append((file, raw, len(parser.positions)))
for file, raw, count in plans:
    file.write_text(raw, encoding='utf-8', newline='')
print(f'Explicit paragraph closures: {sum(p[2] for p in plans)} in {len(plans)} articles.')
