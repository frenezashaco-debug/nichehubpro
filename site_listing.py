"""Keep canonical article hubs useful and crawlable without client-side JavaScript."""
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote

SITE = 'https://nichehubpro.com'
HUBS = {'all-articles': None, 'mental-wellness': 'mental-wellness',
        'productivity': 'productivity', 'healthy-lifestyle': 'healthy-lifestyle'}


class Cover(HTMLParser):
    def __init__(self, markup):
        super().__init__(convert_charrefs=True)
        self.image = None
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        if tag == 'img' and self.image is None:
            self.image = dict(attrs)


def render_card(article, root):
    slug = article['slug']
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
        raise ValueError('Invalid listing slug')
    canonical = f'{SITE}/articles/{slug}.html'
    cover = Cover((root / 'articles' / (slug + '.html')).read_text(encoding='utf-8')).image
    if not cover or not cover.get('src'):
        raise ValueError('Missing actual article cover: ' + slug)
    parsed = urlsplit(urljoin(canonical, cover['src']))
    file = (root / unquote(parsed.path).lstrip('/')).resolve()
    if parsed.hostname != 'nichehubpro.com' or root not in file.parents or not file.is_file():
        raise ValueError('Missing or external cover: ' + slug)
    escape = lambda value: html.escape(str(value), quote=True)
    title, category = escape(article['title']), escape(article['category'])
    excerpt = escape(article.get('excerpt', ''))
    alt = escape(cover.get('alt') or article['title'])
    src = escape(parsed.path)
    width = cover.get('width', '800'); height = cover.get('height', '450')
    if not width.isdigit() or not height.isdigit():
        width, height = '800', '450'
    return (f'<div class="card" data-cat="{escape(article["cat_slug"])}">'
            f'<img src="{src}" alt="{alt}" width="{width}" height="{height}" loading="lazy" '
            'style="width:100%;height:200px;object-fit:cover;border-radius:8px 8px 0 0;">'
            f'<div class="card-body"><span class="card-tag">{category}</span>'
            f'<h3><a href="/articles/{slug}.html">{title}</a></h3><p>{excerpt}</p>'
            f'<a href="/articles/{slug}.html" class="read-more">Read article &rarr;</a></div></div>')


def render_listing_pages(articles, root):
    root = Path(root).resolve()
    # Render and validate every card first, before touching any hub.
    cards = [(article, render_card(article, root)) for article in articles]
    outputs = []
    for hub, category in HUBS.items():
        file = root / hub / 'index.html'
        source = file.read_text(encoding='utf-8')
        selected = [card for article, card in cards if category is None or article['cat_slug'] == category]
        if not selected:
            raise ValueError('Empty article hub: ' + hub)
        replacement = '\n<!-- STATIC_ARTICLE_CARDS_START -->\n' + '\n'.join(selected) + '\n<!-- STATIC_ARTICLE_CARDS_END -->\n'
        pattern = r'(<div\b[^>]*id="article-grid"[^>]*>)[\s\S]*?(</div>\s*<div id="empty-state")'
        updated, count = re.subn(pattern, lambda m: m[1] + replacement + m[2], source, count=1)
        if count != 1:
            raise ValueError('Could not locate article grid in ' + hub)
        outputs.append((file, updated))
    for file, source in outputs:
        file.write_text(source, encoding='utf-8', newline='')
    return {hub: sum(category is None or article['cat_slug'] == category for article in articles) for hub, category in HUBS.items()}


if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    source = (root / 'articles.js').read_text(encoding='utf-8')
    articles = json.loads(re.search(r'const ARTICLES = (\[[\s\S]*?\]);', source).group(1))
    print(json.dumps(render_listing_pages(articles, root), indent=2))
