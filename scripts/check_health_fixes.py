"""Validate sitemap-wide analytics, local assets, and corrected article links."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, unquote
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

def main():
    urls = [n.text for n in ET.parse(ROOT / 'sitemap.xml').getroot().findall('{*}url/{*}loc')]
    inbound = {}
    for url in urls:
        path = urlparse(url).path
        file = ROOT / (path.lstrip('/') + ('index.html' if path.endswith('/') else ''))
        text = file.read_text(encoding='utf-8')
        page = Page(text)
        assert text.count('src="/analytics.js"') == 1, file
        assert 'googletagmanager.com/gtag/js' not in text, file
        for tag, attrs in page.tags:
            key = 'href' if tag in ('a', 'link') else 'src'
            if tag not in ('a', 'link', 'script', 'img') or not attrs.get(key):
                continue
            target = urlparse(urljoin(url, attrs[key]))
            if target.netloc != 'nichehubpro.com':
                continue
            local = ROOT / (unquote(target.path).lstrip('/') + ('index.html' if target.path.endswith('/') else ''))
            assert local.exists(), (file, attrs[key])
            if tag == 'a' and target.path != path:
                inbound.setdefault(target.path, set()).add(path)
    for slug in ('how-to-build-a-productivity-system-with-apps', 'how-to-train-your-brain-for-longer-attention-spans', 'how-to-detox-your-mind'):
        assert len(inbound.get('/articles/' + slug + '.html', set())) >= 2, slug
    article = (ROOT / 'articles/how-to-stop-anxiety-attacks.html').read_text(encoding='utf-8')
    tags = Page(article).tags
    assert sum(t == 'h2' for t, _ in tags) == 6  # five body sections plus the existing related-articles heading
    assert sum(t == 'button' and a.get('class') == 'faq-q' for t, a in tags) == 5
    description = next(a['content'] for t, a in tags if t == 'meta' and a.get('name') == 'description')
    assert 155 <= len(description) <= 160
    assert 'Your heart is healthy' not in article
    assert '60% fewer' not in article
    rows = json.loads((ROOT / 'api/articles.json').read_text(encoding='utf-8'))
    entry = next(r for r in rows if r['id'] == 'how-to-stop-anxiety-attacks')
    assert entry['shortText'] == description
    print(f'PASS: {len(urls)} pages, analytics coverage, local links/assets, contextual links, and revised article checks.')

if __name__ == '__main__':
    main()
