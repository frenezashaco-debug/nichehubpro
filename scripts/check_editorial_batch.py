"""Check the three differentiated lifestyle guides after editorial changes."""
import html
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
slugs = ('healthy-living-tips', 'healthy-daily-habits', 'simple-morning-habits')
catalog_source = (root / 'articles.js').read_text(encoding='utf-8')
catalog = json.loads(catalog_source[catalog_source.index('['):catalog_source.rfind(']') + 1])
sitemap = ET.parse(root / 'sitemap.xml').getroot()
ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
for slug in slugs:
    source = (root / 'articles' / (slug + '.html')).read_text(encoding='utf-8')
    body = source.split('<article class="article-content" id="article-body">')[1].split('</article>')[0]
    documents = [json.loads(raw) for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', source, re.S)]
    faq = next(item for item in documents if item.get('@type') == 'FAQPage')
    answers = re.findall(r'<div class="faq-a">(.*?)</div>', body, re.S)
    assert len(answers) == 5
    assert [item['acceptedAnswer']['text'] for item in faq['mainEntity']] == answers
    assert '\u2014' not in source
    meta = re.search(r'<meta name="description" content="([^"]+)"', source)[1]
    assert 155 <= len(meta) <= 160
    assert slug.replace('-', ' ') in meta.lower()
    record = next(item for item in catalog if item['slug'] == slug)
    assert record['excerpt'] == meta
    assert len(re.findall(r'<p>', body.split('<div class="tldr">')[0])) == 3
    main = body.split('<h2>An Illustrative Scenario</h2>')[0]
    headings = re.findall(r'<h2>(.*?)</h2>', main)
    assert len(headings) == 5 and all(h.endswith('?') for h in headings)
    assert main.count('<ul>') == 5
    assert len(re.findall(r'<strong>[1-7]\. ', main)) == 7
    links = re.findall(r'href="(/articles/[^"#]+)"', main)
    assert len(links) == len(set(links)) == 3
    for link in links:
        assert (root / link.lstrip('/')).is_file(), link
    assert len(re.findall(r'<img ', body)) == 3
    assert body.count('<h2>An Illustrative Scenario</h2>') == 1
    for paragraph in re.findall(r'<p(?: [^>]*)?>(.*?)</p>', body, re.S):
        assert len(html.unescape(re.sub('<[^>]+>', ' ', paragraph)).split()) <= 60
    assert 'This article is for informational purposes only and does not replace professional medical advice.' in body
    url = 'https://nichehubpro.com/articles/' + slug + '.html'
    entry = next(item for item in sitemap if item.find('s:loc', ns).text == url)
    assert entry.find('s:lastmod', ns).text == '2026-10-24'
    print(slug + ': editorial structure, metadata, links, images and FAQ/schema checks passed')
