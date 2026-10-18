"""Build a Make-compatible Pinterest payload without sending it or reading secrets."""
import html
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode, urljoin, urlsplit, unquote

SITE = 'https://nichehubpro.com'
BOARDS = {'Mental Wellness': '1135118349771004496', 'Productivity': '1135118349771004499', 'Healthy Lifestyle': '1135118349771004501'}


class ArticleImages(HTMLParser):
    def __init__(self, markup):
        super().__init__(convert_charrefs=True)
        self.images = []
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'img' and values.get('src'):
            self.images.append((values['src'], values.get('alt', '')))


def campaign_url(canonical, source, medium, campaign, content):
    parts = urlsplit(canonical)
    if parts.scheme != 'https' or parts.hostname != 'nichehubpro.com' or parts.query or parts.fragment:
        raise ValueError('Expected a clean HTTPS canonical URL on nichehubpro.com')
    return canonical + '?' + urlencode({'utm_source': source, 'utm_medium': medium, 'utm_campaign': campaign, 'utm_content': content})


def build_pinterest_payload(article, root, campaign='scheduled_articles'):
    root = Path(root).resolve()
    slug = str(article.get('slug', ''))
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
        raise ValueError('Invalid article slug')
    canonical = f'{SITE}/articles/{slug}.html'
    markup = (root / 'articles' / (slug + '.html')).read_text(encoding='utf-8')
    images = ArticleImages(markup).images
    pins = article.get('pins', [])[:3]
    if not pins or len(images) < len(pins):
        raise ValueError('Missing pin copy or article images')
    category = article.get('category', '')
    if category not in BOARDS:
        raise ValueError('No Pinterest board configured for category')
    enriched = []
    for index, pin in enumerate(pins):
        src, alt = images[index]
        url = urljoin(canonical, src)
        parsed = urlsplit(url)
        asset = (root / unquote(parsed.path).lstrip('/')).resolve()
        if parsed.scheme != 'https' or parsed.hostname != 'nichehubpro.com' or root not in asset.parents or not asset.is_file():
            raise ValueError('Article image must be an existing local public asset')
        title = html.unescape(str(pin.get('title') or article['title']))
        description = html.unescape(str(pin.get('description', '')))
        if re.search(r'[\u2013\u2014\u2015]', title + description):
            raise ValueError('Pin copy contains a forbidden dash; correct the copy first')
        enriched.append({'title': title, 'description': description, 'image_url': url,
                         'alt_text': alt,
                         'article_url': campaign_url(canonical, 'pinterest', 'social', campaign, f'{slug}_pin_{index+1}')})
    # Existing Make scenarios can keep mapping the shared article_url. Per-pin
    # attribution requires mapping pins[].article_url in the Make iterator.
    return {'slug': slug, 'title': article['title'], 'category': category,
            'board_id': BOARDS[category], 'canonical_url': canonical,
            'article_url': campaign_url(canonical, 'pinterest', 'social', campaign, slug),
            'pins': enriched}
