"""Check the revised editorial batches, or article slugs supplied as arguments."""
import html
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
slugs = sys.argv[1:] or ('healthy-living-tips', 'healthy-daily-habits', 'simple-morning-habits',
                        'how-to-stay-calm-under-pressure', 'improve-daily-routine',
                        'how-sleep-affects-mental-health', 'best-foods-for-better-sleep',
                        'daily-wellness-habits', 'healthy-morning-routine-checklist',
                        'how-to-create-sustainable-healthy-habits',
                        'how-to-stop-negative-thoughts', 'how-to-build-confidence',
                        'how-to-stop-worrying-about-the-future',
                        'how-to-improve-energy-naturally', 'how-to-deal-with-stress-at-work',
                        'how-to-build-discipline', 'how-exercise-improves-mental-health',
                        'healthy-daily-routine-checklist', 'best-morning-habits-for-more-energy',
                        'deep-work-vs-multitasking', 'how-to-track-progress-toward-goals',
                        'how-to-control-your-thoughts', 'how-to-stop-self-sabotaging',
                        'fear-of-failure-anxiety', 'why-chronic-stress-makes-everything-feel-harder',
                        'healthy-lifestyle-tips', 'healthy-sleep-habits-that-improve-energy',
                        'life-balance-habits', 'the-science-of-habit-formation-explained-simply',
                        'daily-self-care-routine', 'how-to-build-a-routine-that-survives-a-busy-week',
                        'how-to-calm-down-when-overwhelmed', 'sleep-routine-tips',
                        'best-habit-tracker-methods-that-work', 'best-time-management-techniques-ranked',
                        'how-to-avoid-distractions-while-working', 'how-to-gamify-your-life-for-productivity',
                        'how-to-stop-procrastination', 'why-small-habits-create-big-results',
                        'why-you-feel-lost-in-life', 'why-you-have-no-motivation-anymore',
                        'how-to-improve-emotional-resilience',
                        'how-to-stay-focused-on-hard-tasks-without-burning-out')
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
    headings = re.findall(r'<h2(?: [^>]*)?>(.*?)</h2>', main)
    assert len(headings) == 5 and all(h.endswith('?') for h in headings)
    assert main.count('<ul>') == 5
    title = re.search(r'<h1[^>]*>(.*?)</h1>', source, re.S)[1]
    expected_options = int(re.search(r'\b(\d+)\b', title)[1])
    assert len(re.findall(r'<strong>\d+\. ', main)) == expected_options
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
    article = next(item for item in documents if item.get('@type') == 'Article')
    assert entry.find('s:lastmod', ns).text == article['dateModified']
    print(slug + ': editorial structure, metadata, links, images and FAQ/schema checks passed')
